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
is not yet in `db.json`, and **Shrani v GitHub** hands them to GitHub. On a
device with a [token](#one-tap-saving) that is one tap: the page starts
[apply-decisions.yml](../.github/workflows/apply-decisions.yml) through the API
and passes the patch as its input. On a device without one it opens the GitHub
editor with a patch file prefilled, and committing that file starts the same
workflow. The workflow applies the patch with `swipe.py apply`, republishes the
site, and when the new snapshot lands the browser sees the database already
agrees and clears the banner by itself. After you tap save the page looks for the
new snapshot every 15 seconds for five minutes, and again whenever you come back
to its tab, so the banner clears without a reload.

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
- Saving needs either write access to the repository or a device token. In the
  GitHub editor you are logged in as yourself. With a token, the token is the
  access control, and the page holds nothing until you paste one in. Either way
  the page cannot change the database itself, only ask a workflow to. A batch too
  large for an editor link is copied to the clipboard to paste instead.

### One-tap saving

A device that holds a token saves without leaving the app. **Shrani v GitHub**
sends the patch to GitHub's Actions API, which starts the workflow. The button
turns into **Poslano** until the snapshot catches up. If GitHub turns the call
down, because the token is gone or the network is, the page says why and opens the
editor instead, so a save is never lost to a bad token.

Every device has its own token. Several can be in use at once, and each is revoked
on its own:

1. In the app, open the gear tab and scroll to **Hitro shranjevanje**. **Ustvari
   žeton** opens GitHub's token form with the name, the lifetime and the
   permission filled in. Rename the token after the device, such as `phone`, so the
   list on GitHub stays readable.
2. On that form choose **Only select repositories** and pick this repository.
   Check that the only repository permission is **Actions: Read and write**. GitHub
   adds read-only metadata by itself. The token cannot read or change the code.
3. Generate it, paste it into the field in the app and tap **Vklopi**. The page
   checks it with one read and keeps it only in that browser's storage.

To cut a device off, revoke its token at
<https://github.com/settings/personal-access-tokens>. The other devices carry on.
That device shows **Ne deluje** on its next save and uses the editor until you
paste a new token. **Odstrani z te naprave** only forgets the local copy. The
token stays valid on GitHub until you revoke it there. An expired token behaves
the same way, so a token with a one-year lifetime means one repaste a year.

What the token allows, and what stands in the way of misuse:

- It can start workflows and manage workflow runs, and nothing else. It cannot
  read or write files, change workflows or reach any other repository. A leaked
  one can send crafted decisions, which the `decision_log` makes reversible with
  `swipe.py undo`, or cancel and disable runs. Revoke it when a device is lost.
- Both workflows treat the patch as untrusted text. It arrives as an environment
  variable, never inside a shell command. [dispatch_input.py](../scripts/dispatch_input.py)
  keeps only lines in the exact `code:event_id` or single event ID format and
  refuses the whole run on anything else, before the database is touched.
- A content security policy in `index.html` lets the page load scripts only from
  itself and talk only to itself and `api.github.com`, so a stray script has
  nowhere to send a token. The page uses no inline script and writes no HTML from
  data.
- Browser storage is shared by every Pages site under the same account, because
  they share one address. A token pasted here is readable by any other site there
  that runs script, so keep that account's other sites to your own code.

Two behaviours come from GitHub, not from the page. Runs of one workflow queue
one at a time, and GitHub keeps only one waiting run. If two devices save while a
run is going, the older waiting run is dropped. Its decisions are still staged on
the device that sent them, the banner stays, and **Shrani v GitHub** returns after
the five minute window, so a dropped save is a second tap and not a loss. A push
that loses a race with a sweep is retried from the fresh database up to three
times.

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
on the gear tab, **Info in nastavitve**.

The deck holds the active, not hidden events that have no decision yet, earliest
first. A decided event leaves the deck and appears under **Pregled**, where its
category can be changed or cleared. Clearing returns it to the deck.

## Hiding every rejected event

The **Zavrnjeno** list carries a round floating button with a crossed-out eye,
at the bottom right. It is absent from the other
lists and from an empty Zavrnjeno list.

Tapping it opens a confirmation in Slovenian, **Skrijem vse zavrnjene?**, with the
number of events in the list. It also counts any that are still unsaved, because
they are hidden too. **Prekliči** closes it. **Skrij vse** hands the ID of every
event in the list to GitHub, the same two ways as a save. A device with a token
starts [hide-events.yml](../.github/workflows/hide-events.yml) directly. Otherwise
the GitHub editor opens with a file named `inbox/hide/hide-<hash>.txt` prefilled.
The file name is a hash of its content, so the same list always gets the same name
and the page never reads the clock. A screen explains the one click left,
**Commit changes**, and the page then looks for the rebuilt snapshot like it does
after a save.

Either route runs the same workflow.
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

Tap an event, or its title, to open a dialog with everything known about it:
when and where, with a Maps link, the age, the full price text, the notes, the
source and its link, when it was first seen, its decision and when it was made,
and its ID. Close it with the ✕, by tapping outside it, with `Esc`, or with the
phone's back gesture, which closes the dialog instead of leaving the app.

Rows are display-only. A tap anywhere on a row opens the dialog, and the title
is a real button for keyboard use. When the dialog was opened from a row it holds
an **Odločitev** group after the facts and notes: **Zanima**, **Mogoče**, **Zavrni**
and **V kup**, with the current category highlighted. **V kup** is absent for an
event that is still undecided. A tap moves the event, closes the dialog, shows a
toast such as *Premaknjeno v Mogoče* and puts focus on the row that took its
place. The dialog opened from a deck card has no such group, since the deck has
its own buttons and gestures. The old **Vir** button on the row is the dialog's
**Vir dogodka** link.

Tapping the card in the deck opens it too. A finger that lifts within half a
second having moved under 8 pixels is a tap, and anything else is a swipe. That
is also the way to read a title or price the card had to cut short.

The event ID, on the card and in the dialog, is a copy button. A touch anywhere on
the ID text or on the small copy icon beside it copies the ID, turns the icon into
a check mark for a moment and shows a short confirmation. It neither opens the
dialog nor decides anything, so the ID can be pasted into `swipe.py set`,
`hide_event.py` or a message without selecting text by hand.

### Filtering and bulk edit

Under the four tabs sits one row with a search field, **Filtri** and **Izberi**.
Matching is done by [filters.js](static/filters.js), which Node can test.

- **Search** looks in the title, venue, city, notes and event category. It ignores
  case and diacritics, so `cebelica` finds `čebelica`. `Esc` in the field clears it.
- **Filtri** opens a panel with **Datum od** and **Datum do**, the presets
  **Danes**, **Ta vikend** and **Naslednjih 7 dni**, a chip for each event category
  in the data and **Samo brezplačni**. The badge counts the active filters of the
  panel. The range is inclusive on the stored day, and an event with no date does
  not match while a date limit is set. An inverted range is swapped and says so.
  The presets use Ljubljana's today from `Days.today()` and ISO strings, never the
  device calendar.
- Active filters show as removable chips with a **Počisti filtre** button, and a
  live line such as *Prikazano 6 od 25* gives the numbers for the tab. When
  nothing matches, the list says so and offers the same button.
- Filters live in memory only, so a reload clears them. They survive switching
  tabs and views. The tab counters show matches while a filter is on, and the
  badges on the swipe buttons and the tab bar keep the true totals.
- **Izberi** puts a checkbox on every row, and a tap on a row toggles it. The bar
  at the bottom shows **Izbrano N**, **Izberi vse** (the rows shown after filters)
  or **Počisti izbiro**, the category buttons and **Končaj**. One tap stages all the
  decisions through the same store, with one write and one redraw, and shows
  *Premaknjeno: N*. The button for the tab's own category is left out, and **V kup**
  is left out on **Neodločeno**.
- Selection belongs to the tab. Changing tab clears it, a filter change drops rows
  that are no longer shown, and leaving Pregled or pressing `Esc` ends the mode.
- The hide-all button is hidden while selecting or filtering, because it hides
  every rejected event and not only the ones shown.

## Info and settings

The gear tab, the small one at the right of the tab bar, opens one scrolling page
with these sections:

- **Različica.** The short hash and date of the commit the page was built from,
  and of the newest commit that changed `db.json`. Each links to that commit on
  GitHub, so the commit list shows which version of the app and of the data this
  device is looking at. The build reads them from git history, so the Pages
  workflow checks out the full history. If the history is missing, the build still
  works and the page shows `?`.
- **Stanje podatkov.** When the last sweep ran, how old that is, the date its
  window ends, today in Ljubljana and how many decisions are not saved yet. The
  last-run time and the window end come from the run record in the database, not
  from the clock.
- **Dogodki.** How many events there are, how many are free, how many fall in the
  next seven days and on this weekend, the share already decided and the first
  dated event.
- **Po mesecih**, **Po kategorijah** and **Najpogostejši viri.** Bars of how the
  events are spread. Categories show the six largest and group the rest as
  **Ostalo**. Sources show the five most common hosts.
- **Hitro shranjevanje.** This device's [token](#one-tap-saving). Where the build
  does not know the repository, a note says so instead.

Every figure is worked out in the browser from the events already loaded, so it
follows the same past-event rule as the lists. Weekdays and day counts are read
from the stored dates and never from the device's timezone.

## Asking an AI about an event

The dialog ends with **Vprašaj AI za več o dogodku** and one button each for
ChatGPT and Claude. A tap sends the event to that assistant, which is asked to
search the web and confirm the date, price and venue. The text is English and
built by [askai.js](static/askai.js) from the stored fields only. Anything unknown
is left out rather than guessed.

There is no cross-vendor standard, so the route depends on the device:

- **Android.** An `intent:` link views the assistant's own web address in its
  installed app. If the app is missing, the link falls back to the web page. It is
  a VIEW and not a share (`SEND`) on purpose: Chrome adds the `BROWSABLE` category
  to every intent a page launches, the share screens of these apps do not declare
  it, so a share never resolved and the installed web app showed the fallback page
  in its in-app browser instead.
- **Elsewhere.** The assistant's web page opens in a new tab with the text in the
  address.

The text is always copied too, for an app that opens without it. The `com.*`
package names in `askai.js` are the part most likely to need a fix if an app does
not open.

Gemini and a system share button were tried and removed. Gemini has no documented
prefill, and the share sheet was not needed once the two links opened their apps.

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

To drop all of them at once, use the **✕** at the right of the unsaved banner.
The first tap turns it into **Zavrži?** and the second, within a few seconds,
discards every unsaved decision and returns the cards to where the last snapshot
has them. Nothing already in `db.json` is touched. Once a save has been sent, the
button is disabled until the five minute window ends, because the workflow will
write those decisions whatever the page does.

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
| `static/app.js` | Drag handling, keyboard, review lists, filter bar, selection, details dialog, saving |
| `static/days.js` | Today's date in Ljubljana and the past-event rule |
| `static/filters.js` | Search, date range, categories and presets for the review lists |
| `static/snapshot.js` | The baked snapshot, staged decisions, the re-check and the hide list |
| `static/dispatch.js` | This device's token and the call that starts a save workflow |
| `static/askai.js` | The prompt and the links that hand an event to an AI assistant |

The build also writes `mode.js` (the repository the save link points at and the
commits the bundle was built from) and `state.json` into the bundle. Neither is kept in `static/`.

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
python3 -m unittest discover -s tests -p test_filters.py -v
python3 -m unittest discover -s tests -p test_snapshot.py -v
python3 -m unittest discover -s tests -p test_dispatch.py -v
python3 -m unittest discover -s tests -p test_dispatch_input.py -v
python3 -m unittest discover -s tests -p test_askai.py -v
```

All nine are offline. `test_days.py`, `test_filters.py`, `test_snapshot.py`,
`test_dispatch.py` and `test_askai.py` run the real `days.js`, `filters.js`,
`snapshot.js`, `dispatch.js` and `askai.js` under Node and skip themselves when Node is missing.
What the page draws, its layout and its gestures have no automated test: check a
change by hand in the locally served bundle, on a phone as well as a desktop
window.
