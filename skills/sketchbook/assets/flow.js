// Flow: a timeline board. Time runs left to right in columns, each group is a swimlane, dashed
// arrows show what waits on what, the event itself sits as a card in its column, and the
// dashboard panels run along the top.
//
// Columns are months from PLAN.from to the event, plus "No date", each item placed by its due
// (or start) month. A plan whose time isn't monthly gives PLAN.columns ([[id, label]]) and
// PLAN.current (the column holding today) instead, and each item names its column in `col`.
DESIGNS.flow = {
  name: 'Flow',
  hint: 'Columns are time, rows are groups · arrows mean “waits on” · click a card to open its page',
  build: () => flowBoard(PLAN.columns ? givenColumns() : monthColumns()),
};

function monthColumns() {
  const cols = [['none', 'No date']];
  for (let t = parse(PLAN.from ?? PLAN.asOf); t <= parse(PLAN.event.start); t = nextMonth(t)) {
    const d = new Date(t);
    cols.push([iso(t).slice(0, 7), `${MON[d.getUTCMonth()]} ${String(d.getUTCFullYear()).slice(2)}`]);
  }
  const month = it => (it.due ?? it.start)?.slice(0, 7);
  return { cols, colOf: it => month(it) ?? 'none', current: PLAN.asOf.slice(0, 7), event: PLAN.event.start.slice(0, 7) };
}

function givenColumns() {
  return { cols: PLAN.columns, colOf: it => it.col ?? PLAN.columns.at(-1)[0], current: PLAN.current, event: PLAN.event.col };
}

function flowBoard(spec) {
  const CARD_W = 236, CARD_H = 124, GAP = 12, PAD = 14, HEAD = 56, LANE_LABEL = 190, EMPTY_W = 72;
  const groups = PLAN.groups.filter(g => PLAN.items.some(i => i.group === g.id));
  const cells = {};
  const put = (lane, col, entry) => ((cells[lane + '|' + col] ??= []).push(entry));
  PLAN.items.forEach(it => put(it.group, spec.colOf(it), { item: it }));
  const eventLane = PLAN.event.group ?? groups[0]?.id;
  if (spec.event) put(eventLane, spec.event, { event: true });
  const used = new Set(Object.keys(cells).map(k => k.split('|')[1]));

  // Empty columns shrink so time still reads but space isn't wasted.
  let x = 0;
  const colX = {}, colW = {};
  for (const [id] of spec.cols) { colW[id] = used.has(id) ? CARD_W + PAD * 2 : EMPTY_W; colX[id] = x; x += colW[id]; }
  const boardW = x;
  let y = HEAD;
  const laneY = {}, laneH = {};
  for (const g of groups) {
    const most = Math.max(1, ...spec.cols.map(([c]) => (cells[g.id + '|' + c] ?? []).length));
    laneY[g.id] = y; laneH[g.id] = PAD * 2 + most * CARD_H + (most - 1) * GAP; y += laneH[g.id];
  }
  const boardH = y;

  const nodes = [], edges = [];
  for (const g of groups) for (const [c] of spec.cols) {
    (cells[g.id + '|' + c] ?? []).sort((a, b) => (a.item && b.item ? byDue(a.item, b.item) : a.item ? -1 : 1)).forEach((e, k) => {
      const box = { x: colX[c] + PAD, y: laneY[g.id] + PAD + k * (CARD_H + GAP), w: CARD_W, h: CARD_H };
      nodes.push(e.item ? { id: e.item.id, ...box, html: itemCard(e.item, { size: 'sm', photo: false }) } : { id: 'event', ...box, html: eventCard() });
    });
  }
  PLAN.items.forEach(it => (it.dependsOn ?? []).forEach(d => edges.push({ from: d, to: it.id, kind: 'dep' })));

  let kx = -LANE_LABEL;
  for (const [k, p] of (PLAN.dashboard ?? []).entries()) {
    const w = p.w ?? (p.chart.type === 'swatches' || p.chart.type === 'votes' ? 380 : 330);
    nodes.push({ id: 'k-' + k, x: kx, y: -340, w, html: panel(p.title, p.icon ?? 'chart', chartHtml(p.chart), p.note), fixed: true });
    kx += w + 16;
  }

  const iconSvg = (name, tx, ty) => `<g transform="translate(${tx} ${ty})" class="svg-ic"><path d="${ICONS[name] ?? ICONS.info}"></path></g>`;
  const decor = `
    <rect x="${-LANE_LABEL}" y="0" width="${boardW + LANE_LABEL}" height="${boardH}" rx="16" class="fl-board"></rect>
    ${spec.cols.map(([c, l], k) => `<rect x="${colX[c]}" y="0" width="${colW[c]}" height="${boardH}" class="fl-col${k % 2 ? ' alt' : ''}${c === spec.current ? ' now' : ''}${c === spec.event ? ' ev' : ''}"></rect>
      <text x="${colX[c] + colW[c] / 2}" y="34" class="fl-h${used.has(c) ? '' : ' empty'}${c === spec.current ? ' now' : ''}" text-anchor="middle">${esc(used.has(c) || colW[c] > 100 ? l : l.split(' ')[0])}</text>`).join('')}
    ${groups.map(g => `<line x1="${-LANE_LABEL}" x2="${boardW}" y1="${laneY[g.id]}" y2="${laneY[g.id]}" class="fl-lane"></line>
      ${iconSvg(g.icon, -LANE_LABEL + 18, laneY[g.id] + 18)}<text x="${-LANE_LABEL + 48}" y="${laneY[g.id] + 35}" class="fl-ln">${esc(g.name)}</text>`).join('')}
    ${colX[spec.current] === undefined ? '' : `<text x="${colX[spec.current] + colW[spec.current] / 2}" y="${boardH + 24}" class="fl-today" text-anchor="middle">▲ Today · ${fmt(PLAN.asOf)}</text>`}`;
  return { nodes, edges, decor, extent: { x: -LANE_LABEL, y: -350, w: boardW + LANE_LABEL, h: boardH + 390 } };
}

const eventCard = () => `<div class="ghost ev">${icon(PLAN.event.icon ?? 'star')}<b>${esc(PLAN.event.label ?? PLAN.title)} · ${fmt(PLAN.event.start)}</b>${PLAN.event.note ? `<span>${esc(PLAN.event.note)}</span>` : ''}</div>`;
