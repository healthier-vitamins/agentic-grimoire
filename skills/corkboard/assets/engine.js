// Canvas engine shared by every board. A design returns a scene:
//   nodes: [{ id, x, y, w, h?, html, cls?, rot?, fixed? }]   (positioned HTML in world units)
//   edges: [{ from, to, kind: 'dep' | 'leader' | 'route' | 'soft' }]
//   decor: SVG markup drawn under everything (maps, swimlanes)
//   relayout(box): optional; repositions nodes once their rendered heights are known
//   home: optional { x, y, w? }; the board opens with this point at the top left, at 100% or, given w,
//         zoomed to fit w across, rather than fitting the whole scene
// The engine pans and zooms, drags nodes that aren't fixed, remembers moved nodes per plan and
// design, draws edges from node boxes, and opens the item page when an item is clicked.
const FAR_ZOOM = 0.5;

function canvasEngine(root, designKey, build, hint) {
  const KEY = `corkboard-${PLAN.id}-${designKey}`;
  const view = { x: 0, y: 0, k: 1 };
  let saved = {};
  try { saved = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch { saved = {}; }
  let scene, byId;

  root.innerHTML = `<div class="cv cv-${designKey}">
    <div class="cv-vp" tabindex="0" aria-label="Canvas. Drag to pan; Ctrl and scroll, pinch or the buttons to zoom."><div class="cv-world"></div></div>
    <div class="cv-tools" role="toolbar" aria-label="Canvas tools">
      <button data-act="out" aria-label="Zoom out">${icon('minus')}</button><span class="cv-k num">100%</span><button data-act="in" aria-label="Zoom in">${icon('plus')}</button>
      <button data-act="fit">Fit</button><button data-act="reset">Reset layout</button></div>
    <p class="cv-hint">${esc(hint)}</p></div>`;
  const cv = root.firstElementChild, vp = cv.querySelector('.cv-vp'), world = cv.querySelector('.cv-world');

  function render() {
    scene = build();
    byId = {};
    const restore = n => { if (!n.fixed && saved[n.id]) { n.x = saved[n.id].x; n.y = saved[n.id].y; } };
    for (const n of scene.nodes) { restore(n); byId[n.id] = n; }
    world.innerHTML = `<svg class="cv-decor" aria-hidden="true">${scene.decor ?? ''}</svg>
      <svg class="cv-links" aria-hidden="true"><defs><marker id="arr2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="arrhead"></path></marker></defs><g></g></svg>
      ${scene.nodes.map(n => `<div class="node ${n.cls ?? ''}${n.fixed ? '' : ' movable'}" data-node="${n.id}" style="left:${n.x}px;top:${n.y}px;width:${n.w}px;${n.h ? `height:${n.h}px;` : ''}${n.rot ? `--rot:${n.rot}deg;` : ''}">${n.html}</div>`).join('')}`;
    for (const n of scene.nodes) if (!n.h) n.hh = world.querySelector(`[data-node="${n.id}"]`).offsetHeight;
    // A design whose layout depends on rendered heights places its nodes now, once they're measured.
    if (scene.relayout) {
      scene.relayout(box);
      scene.nodes.forEach(restore);
      for (const n of scene.nodes) Object.assign(world.querySelector(`[data-node="${n.id}"]`).style, { left: n.x + 'px', top: n.y + 'px' });
    }
    drawEdges();
  }
  const box = n => ({ x: n.x, y: n.y, w: n.w, h: n.h ?? n.hh ?? 0 });
  const mid = r => ({ x: r.x + r.w / 2, y: r.y + r.h / 2 });
  function edgePt(r, p) {
    const c = mid(r), dx = p.x - c.x, dy = p.y - c.y;
    if (!dx && !dy) return c;
    const s = Math.min(dx ? Math.abs(r.w / 2 / dx) : Infinity, dy ? Math.abs(r.h / 2 / dy) : Infinity);
    return { x: c.x + dx * s, y: c.y + dy * s };
  }
  function drawEdges() {
    let h = '';
    for (const e of scene.edges ?? []) {
      const A = byId[e.from], B = byId[e.to];
      if (!A || !B) continue;
      const ra = box(A), rb = box(B), a = edgePt(ra, mid(rb)), b = edgePt(rb, mid(ra));
      if (e.kind === 'soft' || e.kind === 'route') {
        const mx = (a.x + b.x) / 2;
        h += `<path class="ln-${e.kind}" d="M${a.x} ${a.y} C${mx} ${a.y} ${mx} ${b.y} ${b.x} ${b.y}"></path>`;
      } else {
        h += `<path class="ln-${e.kind}" d="M${a.x} ${a.y} L${b.x} ${b.y}"${e.kind === 'dep' ? ' marker-end="url(#arr2)"' : ''}></path>`;
      }
    }
    world.querySelector('.cv-links g').innerHTML = h;
  }
  function apply() {
    world.style.transform = `translate(${view.x}px, ${view.y}px) scale(${view.k})`;
    cv.style.setProperty('--gx', view.x + 'px');
    cv.style.setProperty('--gy', view.y + 'px');
    cv.style.setProperty('--gs', 24 * view.k + 'px');
    cv.querySelector('.cv-k').textContent = Math.round(view.k * 100) + '%';
    // Semantic zoom: zoomed out, boards swap detail for a summary readable at that size.
    cv.dataset.zoom = view.k < FAR_ZOOM ? 'far' : 'near';
  }
  const clampK = k => Math.min(2.5, Math.max(0.15, k));
  function zoomAt(cx, cy, f) {
    const k = clampK(view.k * f), wx = (cx - view.x) / view.k, wy = (cy - view.y) / view.k;
    view.k = k; view.x = cx - wx * k; view.y = cy - wy * k; apply();
  }
  // Fit the view to the given boxes (default: the whole scene).
  function fit(only) {
    const r = vp.getBoundingClientRect();
    if (!r.width) return;
    const bs = only ?? [...scene.nodes.map(box), ...(scene.extent ? [scene.extent] : [])];
    const x0 = Math.min(...bs.map(b => b.x)), y0 = Math.min(...bs.map(b => b.y));
    const x1 = Math.max(...bs.map(b => b.x + b.w)), y1 = Math.max(...bs.map(b => b.y + b.h));
    // Leave room for the hint above and the toolbar below.
    const top = 56, bottom = 68;
    view.k = clampK(Math.min((r.width - 32) / (x1 - x0), (r.height - top - bottom) / (y1 - y0), only ? 1.4 : 1));
    view.x = r.width / 2 - ((x0 + x1) / 2) * view.k;
    view.y = top + (r.height - top - bottom) / 2 - ((y0 + y1) / 2) * view.k;
    apply();
  }
  function save() {
    const keep = {};
    for (const n of scene.nodes) if (!n.fixed && (n.x !== n.x0 || n.y !== n.y0)) keep[n.id] = { x: n.x, y: n.y };
    Object.assign(saved, keep);
    try { localStorage.setItem(KEY, JSON.stringify(saved)); } catch { /* storage blocked: moves last for this visit */ }
  }

  // Capture starts only once the pointer moves, so a plain click still reaches the card under it.
  const ptrs = new Map();
  let drag = null, pinch = null, suppress = false;
  const NO_DRAG = 'video, a, select, input, label, textarea, .nodrag';
  vp.addEventListener('pointerdown', e => {
    suppress = false;
    if (e.target.closest(NO_DRAG)) return;
    ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (ptrs.size === 2) {
      const [p, q] = [...ptrs.values()], r = vp.getBoundingClientRect();
      pinch = { d: Math.hypot(p.x - q.x, p.y - q.y), k: view.k, cx: (p.x + q.x) / 2 - r.left, cy: (p.y + q.y) / 2 - r.top, x: view.x, y: view.y };
      drag = null;
      return;
    }
    const el = e.target.closest('.node.movable');
    const n = el && byId[el.dataset.node];
    drag = n ? { n, el, sx: e.clientX, sy: e.clientY, ox: n.x, oy: n.y, moved: false } : { sx: e.clientX, sy: e.clientY, ox: view.x, oy: view.y, moved: false };
    if (n) { n.x0 ??= n.x; n.y0 ??= n.y; }
  });
  vp.addEventListener('pointermove', e => {
    if (!ptrs.has(e.pointerId)) return;
    ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pinch && ptrs.size === 2) {
      const [p, q] = [...ptrs.values()];
      const k = clampK(pinch.k * Math.hypot(p.x - q.x, p.y - q.y) / pinch.d);
      const wx = (pinch.cx - pinch.x) / pinch.k, wy = (pinch.cy - pinch.y) / pinch.k;
      view.k = k; view.x = pinch.cx - wx * k; view.y = pinch.cy - wy * k; apply();
      return;
    }
    if (!drag) return;
    const dx = e.clientX - drag.sx, dy = e.clientY - drag.sy;
    if (!drag.moved) {
      if (Math.hypot(dx, dy) < 4) return;
      drag.moved = true;
      vp.setPointerCapture(e.pointerId);
      vp.classList.add(drag.n ? 'moving' : 'panning');
      if (drag.el) drag.el.classList.add('lifted');
    }
    if (drag.n) {
      drag.n.x = drag.ox + dx / view.k; drag.n.y = drag.oy + dy / view.k;
      drag.el.style.left = drag.n.x + 'px'; drag.el.style.top = drag.n.y + 'px';
      drawEdges();
    } else { view.x = drag.ox + dx; view.y = drag.oy + dy; apply(); }
  });
  const end = e => {
    ptrs.delete(e.pointerId);
    if (ptrs.size < 2) pinch = null;
    if (drag?.moved) { suppress = true; if (drag.n) { drag.el.classList.remove('lifted'); save(); } }
    drag = null;
    vp.classList.remove('panning', 'moving');
  };
  vp.addEventListener('pointerup', end);
  vp.addEventListener('pointercancel', end);
  vp.addEventListener('click', e => {
    if (suppress) { suppress = false; e.preventDefault(); return; }
    const focus = cv.dataset.zoom === 'far' && e.target.closest('[data-focus]');
    if (focus) { fit([box(byId[focus.closest('[data-node]').dataset.node])]); return; }
    const t = e.target.closest('[data-id]');
    if (t && !e.target.closest('a, video, select, input, label')) openPage(findItem(t.dataset.id));
  });
  vp.addEventListener('keydown', e => {
    const t = e.target.closest?.('[data-id]');
    if (t && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); openPage(findItem(t.dataset.id)); }
  });
  vp.addEventListener('wheel', e => {
    e.preventDefault();
    const r = vp.getBoundingClientRect();
    if (e.ctrlKey || e.metaKey) zoomAt(e.clientX - r.left, e.clientY - r.top, Math.exp(-e.deltaY * 0.01));
    else { view.x -= e.deltaX; view.y -= e.deltaY; apply(); }
  }, { passive: false });
  cv.querySelector('.cv-tools').addEventListener('click', e => {
    const act = e.target.closest('[data-act]')?.dataset.act, r = vp.getBoundingClientRect();
    if (act === 'in') zoomAt(r.width / 2, r.height / 2, 1.25);
    if (act === 'out') zoomAt(r.width / 2, r.height / 2, 0.8);
    if (act === 'fit') fit();
    if (act === 'reset') { saved = {}; try { localStorage.removeItem(KEY); } catch { /* ignore */ } render(); fit(); }
  });

  function start() {
    if (!scene.home) return fit();
    const { x, y, w } = scene.home, k = w ? clampK(Math.min(1, (vp.getBoundingClientRect().width - 32) / w)) : 1;
    Object.assign(view, { k, x: 16 - x * k, y: 56 - y * k });
    apply();
  }
  render();
  requestAnimationFrame(start);
  return { redraw: render };
}

// Card helpers the designs share.
const itemCard = (it, { size = '', photo = true, group = false } = {}) => `<div class="icard ${size} st-${it.state}" data-id="${it.id}" role="button" tabindex="0" aria-label="${esc(it.title)}">
  ${photo && it.cover ? `<div class="icard-ph">${mediaHtml(it.cover, { controls: false })}</div>` : ''}
  <div class="icard-b"><div class="icard-top"><span class="ibadge">${icon(it.icon)}</span>${stateChip(it.state)}</div>
  <b class="icard-t">${esc(it.title)}</b>
  <div class="chips">${group ? ichip(groupOf(it.group).icon, groupOf(it.group).name) : ''}${it.due || it.dueLabel ? ichip('calendar', dueText(it), it.state === 'late' ? 'warn' : '') : ''}${it.who ? ichip('users', it.who) : ''}${it.cost ? ichip('wallet', it.cost) : ''}${it.slot ? ichip('clock', it.slot) : ''}</div></div></div>`;
const quoteCard = q => `<blockquote class="qcard"><p>${esc(q.text)}</p><footer>${avatar(q.who)}<span>${esc(q.who)}</span><time>${esc(q.date)}</time></footer></blockquote>`;
const label = (text, ic) => `<div class="clabel">${ic ? icon(ic) : ''}<span>${esc(text)}</span></div>`;
