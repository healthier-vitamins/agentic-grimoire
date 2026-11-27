// Timeline: a roadmap in the manner of Linear and Basecamp. One section per group on a true date
// axis; each dated item is a name over its mark: an outlined bar for a span, with its dates written
// on it, a diamond for a milestone, a ring for a due date. Filled means done, red means overdue,
// and today is the only accent. Undated items are listed under the chart. Positions encode dates,
// so nothing here can be dragged. Long stretches with nothing dated fold into a short marked gap.
DESIGNS.timeline = {
  name: 'Timeline',
  hint: 'Drag to pan · click an item to open its page · Fit shows the whole plan',
  build: timelineBoard,
};

const TL = { HEAD: 64, MARKER: 40, SECTION: 34, ROW: 50, GAP: 26, MARK_W: 280, DAY: 34, BREAK_DAYS: 14, BREAK_W: 70, EDGE_DAYS: 3, DATES_IN_BAR: 120 };

function timelineBoard() {
  const { x, t0, t1, breaks, axisW } = brokenScale();
  const shown = t => !breaks.some(b => t > b.t0 && t < b.t1);
  const left = Math.max(0, x(PLAN.asOf) - 5 * TL.DAY);
  const groups = PLAN.groups.filter(g => PLAN.items.some(i => i.group === g.id && dateOf(i)));

  const nodes = [];
  let y = TL.HEAD + TL.MARKER;
  for (const g of groups) {
    const dated = PLAN.items.filter(i => i.group === g.id && dateOf(i));
    // The board opens on today; say how many of the section's items sit off to the left.
    const before = dated.filter(i => x(i.end ?? dateOf(i)) < left).length;
    nodes.push({ id: 'sec-' + g.id, x: left, y, w: 420, h: TL.SECTION, html: `<div class="tl-sec">${icon(g.icon)}<span>${esc(g.name)}</span>${before ? `<em>← ${before} earlier</em>` : ''}</div>`, fixed: true });
    y += TL.SECTION;
    const rows = packRows(dated.sort(byStart), it => [markX(it, x), markX(it, x) + markWidth(it, x)]);
    rows.forEach((row, r) => row.forEach(it => nodes.push({ id: it.id, x: markX(it, x), y: y + r * TL.ROW, w: markWidth(it, x), h: TL.ROW - 8, html: mark(it, x), fixed: true })));
    y += rows.length * TL.ROW + TL.GAP;
  }
  const undated = PLAN.items.filter(i => !dateOf(i));
  if (undated.length) nodes.push({ id: 'undated', x: left, y: y + 10, w: 980, html: undatedList(undated), fixed: true });

  const mondays = [];
  for (let t = t0 + MS; t < t1; t += MS) if (shown(t) && new Date(t).getUTCDay() === 1) mondays.push(iso(t));
  // A month is named over its first visible Monday, so a month that starts inside a gap still gets a name.
  const months = mondays.filter((d, k) => k === 0 || d.slice(0, 7) !== mondays[k - 1].slice(0, 7));
  const today = x(PLAN.asOf), ev = x(PLAN.event.start);
  const evText = `${PLAN.event.label ?? PLAN.title} · ${fmt(PLAN.event.start)}${PLAN.event.end && PLAN.event.end !== PLAN.event.start ? '–' + fmt(PLAN.event.end) : ''}`;
  const todayText = `Today ${fmt(PLAN.asOf)}`, todayW = todayText.length * 7 + 18;
  const decor = `
    <rect x="-24" y="-8" width="${axisW + 48}" height="${y + (undated.length ? 80 + Math.ceil(undated.length / 3) * 32 : 24)}" rx="12" class="tl-sheet"></rect>
    <line x1="0" x2="${axisW}" y1="${TL.HEAD}" y2="${TL.HEAD}" class="tl-base"></line>
    ${mondays.map(d => `<line x1="${x(d)}" x2="${x(d)}" y1="${TL.HEAD}" y2="${y}" class="tl-week"></line><text x="${x(d)}" y="${TL.HEAD - 12}" text-anchor="middle" class="tl-day">${new Date(parse(d)).getUTCDate()}</text>`).join('')}
    ${months.map(m => `<text x="${x(m) - 4}" y="${TL.HEAD - 40}" class="tl-mon">${MON[new Date(parse(m)).getUTCMonth()].toUpperCase()}${m.slice(5, 7) === '01' || m === months[0] ? ' ' + m.slice(0, 4) : ''}</text>`).join('')}
    ${breaks.map(b => `<text x="${(b.x0 + b.x1) / 2}" y="${TL.HEAD - 12}" text-anchor="middle" class="tl-gap">· ${weeksText(b.t1 - b.t0)} ·</text>`).join('')}
    <line x1="${ev}" x2="${ev}" y1="${TL.HEAD}" y2="${y}" class="tl-ev"></line>
    <g class="tl-evtag"><rect x="${ev}" y="${TL.HEAD + 8}" width="${evText.length * 6.6 + 18}" height="22" rx="4"></rect><text x="${ev + 9}" y="${TL.HEAD + 23}">${esc(evText)}</text></g>
    <line x1="${today}" x2="${today}" y1="${TL.HEAD - 26}" y2="${y}" class="tl-now"></line>
    <g class="tl-nowtag"><rect x="${today - todayW / 2}" y="${TL.HEAD - 30}" width="${todayW}" height="22" rx="11"></rect><text x="${today}" y="${TL.HEAD - 15}" text-anchor="middle">${esc(todayText)}</text></g>`;
  return { nodes, edges: [], decor, home: { x: left - 24, y: 0 }, extent: { x: 0, y: 0, w: axisW, h: y + 40 } };
}

const undatedList = items => `<div class="tl-undated"><h4>Not dated yet <span class="num">${items.length}</span></h4><ul>${items.map(it =>
  `<li data-id="${it.id}" role="button" tabindex="0"><i class="tl-ring${it.state === 'done' ? ' done' : ''}"></i><b>${esc(it.short ?? it.title)}</b><span>${esc(groupOf(it.group).name)}</span></li>`).join('')}</ul></div>`;

// A piecewise date scale: TL.DAY pixels a day, except gaps longer than TL.BREAK_DAYS between dated
// points, which keep TL.EDGE_DAYS at each end and fold their middle into TL.BREAK_W pixels.
function brokenScale() {
  const pts = [...new Set([PLAN.asOf, PLAN.event.start, PLAN.event.end, ...PLAN.items.flatMap(i => [i.due, i.start, i.end])].filter(Boolean).map(parse))].sort((a, b) => a - b);
  const t0 = pts[0] - 4 * MS, t1 = pts.at(-1) + 6 * MS, all = [t0, ...pts, t1];
  const knots = [[t0, 0]], breaks = [];
  let px = 0;
  for (let k = 1; k < all.length; k++) {
    const a = all[k - 1], b = all[k], days = (b - a) / MS;
    if (days > TL.BREAK_DAYS) {
      const e = TL.EDGE_DAYS * MS;
      knots.push([a + e, px += TL.EDGE_DAYS * TL.DAY]);
      breaks.push({ t0: a + e, t1: b - e, x0: px, x1: px + TL.BREAK_W });
      knots.push([b - e, px += TL.BREAK_W]);
      knots.push([b, px += TL.EDGE_DAYS * TL.DAY]);
    } else knots.push([b, px += days * TL.DAY]);
  }
  const x = d => {
    const t = parse(d), k = knots.findIndex(([kt]) => kt >= t);
    if (k <= 0) return knots[0][1];
    const [ta, xa] = knots[k - 1], [tb, xb] = knots[k];
    return xa + ((t - ta) / (tb - ta || 1)) * (xb - xa);
  };
  return { x, t0, t1, breaks, axisW: px + TL.MARK_W };
}

const weeksText = ms => { const d = Math.round(ms / MS); return d >= 14 ? `${Math.round(d / 7)} weeks` : `${d} days`; };
const byStart = (a, b) => parse(dateOf(a)) - parse(dateOf(b));
const spanWidth = (it, x) => (it.start && it.end ? Math.max(x(it.end) - x(it.start), 8) : 0);
// A point mark is centred on its date; a bar starts on it.
const markX = (it, x) => x(dateOf(it)) - (spanWidth(it, x) ? 0 : 7);
// Width from the text it carries (CJK counts double), so short marks pack tightly and long ones don't collide.
const textW = (s, px) => [...s].reduce((w, c) => w + (c.codePointAt(0) > 0x2e80 ? 2 : 1), 0) * px;
function markWidth(it, x) {
  const span = spanWidth(it, x), dates = span ? `${fmt(it.start)} – ${fmt(it.end)}` : dueText(it);
  const line = span >= TL.DATES_IN_BAR ? span : (span || 14) + 16 + textW(dates, 7.2);
  return Math.min(Math.max(span, line, textW(it.short ?? it.title, 7.6) + (it.decision?.status === 'open' ? 18 : 0)), Math.max(span, TL.MARK_W));
}

// Greedy interval packing: each item takes the first row whose last mark ends before it starts.
function packRows(items, extent) {
  const rows = [], ends = [];
  for (const it of items) {
    const [a, b] = extent(it);
    let r = ends.findIndex(e => e + 12 <= a);
    if (r < 0) { r = rows.length; rows.push([]); ends.push(-Infinity); }
    rows[r].push(it); ends[r] = b;
  }
  return rows;
}

// Name on top; below it the bar (dates written on it, or beside it when it is short) or the glyph and date.
function mark(it, x) {
  const span = spanWidth(it, x);
  const tone = it.state === 'done' ? ' done' : it.state === 'late' ? ' late' : '';
  const dates = span ? `${fmt(it.start)} – ${fmt(it.end)}` : dueText(it);
  const line = !span ? `<i class="${it.milestone ? 'tl-dia' : 'tl-ring'}${tone}"></i><span class="tl-d num">${esc(dates)}</span>`
    : span >= TL.DATES_IN_BAR ? `<i class="tl-bar${tone}" style="width:${span}px"><span class="num">${fmt(it.start)}</span><span class="num">${fmt(it.end)}</span></i>`
    : `<i class="tl-bar${tone}" style="width:${span}px"></i><span class="tl-d num">${esc(dates)}</span>`;
  return `<div class="tl-mark${tone}" data-id="${it.id}" role="button" tabindex="0" aria-label="${esc(it.title)}, ${esc(dates)}, ${STATE[it.state]}">
    <span class="tl-t">${it.decision?.status === 'open' ? icon('vote') : ''}<span class="tl-tx">${esc(it.short ?? it.title)}</span></span><div class="tl-line">${line}</div></div>`;
}
