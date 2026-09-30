import contextlib
import copy
import io
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import state
import swipe
from test_state import database, event


class SwipeStateTests(unittest.TestCase):
    def setUp(self):
        self.db = database()
        self.db["events"]["2"] = event(event_id="second", title="Puppet show",
                                       start_time="2026-10-09T09:00:00+02:00", category="lutke")
        # Either side of the daylight-saving change, where sorting the raw
        # strings would put the later instant first.
        self.db["events"]["3"] = event(event_id="after_dst", title="Late show",
                                       start_time="2026-10-25T02:30:00+01:00", category="kino")
        self.db["events"]["4"] = event(event_id="before_dst", title="Early show",
                                       start_time="2026-10-25T03:00:00+02:00", category="kino")

    def test_deck_is_chronological_and_drops_decided_events(self):
        self.assertEqual([item["event_id"] for item in swipe.deck(self.db)],
                         ["second", "sample_20261010_1000", "before_dst", "after_dst"])
        swipe.set_decision(self.db, self.db["events"]["2"], "maybe")
        self.assertEqual([item["event_id"] for item in swipe.deck(self.db)],
                         ["sample_20261010_1000", "before_dst", "after_dst"])
        self.assertEqual(swipe.counts(self.db),
                         {"interested": 0, "maybe": 1, "rejected": 0,
                          "undecided": 3, "decided": 1, "total": 4})

    def test_hidden_and_inactive_events_never_enter_the_deck(self):
        self.db["user_rules"]["1"]["exclude_event_ids"] = ["second"]
        self.db["events"]["3"]["status"] = "expired"
        self.db["events"]["4"]["status"] = "hidden"
        self.assertEqual([item["event_id"] for item in swipe.deck(self.db)],
                         ["sample_20261010_1000"])

    def test_decided_events_stay_in_review_after_expiry(self):
        row = self.db["events"]["3"]
        swipe.set_decision(self.db, row, "interested")
        row["status"] = "expired"
        self.assertEqual([item["event_id"] for item in swipe.decided(self.db)["interested"]],
                         ["after_dst"])
        self.assertEqual(swipe.counts(self.db)["interested"], 1)

    def test_decision_is_independent_of_star_and_hide_rules(self):
        before = copy.deepcopy(self.db)
        event_row = self.db["events"]["1"]
        swipe.set_decision(self.db, event_row, "rejected")
        self.assertEqual(event_row["decision"], "rejected")
        self.assertTrue(event_row["starred"])
        self.assertEqual(event_row["status"], "active")
        self.assertEqual(self.db["user_rules"], before["user_rules"])
        self.assertEqual(self.db["hidden_events"], before["hidden_events"])
        self.assertEqual(self.db["unknown_table"], before["unknown_table"])
        self.assertEqual(event_row["custom_metadata"], {"keep": True})
        self.assertIn(event_row, state.active_events(self.db))

    def test_repeating_the_same_category_writes_nothing(self):
        event_row = self.db["events"]["1"]
        self.assertEqual(swipe.set_decision(self.db, event_row, "maybe"), (True, None))
        stamp = event_row["decided_at"]
        self.assertEqual(swipe.set_decision(self.db, event_row, "maybe"), (False, "maybe"))
        self.assertEqual(event_row["decided_at"], stamp)
        self.assertEqual(len(self.db["decision_log"]), 1)

    def test_undo_walks_back_through_every_change(self):
        event_row = self.db["events"]["1"]
        swipe.set_decision(self.db, event_row, "interested", at="2026-09-30T08:00:00Z")
        swipe.set_decision(self.db, event_row, "rejected", at="2026-09-30T09:00:00Z")
        swipe.clear_decision(self.db, event_row, at="2026-09-30T10:00:00Z")

        swipe.undo(self.db)
        self.assertEqual(event_row["decision"], "rejected")
        self.assertEqual(event_row["decided_at"], "2026-09-30T09:00:00Z")
        swipe.undo(self.db)
        self.assertEqual(event_row["decision"], "interested")
        self.assertEqual(event_row["decided_at"], "2026-09-30T08:00:00Z")
        swipe.undo(self.db)
        self.assertNotIn("decision", event_row)
        self.assertNotIn("decided_at", event_row)
        self.assertEqual(swipe.undo(self.db), (None, None))
        self.assertEqual(len(self.db["decision_log"]), 3)
        self.assertTrue(all(row["undone"] for row in self.db["decision_log"].values()))

    def test_undo_is_last_in_first_out_across_events(self):
        first, second = self.db["events"]["1"], self.db["events"]["2"]
        swipe.set_decision(self.db, first, "interested")
        swipe.set_decision(self.db, second, "rejected")
        swipe.undo(self.db)
        self.assertNotIn("decision", second)
        self.assertEqual(first["decision"], "interested")
        swipe.set_decision(self.db, second, "maybe")
        swipe.undo(self.db)
        self.assertNotIn("decision", second)
        swipe.undo(self.db)
        self.assertNotIn("decision", first)

    def test_undone_rows_are_kept_as_an_audit_trail(self):
        swipe.set_decision(self.db, self.db["events"]["1"], "maybe", at="2026-09-30T08:00:00Z")
        swipe.undo(self.db, at="2026-09-30T08:05:00Z")
        row = self.db["decision_log"]["1"]
        self.assertEqual(row["action"], "set")
        self.assertIsNone(row["before"])
        self.assertEqual(row["after"], "maybe")
        self.assertEqual(row["at"], "2026-09-30T08:00:00Z")
        self.assertEqual(row["undone_at"], "2026-09-30T08:05:00Z")

    def test_clearing_an_undecided_event_is_a_no_op(self):
        self.assertEqual(swipe.clear_decision(self.db, self.db["events"]["1"]), (False, None))
        self.assertNotIn("decision_log", self.db)

    def test_unknown_category_is_refused(self):
        with self.assertRaisesRegex(ValueError, "Unknown category"):
            swipe.set_decision(self.db, self.db["events"]["1"], "hmm")
        self.assertNotIn("decision", self.db["events"]["1"])

    def test_undo_without_its_event_row_reports_instead_of_guessing(self):
        swipe.set_decision(self.db, self.db["events"]["1"], "maybe")
        self.db["events"]["1"]["event_id"] = "renamed_by_hand"
        with self.assertRaisesRegex(ValueError, "Cannot undo"):
            swipe.undo(self.db)

    def test_validation_rejects_unknown_stored_values(self):
        self.db["events"]["1"]["decision"] = "unsure"
        with self.assertRaisesRegex(ValueError, "decision must be one of"):
            state.validate(self.db)
        self.db["events"]["1"]["decision"] = "maybe"
        self.db["decision_log"] = {"1": {"before": "nope", "after": None}}
        with self.assertRaisesRegex(ValueError, "decision_log before"):
            state.validate(self.db)


class PatchTests(unittest.TestCase):
    def setUp(self):
        self.db = database()
        self.db["events"]["2"] = event(event_id="second", title="Puppet show",
                                       start_time="2026-10-09T09:00:00+02:00", category="lutke")

    def test_reads_codes_and_ignores_comments_and_blanks(self):
        text = ("# kids-activities decisions\n\n"
                "i:alpha\n"
                "  m:beta  \n"
                "R:gamma\n"
                "c:delta\n")
        self.assertEqual(swipe.parse_patch(text),
                         [("alpha", "interested"), ("beta", "maybe"),
                          ("gamma", "rejected"), ("delta", None)])

    def test_malformed_lines_name_the_line_and_change_nothing(self):
        for text in ("nonsense\n", "x:alpha\n", "i:\n", "i\n", ":alpha\n"):
            with self.subTest(text=text):
                with self.assertRaisesRegex(ValueError, "Line 1"):
                    swipe.parse_patch(text)

    def test_apply_sets_clears_and_reports_unknown_ids(self):
        entries = [("sample_20261010_1000", "interested"), ("second", "maybe"),
                   ("ghost", "rejected")]
        changed, unchanged, skipped = swipe.apply_patch(self.db, entries)
        self.assertEqual((changed, unchanged, skipped),
                         (["sample_20261010_1000", "second"], [], ["ghost"]))
        self.assertEqual(self.db["events"]["1"]["decision"], "interested")
        self.assertEqual(self.db["events"]["2"]["decision"], "maybe")

        changed, unchanged, skipped = swipe.apply_patch(self.db, [("second", None)])
        self.assertEqual((changed, unchanged, skipped), (["second"], [], []))
        self.assertNotIn("decision", self.db["events"]["2"])

    def test_applying_the_same_patch_twice_changes_nothing_the_second_time(self):
        entries = [("sample_20261010_1000", "rejected"), ("second", None)]
        swipe.apply_patch(self.db, entries)
        before = copy.deepcopy(self.db)
        changed, unchanged, _ = swipe.apply_patch(self.db, entries)
        self.assertEqual(changed, [])
        self.assertEqual(unchanged, ["sample_20261010_1000", "second"])
        self.assertEqual(self.db, before)

    def test_every_applied_change_is_undoable(self):
        swipe.apply_patch(self.db, [("sample_20261010_1000", "maybe"), ("second", "rejected")])
        self.assertEqual(len(self.db["decision_log"]), 2)
        swipe.undo(self.db)
        self.assertNotIn("decision", self.db["events"]["2"])
        self.assertEqual(self.db["events"]["1"]["decision"], "maybe")


class SwipeCommandTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "db.json"
        self.original = database()
        state.save(self.path, self.original)
        self.args = Namespace(db=str(self.path), query="sample_20261010_1000",
                              category="interested")
        output = contextlib.redirect_stdout(io.StringIO())
        output.__enter__()
        self.addCleanup(output.__exit__, None, None, None)

    def test_set_clear_and_undo_survive_a_reload(self):
        self.assertEqual(swipe.cmd_set(self.args), 0)
        self.assertEqual(state.load(self.path)["events"]["1"]["decision"], "interested")

        self.assertEqual(swipe.cmd_clear(self.args), 0)
        self.assertNotIn("decision", state.load(self.path)["events"]["1"])

        # A new process reading the stored log can still reverse the last change.
        self.assertEqual(swipe.cmd_undo(self.args), 0)
        reloaded = state.load(self.path)
        self.assertEqual(reloaded["events"]["1"]["decision"], "interested")
        self.assertEqual(swipe.cmd_undo(self.args), 0)
        self.assertNotIn("decision", state.load(self.path)["events"]["1"])
        self.assertEqual(swipe.cmd_undo(self.args), 0)  # nothing left, still fine

    def test_reports_do_not_change_and_records_are_preserved(self):
        self.assertEqual(swipe.cmd_set(self.args), 0)
        stored = state.load(self.path)
        self.assertEqual(stored["unknown_table"], self.original["unknown_table"])
        self.assertEqual(stored["hidden_events"], self.original["hidden_events"])
        self.assertEqual(stored["user_rules"], self.original["user_rules"])
        self.assertEqual(stored["system_state"]["1"]["total_active_events"], 1)
        self.assertFalse((self.path.parent / "currently_active.md").exists())

    def test_unknown_query_changes_nothing(self):
        before = self.path.read_bytes()
        self.args.query = "nothing like this"
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(swipe.cmd_set(self.args), 1)
            self.assertEqual(swipe.cmd_clear(self.args), 1)
        self.assertEqual(self.path.read_bytes(), before)

    def test_ambiguous_query_changes_nothing(self):
        db = state.load(self.path)
        db["events"]["2"] = event(event_id="other", title="Family concert", category="koncert")
        state.save(self.path, db)
        before = self.path.read_bytes()
        self.args.query = "Family"
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(swipe.cmd_set(self.args), 2)
        self.assertEqual(self.path.read_bytes(), before)

    def test_apply_folds_in_a_patch_file(self):
        patch = self.path.parent / "decisions.txt"
        patch.write_text("# from the app\ni:sample_20261010_1000\n", encoding="utf-8")
        self.assertEqual(swipe.cmd_apply(Namespace(db=str(self.path), patch=str(patch))), 0)
        self.assertEqual(state.load(self.path)["events"]["1"]["decision"], "interested")

        # Nothing to change means nothing written.
        before = self.path.read_bytes()
        self.assertEqual(swipe.cmd_apply(Namespace(db=str(self.path), patch=str(patch))), 0)
        self.assertEqual(self.path.read_bytes(), before)

    def test_apply_of_an_empty_patch_leaves_the_database_alone(self):
        patch = self.path.parent / "empty.txt"
        patch.write_text("# nothing here\n\n", encoding="utf-8")
        before = self.path.read_bytes()
        self.assertEqual(swipe.cmd_apply(Namespace(db=str(self.path), patch=str(patch))), 0)
        self.assertEqual(self.path.read_bytes(), before)

    def test_apply_of_an_unknown_id_changes_nothing(self):
        patch = self.path.parent / "ghost.txt"
        patch.write_text("m:not_in_the_database\n", encoding="utf-8")
        before = self.path.read_bytes()
        with contextlib.redirect_stderr(io.StringIO()) as captured:
            self.assertEqual(swipe.cmd_apply(Namespace(db=str(self.path), patch=str(patch))), 0)
        self.assertIn("not_in_the_database", captured.getvalue())
        self.assertEqual(self.path.read_bytes(), before)

    def test_list_and_stats_are_read_only(self):
        self.assertEqual(swipe.cmd_set(self.args), 0)
        before = self.path.read_bytes()
        self.assertEqual(swipe.cmd_list(Namespace(db=str(self.path), category=None)), 0)
        self.assertEqual(swipe.cmd_stats(self.args), 0)
        self.assertEqual(self.path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
