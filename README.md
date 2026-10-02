# Kids Activities

Scheduled activities for Ljubljana and family trips across Slovenia. Discovery
uses public event sources. Python scripts own state changes and the sweep report.

Open [the app](https://plume-mklokocovnik.github.io/claude-routines-kids-activities/), which lists every
event with its full details, or [the latest sweep report](diff.md).

## Layout

| Location | Purpose |
|---|---|
| [AGENTS.md](AGENTS.md) | Short entry point for any agent |
| [routine.md](routine.md) | Periodic discovery runbook |
| [reference/](reference/README.md) | Discovery policy, URLs, fixtures and artist watchlist |
| [db.json](db.json) | Canonical event records, user preferences and lifecycle state |
| [scripts/](scripts/) | Standard-library state, preference and rendering commands |
| [app/](app/README.md) | Browser app: the live view of every event, and swiping into three categories |
| [inbox/](inbox/README.md) | Decision patches from the published app, applied then removed |
| [docs/data-contract.md](docs/data-contract.md) | Database and staged-run contracts |
| [docs/output-format.md](docs/output-format.md) | Output evaluation and rendering decisions |
| [tests/](tests/) | Offline tests using temporary databases |

Completed sweeps also create an immutable JSON record under `runs/`. Temporary
research inputs live in `.work/` and are ignored by Git. The database and both
reader-facing reports stay at their original root paths.

## Requirements

Python 3.11 or newer on Linux or macOS, with the IANA `Europe/Ljubljana` timezone
installed. No Python packages are needed. The cloud discovery agent also needs
web search, page fetching and repository access. Optional source recipes use
`curl` and `pdftotext`.

## Commands

Run from the repository root. Scripts resolve default paths from their own
location, so they also work when invoked by absolute path from another directory.

```bash
python3 scripts/run.py validate
python3 scripts/run.py render
python3 scripts/run.py check
```

`render` reproduces the sweep report from stored data. It never contacts sources, advances
the clock or expires events. `check` is read-only and fails when an output is stale.

## Preferences

Use an exact event ID from either report, or an unambiguous title/venue fragment.

```bash
python3 scripts/hide_event.py hide <event_id> --reason "not interested"
python3 scripts/hide_event.py hide <event_id> --scope series
python3 scripts/hide_event.py hide <event_id> --scope venue
python3 scripts/hide_event.py unhide <event_id>
python3 scripts/hide_event.py list
python3 scripts/hide_event.py apply <patch-file>
python3 scripts/hide_event.py expired
```

`apply` hides every event ID listed in a file, one per line, each as a single
event with the reason `hidden from the app`. The published app uses it for its
hide-all-Zavrnjeno button, through [inbox/](inbox/README.md). A hidden event
leaves every list and count in the app, and its category is kept.

`expired` hides every event whose stored status is `expired`, each by its ID with the
reason `expired`. It reads the status a sweep wrote, never the clock.
[hide-expired.yml](.github/workflows/hide-expired.yml) runs it every midnight in
Ljubljana and republishes the site.

Each command updates the database atomically. A hide retains the complete event record. An unhide removes the exclusion
and restores retained records as of the last sweep clock. Old hidden references
whose event rows were deleted by earlier versions remain intact, but their
missing details must be rediscovered. Nothing is fabricated to reconstruct them.

All commands accept `--db /path/to/db.json` before the subcommand. Reports and
run records then stay beside that database, which makes sandbox runs convenient.

## Categories

Each event can also be sorted into one of three user-owned categories:
`interested`, `maybe` or `rejected`. This is independent of hiding. A rejected
event is not hidden: it stays in the app's Zavrnjeno list, where it can be changed.

```bash
python3 scripts/swipe.py set <event_id> interested
python3 scripts/swipe.py clear <event_id>
python3 scripts/swipe.py undo
python3 scripts/swipe.py list [--category maybe]
python3 scripts/swipe.py stats
```

`undo` reverses the most recent change from the stored `decision_log`, so it
also works in a later session. The same operations have a phone-sized browser
UI, with swipe gestures for the three categories and a review list per category,
plus one for everything still undecided. Tapping any event there opens all of its
details. It is published to GitHub Pages, where it reads a baked snapshot and
hands decisions back through the repository for `swipe.py apply` to write:

<https://plume-mklokocovnik.github.io/claude-routines-kids-activities/>

See [app/README.md](app/README.md) for gestures, keys, the published build, how
saving from it works and how to preview a change locally.

## Cloud Schedule

The cloud already has repository access. Configure its periodic agent task with:

> Read AGENTS.md and execute routine.md from this checkout. Use the staged run
> commands. Preserve all database records and user preferences. Report coverage,
> validation and publication status. Follow the configured branch and permission
> policy for publishing.

Use a fresh checkout of the latest default branch and allow only one publishing
sweep per repository at a time. No workstation path, persistent home directory,
local conversation memory or provider-specific SDK is required. The cloud agent
does research. The scripts validate and apply its structured results.

The included GitHub Actions workflows validate changes and report consistency,
publish the app to Pages, apply decision patches committed into `inbox/` and
hide the event lists committed into `inbox/hide/`. One also hides expired events
nightly.
None of them discovers events or installs a cloud schedule for sweeps. Scheduling and
write credentials remain with the existing cloud runtime. Direct pushes or PRs
follow that runtime's explicit permissions, never an automatic protection bypass.

## Tests

Focused examples:

```bash
python3 -m unittest discover -s tests -p test_run.py -v
python3 -m unittest discover -s tests -p test_preferences.py -v
python3 -m unittest discover -s tests -p test_render.py -v
python3 -m unittest discover -s tests -p test_swipe.py -v
python3 -m unittest discover -s tests -p test_app.py -v
python3 -m unittest discover -s tests -p test_build_static.py -v
python3 -m unittest discover -s tests -p test_days.py -v
python3 -m unittest discover -s tests -p test_snapshot.py -v
```

The complete offline suite is `python3 -m unittest discover -s tests -v`.
Tests never mutate the repository database or contact event sources.
