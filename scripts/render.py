#!/usr/bin/env python3
"""Render currently_active.md from db.json.

Deterministic, stdlib only. The routine calls this instead of hand-writing the
active list, so the table format never drifts between runs.

    python3 scripts/render.py            # writes currently_active.md
    python3 scripts/render.py --stdout   # prints instead of writing
"""

import argparse
import json
import os
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Europe/Ljubljana")
except Exception:  # pragma: no cover - fallback when tzdata is missing
    TZ = timezone(timedelta(hours=2))

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(REPO, "db.json")
OUT_PATH = os.path.join(REPO, "currently_active.md")

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
    return str(text or "").replace("|", "\\|").replace("\n", " ").strip()


def parse_dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def add_months(dt, months):
    month = dt.month - 1 + months
    year = dt.year + month // 12
    month = month % 12 + 1
    day = min(dt.day, [31, 29 if year % 4 == 0 and (year % 100 or year % 400 == 0) else 28,
                       31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return dt.replace(year=year, month=month, day=day)


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
        return "—"
    return f"{start:%H:%M}"


def age_text(event):
    age = event.get("age_min")
    return f"`{age}+`" if age is not None else "`?`"


def price_text(event):
    raw = (event.get("price_text") or "").strip()
    if event.get("is_free") or raw.lower().startswith("brezplačno"):
        return "🆓"
    euros = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:EUR|€)", raw, re.I)
    if euros:
        return f"{euros.group(1).replace('.', ',')} €"
    if not raw or "ni navedena" in raw.lower():
        return "`?`"
    return cell(raw[:24])


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
    return f"[{cell(label)}]({maps_link(venue, city)})"


def title_text(event):
    title = cell(event.get("title") or "?")
    url = event.get("url")
    linked = f"[{title}]({url})" if url else title
    star = "⭐ " if event.get("starred") else ""
    return f"{star}{linked}<br>`{event.get('category', '?')}`"


def load(db_path):
    with open(db_path, encoding="utf-8") as handle:
        return json.load(handle)


def build(db):
    events = [e for e in db.get("events", {}).values() if e.get("status", "active") == "active"]
    events.sort(key=lambda e: (e.get("start_time") or "", e.get("title") or ""))
    hidden = list(db.get("hidden_events", {}).values())

    last_run = parse_dt(db.get("system_state", {}).get("1", {}).get("last_run")) or datetime.now(timezone.utc)
    local_run = last_run.astimezone(TZ)
    horizon = add_months(local_run, 3)
    free_count = sum(1 for e in events if e.get("is_free"))
    starred_count = sum(1 for e in events if e.get("starred"))

    out = []
    out.append("# 📅 Upcoming Toddler Activities in Ljubljana")
    out.append("")
    out.append("| Zadnja posodobitev | Aktivni dogodki | Brezplačni | ⭐ Zaznamovani | Okno do | Skriti |")
    out.append("|---|---|---|---|---|---|")
    out.append(
        f"| {local_run:%Y-%m-%d %H:%M} | {len(events)} | {free_count} | {starred_count} | "
        f"{si_date(horizon)} | {len(hidden)} |"
    )
    out.append("")

    # Category overview
    by_category = {}
    for event in events:
        by_category.setdefault(event.get("category") or "?", []).append(event)
    out.append("| Zvrst | Št. | Naslednji |")
    out.append("|---|---|---|")
    for category in sorted(by_category, key=lambda c: (-len(by_category[c]), c)):
        rows = by_category[category]
        first = parse_dt(rows[0].get("start_time"))
        out.append(f"| `{category}` | {len(rows)} | {first:%d.%m.} |" if first
                   else f"| `{category}` | {len(rows)} | – |")
    out.append("")
    out.append("**Opombe:** `starost?` starost nad 4, a verjetno primerno · `daljša pot` nad ~45 min · "
               "`razprodano` / `nepotrjeno` / `prijava` veljajo za vstopnino.")
    out.append("")
    out.append("> Dogodek skriješ z njegovim **ID**: `/hide-event <ID>` ali \"skrij <ID>\".")
    out.append("> Dogodek obeležiš kot zanimiv (⭐) z njegovim **ID**: `/star-event <ID>` ali \"zaznamuj <ID>\".")
    out.append("")
    out.append("---")
    out.append("")

    current_day = None
    for event in events:
        start = parse_dt(event.get("start_time"))
        day = start.date() if start else None
        if day != current_day:
            if current_day is not None:
                out.append("")
            current_day = day
            out.append(f"## 📆 {day_heading(start)}" if start else "## 📆 Datum ni znan")
            out.append("")
            out.append("| Ura | Dogodek | Kje | Starost | Cena | Opombe | ID |")
            out.append("|---|---|---|---|---|---|---|")
        out.append(
            f"| {hour_text(event, start)} | {title_text(event)} | {place_text(event)} | "
            f"{age_text(event)} | {price_text(event)} | {cell(notes_text(event))} | "
            f"`{event.get('event_id', '')}` |"
        )

    if hidden:
        out.append("")
        out.append("---")
        out.append("")
        out.append("## 🙈 Skriti dogodki")
        out.append("")
        out.append("Skrito na tvojo zahtevo. Rutina jih ne pobira več. Vrneš jih z `/hide-event unhide <ID>`.")
        out.append("")
        out.append("| ID / vzorec | Dogodek (primer) | Obseg | Skrito | Razlog |")
        out.append("|---|---|---|---|---|")
        for item in sorted(hidden, key=lambda h: h.get("hidden_at") or ""):
            hidden_at = parse_dt(item.get("hidden_at"))
            out.append(
                f"| `{cell(item.get('match') or item.get('event_id'))}` | {cell(item.get('title'))} | "
                f"{cell(item.get('scope', 'event'))} | {hidden_at:%Y-%m-%d} | {cell(item.get('reason'))} |"
                if hidden_at else
                f"| `{cell(item.get('match') or item.get('event_id'))}` | {cell(item.get('title'))} | "
                f"{cell(item.get('scope', 'event'))} | – | {cell(item.get('reason'))} |"
            )

    out.append("")
    return "\n".join(out)


def main_write(db_path=DB_PATH, out_path=OUT_PATH):
    """Render and write the active list. Importable so hide_event.py can refresh it."""
    content = build(load(db_path))
    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write(content)
    return out_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default=DB_PATH)
    parser.add_argument("--out", default=OUT_PATH)
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()

    if args.stdout:
        print(build(load(args.db)))
        return
    print(f"wrote {main_write(args.db, args.out)}")


if __name__ == "__main__":
    main()
