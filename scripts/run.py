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


def words(text):
    return " ".join(re.sub(r"\W+", " ", text.casefold()).split())


def venue_parts(venue):
    return [part for part in (words(re.sub(r"\([^)]*\)", " ", piece)) for piece in venue.split(",")) if part]


def word_prefix(longer, shorter):
    return f"{longer} ".startswith(f"{shorter} ")


def stems(text):
    return {word[:5] for word in words(text).split() if len(word) >= 4}


def similar_titles(a, b):
    left, right = stems(a), stems(b)
    return bool(left and right) and len(left & right) / max(len(left), len(right)) >= 0.6


PLACE_WORDS = {"ljubljana", "ulica", "cesta", "trg", "pri", "in", "na", "v"}


def venue_tokens(venue):
    """Distinctive venue words, plus the acronym of every run of words, so LGL matches its full name."""
    raw = [word for word in words(re.sub(r"\([^)]*\)", " ", venue)).split() if not word.isdigit()]
    tokens = {word for word in raw if word not in PLACE_WORDS and len(word) >= 3}
    acronyms = {"".join(word[0] for word in raw[start:end])
                for start in range(len(raw)) for end in range(start + 2, min(start + 5, len(raw)) + 1)}
    return tokens, acronyms


def close_venues(a, b):
    (left, left_short), (right, right_short) = venue_tokens(a), venue_tokens(b)
    if not left or not right:
        return False
    shared = len(left & right) + len(left & right_short) + len(right & left_short)
    return shared / min(len(left), len(right)) > 0.5


def same_slot(a, b):
    start_a, start_b = state.timestamp(a["start_time"]), state.timestamp(b["start_time"])
    if start_a == start_b:
        return True
    unknown = "time_unknown" in a.get("flags", []) or "time_unknown" in b.get("flags", [])
    return unknown and start_a.date() == start_b.date()


def duplicate_of(item, events):
    """Find a stored record that is the same occurrence under a reworded title or venue."""
    parts = venue_parts(item["venue"])
    title = words(item["title"])
    for key, other in events.items():
        other_parts, other_title = venue_parts(other["venue"]), words(other["title"])
        if not parts or not other_parts or not same_slot(item, other):
            continue
        # Halls of one venue share a listing URL, so a URL match needs the whole venue to agree.
        same_listing = item["url"] == other["url"] and similar_titles(title, other_title) and (
            parts[:len(other_parts)] == other_parts or other_parts[:len(parts)] == parts)
        contained = f" {title} " in f" {other_title} " or f" {other_title} " in f" {title} "
        close_venue = (word_prefix(parts[0], other_parts[0]) or word_prefix(other_parts[0], parts[0])
                       or parts[0] in other_parts or other_parts[0] in parts
                       or close_venues(item["venue"], other["venue"]))
        if same_listing or (contained and close_venue):
            return key
    return None


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
        correction = existing_key is not None
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
        if state.expired(item, clock) and not correction:
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
            twin_key = duplicate_of(item, events)
            if twin_key is not None:
                twin = events[twin_key]
                if twin.get("status") == "hidden" or state.hidden_reason(updated, twin):
                    results["hidden"].append({**item, "reason": f"duplicate of hidden {twin['event_id']}"})
                else:
                    results["filtered"].append({**item, "reason": f"Likely duplicate of {twin['event_id']}. "
                                                "Pass that event_id to refresh it"})
                continue
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


def reject_future_checks(batch, now):
    for source in batch["sources"]:
        if source.get("checked_at") and state.timestamp(source["checked_at"]) > now:
            raise ValueError(f"Source checked_at is later than now: {source['url']}. "
                             "Record the time the page was actually fetched")


def apply(args):
    import report
    batch = json.loads(Path(args.input).read_text(encoding="utf-8"))
    validate_batch(batch)
    reject_future_checks(batch, datetime.now(state.TZ))
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


COLLECTED = ("candidates", "sources", "filtered", "leads", "runtime_notes")


def combine(results):
    kinds = {result.get("status") for result in results}
    status = kinds.pop() if len(kinds) == 1 else "partial"
    reason = " ".join(result["reason"].strip() for result in results if result.get("reason"))
    if status != "ok" and not reason:
        reason = "A researcher reported this pass incomplete without a reason"
    return {"status": status, **({"reason": reason} if reason else {})}


def claim(name, candidate, owners):
    """Name the research file behind a bad or conflicting candidate. apply only names the event."""
    if not isinstance(candidate, dict):
        return
    unknown = set(candidate) - SOURCE_FIELDS - {"event_id"}
    if unknown:
        raise ValueError(f"{name}: candidate {candidate.get('title', '')!r} has protected or unknown fields "
                         f"{sorted(unknown)}. A cancellation goes in flags")
    try:
        identity = candidate.get("event_id") or fingerprint(candidate)
    except (KeyError, AttributeError, TypeError, ValueError):
        return  # validate_batch reports the missing or malformed field
    earlier, first = owners.setdefault(identity, (name, candidate))
    if first != candidate:
        raise ValueError(f"{earlier} and {name} disagree about {candidate['title']!r} at {candidate['start_time']}. "
                         "Keep one version in one research file")


def collect(args):
    """Rebuild the staged lists from researcher files and fetch records, keeping the run identity."""
    path = Path(args.input)
    batch = json.loads(path.read_text(encoding="utf-8"))
    research = sorted((path.parent / "research").glob("*.json"))
    if not research:
        raise ValueError(f"No research files in {path.parent / 'research'}")
    merged = {field: [] for field in COLLECTED}
    reports = {}
    for fetched in sorted((path.parent / "fetch").glob("*.json")):
        for source in json.loads(fetched.read_text(encoding="utf-8")).get("sources", []):
            if source not in merged["sources"]:
                merged["sources"].append(source)
    now = datetime.now(state.TZ)
    owners = {}
    for item in research:
        part = json.loads(item.read_text(encoding="utf-8"))
        try:
            reject_future_checks({"sources": part.get("sources", [])}, now)
        except ValueError as error:
            raise ValueError(f"{item.name}: {error}. Use fetch.py record instead of typing a time") from error
        for candidate in part.get("candidates", []):
            claim(item.name, candidate, owners)
        for field in COLLECTED:
            for entry in part.get(field, []):
                if entry not in merged[field]:
                    merged[field].append(entry)
        for name, result in part.get("passes", {}).items():
            if name not in PASSES:
                raise ValueError(f"Unknown pass {name!r} in {item.name}")
            reports.setdefault(name, []).append(result)
    passes = {name: combine(reports[name]) if name in reports
              else {"status": "skipped", "reason": "No researcher reported this pass"} for name in PASSES}
    batch.update(merged, passes=passes)
    state.atomic_write(path, state.json_text(batch))
    print(json.dumps({"files": len(research), **{field: len(merged[field]) for field in COLLECTED},
                      "passes": {name: result["status"] for name, result in passes.items()}}, ensure_ascii=False))
    validate_batch(batch)


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
    gather = commands.add_parser("collect", help="rebuild a staged input from research/ and fetch/ files")
    gather.add_argument("input", type=Path)
    gather.set_defaults(func=collect)
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