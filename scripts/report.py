"""Render a run report from a persisted run record, never from the current clock."""

import render


def table(headers, rows):
    return ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers),
            *["| " + " | ".join(row) + " |" for row in rows]]


def build(record):
    batch, results = record["input"], record["results"]
    out = [f"# Routine Run: {render.cell(batch['started_at'])}", "", f"Run: `{batch['run_id']}`", ""]
    groups = ("new", "updated", "expired", "hidden", "filtered", "deferred", "unchanged")
    out += table([group.title() for group in groups], [[str(len(results[group])) for group in groups]])
    out += ["", "## Discovery Coverage", ""]
    out += table(["Pass", "Status", "Notes"], [
        [render.cell(name), render.cell(result["status"]), render.cell(result.get("reason", ""))]
        for name, result in sorted(batch["passes"].items())])
    for group in groups:
        out += ["", f"## {group.title()}", ""]
        items = results[group]
        if not items:
            out += ["_No new events found in this run._" if group == "new" else "_None._"]
            continue
        rows = []
        for item in sorted(items, key=lambda item: (item.get("start_time", ""), item.get("event_id", ""), item["title"])):
            start = render.parse_dt(item.get("start_time"))
            when = f"{start:%d.%m.%Y} {render.hour_text(item, start)}" if start else "?"
            detail = item.get("reason", "")
            if group == "updated":
                detail = ", ".join(sorted(field for field in item if field != "before"
                                          and item["before"].get(field) != item[field]))
            title = render.title_text(item)
            details = render.cell(detail)
            if item.get("event_id"):
                title += f"<br>{render.code(item.get('category'))}<br>{render.code(item['event_id'])}"
                details = f"{render.age_text(item)} / {render.price_text(item)}<br>{details}"
                if render.notes_text(item):
                    details += f"<br>{render.cell(render.notes_text(item))}"
            rows.append([when, title, render.place_text(item) if item.get("venue") else "?", details])
        out += table(["When", "Event / ID", "Place", "Age / price / notes"], rows)
    out += ["", "## Unconfirmed Leads", ""]
    out += table(["Lead", "Source", "Missing"], [
        [render.cell(item["title"]), render.link("source", item["url"]), render.cell(item["reason"])]
        for item in batch["leads"]]) if batch["leads"] else ["_None._"]
    out += ["", "## Sources", ""]
    out += table(["Source", "Pass", "Status", "Checked", "Notes"], [
        [render.link(source["url"], source["url"]), render.cell(source["pass"]),
         render.cell(source["status"]), render.cell(source.get("checked_at", "?")),
         render.cell(source.get("reason", ""))]
        for source in sorted(batch["sources"], key=lambda source: (source["pass"], source["url"]))])
    out += ["", "## Runtime Notes", ""]
    out += [f"- {render.cell(note)}" for note in batch["runtime_notes"]] or ["_None._"]
    out += [""]
    return "\n".join(out)