// Decisions: every choice the plan is making, open ones first. Each column is the question, its
// options with who backs each, the pick once made, and the thread that led there, oldest first.
DESIGNS.decisions = {
  name: 'Decisions',
  hint: 'Open decisions first · each column is the question, its options and the thread behind it',
  build: decisionsBoard,
};

function decisionsBoard() {
  const W = 360, GAP = 24, COLS = Math.min(4, Math.max(1, PLAN.items.filter(i => i.decision).length));
  const open = d => (d.decision.status === 'open' ? 0 : 1);
  const items = PLAN.items.filter(i => i.decision).sort((a, b) => open(a) - open(b) || byDue(a, b));
  const nodes = items.map((it, k) => ({ id: 'dc-' + it.id, x: (k % COLS) * (W + GAP), y: 0, w: W, html: decisionColumn(it), fixed: true }));
  // Masonry: each column goes under the shortest stack, in order, so open decisions stay on top.
  const relayout = box => {
    const tops = Array(COLS).fill(0);
    for (const n of nodes) {
      const c = tops.indexOf(Math.min(...tops));
      n.x = c * (W + GAP); n.y = tops[c]; tops[c] += box(n).h + GAP;
    }
  };
  return { nodes, edges: [], relayout };
}

function decisionColumn(it) {
  const thread = [...(it.quotes ?? [])].sort((a, b) => String(a.date).localeCompare(String(b.date)));
  return `<div class="dc">
    <div class="dc-card st-${it.state}" data-id="${it.id}" role="button" tabindex="0" aria-label="${esc(it.title)}">
      <div class="icard-top"><span class="ibadge">${icon(it.icon)}</span>${decisionChip(it.decision)}</div>
      <b class="dc-q">${esc(it.decision.question ?? it.title)}</b>
      ${decisionOptions(it.decision)}
      <div class="chips">${ichip(groupOf(it.group).icon, groupOf(it.group).name)}${it.due || it.dueLabel ? ichip('calendar', dueText(it)) : ''}</div>
    </div>
    ${thread.map(quoteCard).join('')}
  </div>`;
}

const decisionChip = d => (d.status === 'open' ? '<span class="dc-st">Open</span>' : `<span class="dc-st made">${icon('check')}Decided</span>`);

function decisionOptions(d) {
  if (!d.options?.length) return d.chosen ? `<p class="dc-pick">${icon('check')}${esc(d.chosen)}</p>` : '';
  return `<ul class="dc-opts">${d.options.map(o => `<li class="${o.name === d.chosen ? 'chosen' : ''}">
    <span class="dc-on">${o.name === d.chosen ? icon('check') : ''}${esc(o.name)}</span>${o.note ? `<em>${esc(o.note)}</em>` : ''}
    ${o.for?.length ? `<span class="dc-for">${o.for.map(avatar).join('')}</span>` : ''}</li>`).join('')}</ul>`;
}
