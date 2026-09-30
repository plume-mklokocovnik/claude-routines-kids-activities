'use strict';

/* Swipe UI over /api. Every decision is a server round trip, so the database is
   the only source of truth: reloading the page, or stopping the app mid-deck,
   never loses or invents a decision. */

const THRESHOLD_X = 96;   // horizontal pixels before a swipe counts
const THRESHOLD_Y = 112;  // downward pixels before "mogoče" counts
const FLY_MS = 230;

const el = (id) => document.getElementById(id);
const phone = el('phone');
const stack = el('stack');
const list = el('list');

const st = { data: null, view: 'swipe', seg: 'interested', busy: false, stopped: false };

const sleep = (ms) => new Promise((done) => setTimeout(done, ms));
const labelOf = (name) => (st.data && st.data.labels[name]) || name;

/* --- server ------------------------------------------------------------- */

async function api(path, body) {
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

async function refresh(options) {
  const data = await api('/api/state');
  st.data = data.state;
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
    : 'Ni česa razveljaviti';

  el('hint').textContent = counts.undecided
    ? `${counts.undecided} še za odločitev · povleci kartico ali ← ↓ → · Z razveljavi`
    : 'Kup je prazen · Z razveljavi zadnjo odločitev';
  el('done-text').textContent = counts.total
    ? `Vseh ${counts.total} dogodkov je razvrščenih.`
    : 'V bazi ni aktivnih dogodkov.';

  renderStack(options);
  renderList();
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

  node.querySelector('[data-f="starred"]').hidden = !card.starred;
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
  fill(node, 'title', `${card.starred ? '⭐ ' : ''}${card.title}`);
  fill(node, 'place', placeText(card));
  const extra = [card.category, `${card.age} let`, priceText(card)];
  if (card.status !== 'active') extra.push(card.status === 'expired' ? 'poteklo' : 'skrito');
  fill(node, 'meta', extra.concat(card.notes).join(' · '));

  const source = node.querySelector('[data-f="url"]');
  if (card.url) source.href = card.url;
  else source.hidden = true;

  node.querySelectorAll('[data-move]').forEach((button) => {
    const target = button.dataset.move;
    button.classList.toggle('is-on', target === card.decision);
    button.addEventListener('click', () => move(card, target));
  });
  return node;
}

function renderList() {
  document.querySelectorAll('.seg').forEach((seg) => {
    seg.classList.toggle('is-on', seg.dataset.seg === st.seg);
  });
  list.textContent = '';
  const rows = st.data.groups[st.seg] || [];
  if (!rows.length) {
    const empty = document.createElement('p');
    empty.className = 'list-empty';
    empty.textContent = `V kategoriji "${labelOf(st.seg)}" še ni dogodkov.`;
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
    const [response] = await Promise.all([
      api('/api/decide', { event_id: card.event_id, category: dir }),
      sleep(FLY_MS),
    ]);
    st.data = response.state;
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
    const response = await api('/api/undo', {});
    st.data = response.state;
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
    const response = target
      ? await api('/api/decide', { event_id: card.event_id, category: target })
      : await api('/api/clear', { event_id: card.event_id });
    st.data = response.state;
    render();
    toast(target ? `${labelOf(target)}: ${card.title}` : `Nazaj v kup: ${card.title}`);
  } catch (error) {
    toast(error.message, true);
  } finally {
    st.busy = false;
  }
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

  el('quit').addEventListener('click', async () => {
    if (!window.confirm('Končam aplikacijo? Vse odločitve so že shranjene.')) return;
    st.stopped = true;
    try { await api('/api/quit', {}); } catch (error) { /* the socket may close first */ }
    el('curtain').hidden = false;
  });

  document.addEventListener('keydown', (event) => {
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

wire();
setView('swipe');
refresh().catch((error) => toast(error.message, true));
