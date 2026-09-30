#!/usr/bin/env python3
"""Local swipe app for the kids-activities database. Stdlib only, no network use.

Serves a phone-sized browser UI for putting each event into one of three
categories and for reviewing the result. All state changes go through
[scripts/swipe.py](../scripts/swipe.py), so validation, atomic writes, the file
lock and the preservation rules are identical to the command line.

    python3 app/server.py                       # http://127.0.0.1:8765
    python3 app/server.py --port 9000
    python3 app/server.py --db /tmp/sandbox/db.json --no-browser

Stop it with Ctrl+C or with the power button in the app header. Every swipe is
written to the database as it happens, so stopping mid-deck loses nothing.
"""

import argparse
import json
import mimetypes
import socket
import sys
import threading
import webbrowser
from functools import partial
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

APP_DIR = Path(__file__).resolve().parent
REPO = APP_DIR.parent
sys.path.insert(0, str(REPO / "scripts"))

import render  # noqa: E402
import state  # noqa: E402
import swipe  # noqa: E402

STATIC_DIR = APP_DIR / "static"
STATIC_FILES = {"/": "index.html", "/index.html": "index.html",
                "/app.css": "app.css", "/app.js": "app.js", "/mode.js": "mode.js",
                "/days.js": "days.js"}
MAX_BODY = 64 * 1024
LOOPBACK = {"localhost", "127.0.0.1", "::1", "[::1]"}


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


# --- request handling -------------------------------------------------------

class SwipeError(Exception):
    """A request the client got wrong. Carries the HTTP status to answer with."""

    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


class Handler(BaseHTTPRequestHandler):
    server_version = "KidsActivitiesSwipe/1.0"
    protocol_version = "HTTP/1.1"

    def __init__(self, *args, app=None, **kwargs):
        self.app = app
        super().__init__(*args, **kwargs)

    # Quiet by default: the useful log for a local app is what changed, which
    # the mutating handlers print themselves.
    def log_message(self, format, *args):
        if self.app.verbose:
            super().log_message(format, *args)

    def log_error(self, format, *args):
        super().log_message(format, *args)

    def send_json(self, status, body):
        content = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        if int(status) >= 400:
            # A refused request may still have an unread body. Closing the
            # connection keeps those bytes from being parsed as a new request.
            self.close_connection = True
            self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        route = urlsplit(self.path).path
        try:
            if route == "/api/state":
                self.send_json(HTTPStatus.OK, {"ok": True, "state": self.app.read()})
                return
            if route in STATIC_FILES:
                self.send_static(STATIC_FILES[route])
                return
            raise SwipeError(HTTPStatus.NOT_FOUND, f"Unknown path {route}")
        except SwipeError as error:
            self.send_json(error.status, {"ok": False, "error": str(error)})
        except (OSError, ValueError) as error:
            self.send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False, "error": str(error)})

    def do_POST(self):
        route = urlsplit(self.path).path
        try:
            self.check_origin()
            body = self.read_json()
            if route == "/api/decide":
                self.send_json(HTTPStatus.OK, self.app.decide(
                    self.field(body, "event_id"), self.field(body, "category")))
            elif route == "/api/clear":
                self.send_json(HTTPStatus.OK, self.app.clear(self.field(body, "event_id")))
            elif route == "/api/undo":
                self.send_json(HTTPStatus.OK, self.app.undo())
            elif route == "/api/quit":
                self.send_json(HTTPStatus.OK, {"ok": True, "message": "Zaustavljam."})
                self.app.stop()
            else:
                raise SwipeError(HTTPStatus.NOT_FOUND, f"Unknown path {route}")
        except SwipeError as error:
            self.send_json(error.status, {"ok": False, "error": str(error)})
        except (OSError, ValueError) as error:
            self.send_json(HTTPStatus.CONFLICT, {"ok": False, "error": str(error)})

    def check_origin(self):
        """Refuse cross-site writes. A same-origin browser fetch always passes."""
        origin = self.headers.get("Origin")
        if not origin:
            return
        host = (urlsplit(origin).hostname or "").lower()
        if host in LOOPBACK or origin.lower() == f"http://{(self.headers.get('Host') or '').lower()}":
            return
        raise SwipeError(HTTPStatus.FORBIDDEN, f"Cross-origin request from {origin} refused")

    def read_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            raise SwipeError(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "Request body too large")
        if not length:
            return {}
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise SwipeError(HTTPStatus.BAD_REQUEST, f"Invalid JSON: {error}") from error
        if not isinstance(body, dict):
            raise SwipeError(HTTPStatus.BAD_REQUEST, "Request body must be a JSON object")
        return body

    @staticmethod
    def field(body, name):
        value = body.get(name)
        if not isinstance(value, str) or not value.strip():
            raise SwipeError(HTTPStatus.BAD_REQUEST, f"Missing {name}")
        return value.strip()

    def send_static(self, name):
        path = STATIC_DIR / name
        if not path.is_file():
            raise SwipeError(HTTPStatus.NOT_FOUND, f"Missing {name}")
        content = path.read_bytes()
        kind = mimetypes.guess_type(name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{kind}; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)


class App:
    """Decision operations over one database, serialized for concurrent requests."""

    def __init__(self, db_path, verbose=False):
        self.db_path = str(db_path)
        self.verbose = verbose
        self.gate = threading.Lock()
        self.server = None

    def read(self):
        with self.gate:
            return payload(state.load(self.db_path))

    def event(self, db, event_id):
        event = swipe.by_id(db, event_id)
        if event is None:
            raise SwipeError(HTTPStatus.NOT_FOUND, f"No event row for {event_id}")
        return event

    def write(self, mutate):
        """One serialized load, mutate, save. The file lock also covers the CLI."""
        with self.gate, state.locked(self.db_path):
            db = state.load(self.db_path)
            message = mutate(db)
            if message is not None:
                state.save(self.db_path, db)
                print(message, flush=True)
            return {"ok": True, "message": message or "", "state": payload(db)}

    def decide(self, event_id, category):
        if category not in state.DECISIONS:
            raise SwipeError(HTTPStatus.BAD_REQUEST, f"Unknown category {category}")

        def mutate(db):
            event = self.event(db, event_id)
            changed, before = swipe.set_decision(db, event, category)
            if not changed:
                return None
            moved = f" (was {swipe.LABELS[before]})" if before else ""
            return f"{swipe.LABELS[category]}{moved}: {swipe.describe(event)}"

        return self.write(mutate)

    def clear(self, event_id):
        def mutate(db):
            event = self.event(db, event_id)
            changed, before = swipe.clear_decision(db, event)
            if not changed:
                return None
            return f"Back in the deck (was {swipe.LABELS[before]}): {swipe.describe(event)}"

        return self.write(mutate)

    def undo(self):
        def mutate(db):
            row, event = swipe.undo(db)
            if row is None:
                return None
            restored = swipe.LABELS.get(row.get("before")) or "no decision"
            return f"Undone {row.get('action')} → {restored}: {swipe.describe(event)}"

        return self.write(mutate)

    def stop(self):
        print("Stopped from the app. Every decision is already saved.", flush=True)
        if self.server is not None:
            threading.Thread(target=self.server.shutdown, daemon=True).start()


def lan_address():
    """The address another device on the same network would use to reach here.

    Asks the routing table which local address a packet to an unroutable test
    network would leave from. A connected UDP socket sends nothing, so this
    needs no name server and reaches no host.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        try:
            probe.connect(("192.0.2.1", 9))  # TEST-NET-1, reserved and never routed
            return probe.getsockname()[0]
        except OSError:
            return None


def serve(db_path, host="127.0.0.1", port=8765, open_browser=True, verbose=False):
    state.load(db_path)  # fail before binding if the expected state is missing
    app = App(db_path, verbose=verbose)
    server = ThreadingHTTPServer((host, port), partial(Handler, app=app))
    app.server = server
    number = server.server_address[1]
    # A wildcard bind is not an address to open: name this machine instead.
    shown = "127.0.0.1" if host in {"0.0.0.0", "::", ""} else (f"[{host}]" if ":" in host else host)
    url = f"http://{shown}:{number}/"
    print(f"Kids activities swipe app on {url}")
    print(f"Database: {db_path}")
    if host not in LOOPBACK:
        address = lan_address()
        if address:
            print(f"From a phone on the same network: http://{address}:{number}/")
        print("Warning: reachable beyond this machine. Anyone who can reach this "
              "port can change your decisions.")
    if open_browser:
        threading.Thread(target=webbrowser.open, args=(url,), daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped. Every decision is already saved.")
    finally:
        server.server_close()
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--db", default=str(REPO / "db.json"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true",
                        help="do not try to open a browser window")
    parser.add_argument("--verbose", action="store_true", help="log every request")
    args = parser.parse_args()
    try:
        sys.exit(serve(args.db, args.host, args.port,
                       open_browser=not args.no_browser, verbose=args.verbose))
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
