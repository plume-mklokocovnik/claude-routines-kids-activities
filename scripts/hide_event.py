#!/usr/bin/env python3
"""Hide an event from the active list and keep a permanent reference to it.

Hiding does three things at once, so a hidden event never comes back on its own:
drops the row from `events`, writes the matching rule into `user_rules`, and
records why in `hidden_events`. The routine reads `user_rules` on every sweep,
so the event is not re-discovered, not re-saved and not re-listed.

    python3 scripts/hide_event.py hide <query> [--scope event|series|venue] [--reason "..."]
    python3 scripts/hide_event.py unhide <query>
    python3 scripts/hide_event.py list

<query> is an `event_id` or a case-insensitive fragment of the title. An
ambiguous fragment lists the candidates and changes nothing.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(REPO, "db.json")

RULE_FIELD = {
    "event": "exclude_event_ids",
    "series": "exclude_keywords",
    "venue": "exclude_venues",
}


def active_list_path(db_path):
    """Keep the rendered list next to the database it came from."""
    return os.path.join(os.path.dirname(os.path.abspath(db_path)), "currently_active.md")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def save(path, db):
    db.setdefault("system_state", {}).setdefault("1", {})["total_active_events"] = len(db.get("events", {}))
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(db, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def next_key(table):
    keys = [int(k) for k in table if str(k).isdigit()]
    return str(max(keys) + 1 if keys else 1)


def rules(db):
    return db.setdefault("user_rules", {}).setdefault("1", {})


def find(db, query):
    """Match a query against event_id, title or venue of the active events."""
    events = db.get("events", {})
    lowered = query.lower()
    exact = [(k, e) for k, e in events.items() if (e.get("event_id") or "").lower() == lowered]
    if exact:
        return exact
    return [(k, e) for k, e in events.items()
            if lowered in (e.get("title") or "").lower()
            or lowered in (e.get("event_id") or "").lower()
            or lowered in (e.get("venue") or "").lower()]


def describe(event):
    return (f"{event.get('event_id')}  {event.get('start_time', '?')[:16]}  "
            f"{event.get('title')} @ {event.get('venue')}")


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
    rule_list = rules(db).setdefault(field, [])
    if match_value not in rule_list:
        rule_list.append(match_value)

    for key, _ in removed:
        db["events"].pop(key, None)

    hidden = db.setdefault("hidden_events", {})
    already = [h for h in hidden.values() if h.get("match") == match_value and h.get("scope") == args.scope]
    if not already:
        hidden[next_key(hidden)] = {
            "match": match_value,
            "scope": args.scope,
            "rule_field": field,
            "event_id": seed.get("event_id"),
            "title": seed.get("title"),
            "venue": seed.get("venue"),
            "start_time": seed.get("start_time"),
            "url": seed.get("url"),
            "reason": args.reason or "hidden on request",
            "hidden_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    save(args.db, db)
    render.main_write(args.db, active_list_path(args.db))

    print(f"Hidden ({args.scope}): {match_value}")
    print(f"Removed {len(removed)} event(s) from db.json, added to user_rules.{field}.")
    for _, event in sorted(removed, key=lambda m: m[1].get("start_time") or ""):
        print(f"  - {describe(event)}")
    return 0


def cmd_unhide(args):
    db = load(args.db)
    hidden = db.get("hidden_events", {})
    lowered = args.query.lower()
    matches = [(k, h) for k, h in hidden.items()
               if lowered in str(h.get("match", "")).lower()
               or lowered == str(h.get("event_id", "")).lower()]

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
    hidden.pop(key, None)

    save(args.db, db)
    render.main_write(args.db, active_list_path(args.db))

    print(f"Restored ({item.get('scope')}): {item.get('match')}")
    print("The event is not back in db.json yet. The next sweep will re-discover it if it is still listed.")
    return 0


def cmd_list(args):
    db = load(args.db)
    hidden = db.get("hidden_events", {})
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

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
