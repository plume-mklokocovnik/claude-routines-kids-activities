#!/usr/bin/env python3
"""Record which of three categories an event falls into, and undo the last change.

A decision is user-owned, exactly like a star. It lives on the event row in
`db.json` as `decision` (`interested`, `maybe` or `rejected`) plus `decided_at`.
Every change is appended to the `decision_log` table, so the most recent one can
be undone at any time, including after a restart. Nothing is ever deleted: an
undone log row keeps its audit trail and is marked `undone`.

Decisions are independent of stars and hide rules. Rejecting an event does not
hide it, does not touch `user_rules` and does not remove it from
`currently_active.md`. Source refreshes never set or clear a decision.

    python3 scripts/swipe.py set <query> interested|maybe|rejected
    python3 scripts/swipe.py clear <query>
    python3 scripts/swipe.py undo
    python3 scripts/swipe.py list [--category interested|maybe|rejected]
    python3 scripts/swipe.py stats

<query> is an `event_id` or a case-insensitive fragment of the title/venue. An
ambiguous fragment lists the candidates and changes nothing. The swipe app in
[app/](../app/README.md) is a browser front end over exactly these operations.
"""

import argparse
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import state  # noqa: E402
from state import find, load, next_key, save  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(REPO, "db.json")

LABELS = {"interested": "Zanima nas", "maybe": "Mogoče", "rejected": "Zavrnjeno"}
FAR_FUTURE = datetime.max.replace(tzinfo=timezone.utc)


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def describe(event):
    return (f"{event.get('event_id')}  {str(event.get('start_time', '?'))[:16]}  "
            f"{event.get('title')} @ {event.get('venue')}")


def sort_key(event):
    """Chronological, like the calendar. Parsed, so offsets around DST still order."""
    try:
        start = state.timestamp(event.get("start_time"))
    except ValueError:
        start = None
    return (start is None, start or FAR_FUTURE,
            event.get("title") or "", event.get("event_id") or "")


def by_id(db, event_id):
    for event in db.get("events", {}).values():
        if event.get("event_id") == event_id:
            return event
    return None


def deck(db):
    """Events still waiting for a decision: active, not hidden, chronological."""
    return sorted((event for event in state.active_events(db) if not event.get("decision")),
                  key=sort_key)


def decided(db):
    """Every decided event grouped by category, whatever its status became later."""
    groups = {name: [] for name in state.DECISIONS}
    for event in db.get("events", {}).values():
        if event.get("decision") in groups:
            groups[event["decision"]].append(event)
    return {name: sorted(rows, key=sort_key) for name, rows in groups.items()}


def counts(db):
    groups = decided(db)
    result = {name: len(groups[name]) for name in state.DECISIONS}
    result["undecided"] = len(deck(db))
    result["decided"] = sum(result[name] for name in state.DECISIONS)
    result["total"] = result["decided"] + result["undecided"]
    return result


def log_table(db):
    return db.setdefault("decision_log", {})


def record(db, event, action, before, before_at, after, at):
    table = log_table(db)
    table[next_key(table)] = {
        "event_id": event.get("event_id"),
        "action": action,
        "before": before,
        "before_at": before_at,
        "after": after,
        "at": at,
    }


def set_decision(db, event, value, at=None):
    """Return (changed, previous). Re-applying the same category writes nothing."""
    if value not in state.DECISIONS:
        raise ValueError(f"Unknown category {value!r}. Use one of: {', '.join(state.DECISIONS)}")
    before = event.get("decision")
    if before == value:
        return False, before
    before_at = event.get("decided_at")
    event["decision"] = value
    event["decided_at"] = at or now()
    record(db, event, "set", before, before_at, value, event["decided_at"])
    return True, before


def clear_decision(db, event, at=None):
    """Send an event back to the deck. Returns (changed, previous)."""
    before = event.get("decision")
    if not before:
        return False, None
    before_at = event.get("decided_at")
    event.pop("decision", None)
    event.pop("decided_at", None)
    record(db, event, "clear", before, before_at, None, at or now())
    return True, before


def last_change(db):
    """Newest log row that has not been undone yet, or (None, None)."""
    table = db.get("decision_log", {})
    keys = [key for key, row in table.items() if str(key).isdigit() and not row.get("undone")]
    if not keys:
        return None, None
    key = max(keys, key=int)
    return key, table[key]


def undo(db, at=None):
    """Reverse the last recorded change. Returns (row, event) or (None, None)."""
    _, row = last_change(db)
    if row is None:
        return None, None
    event = by_id(db, row.get("event_id"))
    if event is None:
        raise ValueError(f"Cannot undo: no event row for {row.get('event_id')!r}")
    before = row.get("before")
    if before is None:
        event.pop("decision", None)
        event.pop("decided_at", None)
    else:
        event["decision"] = before
        if row.get("before_at"):
            event["decided_at"] = row["before_at"]
        else:
            event.pop("decided_at", None)
    row["undone"] = True
    row["undone_at"] = at or now()
    return row, event


def resolve(db, query):
    """Find exactly one event for a query, or report why not. Returns (event, code)."""
    matches = find(db, query)
    if not matches:
        print(f"No active event matches {query!r}. Nothing changed.", file=sys.stderr)
        return None, 1
    if len(matches) > 1:
        print(f"{query!r} matches {len(matches)} events. Re-run with a full event_id:",
              file=sys.stderr)
        for _, event in sorted(matches, key=lambda match: sort_key(match[1])):
            print(f"  {describe(event)}", file=sys.stderr)
        return None, 2
    return matches[0][1], 0


def cmd_set(args):
    db = load(args.db)
    event, code = resolve(db, args.query)
    if event is None:
        return code
    changed, before = set_decision(db, event, args.category)
    if not changed:
        print(f"Already {LABELS[args.category]}: {describe(event)}")
        return 0
    save(args.db, db)
    moved = f" (was {LABELS[before]})" if before else ""
    print(f"{LABELS[args.category]}{moved}: {describe(event)}")
    return 0


def cmd_clear(args):
    db = load(args.db)
    event, code = resolve(db, args.query)
    if event is None:
        return code
    changed, before = clear_decision(db, event)
    if not changed:
        print(f"No decision to clear: {describe(event)}")
        return 0
    save(args.db, db)
    print(f"Back in the deck (was {LABELS[before]}): {describe(event)}")
    return 0


def cmd_undo(args):
    db = load(args.db)
    row, event = undo(db)
    if row is None:
        print("Nothing to undo.")
        return 0
    save(args.db, db)
    restored = LABELS.get(row.get("before")) or "no decision"
    print(f"Undone {row.get('action')} → {restored}: {describe(event)}")
    return 0


def cmd_list(args):
    db = load(args.db)
    groups = decided(db)
    names = [args.category] if args.category else list(state.DECISIONS)
    for name in names:
        rows = groups[name]
        print(f"{LABELS[name]} ({len(rows)}):" if rows else f"{LABELS[name]} (0)")
        for event in rows:
            star = "⭐ " if event.get("starred") else ""
            print(f"  {star}{describe(event)}")
    return 0


def cmd_stats(args):
    db = load(args.db)
    numbers = counts(db)
    print(f"{numbers['decided']} decided of {numbers['total']}, "
          f"{numbers['undecided']} still in the deck.")
    for name in state.DECISIONS:
        print(f"  {LABELS[name]:<12} {numbers[name]}")
    _, row = last_change(db)
    if row:
        print(f"Undo would reverse: {row.get('action')} {row.get('event_id')} "
              f"→ {row.get('after') or 'cleared'} ({row.get('at')})")
    else:
        print("Nothing to undo.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--db", default=DB_PATH)
    sub = parser.add_subparsers(dest="command", required=True)

    setter = sub.add_parser("set", help="put an event in one of the three categories")
    setter.add_argument("query")
    setter.add_argument("category", choices=list(state.DECISIONS))
    setter.set_defaults(func=cmd_set)

    clearer = sub.add_parser("clear", help="drop the decision and return the event to the deck")
    clearer.add_argument("query")
    clearer.set_defaults(func=cmd_clear)

    undoer = sub.add_parser("undo", help="reverse the most recent decision change")
    undoer.set_defaults(func=cmd_undo)

    listing = sub.add_parser("list", help="show decided events by category")
    listing.add_argument("--category", choices=list(state.DECISIONS))
    listing.set_defaults(func=cmd_list)

    stats = sub.add_parser("stats", help="show progress and what undo would reverse")
    stats.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    try:
        with state.locked(args.db):
            result = args.func(args)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")
    sys.exit(result)


if __name__ == "__main__":
    main()
