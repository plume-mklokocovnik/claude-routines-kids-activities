import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import state


def event(**changes):
    result = {
        "event_id": "sample_20261010_1000", "title": "Family workshop",
        "start_time": "2026-10-10T10:00:00+02:00", "venue": "Museum",
        "city": "Ljubljana", "category": "delavnica", "age_min": None,
        "is_free": None, "price_text": "", "url": "https://example.org/event",
        "flags": [], "status": "active",
        "first_seen": "2026-09-24T07:22:48Z", "custom_metadata": {"keep": True},
    }
    result.update(changes)
    return result


def database():
    return {
        "events": {"1": event()}, "user_rules": {"1": {}}, "hidden_events": {},
        "system_state": {"1": {"last_run": "2026-09-28T10:00:00+02:00"}},
        "unknown_table": {"keep": "all data"},
    }


class StateTests(unittest.TestCase):
    def test_preserves_all_tables_and_fields(self):
        db = database()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "db.json"
            state.save(path, db)
            self.assertEqual(state.load(path), db)

    def test_failed_replace_keeps_original_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "db.json"
            state.atomic_write(path, "original")
            with patch("state.os.replace", side_effect=OSError("disk failure")):
                with self.assertRaises(OSError):
                    state.atomic_write(path, "replacement")
            self.assertEqual(path.read_text(), "original")
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_unknown_time_expires_after_local_day(self):
        item = event(start_time="2026-09-28T00:00:00+02:00", flags=["time_unknown"])
        self.assertFalse(state.expired(item, state.timestamp("2026-09-28T23:00:00+02:00")))
        self.assertTrue(state.expired(item, state.timestamp("2026-09-29T00:00:00+02:00")))

    def test_calendar_horizon_accounts_for_dst_and_month_end(self):
        self.assertEqual(state.add_months(state.timestamp("2026-08-31T10:00:00+02:00")).isoformat(),
                         "2026-11-30T10:00:00+01:00")

    def test_rules_are_case_insensitive_and_do_not_mutate(self):
        db = database()
        db["user_rules"]["1"]["exclude_keywords"] = ["FAMILY"]
        before = copy.deepcopy(db)
        self.assertEqual(state.active_events(db), [])
        self.assertEqual(state.find(db, "sample"), [])
        self.assertEqual(db, before)

    def test_overlapping_writer_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "db.json"
            with state.locked(path):
                with self.assertRaisesRegex(ValueError, "Another process"):
                    with state.locked(path):
                        self.fail("lock was bypassed")

    def test_legacy_hidden_occurrence_survives_new_id_scheme(self):
        db = database()
        db["events"] = {}
        db["hidden_events"]["1"] = {**event(), "scope": "event"}
        discovered = event(event_id="generated_new_id")
        self.assertIn("hidden occurrence", state.hidden_reason(db, discovered))
        db["hidden_events"]["1"]["active"] = False
        self.assertIsNone(state.hidden_reason(db, discovered))


if __name__ == "__main__":
    unittest.main()