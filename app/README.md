# Swipe App

A phone-sized browser app for sorting the discovered events into three
categories, and for reviewing the result afterwards.

The app runs only as the published GitHub Pages site. There is no application
server. To try a change before it is deployed, build the bundle and serve the
files with Python's static file server:

```bash
python3 app/build_static.py --out site && python3 -m http.server 8799 --directory site --bind 127.0.0.1
```

## Published version

[pages.yml](../.github/workflows/pages.yml) publishes the app to GitHub Pages on
every change to `db.json` or `app/`, so it is reachable from anywhere without
running anything:

<https://plume-mklokocovnik.github.io/claude-routines-kids-activities/>

Pages serves files rather than processes, so the build has no Python and no
write access to the repository. It carries a baked snapshot of the database in
`state.json` and stages decisions in the browser instead. A banner counts what
is not yet in `db.json`, and **Shrani v GitHub** opens the GitHub editor with a
patch file prefilled. Committing it runs
[apply-decisions.yml](../.github/workflows/apply-decisions.yml), which applies
the patch with `swipe.py apply`, deletes it and republishes the site. When the
new snapshot lands, the browser sees the database already agrees and clears the
banner by itself. After you tap save the page looks for the new snapshot every
15 seconds for five minutes, and again whenever you come back to its tab, so the
banner clears without a reload.

Every fetch of `state.json` asks the server to revalidate it. Pages sends that
file with `max-age=600`, and a plain fetch obeys that: a reload just after a
deploy was answered from the browser's cache for up to ten minutes, so the banner
stayed even though the workflow had finished. Revalidating costs an empty 304
when nothing has changed.

The same ten minutes could pair a fresh page with an older script, which then
reached for an element that no longer exists. The build therefore adds a `?v=`
suffix, taken from the content of the scripts and stylesheet, to each of their
URLs in `index.html`. A changed file gets a new URL.

The published page is current, not live. It never reads `db.json` itself: the
snapshot is rebuilt and redeployed whenever a change to `db.json` reaches
`main`, which takes about a minute.

Three things follow from that design, all deliberate:

- `db.json` stays the only record. The browser holds a staging area, and a
  decision is not saved until the workflow has written it.
- Undo on the published version reaches back through the decisions that are
  still unsaved. Once they are in the database, undo lives there, so use
  `swipe.py undo`.
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

### Install on Android

The bundle carries a web app manifest (`display: standalone`) and two icons, so
Chrome treats the published page as an installable app. On the phone:

1. Delete any older home screen shortcut of the page. A shortcut made before the
   manifest existed stays a browser tab for good.
2. Open the published address in Chrome and reload it once.
3. Menu (⋮) → **Add to Home screen** → **Install**. The entry reads *Install
   app* when the page qualifies, and *Create shortcut* when it does not.

The installed app opens without the address bar or browser menu. If it still
shows browser bars, it is a shortcut, not an install. There is deliberately no
service worker, so the page always loads the latest snapshot and works online
only.

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

The top card also carries a faint glow along three edges, before any drag: green
on the right, red on the left and blue along the bottom. It is a thin, rounded
rim, a few pixels deep and fading inward like a sunset, and it brightens as the
card is pulled toward that edge. It tells you where each decision lives without
adding anything to read.

The swipe screen shows the current event and nothing else. There is no header,
no status line and no list of counts above the card. Each round button carries
its own count as a small number in its top right corner: rejected on the red ✕,
maybe on the blue ?, and interested on the green ♥. Under the buttons sit the
number of events still to decide and a thin progress bar. The other figures are
on **Pregled**.

The deck holds the active, not hidden events that have no decision yet, earliest
first. A decided event leaves the deck and appears under **Pregled**, where its
category can be changed or cleared. Clearing returns it to the deck.

## Hiding every rejected event

The **Zavrnjeno** list carries a round floating button with a crossed-out eye,
at the bottom right. It is absent from the other
lists and from an empty Zavrnjeno list.

Tapping it opens a confirmation in Slovenian, **Skrijem vse zavrnjene?**, with the
number of events in the list. It also counts any that are still unsaved, because
they are hidden too. **Prekliči** closes it. **Skrij vse** opens the GitHub editor
with a file named `inbox/hide/hide-<hash>.txt` prefilled with the ID of every
event in the list. The file name is a hash of its content, so the same list always
gets the same name and the page never reads the clock. A screen explains the one
click left, **Commit changes**, and the page then looks for the rebuilt snapshot
like it does after a save.

Committing the file runs [hide-events.yml](../.github/workflows/hide-events.yml).
It calls `hide_event.py apply`, which hides each event by its exact ID, as a single
event and never as a series or a show, with the reason `hidden from the app`.
Then it deletes the file, checks the database and republishes. If the push loses a
race with another run, it starts again from the fresh database instead of merging
text. See [inbox/](../inbox/README.md#hide-lists) for the file format.

A hidden event leaves every list and count, in all three categories, because
hiding takes an event out of the app. Its decision stays on the row and
`hide_event.py unhide <event_id>` returns it to the same category. If an
unsaved rejection is hidden before it is saved, the hide wins and the decision is
dropped, so an unhide later returns that event to the deck.

## Past events

The app does not show an event once its date, in Ljubljana, is before today. An
event from today stays whatever time it started, and one with no date is never
treated as past. This applies everywhere: the deck, the four lists and the
counts, which are worked out from what is left.

[days.js](static/days.js) reads the clock when the page is opened, and again when
you return to it on a later day, so an app left open overnight does not keep
showing yesterday. It uses Ljubljana's date whatever timezone the phone is set to,
including across the two daylight-saving changes. This is the one place the app
reads the clock, and it decides visibility only. Nothing is written, so a decision
on a past event stays in `db.json` and the event keeps its status. The published
page needs no rebuild for this, since the rule runs in the browser.

Things this does not do:

- **Multi-day events.** Only a start date is stored, so an event that runs for a
  week disappears after its first day. The end date is in the price text for the
  few that have one, such as `5.-9. 10.`
- **The command line.** `swipe.py stats` and `list` still count events from the
  past, because they answer about the database rather than about today.
- **The sweep.** It still marks an event expired at its start time. An event it
  has already marked expired stays out of the deck even when it is from today.

## Reviewing

**Pregled** has one list per category, **Zanima nas**, **Mogoče** and
**Zavrnjeno**, and a fourth, **Neodločeno**, with everything still in the deck.
Together they are the whole current state, read from the database each time the
app loads. There is no generated file to keep in step with it.

The top of the screen holds the four lists, and below them a block of figures
about the current state: when the last sweep ran, the date its window ends, today
in Ljubljana, how many events there are and how many are free. The last-run time
and the window end come from the run record in the database, not from the clock.

Tap an event, or its title, to open a dialog with everything known about it:
when and where, with a Maps link, the age, the full price text, the notes, the
source and its link, when it was first seen, its decision and when it was made,
and its ID. Close it with the ✕, by tapping outside it, with `Esc`, or with the
phone's back gesture, which closes the dialog instead of leaving the app. The
dialog only reads. To change a category, use the buttons on the row.

Tapping the card in the deck opens it too. A finger that lifts within half a
second having moved under 8 pixels is a tap, and anything else is a swipe. That
is also the way to read a title or price the card had to cut short.

The event ID, on the card and in the dialog, is a copy button. A touch anywhere on
the ID text or on the small copy icon beside it copies the ID, turns the icon into
a check mark for a moment and shows a short confirmation. It neither opens the
dialog nor decides anything, so the ID can be pasted into `swipe.py set`,
`hide_event.py` or a message without selecting text by hand.

## Asking an AI about an event

The dialog ends with **Vprašaj AI za več o dogodku** and one button each for
ChatGPT, Claude and Gemini. A tap sends the event to that assistant, which is
asked to search the web and confirm the date, price and venue. The text is
English and built by [askai.js](static/askai.js) from the stored fields only.
Anything unknown is left out rather than guessed.

There is no cross-vendor standard, so the route depends on the device:

- **Android.** An `intent:` link shares the text to the installed app and opens a
  new chat with it. If the app is missing, the link falls back to the web page.
- **Elsewhere.** The assistant's web page opens in a new tab. ChatGPT and Claude
  take the text in the address. Gemini has no prefill, so its page opens empty.

The text is always copied too, which is what makes Gemini a paste. The
`com.*` package names in `askai.js` are the part most likely to need a fix if an
app does not open.

## Small screens

There is no visible title and no header, so the card starts near the top and the
counts live on the buttons. The save banner is a single line, and the tab bar
keeps clear of the phone's gesture bar. On a tall screen the card stops growing
at 600 pixels and the card with its buttons is centred, which keeps the buttons
within reach. Spare height inside the card is split between the gap above the
title and the gap above the age and price, so a short event reads as three groups.

The card's own height decides what it can show. When it runs short it drops the
notes and the ID, then the links, in that order. The title, time, place, age and
price are never dropped, and everything a card sheds is in the dialog.

## Undoing

A swipe is staged in the browser until it is saved, so the page can be closed at
any point. Reopening continues with the remaining cards. The ↶ button and `Z`
undo staged decisions only.

Once a decision is in `db.json`, `swipe.py undo` reverses it. Each change appends
a row to the `decision_log` table, and undo reverses the newest row that has not
been undone yet, restoring the previous category and its timestamp. Nothing is
deleted: an undone row stays as an audit trail, marked `undone`.

## What it writes, and what it leaves alone

A decision is user-owned data on the event row:

```json
{ "decision": "interested", "decided_at": "2026-09-30T11:26:32Z" }
```

Swiping never touches `user_rules`, `hidden_events` or event status.
Rejecting an event is not hiding it: it moves to the Zavrnjeno list and can be
changed from there. To take an event out of the app entirely, use the hide
command in the [root README](../README.md#preferences), or the hide-all button
described above.

Saved decisions reach `db.json` through [scripts/swipe.py](../scripts/swipe.py)
`apply`, so the validation, the file lock and the atomic write are the same as on
the command line. The two can be used interchangeably:

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
| `build_static.py` | Card presenter. Bakes `db.json` into the Pages bundle |
| `static/index.html` | Markup and the card/row templates |
| `static/app.css` | Phone frame, card stack, direction gradients, edge glow |
| `static/app.js` | Drag handling, keyboard, review lists, details dialog, saving |
| `static/days.js` | Today's date in Ljubljana and the past-event rule |
| `static/snapshot.js` | The baked snapshot, staged decisions, the re-check and the hide list |
| `static/askai.js` | The prompt and the links that hand an event to an AI assistant |

The build also writes `mode.js` (the repository the save link points at) and
`state.json` into the bundle. Neither is kept in `static/`.

The frame is 480 x 1040 CSS pixels, the viewport of a Samsung Galaxy S25 Ultra
(1440 x 3120 hardware pixels at a 3x device ratio). On a narrow screen the frame
drops away and the app fills the window, so the same page works when opened on
the phone itself.

## Tests

```bash
python3 -m unittest discover -s tests -p test_app.py -v
python3 -m unittest discover -s tests -p test_swipe.py -v
python3 -m unittest discover -s tests -p test_build_static.py -v
python3 -m unittest discover -s tests -p test_days.py -v
python3 -m unittest discover -s tests -p test_snapshot.py -v
python3 -m unittest discover -s tests -p test_askai.py -v
```

All six are offline. `test_days.py`, `test_snapshot.py` and `test_askai.py` run the
real `days.js`, `snapshot.js` and `askai.js` under Node and skip themselves when Node is missing.
What the page draws, its layout and its gestures have no automated test: check a
change by hand in the locally served bundle, on a phone as well as a desktop
window.
