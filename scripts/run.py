#!/usr/bin/env python3
"""Stage, validate and apply a discovery run without deleting database records."""

import argparse
import copy
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import state

PASSES = ("ljubljana", "slovenia", "concerts_generic", "concerts_watchlist", "free_entry", "avto_moto")
SOURCE_FIELDS = {"title", "start_time", "venue", "city", "category", "age_min", "is_free", "price_text", "url", "flags"}
RESULT_GROUPS = ("new", "updated", "expired", "hidden", "filtered", "deferred", "unchanged")


def fingerprint(event):
    return (event["title"].strip().casefold(), state.timestamp(event["start_time"]).isoformat(),
            event["venue"].strip().casefold())


def event_id(event):
    identity = json.dumps(fingerprint(event), ensure_ascii=False)
    suffix = hashlib.sha256(identity.encode()).hexdigest()[:12]
    return f"event_{state.timestamp(event['start_time']):%Y%m%d_%H%M}_{suffix}"


def validate_batch(batch):
    if not isinstance(batch, dict) or batch.get("schema_version") != 1:
        raise ValueError("Run input requires schema_version: 1")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", batch.get("run_id", "")):
        raise ValueError("Invalid run_id")
    clock = state.timestamp(batch.get("started_at"))
    if not re.fullmatch(r"[a-f0-9]{64}", batch.get("base_sha256", "")):
        raise ValueError("Run requires base_sha256 from begin")
    for field in ("candidates", "sources", "filtered", "leads", "runtime_notes"):
        if not isinstance(batch.get(field), list):
            raise ValueError(f"Run requires a {field} array")
    passes = batch.get("passes", {})
    if not isinstance(passes, dict) or set(passes) != set(PASSES):
        raise ValueError("Account for all six discovery passes")
    for name, result in passes.items():
        if not isinstance(result, dict) or result.get("status") not in {"ok", "partial", "failed", "skipped"}:
            raise ValueError(f"Invalid pass result: {name}")
        if result["status"] != "ok" and not result.get("reason"):
            raise ValueError(f"Explain incomplete pass: {name}")
    if not any(result["status"] in {"ok", "partial"} for result in passes.values()):
        raise ValueError("No discovery pass succeeded. Database unchanged")
    for source in batch["sources"]:
        if (not isinstance(source, dict) or not state.valid_url(source.get("url"))
                or source.get("status") not in {"ok", "failed", "skipped"}
                or source.get("pass") not in PASSES):
            raise ValueError("Each source requires URL, pass and status")
        if source["status"] == "ok":
            if state.timestamp(source.get("checked_at")) < clock:
                raise ValueError("Successful source checks must belong to this run")
        elif not source.get("reason"):
            raise ValueError("Explain each failed or skipped source")
    successful = {source["url"] for source in batch["sources"] if source["status"] == "ok"}
    if not successful:
        raise ValueError("No source was fetched successfully. Database unchanged")
    for name, result in passes.items():
        if result["status"] in {"ok", "partial"} and not any(
                source["pass"] == name and source["status"] == "ok" for source in batch["sources"]):
            raise ValueError(f"No successful source recorded for {name}")
    for candidate in batch["candidates"]:
        if not isinstance(candidate, dict):
            raise ValueError("Each candidate must be an object")
        unknown = set(candidate) - SOURCE_FIELDS - {"event_id"}
        if unknown:
            raise ValueError(f"Candidate contains protected or unknown fields: {sorted(unknown)}")
        item = dict(candidate)
        item.setdefault("event_id", event_id(item))
        state.validate_event(item)
        if item["url"] not in successful:
            raise ValueError(f"Candidate lacks a successfully fetched source: {item['event_id']}")
    for field in ("filtered", "leads"):
        for item in batch[field]:
            if not isinstance(item, dict) or not all(isinstance(item.get(key), str) and item[key].strip()
                                                     for key in ("title", "reason", "url")):
                raise ValueError(f"Each {field} item requires title, reason and url")
            if not state.valid_url(item["url"]):
                raise ValueError(f"Invalid {field} URL")
    if not all(isinstance(note, str) for note in batch["runtime_notes"]):
        raise ValueError("runtime_notes must contain strings")
    return clock


def merge(db, batch):
    clock = validate_batch(batch)
    if clock < state.timestamp(db["system_state"]["1"]["last_run"]):
        raise ValueError("Run clock is older than the last completed run")
    updated = copy.deepcopy(db)
    results = {group: [] for group in RESULT_GROUPS}
    results["filtered"] = copy.deepcopy(batch["filtered"])
    events = updated["events"]
    by_id = {item["event_id"]: key for key, item in events.items()}
    by_identity = {fingerprint(item): key for key, item in events.items()}
    candidates_seen = {}
    for candidate in batch["candidates"]:
        item = copy.deepcopy(candidate)
        existing_key = by_id.get(item.get("event_id"))
        identity_key = by_identity.get(fingerprint(item))
        if existing_key is not None and identity_key is not None and existing_key != identity_key:
            raise ValueError("Candidate ID and title/time/venue identify different records")
        existing_key = existing_key or identity_key
        previous = events.get(existing_key)
        item["event_id"] = previous["event_id"] if previous else item.get("event_id") or event_id(item)
        identifier = item["event_id"]
        if identifier in candidates_seen:
            if candidates_seen[identifier] != item:
                raise ValueError(f"Conflicting candidates for {identifier}")
            continue
        candidates_seen[identifier] = copy.deepcopy(item)
        reason = state.hidden_reason(updated, item)
        if reason:
            results["hidden"].append({**item, "reason": reason})
            continue
        if state.expired(item, clock):
            results["filtered"].append({**item, "reason": "Already past at the run clock"})
            continue
        if state.timestamp(item["start_time"]) > state.add_months(clock):
            results["deferred"].append({**item, "reason": "Beyond the three-month horizon"})
            continue
        if previous:
            before = copy.deepcopy(previous)
            old_identity = fingerprint(previous)
            previous.update({field: value for field, value in item.items() if field in SOURCE_FIELDS})
            previous["status"] = "active"
            if before == previous:
                results["unchanged"].append(copy.deepcopy(previous))
            else:
                results["updated"].append({**copy.deepcopy(previous), "before": before})
            if by_identity.get(old_identity) == existing_key:
                by_identity.pop(old_identity)
            by_identity[fingerprint(previous)] = existing_key
        else:
            item.update(status="active", first_seen=batch["started_at"])
            key = state.next_key(events)
            events[key] = item
            by_id[identifier] = key
            by_identity[fingerprint(item)] = key
            results["new"].append(copy.deepcopy(item))
    for item in events.values():
        if item.get("status", "active") != "active":
            continue
        reason = state.hidden_reason(updated, item)
        if reason:
            item["status"] = "hidden"
        elif state.expired(item, clock):
            item["status"] = "expired"
            results["expired"].append(copy.deepcopy(item))
    system = updated["system_state"]["1"]
    system.update(last_run=batch["started_at"], latest_run=batch["run_id"],
                  total_active_events=len(state.active_events(updated)))
    state.validate(updated)
    return updated, results


def begin(args):
    db = state.load(args.db)
    clock = state.timestamp(args.at) if args.at else datetime.now(state.TZ).replace(microsecond=0)
    if clock < state.timestamp(db["system_state"]["1"]["last_run"]):
        raise ValueError("Run clock is older than the database")
    checksum = state.digest(args.db)
    run_id = f"{clock.astimezone(timezone.utc):%Y%m%dT%H%M%SZ}_{checksum[:8]}"
    target = Path(args.db).resolve().parent / ".work" / run_id / "input.json"
    if target.exists():
        raise ValueError(f"Run input already exists: {target}")
    batch = {
        "schema_version": 1, "run_id": run_id, "started_at": clock.isoformat(),
        "base_sha256": checksum, "candidates": [], "sources": [],
        "passes": {name: {"status": "skipped", "reason": "Not attempted yet"} for name in PASSES},
        "filtered": [], "leads": [], "runtime_notes": [],
    }
    state.atomic_write(target, state.json_text(batch))
    print(target)


def render_outputs(db_path, db=None):
    import report
    db = db or state.load(db_path)
    root = Path(db_path).resolve().parent
    outputs = {}
    latest = db["system_state"]["1"].get("latest_run")
    if latest:
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", latest):
            raise ValueError("Invalid latest_run reference")
        record = json.loads((root / "runs" / f"{latest}.json").read_text(encoding="utf-8"))
        if record["input"]["run_id"] != latest or record["input"]["started_at"] != db["system_state"]["1"]["last_run"]:
            raise ValueError("Latest run does not match database state")
        outputs[root / "diff.md"] = report.build(record)
    return outputs


def apply(args):
    import report
    batch = json.loads(Path(args.input).read_text(encoding="utf-8"))
    validate_batch(batch)
    root = Path(args.db).resolve().parent
    log_path = root / "runs" / f"{batch['run_id']}.json"
    with state.locked(args.db):
        current_hash = state.digest(args.db)
        record = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else None
        if record and record["input"] != batch:
            raise ValueError("Run ID already exists with different input")
        if record and current_hash == record["after_sha256"]:
            if not args.dry_run:
                for path, content in render_outputs(args.db).items():
                    state.atomic_write(path, content)
            print(f"Already applied: {batch['run_id']}")
            return
        if current_hash != batch["base_sha256"]:
            raise ValueError("Database changed since begin. Start a fresh run against the latest state")
        updated, results = merge(state.load(args.db), batch)
        content = state.json_text(updated)
        computed = {"schema_version": 1, "input": batch, "results": results,
                    "after_sha256": hashlib.sha256(content.encode()).hexdigest()}
        if record and record != computed:
            raise ValueError("Retry would change an existing run record. Use the original script version")
        record_exists = record is not None
        record = computed
        diff_md = report.build(record)
        print(json.dumps({group: len(items) for group, items in results.items()}, sort_keys=True))
        if args.dry_run:
            return
        if not record_exists:
            state.atomic_write(log_path, state.json_text(record))
        state.atomic_write(args.db, content)
        state.atomic_write(root / "diff.md", diff_md)


def check(args):
    outputs = render_outputs(args.db)
    stale = [str(path) for path, content in outputs.items()
             if not path.exists() or path.read_text(encoding="utf-8") != content]
    if stale:
        raise ValueError(f"Generated output is stale: {', '.join(stale)}. Run scripts/run.py render")
    print("Database and generated reports are valid")


def render_all(args):
    with state.locked(args.db):
        for path, content in render_outputs(args.db).items():
            state.atomic_write(path, content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=state.DB_PATH)
    commands = parser.add_subparsers(dest="command", required=True)
    start = commands.add_parser("begin", help="write a staged input, leaving the database unchanged")
    start.add_argument("--at", help="explicit timezone-aware run clock for replay/testing")
    start.set_defaults(func=begin)
    finish = commands.add_parser("apply", help="validate and merge a completed run")
    finish.add_argument("input", type=Path)
    finish.add_argument("--dry-run", action="store_true")
    finish.set_defaults(func=apply)
    commands.add_parser("check", help="validate state and check generated output").set_defaults(func=check)
    commands.add_parser("render", help="regenerate the sweep report from committed state").set_defaults(func=render_all)
    commands.add_parser("validate", help="validate only the database").set_defaults(func=lambda args: state.load(args.db))
    args = parser.parse_args()
    try:
        args.func(args)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()