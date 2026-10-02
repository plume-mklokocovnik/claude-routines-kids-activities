/* The published app's data source: a baked snapshot of db.json plus the
   decisions staged in this browser, waiting to be written back through GitHub.

   It lives in its own file so Node can test it without a browser. The page hands
   it what it needs (fetch, storage and a way to tell the user something) and it
   never touches the DOM.

   Browser storage here is a staging area, never a record. Anything the snapshot
   already agrees with stops being pending, which is what makes the save round
   trip clear itself once the rebuilt snapshot lands. */
(function (root) {
  'use strict';

  const KEY = 'kids-activities-decisions-v1';
  const CODES = { interested: 'i', maybe: 'm', rejected: 'r' };

  function createStaticStore(env) {
    let baked = null;
    let lastText = '';
    let log = [];

    const known = (value) => value === null || Object.prototype.hasOwnProperty.call(CODES, value);

    function valid(entry) {
      return entry && typeof entry.event_id === 'string' && entry.event_id
        && (entry.action === 'set' || entry.action === 'clear')
        && known(entry.after === undefined ? null : entry.after)
        && known(entry.before === undefined ? null : entry.before);
    }

    function readLog() {
      // An unreadable or tampered value is dropped rather than trusted.
      try {
        const parsed = JSON.parse(env.storage.getItem(KEY) || '[]');
        return Array.isArray(parsed) ? parsed.filter(valid) : [];
      } catch (error) {
        return [];
      }
    }

    function writeLog() {
      try {
        env.storage.setItem(KEY, JSON.stringify(log));
      } catch (error) {
        env.notify('Brskalnik ne shranjuje. Odločitve veljajo le do osvežitve.', true);
      }
    }

    async function fetchSnapshot() {
      // Pages sends state.json with max-age=600, and a plain fetch obeys that, so
      // a reload right after a deploy still got the old file for up to ten
      // minutes. `no-cache` asks the server every time. It costs a 304 with no
      // body when nothing changed.
      const response = await env.fetch('state.json', {
        cache: 'no-cache', headers: { Accept: 'application/json' },
      }).catch(() => { throw new Error('Posnetka baze ni bilo mogoče naložiti.'); });
      if (!response.ok) throw new Error(`Posnetek baze ni dosegljiv (${response.status}).`);
      const text = await response.text();
      const parsed = JSON.parse(text);
      if (!parsed || !Array.isArray(parsed.cards)) throw new Error('Posnetek baze ni veljaven.');
      // Only a snapshot that parsed and made sense replaces the one in use.
      const changed = text !== lastText;
      baked = parsed;
      lastText = text;
      return changed;
    }

    function wanted() {
      const map = new Map();
      log.forEach((entry) => map.set(entry.event_id, entry.after || null));
      return map;
    }

    function reconcile() {
      // Anything the database already agrees with, or no longer holds, stops
      // being pending.
      const stored = new Map(baked.cards.map((card) => [card.event_id, card.decision || null]));
      const settled = new Set();
      wanted().forEach((value, id) => {
        if (!stored.has(id) || stored.get(id) === value) settled.add(id);
      });
      if (settled.size) {
        log = log.filter((entry) => !settled.has(entry.event_id));
        writeLog();
      }
    }

    function decisionOf(id) {
      const pending = wanted();
      if (pending.has(id)) return pending.get(id);
      const card = baked.cards.find((item) => item.event_id === id);
      return card ? card.decision || null : null;
    }

    function titleOf(id) {
      const card = baked.cards.find((item) => item.event_id === id);
      return card ? card.title : id;
    }

    function build() {
      const pending = wanted();
      const groups = { interested: [], maybe: [], rejected: [] };
      const deck = [];
      baked.cards.forEach((card) => {
        const staged = pending.has(card.event_id);
        const decision = staged ? pending.get(card.event_id) : card.decision || null;
        const shaped = Object.assign({}, card, { decision: decision, unsaved: staged });
        if (decision) groups[decision].push(shaped);
        else if (card.status === 'active') deck.push(shaped);
      });
      const counts = {
        interested: groups.interested.length,
        maybe: groups.maybe.length,
        rejected: groups.rejected.length,
        undecided: deck.length,
      };
      counts.decided = counts.interested + counts.maybe + counts.rejected;
      counts.total = counts.decided + counts.undecided;
      const last = log[log.length - 1];
      return {
        clock: baked.clock,
        labels: baked.labels,
        deck: deck,
        groups: groups,
        counts: counts,
        undo: last
          ? {
            available: true,
            action: last.action,
            title: titleOf(last.event_id),
            label: baked.labels[last.after] || 'brez kategorije',
            restores: baked.labels[last.before] || 'brez kategorije',
          }
          : { available: false },
      };
    }

    function record(id, action, before, after) {
      log.push({ event_id: id, action: action, before: before || null, after: after || null });
      writeLog();
    }

    return {
      live: false,
      load: async () => {
        await fetchSnapshot();
        log = readLog();
        reconcile();
        return build();
      },
      // Look for a newer snapshot. Null when nothing changed, so the page can
      // skip redrawing. The staged decisions are not read from storage again:
      // if storage refused a write, memory is the only place they still are.
      poll: async () => {
        if (!(await fetchSnapshot())) return null;
        reconcile();
        return build();
      },
      decide: async (id, category) => {
        const current = decisionOf(id);
        if (current !== category) record(id, 'set', current, category);
        return build();
      },
      clear: async (id) => {
        const current = decisionOf(id);
        if (current) record(id, 'clear', current, null);
        return build();
      },
      undo: async () => {
        if (log.length) {
          log.pop();
          writeLog();
        }
        return build();
      },
      pending: () => {
        const entries = [...wanted().entries()].sort((a, b) => (a[0] < b[0] ? -1 : 1));
        const lines = ['# kids-activities decisions'];
        entries.forEach(([id, value]) => lines.push(`${value ? CODES[value] : 'c'}:${id}`));
        return { count: entries.length, patch: `${lines.join('\n')}\n` };
      },
    };
  }

  // The list of events to hide, one exact ID per line, sorted so the same set
  // always gives the same text. The name is a hash of that text rather than a
  // timestamp: committing the same list twice names the same file, and nothing
  // here reads the clock.
  function hidePatch(ids) {
    const unique = [...new Set(ids)].sort();
    const text = `${['# kids-activities hide', ...unique].join('\n')}\n`;
    let hash = 0x811c9dc5;
    for (let index = 0; index < text.length; index += 1) {
      hash ^= text.charCodeAt(index);
      hash = Math.imul(hash, 0x01000193) >>> 0;
    }
    return { count: unique.length, patch: text, name: `hide-${hash.toString(16).padStart(8, '0')}.txt` };
  }

  const api = { KEY, createStaticStore, hidePatch };
  root.Snapshot = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
}(typeof window !== 'undefined' ? window : globalThis));
