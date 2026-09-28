"""Shared state, calendar and persistence helpers. Python 3.11+, standard library only."""

import calendar
import hashlib
import json
import os
import tempfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

import fcntl

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db.json"
TZ = ZoneInfo("Europe/Ljubljana")
CATEGORIES = {
    "lutke", "pravljice", "kino", "delavnica", "sport", "tek", "kolo",
    "ples", "koncert", "odprta_vrata", "zoo", "festival", "pop_up", "avto_moto",
}


def timestamp(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.utcoffset() is not None:
            return parsed.astimezone(TZ)
    except (AttributeError, TypeError, ValueError):
        pass
    raise ValueError(f"Expected an ISO timestamp with timezone, got {value!r}")


def add_months(value, months=3):
    index = value.month - 1 + months
    year = value.year + index // 12
    month = index % 12 + 1
    return value.replace(year=year, month=month,
                         day=min(value.day, calendar.monthrange(year, month)[1]))


def valid_url(value):
    if not isinstance(value, str) or any(char.isspace() for char in value):
        return False
    try:
        parsed = urlsplit(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.hostname)
    except ValueError:
        return False


def validate_event(event):
    if not isinstance(event, dict):
        raise ValueError("Each event must be an object")
    for field in ("event_id", "title", "venue", "city", "category", "url"):
        if not isinstance(event.get(field), str) or not event[field].strip():
            raise ValueError(f"Event requires a nonempty {field}")
    timestamp(event.get("start_time"))
    if event["category"] not in CATEGORIES or not valid_url(event["url"]):
        raise ValueError(f"Invalid category or URL for {event['event_id']}")
    if not isinstance(event.get("flags"), list) or not all(isinstance(flag, str) for flag in event["flags"]):
        raise ValueError("flags must be a list of strings")
    age = event.get("age_min")
    if age is not None and (type(age) is not int or age < 0):
        raise ValueError("age_min must be a nonnegative integer or null")
    if event.get("is_free") is not None and type(event["is_free"]) is not bool:
        raise ValueError("is_free must be true, false or null")
    if not isinstance(event.get("price_text", ""), str):
        raise ValueError("price_text must be a string")
    if "starred" in event and type(event["starred"]) is not bool:
        raise ValueError("starred must be a boolean")
    if event.get("status", "active") not in {"active", "expired", "hidden"}:
        raise ValueError("Unknown event status")


def validate(db):
    if not isinstance(db, dict):
        raise ValueError("Database must be an object")
    for table in ("events", "user_rules", "hidden_events", "system_state"):
        if not isinstance(db.get(table), dict):
            raise ValueError(f"Database requires the {table} table")
    timestamp(db["system_state"].get("1", {}).get("last_run"))
    identifiers = set()
    for event in db["events"].values():
        validate_event(event)
        if event["event_id"] in identifiers:
            raise ValueError(f"Duplicate event_id: {event['event_id']}")
        identifiers.add(event["event_id"])
    for rule in db["user_rules"].values():
        if not isinstance(rule, dict):
            raise ValueError("User rule rows must be objects")
        for field in ("exclude_event_ids", "exclude_venues", "exclude_keywords", "exclude_categories", "force_include_urls"):
            values = rule.get(field, [])
            if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
                raise ValueError(f"{field} must be a list of strings")
    if any(not isinstance(item, dict) for item in db["hidden_events"].values()):
        raise ValueError("Hidden event rows must be objects")


def load(path=DB_PATH):
    with open(path, encoding="utf-8") as handle:
        db = json.load(handle)
    validate(db)
    return db


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def atomic_write(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def locked(path=DB_PATH):
    lock_path = Path(path).with_name(f".{Path(path).name}.lock")
    with lock_path.open("a") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError("Another process is updating this database") from error
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def next_key(table):
    return str(max((int(key) for key in table if str(key).isdigit()), default=0) + 1)


def hidden_reason(db, event):
    for rules in db.get("user_rules", {}).values():
        for field, value, substring in (
            ("exclude_event_ids", event.get("event_id", ""), False),
            ("exclude_venues", event.get("venue", ""), False),
            ("exclude_keywords", event.get("title", ""), True),
            ("exclude_categories", event.get("category", ""), False),
        ):
            for pattern in rules.get(field, []):
                if (pattern.casefold() in value.casefold() if substring else pattern.casefold() == value.casefold()):
                    return f"{field}: {pattern}"
    for item in db.get("hidden_events", {}).values():
        if not item.get("active", True) or item.get("scope", "event") != "event":
            continue
        if item.get("event_id") == event.get("event_id"):
            return f"hidden event: {item.get('event_id')}"
        try:
            same_time = timestamp(item.get("start_time")) == timestamp(event.get("start_time"))
        except ValueError:
            continue
        if same_time and all(str(item.get(field, "")).strip().casefold()
                             == str(event.get(field, "")).strip().casefold() for field in ("title", "venue")):
            return f"hidden occurrence: {item.get('event_id')}"
    return None


def expired(event, clock):
    start = timestamp(event["start_time"])
    if "time_unknown" in event.get("flags", []):
        return start.date() < clock.date()
    return start < clock


def active_events(db):
    return [event for event in db.get("events", {}).values()
            if event.get("status", "active") == "active" and not hidden_reason(db, event)]


def save(path, db):
    db["system_state"]["1"]["total_active_events"] = len(active_events(db))
    validate(db)
    atomic_write(path, json_text(db))


def find(db, query):
    events = [(key, event) for key, event in db["events"].items()
              if event.get("status", "active") == "active" and not hidden_reason(db, event)]
    lowered = query.strip().casefold()
    if not lowered:
        return []
    exact = [(key, event) for key, event in events if event["event_id"].casefold() == lowered]
    return exact or [(key, event) for key, event in events
                     if any(lowered in event.get(field, "").casefold()
                            for field in ("event_id", "title", "venue"))]