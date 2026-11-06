// Kanban: one column per state, cards sorted by due date and tagged with their group. A card's
// column is its state in the sources, so cards are fixed; change state on the item's page. A state
// holding more than MAX cards wraps into side-by-side sub-columns instead of one long scroll.
// No arrows: columns here are states, not a sequence.
DESIGNS.kanban = {
  name: 'Kanban',
  hint: 'One column per state · cards sorted by due date · click a card to open its page',
  build: kanbanBoard,
};

function kanbanBoard() {
  const COL_W = 268, CARD_H = 124, GAP = 12, PAD = 14, HEAD = 56, EMPTY_W = 140, MAX = 7;
  const nodes = [];
  let x = 0, tallest = 0;
  const cols = planStates().map(st => {
    const items = PLAN.items.filter(i => i.state === st).sort(byDue);
    const subs = Math.ceil(items.length / MAX), rows = Math.ceil(items.length / Math.max(subs, 1));
    const w = items.length ? subs * (COL_W - PAD) + PAD : EMPTY_W, col = { st, x, w, n: items.length, h: HEAD + PAD + Math.max(rows, 0) * (CARD_H + GAP) + (rows ? 2 : PAD) };
    items.forEach((it, k) => nodes.push({ id: it.id, x: x + PAD + Math.floor(k / rows) * (COL_W - PAD), y: HEAD + PAD + (k % rows) * (CARD_H + GAP), w: COL_W - PAD * 2, h: CARD_H, html: itemCard(it, { size: 'sm', photo: false, group: true }), fixed: true }));
    tallest = Math.max(tallest, rows);
    x += w + GAP;
    return col;
  });
  const h = HEAD + PAD * 2 + Math.max(1, tallest) * (CARD_H + GAP);
  // Columns hug their cards; the state's colour is a small dot by its name, nothing more.
  const decor = cols.map(c => `<rect x="${c.x}" y="0" width="${c.w}" height="${c.h}" rx="10" class="kb-col"></rect>
    <circle cx="${c.x + PAD + 4}" cy="31" r="4" class="kb-dot st-${c.st}"></circle>
    <text x="${c.x + PAD + 16}" y="36" class="kb-h">${STATE[c.st]}<tspan class="kb-n" dx="8">${c.n}</tspan></text>`).join('');
  return { nodes, edges: [], decor, extent: { x: 0, y: 0, w: x, h } };
}
