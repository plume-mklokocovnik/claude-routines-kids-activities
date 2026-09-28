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
| Other tables/fields | Preserve without interpretation |

`starred: true` is user-owned on the event. Refreshes cannot set or clear it.
Expiry/hiding retain it. New source observations update only source-owned fields.
The previous version of an updated event is kept in its run record's `before` field.

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