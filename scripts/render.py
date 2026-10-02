"""Formatting helpers shared by the sweep report and the swipe app.

Slovenian labels and dates, Markdown-safe cells and links, and the wording for
price, age and notes. [report.py](report.py) builds diff.md from these and
[app/build_static.py](../app/build_static.py) builds the app's cards from them, so an event
reads the same in both. Nothing here reads the database or the wall clock, and
there is no report of its own: the live view of the current state is the app.
"""

import re
from html import escape
from urllib.parse import quote

import state

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
