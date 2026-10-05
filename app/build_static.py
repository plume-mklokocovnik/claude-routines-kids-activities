#!/usr/bin/env python3
"""Build the offline version of the swipe app for GitHub Pages.

GitHub Pages serves files, not processes, so there is no Python and no way to
write to the repository. The build therefore bakes the card payload into
`state.json`. The page stages decisions in the browser and hands a patch back
through GitHub, either by starting a workflow with a device token or through the
GitHub editor. [scripts/swipe.py](../scripts/swipe.py) applies it.
`db.json` stays the only record: the browser holds a staging area, never a
second source of truth.

    python3 app/build_static.py                     # writes ./site
    python3 app/build_static.py --out /tmp/site --repo owner/name

The repository is needed for the save link and otherwise comes from
`GITHUB_REPOSITORY`. Without it the bundle still builds and still swipes, but
the page can only copy a patch to the clipboard.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

APP_DIR = Path(__file__).resolve().parent
REPO = APP_DIR.parent
sys.path.insert(0, str(REPO / "scripts"))

import render  # noqa: E402
import state  # noqa: E402
import swipe  # noqa: E402

STATIC_DIR = APP_DIR / "static"
COPIED = ("index.html", "app.css", "app.js", "days.js", "filters.js", "snapshot.js", "dispatch.js",
          "askai.js", "manifest.webmanifest", "icon-192.png", "icon-512.png")
INBOX = "inbox/decisions.txt"
HIDE_INBOX = "inbox/hide"


# --- presentation -----------------------------------------------------------
# Display strings are built here from the stored sweep clock, never from the
# wall clock, so the app shows the same dates as the sweep report.

def notes(event):
    text = render.notes_text(event)
    return [part for part in text.split(", ") if part]


def stamp(value):
    """A stored UTC instant as local date and time, or empty when absent."""
    moment = render.parse_dt(value)
    return f"{moment:%d.%m.%Y %H:%M}" if moment else ""


def source_host(url):
    """The site a source link points at, so the modal can name where it leads."""
    if not state.valid_url(url):
        return ""
    host = urlsplit(url).hostname or ""
    return host[4:] if host.startswith("www.") else host


def card(event):
    start = render.parse_dt(event.get("start_time"))
    age = event.get("age_min")
    return {
        "event_id": event.get("event_id"),
        "title": event.get("title") or "?",
        "venue": event.get("venue") or "?",
        "city": event.get("city") or "",
        "category": event.get("category") or "?",
        "day": render.DAYS[start.weekday()] if start else "",
        "date": f"{start:%d.%m.%Y}" if start else "",
        "date_short": f"{start:%d.%m.}" if start else "?",
        "day_iso": start.strftime("%Y-%m-%d") if start else "",
        "date_long": render.si_date(start) if start else "Datum ni znan",
        "month": start.strftime("%Y-%m") if start else "",
        "month_long": (f"{render.MONTHS[start.month - 1].capitalize()} {start.year}"
                       if start else "Brez datuma"),
        "time": render.hour_text(event, start),
        "age": f"{age}+" if isinstance(age, int) else "?",
        "price": (event.get("price_text") or "").strip(),
        "is_free": event.get("is_free") is True,
        "notes": notes(event),
        "url": event.get("url") if state.valid_url(event.get("url")) else "",
        "source": source_host(event.get("url")),
        "maps": render.maps_link(event.get("venue"), event.get("city")),
        "status": event.get("status", "active"),
        "decision": event.get("decision"),
        "decided_at": stamp(event.get("decided_at")),
        "first_seen": stamp(event.get("first_seen")),
    }


def undo_preview(db):
    _, row = swipe.last_change(db)
    if row is None:
        return {"available": False}
    event = swipe.by_id(db, row.get("event_id"))
    target = row.get("after")
    return {
        "available": True,
        "action": row.get("action"),
        "title": (event or {}).get("title") or row.get("event_id"),
        "label": swipe.LABELS.get(target, "brez kategorije"),
        "restores": swipe.LABELS.get(row.get("before"), "brez kategorije"),
    }


def payload(db):
    clock = state.timestamp(db["system_state"]["1"]["last_run"])
    groups = swipe.decided(db)
    return {
        "clock": {
            "date": f"{clock:%d.%m.%Y}",
            "time": f"{clock:%H:%M}",
            "horizon": f"{state.add_months(clock, 3):%d.%m.%Y}",
        },
        "counts": swipe.counts(db),
        "deck": [card(event) for event in swipe.deck(db)],
        "groups": {name: [card(event) for event in rows] for name, rows in groups.items()},
        "undo": undo_preview(db),
        "labels": {**swipe.LABELS, "undecided": "Neodločeno"},
    }


# --- bundle -----------------------------------------------------------------

def snapshot(db):
    """One flat, chronological card list. The page derives the deck and the
    three groups from it, so a locally staged decision only moves a card.

    Ordered by the same parsed key as the swipe deck, not by the display strings,
    so events either side of a daylight-saving change keep their real order.
    """
    events = {}
    for event in swipe.deck(db):
        events[event["event_id"]] = event
    for rows in swipe.decided(db).values():
        for event in rows:
            events.setdefault(event["event_id"], event)
    cards = [card(event) for event in sorted(events.values(), key=swipe.sort_key)]
    base = payload(db)
    return {"clock": base["clock"], "labels": base["labels"], "cards": cards}


def git_commit(*paths):
    """Hash and committer date of the newest commit, optionally for given paths.

    Empty fields when git or the history is missing, so a build never fails on it.
    The date is the commit's own, not the wall clock.
    """
    command = ["git", "-C", str(REPO), "log", "-1", "--format=%H %cs"]
    if paths:
        command += ["--", *paths]
    try:
        out = subprocess.run(command, capture_output=True, text=True, timeout=15,
                             check=True).stdout.split()
    except (OSError, subprocess.SubprocessError):
        return {"sha": "", "date": ""}
    return {"sha": out[0], "date": out[1]} if len(out) == 2 else {"sha": "", "date": ""}


def build_info():
    """Which commit of the app and which commit of the data this bundle shows."""
    app = git_commit()
    if not app["sha"]:
        app["sha"] = os.environ.get("GITHUB_SHA", "")
    return {"app": app, "data": git_commit("db.json")}


def mode_script(repo, branch, inbox, hide_inbox=HIDE_INBOX, info=None):
    owner, _, name = (repo or "").partition("/")
    target = {"owner": owner, "repo": name, "branch": branch, "inbox": inbox,
              "hide_inbox": hide_inbox}
    empty = {"sha": "", "date": ""}
    info = {"app": empty, "data": empty, **(info or {})}
    # The build line comes first: the SWIPE_REPO assignment runs to the end of the file.
    return ("/* Generated by app/build_static.py. Do not edit. */\n"
            f"window.SWIPE_BUILD = {json.dumps(info, ensure_ascii=False)};\n"
            f"window.SWIPE_REPO = {json.dumps(target, ensure_ascii=False)};\n")


VERSIONED = ("app.css", "mode.js", "days.js", "filters.js", "snapshot.js", "dispatch.js", "askai.js",
             "app.js")


def version_assets(html, out):
    """Tie each script and the stylesheet to its content with a `?v=` suffix.

    Pages sends everything with `max-age=600`, so a browser can pair a fresh page
    with an older script, which then reaches for elements that no longer exist.
    A changed file gets a new URL, so the page can only ever load the scripts it
    was built with.
    """
    digest = hashlib.sha256()
    for name in VERSIONED:
        digest.update((out / name).read_bytes())
    tag = digest.hexdigest()[:10]
    for name in VERSIONED:
        html = html.replace(f'href="{name}"', f'href="{name}?v={tag}"')
        html = html.replace(f'src="{name}"', f'src="{name}?v={tag}"')
    return html


def build(db_path, out_dir, repo=None, branch="main", inbox=INBOX, hide_inbox=HIDE_INBOX,
          info=None):
    db = state.load(db_path)  # refuses to build a bundle from missing state
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name in COPIED:
        shutil.copyfile(STATIC_DIR / name, out / name)
    generated = {
        "mode.js": mode_script(repo, branch, inbox, hide_inbox,
                               build_info() if info is None else info),
        "state.json": state.json_text(snapshot(db)),
        # Pages would otherwise hand the bundle to Jekyll, which skips _ paths.
        ".nojekyll": "",
    }
    for name, content in generated.items():
        state.atomic_write(out / name, content)
        os.chmod(out / name, 0o644)  # atomic_write keeps a private temp mode
    page = out / "index.html"
    state.atomic_write(page, version_assets(page.read_text(encoding="utf-8"), out))
    os.chmod(page, 0o644)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--db", default=str(REPO / "db.json"))
    parser.add_argument("--out", default=str(REPO / "site"))
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""),
                        help="owner/name for the save link")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--inbox", default=INBOX)
    args = parser.parse_args()
    try:
        out = build(args.db, args.out, args.repo, args.branch, args.inbox)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")
    snap = json.loads((out / "state.json").read_text(encoding="utf-8"))
    print(f"Built {out} with {len(snap['cards'])} card(s)")
    if not args.repo:
        print("No --repo and no GITHUB_REPOSITORY: the save link is disabled.")


if __name__ == "__main__":
    main()
