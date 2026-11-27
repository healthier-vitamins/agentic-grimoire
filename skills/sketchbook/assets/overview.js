// Overview: the whole plan on one screen, for whoever runs it. Headline numbers across the top,
// a milestone strip from today to the event, then one tile per group with its progress, what's
// next, what's stuck, and every item as a row. Zoomed out, each tile collapses to its summary and
// a click on any part zooms into it.
DESIGNS.overview = {
  name: 'Overview',
  hint: 'Every group at a glance · zoom out for the summary, in for each item · click a row to open it',
  build: overview,
};

const OV = { W: 1260, TILE_W: 405, GAP: 22, COLS: 3, HEAD: 128, ROW: 32, TOP: 460 };

function overview() {
  const nodes = [
    { id: 'ov-kpi', x: 0, y: 0, w: OV.W, h: 110, html: kpiStrip(), fixed: true },
    { id: 'ov-ms', x: 0, y: 128, w: OV.W, h: 310, html: milestoneStrip(OV.W), fixed: true },
  ];
  const groups = PLAN.groups.filter(g => PLAN.items.some(i => i.group === g.id));
  let y = OV.TOP;
  for (let k = 0; k < groups.length; k += OV.COLS) {
    const row = groups.slice(k, k + OV.COLS);
    const h = Math.max(...row.map(g => OV.HEAD + PLAN.items.filter(i => i.group === g.id).length * OV.ROW + 14));
    row.forEach((g, c) => nodes.push({ id: 'ov-' + g.id, x: c * (OV.TILE_W + OV.GAP), y, w: OV.TILE_W, h, html: groupTile(g), fixed: true }));
    y += h + OV.GAP;
  }
  return { nodes, edges: [], home: { x: 0, y: 0, w: OV.W } };
}

function kpiStrip() {
  const items = PLAN.items, count = st => items.filter(i => i.state === st).length;
  const next = items.filter(i => i.milestone && i.state !== 'done' && dateOf(i) >= PLAN.asOf).sort(byDue)[0];
  const tile = (v, l, ic, tone = '') => `<div class="tile ${tone}"><b class="num">${esc(v)}</b><span>${esc(l)}</span></div>`;
  return `<div class="ov-kpi" data-focus>
    ${tile(daysToGo(), 'days to go', 'clock')}
    ${tile(`${count('done')}/${items.length}`, 'items done', 'check')}
    ${tile(count('late'), 'overdue', 'alert', count('late') ? 'warn' : '')}
    ${tile(count('waiting'), 'waiting on someone', 'hourglass')}
    ${tile(openDecisions().length, 'decisions open', 'vote')}
    ${tile(next ? fmt(dateOf(next)) : 'None', next ? `next: ${next.short ?? next.title}` : 'no milestone ahead', 'flag')}
  </div>`;
}

// Milestones and the event on one axis. Each label takes the nearest free level, alternating
// above and below the axis, so clustered dates stack instead of overprinting.
// Below the axis the first level clears the Today tag and the event name, which share one row.
const MS_LEVELS = [-28, 72, -54, 98, -80, 124];

function milestoneStrip(w) {
  const { t0, t1 } = planSpan(), pad = 70, axisY = 120;
  const x = d => pad + ((parse(d) - t0) / Math.max(t1 - t0, MS)) * (w - pad * 2);
  const ms = PLAN.items.filter(i => i.milestone).sort(byDue);
  const months = [];
  for (let t = Date.UTC(new Date(t0).getUTCFullYear(), new Date(t0).getUTCMonth(), 1); t <= t1; t = nextMonth(t)) if (t >= t0) months.push(iso(t));
  const ends = MS_LEVELS.map(() => -Infinity);
  const marks = ms.map(it => {
    const mx = x(dateOf(it)), text = it.short ?? it.title, half = Math.max(text.length, 7) * 3.4 + 6;
    let lv = ends.findIndex(e => e < mx - half);
    if (lv < 0) lv = ends.indexOf(Math.min(...ends));
    ends[lv] = mx + half;
    const dy = MS_LEVELS[lv], up = dy < 0, ly = axisY + dy;
    return `<g class="ms st-${it.state}" data-id="${it.id}" role="button" tabindex="0" aria-label="${esc(it.title)}">
      <line x1="${mx}" x2="${mx}" y1="${axisY}" y2="${up ? ly + 6 : ly - 26}" class="ms-stem"></line>
      <path d="M${mx} ${axisY - 6}l6 6-6 6-6-6z" class="ms-dia"></path>
      <text x="${mx}" y="${ly}" text-anchor="middle" class="ms-l">${esc(text)}<tspan class="ms-d" dx="5">${fmt(dateOf(it))}</tspan></text></g>`;
  }).join('');
  const ev0 = x(PLAN.event.start), ev1 = Math.max(x(PLAN.event.end), ev0 + 6);
  return `<div class="panel ov-ms" data-focus><h4>${icon('flag')}Milestones</h4><svg viewBox="0 0 ${w} 260" width="100%" height="260" aria-label="Milestone timeline">
    <line x1="${ev0}" x2="${ev0}" y1="${axisY - 22}" y2="${axisY + 22}" class="ms-evl"></line><line x1="${ev1}" x2="${ev1}" y1="${axisY - 22}" y2="${axisY + 22}" class="ms-evl"></line>
    <line x1="${pad}" x2="${w - pad}" y1="${axisY}" y2="${axisY}" class="ms-axis"></line>
    ${months.map(m => `<line x1="${x(m)}" x2="${x(m)}" y1="${axisY - 4}" y2="${axisY + 4}" class="ms-axis"></line><text x="${x(m) + 4}" y="${axisY + 20}" class="ms-m">${MON[new Date(parse(m)).getUTCMonth()].toUpperCase()}</text>`).join('')}
    <line x1="${x(PLAN.asOf)}" x2="${x(PLAN.asOf)}" y1="${axisY - 22}" y2="${axisY + 22}" class="ms-today"></line>
    <g class="tl-nowtag"><rect x="${x(PLAN.asOf) - 26}" y="${axisY + 26}" width="52" height="20" rx="10"></rect><text x="${x(PLAN.asOf)}" y="${axisY + 40}" text-anchor="middle">Today</text></g>
    ${marks}
    <text x="${ev1}" y="${axisY + 40}" text-anchor="end" class="ms-l ev">${esc(PLAN.event.label ?? PLAN.title)}</text></svg></div>`;
}

function groupTile(g) {
  const items = PLAN.items.filter(i => i.group === g.id).sort(byDue);
  const done = items.filter(i => i.state === 'done').length;
  const stuck = items.filter(i => i.state === 'late' || i.state === 'waiting').length;
  const next = items.find(i => i.state !== 'done' && dateOf(i));
  const late = items.filter(i => i.state === 'late').length;
  return `<div class="ov-tile">
    <div class="ov-head"><span class="ibadge">${icon(g.icon)}</span><b>${esc(g.name)}</b><span class="num ov-frac">${done}/${items.length}</span></div>
    <div class="ov-prog" aria-label="${done} of ${items.length} done"><i class="done" style="flex:${done}"></i><i class="late" style="flex:${late}"></i><i style="flex:${items.length - done - late}"></i></div>
    <p class="ov-next">${next ? `${icon('flag')}Next: <b>${esc(next.short ?? next.title)}</b> · ${esc(dueText(next))}` : `${icon('check')}Nothing dated ahead`}${stuck ? ` <span class="ichip warn">${icon('alert')}<span>${stuck} stuck</span></span>` : ''}</p>
    <ul class="ov-rows">${items.map(it => `<li class="ov-row" data-id="${it.id}" role="button" tabindex="0"><i class="${it.milestone ? 'tl-dia' : 'tl-ring'}${it.state === 'done' ? ' done' : it.state === 'late' ? ' late' : ''}" title="${STATE[it.state]}"></i>
      <span class="ov-t">${it.decision?.status === 'open' ? icon('vote', 'ov-dec-ic') : ''}${esc(it.title)}</span><span class="ov-d num">${esc(dueText(it))}</span></li>`).join('')}</ul>
    <div class="zcover" data-focus role="button" tabindex="0" aria-label="Zoom into ${esc(g.name)}"><b>${esc(g.name)}</b><span class="num">${done} of ${items.length} done</span><div class="ov-prog"><i class="done" style="flex:${done}"></i><i class="late" style="flex:${late}"></i><i style="flex:${items.length - done - late}"></i></div>${stuck ? `<span class="warn">${stuck} stuck</span>` : ''}</div>
  </div>`;
}
