'use strict';

/* The deployed build ships a baked snapshot. Decisions are staged in this
   browser, and saving hands them to GitHub to be written into db.json. A device
   with a token starts the workflow itself. One without opens the GitHub editor. */

const THRESHOLD_X = 96;   // horizontal pixels before a swipe counts
const THRESHOLD_Y = 112;  // downward pixels before "mogoče" counts
const FLY_MS = 230;
const TAP_SLOP = 8;       // pixels a finger may drift and still count as a tap
const TAP_MS = 500;       // and how long it may stay down
const POLL_MS = 15 * 1000;       // how often to look for the rebuilt snapshot after saving
const WATCH_MS = 5 * 60 * 1000;  // and for how long
const URL_BUDGET = 6000;  // a prefilled GitHub editor link has to stay openable

const el = (id) => document.getElementById(id);
const phone = el('phone');
const stack = el('stack');
const list = el('rows');

// `raw` is what the backend sent. `data` is the same without events that are already
// past in Ljubljana, which is what everything on screen reads.
let watchUntil = 0;  // until when to keep looking for the rebuilt snapshot after a save

const st = {
  raw: null, data: null, view: 'swipe', seg: 'interested',
  busy: false, dragging: false,
  hiding: [],  // events handed to GitHub to be hidden, until the snapshot drops them
  sending: false,  // a workflow is being started right now
  sent: '',        // the patch the last successful send carried
  filters: Filters.empty(),  // memory only, so a reload starts unfiltered
  rangeFixed: false,   // the last change put the dates in order
  panelOpen: false,    // the filter panel is expanded
  selecting: false,    // rows are being ticked for a bulk change
  selected: new Set(), // ids ticked in the tab that is showing
};

const sleep = (ms) => new Promise((done) => setTimeout(done, ms));
const labelOf = (name) => (st.data && st.data.labels[name]) || name;

/* --- backends ----------------------------------------------------------- */

function browserStorage() {
  // Reading it can throw in a private window or with site data blocked.
  try { return window.localStorage; } catch (error) { return null; }
}

const store = Snapshot.createStaticStore({
  fetch: (...args) => window.fetch(...args),
  storage: browserStorage(),
  notify: (text, bad) => toast(text, bad),
});

const dispatcher = Dispatch.createClient({
  fetch: (...args) => window.fetch(...args),
  storage: browserStorage(),
  repo: window.SWIPE_REPO,
});

function setData(raw) {
  st.raw = raw;
  st.data = Days.upcoming(raw, Days.today());
}

async function refresh(options) {
  setData(await store.load());
  render(options);
}

/* --- rendering ---------------------------------------------------------- */

function render(options) {
  if (!st.data) return;
  const counts = st.data.counts;

  document.querySelectorAll('[data-count]').forEach((node) => {
    const value = counts[node.dataset.count];
    node.textContent = value;
    // A badge at zero stays, since it says nothing has been chosen, but fades.
    node.classList.toggle('is-zero', node.classList.contains('act-count') && !value);
  });
  el('tab-left').textContent = counts.undecided;
  el('tab-done').textContent = counts.decided;
  const share = counts.total ? Math.round((counts.decided / counts.total) * 100) : 0;
  el('progress-fill').style.width = `${share}%`;
  el('progress').setAttribute('aria-valuenow', String(counts.decided));
  el('progress').setAttribute('aria-valuemax', String(counts.total));

  document.querySelectorAll('[data-decide]').forEach((button) => {
    const category = button.dataset.decide;
    button.disabled = counts.undecided === 0;
    button.setAttribute('aria-label', `${labelOf(category)}, ${counts[category]}`);
  });
  const undoInfo = st.data.undo;
  const undoButton = el('undo');
  undoButton.disabled = !undoInfo.available;
  undoButton.title = undoInfo.available
    ? `Razveljavi: ${undoInfo.title} → ${undoInfo.restores} (Z)`
    : 'Razveljavi se le še neshranjene odločitve';

  el('hint-count').textContent = counts.undecided
    ? `${counts.undecided} še za odločitev`
    : 'Kup je prazen';
  el('done-text').textContent = counts.total
    ? `Vseh ${counts.total} dogodkov je razvrščenih.`
    : 'V bazi ni aktivnih dogodkov.';

  renderStats();
  renderCharts();
  renderPending();
  renderQuick();
  renderStack(options);
  renderList();
}

function isoToSi(iso) {
  return iso ? `${iso.slice(8, 10)}.${iso.slice(5, 7)}.${iso.slice(0, 4)}` : '?';
}

const DAY_MS = 24 * 60 * 60 * 1000;
const TOP_CATEGORIES = 6;
const TOP_SOURCES = 5;

// Days are counted from ISO strings through UTC, so the device timezone never
// enters. The value is days since 1970-01-01, and NaN for a missing date.
function isoDay(iso) {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || '');
  if (!match) return NaN;
  return Math.round(Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3])) / DAY_MS);
}

function weekdayOf(day) {
  return new Date(day * DAY_MS).getUTCDay();
}

function siToIso(text) {
  const match = /^(\d{2})\.(\d{2})\.(\d{4})$/.exec(text || '');
  return match ? `${match[3]}-${match[2]}-${match[1]}` : '';
}

function allCards() {
  return st.data.deck.concat(...Object.values(st.data.groups));
}

function agePhrase(days) {
  if (!Number.isFinite(days) || days < 0) return '?';
  if (days === 0) return 'danes';
  if (days === 1) return 'včeraj';
  const tail = days % 100;
  if (tail === 2) return `${days} dneva nazaj`;
  if (tail === 3 || tail === 4) return `${days} dnevi nazaj`;
  return `${days} dni nazaj`;
}

function countBetween(cards, from, to) {
  return cards.filter((card) => {
    const day = isoDay(card.day_iso);
    return day >= from && day <= to;
  }).length;
}

// The facts about the data that the deck has no room for: when the last sweep
// ran, how old that is, what today is and how the events are spread.
// The commit this page was built from, shown as its short hash and date and linked
// to the commit on GitHub. Empty when the build could not read the history.
function renderVersion(id, commit) {
  const link = el(id);
  const sha = (commit && commit.sha) || '';
  if (!sha) {
    link.textContent = '?';
    link.removeAttribute('href');
    return;
  }
  const repo = window.SWIPE_REPO || {};
  const date = commit.date ? ` · ${isoToSi(commit.date)}` : '';
  link.textContent = `${sha.slice(0, 7)}${date}`;
  if (repo.owner && repo.repo) {
    link.href = `https://github.com/${repo.owner}/${repo.repo}/commit/${sha}`;
  } else {
    link.removeAttribute('href');
  }
}

function renderStats() {
  const { clock, counts, free, today } = st.data;
  const build = window.SWIPE_BUILD || {};
  renderVersion('ver-app', build.app);
  renderVersion('ver-data', build.data);
  const cards = allCards();
  const todayDay = isoDay(today);
  el('st-run').textContent = `${clock.date} ${clock.time}`;
  el('st-age').textContent = agePhrase(todayDay - isoDay(siToIso(clock.date)));
  el('st-window').textContent = clock.horizon;
  el('st-today').textContent = isoToSi(today);
  el('st-unsaved').textContent = String(store.pending ? store.pending().count : 0);

  el('st-total').textContent = String(counts.total);
  el('st-free').textContent = String(free);
  el('st-week').textContent = String(countBetween(cards, todayDay, todayDay + 6));
  // Saturday and Sunday of this week. On a Sunday only today is left of it.
  const weekday = weekdayOf(todayDay);
  const from = weekday === 0 ? todayDay : todayDay + 6 - weekday;
  const to = weekday === 0 ? todayDay : from + 1;
  el('st-weekend').textContent = String(countBetween(cards, from, to));
  el('st-decided').textContent = `${counts.total ? Math.round((counts.decided / counts.total) * 100) : 0} %`;
  const first = cards.filter((card) => card.day_iso)
    .reduce((best, card) => (!best || card.day_iso < best.day_iso ? card : best), null);
  el('st-next').textContent = first ? `${first.day} ${first.date}` : '?';
}

function tally(cards, keyOf, nameOf) {
  const groups = new Map();
  cards.forEach((card) => {
    const key = keyOf(card);
    if (!key) return;
    const entry = groups.get(key) || { key, label: nameOf(card), count: 0 };
    entry.count += 1;
    groups.set(key, entry);
  });
  return [...groups.values()];
}

const byCountThenLabel = (a, b) => b.count - a.count || a.label.localeCompare(b.label, 'sl');

function topWithRest(entries, limit) {
  const sorted = entries.sort(byCountThenLabel);
  if (sorted.length <= limit + 1) return sorted;
  const rest = sorted.slice(limit).reduce((sum, entry) => sum + entry.count, 0);
  return sorted.slice(0, limit).concat({ label: 'Ostalo', count: rest });
}

function renderBars(containerId, entries) {
  const box = el(containerId);
  box.textContent = '';
  if (!entries.length) {
    const none = document.createElement('p');
    none.className = 'panel-note';
    none.textContent = 'Ni podatkov';
    box.appendChild(none);
    return;
  }
  const most = Math.max(...entries.map((entry) => entry.count));
  entries.forEach((entry) => {
    const row = document.createElement('div');
    row.className = 'bar-row';
    const label = document.createElement('span');
    label.className = 'bar-label';
    label.textContent = entry.label;
    const count = document.createElement('span');
    count.className = 'bar-count';
    count.textContent = String(entry.count);
    const track = document.createElement('div');
    track.className = 'bar-track';
    const fill = document.createElement('div');
    fill.className = 'bar-fill';
    fill.style.width = `${Math.max(2, Math.round((entry.count / most) * 100))}%`;
    track.appendChild(fill);
    row.append(label, count, track);
    box.appendChild(row);
  });
}

function renderCharts() {
  const cards = allCards();
  // Month keys sort in time order, and events without a date come last.
  const months = tally(cards, (card) => card.month || 'z', (card) => card.month_long)
    .sort((a, b) => (a.key < b.key ? -1 : 1));
  renderBars('bars-months', months);
  renderBars('bars-categories', topWithRest(
    tally(cards, (card) => card.category, (card) => card.category.replace(/_/g, ' ')),
    TOP_CATEGORIES,
  ));
  renderBars('bars-sources', tally(cards, (card) => card.source, (card) => card.source)
    .sort(byCountThenLabel).slice(0, TOP_SOURCES));
}

function pendingPhrase(count) {
  const tail = count % 100;
  if (tail === 1) return `${count} odločitev čaka`;
  if (tail === 2) return `${count} odločitvi čakata`;
  if (tail === 3 || tail === 4) return `${count} odločitve čakajo`;
  return `${count} odločitev čaka`;
}

function renderPending() {
  if (!store.pending) return;
  const { count, patch } = store.pending();
  const banner = el('pending');
  banner.hidden = count === 0;
  if (count) el('pending-text').textContent = pendingPhrase(count);
  if (!count) st.sent = '';
  // Sent and still unsaved: the same patch would only start the workflow again.
  // After the watch window the button returns, in case the run never happened.
  const waiting = count > 0 && st.sent === patch && Date.now() < watchUntil;
  const button = el('save');
  button.disabled = st.sending || waiting;
  button.textContent = st.sending ? 'Pošiljam …' : waiting ? 'Poslano' : 'Shrani v GitHub';
  // Once sent, the workflow will write them whatever this page does, so there is
  // nothing left to cancel here.
  const cancel = el('discard');
  if (!count || st.sending || waiting) disarmDiscard();
  cancel.disabled = st.sending || waiting;
  cancel.classList.toggle('is-armed', discarding.armed);
  cancel.textContent = discarding.armed ? 'Zavrži?' : '✕';
  cancel.title = waiting ? 'Že poslano, odločitev ni več mogoče preklicati'
    : discarding.armed ? 'Še en dotik zavrže vse neshranjene odločitve'
      : 'Zavrži neshranjene odločitve';
}

// Dropping decisions cannot be undone, so the first tap only asks and the second,
// within a few seconds, does it.
const discarding = { armed: false, timer: null };

function disarmDiscard() {
  clearTimeout(discarding.timer);
  discarding.armed = false;
}

async function discardPending() {
  if (!store.discard || st.busy || st.sending) return;
  const { count } = store.pending();
  if (!count) return;
  if (!discarding.armed) {
    discarding.armed = true;
    clearTimeout(discarding.timer);
    discarding.timer = setTimeout(() => { disarmDiscard(); renderPending(); }, 3500);
    renderPending();
    return;
  }
  disarmDiscard();
  st.busy = true;
  try {
    setData(await store.discard());
    st.sent = '';
    render({ returning: true });
    toast(`Zavrženo: ${count}`);
  } catch (error) {
    toast(error.message, true);
  } finally {
    st.busy = false;
  }
}

const QUICK_TEXT = {
  off: 'Z žetonom ta naprava shrani z enim dotikom, brez urejevalnika GitHub. '
    + 'Vsaka naprava ima svoj žeton, ki ga na GitHubu prekličeš posebej.',
  on: 'Ta naprava shranjuje z enim dotikom. Žeton je le na njej. '
    + 'Prekličeš ga v nastavitvah GitHub, drugim napravam to ne škodi.',
  rejected: 'GitHub žetona ne sprejme. Je pretekel ali preklican? Odstrani ga in vnesi novega. '
    + 'Do takrat shranjuješ prek urejevalnika.',
};

// The token settings are the last section of the info page. Nothing about the
// token leaves this function: the field is emptied once it is stored.
function renderQuick() {
  const section = el('quick');
  section.hidden = !dispatcher.available();
  el('quick-none').hidden = !section.hidden;
  if (section.hidden) return;
  const on = dispatcher.enabled();
  const bad = on && dispatcher.rejected();
  const mode = bad ? 'rejected' : on ? 'on' : 'off';
  el('quick-state').textContent = { off: 'Izklopljeno', on: 'Vklopljeno', rejected: 'Ne deluje' }[mode];
  el('quick-state').dataset.mode = mode;
  el('quick-text').textContent = QUICK_TEXT[mode];
  el('quick-token').hidden = mode === 'on';
  el('quick-on').hidden = mode === 'on';
  el('quick-off').hidden = !on;
  const link = el('quick-new');
  link.hidden = mode === 'on';
  if (!link.hidden) link.href = dispatcher.templateUrl();
}

function fill(node, name, text) {
  const target = node.querySelector(`[data-f="${name}"]`);
  if (target) target.textContent = text;
  return target;
}

function placeText(card) {
  if (!card.city || card.city === 'Ljubljana') return card.venue;
  // Some venues already carry their town, so appending it would read twice.
  if (card.venue.toLowerCase().includes(card.city.toLowerCase())) return card.venue;
  return `${card.venue}, ${card.city}`;
}

function priceText(card) {
  if (card.is_free) return card.price ? `Brezplačno · ${card.price}` : 'Brezplačno';
  return card.price || '?';
}

function buildCard(card) {
  const node = el('card-template').content.firstElementChild.cloneNode(true);
  fill(node, 'category', card.category);
  fill(node, 'day', card.day);
  fill(node, 'time', card.time);
  fill(node, 'date_long', card.date_long);
  fill(node, 'title', card.title);
  fill(node, 'place', placeText(card));
  fill(node, 'age', card.age);
  node.querySelector('[data-slot="id"]').appendChild(idButton(card.event_id));
  fill(node, 'price', priceText(card)).classList.toggle('is-free', card.is_free);

  const status = node.querySelector('[data-f="status"]');
  status.hidden = card.status === 'active';
  status.textContent = card.status === 'expired' ? 'poteklo' : 'skrito';

  const notes = node.querySelector('[data-f="notes"]');
  card.notes.forEach((text) => {
    const chip = document.createElement('span');
    chip.textContent = text;
    notes.appendChild(chip);
  });

  const source = node.querySelector('[data-f="url"]');
  if (card.url) source.href = card.url;
  else source.hidden = true;
  node.querySelector('[data-f="maps"]').href = card.maps;
  return node;
}

function renderStack(options) {
  stack.textContent = '';
  const deck = st.data.deck;
  el('done').hidden = deck.length > 0;
  stack.hidden = deck.length === 0;

  const visible = deck.slice(0, 3).reverse();
  visible.forEach((card, index) => {
    const node = buildCard(card);
    const depth = visible.length - 1 - index;
    if (depth === 0) {
      node.classList.add('is-top');
      if (options && options.returning) node.classList.add('is-returning');
      attachDrag(node, card);
    } else {
      node.style.transform = `translateY(${depth * -9}px) scale(${1 - depth * 0.035})`;
      node.style.opacity = String(1 - depth * 0.28);
    }
    stack.appendChild(node);
  });
}

function buildRow(card) {
  const node = el('row-template').content.firstElementChild.cloneNode(true);
  fill(node, 'date', card.date_short);
  fill(node, 'time', card.time);
  fill(node, 'title', card.title);
  fill(node, 'place', placeText(card));
  const extra = [card.category, `${card.age} let`, priceText(card)];
  if (card.status !== 'active') extra.push(card.status === 'expired' ? 'poteklo' : 'skrito');
  if (card.unsaved) extra.push('ni shranjeno');
  fill(node, 'meta', extra.concat(card.notes).join(' · '));
  node.classList.toggle('is-unsaved', Boolean(card.unsaved));

  const check = node.querySelector('.row-check');
  const opener = node.querySelector('.row-title');
  const picked = st.selected.has(card.event_id);
  node.classList.toggle('is-selected', picked);
  check.checked = picked;
  check.setAttribute('aria-label', `Izberi: ${card.title}`);
  check.addEventListener('change', () => setPicked(card, check.checked));
  if (st.selecting) {
    // The checkbox is the control now. The title only passes the tap on.
    opener.tabIndex = -1;
    opener.removeAttribute('aria-haspopup');
  }

  // The title is a real button, so keyboard and screen-reader users can open
  // the dialog. A tap anywhere else on the row opens it too, unless it finished
  // a text selection. While rows are being ticked, a tap toggles the row instead.
  node.addEventListener('click', (event) => {
    if (String(window.getSelection && window.getSelection()).length) return;
    if (!st.selecting) {
      openDetails(card, opener, { decide: true });
    } else if (event.target !== check) {
      check.checked = !check.checked;
      setPicked(card, check.checked);
    }
  });
  rowNodes.set(card.event_id, node);
  return node;
}

// The button hides every event in the Zavrnjeno list. Writing needs the
// repository, so it only shows on that list, and not while a filter or the
// selection narrows what the list shows, since the button hides all of them.
function renderFab() {
  const visible = st.view === 'review' && st.seg === 'rejected'
    && Boolean(st.data) && st.data.groups.rejected.length > 0
    && !st.selecting && !Filters.isActive(st.filters);
  el('hide-fab').hidden = !visible;
  el('list').classList.toggle('has-fab', visible);
}

function segmentRows(name) {
  return name === 'undecided' ? st.data.deck : (st.data.groups[name] || []);
}

function emptyState(hasRows) {
  const box = document.createElement('div');
  box.className = 'list-empty';
  const text = document.createElement('p');
  box.appendChild(text);
  if (hasRows) {
    text.textContent = 'Ni zadetkov za izbrane filtre.';
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'wide-btn';
    button.textContent = 'Počisti filtre';
    button.addEventListener('click', clearFilters);
    box.appendChild(button);
  } else {
    text.textContent = st.seg === 'undecided'
      ? 'Vsi dogodki so razvrščeni.'
      : `V kategoriji "${labelOf(st.seg)}" še ni dogodkov.`;
  }
  return box;
}

function renderList() {
  if (!st.data) return;
  document.querySelectorAll('.seg').forEach((seg) => {
    seg.classList.toggle('is-on', seg.dataset.seg === st.seg);
  });
  pruneCategories();
  renderSegmentCounts();
  const base = segmentRows(st.seg);
  shown = Filters.apply(base, st.filters);
  pruneSelection();
  renderFab();
  renderFilters(base.length);
  renderSelection();

  list.textContent = '';
  rowNodes.clear();
  list.classList.toggle('is-selecting', st.selecting);
  if (!shown.length) {
    list.appendChild(emptyState(base.length > 0));
    return;
  }
  let month = null;
  shown.forEach((card) => {
    if (card.month_long !== month) {
      month = card.month_long;
      const heading = document.createElement('p');
      heading.className = 'list-head';
      heading.textContent = month;
      list.appendChild(heading);
    }
    list.appendChild(buildRow(card));
  });
}

/* --- filters ------------------------------------------------------------ */

let shown = [];  // the rows of the current tab that pass the filters
const rowNodes = new Map();

// The tab counters show what passes the filters while any is set. They have an
// attribute of their own, so the badges and the tab bar keep the true totals.
function renderSegmentCounts() {
  const keep = Filters.predicate(st.filters);
  document.querySelectorAll('[data-seg-count]').forEach((node) => {
    const rows = segmentRows(node.dataset.segCount);
    node.textContent = String(Filters.isActive(st.filters) ? rows.filter(keep).length : rows.length);
  });
}

// A category that left the data, after a newer snapshot, cannot stay selected.
function pruneCategories() {
  const keys = Filters.categories(allCards());
  const kept = st.filters.categories.filter((key) => keys.includes(key));
  if (kept.length !== st.filters.categories.length) {
    st.filters = Object.assign({}, st.filters, { categories: kept });
  }
}

function syncCategoryChips() {
  const box = el('filter-cats');
  const keys = Filters.categories(allCards());
  // The chips are rebuilt only when the set of categories changes, so a chip
  // that has just been tapped keeps the focus.
  if (box.dataset.keys !== keys.join('|')) {
    box.dataset.keys = keys.join('|');
    box.textContent = '';
    keys.forEach((key) => {
      const chipButton = document.createElement('button');
      chipButton.type = 'button';
      chipButton.className = 'fchip';
      chipButton.dataset.category = key;
      chipButton.textContent = key.replace(/_/g, ' ');
      chipButton.addEventListener('click', () => changeFilters(Filters.toggleCategory(st.filters, key)));
      box.appendChild(chipButton);
    });
  }
  box.querySelectorAll('.fchip').forEach((button) => {
    button.setAttribute('aria-pressed', String(st.filters.categories.includes(button.dataset.category)));
  });
  el('filter-cat-group').hidden = keys.length === 0;
}

function renderActiveChips() {
  const box = el('filter-chips');
  box.textContent = '';
  Filters.describe(st.filters, st.data.today).forEach((item) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'fchip fchip-active';
    button.dataset.filter = item.id;
    button.setAttribute('aria-label', `Odstrani filter: ${item.label}`);
    const text = document.createElement('span');
    text.className = 'fchip-text';
    text.textContent = item.label;
    const cross = document.createElement('span');
    cross.setAttribute('aria-hidden', 'true');
    cross.textContent = '✕';
    button.append(text, cross);
    box.appendChild(button);
  });
  box.hidden = box.children.length === 0;
}

function renderFilters(baseCount) {
  const filters = st.filters;
  const active = Filters.isActive(filters);
  const search = el('filter-search');
  if (search.value !== filters.text) search.value = filters.text;
  el('filter-search-clear').hidden = !filters.text;

  const panelCount = Filters.describe(filters).filter((item) => item.id !== 'text').length;
  const toggle = el('filters-toggle');
  toggle.setAttribute('aria-expanded', String(st.panelOpen));
  toggle.setAttribute('aria-label', panelCount ? `Filtri, aktivnih: ${panelCount}` : 'Filtri');
  el('filters-badge').hidden = panelCount === 0;
  el('filters-badge').textContent = String(panelCount);
  el('filter-panel').hidden = !st.panelOpen;

  if (el('filter-from').value !== filters.from) el('filter-from').value = filters.from;
  if (el('filter-to').value !== filters.to) el('filter-to').value = filters.to;
  el('filter-hint').hidden = !st.rangeFixed;
  const presets = Filters.presets(st.data.today);
  document.querySelectorAll('[data-preset]').forEach((button) => {
    const range = presets[button.dataset.preset];
    button.setAttribute('aria-pressed', String(filters.from === range.from && filters.to === range.to));
  });
  el('filter-free').setAttribute('aria-checked', String(filters.free));
  syncCategoryChips();
  renderActiveChips();

  el('filter-result').textContent = active ? `Prikazano ${shown.length} od ${baseCount}` : '';
  el('filter-clear').hidden = !active;
  el('filter-foot').classList.toggle('is-on', active);
}

function changeFilters(next) {
  const fixed = Filters.ordered(next);
  st.filters = fixed.filters;
  st.rangeFixed = fixed.swapped;
  el('list').scrollTop = 0;
  renderList();
}

function clearFilters() {
  st.filters = Filters.empty();
  st.rangeFixed = false;
  renderList();
  document.querySelector('.seg.is-on').focus({ preventScroll: true });
}

function removeFilter(button) {
  const chips = [...el('filter-chips').children];
  const at = chips.indexOf(button);
  changeFilters(Filters.remove(st.filters, button.dataset.filter));
  const left = el('filter-chips').children;
  (left[Math.min(at, left.length - 1)] || el('filters-toggle')).focus({ preventScroll: true });
}

function applyPreset(name) {
  const range = Filters.presets(st.data.today)[name];
  const on = st.filters.from === range.from && st.filters.to === range.to;
  changeFilters(Object.assign({}, st.filters, on ? { from: '', to: '' } : range));
}

function wireFilters() {
  const search = el('filter-search');
  search.addEventListener('input', () => changeFilters(Object.assign({}, st.filters, { text: search.value })));
  search.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape' || !search.value) return;
    event.preventDefault();
    event.stopPropagation();
    changeFilters(Object.assign({}, st.filters, { text: '' }));
  });
  el('filter-search-clear').addEventListener('click', () => {
    changeFilters(Object.assign({}, st.filters, { text: '' }));
    search.focus({ preventScroll: true });
  });
  el('filters-toggle').addEventListener('click', () => {
    st.panelOpen = !st.panelOpen;
    renderFilters(segmentRows(st.seg).length);
  });
  el('filter-from').addEventListener('change', (event) => {
    changeFilters(Object.assign({}, st.filters, { from: event.target.value }));
  });
  el('filter-to').addEventListener('change', (event) => {
    changeFilters(Object.assign({}, st.filters, { to: event.target.value }));
  });
  document.querySelectorAll('[data-preset]').forEach((button) => {
    button.addEventListener('click', () => applyPreset(button.dataset.preset));
  });
  el('filter-free').addEventListener('click', () => {
    changeFilters(Object.assign({}, st.filters, { free: !st.filters.free }));
  });
  el('filter-chips').addEventListener('click', (event) => {
    const button = event.target.closest('[data-filter]');
    if (button) removeFilter(button);
  });
  el('filter-clear').addEventListener('click', clearFilters);
}

/* --- selecting rows for a bulk change ------------------------------------- */

function pruneSelection() {
  if (!st.selected.size) return;
  const ids = new Set(shown.map((card) => card.event_id));
  st.selected.forEach((id) => { if (!ids.has(id)) st.selected.delete(id); });
}

function syncRow(id) {
  const node = rowNodes.get(id);
  if (!node) return;
  const on = st.selected.has(id);
  node.classList.toggle('is-selected', on);
  node.querySelector('.row-check').checked = on;
}

function renderSelection() {
  const toggle = el('select-toggle');
  toggle.setAttribute('aria-pressed', String(st.selecting));
  el('selbar').hidden = !st.selecting;
  if (!st.selecting) return;
  const count = st.selected.size;
  el('sel-count').textContent = `Izbrano ${count}`;
  const all = shown.length > 0 && count === shown.length;
  el('sel-all').textContent = all ? 'Počisti izbiro' : 'Izberi vse';
  el('sel-all').disabled = shown.length === 0;
  document.querySelectorAll('[data-bulk]').forEach((button) => {
    const target = button.dataset.bulk;
    // The tab already is that category, and the deck cannot go back to the deck.
    button.hidden = target === st.seg || (target === '' && st.seg === 'undecided');
    button.disabled = count === 0;
  });
}

function setPicked(card, on) {
  if (on) st.selected.add(card.event_id);
  else st.selected.delete(card.event_id);
  syncRow(card.event_id);
  renderSelection();
}

function toggleAll() {
  const all = shown.length > 0 && st.selected.size === shown.length;
  st.selected.clear();
  if (!all) shown.forEach((card) => st.selected.add(card.event_id));
  shown.forEach((card) => syncRow(card.event_id));
  renderSelection();
}

// Selection never reaches across tabs, but the mode stays on.
function pickSegment(name) {
  if (st.seg !== name) st.selected.clear();
  st.seg = name;
  renderList();
}

function setSelecting(on) {
  if (st.selecting === on) return;
  st.selecting = on;
  st.selected.clear();
  if (st.data) renderList();
}

function endSelecting() {
  setSelecting(false);
  el('select-toggle').focus({ preventScroll: true });
}

async function bulkMove(target) {
  if (st.busy || !st.selecting) return;
  const ids = shown.filter((card) => st.selected.has(card.event_id)).map((card) => card.event_id);
  if (!ids.length) return;
  st.busy = true;
  try {
    setData(await store.decideMany(ids, target));
    st.selected.clear();
    st.selecting = false;
    render();
    el('select-toggle').focus({ preventScroll: true });
    toast(`Premaknjeno: ${ids.length}`);
  } catch (error) {
    toast(error.message, true);
  } finally {
    st.busy = false;
  }
}

function wireSelection() {
  el('select-toggle').addEventListener('click', () => setSelecting(!st.selecting));
  el('sel-done').addEventListener('click', endSelecting);
  el('sel-all').addEventListener('click', toggleAll);
  el('sel-actions').addEventListener('click', (event) => {
    const button = event.target.closest('[data-bulk]');
    if (button) bulkMove(button.dataset.bulk);
  });
}

/* --- swipe mechanics ---------------------------------------------------- */

function vector(dx, dy) {
  if (dy > 0 && dy > Math.abs(dx) * 1.15) return { dir: 'maybe', p: dy / THRESHOLD_Y };
  if (dx > 0) return { dir: 'interested', p: dx / THRESHOLD_X };
  if (dx < 0) return { dir: 'rejected', p: -dx / THRESHOLD_X };
  return { dir: null, p: 0 };
}

function setGlow(dir, share) {
  const value = Math.min(1, Math.max(0, share));
  phone.style.setProperty('--in-right', String(dir === 'interested' ? value : 0));
  phone.style.setProperty('--in-left', String(dir === 'rejected' ? value : 0));
  phone.style.setProperty('--in-down', String(dir === 'maybe' ? value : 0));
}

function attachDrag(node, card) {
  let pointer = null;
  let sx = 0;
  let sy = 0;
  let dx = 0;
  let dy = 0;
  let startedAt = 0;
  let tappedAt = -Infinity;

  node.addEventListener('pointerdown', (event) => {
    if (st.busy || pointer !== null) return;
    if (event.target.closest('a, button')) return;
    if (event.pointerType === 'mouse' && event.button !== 0) return;
    pointer = event.pointerId;
    tappedAt = -Infinity;
    st.dragging = true;
    startedAt = event.timeStamp;
    sx = event.clientX;
    sy = event.clientY;
    dx = 0;
    dy = 0;
    node.classList.remove('is-springing', 'is-returning');
    try { node.setPointerCapture(pointer); } catch (error) { /* capture is optional */ }
  });

  node.addEventListener('pointermove', (event) => {
    if (event.pointerId !== pointer) return;
    dx = event.clientX - sx;
    dy = event.clientY - sy;
    const reading = vector(dx, dy);
    setGlow(reading.dir, reading.p);
    const tilt = Math.max(-14, Math.min(14, dx / 14));
    node.style.transform = `translate(${dx}px, ${dy}px) rotate(${tilt}deg)`;
  });

  const release = (event) => {
    if (event.pointerId !== pointer) return;
    try { node.releasePointerCapture(pointer); } catch (error) { /* already gone */ }
    pointer = null;
    st.dragging = false;
    // A finger that barely moved and lifted quickly is a tap, not a swipe.
    const tapped = event.type === 'pointerup' && Math.hypot(dx, dy) < TAP_SLOP
      && event.timeStamp - startedAt < TAP_MS;
    if (tapped) {
      springBack(node);
      tappedAt = event.timeStamp;
      return;
    }
    const reading = vector(dx, dy);
    if (reading.dir && reading.p >= 1) commit(reading.dir, node, card);
    else springBack(node);
  };

  // A tap ends in a click, and that is when the dialog opens. Opening on pointerup
  // would put the dialog under the finger before the browser sends the rest of
  // the same tap as mouse events, and they would land on its backdrop.
  node.addEventListener('click', (event) => {
    if (event.timeStamp - tappedAt > 800) return;
    tappedAt = -Infinity;
    openDetails(card, null);
  });

  node.addEventListener('pointerup', release);
  node.addEventListener('pointercancel', release);
  node.addEventListener('lostpointercapture', (event) => {
    if (event.pointerId === pointer) release(event);
  });
}

function springBack(node) {
  node.classList.add('is-springing');
  node.style.transform = '';
  setGlow(null, 0);
  setTimeout(() => node.classList.remove('is-springing'), 240);
}

function flyOut(node, dir) {
  const width = stack.clientWidth + 140;
  const height = stack.clientHeight + 140;
  node.classList.add('is-sliding');
  node.style.opacity = '0.15';
  if (dir === 'interested') node.style.transform = `translate(${width}px, -40px) rotate(20deg)`;
  else if (dir === 'rejected') node.style.transform = `translate(${-width}px, -40px) rotate(-20deg)`;
  else node.style.transform = `translate(0, ${height}px) rotate(3deg)`;
}

async function commit(dir, node, card) {
  if (st.busy) return;
  st.busy = true;
  setGlow(dir, 1);
  flyOut(node, dir);
  try {
    const [state] = await Promise.all([store.decide(card.event_id, dir), sleep(FLY_MS)]);
    setData(state);
    render();
    toast(`${labelOf(dir)}: ${card.title}`);
  } catch (error) {
    toast(error.message, true);
    await refresh().catch(() => {});
  } finally {
    setGlow(null, 0);
    st.busy = false;
  }
}

function decideTop(dir) {
  if (st.busy || !st.data || !st.data.deck.length) return;
  const node = stack.querySelector('.card.is-top');
  if (node) commit(dir, node, st.data.deck[0]);
}

async function undo() {
  if (st.busy || !st.data || !st.data.undo.available) return;
  const previous = st.data.undo;
  st.busy = true;
  try {
    setData(await store.undo());
    render({ returning: true });
    toast(`Razveljavljeno: ${previous.title} → ${previous.restores}`);
  } catch (error) {
    toast(error.message, true);
  } finally {
    st.busy = false;
  }
}

// True when the event was moved. An empty target sends it back to the deck.
async function move(card, target) {
  if (st.busy || target === (card.decision || '')) return false;
  st.busy = true;
  try {
    setData(target ? await store.decide(card.event_id, target) : await store.clear(card.event_id));
    render();
    toast(`Premaknjeno v ${labelOf(target || 'undecided')}`);
    return true;
  } catch (error) {
    toast(error.message, true);
    return false;
  } finally {
    st.busy = false;
  }
}

// The row that was opened is gone once it moved, so focus goes to the row that
// took its place, or to the tab when the list is empty.
function focusRowAt(index) {
  const titles = list.querySelectorAll('.row-title');
  const next = titles[Math.max(0, Math.min(index, titles.length - 1))];
  (next || document.querySelector('.seg.is-on')).focus({ preventScroll: true });
}

async function pickFromDialog(target) {
  const card = dialog.card;
  if (!card || st.busy) return;
  if (target === (card.decision || '')) {
    closeDetails();
    return;
  }
  const at = shown.findIndex((item) => item.event_id === card.event_id);
  if (!(await move(card, target))) return;
  closeDetails();
  focusRowAt(at);
}

/* --- details dialog ------------------------------------------------------ */

const dialog = {
  open: false, opener: null, pushed: false, pressedBackdrop: false, card: null,
  decide: false,  // opened from a row of Pregled, so it offers the decision buttons
};
const BEHIND = '.bar, .progress, .tallies, .main, .pending, .tabs';

function chip(parent, className, text) {
  const node = document.createElement('span');
  node.className = className;
  node.textContent = text;
  parent.appendChild(node);
  return node;
}

function fact(parent, label, content, className) {
  if (content === '' || content === null || content === undefined) return;
  const term = document.createElement('dt');
  term.textContent = label;
  const detail = document.createElement('dd');
  if (className) detail.className = className;
  if (content instanceof Node) {
    detail.appendChild(content);
  } else {
    const [main, note] = Array.isArray(content) ? content : [content, ''];
    detail.textContent = main;
    if (note) {
      const small = document.createElement('small');
      small.textContent = note;
      detail.appendChild(small);
    }
  }
  parent.append(term, detail);
}

function whenFacts(card) {
  if (!card.date) return ['Datum ni znan', ''];
  return [`${card.day}, ${card.date_long}`, card.time === '?' ? 'Ura ni znana' : `ob ${card.time}`];
}

function fillDecision(card) {
  el('d-decide').hidden = !dialog.decide;
  const current = card.decision || '';
  el('d-decide').querySelectorAll('[data-pick]').forEach((button) => {
    const target = button.dataset.pick;
    button.classList.toggle('is-on', target === current);
    if (target) button.setAttribute('aria-pressed', String(target === current));
    // Sending an undecided event back to the deck would change nothing.
    else button.hidden = !card.decision;
  });
}

function fillDetails(card) {
  const state = card.decision || 'undecided';
  el('details-title').textContent = card.title;

  const chips = el('d-chips');
  chips.textContent = '';
  chip(chips, 'chip chip-cat', card.category.replace(/_/g, ' '));
  chip(chips, 'chip chip-decision', labelOf(state)).dataset.decision = state;
  if (card.status !== 'active') {
    chip(chips, 'chip chip-status', card.status === 'expired' ? 'poteklo' : 'skrito');
  }
  if (card.unsaved) chip(chips, 'chip chip-unsaved', 'ni shranjeno');

  const facts = el('d-facts');
  facts.textContent = '';
  const extra = card.price && card.price.toLowerCase() !== 'brezplačno' ? card.price : '';
  fact(facts, 'Kdaj', whenFacts(card));
  fact(facts, 'Kje', placeText(card));
  fact(facts, 'Starost', card.age === '?' ? 'Ni objavljeno' : `${card.age} let`);
  if (card.is_free) fact(facts, 'Cena', ['Brezplačno', extra], 'is-free');
  else fact(facts, 'Cena', card.price || 'Ni objavljeno');
  fact(facts, 'Vir', card.source || 'Brez povezave');
  if (card.decision) {
    fact(facts, 'Odločitev', [labelOf(state), card.decided_at ? `zabeleženo ${card.decided_at}` : '']);
  }
  fact(facts, 'Prvič videno', card.first_seen);
  fact(facts, 'ID', idButton(card.event_id));

  const notes = el('d-notes');
  notes.textContent = '';
  card.notes.forEach((text) => chip(notes, '', text));

  const source = el('d-source');
  source.hidden = !card.url;
  if (card.url) source.href = card.url;
  el('d-maps').href = card.maps;
  fillDecision(card);
}

function openDetails(card, opener, options) {
  if (dialog.open) return;
  dialog.decide = Boolean(options && options.decide);
  fillDetails(card);
  dialog.card = card;
  dialog.open = true;
  dialog.opener = opener;
  dialog.pressedBackdrop = false;
  el('details').hidden = false;
  // Everything behind the dialog stops taking focus and taps.
  document.querySelectorAll(BEHIND).forEach((node) => { node.inert = true; });
  // One history entry, so the phone's back gesture closes the dialog rather
  // than leaving the app.
  try {
    history.pushState({ details: true }, '');
    dialog.pushed = true;
  } catch (error) {
    dialog.pushed = false;
  }
  el('details').querySelector('.sheet-body').scrollTop = 0;
  el('sheet').focus({ preventScroll: true });
}

function hideDetails() {
  if (!dialog.open) return;
  dialog.open = false;
  dialog.card = null;
  el('details').hidden = true;
  document.querySelectorAll(BEHIND).forEach((node) => { node.inert = false; });
  const opener = dialog.opener;
  dialog.opener = null;
  // The list may have been redrawn since, so only return to a row still there.
  if (opener && document.contains(opener)) opener.focus({ preventScroll: true });
}

function closeDetails() {
  if (!dialog.open) return;
  hideDetails();
  if (dialog.pushed && history.state && history.state.details) {
    dialog.pushed = false;
    history.back();
  }
}

// One tap: the event goes to the chosen assistant. The text is also copied, so
// an app that opens without it only needs a paste.
// The navigation has to happen in the tap itself, before anything is awaited.
function askAi(name, card) {
  const target = AskAi.TARGETS[name];
  if (!target) return;
  const text = AskAi.prompt(card, placeText(card));
  const copied = copyText(text);
  if (AskAi.isAndroid(navigator.userAgent)) {
    window.location.href = AskAi.intentUrl(name, text);
  } else {
    window.open(AskAi.webUrl(name, text), '_blank', 'noopener,noreferrer');
  }
  copied.then((ok) => {
    toast(ok ? `Besedilo kopirano. Odpiram ${target.label} …` : `Odpiram ${target.label} …`);
  });
}

function wireDetails() {
  const overlay = el('details');
  // A drag that starts inside the dialog and ends outside it, such as selecting
  // text, would otherwise click the backdrop and close it.
  overlay.addEventListener('pointerdown', (event) => { dialog.pressedBackdrop = event.target === overlay; });
  overlay.addEventListener('click', (event) => {
    const close = event.target === overlay && dialog.pressedBackdrop;
    dialog.pressedBackdrop = false;
    if (close) closeDetails();
  });
  el('details-close').addEventListener('click', closeDetails);
  el('sheet').addEventListener('click', (event) => {
    const ai = event.target.closest('[data-ai]');
    if (ai && dialog.card) askAi(ai.dataset.ai, dialog.card);
    const pick = event.target.closest('[data-pick]');
    if (pick) pickFromDialog(pick.dataset.pick);
  });
  window.addEventListener('popstate', () => { dialog.pushed = false; hideDetails(); });

  overlay.addEventListener('keydown', (event) => {
    if (event.key !== 'Tab') return;
    const items = [...el('sheet').querySelectorAll('button, a[href]')]
      .filter((node) => !node.closest('[hidden]'));
    if (!items.length) return;
    const first = items[0];
    const last = items[items.length - 1];
    const inside = el('sheet').contains(document.activeElement) && document.activeElement !== el('sheet');
    if (event.shiftKey && (document.activeElement === first || !inside)) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });
}

/* --- saving from the static build --------------------------------------- */

function editorUrl(patch, file) {
  const repo = window.SWIPE_REPO;
  if (!repo || !repo.owner || !repo.repo) return null;
  const base = `https://github.com/${repo.owner}/${repo.repo}/new/${repo.branch || 'main'}`;
  const name = `?filename=${encodeURIComponent(file || repo.inbox || 'inbox/decisions.txt')}`;
  const full = `${base}${name}&value=${encodeURIComponent(patch)}`;
  return full.length <= URL_BUDGET ? full : `${base}${name}`;
}

// The clipboard API only exists on https and localhost. Over plain http on
// another address it is missing, so fall back to selecting a hidden field.
async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (error) { /* missing or refused: try the older way */ }
  const previous = document.activeElement;
  const field = document.createElement('textarea');
  field.value = text;
  field.setAttribute('readonly', '');
  field.style.cssText = 'position:fixed;top:0;left:0;opacity:0;pointer-events:none';
  document.body.appendChild(field);
  field.select();
  let copied = false;
  try { copied = document.execCommand('copy'); } catch (error) { copied = false; }
  field.remove();
  if (previous && previous.focus) previous.focus({ preventScroll: true });
  return copied;
}

// The whole button is the target: the text and the icon copy the ID alike.
function idButton(id) {
  const node = el('copy-id-template').content.firstElementChild.cloneNode(true);
  node.querySelector('.copy-id-text').textContent = id;
  let timer = null;
  node.addEventListener('click', async () => {
    const copied = await copyText(id);
    toast(copied ? `ID kopiran: ${id}` : 'Kopiranje ni uspelo.', !copied);
    if (!copied) return;
    node.classList.add('is-copied');
    clearTimeout(timer);
    timer = setTimeout(() => node.classList.remove('is-copied'), 1400);
  });
  return node;
}

// Open the GitHub editor with the patch prefilled, then show the screen that
// says what to click. False when the repository is unknown and the patch was
// only copied.
async function handOff(patch, file, screen, words) {
  const url = editorUrl(patch, file);
  if (!url) {
    const copied = await copyText(patch);
    toast(copied ? `${words.copied} Prilepi jih v repo.`
      : 'Repozitorij ni znan. Uporabi gumb za kopiranje.', true);
    return false;
  }
  // A link without the content prefilled means the batch outgrew the URL.
  if (!url.includes('&value=')) {
    const copied = await copyText(patch);
    toast(copied ? `${words.tooMany} Prilepi jih v urejevalnik.`
      : `${words.tooMany} Uporabi gumb za kopiranje.`, true);
  }
  window.open(url, '_blank', 'noopener');
  el(screen).hidden = false;
  watchUntil = Date.now() + WATCH_MS;
  return true;
}

// Start the workflow with this device's token. False when there is no token or
// GitHub turned the call down, and the caller then uses the editor instead.
async function sendPatch(kind, patch) {
  if (!dispatcher.enabled()) return false;
  st.sending = true;
  renderPending();
  let result;
  try {
    result = await dispatcher.send(kind, patch);
  } finally {
    st.sending = false;
  }
  if (result.ok) {
    watchUntil = Date.now() + WATCH_MS;
    return true;
  }
  toast(`${result.message} Odpiram urejevalnik.`, true);
  renderQuick();
  return false;
}

async function save() {
  if (!store.pending || st.sending) return;
  const { count, patch } = store.pending();
  if (!count) return;
  if (await sendPatch('decisions', patch)) {
    st.sent = patch;
    renderPending();
    toast('Poslano. Baza se osveži v približno minuti.');
    return;
  }
  renderPending();
  await handOff(patch, null, 'handoff', {
    copied: 'Odločitve so kopirane.', tooMany: 'Preveč odločitev za povezavo.',
  });
}

/* --- this device's token -------------------------------------------------- */

async function rememberToken() {
  const field = el('quick-token');
  const button = el('quick-on');
  if (!field.value.trim() || button.disabled) return;
  button.disabled = true;
  button.textContent = 'Preverjam …';
  try {
    const result = await dispatcher.remember(field.value);
    if (!result.ok) {
      toast(result.message, true);
      return;
    }
    field.value = '';
    toast('Hitro shranjevanje je vklopljeno.');
  } finally {
    button.disabled = false;
    button.textContent = 'Vklopi';
    renderQuick();
    renderPending();
  }
}

function forgetToken() {
  const done = dispatcher.forget();
  toast(done ? 'Žeton je odstranjen s te naprave. Na GitHubu ga lahko še prekličeš.'
    : 'Žetona ni bilo mogoče odstraniti.', !done);
  renderQuick();
  renderPending();
}

function wireQuick() {
  el('quick-on').addEventListener('click', rememberToken);
  el('quick-off').addEventListener('click', forgetToken);
  el('quick-token').addEventListener('keydown', (event) => {
    if (event.key === 'Enter') { event.preventDefault(); rememberToken(); }
  });
}

/* --- hiding every rejected event (static build only) --------------------- */

const confirmation = { open: false, pushed: false, pressedBackdrop: false };

function rejectedIds() {
  return st.data ? st.data.groups.rejected.map((card) => card.event_id) : [];
}

function openConfirm() {
  if (confirmation.open || dialog.open || st.busy) return;
  const rows = st.data.groups.rejected;
  if (!rows.length) return;
  const unsaved = rows.filter((card) => card.unsaved).length;
  el('hide-count').textContent = String(rows.length);
  const note = el('hide-unsaved');
  note.hidden = unsaved === 0;
  note.textContent = unsaved ? `Od tega neshranjenih: ${unsaved}. Skrijejo se vseeno.` : '';
  confirmation.open = true;
  confirmation.pressedBackdrop = false;
  el('hide-confirm').hidden = false;
  document.querySelectorAll(BEHIND).forEach((node) => { node.inert = true; });
  try {
    history.pushState({ confirm: true }, '');
    confirmation.pushed = true;
  } catch (error) {
    confirmation.pushed = false;
  }
  el('hide-cancel').focus({ preventScroll: true });
}

function hideConfirm() {
  if (!confirmation.open) return;
  confirmation.open = false;
  el('hide-confirm').hidden = true;
  document.querySelectorAll(BEHIND).forEach((node) => { node.inert = false; });
  if (!el('hide-fab').hidden) el('hide-fab').focus({ preventScroll: true });
}

function closeConfirm() {
  if (!confirmation.open) return;
  hideConfirm();
  if (confirmation.pushed && history.state && history.state.confirm) {
    confirmation.pushed = false;
    history.back();
  }
}

async function confirmHide() {
  const ids = rejectedIds();
  closeConfirm();
  if (!ids.length) return;
  const { patch, name } = Snapshot.hidePatch(ids);
  if (await sendPatch('hide', patch)) {
    st.hiding = ids;
    toast('Poslano. Dogodki se skrijejo v približno minuti.');
    return;
  }
  const repo = window.SWIPE_REPO || {};
  const folder = (repo.hide_inbox || 'inbox/hide').replace(/\/+$/, '');
  const opened = await handOff(patch, `${folder}/${name}`, 'hide-handoff', {
    copied: 'ID-ji so kopirani.', tooMany: 'Preveč dogodkov za povezavo.',
  });
  if (opened) st.hiding = ids;
}

function wireConfirm() {
  const overlay = el('hide-confirm');
  el('hide-fab').addEventListener('click', openConfirm);
  el('hide-cancel').addEventListener('click', closeConfirm);
  el('hide-ok').addEventListener('click', confirmHide);
  el('hide-handoff-close').addEventListener('click', () => { el('hide-handoff').hidden = true; });
  overlay.addEventListener('pointerdown', (event) => { confirmation.pressedBackdrop = event.target === overlay; });
  overlay.addEventListener('click', (event) => {
    const close = event.target === overlay && confirmation.pressedBackdrop;
    confirmation.pressedBackdrop = false;
    if (close) closeConfirm();
  });
  window.addEventListener('popstate', () => { confirmation.pushed = false; hideConfirm(); });

  overlay.addEventListener('keydown', (event) => {
    if (event.key !== 'Tab') return;
    const items = [...el('hide-sheet').querySelectorAll('button')];
    const first = items[0];
    const last = items[items.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });
}

// Which of the events handed over are still in the snapshot. Once none is, the
// database has hidden them and there is nothing left to wait for.
function stillListed(ids) {
  const shown = new Set(st.raw.deck.map((card) => card.event_id));
  Object.values(st.raw.groups).forEach((rows) => rows.forEach((card) => shown.add(card.event_id)));
  return ids.filter((id) => shown.has(id));
}

/* --- waiting for the rebuilt snapshot ----------------------------------- */

// Look for a newer snapshot and redraw only if there is one. Never while a card
// is being dragged or a dialog is open, since redrawing would pull them away.
async function checkSnapshot() {
  if (!store.poll || !st.raw || st.busy || st.dragging || dialog.open || confirmation.open
    || document.hidden) return;
  try {
    const data = await store.poll();
    if (data) {
      setData(data);
      if (st.hiding.length) st.hiding = stillListed(st.hiding);
      render();
    }
  } catch (error) {
    /* offline or mid-deploy: the next check tries again */
  }
}

// Something is still on its way into the database: a staged decision, or events
// handed to GitHub to be hidden.
function awaitingGithub() {
  return Boolean(st.hiding.length || (store.pending && store.pending().count));
}

function watchForSnapshot() {
  setInterval(() => {
    if (Date.now() < watchUntil && awaitingGithub()) checkSnapshot();
    // Brings the save button back once the watch window has run out.
    renderPending();
  }, POLL_MS);
}

/* --- chrome ------------------------------------------------------------- */

let toastTimer = null;

function toast(text, bad) {
  const node = el('toast');
  node.textContent = text;
  node.classList.toggle('is-bad', Boolean(bad));
  node.classList.add('is-on');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => node.classList.remove('is-on'), bad ? 4500 : 2100);
}

function setView(name) {
  if (name !== 'review') setSelecting(false);
  st.view = name;
  document.body.dataset.view = name;
  el('view-swipe').hidden = name !== 'swipe';
  el('view-review').hidden = name !== 'review';
  el('view-info').hidden = name !== 'info';
  document.querySelectorAll('.tab').forEach((tab) => {
    tab.classList.toggle('is-on', tab.dataset.view === name);
  });
  renderFab();
}

function wire() {
  document.querySelectorAll('[data-decide]').forEach((button) => {
    button.addEventListener('click', () => decideTop(button.dataset.decide));
  });
  document.querySelectorAll('[data-view]').forEach((button) => {
    button.addEventListener('click', () => setView(button.dataset.view));
  });
  document.querySelectorAll('[data-seg]').forEach((button) => {
    button.addEventListener('click', () => pickSegment(button.dataset.seg));
  });
  el('undo').addEventListener('click', undo);

  el('save').addEventListener('click', save);
  el('discard').addEventListener('click', discardPending);
  el('copy').addEventListener('click', async () => {
    const { count, patch } = store.pending ? store.pending() : { count: 0 };
    if (!count) return;
    const copied = await copyText(patch);
    toast(copied ? 'Odločitve so kopirane.' : 'Kopiranje ni uspelo.', !copied);
  });
  el('handoff-close').addEventListener('click', () => { el('handoff').hidden = true; });
  wireQuick();
  wireFilters();
  wireSelection();

  wireDetails();
  wireConfirm();

  // Coming back to the app on a later day must not keep showing yesterday's events.
  document.addEventListener('visibilitychange', () => {
    if (document.hidden || !st.raw || st.busy) return;
    // Back from the GitHub tab: the rebuilt snapshot may be ready by now.
    if (awaitingGithub()) checkSnapshot();
    if (Days.today() !== st.data.today) {
      setData(st.raw);
      render();
    }
  });

  document.addEventListener('keydown', (event) => {
    if (confirmation.open) {
      if (event.key === 'Escape') { event.preventDefault(); closeConfirm(); }
      return;
    }
    if (dialog.open) {
      if (event.key === 'Escape') { event.preventDefault(); closeDetails(); }
      return;
    }
    if (event.key === 'Escape' && st.selecting && st.view === 'review') {
      event.preventDefault();
      endSelecting();
      return;
    }
    if (event.altKey || event.metaKey) return;
    if (event.target.closest('input, textarea')) return;
    const key = event.key;
    if (key === 'z' || key === 'Z') { event.preventDefault(); undo(); return; }
    if (event.ctrlKey) return;
    if (st.view !== 'swipe') return;
    if (key === 'ArrowRight') { event.preventDefault(); decideTop('interested'); }
    else if (key === 'ArrowLeft') { event.preventDefault(); decideTop('rejected'); }
    else if (key === 'ArrowDown') { event.preventDefault(); decideTop('maybe'); }
  });
}

// A reload with the dialog open leaves its history entry behind. Drop the
// marker, so the first back gesture is not spent on a dialog that is not there.
try {
  if (history.state && (history.state.details || history.state.confirm)) history.replaceState(null, '');
} catch (error) { /* history is optional */ }

wire();
watchForSnapshot();
setView('swipe');
refresh().catch((error) => toast(error.message, true));
