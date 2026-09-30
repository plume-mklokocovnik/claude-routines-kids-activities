/* Which events the app still shows, by today's date in Ljubljana.

   This is the one place the app reads the clock. It decides visibility only:
   nothing here changes stored data, expiry or a generated report. It runs in
   the browser for both modes, because the published page carries a snapshot
   that can be days old, so "today" has to be read when the page is opened.

   An event is past once its Ljubljana calendar date is before today. Events from
   today stay, whatever time they started. A card with no date is never past. */
(function (root) {
  'use strict';

  const ZONE = 'Europe/Ljubljana';
  const format = new Intl.DateTimeFormat('en-GB', {
    timeZone: ZONE, year: 'numeric', month: '2-digit', day: '2-digit',
  });

  // Today's date in Ljubljana as YYYY-MM-DD, whatever timezone the device is in.
  function today(now) {
    const fields = {};
    format.formatToParts(now || new Date()).forEach((part) => { fields[part.type] = part.value; });
    return `${fields.year}-${fields.month}-${fields.day}`;
  }

  function isPast(card, todayIso) {
    return Boolean(card.day_iso) && card.day_iso < todayIso;
  }

  // The state without past events, with the counts worked out again from what is
  // left, plus how many events were left out and how many of the rest are free.
  // The input is not changed, so the same data can be filtered again later.
  function upcoming(data, todayIso) {
    const keep = (rows) => rows.filter((card) => !isPast(card, todayIso));
    const groups = {};
    let before = data.deck.length;
    Object.keys(data.groups).forEach((name) => {
      groups[name] = keep(data.groups[name]);
      before += data.groups[name].length;
    });
    const deck = keep(data.deck);
    const counts = {
      interested: (groups.interested || []).length,
      maybe: (groups.maybe || []).length,
      rejected: (groups.rejected || []).length,
      undecided: deck.length,
    };
    counts.decided = counts.interested + counts.maybe + counts.rejected;
    counts.total = counts.decided + counts.undecided;
    const shown = deck.concat(...Object.values(groups));
    return Object.assign({}, data, {
      deck, groups, counts, today: todayIso,
      past: before - counts.total,
      free: shown.filter((card) => card.is_free).length,
    });
  }

  const api = { ZONE, today, isPast, upcoming };
  root.Days = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
}(typeof window !== 'undefined' ? window : globalThis));
