'use strict';
// Shared by every board and the item page: dates, states, icons, media figures and the tooltip.
// build.py writes `const PLAN = {...}` (from plan.json) and `const MEDIA = {...}` (from
// media/media.json) ahead of this file, so everything below may read them.
const DESIGNS = {};
const APP = { refresh() {}, design: 'moodboard', artifactUrl: '' };

const MS = 864e5;
const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const DOW = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const parse = s => { const [y, m, d] = s.split('-').map(Number); return Date.UTC(y, m - 1, d || 1); };
const iso = t => new Date(t).toISOString().slice(0, 10);
const diff = (a, b) => Math.round((parse(b) - parse(a)) / MS);
const fmt = (s, year) => { const t = new Date(parse(s)); return `${t.getUTCDate()} ${MON[t.getUTCMonth()]}${year ? ' ' + t.getUTCFullYear() : ''}`; };
const fmtDow = s => { const t = new Date(parse(s)); return `${DOW[t.getUTCDay()]} ${t.getUTCDate()} ${MON[t.getUTCMonth()]}`; };
const nextMonth = t => { const d = new Date(t); return Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + 1, 1); };
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

const STATE = { late: 'Overdue', now: 'Do now', waiting: 'Waiting', later: 'Upcoming', idea: 'Idea', done: 'Done' };
const STATE_ICON = { late: 'alert', now: 'clock', waiting: 'hourglass', later: 'calendar', idea: 'sparkle', done: 'check' };
const ORDER = Object.keys(STATE);
const planStates = () => PLAN.states ?? ORDER;
const groupOf = id => PLAN.groups.find(g => g.id === id) ?? { id: '', name: '', icon: 'list' };
const findItem = id => PLAN.items.find(i => i.id === id);
const dueText = it => it.dueLabel ?? (it.due ? fmt(it.due) : 'No date');
const daysToGo = () => diff(PLAN.asOf, PLAN.event.start);
const dateOf = it => it.due ?? it.start;
// The days a timeline must cover: every dated item, today and the event.
function planSpan() {
  const ds = [PLAN.from ?? PLAN.asOf, PLAN.asOf, PLAN.event.start, PLAN.event.end, ...PLAN.items.flatMap(i => [i.due, i.start, i.end])].filter(Boolean).map(parse);
  return { t0: Math.min(...ds), t1: Math.max(...ds) };
}
const openDecisions = () => PLAN.items.filter(i => i.decision?.status === 'open');
const byDue = (a, b) =>
  (a.due ? parse(a.due) : Infinity) - (b.due ? parse(b.due) : Infinity) || ORDER.indexOf(a.state) - ORDER.indexOf(b.state);

// 24px stroke icons. Name an icon by its key; an unknown key falls back to `info`.
const ICONS = {
  flag: 'M5 21V4 M5 4h12l-2 4 2 4H5',
  diamond: 'M12 3l9 9-9 9-9-9z',
  layers: 'M12 3l9 5-9 5-9-5z M3 13l9 5 9-5',
  columns: 'M3 4h5v16H3z M10 4h5v10h-5z M17 4h4v13h-4z',
  calendar: 'M3 6h18v15H3z M3 10h18 M8 3v5 M16 3v5',
  users: 'M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z M2 21v-1a6 6 0 0 1 12 0v1 M16 3.5a4 4 0 0 1 0 7.5 M18 14a5 5 0 0 1 4 5v2',
  bed: 'M2 19V5 M2 15h20 M22 19v-6a3 3 0 0 0-3-3H10v5 M6.5 12.5a2 2 0 1 0 0-4 2 2 0 0 0 0 4z',
  sofa: 'M4 11V8a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3v3 M2 13a2 2 0 0 1 4 0v2h12v-2a2 2 0 0 1 4 0v5H2z M5 18v2 M19 18v2',
  utensils: 'M5 3v8a2 2 0 0 0 2 2v8 M9 3v8a2 2 0 0 1-2 2 M7 3v6 M17 21V3c-2 1-3 4-3 7v3h3',
  crown: 'M3 8l4 4 5-7 5 7 4-4-2 11H5z',
  phone: 'M7 2h10v20H7z M11 18h2',
  search: 'M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14z M21 21l-5-5',
  list: 'M9 6h12 M9 12h12 M9 18h12 M4 6h.01 M4 12h.01 M4 18h.01',
  crab: 'M6 14a6 4 0 1 0 12 0a6 4 0 1 0-12 0 M8 11L5 6l3-1 M16 11l3-5-3-1 M6 15l-3 1 M6 13l-3-1 M18 15l3 1 M18 13l3-1 M10 12h.01 M14 12h.01',
  moon: 'M20 14A8 8 0 1 1 10 4a6 6 0 0 0 10 10z',
  camera: 'M3 7h4l2-3h6l2 3h4v13H3z M12 17a4 4 0 1 0 0-8 4 4 0 0 0 0 8z',
  video: 'M3 6h12v12H3z M15 10l6-3v10l-6-3z',
  pin: 'M12 22s7-7 7-12a7 7 0 0 0-14 0c0 5 7 12 7 12z M12 12a2 2 0 1 0 0-4 2 2 0 0 0 0 4z',
  wallet: 'M3 7h18v13H3z M3 7l13-4v4 M16 13h3',
  ticket: 'M3 7h18v3a2 2 0 0 0 0 4v3H3v-3a2 2 0 0 0 0-4z M14 7v10',
  clock: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z M12 7v5l3 2',
  hourglass: 'M6 3h12 M6 21h12 M7 3c0 5 5 6 5 9s-5 4-5 9 M17 3c0 5-5 6-5 9s5 4 5 9',
  check: 'M5 12l5 5 9-10',
  alert: 'M12 3l10 18H2z M12 10v4 M12 17h.01',
  mail: 'M3 5h18v14H3z M3 6l9 7 9-7',
  ring: 'M12 21a6 6 0 1 0 0-12 6 6 0 0 0 0 12z M9 4h6l-3 5z',
  suit: 'M8 3l4 4 4-4 4 3v15H4V6z M12 7v14 M8 11l2 2',
  dress: 'M9 3h6l-1 5 5 13H5l5-13z',
  car: 'M3 16v-4l2-5h14l2 5v4z M3 16v3h3v-3 M18 16v3h3v-3 M7 13h.01 M17 13h.01',
  flower: 'M12 22V12 M12 12c-4 0-6-3-6-7l3 2 3-4 3 4 3-2c0 4-2 7-6 7z M12 18c-2-2-5-2-6-1 M12 18c2-2 5-2 6-1',
  mic: 'M9 3h6v10a3 3 0 0 1-6 0z M5 11a7 7 0 0 0 14 0 M12 18v3',
  music: 'M9 18V5l11-2v13 M9 18a3 3 0 1 1-6 0 3 3 0 0 1 6 0z M20 16a3 3 0 1 1-6 0 3 3 0 0 1 6 0z',
  tea: 'M4 9h12v5a6 6 0 0 1-12 0z M16 10h2a2 2 0 0 1 0 4h-2 M8 3c0 2 2 2 2 4 M12 3c0 2 2 2 2 4',
  heart: 'M12 20s-8-5-8-11a4.5 4.5 0 0 1 8-2.5A4.5 4.5 0 0 1 20 9c0 6-8 11-8 11z',
  chart: 'M4 20V10 M10 20V4 M16 20v-7 M3 20h18',
  link: 'M10 14a4 4 0 0 0 6 0l3-3a4 4 0 0 0-6-6l-1 1 M14 10a4 4 0 0 0-6 0l-3 3a4 4 0 0 0 6 6l1-1',
  sparkle: 'M12 3l2 6 6 2-6 2-2 6-2-6-6-2 6-2z',
  plane: 'M10 14l-7-3 1-2 9 1 5-7h2l-2 8 6 2v2l-7-1-3 6h-2l1-6z',
  home: 'M3 11l9-8 9 8 M5 9v12h14V9 M10 21v-6h4v6',
  building: 'M4 21V3h11v18 M15 9h5v12 M8 7h3 M8 11h3 M8 15h3 M2 21h20',
  table: 'M12 15a7 3 0 1 0 0-6 7 3 0 0 0 0 6z M12 15v6 M8 21h8',
  film: 'M3 4h18v16H3z M7 4v16 M17 4v16 M3 9h4 M3 15h4 M17 9h4 M17 15h4',
  scissors: 'M6 9a3 3 0 1 0 0-6 3 3 0 0 0 0 6z M6 21a3 3 0 1 0 0-6 3 3 0 0 0 0 6z M8.5 7.5 20 19 M8.5 16.5 20 5',
  receipt: 'M5 3h14v18l-3-2-2 2-2-2-2 2-2-2-3 2z M9 8h6 M9 12h6',
  envelope: 'M5 3h14v18H5z M5 9l7 4 7-4',
  expand: 'M14 4h6v6 M10 20H4v-6 M20 4l-7 7 M4 20l7-7',
  x: 'M6 6l12 12 M18 6L6 18',
  plus: 'M12 5v14 M5 12h14',
  minus: 'M5 12h14',
  external: 'M14 4h6v6 M20 4l-9 9 M18 14v6H4V6h6',
  back: 'M15 18l-6-6 6-6',
  quote: 'M7 7h4v4c0 3-2 5-4 6 M15 7h4v4c0 3-2 5-4 6',
  star: 'M12 3l2.8 5.8 6.2.9-4.5 4.4 1 6.3L12 17.5 6.5 20.4l1-6.3L3 9.7l6.2-.9z',
  vote: 'M4 12h16v8H4z M8 12V4h8v8 M10 8l1.5 1.5L14 7',
  route: 'M6 19a2 2 0 1 0 0-4 2 2 0 0 0 0 4z M18 9a2 2 0 1 0 0-4 2 2 0 0 0 0 4z M6 15V9a4 4 0 0 1 4-4h6 M18 9v6a4 4 0 0 1-4 4H8',
  seat: 'M6 10V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v5 M4 10h16v5H4z M6 15v6 M18 15v6',
  image: 'M3 5h18v14H3z M3 16l5-5 4 4 3-3 6 6 M15 9h.01',
  info: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z M12 11v6 M12 7h.01',
  play: 'M7 4l13 8-13 8z',
  palette: 'M12 21a9 9 0 1 1 9-9c0 2-2 3-4 3h-2a2 2 0 0 0-1 4c0 1-1 2-2 2z M7.5 11h.01 M10 7h.01 M15 7h.01',
  shopping: 'M5 8h14l-1 13H6z M9 8a3 3 0 0 1 6 0',
};
const icon = (name, cls = '') => `<svg class="ic ${cls}" viewBox="0 0 24 24" aria-hidden="true"><path d="${ICONS[name] ?? ICONS.info}"></path></svg>`;
const ichip = (name, text, cls = '') => `<span class="ichip ${cls}">${icon(name)}<span>${esc(text)}</span></span>`;
const stateChip = st => `<span class="ichip st-${st}">${icon(STATE_ICON[st])}<span>${STATE[st]}</span></span>`;
const avatar = name => `<i class="av" title="${esc(name)}">${esc([...name.trim()][0] ?? '?')}</i>`;

// Every figure says what it is and where it came from: the caption names the kind of evidence,
// and the credit links to the page it was taken from.
const KIND_LABEL = { photo: 'Photo', screenshot: 'Screenshot', commons: 'Photo', video: 'Video' };
function creditText(m) {
  if (m.kind === 'commons') return [m.credit, m.license].filter(Boolean).join(' · ');
  if (m.kind === 'screenshot') return `${m.source.label}${m.captured ? ' · captured ' + fmt(m.captured, 1) : ''}`;
  return m.source.label;
}
function mediaHtml(key, { cls = '', caption = '', controls = true } = {}) {
  const m = MEDIA[key];
  if (!m) return '';
  const body = m.kind === 'video'
    ? `<video src="${m.src}"${m.poster ? ` poster="${m.poster}"` : ''} ${controls ? 'controls' : ''} muted loop playsinline preload="none" aria-label="${esc(m.alt)}"></video>`
    : `<img src="${m.src}" alt="${esc(m.alt)}" loading="lazy" draggable="false">`;
  const label = caption || m.caption || '';
  const link = m.source.url ? `<a href="${esc(m.source.url)}" target="_blank" rel="noopener" class="credit">${esc(creditText(m))}</a>` : `<span class="credit">${esc(creditText(m))}</span>`;
  return `<figure class="mfig ${cls} k-${m.kind}">${body}<figcaption><span class="kind">${icon(m.kind === 'screenshot' ? 'link' : m.kind === 'video' ? 'video' : 'camera')}${KIND_LABEL[m.kind]}</span>${label ? `<span>${esc(label)}</span>` : ''}${link}</figcaption></figure>`;
}

// One tooltip for every chart mark that carries data-tip.
(() => {
  let tip;
  document.addEventListener('pointerover', e => {
    const t = e.target.closest?.('[data-tip]');
    if (!t) return;
    tip ??= Object.assign(document.createElement('div'), { className: 'tip', hidden: true });
    if (!tip.isConnected) document.body.append(tip);
    tip.textContent = t.dataset.tip;
    tip.hidden = false;
  });
  document.addEventListener('pointermove', e => {
    if (!tip || tip.hidden) return;
    tip.style.left = Math.min(e.clientX + 14, innerWidth - tip.offsetWidth - 8) + 'px';
    tip.style.top = (e.clientY + 16) + 'px';
  });
  document.addEventListener('pointerout', e => { if (tip && e.target.closest?.('[data-tip]')) tip.hidden = true; });
})();
