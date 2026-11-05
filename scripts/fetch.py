#!/usr/bin/env python3
"""Read structured event sources for a staged run and record each request with its real time.

    python3 scripts/fetch.py <input.json> pull [source ...]
    python3 scripts/fetch.py <input.json> verify --pass <pass> [--chars N] <url> [url ...]
    python3 scripts/fetch.py <input.json> record --pass <pass> [--failed <reason>] <url> [url ...]

`pull` reads the listed sources, or all of them, and writes one file per source to
`.work/<run_id>/fetch/`. `verify` fetches event pages and prints their title and text.
`record` stamps a page read some other way, such as WebFetch, with the current time,
so nobody writes a check time by hand. Run it right after reading the page.
Every file carries `sources` records in the staged-input shape, which
`run.py collect` copies into the input. Rows are leads for the researcher to judge.
Nothing here decides scope. Rows outside the run window or hidden by the user are
dropped, and a row that matches a stored event names it in `stored`. A row with
`verified: false` needs `verify` on its URL before it can become a candidate. A row
whose title or text announces a cancellation carries `cancelled: true`. A file header
with `notes` names a coverage gap the researcher copies into `runtime_notes`.
"""

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import threading
import time
import unicodedata
import urllib.error
import urllib.request
import xml.etree.ElementTree as ElementTree
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from http.cookiejar import CookieJar
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run
import state

USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")
WORKERS = 4
TEXT_LIMIT = 400
# Kept for the whole process. vsi-eventi accepts its Livewire POST only with the session
# cookie its listing set, because the form token on that page belongs to that session.
COOKIES = CookieJar()


def http(url, data=None, timeout=40):
    """Return (status, body, reason). Status 0 means the request never got an answer.
    A body that starts with `{` is sent as JSON, any other body as a form."""
    body = data.encode() if data is not None else None
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/json,*/*",
               "Accept-Language": "sl,en;q=0.5"}
    kind = "application/json" if data is not None and data.lstrip().startswith("{") \
        else "application/x-www-form-urlencoded"
    if body is not None:
        headers["Content-Type"] = kind
    request = urllib.request.Request(url, data=body, headers=headers)
    COOKIES.add_cookie_header(request)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            COOKIES.extract_cookies(response, request)
            return response.status, response.read().decode("utf-8", "replace"), ""
    except urllib.error.HTTPError as error:
        return error.code, "", f"HTTP {error.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        reason = f"No answer: {getattr(error, 'reason', error)}"
    # Some hosts fail Python's TLS or connection handling and still answer curl.
    if not shutil.which("curl"):
        return 0, "", reason
    command = ["curl", "-sL", "--max-time", str(timeout), "-A", USER_AGENT, "-H", "Accept-Language: sl,en;q=0.5",
               "-w", "\n%{http_code}", *(["-H", f"Content-Type: {kind}", "--data", data] if data is not None else []),
               url]
    try:
        result = subprocess.run(command, capture_output=True, timeout=timeout + 10)
    except subprocess.TimeoutExpired:
        return 0, "", reason
    text, _, code = result.stdout.decode("utf-8", "replace").rpartition("\n")
    status = int(code) if code.isdigit() else 0
    return status, text if status == 200 else "", "" if status == 200 else f"{reason}. curl: HTTP {status}"


class Fetcher:
    def __init__(self, get=http):
        self.get = get
        self.sources = []
        self.notes = []
        self.lock = threading.Lock()

    def fetch(self, url, pass_name, data=None, record=None):
        status, body, reason = self.get(url, data)
        if status == 200 and not body.strip():
            status, reason = 0, "Empty response"
        entry = {"url": record or url, "pass": pass_name, "status": "ok" if status == 200 else "failed",
                 "checked_at": datetime.now(state.TZ).replace(microsecond=0).isoformat()}
        if status != 200:
            entry["reason"] = reason or f"HTTP {status}"
        with self.lock:
            self.sources.append(entry)
        return body if status == 200 else None

    def json(self, url, pass_name):
        body = self.fetch(url, pass_name)
        try:
            return json.loads(body) if body else None
        except ValueError:
            return None

    def many(self, jobs):
        with ThreadPoolExecutor(WORKERS) as pool:
            return list(pool.map(lambda job: job(), jobs))


def plain(markup, limit=TEXT_LIMIT):
    text = re.sub(r"(?is)<(script|style|noscript|svg)\b.*?</\1>", " ", markup or "")
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text))).strip()
    return text[:limit].rstrip() + ("…" if len(text) > limit else "")


def page(markup, limit=1500):
    """Title, canonical URL and the text from the first heading on, without navigation."""
    title = re.search(r'(?is)<meta[^>]+property="og:title"[^>]+content="([^"]*)"', markup) or \
        re.search(r"(?is)<title[^>]*>(.*?)</title>", markup)
    canonical = re.search(r'(?is)<meta[^>]+property="og:url"[^>]+content="([^"]+)"', markup)
    body = re.sub(r"(?is)<(nav|header|footer)\b.*?</\1>", " ", markup)
    heading = re.search(r"(?i)<h1\b", body)
    text = plain(body[heading.start():] if heading else body, limit + 300)
    text = re.sub(r"Deli na:?(\s*Deli na [^()]{1,40}\(Odpre se v novem oknu\))*\s*", "", text)
    return {"title": plain(title.group(1), 200) if title else "",
            "canonical": html.unescape(canonical.group(1)) if canonical else "",
            "text": text[:limit].rstrip() + ("…" if len(text) > limit else "")}


def slug(text):
    text = unicodedata.normalize("NFKD", re.sub(r"[.'’]", "", text.casefold()))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def local(year, month, day, hour=None, minute=0):
    value = datetime(int(year), int(month), int(day), int(hour or 0), int(minute), tzinfo=state.TZ)
    return value.isoformat(), [] if hour is not None else ["time_unknown"]


def row(title, start, flags, venue, url, verified, **extra):
    item = {"title": html.unescape(title).strip(), "start_time": start, "flags": flags,
            "venue": html.unescape(venue or "").strip(), "url": url, "verified": verified}
    item.update({key: value for key, value in extra.items() if value not in (None, "", [])})
    return item


# Sources. Each takes (fetcher, context) and returns rows.

def mol(f, ctx):
    listing = "https://www.ljubljana.si/sl/aktualno/dogodki?nrOfItems=100"
    markup = f.fetch(listing, "ljubljana") or ""
    cards = []
    for card in markup.split('class="list-type--card--item"')[1:]:
        link = re.search(r'<h3[^>]*>\s*<a href="(/sl/aktualno/dogodki/[^"]+)">(.*?)</a>', card, re.S)
        when = re.search(r'date-from">\s*(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})(?:\s+(\d{1,2}):(\d{2}))?', card)
        if not link or not when:
            continue
        venue = re.search(r'item-iteration-list--item">\s*<p class="text-normal">(.*?)</p>', card, re.S)
        tags = [plain(tag, 60) for tag in re.findall(r'list-tags-item"><span>(.*?)</span>', card)]
        day, month, year, hour, minute = when.groups()
        cards.append((f"https://www.ljubljana.si{link.group(1)}", plain(link.group(2), 200),
                      local(year, month, day, hour, minute or 0), plain(venue.group(1), 200) if venue else "", tags))
    cards = [card for card in cards if ctx.in_window(card[2][0], card[2][1])]
    details = f.many([lambda url=card[0]: f.fetch(url, "ljubljana") for card in cards])
    return [row(title, start, flags, venue, url, body is not None, city="Ljubljana", tags=tags,
                notes=page(body, TEXT_LIMIT)["text"] if body else None)
            for (url, title, (start, flags), venue, tags), body in zip(cards, details)]


def mkl(f, ctx):
    url = ("https://www.mklj.si/wp-json/tribe/events/v1/events?per_page=50"
           f"&start_date={ctx.clock:%Y-%m-%d}&end_date={ctx.horizon:%Y-%m-%d}")
    rows = []
    for _ in range(30):
        data = f.json(url, "ljubljana")
        if not data:
            break
        for event in data.get("events", []):
            when = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):\d{2}", event.get("start_date", ""))
            if not when:
                continue
            year, month, day, hour, minute = when.groups()
            start, flags = local(year, month, day, None if event.get("all_day") else hour, minute)
            venue = event.get("venue") or {}
            rows.append(row(event.get("title", ""), start, flags, venue.get("venue", "") if isinstance(venue, dict) else "",
                            event.get("url", ""), False, city="Ljubljana",
                            tags=[item.get("name") for item in event.get("categories", [])],
                            price_text=event.get("cost"), notes=plain(event.get("description"))))
        url = data.get("next_rest_url")
        if not url:
            break
    return rows


NAPOVEDNIK_API = "https://api.napovednik.com/api/website/v1"


def napovednik(f, ctx):
    labels = f.json("https://napovednik.com/assets/i18n/sl.json", "ljubljana") or {}
    names = labels.get("CodeList", {})
    events = []
    for genre, pass_name in (("For-children", "ljubljana"), ("Events", "ljubljana"), ("Music", "concerts_generic")):
        data = f.json(f"{NAPOVEDNIK_API}/search?genreName={genre}", pass_name) or {}
        events += [(item, pass_name) for item in data.get("events", [])]
    seen, unique = set(), []
    for item, pass_name in events:
        if item.get("idDataEvent") not in seen:
            seen.add(item.get("idDataEvent"))
            unique.append((item, pass_name))

    def one(item, pass_name):
        town = (item.get("location") or {}).get("postalName") or ""
        if pass_name == "ljubljana" and town and not town.startswith("Ljubljana"):
            pass_name = "slovenia"
        detail = f.json(f"{NAPOVEDNIK_API}/events/{item['idDataEvent']}", pass_name) or {}
        genre = item.get("genre") or {}
        path = "/".join(slug(names.get(group, {}).get(key, key))
                        for group, key in (("Genre", genre.get("genreTranslationName", "")),
                                           ("Sub-genre", genre.get("subGenreTranslationName", ""))))
        human = f"https://napovednik.com/{path}/{slug(item.get('name', ''))}-{item['idDataEvent']}"
        body = f.fetch(human, pass_name)
        canonical = page(body)["canonical"] if body else ""
        if body and canonical and canonical != human:
            human = canonical if f.fetch(canonical, pass_name) else human
        return item, detail, human, body is not None, pass_name

    rows = []
    for item, detail, human, verified, pass_name in f.many(
            [lambda item=item, pass_name=pass_name: one(item, pass_name) for item, pass_name in unique]):
        when = re.match(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})", detail.get("eventStart") or item.get("startDateTime", ""))
        if not when:
            continue
        location = detail.get("location") or item.get("location") or {}
        venue = ", ".join(part for part in (location.get("name"), location.get("address")) if part)
        genre = item.get("genre") or {}
        rows.append(row(item.get("name", ""), *local(*when.groups()), venue, human, verified,
                        city=location.get("postalName"), pass_hint=pass_name,
                        tags=[genre.get("genreTranslationName"), genre.get("subGenreTranslationName")],
                        price_text=detail.get("ticketPrice"), organiser=item.get("organizationName"),
                        notes=plain(detail.get("descriptionSl"))))
    return rows


def kinobezigrad(f, ctx):
    base = "https://www.kino-bezigrad.si"
    markup = f.fetch(f"{base}/predstave-in-delavnice/", "ljubljana") or ""
    shows = {}
    for post, url, title in re.findall(
            r'id="post-(\d+)".*?<div class="movie_title"><a href="([^"]+/predstava/[^"]+)">(.*?)</a>', markup, re.S):
        shows.setdefault(url, (post, plain(title, 200)))

    def one(url, post, title):
        body = f.fetch(url, "ljubljana")
        if not body:
            return []
        dates = json.loads(re.search(r"movieScreeningDates\s*=\s*(\[[^\]]*\])", body).group(1)) \
            if "movieScreeningDates" in body else []
        age = re.search(r'event_restriction">\s*(\d+)\s*\+', body)
        price = re.search(r"[^.<>]*\d+,\d{2}\s*€[^.<>]*", body)
        found = []
        for date in dates:
            year, month, day = date.split("-")
            start, _ = local(year, month, day)
            if not ctx.in_window(start, ["time_unknown"]):
                continue
            ajax = f"{base}/wp-admin/admin-ajax.php"
            fields = f"action=event-filter&date={month}.{day}.{year}&post_id={post}&all_tickets="
            hours = re.findall(r'data-hour="(\d{1,2}):(\d{2})"', f.fetch(ajax, "ljubljana", fields, f"{ajax}?{fields}") or "")
            for hour, minute in sorted(set(hours)) or [(None, 0)]:
                found.append(row(title, *local(year, month, day, hour, minute), "Kino Bežigrad", url, True,
                                 city="Ljubljana", age_min=int(age.group(1)) if age else None,
                                 price_text=plain(price.group(0), 160) if price else None))
        return found

    return [item for found in f.many([lambda url=url, post=post, title=title: one(url, post, title)
                                      for url, (post, title) in shows.items()]) for item in found]


def svamz(f, ctx):
    script = f.fetch("https://svamz.com/js/dogodki-data.js", "avto_moto") or ""
    base = re.search(r'BASE\s*=\s*"([^"]+)"', script)
    key = re.search(r'KEY\s*=\s*"([^"]+)"', script)
    if not base or not key:
        return []
    base, key = base.group(1), key.group(1)
    documents, token = [], ""
    for _ in range(20):
        data = f.json(f"{base}dogodki?pageSize=300&key={key}" + (f"&pageToken={token}" if token else ""), "avto_moto")
        if not data:
            break
        documents += data.get("documents", [])
        token = data.get("nextPageToken")
        if not token:
            break

    def value(fields, name):
        return next(iter((fields.get(name) or {}).values()), "")

    picked = []
    for document in documents:
        fields = document.get("fields", {})
        when = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", value(fields, "start"))
        if when:
            start, flags = local(*when.groups())
            if ctx.in_window(start, flags):
                picked.append((document["name"].rsplit("/", 1)[-1], fields, start, flags))
    detail = [f"https://svamz.com/event.html?id={identifier}" for identifier, *_ in picked]
    fetched = f.many([lambda url=url: f.fetch(url, "avto_moto") for url in detail])
    return [row(value(fields, "title"), start, flags, value(fields, "place"), url, body is not None,
                end=value(fields, "end"), contact=value(fields, "contact"), notes=plain(value(fields, "description")))
            for (identifier, fields, start, flags), url, body in zip(picked, detail, fetched)]


def zoo(f, ctx):
    products = f.json("https://trgovina.zoo.si/wp-json/wp/v2/product?per_page=50", "ljubljana") or []
    return [{"title": html.unescape(item["title"]["rendered"]), "url": item["link"], "verified": False,
             "modified": item.get("modified"), "venue": "ZOO Ljubljana, Večna pot 70",
             "notes": plain(item["content"]["rendered"], 600)}
            for item in products if 19 in item.get("product_cat", [])]


def cankarjevdom(f, ctx):
    """The feed Cankarjev dom publishes for Kulturnik. One item per performance, with hall and start."""
    body = f.fetch("https://www.cd-cc.si/feeds/kulturnik", "ljubljana")
    try:
        items = ElementTree.fromstring(body).findall("item") if body else []
    except ElementTree.ParseError:
        items = []
    picked = []
    for item in items:
        when = re.match(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})", item.findtext("ical_dtstart") or "")
        if not when:
            continue
        year, month, day, hour, minute = when.groups()
        start, flags = local(year, month, day, None if (hour, minute) == ("00", "00") else hour, minute)
        if ctx.in_window(start, flags):
            picked.append((item, start, flags))
    # Only the youth programme gets its page read up front. Other rows are judged first.
    youth = [item.findtext("category") == "Za mlade in šole" for item, *_ in picked]
    bodies = f.many([lambda item=item, wanted=wanted: f.fetch(item.findtext("link"), "ljubljana") if wanted else None
                     for (item, *_), wanted in zip(picked, youth)])
    return [row(item.findtext("title") or "", start, flags,
                ", ".join(part for part in ("Cankarjev dom", item.findtext("ical_location")) if part),
                item.findtext("link") or "", body is not None, city="Ljubljana", tags=[item.findtext("category")],
                notes=page(body, TEXT_LIMIT)["text"] if body else None)
            for (item, start, flags), body in zip(picked, bodies)]


VSIEVENTI = "https://vsi-eventi.com"
VSIEVENTI_CARDS, VSIEVENTI_PAGES = 36, 5  # cards per page, and the most pages the site lists
VSIEVENTI_CARD = '<div class="max-w-sm bg-white'


def vsieventi(f, ctx):
    """Ljubljana's children's category on vsi-eventi.com. The listing hides each card's
    description, venue and start time behind a Livewire property that has no control on the
    page. The page's own Livewire call turns it off: one GET, then one POST per page of cards."""
    listing = (f"{VSIEVENTI}/?city=2698&categories%5B0%5D=5"
               f"&start_date={ctx.clock:%Y-%m-%d}&end_date={ctx.horizon:%Y-%m-%d}")
    markup = f.fetch(listing, "ljubljana") or ""
    token = re.search(r'<meta name="csrf-token" content="([^"]+)"', markup)
    snapshot = next((value for value in map(html.unescape, re.findall(r'wire:snapshot="([^"]*)"', markup))
                     if '"events-overview"' in value), None)
    fragments, updates, calls = [], {"hideDetails": False}, []
    for number in range(1, VSIEVENTI_PAGES + 1):
        if not token or not snapshot:
            break
        body = json.dumps({"_token": token.group(1), "components": [
            {"snapshot": snapshot, "updates": updates, "calls": calls}]})
        reply = f.fetch(f"{VSIEVENTI}/livewire/update", "ljubljana", body,
                        f"{VSIEVENTI}/livewire/update?hideDetails=false&page={number}")
        try:
            component = json.loads(reply)["components"][0]
            snapshot, fragment = component["snapshot"], component["effects"]["html"]
        except (TypeError, ValueError, KeyError, IndexError):
            break
        fragments.append(fragment)
        if "nextPage('page')" not in fragment:
            break
        updates, calls = {}, [{"path": "", "method": "nextPage", "params": ["page"]}]
    if markup and not fragments:
        f.notes.append("vsi-eventi: the Livewire details call failed, so rows come from the plain listing "
                       "without venue or start time" + (". Only its first page was read" if "nextPage('page')" in markup else ""))
        fragments = [markup]
    if len(fragments) == VSIEVENTI_PAGES and fragments[-1].count(VSIEVENTI_CARD) >= VSIEVENTI_CARDS:
        f.notes.append(f"vsi-eventi: the listing reached the site's cap of {VSIEVENTI_PAGES} pages, "
                       "so later events in the horizon may be missing")
    rows = {}
    for fragment in fragments:
        for card in fragment.split(VSIEVENTI_CARD)[1:]:
            link = re.search(r'href="(https://vsi-eventi\.com/event/[^"]+)"', card)
            title = re.search(r"<h5\b[^>]*>(.*?)</h5>", card, re.S)
            date = re.search(r'<p class="text-sm sm:text-base text-black">[^<]*?(\d{1,2})\.(\d{1,2})\.(\d{4})', card)
            if not link or not title or not date or link.group(1) in rows:
                continue
            # The venue line sits above the date and the start-time sentence below it.
            small = [(found.start(), plain(found.group(1), 300))
                     for found in re.finditer(r'<p class="text-xs md:text-sm line-clamp-2">(.*?)</p>', card, re.S)]
            venue = next((text for at, text in small if at < date.start()), "")
            when = next((text for at, text in small if at > date.start()), "")
            # "ob 16:30", "od 10.00 do 13.00". A date such as "od 15.10.2026" is not a time.
            clock = re.search(r"(?i)\b(?:ob|od)\s+(\d{1,2})[:.](\d{2})\b(?!\.\d)", when) or \
                re.search(r"\b(\d{1,2}):(\d{2})\b", when)
            hour, minute = clock.groups() if clock and int(clock.group(1)) < 24 else (None, 0)
            city = re.search(r'href="https://vsi-eventi\.com\?city=\d+"[^>]*>(.*?)</a>', card, re.S)
            about = re.search(r'<p class="text-xs md:text-base font-normal text-gray-700[^"]*">(.*?)</p>', card, re.S)
            tags = re.findall(r'<p class="items-center rounded-md bg-purple-50[^"]*">(.*?)</p>', card, re.S)
            day, month, year = date.groups()
            rows[link.group(1)] = row(plain(title.group(1), 200), *local(year, month, day, hour, minute), venue,
                                      link.group(1), False, city=plain(city.group(1), 80) if city else "Ljubljana",
                                      tags=[plain(tag, 60) for tag in tags], time_text=when,
                                      notes=plain(about.group(1)) if about else None)
    return list(rows.values())


SOURCES = {"mol": mol, "mkl": mkl, "napovednik": napovednik, "kinobezigrad": kinobezigrad,
           "cankarjevdom": cankarjevdom, "svamz": svamz, "zoo": zoo, "vsieventi": vsieventi}
CANCELLED = re.compile(r"(?i)\bodpovedan[oa]?\b|\bodpade\b|\bprestavljen[oa]?\b")


class Context:
    def __init__(self, batch, db):
        self.clock = state.timestamp(batch["started_at"])
        self.horizon = state.add_months(self.clock)
        self.db = db
        self.by_day = {}
        for key, event in db["events"].items():
            self.by_day.setdefault(state.timestamp(event["start_time"]).date(), {})[key] = event

    def in_window(self, start, flags):
        item = {"start_time": start, "flags": flags}
        return not state.expired(item, self.clock) and state.timestamp(start) <= self.horizon

    def annotate(self, rows):
        kept, dropped = [], {"outside_window": 0, "hidden": 0}
        for item in rows:
            if "start_time" not in item:
                kept.append(item)
                continue
            if not self.in_window(item["start_time"], item["flags"]):
                dropped["outside_window"] += 1
                continue
            probe = {"category": "", **item}
            same_day = self.by_day.get(state.timestamp(item["start_time"]).date(), {})
            twin_key = next((key for key, event in same_day.items()
                             if run.fingerprint(event) == run.fingerprint(probe)), None) or run.duplicate_of(probe, same_day)
            twin = same_day.get(twin_key)
            if state.hidden_reason(self.db, probe) or (twin and (twin.get("status") == "hidden"
                                                                 or state.hidden_reason(self.db, twin))):
                dropped["hidden"] += 1
                continue
            if twin:
                item["stored"] = twin["event_id"]
            if CANCELLED.search(f"{item['title']} {item.get('notes', '')}"):
                item["cancelled"] = True
            kept.append(item)
        return kept, dropped


def write(path, header, sources, rows):
    lines = ",\n".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) for item in rows)
    found = ",\n".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) for item in sources)
    head = json.dumps(header, ensure_ascii=False, separators=(",", ":"))[:-1]
    state.atomic_write(path, f'{head},"sources":[\n{found}\n],"rows":[\n{lines}\n]}}\n')


def pull(batch, db, names, folder, get=http):
    ctx = Context(batch, db)
    summary = {}
    for name in names:
        fetcher = Fetcher(get)
        started = time.monotonic()
        rows, dropped = ctx.annotate(SOURCES[name](fetcher, ctx))
        notes = {"notes": fetcher.notes} if fetcher.notes else {}
        write(folder / f"{name}.json", {"source": name, "dropped": dropped, **notes}, fetcher.sources, rows)
        failed = sum(source["status"] != "ok" for source in fetcher.sources)
        summary[name] = {"rows": len(rows), "stored": sum("stored" in item for item in rows),
                         "requests": len(fetcher.sources), "failed": failed, **dropped,
                         "seconds": round(time.monotonic() - started), **notes}
    return summary


def verify(pass_name, urls, folder, get=http, chars=1500):
    fetcher = Fetcher(get)
    bodies = fetcher.many([lambda url=url: fetcher.fetch(url, pass_name) for url in urls])
    pages = [{"url": url, "ok": body is not None, **(page(body, chars) if body else {})}
             for url, body in zip(urls, bodies)]
    write(folder / f"verify-{pass_name}-{time.time_ns()}.json", {"source": "verify"}, fetcher.sources, pages)
    return pages


def record(pass_name, urls, folder, failed=None):
    now = datetime.now(state.TZ).replace(microsecond=0).isoformat()
    sources = [{"url": url, "pass": pass_name, "status": "failed" if failed else "ok", "checked_at": now,
                **({"reason": failed} if failed else {})} for url in urls]
    for source in sources:
        if not state.valid_url(source["url"]):
            raise ValueError(f"Not a URL: {source['url']}")
    write(folder / f"record-{pass_name}-{time.time_ns()}.json", {"source": "record"}, sources, [])
    return sources


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", type=Path)
    parser.add_argument("--db", type=Path, default=state.DB_PATH)
    commands = parser.add_subparsers(dest="command", required=True)
    pulling = commands.add_parser("pull", help="read structured sources into .work/<run_id>/fetch/")
    # No `choices` here: argparse on Python 3.11 to 3.13 rejects an empty `*` list against them.
    pulling.add_argument("sources", nargs="*", metavar="source", help=f"default: all of {', '.join(SOURCES)}")
    checking = commands.add_parser("verify", help="fetch event pages and record them as sources")
    checking.add_argument("--pass", dest="pass_name", required=True, choices=run.PASSES)
    checking.add_argument("--chars", type=int, default=1500, help="page text to print, default 1500")
    checking.add_argument("urls", nargs="+")
    noting = commands.add_parser("record", help="stamp pages read another way, such as WebFetch")
    noting.add_argument("--pass", dest="pass_name", required=True, choices=run.PASSES)
    noting.add_argument("--failed", metavar="REASON", help="record a failed read with this reason")
    noting.add_argument("urls", nargs="+")
    args = parser.parse_args()
    unknown = [name for name in getattr(args, "sources", []) if name not in SOURCES]
    if unknown:
        parser.error(f"unknown source {', '.join(unknown)}. Choose from {', '.join(SOURCES)}")
    try:
        batch = json.loads(args.input.read_text(encoding="utf-8"))
        state.timestamp(batch["started_at"])
        folder = args.input.parent / "fetch"
        if args.command == "pull":
            names = args.sources or list(SOURCES)
            print(json.dumps(pull(batch, state.load(args.db), names, folder), ensure_ascii=False, indent=1))
        elif args.command == "record":
            for item in record(args.pass_name, args.urls, folder, args.failed):
                print(json.dumps(item, ensure_ascii=False))
        else:
            for item in verify(args.pass_name, args.urls, folder, chars=args.chars):
                print(json.dumps(item, ensure_ascii=False))
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
