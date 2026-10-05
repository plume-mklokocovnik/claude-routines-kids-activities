import contextlib
import io
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import dispatch_input
import hide_event
import swipe


class DecisionInputTests(unittest.TestCase):
    def test_a_well_formed_patch_is_kept_without_comments_or_blanks(self):
        text = "# kids-activities decisions\n\ni:event_20261114_1440_35c838879cf0\nr:grad_20261014_1730\n"
        self.assertEqual(dispatch_input.clean_decisions(text),
                         ["i:event_20261114_1440_35c838879cf0", "r:grad_20261014_1730"])

    def test_every_code_the_app_sends_is_accepted(self):
        lines = [f"{code}:a" for code in "imrc"]
        self.assertEqual(dispatch_input.clean_decisions("\n".join(lines)), lines)

    def test_the_cleaned_text_is_one_the_applier_reads(self):
        lines = dispatch_input.clean_decisions("i:one\nm:two\nc:three\n")
        self.assertEqual(swipe.parse_patch("\n".join(lines)),
                         [("one", "interested"), ("two", "maybe"), ("three", None)])

    def test_anything_off_format_aborts_the_whole_patch(self):
        bad = [
            "x:one",                   # unknown code
            "I:one",                   # codes are lower case
            "i:",                      # no ID
            "i: one",                  # a space where the ID starts
            "i:one two",               # a space inside the ID
            "i:one;rm -rf /",          # shell syntax is never an ID
            "i:$(whoami)",
            "i:`id`",
            "i:../../db.json",         # an ID is a name, not a path
            "i:one\ti:two",
            "one",
            "i:" + "a" * 121,          # longer than any real ID
        ]
        for line in bad:
            with self.subTest(line=line):
                with self.assertRaises(ValueError):
                    dispatch_input.clean_decisions(f"i:fine\n{line}\n")

    def test_empty_and_comment_only_patches_are_refused(self):
        for text in ("", "   \n", "# only a comment\n", None):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    dispatch_input.clean_decisions(text)

    def test_size_limits_hold(self):
        with self.assertRaises(ValueError):
            dispatch_input.clean_decisions("i:a\n" * (dispatch_input.MAX_LINES + 1))
        with self.assertRaises(ValueError):
            dispatch_input.clean_decisions("# " + "x" * dispatch_input.MAX_CHARS)

    def test_a_real_sized_batch_fits_with_room_to_spare(self):
        batch = "\n".join(f"r:event_20261114_1440_{index:012x}" for index in range(200))
        self.assertEqual(len(dispatch_input.clean_decisions(batch)), 200)
        self.assertLess(len(batch), dispatch_input.MAX_CHARS)


class HideInputTests(unittest.TestCase):
    def test_ids_are_kept_one_per_line(self):
        text = "# kids-activities hide\ngrad_20261014_1730\npumptrackgrosuplje_20261010_0000\n"
        self.assertEqual(dispatch_input.clean_hide(text),
                         ["grad_20261014_1730", "pumptrackgrosuplje_20261010_0000"])
        self.assertEqual(hide_event.parse_ids("\n".join(dispatch_input.clean_hide(text))),
                         ["grad_20261014_1730", "pumptrackgrosuplje_20261010_0000"])

    def test_a_decision_line_is_not_an_id(self):
        with self.assertRaises(ValueError):
            dispatch_input.clean_hide("i:grad_20261014_1730\n")

    def test_shell_syntax_is_refused(self):
        for line in ("a b", "a;b", "$(id)", "a&&b", "a|b", "a/b"):
            with self.subTest(line=line):
                with self.assertRaises(ValueError):
                    dispatch_input.clean_hide(line)


class CommandLineTests(unittest.TestCase):
    def run_main(self, kind, text):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "patch.txt"
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                code = dispatch_input.main([kind, "--out", str(out)], environ={"PATCH": text})
            return code, out.read_text(encoding="utf-8") if out.exists() else None

    def test_valid_input_is_written_and_invalid_input_writes_nothing(self):
        self.assertEqual(self.run_main("decisions", "# c\ni:a\nr:b\n"), (0, "i:a\nr:b\n"))
        code, written = self.run_main("decisions", "i:a\nrm -rf /\n")
        self.assertEqual((code, written), (1, None))

    def test_a_missing_variable_is_an_error(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "patch.txt"
            with contextlib.redirect_stderr(io.StringIO()):
                code = dispatch_input.main(["hide", "--out", str(out)], environ={})
            self.assertEqual(code, 1)
            self.assertFalse(out.exists())


class WorkflowTests(unittest.TestCase):
    """The text of the workflows, since nothing else runs them offline."""

    FILES = {"apply-decisions.yml": ("patch", "decisions"), "hide-events.yml": ("ids", "hide")}

    def workflow(self, name):
        return (ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")

    def test_dispatch_inputs_never_reach_a_shell_as_text(self):
        for name, (field, _) in self.FILES.items():
            text = self.workflow(name)
            with self.subTest(workflow=name):
                self.assertIn("workflow_dispatch:", text)
                # Only an `env:` value may carry the input. Inside `run:` the
                # expression would be pasted into the script before it runs.
                for number, line in enumerate(text.splitlines(), start=1):
                    if "${{" in line and "inputs." in line:
                        self.assertRegex(line, rf"^\s+PATCH: \$\{{\{{ inputs\.{field} \}}\}}$",
                                         f"{name}:{number}")

    def test_dispatch_inputs_go_through_the_validator(self):
        for name, (_, kind) in self.FILES.items():
            with self.subTest(workflow=name):
                self.assertRegex(self.workflow(name),
                                 rf"scripts/dispatch_input\.py {kind} --out")

    def test_both_writers_start_again_from_the_fresh_tip_after_a_lost_push(self):
        for name in self.FILES:
            text = self.workflow(name)
            with self.subTest(workflow=name):
                self.assertIn("for attempt in 1 2 3", text)
                self.assertIn("git reset --hard origin/main", text)
                self.assertNotIn("git pull", text)
                self.assertNotRegex(text, re.compile(r"git push\s+--force|git push -f"))


if __name__ == "__main__":
    unittest.main()
