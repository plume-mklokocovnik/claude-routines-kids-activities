---
name: hide-event
description: Hide, remove or delete an event from the kids-activities list and keep a permanent reference so the routine never shows or re-processes it again. Use when the user says hide, remove, delete, skip, drop, "don't show", "not interested in" about an event, a show, a series or a venue in this repo, or names an event ID from currently_active.md. Also handles unhide, restore, "bring it back" and "what have I hidden".
---

# Hide an event

Hiding is not deleting. The row leaves `currently_active.md`, and the reference stays in
`db.json` so the next sweep skips it instead of re-discovering it.

## What a hide actually writes

Three changes, all in `db.json`, all in one command:

| Where | What it does |
|---|---|
| `events` | The matching row is dropped, so the event leaves `currently_active.md` |
| `user_rules` | The matching rule stops the next sweep from re-saving it |
| `hidden_events` | The permanent reference: what was hidden, which scope, when and why |

`routine.md` §3 applies `user_rules` before anything is written, so a hidden event is never
re-discovered, never re-saved and never re-listed. Nothing expires on its own.

## Run it

Always use the script. Never hand-edit `db.json`, and never re-render `currently_active.md`
by hand. The script keeps the three tables and the rendered list consistent.

```bash
python3 scripts/hide_event.py hide <query> [--scope event|series|venue] [--reason "..."]
```

`<query>` is an `event_id` from the **ID** column of `currently_active.md`, or a
case-insensitive fragment of the title.

## Pick the scope

Default to `event`. Widen only when the user's wording is clearly about the show or the place
rather than the one date.

| Scope | Hides | Rule written | Use when the user says |
|---|---|---|---|
| `event` *(default)* | That one dated event | `exclude_event_ids` | "hide `kinodvor_20261010_1000`", "not that Saturday one" |
| `series` | Every date of that title, now and later | `exclude_keywords` | "hide all Bacek Jon screenings", "we never want this show" |
| `venue` | Everything at that venue | `exclude_venues` | "nothing from SiTi Teater", "that place is too far" |

## Working rules

1. **An ambiguous fragment is not a guess.** The script exits with the candidate list when a
   fragment matches more than one event. Show the user that list and ask which one, or offer
   `--scope series` when they clearly meant all of them. Never pick one yourself.
2. **Record the reason** when the user gave one. `--reason "too late for bedtime"` is what makes
   the hidden list readable three months from now. Leave it off rather than inventing one.
3. **Several events at once** means one call per hide. Run them in sequence and report the total.
4. **Confirm before a `venue` hide** unless the user named the venue themselves. It can drop a
   dozen events in one go.
5. **Report what changed** in a table: ID, title, scope, count of rows removed.

## Unhide and inspect

```bash
python3 scripts/hide_event.py unhide <query>   # drop the rule, let it come back
python3 scripts/hide_event.py list             # everything currently hidden
```

An unhide removes the rule but does not restore the row, because the original listing may be
gone. Tell the user the next sweep will pick it up again if the event is still published.

## Commit

Changes to `db.json` and `currently_active.md` are committed like any other change in this repo:
Conventional Commits, no Jira ticket, no attribution.

```bash
git add db.json currently_active.md && git commit -m "chore: Hide event <id>"
```
