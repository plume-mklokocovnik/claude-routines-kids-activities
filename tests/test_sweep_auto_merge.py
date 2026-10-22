import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "sweep-auto-merge.yml"


class SweepAutoMergeWorkflowTests(unittest.TestCase):
    """The text of the workflow, since nothing else runs it offline."""

    def setUp(self):
        self.text = WORKFLOW.read_text(encoding="utf-8")

    def allowlist(self):
        match = re.search(r"^\s+([^\s)]+)\) ;;$", self.text, flags=re.MULTILINE)
        self.assertIsNotNone(match, "no case allowlist in the guardrail step")
        return match.group(1).split("|")

    def test_allowlist_covers_every_file_a_sweep_may_stage(self):
        # routine.md section 5: database, sweep report, run record and the
        # source index with evidence from the run.
        self.assertEqual(
            sorted(self.allowlist()),
            ["db.json", "diff.md", "reference/*.md", "runs/*.json"],
        )

    def test_allowlist_keeps_code_and_instructions_out(self):
        for pattern in self.allowlist():
            self.assertFalse(pattern.startswith(("scripts", "app", ".github", "tests")), pattern)
            self.assertNotIn(pattern, ("AGENTS.md", "routine.md", "*"))

    def test_a_refused_merge_fails_the_run(self):
        guard = self.text[self.text.index("- name: Guardrails"):self.text.index("- name: Re-validate")]
        # Every refusal is an error annotation followed by a failing exit. The
        # old warning-and-exit-0 shape left a skipped sweep as a green run.
        self.assertNotIn("::warning::", guard)
        self.assertEqual(guard.count("::error::"), 3)
        # One exit for the diverged case, one shared by the collected problems.
        self.assertEqual(guard.count("exit 1"), 2)
        # The benign case, a branch already level with main, stays green.
        self.assertIn("Branch is already level with main", guard)
        self.assertEqual(guard.count("exit 0"), 1)

    def test_never_force_pushes_or_merges(self):
        self.assertNotRegex(self.text, re.compile(r"git push\s+--force|git push -f"))
        self.assertNotRegex(self.text, re.compile(r"git (merge(?!-base)|rebase|pull)\b"))
        self.assertIn("git push origin HEAD:main", self.text)


if __name__ == "__main__":
    unittest.main()
