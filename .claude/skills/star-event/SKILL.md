---
name: star-event
description: Mark, or un-mark, an event in the kids-activities list as interested/starred, shown with a ⭐ next to its title in currently_active.md. Use when the user says star, unstar, mark as interested, bookmark, favorite, flag, or "we want to go to this one" about an event in this repo, or names an event ID from currently_active.md to that effect. Also handles listing what is currently starred.
---

# Star an event

Starring is not hiding. The row stays exactly where it is in `currently_active.md`, it just
gets a ⭐ in front of its title so it stands out among everything else on the list.

## What a star actually writes

One change, in `db.json`: the matching event in `events` gets `"starred": true`. There is no
separate audit table like `hidden_events` has, on purpose, because a star only ever needs to
outlive the event itself. When `routine.md` §5 prunes an expired event, its star goes with it.

## Run it

Always use the script. Never hand-edit `db.json`, and never re-render `currently_active.md`
by hand. The script keeps `db.json` and the rendered list consistent.

```bash
python3 scripts/star_event.py star <query>
```

`<query>` is an `event_id` from the **ID** column of `currently_active.md`, or a
case-insensitive fragment of the title or venue.

## Working rules

1. **An ambiguous fragment is not a guess.** The script exits with the candidate list when a
   fragment matches more than one event. Show the user that list and ask which one, or use the
   full `event_id` instead. Never pick one yourself.
2. **A URL is not a query.** If the user gives a link instead of an ID, find the matching event
   in `db.json` by its `url` field first, then star it by `event_id`.
3. **Several events at once** means one call per star. Run them in sequence and report the total.
4. **Report what changed**: ID, title, and date for each event starred.

## Unstar and inspect

```bash
python3 scripts/star_event.py unstar <query>   # drop the ⭐
python3 scripts/star_event.py list             # everything currently starred
```

## Commit

Changes to `db.json` and `currently_active.md` are committed like any other change in this repo:
Conventional Commits, no Jira ticket, no attribution.

```bash
git add db.json currently_active.md && git commit -m "chore: Star event <id>"
```
