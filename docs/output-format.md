# Output Evaluation

## Findings

The original calendar was deterministic when its run timestamp existed, but
silently used the wall clock otherwise. Its seven-column tables placed long IDs
in a separate column, increasing horizontal scrolling. The overview preceded
the events, five starred selections were scattered through the list, and 44
hidden references occupied an expanded table at the bottom.

Price shortening introduced a more serious problem. Taking the first euro
amount or treating any text beginning with "free" as a free event could hide
participant fees and ticket conditions. The hand-authored run report also had
independent counts, formatting and dates that could drift from the database.

## Decisions

These apply to the sweep report and to the app, which format events with the same
helpers in [render.py](../scripts/render.py).

| Concern | Format |
|---|---|
| Narrow screens | The report keeps four columns, with category and exact ID below the event title |
| Prices | Full published text, with a free marker only when `is_free` is explicitly true |
| Missing time | `?`, never a fictional midnight |
| Maps and evidence | Source link on the title, Maps link on the venue |
| Replay | The report derives only from stored state and structured run records |
| Coverage | Every discovery pass and attempted source has an explicit outcome in the run report |
| Full detail | The app opens every field it holds for an event in a dialog on a tap |

## Retiring the Markdown calendar

The current state used to be a generated Markdown file, first a chronological
calendar, then an overview grouped by the three swipe categories. It is gone, and
the [app](../app/README.md) is the view of the current state now: a list per
category, one for everything undecided, and a dialog with the full detail of any
event.

The file was retired because it could only ever describe the database, and keeping
it in step cost more than it gave. Every command that changed a decision had to
re-render it, a swipe session rewrote it in Git on every card, and a table row
could not show more than it already did without growing.

The trade-offs are real, and were accepted:

- Events can no longer be browsed on GitHub without opening the app.
- The hidden-rule audit table has no rendered view. `python3 scripts/hide_event.py
  list` prints the same references.
- The published app is current, not live: it is rebuilt from `db.json` whenever a
  change reaches `main`.

Earlier versions of the file remain in Git history. Hidden and expired event
records remain in the database. The app stops showing an event once its date in
Ljubljana has passed, but a decision on it stays in `db.json`.

## Ownership and Verification

[report.py](../scripts/report.py) owns the sweep report and
[run.py](../scripts/run.py) regenerates it from stored input. No agent should
hand-patch a generated report to improve its layout. [render.py](../scripts/render.py)
holds the shared formatting helpers and writes nothing.

Tests cover stable output, exact IDs, timezone conversion, unknown times, full
price text and HTML/link escaping in the helpers, and the card fields, the API and
the client's element lookups in the app. `python3 scripts/run.py check` verifies
that the committed sweep report equals fresh rendering.
