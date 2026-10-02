'use strict';

/* The deployed build ships a baked snapshot. Decisions are staged in this
   browser, and saving hands them to GitHub to be written into db.json. */

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
  renderPending();
  renderStack(options);
  renderList();
}

function isoToSi(iso) {
  return iso ? `${iso.slice(8, 10)}.${iso.slice(5, 7)}.${iso.slice(0, 4)}` : '?';
}

// The facts about the data that the deck has no room for: when the last sweep
// ran, how far it looks ahead, what today is and how much is left out.
function renderStats() {
  const { clock, counts, free, today } = st.data;
  el('st-run').textContent = `${clock.date} ${clock.time}`;
  el('st-window').textContent = clock.horizon;
  el('st-today').textContent = isoToSi(today);
  el('st-total').textContent = String(counts.total);
  el('st-free').textContent = String(free);
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
  const { count } = store.pending();
  const banner = el('pending');
  banner.hidden = count === 0;
  if (count) el('pending-text').textContent = pendingPhrase(count);
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

  const source = node.querySelector('[data-f="url"]');
  if (card.url) source.href = card.url;
  else source.hidden = true;

  node.querySelectorAll('[data-move]').forEach((button) => {
    const target = button.dataset.move;
    button.classList.toggle('is-on', target === card.decision);
    // Sending an undecided event "back to the deck" would change nothing.
    if (target === '') button.hidden = !card.decision;
    button.addEventListener('click', () => move(card, target));
  });

  // The title is a real button, so keyboard and screen-reader users can open
  // the dialog. A tap anywhere else on the row opens it too, unless it landed
  // on a control of its own or finished a text selection.
  const opener = node.querySelector('.row-title');
  node.addEventListener('click', (event) => {
    const control = event.target.closest('a, button');
    if (control && control !== opener) return;
    if (String(window.getSelection && window.getSelection()).length) return;
    openDetails(card, opener);
  });
  return node;
}

// The button hides every event in the Zavrnjeno list. Writing needs the
// repository, so it only shows on that list.
function renderFab() {
  const shown = st.view === 'review' && st.seg === 'rejected'
    && Boolean(st.data) && st.data.groups.rejected.length > 0;
  el('hide-fab').hidden = !shown;
  el('list').classList.toggle('has-fab', shown);
}

function renderList() {
  document.querySelectorAll('.seg').forEach((seg) => {
    seg.classList.toggle('is-on', seg.dataset.seg === st.seg);
  });
  renderFab();
  list.textContent = '';
  const rows = st.seg === 'undecided' ? st.data.deck : (st.data.groups[st.seg] || []);
  if (!rows.length) {
    const empty = document.createElement('p');
    empty.className = 'list-empty';
    empty.textContent = st.seg === 'undecided'
      ? 'Vsi dogodki so razvrščeni.'
      : `V kategoriji "${labelOf(st.seg)}" še ni dogodkov.`;
    list.appendChild(empty);
    return;
  }
  let month = null;
  rows.forEach((card) => {
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

async function move(card, target) {
  if (st.busy) return;
  if (target === card.decision) return;
  st.busy = true;
  try {
    setData(target ? await store.decide(card.event_id, target) : await store.clear(card.event_id));
    render();
    toast(target ? `${labelOf(target)}: ${card.title}` : `Nazaj v kup: ${card.title}`);
  } catch (error) {
    toast(error.message, true);
  } finally {
    st.busy = false;
  }
}

/* --- details dialog ------------------------------------------------------ */

const dialog = { open: false, opener: null, pushed: false, pressedBackdrop: false, card: null };
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
}

function openDetails(card, opener) {
  if (dialog.open) return;
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
// an app that opens without it (Gemini has no prefill) only needs a paste.
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
    const button = event.target.closest('[data-ai]');
    if (button && dialog.card) askAi(button.dataset.ai, dialog.card);
  });
  window.addEventListener('popstate', () => { dialog.pushed = false; hideDetails(); });

  overlay.addEventListener('keydown', (event) => {
    if (event.key !== 'Tab') return;
    const items = [...el('sheet').querySelectorAll('button, a[href]')].filter((node) => !node.hidden);
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

async function save() {
  if (!store.pending) return;
  const { count, patch } = store.pending();
  if (!count) return;
  await handOff(patch, null, 'handoff', {
    copied: 'Odločitve so kopirane.', tooMany: 'Preveč odločitev za povezavo.',
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
  st.view = name;
  document.body.dataset.view = name;
  el('view-swipe').hidden = name !== 'swipe';
  el('view-review').hidden = name !== 'review';
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
    button.addEventListener('click', () => { st.seg = button.dataset.seg; renderList(); });
  });
  el('undo').addEventListener('click', undo);

  el('save').addEventListener('click', save);
  el('copy').addEventListener('click', async () => {
    const { count, patch } = store.pending ? store.pending() : { count: 0 };
    if (!count) return;
    const copied = await copyText(patch);
    toast(copied ? 'Odločitve so kopirane.' : 'Kopiranje ni uspelo.', !copied);
  });
  el('handoff-close').addEventListener('click', () => { el('handoff').hidden = true; });

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
