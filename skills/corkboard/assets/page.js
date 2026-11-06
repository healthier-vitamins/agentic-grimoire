// The item page: a Notion-style document for one item. It opens as a large popup over the board;
// "Expand" turns it into a full page with its own address, and "New tab" opens that address.
// Doors: openPage(it), closePage(), renderFullPage(stage, it, backRoute), pageRoute(it).

function openPage(it) {
  closePage();
  const g = groupOf(it.group);
  const scrim = document.createElement('div');
  scrim.className = 'pm-scrim';
  scrim.innerHTML = `<div class="pm" role="dialog" aria-modal="true" aria-label="${esc(it.title)}">
    <div class="pm-bar"><span class="pm-crumb">${icon(g.icon)}${esc(g.name)} / ${esc(it.short ?? it.title)}</span>
      <a class="pm-btn" href="#${pageRoute(it)}" data-expand>${icon('expand')}<span>Expand</span></a>
      <a class="pm-btn" href="${esc(newTabHref(pageRoute(it)))}" target="_blank" rel="noopener">${icon('external')}<span>New tab</span></a>
      <button class="pm-btn icon-only" data-close aria-label="Close">${icon('x')}</button></div>
    <div class="pm-scroll">${pageHtml(it, false)}</div></div>`;
  document.body.append(scrim);
  document.body.classList.add('pm-open');
  scrim.addEventListener('click', e => { if (e.target === scrim || e.target.closest('[data-close]')) closePage(); });
  scrim.querySelector('[data-expand]').addEventListener('click', () => closePage());
  wirePage(scrim, it, { reopen: () => openPage(it), open: openPage });
  document.addEventListener('keydown', closeOnEscape);
  scrim.querySelector('[data-close]').focus();
}

function closePage() {
  document.querySelectorAll('.pm-scrim').forEach(n => n.remove());
  document.body.classList.remove('pm-open');
  document.removeEventListener('keydown', closeOnEscape);
}

function renderFullPage(stage, it, backRoute) {
  stage.innerHTML = `<div class="pfull"><div class="pm-bar">
      <a class="pm-btn" href="#${backRoute}">${icon('back')}<span>Back to the board</span></a>
      <span class="pm-crumb">${esc(PLAN.title)} / ${esc(groupOf(it.group).name)}</span>
      <a class="pm-btn" href="${esc(newTabHref(pageRoute(it)))}" target="_blank" rel="noopener">${icon('external')}<span>New tab</span></a></div>
    ${pageHtml(it, true)}</div>`;
  wirePage(stage, it, { reopen: () => renderFullPage(stage, it, backRoute), open: x => { location.hash = pageRoute(x); } });
}

const pageRoute = it => `${APP.design}-item-${it.id}`;
const newTabHref = route => `${APP.artifactUrl || location.href.split('#')[0]}#${route}`;
const closeOnEscape = e => { if (e.key === 'Escape') closePage(); };

function wirePage(root, it, nav) {
  root.querySelector('.pg-state').onchange = e => { it.state = e.target.value; APP.refresh(); nav.reopen(); };
  root.querySelectorAll('[data-open]').forEach(b => { b.onclick = () => nav.open(findItem(b.dataset.open)); });
}

function pageHtml(it, full) {
  const g = groupOf(it.group);
  return `<article class="pg${full ? ' full' : ''}">
    ${coverHtml(it, g)}
    <div class="pg-head"><div class="pg-icon">${icon(it.icon)}</div>
      <div class="crumbs">${icon('list')}${esc(PLAN.title)} <span>/</span> ${icon(g.icon)}${esc(g.name)}</div>
      <h1>${esc(it.title)}</h1>${propsHtml(it, g)}</div>
    <div class="pg-body">
      <div class="pg-main">
        ${it.notes ? `<p class="lede">${esc(it.notes)}</p>` : ''}
        ${mainBlocks(it).map(h => `<section class="blk">${h}</section>`).join('')}
      </div>
      <aside class="pg-side">${sideHtml(it)}</aside>
    </div></article>`;
}

// The cover is the item's own evidence when it has some, else a quiet pattern of its icons.
function coverHtml(it, g) {
  if (it.cover) return `<div class="pg-cover photo">${mediaHtml(it.cover, { controls: false })}</div>`;
  const pattern = Array.from({ length: 72 }, (_, n) => icon(n % 3 === 1 ? g.icon : it.icon)).join('');
  return `<div class="pg-cover"><div class="pattern" aria-hidden="true">${pattern}</div></div>`;
}

function propsHtml(it, g) {
  const days = it.due ? diff(PLAN.asOf, it.due) : null;
  const dueNote = days === null ? '' : days < 0 ? `${-days} days overdue` : days === 0 ? 'Due today' : `In ${days} days`;
  const prop = (ic, k, v) => (v ? `<div class="prop">${icon(ic)}<span class="pk">${k}</span><span class="pv">${v}</span></div>` : '');
  const options = planStates().map(s => `<option value="${s}"${s === it.state ? ' selected' : ''}>${STATE[s]}</option>`).join('');
  return `<div class="props">
    <div class="prop">${icon(STATE_ICON[it.state])}<span class="pk">Status</span><span class="pv"><select class="pg-state" aria-label="Status">${options}</select> ${stateChip(it.state)}</span></div>
    ${prop('calendar', 'Due', it.due || it.dueLabel ? esc(dueText(it)) + (dueNote ? ` <em class="${days < 0 ? 'late' : ''}">${dueNote}</em>` : '') : '')}
    ${prop('clock', 'When', it.start ? `${fmt(it.start)} – ${fmt(it.end ?? it.start, 1)}` : esc(it.slot))}
    ${prop('users', 'Who', esc(it.who))}
    ${prop('wallet', 'Cost', esc(it.cost))}
    ${prop(g.icon, 'Group', esc(g.name))}
    ${prop('diamond', 'Milestone', it.milestone ? 'Yes' : '')}
  </div>`;
}

// Main column, in reading order: where the item sits in time, its moments on the day, the blocks
// plan.js gives it, its evidence, then the source's own words.
function mainBlocks(it) {
  return [
    it.due ? yearline(it) : '',
    it.decision ? `<h3 class="h3">${icon('vote')} ${esc(it.decision.question ?? 'Decision')} ${decisionChip(it.decision)}</h3>${decisionOptions(it.decision)}` : '',
    onTheDay(it),
    ...(it.blocks ?? []).map(b => BLOCKS[b.type]?.(b, it) ?? ''),
    it.media?.length ? BLOCKS.gallery({ media: it.media }) : '',
    it.quotes?.length ? quotesHtml(it) : '',
  ].filter(Boolean);
}

const BLOCKS = {
  tiles: b => `<div class="pg-tiles">${b.tiles.map(([v, l, ic, tone]) => `<div class="tile ${tone ?? ''}">${ic ? icon(ic) : ''}<b class="num">${esc(v)}</b><span>${esc(l)}</span></div>`).join('')}</div>`,
  callout: b => `<div class="callout">${icon(b.icon ?? 'info')}<p>${esc(b.text)}</p></div>`,
  iconlist: b => `${b.title ? `<h3 class="h3">${esc(b.title)}</h3>` : ''}<ul class="iconlist">${b.items.map(([ic, t, sub]) => `<li>${icon(ic)}<span>${esc(t)}${sub ? `<em>${esc(sub)}</em>` : ''}</span></li>`).join('')}</ul>`,
  chipset: b => `<h3 class="h3">${esc(b.title)}</h3><div class="chips big">${b.chips.map(([ic, t, tone]) => ichip(ic, t, tone ?? '')).join('')}</div>`,
  people: b => `<div class="people">${b.people.map(([ic, l], n) => `<div class="person${n === 0 ? ' lead' : ''}">${icon(ic)}<span>${esc(l)}</span></div>`).join('')}</div>`,
  checklist: (b, it) => `<h3 class="h3">${icon('check')}${esc(b.title)}</h3><ul class="checks">${b.items.map((t, n) => `<li><input type="checkbox" id="ck-${it.id}-${n}"><label for="ck-${it.id}-${n}">${esc(t)}</label></li>`).join('')}</ul><p class="note">Ticks stay on this page only.</p>`,
  gallery: b => `<h3 class="h3">${icon('image')}Evidence</h3><div class="gallery g${Math.min(b.media.length, 3)}">${b.media.map(k => mediaHtml(k)).join('')}</div>`,
  chart: b => `<h3 class="h3">${icon(b.icon ?? 'chart')}${esc(b.title)}</h3>${chartHtml(b.chart)}${b.note ? `<p class="note">${esc(b.note)}</p>` : ''}`,
  window: b => yearline(null, b),
};

// Where the item's due date (or a window, for a `window` block) sits between the first month and the event.
function yearline(it, win) {
  const a = parse(PLAN.from ?? PLAN.asOf), z = parse(PLAN.event.end) + 20 * MS, x = s => ((parse(s) - a) / (z - a)) * 100;
  const months = [];
  for (let t = a; t < z; t = nextMonth(t)) months.push(t);
  const marks = win
    ? `<div class="yl-win" style="left:${x(win.from)}%;width:${x(win.to) - x(win.from)}%" data-tip="${esc(win.label)}"></div>`
    : `${it.start ? `<div class="yl-win st-${it.state}" style="left:${x(it.start)}%;width:${Math.max(x(it.end ?? it.start) - x(it.start), 0.8)}%"></div>` : ''}
       <div class="yl-due st-${it.state}" style="left:${x(it.due)}%" data-tip="Due ${fmt(it.due, 1)}"></div>`;
  return `<h3 class="h3">${icon('calendar')}${win ? 'When it should happen' : 'Where this sits in the plan'}</h3><div class="yline"><div class="yl-track"></div>
    ${months.map(t => `<span class="yl-m" style="left:${((t - a) / (z - a)) * 100}%">${MON[new Date(t).getUTCMonth()]}</span>`).join('')}
    ${marks}
    <div class="yl-mk now" style="left:${x(PLAN.asOf)}%"><span>Today</span></div><div class="yl-mk ev" style="left:${x(PLAN.event.start)}%"><span>${fmt(PLAN.event.start)}</span></div></div>
    ${win ? `<p class="note">${esc(win.label)}</p>` : ''}`;
}

// The agenda rows this item touches (item.onDay holds agenda row ids).
function onTheDay(it) {
  const rows = (it.onDay ?? []).map(agendaRow).filter(Boolean);
  if (!rows.length) return '';
  return `<h3 class="h3">${icon('clock')}On the day · ${rows.length} moment${rows.length === 1 ? '' : 's'}</h3><ol class="onday">${rows.map(r => `<li><span class="od-t num">${esc(r.t)}${r.end ? `–${esc(r.end)}` : ''}</span><span class="od-p">${icon(r.phase.icon)}${esc(r.phase.place)}</span><span class="od-w">${esc(r.what)}${r.items ? `<em>Bring: ${esc(r.items)}</em>` : ''}</span></li>`).join('')}</ol>`;
}
function agendaRow(id) {
  for (const phase of PLAN.agenda ?? []) {
    const row = phase.rows.find(r => r.id === id);
    if (row) return { ...row, phase };
  }
  return null;
}

const quotesHtml = it => `<h3 class="h3">${icon('quote')}In their words</h3><div class="quotes">${it.quotes.map(q => `<blockquote><p>${esc(q.text)}</p><footer>${avatar(q.who)}<span>${esc(q.who)}</span><time>${esc(q.date)}</time></footer></blockquote>`).join('')}</div>`;

function sideHtml(it) {
  const deps = (it.dependsOn ?? []).map(findItem).filter(Boolean);
  const unlocks = PLAN.items.filter(x => (x.dependsOn ?? []).includes(it.id));
  const days = it.due ? diff(PLAN.asOf, it.due) : null;
  const linkBtn = x => `<button class="lnk" data-open="${x.id}">${icon(x.icon)}<span>${esc(x.short ?? x.title)}</span>${stateChip(x.state)}</button>`;
  return `${days === null ? '' : `<div class="side-card count st-${it.state}"><b class="num">${Math.abs(days)}</b><span>${days < 0 ? 'days overdue' : days === 0 ? 'due today' : 'days left'}</span></div>`}
    ${deps.length ? `<div class="side-card"><h3 class="h3">${icon('link')}Waits on</h3>${deps.map(linkBtn).join('')}</div>` : ''}
    ${unlocks.length ? `<div class="side-card"><h3 class="h3">${icon('link')}Unlocks</h3>${unlocks.map(linkBtn).join('')}</div>` : ''}
    ${it.link ? `<div class="side-card"><h3 class="h3">${icon('external')}Link</h3><a href="${esc(it.link)}" target="_blank" rel="noopener">${esc(it.linkLabel ?? 'Open')}</a></div>` : ''}
    <div class="side-card"><h3 class="h3">${icon('info')}Source</h3><p>${esc(it.source ?? PLAN.source)}</p></div>`;
}
