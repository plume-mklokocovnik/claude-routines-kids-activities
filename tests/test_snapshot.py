"""The published app's data source, run through Node against the real snapshot.js.

These cover the save round trip: decisions staged in the browser, written to the
database through GitHub, and cleared from the banner once the rebuilt snapshot
shows them. Skipped when Node is not installed.
"""

import unittest

import node_runner
from node_runner import NODE

PRELUDE = node_runner.require("snapshot.js") + """
const card = (id, decision) => ({ event_id: id, title: 'T ' + id, status: 'active',
                                  decision: decision || null, day_iso: '2026-10-05' });
const snapshot = (cards) => JSON.stringify({
  clock: { date: '28.09.2026', time: '15:10', horizon: '28.12.2026' },
  labels: { interested: 'Zanima nas', maybe: 'Mogoče', rejected: 'Zavrnjeno', undecided: 'Neodločeno' },
  cards });
const memory = (initial) => {
  const data = new Map(initial === undefined ? [] : [[Snapshot.KEY, initial]]);
  return { getItem: (key) => (data.has(key) ? data.get(key) : null),
           setItem: (key, value) => { data.set(key, value); } };
};
// A stand-in for GitHub Pages: the file it serves can change between calls.
const pages = (text) => {
  const server = { text, ok: true, status: 200, calls: [] };
  server.fetch = async (url, options) => {
    server.calls.push({ url, cache: options && options.cache });
    return { ok: server.ok, status: server.status, text: async () => server.text };
  };
  return server;
};
const make = (storage, server, notes) => Snapshot.createStaticStore({
  fetch: (...args) => server.fetch(...args), storage,
  notify: (text, bad) => (notes || []).push([text, bad]) });
const stored = (storage) => JSON.parse(storage.getItem(Snapshot.KEY) || '[]');
const ids = (rows) => rows.map((row) => row.event_id);
"""


def evaluate(body):
    return node_runner.run(PRELUDE + body)


@unittest.skipUnless(NODE, "node is not installed")
class SnapshotTests(unittest.TestCase):
    def test_every_load_asks_the_server_to_revalidate(self):
        # Pages serves state.json with max-age=600. Without `no-cache`, a reload
        # right after a deploy was answered from the browser's cache for up to ten
        # minutes, which is how the banner outlived the workflow that cleared it.
        got = evaluate("""
          const server = pages(snapshot([card('a')]));
          const store = make(memory(), server);
          await store.load();
          await store.poll();
          return server.calls;""")
        self.assertEqual(got, [{"url": "state.json", "cache": "no-cache"}] * 2)

    def test_staged_decisions_move_cards_and_write_the_patch(self):
        got = evaluate("""
          const store = make(memory(), pages(snapshot([card('a'), card('b'), card('c')])));
          await store.load();
          await store.decide('a', 'interested');
          await store.decide('b', 'rejected');
          const state = await store.decide('b', 'maybe');   // the last choice wins
          return { deck: ids(state.deck), interested: ids(state.groups.interested),
                   maybe: ids(state.groups.maybe), rejected: ids(state.groups.rejected),
                   unsaved: state.groups.interested[0].unsaved, counts: state.counts,
                   pending: store.pending() };""")
        self.assertEqual(got["deck"], ["c"])
        self.assertEqual((got["interested"], got["maybe"], got["rejected"]), (["a"], ["b"], []))
        self.assertTrue(got["unsaved"])
        self.assertEqual(got["counts"], {"interested": 1, "maybe": 1, "rejected": 0,
                                         "undecided": 1, "decided": 2, "total": 3})
        self.assertEqual(got["pending"], {"count": 2, "patch": "# kids-activities decisions\ni:a\nm:b\n"})

    def test_decide_many_stages_each_event_and_writes_storage_once(self):
        got = evaluate("""
          const storage = memory();
          let writes = 0;
          const counting = { getItem: storage.getItem, setItem: (k, v) => { writes += 1; storage.setItem(k, v); } };
          const store = make(counting, pages(snapshot([card('a'), card('b', 'rejected'), card('c'), card('d')])));
          await store.load();
          const before = writes;
          const state = await store.decideMany(['a', 'b', 'c', 'a'], 'maybe');
          const written = writes - before;
          const undone = await store.undo();
          const cleared = await store.decideMany(['a', 'b'], '');
          return { maybe: ids(state.groups.maybe), deck: ids(state.deck), written,
                   pending: store.pending(), afterUndo: ids(undone.groups.maybe),
                   deckAfterClear: ids(cleared.deck) };""")
        self.assertEqual(got["maybe"], ["a", "b", "c"])
        self.assertEqual(got["deck"], ["d"])
        self.assertEqual(got["written"], 1)
        # One row per event, so undo steps back one event at a time.
        self.assertEqual(got["afterUndo"], ["a", "b"])
        # Cleared events return to the deck, including one the database had rejected.
        self.assertEqual(got["deckAfterClear"], ["a", "b", "c", "d"])
        self.assertEqual(got["pending"]["count"], 2)

    def test_decide_many_skips_events_already_in_the_target(self):
        got = evaluate("""
          const store = make(memory(), pages(snapshot([card('a', 'maybe'), card('b')])));
          await store.load();
          await store.decideMany(['a'], 'maybe');
          return store.pending();""")
        self.assertEqual(got["count"], 0)

    def test_saving_and_reloading_clears_the_banner(self):
        # The reported case: three decisions, committed, workflow ran, page reloaded.
        got = evaluate("""
          const storage = memory();
          const server = pages(snapshot([card('a'), card('b'), card('c')]));
          let store = make(storage, server);
          await store.load();
          await store.decide('a', 'maybe');
          await store.decide('b', 'rejected');
          await store.decide('c', 'rejected');
          const before = store.pending().count;
          // Commit, the apply workflow and the deploy: the snapshot now has them.
          server.text = snapshot([card('a', 'maybe'), card('b', 'rejected'), card('c', 'rejected')]);
          store = make(storage, server);                      // a page reload
          const state = await store.load();
          return { before, after: store.pending().count, stored: stored(storage),
                   counts: state.counts,
                   anyUnsaved: [...state.groups.maybe, ...state.groups.rejected].some((c) => c.unsaved) };""")
        self.assertEqual(got["before"], 3)
        self.assertEqual(got["after"], 0)
        self.assertEqual(got["stored"], [])
        self.assertEqual((got["counts"]["maybe"], got["counts"]["rejected"]), (1, 2))
        self.assertFalse(got["anyUnsaved"])

    def test_polling_picks_up_the_rebuilt_snapshot_without_a_reload(self):
        got = evaluate("""
          const storage = memory();
          const server = pages(snapshot([card('a'), card('b')]));
          const store = make(storage, server);
          await store.load();
          await store.decide('a', 'maybe');
          const whileWaiting = await store.poll();           // the same file again
          const pendingWhileWaiting = store.pending().count;
          server.text = snapshot([card('a', 'maybe'), card('b')]);
          const rebuilt = await store.poll();
          return { whileWaiting, pendingWhileWaiting, maybe: rebuilt && rebuilt.counts.maybe,
                   pendingAfter: store.pending().count, stored: stored(storage) };""")
        self.assertIsNone(got["whileWaiting"])  # nothing new, so the page does not redraw
        self.assertEqual(got["pendingWhileWaiting"], 1)
        self.assertEqual(got["maybe"], 1)
        self.assertEqual(got["pendingAfter"], 0)
        self.assertEqual(got["stored"], [])

    def test_only_what_the_database_agrees_with_stops_being_pending(self):
        got = evaluate("""
          const storage = memory();
          const server = pages(snapshot([card('a'), card('b'), card('c')]));
          let store = make(storage, server);
          await store.load();
          await store.decide('a', 'maybe');
          await store.decide('b', 'rejected');
          await store.decide('c', 'interested');
          // a agrees, b was decided differently meanwhile, c is no longer listed.
          server.text = snapshot([card('a', 'maybe'), card('b', 'maybe')]);
          store = make(storage, server);
          await store.load();
          return store.pending();""")
        self.assertEqual(got, {"count": 1, "patch": "# kids-activities decisions\nr:b\n"})

    def test_clearing_undoing_and_repeating_are_safe(self):
        got = evaluate("""
          const store = make(memory(), pages(snapshot([card('a', 'interested'), card('b')])));
          await store.load();
          const steps = [];
          await store.decide('a', 'interested');             // already so: nothing to stage
          steps.push(store.pending().patch);
          await store.clear('a');
          steps.push(store.pending().patch);
          await store.decide('b', 'maybe');
          steps.push(store.pending().patch);
          await store.undo();
          steps.push(store.pending().patch);
          await store.undo();
          steps.push(store.pending().count);
          await store.undo();                                // empty: still fine
          steps.push(store.pending().count);
          return steps;""")
        head = "# kids-activities decisions\n"
        self.assertEqual(got, [head, head + "c:a\n", head + "c:a\nm:b\n", head + "c:a\n", 0, 0])

    def test_discarding_drops_every_unsaved_decision_and_only_those(self):
        got = evaluate("""
          const storage = memory();
          const server = pages(snapshot([card('a', 'interested'), card('b'), card('c', 'maybe')]));
          let store = make(storage, server);
          await store.load();
          await store.decide('b', 'rejected');       // staged on a card in the deck
          await store.decide('c', 'rejected');       // staged over a saved decision
          await store.clear('a');                    // staged clearing of a saved decision
          const before = store.pending().count;
          const state = await store.discard();
          store = make(storage, server);             // a reload must not bring them back
          const reloaded = await store.load();
          return { before, pending: store.pending(), stored: stored(storage),
                   deck: ids(state.deck), interested: ids(state.groups.interested),
                   maybe: ids(state.groups.maybe), rejected: ids(state.groups.rejected),
                   unsaved: [].concat(...Object.values(state.groups)).some((row) => row.unsaved),
                   reloadedDeck: ids(reloaded.deck), undo: state.undo.available };""")
        self.assertEqual(got["before"], 3)
        self.assertEqual(got["pending"], {"count": 0, "patch": "# kids-activities decisions\n"})
        self.assertEqual(got["stored"], [])
        self.assertEqual((got["interested"], got["maybe"], got["rejected"]), (["a"], ["c"], []))
        self.assertEqual((got["deck"], got["reloadedDeck"]), (["b"], ["b"]))
        self.assertFalse(got["unsaved"])
        self.assertFalse(got["undo"])

    def test_discarding_with_nothing_staged_changes_nothing(self):
        got = evaluate("""
          const store = make(memory(), pages(snapshot([card('a'), card('b', 'maybe')])));
          await store.load();
          const state = await store.discard();
          return { counts: state.counts, pending: store.pending().count };""")
        self.assertEqual(got["pending"], 0)
        self.assertEqual(got["counts"], {"interested": 0, "maybe": 1, "rejected": 0,
                                         "undecided": 1, "decided": 1, "total": 2})

    def test_tampered_or_broken_storage_is_ignored(self):
        got = evaluate("""
          const cases = ['{not json', '"text"', '{}',
                         '[{"event_id":"a","action":"set","after":"bogus"}]',
                         '[{"event_id":1,"action":"set","after":"maybe"}]',
                         '[{"event_id":"a","action":"set","before":null,"after":"maybe"}]'];
          const counts = [];
          for (const value of cases) {
            const store = make(memory(value), pages(snapshot([card('a')])));
            await store.load();
            counts.push(store.pending().count);
          }
          return counts;""")
        self.assertEqual(got, [0, 0, 0, 0, 0, 1])

    def test_without_storage_decisions_still_work_and_the_user_is_told(self):
        got = evaluate("""
          const notes = [];
          const store = make(null, pages(snapshot([card('a')])), notes);
          await store.load();
          await store.decide('a', 'maybe');
          return { pending: store.pending().count, told: notes.length > 0 && notes[0][1] === true };""")
        self.assertEqual(got, {"pending": 1, "told": True})

    def test_a_refused_write_does_not_lose_decisions_on_the_next_check(self):
        # If storage will not save, memory is the only copy. Polling must not
        # replace it with whatever storage last held.
        got = evaluate("""
          const notes = [];
          const refusing = { getItem: () => null, setItem: () => { throw new Error('quota'); } };
          const server = pages(snapshot([card('a'), card('b')]));
          const store = make(refusing, server, notes);
          await store.load();
          await store.decide('a', 'maybe');
          server.text = snapshot([card('a'), card('b'), card('c')]);   // an unrelated change
          const state = await store.poll();
          return { pending: store.pending().count, cards: state.counts.total, told: notes.length > 0 };""")
        self.assertEqual(got, {"pending": 1, "cards": 3, "told": True})

    def test_a_bad_response_leaves_the_working_snapshot_alone(self):
        got = evaluate("""
          const server = pages(snapshot([card('a')]));
          const store = make(memory(), server);
          await store.load();
          const failures = [];
          const attempt = async () => { try { await store.poll(); failures.push('no error'); }
                                        catch (error) { failures.push(error.message); } };
          server.ok = false; server.status = 503;
          await attempt();
          server.ok = true; server.text = '{oops';
          await attempt();
          server.text = JSON.stringify({ cards: 'nope' });
          await attempt();
          server.fetch = async () => { throw new TypeError('offline'); };
          await attempt();
          const state = await store.decide('a', 'maybe');    // the first snapshot still works
          return { failures, maybe: state.counts.maybe };""")
        self.assertEqual(got["failures"][0], "Posnetek baze ni dosegljiv (503).")
        self.assertNotEqual(got["failures"][1], "no error")
        self.assertEqual(got["failures"][2], "Posnetek baze ni veljaven.")
        self.assertEqual(got["failures"][3], "Posnetka baze ni bilo mogoče naložiti.")
        self.assertEqual(got["maybe"], 1)


@unittest.skipUnless(NODE, "node is not installed")
class HidePatchTests(unittest.TestCase):
    def test_one_exact_id_per_line_sorted_and_deduplicated(self):
        got = evaluate("return Snapshot.hidePatch(['b', 'a', 'b', 'c']);")
        self.assertEqual(got["patch"], "# kids-activities hide\na\nb\nc\n")
        self.assertEqual(got["count"], 3)

    def test_the_file_name_follows_the_content_not_the_clock(self):
        got = evaluate("""
          const first = Snapshot.hidePatch(['b', 'a']);
          const again = Snapshot.hidePatch(['a', 'b', 'a']);
          const other = Snapshot.hidePatch(['a', 'c']);
          return { same: first.name === again.name, differs: first.name !== other.name,
                   name: first.name };""")
        self.assertTrue(got["same"])
        self.assertTrue(got["differs"])
        self.assertRegex(got["name"], r"^hide-[0-9a-f]{8}\.txt$")

    def test_the_patch_is_readable_by_the_apply_command(self):
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
        import hide_event
        got = evaluate("return Snapshot.hidePatch(['event_20260928_1700_4d79d389347a', 'grad_20261014_1730']);")
        self.assertEqual(hide_event.parse_ids(got["patch"]),
                         ["event_20260928_1700_4d79d389347a", "grad_20261014_1730"])


if __name__ == "__main__":
    unittest.main()
