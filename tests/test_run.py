import contextlib
import copy
import io
import json
import subprocess
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run
import report
import state
from test_state import database, event


def batch():
    return {
        "schema_version": 1, "run_id": "20260928_test", "started_at": "2026-09-28T12:00:00+02:00",
        "base_sha256": "a" * 64, "candidates": [], "filtered": [], "leads": [], "runtime_notes": [],
        "sources": [{"url": "https://example.org/event", "pass": "ljubljana", "status": "ok",
                     "checked_at": "2026-09-28T12:01:00+02:00"}],
        "passes": {name: {"status": "ok"} if name == "ljubljana" else {"status": "skipped", "reason": "test"}
                   for name in run.PASSES},
    }


def candidate(**changes):
    return {key: value for key, value in event(**changes).items() if key in run.SOURCE_FIELDS or key == "event_id"}


class RunTests(unittest.TestCase):
    def test_refresh_preserves_decision_unknown_fields_and_tables(self):
        db, payload = database(), batch()
        db["events"]["1"]["decision"] = "interested"
        db["events"]["1"]["decided_at"] = "2026-09-27T08:00:00Z"
        payload["candidates"] = [candidate(price_text="8 EUR")]
        before = copy.deepcopy(db)
        merged, results = run.merge(db, payload)
        self.assertEqual(db, before)
        self.assertEqual(merged["events"]["1"]["price_text"], "8 EUR")
        self.assertEqual(merged["events"]["1"]["decision"], "interested")
        self.assertEqual(merged["events"]["1"]["decided_at"], "2026-09-27T08:00:00Z")
        self.assertEqual(merged["events"]["1"]["custom_metadata"], {"keep": True})
        self.assertEqual(merged["unknown_table"], db["unknown_table"])
        self.assertEqual(results["updated"][0]["before"], db["events"]["1"])

    def test_expiry_preserves_records_and_preferences(self):
        db = database()
        db["events"]["1"]["start_time"] = "2026-09-27T10:00:00+02:00"
        merged, results = run.merge(db, batch())
        self.assertEqual(merged["events"]["1"], {**db["events"]["1"], "status": "expired"})
        self.assertEqual(len(results["expired"]), 1)

    def test_hidden_candidates_cannot_return_and_future_is_deferred(self):
        db, payload = database(), batch()
        db["user_rules"]["1"]["exclude_event_ids"] = ["sample_20261010_1000"]
        payload["candidates"] = [candidate(), candidate(event_id="later", start_time="2027-01-01T10:00:00+01:00")]
        merged, results = run.merge(db, payload)
        self.assertEqual(len(merged["events"]), 1)
        self.assertEqual(merged["events"]["1"]["status"], "hidden")
        self.assertEqual(len(results["hidden"]), 1)
        self.assertEqual(len(results["deferred"]), 1)

    def test_natural_identity_preserves_legacy_id_and_deduplicates(self):
        payload = batch()
        payload["candidates"] = [candidate(event_id="new-style-id"), candidate(event_id="new-style-id")]
        merged, results = run.merge(database(), payload)
        self.assertEqual(len(merged["events"]), 1)
        self.assertEqual(merged["events"]["1"]["event_id"], "sample_20261010_1000")
        self.assertEqual(len(results["unchanged"]), 1)

    def test_conflicting_and_unverified_candidates_are_rejected(self):
        for candidates in ([candidate(), candidate(price_text="different")],
                           [candidate(url="https://example.org/not-fetched")],
                           [{**candidate(), "decision": "interested"}],
                           [candidate(start_time="2026-10-10T10:00:00")]):
            with self.subTest(candidates=candidates):
                payload = batch()
                payload["candidates"] = candidates
                with self.assertRaises(ValueError):
                    run.merge(database(), payload)

    def test_total_outage_is_rejected(self):
        payload = batch()
        payload["sources"][0].update(status="failed", reason="network")
        with self.assertRaisesRegex(ValueError, "No source"):
            run.merge(database(), payload)

    def test_new_id_and_report_are_repeatable(self):
        payload = batch()
        item = candidate(title="New workshop", price_text="Adults 8 EUR, children free")
        item.pop("event_id")
        payload["candidates"] = [item]
        merged, results = run.merge(database(), payload)
        self.assertEqual(len(merged["events"]), 2)
        self.assertEqual(results["new"][0]["event_id"], run.event_id(item))
        record = {"input": payload, "results": results}
        self.assertEqual(report.build(record), report.build(record))
        self.assertIn("Adults 8 EUR, children free", report.build(record))
        self.assertIn(results["new"][0]["event_id"], report.build(record))

    def test_stale_source_evidence_is_rejected(self):
        payload = batch()
        payload["sources"][0]["checked_at"] = "2026-09-27T12:00:00+02:00"
        with self.assertRaisesRegex(ValueError, "this run"):
            run.merge(database(), payload)

    def test_interrupted_apply_recovers_without_rewriting_record(self):
        for failed_file in ("db.json", "diff.md"):
            with self.subTest(failed_file=failed_file), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                path, staged = root / "db.json", root / "input.json"
                state.save(path, database())
                payload = batch()
                payload["base_sha256"] = state.digest(path)
                state.atomic_write(staged, state.json_text(payload))
                args = Namespace(db=path, input=staged, dry_run=False)
                write = state.atomic_write

                def interrupted_write(target, content):
                    if Path(target).name == failed_file:
                        raise OSError("simulated interruption")
                    write(target, content)

                with contextlib.redirect_stdout(io.StringIO()):
                    with patch("state.atomic_write", side_effect=interrupted_write):
                        with self.assertRaisesRegex(OSError, "interruption"):
                            run.apply(args)
                    log = root / "runs" / f"{payload['run_id']}.json"
                    before = log.read_bytes()
                    run.apply(args)
                    run.check(args)
                    self.assertEqual(log.read_bytes(), before)

    def test_cli_flow_outside_repository(self):
        scripts = Path(__file__).resolve().parents[1] / "scripts"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "db.json"
            state.save(path, database())

            def command(script, *arguments):
                result = subprocess.run([sys.executable, str(scripts / script), "--db", str(path), *arguments],
                                        cwd=root, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                return result.stdout

            staged = Path(command("run.py", "begin", "--at", "2026-09-28T12:00:00+02:00").strip())
            scaffold = json.loads(staged.read_text())
            payload = batch()
            payload.update({key: scaffold[key] for key in ("run_id", "started_at", "base_sha256")})
            state.atomic_write(staged, state.json_text(payload))
            before = path.read_bytes()
            command("run.py", "apply", str(staged), "--dry-run")
            self.assertEqual(path.read_bytes(), before)
            command("run.py", "apply", str(staged))
            command("run.py", "check")
            self.assertEqual(sorted(entry.name for entry in root.iterdir()
                                    if entry.is_file() and not entry.name.startswith(".")),
                             ["db.json", "diff.md"])  # the live view is the app, not a file
            command("swipe.py", "set", "sample_20261010_1000", "interested")
            command("run.py", "check")  # a decision must not stale the report
            command("hide_event.py", "hide", "sample_20261010_1000")
            command("run.py", "check")
            command("hide_event.py", "unhide", "sample_20261010_1000")
            command("run.py", "check")

    def test_apply_dry_run_retry_and_stale_write(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()):
            root = Path(directory)
            path, staged = root / "db.json", root / "input.json"
            state.save(path, database())
            payload = batch()
            payload["base_sha256"] = state.digest(path)
            state.atomic_write(staged, state.json_text(payload))
            args = Namespace(db=path, input=staged, dry_run=True)
            before = path.read_bytes()
            run.apply(args)
            self.assertEqual(path.read_bytes(), before)
            self.assertFalse((root / "runs").exists())
            args.dry_run = False
            run.apply(args)
            after = path.read_bytes()
            run.apply(args)
            self.assertEqual(path.read_bytes(), after)
            run.check(args)
            db = state.load(path)
            db["events"]["1"]["decision"] = "maybe"
            state.save(path, db)
            with self.assertRaisesRegex(ValueError, "Database changed"):
                run.apply(args)


if __name__ == "__main__":
    unittest.main()