/* Filtering for the review lists, kept free of the page so Node can test it.

   Everything here is a pure function of the filter object, the cards and the
   Ljubljana date the caller passes in. Nothing reads the clock, and dates are
   worked out from ISO strings through UTC, so the device timezone never enters.

   A filter object is { text, from, to, categories, free }. Every function that
   changes one returns a new object. */
(function (root) {
  'use strict';

  const DAY_MS = 24 * 60 * 60 * 1000;
  const ISO = /^(\d{4})-(\d{2})-(\d{2})$/;

  // Lower case, without diacritics, so "cebelica" finds "čebelica".
  function fold(text) {
    return String(text === null || text === undefined ? '' : text)
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()
      .replace(/đ/g, 'd');
  }

  function utc(iso) {
    const match = ISO.exec(iso || '');
    return match ? Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3])) : NaN;
  }

  function addDays(iso, days) {
    const time = utc(iso);
    return Number.isNaN(time) ? '' : new Date(time + days * DAY_MS).toISOString().slice(0, 10);
  }

  function weekday(iso) {
    return new Date(utc(iso)).getUTCDay();
  }

  const valid = (iso) => Boolean(iso) && addDays(iso, 0) === iso;

  const words = (text) => fold(text).split(/\s+/).filter(Boolean);

  function empty() {
    return { text: '', from: '', to: '', categories: [], free: false };
  }

  function isActive(filters) {
    return Boolean(words(filters.text).length || valid(filters.from) || valid(filters.to)
      || filters.categories.length || filters.free);
  }

  // The range with its ends in order. `swapped` says whether they had to be.
  function ordered(filters) {
    if (valid(filters.from) && valid(filters.to) && filters.from > filters.to) {
      return { filters: Object.assign({}, filters, { from: filters.to, to: filters.from }), swapped: true };
    }
    return { filters, swapped: false };
  }

  function haystack(card) {
    const category = String(card.category || '');
    return fold([card.title, card.venue, card.city, category, category.replace(/_/g, ' ')]
      .concat(card.notes || []).join(' '));
  }

  // A function that says whether a card passes. A card without a date never
  // passes while a date limit is set.
  function predicate(filters) {
    const range = ordered(filters).filters;
    const from = valid(range.from) ? range.from : '';
    const to = valid(range.to) ? range.to : '';
    const tokens = words(range.text);
    const kinds = new Set(range.categories);
    return (card) => {
      if (from || to) {
        const day = card.day_iso;
        if (!day || (from && day < from) || (to && day > to)) return false;
      }
      if (kinds.size && !kinds.has(card.category)) return false;
      if (range.free && card.is_free !== true) return false;
      if (!tokens.length) return true;
      const text = haystack(card);
      return tokens.every((token) => text.includes(token));
    };
  }

  const apply = (cards, filters) => cards.filter(predicate(filters));
  const matches = (card, filters) => predicate(filters)(card);

  // Event categories that exist in the cards, in alphabetical order.
  function categories(cards) {
    const found = new Set();
    cards.forEach((card) => { if (card.category && card.category !== '?') found.add(card.category); });
    return [...found].sort((a, b) => a.localeCompare(b, 'sl'));
  }

  function toggleCategory(filters, key) {
    const has = filters.categories.includes(key);
    return Object.assign({}, filters, {
      categories: has ? filters.categories.filter((item) => item !== key) : filters.categories.concat(key),
    });
  }

  // Today, this weekend and the next seven days. A Sunday has only itself left of
  // its weekend, the same as the figures on the info page.
  function presets(todayIso) {
    const day = weekday(todayIso);
    const saturday = addDays(todayIso, day === 0 ? 0 : 6 - day);
    return {
      today: { from: todayIso, to: todayIso },
      weekend: { from: saturday, to: day === 0 ? todayIso : addDays(saturday, 1) },
      week: { from: todayIso, to: addDays(todayIso, 6) },
    };
  }

  // A date as people write it here: 20.10. and, in another year than today's,
  // 05.01.2027.
  function dateLabel(iso, todayIso) {
    const short = `${iso.slice(8, 10)}.${iso.slice(5, 7)}.`;
    return valid(todayIso) && iso.slice(0, 4) !== todayIso.slice(0, 4) ? `${short}${iso.slice(0, 4)}` : short;
  }

  // One entry per active filter, for the removable chips.
  function describe(filters, todayIso) {
    const items = [];
    const text = String(filters.text || '').trim().replace(/\s+/g, ' ');
    if (words(text).length) items.push({ id: 'text', label: `Iskanje: ${text}` });
    if (valid(filters.from)) items.push({ id: 'from', label: `Od ${dateLabel(filters.from, todayIso)}` });
    if (valid(filters.to)) items.push({ id: 'to', label: `Do ${dateLabel(filters.to, todayIso)}` });
    filters.categories.forEach((key) => {
      items.push({ id: `category:${key}`, label: key.replace(/_/g, ' ') });
    });
    if (filters.free) items.push({ id: 'free', label: 'Brezplačno' });
    return items;
  }

  function remove(filters, id) {
    if (id === 'text') return Object.assign({}, filters, { text: '' });
    if (id === 'from') return Object.assign({}, filters, { from: '' });
    if (id === 'to') return Object.assign({}, filters, { to: '' });
    if (id === 'free') return Object.assign({}, filters, { free: false });
    if (id.startsWith('category:')) return toggleCategory(filters, id.slice('category:'.length));
    return filters;
  }

  const api = {
    fold, empty, isActive, ordered, predicate, apply, matches, categories, toggleCategory,
    presets, describe, remove, addDays, weekday,
  };
  root.Filters = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
}(typeof window !== 'undefined' ? window : globalThis));
