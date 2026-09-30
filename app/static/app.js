'use strict';

/* One UI over two backends, chosen by mode.js.
   server: every decision is a round trip, so db.json is the only state.
   static: the deployed build ships a baked snapshot, decisions are staged in
   this browser, and saving hands them to GitHub to be written into db.json. */

const THRESHOLD_X = 96;   // horizontal pixels before a swipe counts
const THRESHOLD_Y = 112;  // downward pixels before "mogoče" counts
const FLY_MS = 230;
const URL_BUDGET = 6000;  // a prefilled GitHub editor link has to stay openable

const el = (id) => document.getElementById(id);
const phone = el('phone');
const stack = el('stack');
const list = el('list');

const st = { data: null, view: 'swipe', seg: 'interested', busy: false, stopped: false };

const sleep = (ms) => new Promise((done) => setTimeout(done, ms));
const labelOf = (name) => (st.data && st.data.labels[name]) || name;

/* --- backends ----------------------------------------------------------- */

async function request(path, body) {
  const options = body === undefined
    ? { headers: { Accept: 'application/json' } }
    : { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) };
  let response;
  try {
    response = await fetch(path, options);
  } catch (error) {
    throw new Error('Strežnik se ne odziva. Je aplikacija še zagnana?');
  }
  const data = await response.json().catch(() => ({ ok: false, error: 'Neveljaven odgovor strežnika' }));
  if (!response.ok || !data.ok) throw new Error(data.error || `Napaka ${response.status}`);
  return data;
}

function serverStore() {
  return {
    live: true,
    load: async () => (await request('/api/state')).state,
    decide: async (id, category) => (await request('/api/decide', { event_id: id, category })).state,
    clear: async (id) => (await request('/api/clear', { event_id: id })).state,
    undo: async () => (await request('/api/undo', {})).state,
    quit: () => request('/api/quit', {}),
  };
}

function staticStore() {
  const KEY = 'kids-activities-decisions-v1';
  const CODES = { interested: 'i', maybe: 'm', rejected: 'r' };
  let baked = null;
  let log = [];

  const known = (value) => value === null || Object.prototype.hasOwnProperty.call(CODES, value);

  function valid(entry) {
    return entry && typeof entry.event_id === 'string' && entry.event_id
      && (entry.action === 'set' || entry.action === 'clear')
      && known(entry.after === undefined ? null : entry.after)
      && known(entry.before === undefined ? null : entry.before);
  }

  function readLog() {
    // Browser storage is a staging area, not a record: an unreadable or
    // tampered value is dropped rather than trusted or reported as state.
    try {
      const parsed = JSON.parse(localStorage.getItem(KEY) || '[]');
      return Array.isArray(parsed) ? parsed.filter(valid) : [];
    } catch (error) {
      return [];
    }
  }

  function writeLog() {
    try {
      localStorage.setItem(KEY, JSON.stringify(log));
    } catch (error) {
      toast('Brskalnik ne shranjuje. Odločitve veljajo le do osvežitve.', true);
    }
  }

  function wanted() {
    const map = new Map();
    log.forEach((entry) => map.set(entry.event_id, entry.after || null));
    return map;
  }

  function reconcile() {
    // Anything the database already agrees with, or no longer holds, stops
    // being pending. That is what makes the save round trip self-clearing.
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
      const response = await fetch('state.json', { headers: { Accept: 'application/json' } })
        .catch(() => { throw new Error('Posnetka baze ni bilo mogoče naložiti.'); });
      if (!response.ok) throw new Error(`Posnetek baze ni dosegljiv (${response.status}).`);
      baked = await response.json();
      log = readLog();
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

const store = window.SWIPE_MODE === 'static' ? staticStore() : serverStore();

async function refresh(options) {
  st.data = await store.load();
  render(options);
}

/* --- rendering ---------------------------------------------------------- */

function render(options) {
  if (!st.data) return;
  const counts = st.data.counts;
  const clock = st.data.clock;

  el('clock').textContent =
    `Rutina ${clock.date} ${clock.time} · okno do ${clock.horizon}`;
  document.querySelectorAll('[data-count]').forEach((node) => {
    node.textContent = counts[node.dataset.count];
  });
  el('tab-left').textContent = counts.undecided;
  el('tab-done').textContent = counts.decided;
  const share = counts.total ? Math.round((counts.decided / counts.total) * 100) : 0;
  el('progress-fill').style.width = `${share}%`;
  el('progress').setAttribute('aria-valuenow', String(counts.decided));
  el('progress').setAttribute('aria-valuemax', String(counts.total));

  document.querySelectorAll('[data-decide]').forEach((button) => {
    button.disabled = counts.undecided === 0;
  });
  const undoInfo = st.data.undo;
  const undoButton = el('undo');
  undoButton.disabled = !undoInfo.available;
  undoButton.title = undoInfo.available
    ? `Razveljavi: ${undoInfo.title} → ${undoInfo.restores} (Z)`
    : store.live ? 'Ni česa razveljaviti' : 'Razveljavi se le še neshranjene odločitve';

  el('hint').textContent = counts.undecided
    ? `${counts.undecided} še za odločitev · povleci kartico ali ← ↓ → · Z razveljavi`
    : 'Kup je prazen · Z razveljavi zadnjo odločitev';
  el('done-text').textContent = counts.total
    ? `Vseh ${counts.total} dogodkov je razvrščenih.`
    : 'V bazi ni aktivnih dogodkov.';

  renderPending();
  renderStack(options);
  renderList();
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
  if (count) el('pending-text').textContent = `${pendingPhrase(count)} na vpis v db.json`;
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
  fill(node, 'glyph', card.category.replace(/_/g, ' '));
  fill(node, 'age', card.age);
  fill(node, 'event_id', card.event_id);
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

function renderList() {
  document.querySelectorAll('.seg').forEach((seg) => {
    seg.classList.toggle('is-on', seg.dataset.seg === st.seg);
  });
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

  node.addEventListener('pointerdown', (event) => {
    if (st.busy || pointer !== null) return;
    if (event.target.closest('a, button')) return;
    if (event.pointerType === 'mouse' && event.button !== 0) return;
    pointer = event.pointerId;
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
    const reading = vector(dx, dy);
    if (reading.dir && reading.p >= 1) commit(reading.dir, node, card);
    else springBack(node);
  };

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
    st.data = state;
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
    st.data = await store.undo();
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
    st.data = target ? await store.decide(card.event_id, target) : await store.clear(card.event_id);
    render();
    toast(target ? `${labelOf(target)}: ${card.title}` : `Nazaj v kup: ${card.title}`);
  } catch (error) {
    toast(error.message, true);
  } finally {
    st.busy = false;
  }
}

/* --- details dialog ------------------------------------------------------ */

const dialog = { open: false, opener: null, pushed: false };
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
  const [main, note] = Array.isArray(content) ? content : [content, ''];
  const term = document.createElement('dt');
  term.textContent = label;
  const detail = document.createElement('dd');
  if (className) detail.className = className;
  detail.textContent = main;
  if (note) {
    const small = document.createElement('small');
    small.textContent = note;
    detail.appendChild(small);
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
  fact(facts, 'ID', card.event_id, 'is-mono');

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
  dialog.open = true;
  dialog.opener = opener;
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

function wireDetails() {
  const overlay = el('details');
  let pressedBackdrop = false;
  // A drag that starts inside the dialog and ends outside it, such as selecting
  // text, would otherwise click the backdrop and close it.
  overlay.addEventListener('pointerdown', (event) => { pressedBackdrop = event.target === overlay; });
  overlay.addEventListener('click', (event) => {
    if (event.target === overlay && pressedBackdrop) closeDetails();
  });
  el('details-close').addEventListener('click', closeDetails);
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

function editorUrl(patch) {
  const repo = window.SWIPE_REPO;
  if (!repo || !repo.owner || !repo.repo) return null;
  const base = `https://github.com/${repo.owner}/${repo.repo}/new/${repo.branch || 'main'}`;
  const name = `?filename=${encodeURIComponent(repo.inbox || 'inbox/decisions.txt')}`;
  const full = `${base}${name}&value=${encodeURIComponent(patch)}`;
  return full.length <= URL_BUDGET ? full : `${base}${name}`;
}

async function copyPatch(patch) {
  try {
    await navigator.clipboard.writeText(patch);
    return true;
  } catch (error) {
    return false;
  }
}

async function save() {
  if (!store.pending) return;
  const { count, patch } = store.pending();
  if (!count) return;
  const url = editorUrl(patch);
  if (!url) {
    const copied = await copyPatch(patch);
    toast(copied ? 'Odločitve so kopirane. Prilepi jih v repo.'
      : 'Repozitorij ni znan. Uporabi gumb za kopiranje.', true);
    return;
  }
  // A link without the content prefilled means the batch outgrew the URL.
  if (!url.includes('&value=')) {
    const copied = await copyPatch(patch);
    toast(copied ? 'Preveč odločitev za povezavo. Prilepi jih v urejevalnik.'
      : 'Preveč odločitev za povezavo. Uporabi gumb za kopiranje.', true);
  }
  window.open(url, '_blank', 'noopener');
  el('handoff').hidden = false;
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
  document.querySelectorAll('[data-jump]').forEach((button) => {
    button.addEventListener('click', () => {
      st.seg = button.dataset.jump;
      setView('review');
      renderList();
    });
  });
  el('undo').addEventListener('click', undo);

  if (store.quit) {
    el('quit').addEventListener('click', async () => {
      if (!window.confirm('Končam aplikacijo? Vse odločitve so že shranjene.')) return;
      st.stopped = true;
      try { await store.quit(); } catch (error) { /* the socket may close first */ }
      el('curtain').hidden = false;
    });
  } else {
    el('quit').hidden = true;
  }

  el('save').addEventListener('click', save);
  el('copy').addEventListener('click', async () => {
    const { count, patch } = store.pending ? store.pending() : { count: 0 };
    if (!count) return;
    const copied = await copyPatch(patch);
    toast(copied ? 'Odločitve so kopirane.' : 'Kopiranje ni uspelo.', !copied);
  });
  el('handoff-close').addEventListener('click', () => { el('handoff').hidden = true; });

  wireDetails();

  document.addEventListener('keydown', (event) => {
    if (dialog.open) {
      if (event.key === 'Escape') { event.preventDefault(); closeDetails(); }
      return;
    }
    if (st.stopped || event.altKey || event.metaKey) return;
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
  if (history.state && history.state.details) history.replaceState(null, '');
} catch (error) { /* history is optional */ }

wire();
setView('swipe');
refresh().catch((error) => toast(error.message, true));
