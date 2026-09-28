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
| `events` | The complete row stays, with `status: hidden`, so it leaves the calendar |
| `user_rules` | The matching rule stops the next sweep from re-saving it |
| `hidden_events` | The permanent reference: what was hidden, which scope, when and why |

The [run workflow](../../../routine.md) applies exclusions before saving candidates.
The original event, its star and the audit reference are retained. Rules hold
until the user restores them. Legacy hidden occurrences also match by title,
time and venue when a new ID would otherwise bypass the rule.

## Run it

Always use the script. Never hand-edit `db.json`, and never re-render `currently_active.md`
by hand. The script keeps the three tables and the rendered list consistent.

```bash
python3 scripts/hide_event.py hide <query> [--scope event|series|venue] [--reason "..."]
```

`<query>` is an `event_id` printed below a title in `currently_active.md`, or a
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
5. **Report what changed**: ID, title, scope and count of events hidden. No rows are deleted.

## Unhide and inspect

```bash
python3 scripts/hide_event.py unhide <query>   # drop the rule, let it come back
python3 scripts/hide_event.py list             # everything currently hidden
```

An unhide removes the rule, marks its audit reference inactive and restores retained
records as of the last sweep clock, unless another rule still excludes them. It keeps
the audit history. References created by older versions may have no event row to
restore. Those details need re-discovery, not reconstruction from guesses.

## Verify and publish

Run `python3 scripts/run.py check`. Do not modify the historical sweep report for
a preference change. Commit or push only when explicitly authorized. Follow
[AGENTS.md](../../../AGENTS.md) for publication. An appropriate commit subject is
`chore: Hide event <id>`, with no Jira ticket or attribution.
