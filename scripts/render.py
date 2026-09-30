#!/usr/bin/env python3
"""Render overview.md from db.json.

An overview of the current state, grouped the way the swipe app sorts it: one
section per category, then everything still waiting for a decision. Every
active event appears exactly once, with the same detail in every section.

Deterministic, stdlib only. The routine calls this instead of hand-writing the
overview, so the table format never drifts between runs.

    python3 scripts/render.py            # writes overview.md
    python3 scripts/render.py --stdout   # prints instead of writing
"""

import argparse
import os
import re
from urllib.parse import quote
from html import escape

import state
from state import TZ, add_months, load

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(REPO, "db.json")
OUT_PATH = os.path.join(REPO, "overview.md")

MARKS = {"interested": "👍", "maybe": "🤔", "rejected": "👎", "undecided": "🃏"}
ANCHORS = {"interested": "zanima-nas", "maybe": "mogoce", "rejected": "zavrnjeno",
           "undecided": "neodloceno"}

DAYS = ["Ponedeljek", "Torek", "Sreda", "Četrtek", "Petek", "Sobota", "Nedelja"]
MONTHS = ["januar", "februar", "marec", "april", "maj", "junij",
          "julij", "avgust", "september", "oktober", "november", "december"]

FLAG_LABELS = {
    "age_stretch": "starost?",
    "travel": "daljša pot",
    "not_toddler_appropriate": "ni za malčke",
    "time_unknown": "ura ni znana",
    "outside_ljubljana": None,  # already visible in the Kje column
}

PRICE_NOTES = [
    ("razprodano", "razprodano"),
    ("zasedeno", "zasedeno"),
    ("nepotrjeno", "nepotrjeno"),
    ("le nekaj vstopnic", "malo vstopnic"),
    ("prijava", "prijava"),
]


def cell(text):
    """Escape a value so it cannot break out of a markdown table cell."""
    text = escape(str(text or ""), quote=False).replace("\r", " ").replace("\n", " ").strip()
    return re.sub(r"([\\`*\[\]_|])", r"\\\1", text)


def link(label, url):
    if not state.valid_url(url):
        return cell(label)
    return f"[{cell(label)}]({quote(url, safe=':/?&=#%+@,;~!-._')})"


def parse_dt(value):
    if not value:
        return None
    try:
        return state.timestamp(value)
    except ValueError:
        return None


def si_date(dt):
    return f"{dt.day}. {MONTHS[dt.month - 1]} {dt.year}"


def day_heading(dt):
    return f"{DAYS[dt.weekday()]}, {si_date(dt)}"


def maps_link(venue, city):
    query = quote(f"{venue or ''} {city or 'Ljubljana'}".strip())
    return f"https://maps.google.com/?q={query}"


def hour_text(event, start):
    """Never print a fictional midnight for a source that publishes no start time."""
    if start is None or "time_unknown" in (event.get("flags") or []):
        return "?"
    return f"{start:%H:%M}"


def age_text(event):
    age = event.get("age_min")
    return f"`{age}+`" if age is not None else "`?`"


def price_text(event):
    raw = (event.get("price_text") or "").strip()
    if event.get("is_free") is True:
        return "🆓" + (f" {cell(raw)}" if raw and raw.lower() != "brezplačno" else "")
    return cell(raw) if raw else "`?`"


def notes_text(event):
    notes = []
    raw = (event.get("price_text") or "").lower()
    for needle, label in PRICE_NOTES:
        if needle in raw and label not in notes:
            notes.append(label)
    for flag in event.get("flags") or []:
        label = FLAG_LABELS.get(flag, flag)
        if label and label not in notes:
            notes.append(label)
    return ", ".join(notes)


def place_text(event):
    venue = event.get("venue") or "?"
    city = event.get("city") or ""
    label = venue if city in ("", "Ljubljana") else f"{venue}, {city}"
    return link(label, maps_link(venue, city))


def title_text(event):
    return link(event.get("title") or "?", event.get("url"))


def code(value):
    safe = escape(str(value or "?"), quote=False).replace("|", "&#124;").replace("\n", " ")
    return f"<code>{safe}</code>" if "`" in safe else f"`{safe}`"


def event_table(events, dated=False):
    """Rows for one table. `dated` carries the date in the first column, for the
    decided sections, which are not grouped under daily headings."""
    out = ["| Kdaj | Dogodek / ID | Kje | Starost / cena / opombe |" if dated
           else "| Ura | Dogodek / ID | Kje | Starost / cena / opombe |",
           "|---|---|---|---|"]
    for event in events:
        start = parse_dt(event.get("start_time"))
        when = hour_text(event, start)
        if dated:
            when = f"{start:%d.%m.%Y}<br>{when}" if start else "?"
        title = f"{title_text(event)}<br>{code(event.get('category'))}<br>{code(event.get('event_id'))}"
        details = f"{age_text(event)} · {price_text(event)}"
        notes = notes_text(event)
        if notes:
            details += f"<br>{cell(notes)}"
        out.append(f"| {when} | {title} | {place_text(event)} | {details} |")
    return out


def grouped(events):
    """Split chronologically ordered events into the three categories, plus the
    ones still waiting for a decision. Each group keeps the incoming order."""
    groups = {name: [] for name in state.DECISIONS}
    undecided = []
    for event in events:
        groups.get(event.get("decision"), undecided).append(event)
    return groups, undecided


def calendar(events):
    """Month navigation, daily headings and one row per event."""
    months = sorted({start.strftime("%Y-%m") for event in events
                     if (start := parse_dt(event.get("start_time")))})
    out = [" · ".join(f"[{MONTHS[int(month[5:]) - 1]} {month[:4]}](#mesec-{month})"
                      for month in months), ""]
    current_day, current_month = object(), None
    for event in events:
        start = parse_dt(event.get("start_time"))
        month = start.strftime("%Y-%m") if start else None
        day = start.date() if start else None
        if month != current_month:
            current_month = month
            out += ["", f'<a id="mesec-{month}"></a>', ""]
        if day != current_day:
            current_day = day
            out += ["", f"### {day_heading(start)}" if start else "### Datum ni znan", ""]
            out += event_table([])
        out += event_table([event])[-1:]
    return out


def build(db):
    last_run = parse_dt(db.get("system_state", {}).get("1", {}).get("last_run"))
    if last_run is None or last_run.utcoffset() is None:
        raise ValueError("system_state.1.last_run must be an ISO timestamp with a timezone")
    local_run = last_run.astimezone(TZ)
    horizon = add_months(local_run, 3)
    events = state.active_events(db)
    events.sort(key=lambda event: (parse_dt(event.get("start_time")) or horizon,
                                   event.get("title", ""), event.get("event_id", "")))
    hidden = [item for item in db.get("hidden_events", {}).values() if item.get("active", True)]
    free_count = sum(event.get("is_free") is True for event in events)
    groups, undecided = grouped(events)
    sections = [(ANCHORS[name], MARKS[name], state.DECISION_LABELS[name], groups[name])
                for name in state.DECISIONS]

    out = ["# Dogodki za otroke", "", "Ljubljana in izleti po Sloveniji", "",
           f"Posodobljeno **{local_run:%d.%m.%Y ob %H:%M}** (Europe/Ljubljana). "
           f"Okno do **{si_date(horizon)}**.", "",
           f"**{len(events)}** dogodkov · **{free_count}** brezplačnih · "
           f"**{len(hidden)}** skritih pravil", "",
           "| Kategorija | Število | Naslednji |", "|---|---|---|"]
    for anchor, mark, label, rows in sections + [(ANCHORS["undecided"], MARKS["undecided"],
                                                  "Neodločeno", undecided)]:
        first = parse_dt(rows[0].get("start_time")) if rows else None
        out.append(f"| [{mark} {label}](#{anchor}) | {len(rows)} | "
                   f"{f'{first:%d.%m.%Y}' if first else '-'} |")
    out += [""]

    for anchor, mark, label, rows in sections:
        out += ["", f'<a id="{anchor}"></a>', "", f"## {mark} {label} ({len(rows)})", ""]
        out += event_table(rows, dated=True) if rows else ["_Ni dogodkov v tej kategoriji._"]

    out += ["", f'<a id="{ANCHORS["undecided"]}"></a>', "",
            f"## {MARKS['undecided']} Neodločeno ({len(undecided)})", ""]
    out += calendar(undecided) if undecided else ["_Vsi dogodki so razvrščeni._", ""]

    out += ["", "<details>", "<summary>Pregled po zvrsteh</summary>", "",
            "| Zvrst | Število | Naslednji |", "|---|---|---|"]
    by_category = {}
    for event in events:
        by_category.setdefault(event.get("category") or "?", []).append(event)
    for category in sorted(by_category, key=lambda c: (-len(by_category[c]), c)):
        rows = by_category[category]
        first = parse_dt(rows[0].get("start_time"))
        when = f"{first:%d.%m.%Y}" if first else "?"
        out.append(f"| {code(category)} | {len(rows)} | {when} |")
    out += ["", "</details>", ""]
    if hidden:
        out += ["<details>", f"<summary>Skrita pravila ({len(hidden)})</summary>", "",
                "| ID / vzorec | Obseg | Skrito | Razlog |", "|---|---|---|---|"]
        for item in sorted(hidden, key=lambda item: (item.get("hidden_at", ""), item.get("match", ""))):
            hidden_at = parse_dt(item.get("hidden_at"))
            when = f"{hidden_at:%d.%m.%Y}" if hidden_at else "?"
            out.append(f"| {code(item.get('match') or item.get('event_id'))} | "
                       f"{cell(item.get('scope', 'event'))} | {when} | {cell(item.get('reason'))} |")
        out += ["", "</details>", ""]
    out += ["`?` = ni objavljeno · `starost?` = 5+ · `daljša pot` = nad približno 45 minut", "",
            "[Spremembe zadnje rutine](diff.md) · [Ukazi in navodila](README.md#preferences)", ""]
    return "\n".join(out)


def main_write(db_path=DB_PATH, out_path=OUT_PATH):
    """Render and write the active list. Importable so hide_event.py can refresh it."""
    content = build(load(db_path))
    state.atomic_write(out_path, content)
    return out_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default=DB_PATH)
    parser.add_argument("--out", default=OUT_PATH)
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()

    if args.stdout:
        print(build(load(args.db)), end="")
        return
    with state.locked(args.db):
        print(f"wrote {main_write(args.db, args.out)}")


if __name__ == "__main__":
    main()
