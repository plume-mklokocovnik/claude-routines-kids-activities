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

| Concern | New format |
|---|---|
| Fast planning | Starred shortlist first, then the complete chronological calendar |
| Narrow screens | Four columns, with category and exact ID below the event title |
| Long calendar | Month navigation and dated daily headings |
| Prices | Full published text, with a free marker only when `is_free` is explicitly true |
| Missing time | `?`, never a fictional midnight |
| Maps and evidence | Source link on the title, Maps link on the venue |
| Secondary information | Category summary and hidden-rule audit in native Markdown details sections |
| Replay | Both reports derive only from stored state and structured run records |
| Coverage | Every discovery pass and attempted source has an explicit outcome in the run report |

Stars appear both in the shortlist and their chronological position. That is
intentional duplication, not two database records. IDs remain unchanged and
copyable. All active events remain visible in the calendar, with no page-size
limit or silent truncation. Hidden and expired event records remain in the database.

This remains GitHub-compatible Markdown, not a web app. Four columns reduce
width, but long IDs or source text can still require horizontal scrolling on a
small phone. Full prices trade some row height for accuracy. Native details
sections may expand in renderers that do not support interactive HTML.

## Ownership and Verification

[render.py](../scripts/render.py) owns the calendar. [report.py](../scripts/report.py)
owns sweep reports. [run.py](../scripts/run.py) regenerates both from stored input.
No agent should hand-patch a generated report to improve its layout.

Tests cover stable output, exact IDs, star visibility, timezone conversion,
unknown times, full price text, HTML/link escaping and contiguous daily tables.
`python3 scripts/run.py check` verifies committed output equals fresh rendering.
The legacy [diff.md](../diff.md) stays untouched until the first structured run.
Its historical narrative cannot be faithfully reconstructed into invented data.