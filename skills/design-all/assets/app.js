// Routes: #<board> and #<board>-item-<id> for an item's full page. The tabs are BOARDS, the list
// build.py chose for this plan. Runs last.
(() => {
  const stage = document.getElementById('stage');
  const RE = new RegExp(`^(${BOARDS.join('|')})(?:-item-([A-Za-z0-9_-]+))?$`);
  document.querySelector('.brand').textContent = PLAN.title;
  const nav = document.querySelector('.seg');
  nav.innerHTML = BOARDS.map(b => `<button data-board="${b}">${esc(DESIGNS[b].name)}</button>`).join('');
  nav.querySelectorAll('[data-board]').forEach(b => { b.onclick = () => { location.hash = b.dataset.board; }; });

  function route() {
    const [, board = BOARDS[0], itemId] = RE.exec(location.hash.slice(1)) ?? [];
    const it = itemId && findItem(itemId);
    closePage();
    APP.design = board;
    if (it) {
      renderFullPage(stage, it, board);
      APP.refresh = () => {};
    } else {
      APP.refresh = canvasEngine(stage, board, DESIGNS[board].build, DESIGNS[board].hint).redraw;
    }
    window.scrollTo(0, 0);
    nav.querySelectorAll('[data-board]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.board === board)));
  }
  window.addEventListener('hashchange', route);
  route();
})();
