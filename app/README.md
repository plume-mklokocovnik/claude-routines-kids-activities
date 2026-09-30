# Swipe App

A phone-sized browser app for sorting the discovered events into three
categories, and for reviewing the result afterwards.

```bash
python3 app/server.py
```

Run it from the repository root. It serves <http://127.0.0.1:8765/> and opens a
browser window. Nothing is installed, no package is needed and no request leaves
the machine. Stop it with Ctrl+C.

| Flag | Meaning |
|---|---|
| `--db PATH` | Use another database. Reports and run records stay beside it |
| `--port N` | Listen on another port. Default `8765` |
| `--host H` | Bind another address. Default `127.0.0.1`, which is this machine only |
| `--no-browser` | Do not try to open a browser window |
| `--verbose` | Log every request, not only the changes |

## On the phone

The card size is a phone viewport, but the server still runs on the computer
that holds the database. To reach it from the phone, bind every interface:

```bash
python3 app/server.py --host 0.0.0.0
```

It then prints the address to type into the phone browser:

```
Kids activities swipe app on http://127.0.0.1:8765/
From a phone on the same network: http://192.168.1.24:8765/
Warning: reachable beyond this machine. Anyone who can reach this port can change your decisions.
```

Both devices have to be on the same network, and the computer's firewall has to
allow the port. If the printed address does not answer, the computer has more
than one network interface and the phone is on the other one: use the address of
the interface the phone shares, from `ip addr` or `ifconfig`.

This opens the app to everyone on that network. There is no password, so treat
it as a home-network convenience, not something to run on shared Wi-Fi. The
default loopback bind is unreachable from other devices.

In the phone browser, "Add to Home Screen" gives a fullscreen launcher without
the browser bars.

## Deciding

| Gesture | Key | Category | Background |
|---|---|---|---|
| Swipe right | `→` | Zanima nas | green from the right edge |
| Swipe left | `←` | Zavrnjeno | red from the left edge |
| Swipe down | `↓` | Mogoče | blue from the bottom edge |
| — | `Z` | Undo the last change | — |

The gradient and the stamp on the card grow with the drag, so the direction is
visible before the card is released. A drag that stops short of the threshold
springs back and decides nothing. The three buttons below the card do the same
as the gestures, and the ↶ button undoes.

The deck holds the active, not hidden events that have no decision yet, earliest
first. A decided event leaves the deck and appears under **Pregled**, where its
category can be changed or cleared. Clearing returns it to the deck.

## Stopping and undoing

Every swipe is written to `db.json` before the next card appears, so the run can
be abandoned at any point: close the tab, press Ctrl+C, or use the ⏻ button in
the header, which stops the server from inside the app. Reopening continues with
the remaining cards.

Undo is not limited to the current session. Each change appends a row to the
`decision_log` table, and undo reverses the newest row that has not been undone
yet, restoring the previous category and its timestamp. Walking back through
several wrong swipes therefore works after a restart as well. Nothing is
deleted: an undone row stays as an audit trail, marked `undone`.

## What it writes, and what it leaves alone

Decisions are user-owned data on the event row, exactly like a star:

```json
{ "decision": "interested", "decided_at": "2026-09-30T11:26:32Z" }
```

The app never touches stars, `user_rules`, `hidden_events` or event status.
Rejecting an event is not hiding it: it stays in
[currently_active.md](../currently_active.md), which the app does not regenerate.
To remove an event from the calendar, use the hide command in the
[root README](../README.md#preferences).

All state changes go through [scripts/swipe.py](../scripts/swipe.py), so the
validation, the file lock and the atomic write are the same as on the command
line. The two can be used interchangeably:

```bash
python3 scripts/swipe.py stats
python3 scripts/swipe.py list --category interested
python3 scripts/swipe.py set <event_id> maybe
python3 scripts/swipe.py undo
```

Dates come from the sweep clock stored in the database, never from the wall
clock, so the app shows the same day, time and horizon as the calendar. An event
whose source publishes no start time shows `?`, and full price text is shown
unshortened.

## Layout

| File | Purpose |
|---|---|
| `server.py` | Local HTTP server, JSON API and the card presenter |
| `static/index.html` | Markup and the card/row templates |
| `static/app.css` | Phone frame, card stack, direction gradients |
| `static/app.js` | Drag handling, keyboard, review list, API calls |

The frame is 480 x 1040 CSS pixels, the viewport of a Samsung Galaxy S25 Ultra
(1440 x 3120 hardware pixels at a 3x device ratio). On a narrow screen the frame
drops away and the app fills the window, so the same page works when opened on
the phone itself.

## API

`GET /api/state` returns the deck, the three groups, the counts and what undo
would reverse. `POST /api/decide` takes `event_id` and `category`,
`POST /api/clear` takes `event_id`, `POST /api/undo` takes no arguments and
`POST /api/quit` stops the server. Every successful change answers with the full
new state, so the page never has to guess what the database now holds.

Writes from another site are refused, and the server binds to this machine only
unless `--host` says otherwise. It is a single-user local tool with no
authentication, so see the phone section above before exposing the port.

## Tests

```bash
python3 -m unittest discover -s tests -p test_app.py -v
python3 -m unittest discover -s tests -p test_swipe.py -v
```

Both are offline. The API test binds an ephemeral loopback port and uses a
temporary database.
