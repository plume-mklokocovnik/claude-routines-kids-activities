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
   captured clock, not from a later call to the wall clock. Run `begin` before the
   first fetch. A page read before `begin` is not evidence for this run.
5. Read the last run's leads, failed sources and runtime notes from its record's
   `input` in `runs/<latest_run>.json`, not the whole report. Whoever researches a pass
   reads [the URL index](reference/links.md), including do-not-retry entries, and
   [the discovery policy](reference/discovery.md) for that pass. A coordinator that
   delegates every pass does not load them itself.

## 2. Discover

Account for each pass in the staged input. Use Slovenian search terms and source
text. Derive month names and years from the current horizon, including year rolls.

Every scheduled run works all six passes. A previous run's coverage, a thin web search
and the length of the run are not reasons to skip one. `skipped` means the pass could
not run at all, for example a missing tool, and the reason names that cause. Read each
pass's minimum sources before searching. They do not depend on the web search tool,
which is US-region and returns little for Slovenian local events. Mark a pass `ok` only
when its whole minimum set was read, and `partial` when part of it was. Recipes are in
[links.md](reference/links.md).

| Pass | Minimum sources, read every run |
|---|---|
| `ljubljana` | MOL calendar (`nrOfItems=100`), MKL events API, Napovednik API `For-children`, Kinodvor Kinobalon, Kino Bežigrad index with start times, LGL schedule pages 1 to 3, SiTi Teater, MGML events, Ljubljanski grad, the Cankarjev dom feed, the vsi-eventi children's listing, Citypark, the ZOO check |
| `slovenia` | Napovednik API rows outside Ljubljana (`For-children`, `Events`), Zgodovinska mesta, and the regional source for every [regions.md](reference/regions.md) fixture inside the horizon |
| `concerts_generic` | Napovednik API `Music`, the musical rows of `For-children` and of the Cankarjev dom feed, then the Pass 3A queries |
| `concerts_watchlist` | The dated query set for every artist and every month in the horizon, then each artist's confirm-at page from [artists.md](reference/artists.md) |
| `free_entry` | `sms-muzeji.si`, the first-Sunday pages of Narodna galerija, Narodni muzej, SEM and MAO, MGML, and every Pass 4 named check due in the horizon |
| `avto_moto` | SVAMZ Firestore calendar, Moto klub MAK, Zveza SVS news, then the Pass 5 queries |

Every [annual fixture](reference/annual.md) dated inside the horizon must end the run
as a stored event, a candidate or a lead that names the missing evidence. Check the
stored events first, so a fixture saved earlier is not searched again.

| Input pass key | Work | Additional reference |
|---|---|---|
| `ljubljana` | Priority aggregators and venues, including the complete MOL calendar | [sources.md](reference/sources.md) as needed |
| `slovenia` | Regional events worth the trip on their own | [regions.md](reference/regions.md) |
| `concerts_generic` | Generic children's concerts, free first, then paid | Discovery policy Pass 3A |
| `concerts_watchlist` | Each named artist, each month, Slovenia-wide | [artists.md](reference/artists.md) |
| `free_entry` | Dated free museum, gallery and memorial-house entry | Discovery policy Pass 4 |
| `avto_moto` | Veteran cars, motorbikes and visitor meetups, Slovenia-wide | Regional calendar and SVAMZ recipe |

Named checks. Settle each of these explicitly every run, even when the pass around it
finds nothing. A campaign whose window is outside the horizon is not due, so skip it
silently. One that is inside the horizon but not published yet is a lead, never a
candidate, and is checked again on the next run.

| Check | Pass | Window and where to look |
|---|---|---|
| Za družine brezplačno (Teden družin) | `free_entry` | 15 to 22 May. ZPMS announces it only days ahead, so expect a lead first |
| Mednarodni dan muzejev | `free_entry` | 18 May, inside Teden družin. Participating museum sites |
| Poletna muzejska noč (Noč muzejev) | `free_entry` | Third Saturday of June. `sms-muzeji.si` |
| Ta veseli dan kulture | `free_entry` | 3 December. Each participating museum or gallery is its own event. Ljubljana venues first, then regional ones worth the trip |
| December in Ljubljana | `ljubljana` | Prižig lučk, Miklavžev sprevod, Čarobni gozd, Dedek Mraz in Park Zvezda, Ana Mraz and Silvestrovanje za otroke. MOL calendar and the Visit Ljubljana December page from late October |
| Dejan Dogaja, free and paid appearances | `concerts_watchlist` | Any month. Organiser calendars, since he publishes none |
| Vila Eksena, free and paid appearances | `concerts_watchlist` | Any month. Organiser calendars, since she publishes none |
| ZOO Ljubljana activities and events | `ljubljana` | Every run. Follow the [ZOO check](reference/sources.md#zoo-ljubljana): news, the daily programme, the shop API and one press search. Record the outcome even when the zoo publishes nothing dated |

Price never gates a save for any watchlist artist. Save free and paid appearances alike and
let the reader decide.

Queries, lead times and the free-entry test are in
[Pass 4](reference/discovery.md#pass-4--free-entry-to-museums-galleries-and-memorial-houses)
and [artists.md](reference/artists.md).

Run generic concerts every time, also when a watchlist artist has a date. Check [annual fixtures](reference/annual.md)
only when their event or booking window is relevant. Record early booking leads
outside the event horizon as leads, not active candidates.

Record every attempted URL with its pass, outcome and check timestamp. The timestamp
is when that page was actually fetched, taken from `date -Iseconds` or the tool output.
Never a rounded, estimated or shared batch time. `apply` rejects a check time later
than the moment it runs. Open the actual event page before saving. Confirm social claims with a non-social source.
For access failures, use the bounded fallbacks in the URL index. Distinguish
bot-blocking, seasonal pages, moved paths and dead domains. Never bypass logins.

One failed source does not abort a run. Record partial/skipped/failed passes and
their reasons. A total source outage or no successful pass leaves state unchanged.
Do not mark coverage complete merely because the calendar contains old events.

### Parallel research

Claude Code routines support subagents, so the session coordinates and the
[sweep-researcher](.agents/agents/sweep-researcher.md) subagents research. The
researcher runs on Sonnet at medium effort, set in its file. Without subagent
support, one session works the same groups in sequence with the same files.

1. Right after `begin`, read the structured sources once. This takes about two
   minutes and writes compact rows with real check times to `.work/<run_id>/fetch/`:

   ```bash
   python3 scripts/fetch.py .work/<run_id>/input.json pull
   ```

2. Start one researcher per group in the background, all in one message. Give each
   the input path, its research file name, its passes and the minimum sources above.
   Do not paste reference text into the prompt. The researcher reads its own.

   | Research file | Passes | Fetch files |
   |---|---|---|
   | `ljubljana-listings` | `ljubljana` | `mol`, `mkl`, `kinobezigrad`, `cankarjevdom`, `zoo`, `vsieventi`, Ljubljana rows of `napovednik`. Also the rest of the ZOO check |
   | `ljubljana-venues` | `ljubljana` | None. Kinodvor, LGL, SiTi, MGML, Ljubljanski grad, Citypark and the December check |
   | `slovenia` | `slovenia` | `napovednik` rows with `pass_hint: slovenia` |
   | `concerts-generic` | `concerts_generic` | `napovednik` `Music` rows, the musical `For-children` rows and the concert rows of `cankarjevdom` |
   | `concerts-watchlist` | `concerts_watchlist` | None |
   | `free-entry` | `free_entry` | None |
   | `avto-moto` | `avto_moto` | `svamz` |

3. When every researcher has finished, assemble the input. `collect` rebuilds the
   lists from `research/*.json` plus the fetch records and combines the reports for
   each pass. Fix a finding in its research file and rerun `collect`, never by editing
   the input. The coordinator's own findings go in `research/coordinator.json`.

   ```bash
   python3 scripts/run.py collect .work/<run_id>/input.json
   ```

4. Check the summary for a pass reported by nobody, then dry-run as below. Repeats
   across groups collapse in the merger.

Keep coordinator context small. Read researcher replies and the `collect` summary,
not the fetch or research files, unless a dry-run error points at one.

## 3. Stage

Populate the input according to [the data contract](docs/data-contract.md).

- `candidates`: confirmed, in-scope event fields only. Reuse known IDs for corrections.
  Omit the ID on a genuinely new event to let the script generate it. Match each
  find against stored events first. A refresh under a reworded title or venue is
  filtered as a likely duplicate, and a duplicate of a hidden event stays hidden.
  When a stored `time_unknown` row now has a readable time, correct it through its ID.
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

Researchers write only their research files. Only the coordinator assembles the
final input with `collect` and applies it.

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
   Do not stage `.work/`, lock files, credentials or unrelated changes. The
   auto-merge workflow lands a `claude/*` branch on `main` only when every commit
   has the sweep subject below and the diff touches nothing outside `db.json`,
   `diff.md`, `runs/*.json` and `reference/*.md`. Anything else fails that run
   and leaves the branch for a human. When `main` moved during the sweep without
   touching `db.json`, `diff.md` or `runs/`, it replays the sweep on top first.
3. Use `chore: Routine sweep <YYYY-MM-DD>` when committing a sweep. No ticket key.
   Push the sweep to the session's own `claude/*` branch and never to `main`. The
   auto-merge workflow lands it on `main` within a minute, so the branch push is
   the whole publication step. Never open a pull request, never force-push, and do
   not add a runtime note about the branch.
4. When the auto-merge workflow refuses because `main` changed `db.json`, `diff.md`
   or `runs/` during the sweep, do not merge the database as text. The next run
   starts from the newer `main` and covers the same window again.
5. Report run ID, new/updated/expired counts, incomplete passes, validation outcome
   and the `claude/*` branch the sweep was pushed to.

Use scheduler-level serialization for publishing. The script lock covers only
processes sharing one checkout. Checksum protection covers changes to that local
database, not remote writers. Run evidence is immutable. Publication results go
in the cloud job output, not a post-commit edit of the run record.