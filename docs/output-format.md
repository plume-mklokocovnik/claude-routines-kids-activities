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
| Fast planning | One section per swipe category, decided ones first, then what is left |
| Seeing the shape at a glance | A counts table with the next date per category, linking to each section |
| Narrow screens | Four columns, with category and exact ID below the event title |
| Long undecided list | Month navigation and dated daily headings inside that section |
| Prices | Full published text, with a free marker only when `is_free` is explicitly true |
| Missing time | `?`, never a fictional midnight |
| Maps and evidence | Source link on the title, Maps link on the venue |
| Secondary information | Category summary and hidden-rule audit in native Markdown details sections |
| Replay | Both reports derive only from stored state and structured run records |
| Coverage | Every discovery pass and attempted source has an explicit outcome in the run report |

The shortlist described in the findings was a list of starred events. Stars were
replaced by the three swipe categories, and `currently_active.md` became
[overview.md](../overview.md), organised by those categories rather than by what
happens to be active. Each event appears in exactly one section, with identical
detail in all four, so nothing is summarised away. The three decided sections
carry the date in the first column, because they are not grouped under daily
headings. Undecided keeps the month navigation and daily headings, since it is
the section that stays long.

Ordering puts the decisions first and the backlog last: what has been chosen is
what gets planned around, and the undecided pile is the work still to do in the
app. IDs remain unchanged and copyable. There is no page-size limit or silent
truncation. Hidden and expired event records remain in the database, and the
overview lists neither, so an event decided long ago drops out of the file once
it expires while keeping its decision in `db.json`.

This remains GitHub-compatible Markdown, not a web app. Four columns reduce
width, but long IDs or source text can still require horizontal scrolling on a
small phone. Full prices trade some row height for accuracy. Native details
sections may expand in renderers that do not support interactive HTML.

## Ownership and Verification

[render.py](../scripts/render.py) owns the overview. [report.py](../scripts/report.py)
owns sweep reports. [run.py](../scripts/run.py) regenerates both from stored input.
No agent should hand-patch a generated report to improve its layout.

Tests cover stable output, exact IDs, timezone conversion, unknown times, full
price text, HTML/link escaping, contiguous daily tables and the placement of
each event in exactly one category section.
`python3 scripts/run.py check` verifies committed output equals fresh rendering.
The legacy [diff.md](../diff.md) stays untouched until the first structured run.
Its historical narrative cannot be faithfully reconstructed into invented data.