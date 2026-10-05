# Data Contract

## Database

[db.json](../db.json) remains TinyDB-shaped JSON. Existing string document keys,
event IDs, table contents and unknown fields are preserved. Python validation in
[state.py](../scripts/state.py) is the executable contract, without a second
schema to keep in sync.

| Table | Ownership and lifecycle |
|---|---|
| `events` | Confirmed records. Status is `active`, `expired` or `hidden`. Never delete rows |
| `user_rules` | User exclusions. Only preference commands change them |
| `hidden_events` | Permanent hide audit. Old rows default to active. Restore adds `active: false` and `restored_at` |
| `system_state` | Row `1` stores the sweep clock, active count and optional `latest_run` ID |
| `decision_log` | Append-only undo history for categories. Optional table. Never delete rows |
| Other tables/fields | Preserve without interpretation |

New source observations update only source-owned fields, so user-owned ones
survive a refresh and are retained through expiry and hiding. The previous
version of an updated event is kept in its run record's `before` field.

An earlier `starred: true` flag was removed in favour of `decision`. Run records
under `runs/` still mention it, and those are immutable history that stays as
written. Nothing reads the field any more.

`decision` is user-owned in the same way, with the same guarantees. It is
`interested`, `maybe` or `rejected`, alongside a `decided_at` string, and only
[swipe.py](../scripts/swipe.py) and the app in [app/](../app/README.md) change it.
An absent key means undecided; clearing removes both keys rather than storing a
null. A decision is not a preference rule: it never hides an event, never edits
`user_rules` and never changes an event's status, so a rejected event stays in the
app's Zavrnjeno list until it is hidden explicitly. Every change appends a
`decision_log` row holding `event_id`, `action`, `before`, `before_at`, `after`
and `at`. Undo reverses the newest row that has no `undone` flag, restores the
recorded previous value and timestamp, and marks that row `undone` with
`undone_at` instead of deleting it. Undo therefore survives a restart, and the
log is a history rather than a stack that can be popped away.

Exclusions from all user-rule rows are applied case-insensitively. ID, venue and
category exclusions use equality. Keyword exclusions match substrings of titles.
They apply before candidate persistence and during rendering. Existing
active legacy hide references also match an occurrence by title, time and venue,
so changing the ID scheme cannot bring back a previously hidden event. Existing
`force_include_urls` and `max_travel_minutes` values are retained. They are not
automatic overrides of exclusions or evidence requirements. If the user changes
these currently unused controls, define and test their behavior before relying on them.

Dates must be timezone-aware ISO timestamps. Unknown time is stored at local
midnight with `time_unknown` and displayed as `?`. It expires after that local
calendar day, not at midnight at its start. Otherwise expiry uses the start instant.
The horizon uses calendar months and Ljubljana daylight-saving rules.

## Staged Input

`begin` creates a complete scaffold. Preserve its run ID, checksum and clock.
Each source uses one of the six pass keys defined in [run.py](../scripts/run.py).
Successful passes need at least one successfully fetched source. Non-successful
passes and sources require a reason. The agent is responsible for honest coverage
and actual verification. A schema check cannot prove that a page was fetched.

Example candidate and matching source entry:

```json
{
  "candidates": [
    {
      "title": "Example family workshop",
      "start_time": "2026-10-10T10:00:00+02:00",
      "venue": "Example museum",
      "city": "Ljubljana",
      "category": "delavnica",
      "age_min": null,
      "is_free": null,
      "price_text": "",
      "url": "https://example.org/event",
      "flags": []
    }
  ],
  "sources": [
    {
      "url": "https://example.org/event",
      "pass": "ljubljana",
      "status": "ok",
      "checked_at": "2026-09-28T12:01:00+02:00"
    }
  ]
}
```

This is a shape example, not an event to import. The full scaffold also contains
`schema_version: 1`, `run_id`, `started_at`, `base_sha256`, `passes`, `filtered`,
`leads` and `runtime_notes`. Source outcomes are `ok`, `failed` or `skipped`.
Pass outcomes also allow `partial`. Lead/filter rows require `title`, `url` and
`reason`. Runtime notes are strings.

Candidates accept only `event_id` plus source fields shown above. Required
identity/source fields must be nonempty. `age_min` is a nonnegative integer or
null. `is_free` is true, false or null. A candidate URL must exactly match a
successful source URL. Record the final confirming URL when redirects occur.

New IDs are deterministic hashes of normalized title, local start instant and
venue, with a readable date prefix. Existing IDs win over newly proposed IDs
when title/time/venue match. To correct time, venue or title on an existing event,
pass its existing ID. Conflicting ID/identity matches abort rather than guessing.
Identical candidates from multiple passes collapse. Conflicting duplicates abort.
Do not use a known ID for a different occurrence of a recurring show.

The merger retains source fields not included in a refresh and all unknown
database metadata. Do not pass fabricated nulls to erase a known value. The
current model has no separate end date. Keep published date ranges in price text
as before. A future end-date migration needs its own reviewed contract.

## Decision Patches

Decisions taken where the database cannot be written, currently the published
static build of the app, arrive as a patch file in `inbox/`, or as the `patch`
input of a workflow run that a device token started. One `code:event_id`
per line, with `i`, `m`, `r` and `c` for interested, maybe, rejected and
cleared. Blank lines and `#` comments are ignored. A malformed line aborts the
whole patch rather than applying part of it.

Each line names the wanted end state, so a patch is idempotent and its lines
are order independent. Applying one is exactly a sequence of the operations
above: the same validation, the same `decision_log` rows, the same undo. An
event ID the database does not hold is reported and skipped. It is never
created, and a missing event is never reconstructed from a patch, which carries
no event details to reconstruct it from. The staging copy in a browser is not a
record and is never read back as state: a patch is applied only after someone
with write access commits it or a device token starts the workflow. The dispatch
input is untrusted text. It keeps only lines in this exact format, so a malformed
line aborts the run.

## Run Records and Recovery

Successful apply writes `runs/<run_id>.json` with the original input, computed
result groups and the resulting database hash. The database references the latest
run by ID. New, updated, expired, hidden, filtered, deferred and unchanged counts
come from these lists, not narrative estimates.

The record is written before the database, followed by derived reports. A crash
may leave these files out of sync. Retrying the identical apply repairs that
state when the database is still the base or exactly the recorded result.
Otherwise it refuses to overwrite intervening changes. Preference commands may
legitimately change the database after a sweep, so the recorded result hash is
not a permanent whole-database integrity checksum.

Individual writes use same-directory temporary files, flush, fsync and atomic
replacement. Advisory nonblocking locks protect mutating commands in one Linux
or macOS checkout. Cloud jobs in different checkouts need scheduler serialization
and normal Git fast-forward checks. No multi-file transaction or distributed lock
is claimed.