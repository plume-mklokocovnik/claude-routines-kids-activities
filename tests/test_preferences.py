import contextlib
import io
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import hide_event
import state
from test_state import database, event


class PreferenceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "db.json"
        self.db = database()
        state.save(self.path, self.db)
        self.args = Namespace(db=str(self.path), query="sample_20261010_1000", scope="event", reason="test")
        self.output = contextlib.redirect_stdout(io.StringIO())
        self.output.__enter__()
        self.addCleanup(self.output.__exit__, None, None, None)

    def test_hide_and_restore_preserve_the_event_and_the_audit(self):
        self.assertEqual(hide_event.cmd_hide(self.args), 0)
        hidden = state.load(self.path)
        self.assertEqual(hidden["events"]["1"], {**self.db["events"]["1"], "status": "hidden"})
        self.assertEqual(hidden["system_state"]["1"]["total_active_events"], 0)
        self.assertEqual(hide_event.cmd_unhide(self.args), 0)
        restored = state.load(self.path)
        self.assertEqual(restored["events"], self.db["events"])
        self.assertFalse(restored["hidden_events"]["1"]["active"])
        self.assertIn("restored_at", restored["hidden_events"]["1"])
        self.assertEqual(restored["unknown_table"], self.db["unknown_table"])

    def test_hiding_and_restoring_write_the_database_and_nothing_else(self):
        self.assertEqual(hide_event.cmd_hide(self.args), 0)
        self.assertEqual(hide_event.cmd_unhide(self.args), 0)
        self.assertEqual([entry.name for entry in self.path.parent.iterdir()], ["db.json"])

    def test_a_hidden_event_leaves_the_swipe_deck_and_comes_back(self):
        import swipe
        ids = lambda: [item["event_id"] for item in swipe.deck(state.load(self.path))]
        self.assertEqual(ids(), ["sample_20261010_1000"])
        self.assertEqual(hide_event.cmd_hide(self.args), 0)
        self.assertEqual(ids(), [])
        self.assertEqual(hide_event.cmd_unhide(self.args), 0)
        self.assertEqual(ids(), ["sample_20261010_1000"])

    def test_hiding_an_already_hidden_event_changes_nothing(self):
        self.assertEqual(hide_event.cmd_hide(self.args), 0)
        before = self.path.read_bytes()
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(hide_event.cmd_hide(self.args), 1)
        self.assertEqual(self.path.read_bytes(), before)

    def test_ambiguous_query_changes_nothing(self):
        self.db["events"]["2"] = event(event_id="other", title="Family concert", category="koncert")
        state.save(self.path, self.db)
        before = self.path.read_bytes()
        self.args.query = "Family"
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(hide_event.cmd_hide(self.args), 2)
            self.args.scope = "series"
            self.assertEqual(hide_event.cmd_hide(self.args), 2)
        self.assertEqual(self.path.read_bytes(), before)


class HideFromAppTests(unittest.TestCase):
    """`hide_event.py apply`: the batch behind the app's hide-all-Zavrnjeno button."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "db.json"
        self.patch = Path(self.directory.name) / "hide.txt"
        self.db = database()
        self.db["events"]["2"] = event(event_id="second", title="Puppet show", category="lutke",
                                       decision="rejected", decided_at="2026-09-30T08:00:00Z")
        self.db["events"]["3"] = event(event_id="third", title="Puppet show", category="lutke",
                                       start_time="2026-10-17T10:00:00+02:00")
        state.save(self.path, self.db)
        output = contextlib.redirect_stdout(io.StringIO())
        output.__enter__()
        self.addCleanup(output.__exit__, None, None, None)

    def run_patch(self, text, reason="hidden from the app"):
        self.patch.write_text(text, encoding="utf-8")
        with contextlib.redirect_stderr(io.StringIO()) as errors:
            code = hide_event.cmd_apply(Namespace(db=str(self.path), patch=str(self.patch), reason=reason))
        return code, errors.getvalue()

    def test_each_id_is_hidden_alone_with_the_app_reason(self):
        self.assertEqual(self.run_patch("# kids-activities hide\nsecond\n")[0], 0)
        stored = state.load(self.path)
        self.assertEqual(stored["events"]["2"]["status"], "hidden")
        # A show with the same title on another date is not a series hide.
        self.assertEqual(stored["events"]["3"].get("status", "active"), "active")
        self.assertEqual(stored["user_rules"]["1"]["exclude_event_ids"], ["second"])
        self.assertNotIn("exclude_keywords", stored["user_rules"]["1"])
        self.assertNotIn("exclude_venues", stored["user_rules"]["1"])
        reference = stored["hidden_events"]["1"]
        self.assertEqual((reference["scope"], reference["event_id"], reference["reason"]),
                         ("event", "second", "hidden from the app"))

    def test_the_decision_and_the_rest_of_the_row_survive(self):
        self.run_patch("second\n")
        row = state.load(self.path)["events"]["2"]
        self.assertEqual({**row, "status": "active"}, self.db["events"]["2"] | {"status": "active"})
        self.assertEqual(row["decision"], "rejected")

    def test_hidden_events_leave_the_app_lists_and_come_back_with_their_decision(self):
        import swipe
        rejected = lambda: [item["event_id"] for item in swipe.decided(state.load(self.path))["rejected"]]
        self.assertEqual(rejected(), ["second"])
        self.run_patch("second\n")
        self.assertEqual(rejected(), [])
        self.assertEqual(swipe.counts(state.load(self.path))["rejected"], 0)
        self.assertEqual(hide_event.cmd_unhide(Namespace(db=str(self.path), query="second")), 0)
        self.assertEqual(rejected(), ["second"])

    def test_applying_the_same_list_twice_changes_nothing_the_second_time(self):
        self.run_patch("second\nthird\n")
        before = self.path.read_bytes()
        self.run_patch("second\nthird\n")
        self.assertEqual(self.path.read_bytes(), before)

    def test_unknown_ids_are_reported_and_never_invented(self):
        code, errors = self.run_patch("ghost\nsecond\n")
        self.assertEqual(code, 0)
        self.assertIn("ghost", errors)
        stored = state.load(self.path)
        self.assertEqual(stored["user_rules"]["1"]["exclude_event_ids"], ["second"])
        self.assertEqual(len(stored["events"]), 3)

    def test_a_fragment_is_never_treated_as_an_id(self):
        code, errors = self.run_patch("Puppet\n")
        self.assertEqual(code, 0)
        self.assertIn("Puppet", errors)
        self.assertEqual(state.load(self.path)["events"]["2"].get("status", "active"), "active")

    def test_malformed_lines_are_refused_and_change_nothing(self):
        before = self.path.read_bytes()
        for text in ("second third\n", "r:second\n"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.run_patch(text)
        self.assertEqual(self.path.read_bytes(), before)

    def test_blank_lines_comments_and_repeats_are_ignored(self):
        self.assertEqual(hide_event.parse_ids("# note\n\n second \nsecond\nthird\n"), ["second", "third"])

    def test_an_empty_list_leaves_the_database_alone(self):
        before = self.path.read_bytes()
        self.assertEqual(self.run_patch("# nothing\n")[0], 0)
        self.assertEqual(self.path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
