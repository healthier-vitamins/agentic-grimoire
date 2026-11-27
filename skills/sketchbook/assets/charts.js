// Charts drawn from the plan's own numbers. `chartHtml(spec)` is the door: board panels and item
// pages both call it with a spec from plan.js, and each spec type maps to one renderer below.
// A renderer only draws what the spec holds; it never invents a value, a row or a layout.
function chartHtml(spec) {
  const draw = CHARTS[spec.type];
  return draw ? draw(spec) : '';
}

const panel = (title, ic, body, note = '') =>
  `<div class="panel"><h4>${icon(ic)}${esc(title)}</h4>${body}${note ? `<p class="note">${esc(note)}</p>` : ''}</div>`;

// A currency symbol ($, S$, ₩) goes before the number; any other unit (KRW, of 4 friends) after it.
const money = (v, unit = '') => {
  const n = Number(v).toLocaleString('en', { maximumFractionDigits: 2 });
  return !unit ? n : /^[A-Z]{0,2}[$€£¥₩₫]$/.test(unit) ? unit + n : `${n} ${unit}`;
};

const CHARTS = {
  // Items by state, counted from PLAN.items.
  status() {
    const counts = planStates().map(s => [s, PLAN.items.filter(i => i.state === s).length]).filter(([, n]) => n);
    const total = counts.reduce((sum, [, n]) => sum + n, 0);
    const R = 46, C = 2 * Math.PI * R, GAP = 3;
    let offset = 0;
    const arcs = counts.map(([s, n]) => {
      const len = (n / total) * C;
      const arc = `<circle cx="60" cy="60" r="${R}" class="dn-arc st-${s}" stroke-dasharray="${Math.max(len - GAP, 1)} ${C}" stroke-dashoffset="${-offset}" data-tip="${STATE[s]}: ${n} of ${total}"></circle>`;
      offset += len;
      return arc;
    }).join('');
    return `<div class="donut"><svg viewBox="0 0 120 120" role="img" aria-label="${counts.map(([s, n]) => `${n} ${STATE[s]}`).join(', ')}"><g transform="rotate(-90 60 60)">${arcs}</g>
      <text x="60" y="58" class="dn-n">${total}</text><text x="60" y="76" class="dn-l">items</text></svg>
      <ul>${counts.map(([s, n]) => `<li>${stateChip(s)}<b class="num">${n}</b></li>`).join('')}</ul></div>`;
  },

  // { rows: [[label, value]], unit?, pick? } — one bar per row; `pick` highlights the chosen row.
  bars({ rows, unit = '', pick }) {
    const max = Math.max(...rows.map(r => r[1]));
    return `<div class="hbars">${rows.map(([label, v]) => `<div class="hb${label === pick ? ' pick' : ''}"><span class="hl">${esc(label)}</span>
      <span class="ht"><span style="width:${(v / max) * 100}%" data-tip="${esc(label)}: ${money(v, unit)}"></span></span><b class="num">${money(v, unit)}</b></div>`).join('')}</div>`;
  },

  // { parts: [[label, value]], total?, unit?, rest?, big? } — parts of one whole. With `total`,
  // the unfilled share is drawn as `rest` ("Not listed yet"); without it, the parts are the whole.
  stack({ parts, total, unit = '', rest = 'Remaining', big }) {
    const sum = parts.reduce((s, [, v]) => s + v, 0), whole = total ?? sum, left = whole - sum;
    const seg = (cls, label, v) => `<span class="${cls}" style="width:${(v / whole) * 100}%" data-tip="${esc(label)}: ${money(v, unit)}"></span>`;
    const key = (cls, label, v) => `<span><i class="${cls}"></i>${esc(label)} <b class="num">${money(v, unit)}</b></span>`;
    return `<div class="gauge"><div class="mg-big"><b class="num">${esc(big ?? money(sum, unit))}</b>${total ? `<span>of ${money(total, unit)}</span>` : ''}</div>
      <div class="gbar">${parts.map(([l, v], k) => seg(`c${k + 1}`, l, v)).join('')}${left > 0 ? seg('rest', rest, left) : ''}</div>
      <div class="glegend">${parts.map(([l, v], k) => key(`c${k + 1}`, l, v)).join('')}${left > 0 ? key('rest', rest, left) : ''}</div></div>`;
  },

  // { options: [{ name, note?, votes: [who], link?, linkLabel? }], pending?: [who] }
  votes({ options, pending = [] }) {
    const max = Math.max(1, ...options.map(o => o.votes.length));
    return `<div class="votes-chart">${options.map(o => `<div class="vrow"><div class="vname"><b>${esc(o.name)}</b>${o.note ? `<span>${esc(o.note)}</span>` : ''}</div>
      <div class="vbar"><span style="width:${(o.votes.length / max) * 100}%" data-tip="${esc(o.name)}: ${o.votes.length} vote${o.votes.length === 1 ? '' : 's'}${o.votes.length ? ' (' + esc(o.votes.join(', ')) + ')' : ''}"></span></div>
      <div class="vwho">${o.votes.map(avatar).join('') || '<em>0</em>'}</div>
      ${o.link ? `<a href="${esc(o.link)}" target="_blank" rel="noopener" class="vlink">${esc(o.linkLabel ?? 'Open')} ${icon('external')}</a>` : ''}</div>`).join('')}</div>
      ${pending.length ? `<div class="pending">${icon('clock')}<span>Still to vote:</span>${pending.map(p => `<span class="pp">${esc(p)}</span>`).join('')}</div>` : ''}`;
  },

  // { colors: [[hex, name]] }
  swatches({ colors }) {
    return `<div class="mpal">${colors.map(([hex, name]) => `<div class="sw-c"><i style="background:${esc(hex)}"></i><span>${esc(name)}</span><code>${esc(hex)}</code></div>`).join('')}</div>`;
  },

  // { value, label, tone? } — one headline number. tone 'late' paints it as overdue.
  stat({ value, label, tone = '' }) {
    return `<div class="ring-kpi ${esc(tone)}"><b class="num">${esc(value)}</b><span>${esc(label)}</span></div>`;
  },

  // { points: [[date, label]], span?: [from, to] } — dated milestones on one line; `span` shades a stretch.
  timeline({ points, span }) {
    const dates = [...points.map(p => p[0]), ...(span ?? []), PLAN.asOf].map(parse);
    const a = Math.min(...dates) - 4 * MS, b = Math.max(...dates) + 4 * MS, x = s => ((parse(s) - a) / (b - a)) * 100;
    const all = [...points, [PLAN.asOf, 'Today']].sort((p, q) => parse(p[0]) - parse(q[0]));
    return `<div class="runway"><div class="rw-track"></div>${span ? `<div class="rw-trip" style="left:${x(span[0])}%;width:${x(span[1]) - x(span[0])}%"></div>` : ''}
      ${all.map(([d, l], n) => `<div class="rw-pt${l === 'Today' ? ' now' : ''}" style="left:${x(d)}%" data-tip="${fmt(d, 1)}: ${esc(l)}"><i></i><span class="${n % 2 ? 'up' : ''}"><b>${fmt(d)}</b>${esc(l)}</span></div>`).join('')}</div>`;
  },

  // Every day of the event, with the items whose `on` date falls on it.
  days() {
    const out = [];
    for (let t = parse(PLAN.event.start), n = 1; t <= parse(PLAN.event.end); t += MS, n++) {
      const day = iso(t), weekday = new Date(t).getUTCDay();
      const on = PLAN.items.filter(i => i.on === day).map(i => i.short ?? i.title);
      out.push(`<div class="dstrip${weekday === 0 || weekday === 6 ? ' wk' : ''}"><b>${n}</b><span>${fmtDow(day).split(' ')[0]}</span><em>${on.length ? esc(on.join(', ')) : 'Free'}</em></div>`);
    }
    return `<div class="daystrip" style="--n:${Math.min(out.length, 10)}">${out.join('')}</div>`;
  },
};

// Plan-level panels: the gaps (what the sources don't say yet) and the sources themselves.
const gapsList = () => `<ul class="mini-gaps">${(PLAN.gaps ?? []).map(g => `<li>${icon('info')}<span>${esc(g)}</span></li>`).join('')}</ul>`;
const sourcesList = () => `<ul class="mini-gaps">${(PLAN.sources ?? []).map(s => `<li>${icon('link')}<span>${s.url ? `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.label)}</a>` : esc(s.label)}${s.read ? ` · read ${fmt(s.read, 1)}` : ''}</span></li>`).join('')}</ul>`;
