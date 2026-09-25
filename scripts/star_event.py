#!/usr/bin/env python3
"""Star (and unstar) an event so it stands out in the active list.

Starring is not hiding: the row stays in `currently_active.md`, it just gets a
⭐ marker in front of its title so it is easy to spot among everything else.
There is no separate audit table for it — the flag lives on the event itself
in `db.json`, so it naturally disappears when the event expires and is pruned.

    python3 scripts/star_event.py star <query>
    python3 scripts/star_event.py unstar <query>
    python3 scripts/star_event.py list

<query> is an `event_id` or a case-insensitive fragment of the title/venue. An
ambiguous fragment lists the candidates and changes nothing.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(REPO, "db.json")


def active_list_path(db_path):
    """Keep the rendered list next to the database it came from."""
    return os.path.join(os.path.dirname(os.path.abspath(db_path)), "currently_active.md")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def save(path, db):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(db, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


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


def cmd_star(args):
    db = load(args.db)
    matches = find(db, args.query)

    if not matches:
        print(f"No active event matches {args.query!r}. Nothing changed.", file=sys.stderr)
        return 1
    if len(matches) > 1:
        print(f"{args.query!r} matches {len(matches)} events. Re-run with a full event_id:",
              file=sys.stderr)
        for _, event in sorted(matches, key=lambda m: m[1].get("start_time") or ""):
            print(f"  {describe(event)}", file=sys.stderr)
        return 2

    _, event = matches[0]
    event["starred"] = True

    save(args.db, db)
    render.main_write(args.db, active_list_path(args.db))

    print(f"Starred: {describe(event)}")
    return 0


def cmd_unstar(args):
    db = load(args.db)
    matches = find(db, args.query)

    if not matches:
        print(f"No active event matches {args.query!r}. Nothing changed.", file=sys.stderr)
        return 1
    if len(matches) > 1:
        print(f"{args.query!r} matches {len(matches)} events. Re-run with a full event_id:",
              file=sys.stderr)
        for _, event in sorted(matches, key=lambda m: m[1].get("start_time") or ""):
            print(f"  {describe(event)}", file=sys.stderr)
        return 2

    _, event = matches[0]
    event.pop("starred", None)

    save(args.db, db)
    render.main_write(args.db, active_list_path(args.db))

    print(f"Unstarred: {describe(event)}")
    return 0


def cmd_list(args):
    db = load(args.db)
    starred = [e for e in db.get("events", {}).values() if e.get("starred")]
    if not starred:
        print("Nothing is starred.")
        return 0
    print(f"{len(starred)} starred event(s):")
    for event in sorted(starred, key=lambda e: e.get("start_time") or ""):
        print(f"  {describe(event)}")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--db", default=DB_PATH)
    sub = parser.add_subparsers(dest="command", required=True)

    star = sub.add_parser("star", help="mark an event as interested (⭐)")
    star.add_argument("query")
    star.set_defaults(func=cmd_star)

    unstar = sub.add_parser("unstar", help="drop the ⭐ marker from an event")
    unstar.add_argument("query")
    unstar.set_defaults(func=cmd_unstar)

    listing = sub.add_parser("list", help="show everything currently starred")
    listing.set_defaults(func=cmd_list)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
