# Periodic Discovery Runbook

## Contract

Discover scheduled activities using [the discovery policy](reference/discovery.md).
Use the repository as the only persistent memory. Keep all database records and
preferences. A completed sweep has structured evidence, validated state and
reproducible reports. An incomplete or blocked run must be reported as such.

Commands below run from the checkout root. Python 3.11+ and the IANA
`Europe/Ljubljana` timezone are required. Use the runtime's checkout and assigned
branch, not a hardcoded path or branch name.

## 1. Preflight

1. Read [AGENTS.md](AGENTS.md). Inspect `git status --short` and the assigned branch.
   Do not overwrite local work. Use a separate clean checkout if necessary.
2. Fetch the default branch when credentials and runtime policy permit. Verify
   this checkout includes its latest state before discovery. If freshness cannot
   be established, report it and do not publish a sweep as current.
3. Validate the existing state. Missing or invalid state is a hard stop.

   ```bash
   python3 scripts/run.py validate
   python3 scripts/run.py begin
   ```

4. Keep the printed `.work/<run_id>/input.json` path. It captures `started_at` and
   `base_sha256`. Do not change either. Compute the three-month horizon from this
   captured clock, not from a later call to the wall clock.
5. Read [the URL index](reference/links.md), including do-not-retry entries, and
   [the discovery policy](reference/discovery.md). Load current user rules and
   existing IDs from the database. Read the last run's leads and source failures.
   Until a structured run exists, use [diff.md](diff.md) for that context.

## 2. Discover

Account for each pass in the staged input. Use Slovenian search terms and source
text. Derive month names and years from the current horizon, including year rolls.

| Input pass key | Work | Additional reference |
|---|---|---|
| `ljubljana` | Priority aggregators and venues, including the complete MOL calendar | [sources.md](reference/sources.md) as needed |
| `slovenia` | Regional events worth the trip on their own | [regions.md](reference/regions.md) |
| `concerts_generic` | Generic children's concerts, free first, then paid | Discovery policy Pass 3A |
| `concerts_watchlist` | Each named artist, each month, Slovenia-wide | [artists.md](reference/artists.md) |
| `free_entry` | Dated free museum, gallery and memorial-house entry | Discovery policy Pass 4 |
| `avto_moto` | Veteran cars, motorbikes and visitor meetups, Slovenia-wide | Regional calendar and SVAMZ recipe |

Run generic concerts before the watchlist. Check [annual fixtures](reference/annual.md)
only when their event or booking window is relevant. Record early booking leads
outside the event horizon as leads, not active candidates.

Record every attempted URL with its pass, outcome and check timestamp. Open the
actual event page before saving. Confirm social claims with a non-social source.
For access failures, use the bounded fallbacks in the URL index. Distinguish
bot-blocking, seasonal pages, moved paths and dead domains. Never bypass logins.

One failed source does not abort a run. Record partial/skipped/failed passes and
their reasons. A total source outage or no successful pass leaves state unchanged.
Do not mark coverage complete merely because the calendar contains old events.

## 3. Stage

Populate the input according to [the data contract](docs/data-contract.md).

- `candidates`: confirmed, in-scope event fields only. Reuse known IDs for corrections.
  Omit the ID on a genuinely new event to let the script generate it.
- `sources`: fetched URL, pass, status, timestamp, and failure reason where relevant.
- `passes`: all six keys, each with `ok`, `partial`, `failed` or `skipped`.
- `filtered`: out-of-scope discoveries with title, URL and reason.
- `leads`: unconfirmed or early-booking leads with title, URL and missing evidence.
- `runtime_notes`: factual access issues, skipped work and execution constraints.

Do not set `decision`, `status`, `first_seen` or user-rule fields in candidates.
The merger keeps these under their owning workflow. It applies user exclusions,
deduplication, horizon checks and expiry. Use the policy for semantic filtering,
including its single-ticket and open-door exceptions. Never exclude on age alone
or time of day.

For parallel discovery, researchers return isolated candidate/evidence lists to
the coordinator. Only the coordinator fills the final input and applies it.

## 4. Validate and Apply

```bash
python3 scripts/run.py apply .work/<run_id>/input.json --dry-run
python3 scripts/run.py apply .work/<run_id>/input.json
python3 scripts/run.py check
```

Inspect the dry-run counts before applying. The command retains expired/hidden
records and writes an immutable `runs/<run_id>.json` record, then the database and
the sweep report. Report content is computed before any write. Each file is replaced
atomically. The set of files is not a filesystem-wide transaction.

If interrupted after the database write, rerun the identical apply command. It
recognizes the completed database hash and repairs the report. If interrupted
before that write, retry the same input against the unchanged base. A run ID may
never be reused with different input. `render` also repairs stale derived output.

If the checksum check rejects the run, someone changed the database during
research. Begin again against the newest state, reconcile the candidates and
coverage, then validate. Do not edit the old checksum to force acceptance.

A successful zero-new-event run still advances `last_run`, records coverage and
produces the explicit no-new-events report. Missing a source listing is not proof
of cancellation. Do not delete or expire a future event just because it was absent.

## 5. Publish and Report

1. Review changed paths and validation results. Update the source index only for
   evidence gathered in this run. Preserve earlier observations when adding a new one.
2. Publish only when authorized by the scheduled task. Stage explicit paths:
   database, the sweep report, this run record and any intentional reference updates.
   Do not stage `.work/`, lock files, credentials or unrelated changes.
3. Use `chore: Routine sweep <YYYY-MM-DD>` when committing a sweep. No ticket key.
   Respect the runtime's branch and repository protection policy. If a direct push
   is disallowed, publish a branch/PR and leave it for the normal review process.
4. A rejected push means the remote may contain newer preferences. Do not rebase
   generated database edits blindly. Start from the latest state in a clean
   checkout and re-run the staged merge. Never force-push or auto-merge a fallback PR.
5. Report run ID, new/updated/expired counts, incomplete passes, validation outcome
   and publication status or PR URL. A local success is not a successful remote
   publication. Report blocked publication without claiming that the run shipped.

Use scheduler-level serialization for publishing. The script lock covers only
processes sharing one checkout. Checksum protection covers changes to that local
database, not remote writers. Run evidence is immutable. Publication results go
in the cloud job output or PR, not a post-commit edit of the run record.