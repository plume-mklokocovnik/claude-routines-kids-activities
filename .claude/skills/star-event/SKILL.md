---
name: star-event
description: Mark, or un-mark, an event in the kids-activities list as interested/starred, shown with a ⭐ next to its title in currently_active.md. Use when the user says star, unstar, mark as interested, bookmark, favorite, flag, or "we want to go to this one" about an event in this repo, or names an event ID from currently_active.md to that effect. Also handles listing what is currently starred.
---

# Star an event

Starring keeps the event in its chronological position and adds it to the ⭐
shortlist at the top of `currently_active.md`.

## What a star actually writes

The matching event gets `"starred": true`. Source refreshes cannot overwrite it.
Expiry and hiding keep the complete event and its star. The shortlist contains
only active, non-excluded events. No separate preference database is needed.

## Run it

Always use the script. Never hand-edit `db.json`, and never re-render `currently_active.md`
by hand. The script keeps `db.json` and the rendered list consistent.

```bash
python3 scripts/star_event.py star <query>
```

`<query>` is an `event_id` printed below a title in `currently_active.md`, or a
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

## Verify and publish

Run `python3 scripts/run.py check`. Do not modify the historical sweep report for
a preference change. Commit or push only when explicitly authorized. Follow
[AGENTS.md](../../../AGENTS.md) for publication. An appropriate commit subject is
`chore: Star event <id>`, with no Jira ticket or attribution.
