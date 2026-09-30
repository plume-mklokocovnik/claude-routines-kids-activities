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

## Published version

[pages.yml](../.github/workflows/pages.yml) publishes the same app to GitHub
Pages on every change to `db.json` or `app/`, so it is reachable from anywhere
without running anything:

<https://plume-mklokocovnik.github.io/claude-routines-kids-activities/>

Pages serves files rather than processes, so that build has no Python and no
write access to the repository. It carries a baked snapshot of the database in
`state.json` and stages decisions in the browser instead. A banner counts what
is not yet in `db.json`, and **Shrani v GitHub** opens the GitHub editor with a
patch file prefilled. Committing it runs
[apply-decisions.yml](../.github/workflows/apply-decisions.yml), which applies
the patch with `swipe.py apply`, deletes it and republishes the site. When the
new snapshot lands, the browser sees the database already agrees and clears the
banner by itself.

The published page is current, not live. It never reads `db.json` itself: the
snapshot is rebuilt and redeployed whenever a change to `db.json` reaches
`main`, which takes about a minute. The local server reads the file on every
request.

Three things follow from that design, all deliberate:

- `db.json` stays the only record. The browser holds a staging area, and a
  decision is not saved until the workflow has written it.
- Undo on the published version reaches back through the decisions that are
  still unsaved. Once they are in the database, undo lives there, so use the
  local app or `swipe.py undo`.
- Saving needs write access to the repository, which is the only access control
  on this path. You are logged in as yourself in the GitHub editor, and the page
  itself holds no credential, so nothing in the published site can change the
  database. A batch too large for a link is copied to the clipboard to paste
  instead.

Pages has to be switched on once before the first deploy can work: in the
repository, Settings → Pages → Source → **GitHub Actions**. A workflow token is
not allowed to create the site, so the deploy step fails with
`Create Pages site failed: Resource not accessible by integration` until that
setting exists. Re-run the workflow afterwards and it publishes.

Note that a Pages site is public to the internet whatever the repository's
visibility, unless the owner is on GitHub Enterprise Cloud.

Build it locally to see exactly what gets deployed:

```bash
python3 app/build_static.py --out site
python3 -m http.server 8799 --directory site --bind 127.0.0.1
```

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

## Reviewing

**Pregled** has one list per category, **Zanima nas**, **Mogoče** and
**Zavrnjeno**, and a fourth, **Neodločeno**, with everything still in the deck.
Together they are the whole current state, read from the database each time the
app loads. There is no generated file to keep in step with it.

Tap an event, or its title, to open a dialog with everything known about it:
when and where, with a Maps link, the age, the full price text, the notes, the
source and its link, when it was first seen, its decision and when it was made,
and its ID. Close it with the ✕, by tapping outside it, with `Esc`, or with the
phone's back gesture, which closes the dialog instead of leaving the app. The
dialog only reads. To change a category, use the buttons on the row.

The deck's swipe cards do not open it. A tap and a drag start the same way, and
the card already shows the essentials.

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

A decision is user-owned data on the event row:

```json
{ "decision": "interested", "decided_at": "2026-09-30T11:26:32Z" }
```

The app never touches `user_rules`, `hidden_events` or event status.
Rejecting an event is not hiding it: it moves to the Zavrnjeno list and can be
changed from there. To take an event out of the app entirely, use the hide
command in the [root README](../README.md#preferences).

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
clock, so the app shows the same day, time and horizon as the sweep report. An
event whose source publishes no start time shows `?`, and full price text is
shown unshortened.

## Layout

| File | Purpose |
|---|---|
| `server.py` | Local HTTP server, JSON API and the card presenter |
| `build_static.py` | Bakes `db.json` into the Pages bundle |
| `static/index.html` | Markup and the card/row templates |
| `static/app.css` | Phone frame, card stack, direction gradients |
| `static/app.js` | Drag handling, keyboard, review lists, details dialog, both backends |
| `static/mode.js` | Which backend to use. The build overwrites it |

One page and one renderer serve both modes. `app.js` holds two backends behind
the same small interface: the local one is a round trip per decision, the
published one reads the baked snapshot and stages changes in the browser.
`mode.js` picks between them, so neither the markup nor the UI is duplicated.

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
python3 -m unittest discover -s tests -p test_build_static.py -v
```

All three are offline. The API test binds an ephemeral loopback port and uses a
temporary database. The browser behaviour of `app.js` has no automated test:
check a change against both modes by hand, with the server and with a locally
served bundle.
