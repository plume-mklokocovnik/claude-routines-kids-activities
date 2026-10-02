#!/usr/bin/env python3
"""Hide an event from the swipe deck and keep a permanent reference to it.

Hiding does three things at once, so a hidden event never comes back on its own:
marks the retained row hidden, writes the matching rule into `user_rules`, and
records why in `hidden_events`. The routine reads `user_rules` on every sweep,
so the event is not re-discovered, not re-saved and not re-listed.

    python3 scripts/hide_event.py hide <query> [--scope event|series|venue] [--reason "..."]
    python3 scripts/hide_event.py unhide <query>
    python3 scripts/hide_event.py list
    python3 scripts/hide_event.py apply <patch-file> [--reason "..."]

<query> is an `event_id` or a case-insensitive fragment of the title. An
ambiguous fragment lists the candidates and changes nothing.

`apply` hides a batch chosen in the app, such as every Zavrnjeno event. The patch
is one exact `event_id` per line, and `#` comments and blank lines are ignored.
Each ID is hidden with the `event` scope only, so no series or venue rule is
written. The default reason is "hidden from the app". An ID already hidden is
left alone, and an ID that is not in the database is reported and skipped.
"""

import argparse
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import state
from state import find, load, next_key, save

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(REPO, "db.json")

APP_REASON = "hidden from the app"

RULE_FIELD = {
    "event": "exclude_event_ids",
    "series": "exclude_keywords",
    "venue": "exclude_venues",
}


def rules(db):
    return db.setdefault("user_rules", {}).setdefault("1", {})


def describe(event):
    return (f"{event.get('event_id')}  {event.get('start_time', '?')[:16]}  "
            f"{event.get('title')} @ {event.get('venue')}")


def record_hide(db, seed, removed, scope, match_value, reason):
    """Write the three-table hide: the rule, the hidden status and the reference."""
    field = RULE_FIELD[scope]
    rule_list = rules(db).setdefault(field, [])
    if match_value not in rule_list:
        rule_list.append(match_value)

    for _, event in removed:
        if event.get("status", "active") == "active":
            event["status"] = "hidden"

    hidden = db.setdefault("hidden_events", {})
    already = [h for h in hidden.values() if h.get("match") == match_value
               and h.get("scope") == scope and h.get("active", True)]
    if not already:
        hidden[next_key(hidden)] = {
            "match": match_value,
            "scope": scope,
            "rule_field": field,
            "event_id": seed.get("event_id"),
            "title": seed.get("title"),
            "venue": seed.get("venue"),
            "start_time": seed.get("start_time"),
            "url": seed.get("url"),
            "reason": reason,
            "hidden_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }


def parse_ids(text):
    """Read a patch of event IDs, one per line. Blank lines and `#` comments are
    ignored. A line holding anything but one ID is refused, never guessed at."""
    ids = []
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if any(char.isspace() for char in line) or ":" in line:
            raise ValueError(f"Line {number}: expected one event_id, got {raw!r}")
        if line not in ids:
            ids.append(line)
    return ids


def hide_ids(db, ids, reason):
    """Hide each event by its exact ID and the event scope only, never a series or
    a venue. Returns (hidden, already_hidden, unknown) lists of IDs."""
    hidden, already, unknown = [], [], []
    for event_id in ids:
        event = next((item for item in db.get("events", {}).values()
                      if item.get("event_id") == event_id), None)
        if event is None:
            unknown.append(event_id)
        elif event.get("status") == "hidden" or state.hidden_reason(db, event):
            already.append(event_id)
        else:
            record_hide(db, event, [(None, event)], "event", event_id, reason)
            hidden.append(event_id)
    return hidden, already, unknown


def cmd_apply(args):
    with open(args.patch, encoding="utf-8") as handle:
        ids = parse_ids(handle.read())
    if not ids:
        print(f"{args.patch} lists no events. Nothing changed.")
        return 0

    db = load(args.db)
    hidden, already, unknown = hide_ids(db, ids, args.reason)
    if hidden:
        save(args.db, db)

    print(f"Hidden {len(hidden)} event(s) from {args.patch}, "
          f"{len(already)} were already hidden.")
    for event_id in hidden:
        print(f"  - {event_id}")
    if unknown:
        print(f"Skipped {len(unknown)} unknown event ID(s). These need a sweep, "
              f"not a guess:", file=sys.stderr)
        for event_id in unknown:
            print(f"  {event_id}", file=sys.stderr)
    return 0


def cmd_hide(args):
    db = load(args.db)
    matches = find(db, args.query)

    if not matches:
        print(f"No active event matches {args.query!r}. Nothing changed.", file=sys.stderr)
        print("Run `python3 scripts/hide_event.py list` to see what is already hidden.", file=sys.stderr)
        return 1

    if len(matches) > 1 and args.scope == "event":
        print(f"{args.query!r} matches {len(matches)} events. Re-run with a full event_id, "
              f"or with --scope series to hide all of them:", file=sys.stderr)
        for _, event in sorted(matches, key=lambda m: m[1].get("start_time") or ""):
            print(f"  {describe(event)}", file=sys.stderr)
        return 2

    seed = sorted(matches, key=lambda m: m[1].get("start_time") or "")[0][1]
    scope_field = {"series": "title", "venue": "venue"}.get(args.scope)
    if scope_field and len({item[scope_field].casefold() for _, item in matches}) > 1:
        print(f"Ambiguous {args.scope}. Use one exact event_id to select the scope:", file=sys.stderr)
        for _, item in matches:
            print(f"  {describe(item)}", file=sys.stderr)
        return 2

    if args.scope == "event":
        match_value = seed.get("event_id")
        removed = [m for m in matches if m[1].get("event_id") == match_value]
    elif args.scope == "series":
        match_value = seed.get("title")
        removed = [(k, e) for k, e in db["events"].items()
                   if match_value.lower() in (e.get("title") or "").lower()]
    else:
        match_value = seed.get("venue")
        removed = [(k, e) for k, e in db["events"].items()
                   if (e.get("venue") or "") == match_value]

    field = RULE_FIELD[args.scope]
    record_hide(db, seed, removed, args.scope, match_value, args.reason or "hidden on request")

    save(args.db, db)

    print(f"Hidden ({args.scope}): {match_value}")
    print(f"Hidden {len(removed)} event(s), retained all records, added to user_rules.{field}.")
    for _, event in sorted(removed, key=lambda m: m[1].get("start_time") or ""):
        print(f"  - {describe(event)}")
    return 0


def cmd_unhide(args):
    db = load(args.db)
    hidden = db.get("hidden_events", {})
    lowered = args.query.lower()
    active = [(key, item) for key, item in hidden.items() if item.get("active", True)]
    exact = [(key, item) for key, item in active
             if lowered == str(item.get("match", "")).lower()
             or lowered == str(item.get("event_id", "")).lower()]
    matches = exact or [(key, item) for key, item in active
                        if lowered and lowered in str(item.get("match", "")).lower()]

    if not matches:
        print(f"Nothing hidden matches {args.query!r}.", file=sys.stderr)
        return 1
    if len(matches) > 1:
        print(f"{args.query!r} matches {len(matches)} hidden entries. Be more specific:", file=sys.stderr)
        for _, item in matches:
            print(f"  {item.get('scope')}: {item.get('match')}", file=sys.stderr)
        return 2

    key, item = matches[0]
    field = item.get("rule_field") or RULE_FIELD.get(item.get("scope", "event"), "exclude_event_ids")
    rule_list = rules(db).setdefault(field, [])
    if item.get("match") in rule_list:
        rule_list.remove(item["match"])
    item["active"] = False
    item["restored_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    restored = 0
    clock = state.timestamp(db["system_state"]["1"]["last_run"])
    for event in db["events"].values():
        if event.get("status") == "hidden" and not state.hidden_reason(db, event):
            event["status"] = "expired" if state.expired(event, clock) else "active"
            restored += 1

    save(args.db, db)

    print(f"Restored ({item.get('scope')}): {item.get('match')}")
    print(f"Restored {restored} retained record(s). Legacy deleted rows need re-discovery in a later sweep.")
    return 0


def cmd_list(args):
    db = load(args.db)
    hidden = {key: item for key, item in db.get("hidden_events", {}).items() if item.get("active", True)}
    if not hidden:
        print("Nothing is hidden.")
        return 0
    print(f"{len(hidden)} hidden entr{'y' if len(hidden) == 1 else 'ies'}:")
    for item in sorted(hidden.values(), key=lambda h: h.get("hidden_at") or ""):
        print(f"  [{item.get('scope')}] {item.get('match')}")
        print(f"      {item.get('title')} | hidden {str(item.get('hidden_at'))[:10]} | {item.get('reason')}")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--db", default=DB_PATH)
    sub = parser.add_subparsers(dest="command", required=True)

    hide = sub.add_parser("hide", help="hide an event, a whole series, or a venue")
    hide.add_argument("query")
    hide.add_argument("--scope", choices=sorted(RULE_FIELD), default="event")
    hide.add_argument("--reason", default="")
    hide.set_defaults(func=cmd_hide)

    unhide = sub.add_parser("unhide", help="drop a hide rule and let the event come back")
    unhide.add_argument("query")
    unhide.set_defaults(func=cmd_unhide)

    listing = sub.add_parser("list", help="show everything currently hidden")
    listing.set_defaults(func=cmd_list)

    applier = sub.add_parser("apply", help="hide every event ID listed in a patch file")
    applier.add_argument("patch")
    applier.add_argument("--reason", default=APP_REASON)
    applier.set_defaults(func=cmd_apply)

    args = parser.parse_args()
    try:
        with state.locked(args.db):
            result = args.func(args)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")
    sys.exit(result)


if __name__ == "__main__":
    main()
