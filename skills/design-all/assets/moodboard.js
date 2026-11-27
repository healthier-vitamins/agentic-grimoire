// Moodboard: a wall of everything the plan knows. A title card and the dashboard panels across the
// top, one cluster of cards per group below (each card wearing its own evidence), the agenda
// ribbon, then two stickies: what the sources don't say yet, and the sources themselves.
DESIGNS.moodboard = {
  name: 'Moodboard',
  hint: 'Drag anything to rearrange · click a card to open its page · Ctrl + scroll to zoom',
  build: moodboard,
};

const MOOD = { CARD_W: 285, GX: 44, GY: 60, COLS: 3, GAP: 90 };

// Nodes are created here and placed in relayout, once their rendered heights are known.
function moodboard() {
  const groups = PLAN.groups.filter(g => PLAN.items.some(i => i.group === g.id));
  const edges = PLAN.items.flatMap(it => (it.dependsOn ?? []).map(d => ({ from: d, to: it.id, kind: 'dep' })));
  const clusters = groups.map(g => groupCluster(g, edges));
  const footer = footerRow();
  const top = [moodTitle(), ...dashboardRow()];
  const nodes = [...top, ...clusters.flatMap(c => [c.label, ...c.cards]), ...footer];
  const relayout = box => {
    let y = Math.max(...top.map(n => n.y + box(n).h)) + MOOD.GAP;
    for (let k = 0; k < clusters.length; k += MOOD.COLS) {
      let x = 0;
      const heights = clusters.slice(k, k + MOOD.COLS).map(c => {
        const h = placeCluster(c, x, y, box);
        x += clusterWidth(c) + MOOD.GAP;
        return h;
      });
      y += Math.max(...heights) + MOOD.GAP;
    }
    footer.forEach(n => { n.y = y + n.dy; });
  };
  return { nodes, edges, relayout };
}

function moodTitle() {
  const chips = [ichip('clock', `${daysToGo()} days to go`), ...(PLAN.headline ?? []).map(([ic, t, tone]) => ichip(ic, t, tone ?? ''))].join('');
  return { id: 'title', x: 0, y: 0, w: 420, cls: 'card-plain', html: `<div class="mood-title">${PLAN.glyph ? `<span class="glyph">${esc(PLAN.glyph)}</span>` : ''}
    <b>${esc(PLAN.title)}</b><span class="big-date num">${esc(PLAN.when)}</span>
    ${PLAN.place ? `<span class="mt-when">${icon('pin')} ${esc(PLAN.place)}</span>` : ''}<div class="chips">${chips}</div></div>` };
}

function dashboardRow() {
  let x = 450;
  return (PLAN.dashboard ?? []).map((p, k) => {
    const w = p.w ?? (p.chart.type === 'swatches' || p.chart.type === 'votes' ? 380 : 330);
    const node = { id: 'dash-' + k, x, y: 0, w, html: panel(p.title, p.icon ?? 'chart', chartHtml(p.chart), p.note) };
    x += w + 30;
    return node;
  });
}

// A group's cards in layers: each linked card sits one row below the last card it waits on, and a
// row is ordered by where its arrows go, so a hub lands in the middle with its links around it and
// arrows run downward with few crossings. Unlinked cards and pinned quotes follow in rows of three.
function groupCluster(g, edges) {
  const items = PLAN.items.filter(i => i.group === g.id).sort(byDue);
  const cards = items.map((it, j) => ({ id: it.id, x: 0, y: 0, w: MOOD.CARD_W, html: itemCard(it), rot: ((j * 7) % 5 - 2) * 0.4 }));
  const quotes = items.flatMap(it => (it.quotes ?? []).filter(q => q.pin).map((q, j) =>
    ({ id: `q-${it.id}-${j}`, x: 0, y: 0, w: MOOD.CARD_W, html: quoteCard(q), rot: j % 2 ? 1.5 : -1.5 })));
  const byId = Object.fromEntries(cards.map(c => [c.id, c]));
  const layered = layers(items.map(i => i.id), edges).map(row => row.map(id => byId[id]));
  const placed = new Set(layered.flat());
  const loose = [...cards.filter(c => !placed.has(c)), ...quotes];
  const rows = [...layered, ...Array.from({ length: Math.ceil(loose.length / 3) }, (_, k) => loose.slice(k * 3, k * 3 + 3))];
  return {
    label: { id: 'l-' + g.id, x: 0, y: 0, w: MOOD.CARD_W, html: label(g.name, g.icon), fixed: true },
    cards: [...cards, ...quotes],
    rows,
    cols: Math.max(3, ...rows.map(r => r.length)),
  };
}

// Longest-path ranks, then a few barycenter sweeps to order each rank by its neighbours' positions.
function layers(ids, edges) {
  const ins = new Map(ids.map(id => [id, []])), outs = new Map(ids.map(id => [id, []]));
  for (const e of edges) if (ins.has(e.from) && ins.has(e.to)) { outs.get(e.from).push(e.to); ins.get(e.to).push(e.from); }
  const rank = new Map();
  const rankOf = id => {
    if (!rank.has(id)) { rank.set(id, 0); rank.set(id, Math.max(0, ...ins.get(id).map(p => rankOf(p) + 1))); }
    return rank.get(id);
  };
  const rows = [];
  ids.filter(id => ins.get(id).length || outs.get(id).length).forEach(id => (rows[rankOf(id)] ??= []).push(id));
  const pos = new Map();
  const index = r => r.forEach((id, k) => pos.set(id, k - (r.length - 1) / 2));
  rows.forEach(index);
  for (let sweep = 0; sweep < 4; sweep++) {
    const nbrs = sweep % 2 ? outs : ins;
    const centre = id => nbrs.get(id).length ? nbrs.get(id).reduce((t, n) => t + pos.get(n), 0) / nbrs.get(id).length : pos.get(id);
    for (const r of sweep % 2 ? [...rows].reverse() : rows) { r.sort((a, b) => centre(a) - centre(b)); index(r); }
  }
  return rows.filter(Boolean);
}

const clusterWidth = c => c.cols * MOOD.CARD_W + (c.cols - 1) * MOOD.GX;

// Lays a cluster out from (x, y) with measured heights, each row centred; returns its height.
function placeCluster(c, x, y, box) {
  Object.assign(c.label, { x, y, w: clusterWidth(c) });
  let top = y + 56;
  for (const row of c.rows) {
    const left = x + (clusterWidth(c) - (row.length * MOOD.CARD_W + (row.length - 1) * MOOD.GX)) / 2;
    row.forEach((n, k) => { n.x = left + k * (MOOD.CARD_W + MOOD.GX); n.y = top; });
    top += Math.max(...row.map(n => box(n).h)) + MOOD.GY;
  }
  return top - y;
}

// dy is the offset from the row's top, set once the clusters above are placed.
function footerRow() {
  const nodes = [];
  let x = 0;
  if (PLAN.agenda?.length) {
    nodes.push({ id: 'ribbon', x, dy: 0, w: 1420, html: panel(PLAN.event.label ?? 'On the day', 'clock', agendaRibbon()) });
    x += 1480;
  }
  if (PLAN.gaps?.length) {
    nodes.push({ id: 'gaps', x, dy: -40, w: 300, rot: 1.5, html: `<div class="sticky"><h4>${icon('info')}Not in the sources yet</h4>${gapsList()}</div>` });
    x += 340;
  }
  if (PLAN.sources?.length) nodes.push({ id: 'sources', x, dy: -20, w: 300, rot: -1, html: `<div class="sticky blue"><h4>${icon('link')}Sources</h4>${sourcesList()}</div>` });
  return nodes;
}

// One arrow-step per agenda phase: its icon, place, and first-to-last time.
const agendaRibbon = () => `<div class="ribbon" style="--n:${PLAN.agenda.length}">${PLAN.agenda.map(ph => {
  const first = ph.rows[0], last = ph.rows.at(-1);
  return `<div class="rb-step"><span class="rb-ic">${icon(ph.icon)}</span><div><b>${esc(ph.phase)}</b><span>${esc(ph.place)}</span><em class="num">${esc(first.t)}–${esc(last.end ?? last.t)}</em></div></div>`;
}).join('')}</div>`;
