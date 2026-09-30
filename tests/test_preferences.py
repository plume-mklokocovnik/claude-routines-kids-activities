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


if __name__ == "__main__":
    unittest.main()
