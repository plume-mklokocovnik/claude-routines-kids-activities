# Inbox

Decisions taken in the [published app](../app/README.md) land here as a patch
file, because GitHub Pages cannot write to a repository. Committing a `.txt`
file into this folder runs
[apply-decisions.yml](../.github/workflows/apply-decisions.yml), which folds the
decisions into [db.json](../db.json) with
[scripts/swipe.py](../scripts/swipe.py), deletes the patch and republishes the
site. The folder is normally empty.

One decision per line. The code is `i` for interested, `m` for maybe, `r` for
rejected and `c` for cleared back into the deck. Blank lines and `#` comments
are ignored.

```
# kids-activities decisions
i:event_20260928_1700_4d79d389347a
m:event_20260928_2000_4c3eb5b6c9ed
r:grad_20261014_1730
c:pumptrackgrosuplje_20261010_0000
```

Each line names the wanted end state, not a change, so applying the same patch
twice does nothing the second time. An event ID that is not in the database is
reported and skipped. Nothing is invented to match it.

The same file can be applied by hand:

```bash
python3 scripts/swipe.py apply inbox/decisions.txt
```

## Hide lists

The `inbox/hide/` folder takes a different kind of file. The published app's
floating eye button, on its Zavrnjeno list, hands over the ID of every rejected
event. Committing that `.txt` file runs
[hide-events.yml](../.github/workflows/hide-events.yml), which hides each event
with [scripts/hide_event.py](../scripts/hide_event.py), deletes the file and
republishes the site. Like this folder, it is normally empty.

One exact event ID per line. Blank lines and `#` comments are ignored:

```
# kids-activities hide
grad_20261014_1730
pumptrackgrosuplje_20261010_0000
```

Every ID is hidden as a single event, never as a series or a venue, with the
reason `hidden from the app`. An ID already hidden is left alone and one that is
not in the database is reported and skipped. The decision stays on the event row,
so `hide_event.py unhide <event_id>` puts it back in Zavrnjeno.

```bash
python3 scripts/hide_event.py apply inbox/hide/hide-1a2b3c4d.txt
```
