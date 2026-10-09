// PlayIDE: the model drawn in UML state-machine notation on a maxGraph canvas, with Build & run beside it (ADR-0151).
// The page only draws what the server returns; every rule lives in the Python kernel.
"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  const caseId = new URLSearchParams(location.search).get("case");
  let token = location.hash.slice(1) || sessionStorage.getItem("eija-session") || "";
  // Drop the token from the address bar but keep ?case=, so a reload still shows the same model.
  if (location.hash) { sessionStorage.setItem("eija-session", token); history.replaceState(null, "", location.pathname + location.search); }
  const STATE = { width: 150, height: 54 }, INITIAL = 22;
  let graph, model, selected = "", sim = null, replayTimer = 0, data = null, savedData = null, classGraph = null, useCaseGraph = null, tab = "states";
  let components = null, componentGraph = null, lastBuild = null;
  let baseModel = null, plan = null; // the server's model, and the chat plan being previewed on top of it (if any)
  let packInfo = null, points = 0, simKey = null, cards = 0, problemsFor = null; // the pack's actions and roles; check points; what was simulated
  let shownChange = null; // while the Changes view is on: the union of the model in force and the change (ADR-0176), drawn on the class and use case diagrams too
  let ripple = null, rippleSeq = 0; // what the accepted plan does to every diagram, with the proposer's follow-ons (ADR-0158)
  const earned = [];
  let screens = null, screensEdited = false, useCase = null, checkTimer = 0, problems = [], useCaseList = [], a11y = null;
  const base = {}; // each cell's own style and label, so overlays can be cleared
  // The kind of actor holding each role (ADR-0210). UML draws all four as actors; a person keeps the stick figure, the
  // others are drawn as an actor classifier with their keyword, as UML allows.
  let roleKinds = {};
  const ACTOR_KINDS = { human: "person", agent: "AI agent", timer: "timer", system: "external system" };
  const A_KIND = { human: "a person", agent: "an AI agent", timer: "a timer", system: "an external system" };
  const ACTOR_GROUPS = { human: "People", agent: "AI agents", timer: "Timers", system: "External systems" };
  // A role's kind as the plan would have it, while the plan is previewed (and so allowed): an accepted "make X an AI
  // agent" step shows on every diagram (#156). Back on the model, the kind in force.
  const roleKind = (role) => {
    const shown = plan && plan.previewing && plan.result && plan.result.legal;
    const step = shown ? accepted().filter((t) => t.kind === "set_role_kind" && t.role === role).at(-1) : null;
    return step ? step.to : roleKinds[role] || "human";
  };
  const kindNote = (role) => (roleKind(role) === "human" ? "" : ` (${ACTOR_KINDS[roleKind(role)]})`); // "Who may take it" says who
  const hooks = { redraw: [], inspect: [], laws: [], tab: [], changeSelect: [], edit: [], screens: [] }; // the run bar (play-run.js) redraws its marks and adds inspector tools; play-laws.js and play-access.js draw their tabs
  // the Changes view (play-diff.js, ADR-0176) closes when another tab is shown and answers current() while open;
  // edit hears every undoable edit (ADR-0198); screens hears the screen designer redraw its list and card (play-roles.js)

  async function api(path, body) {
    const options = { headers: { Authorization: "Bearer " + token } };
    if (body !== undefined) Object.assign(options, { method: "POST", body: JSON.stringify(body) }, { headers: { ...options.headers, "Content-Type": "application/json" } });
    const response = await fetch(path, options);
    const value = await response.json();
    if (!response.ok) throw Object.assign(new Error(value.message || "Request failed"), { code: value.code });
    return value;
  }

  function el(tag, text, attrs = {}) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
    return node;
  }

  // While a plan can be previewed, both models are laid out together, in a fixed order, so Preview and Back to the
  // model move nothing: every state keeps its place, and a removed one leaves its gap (ADR-0176).
  function basis(workflow) {
    const models = plan && plan.result && plan.result.legal ? [baseModel, plan.result.candidate] : [workflow];
    const seen = new Set(), transitions = [];
    for (const t of models.flatMap((w) => w.transitions)) {
      const key = `${t.id} ${t.from_state} ${t.to_state}`;
      if (!seen.has(key)) { seen.add(key); transitions.push(t); }
    }
    return { states: [...new Set(models.flatMap((w) => w.states))], initials: [...new Set(models.map((w) => w.initial_state))], transitions };
  }

  // The state machine runs left to right, or top to bottom when that draws it clearly larger in the canvas: on a laptop
  // with the side bar and the chat open the canvas is taller than it is wide, and a left-to-right chain shrinks its
  // labels to a few pixels. The direction is chosen once, on the first drawing, so an edit or a preview never turns it.
  let direction = null;
  function layout(workflow) {
    const shape = basis(workflow), box = $("canvas");
    if (!direction) {
      const fits = (g) => Math.min(1.4, (box.clientWidth - 48) / g.graph().width, (box.clientHeight - 48) / g.graph().height);
      direction = box.clientWidth && fits(laidOut(shape, "TB")) > fits(laidOut(shape, "LR")) * 1.15 ? "TB" : "LR";
    }
    const g = laidOut(shape, direction);
    const at = (id) => { const n = g.node(id); return [n.x - n.width / 2, n.y - n.height / 2]; };
    // dagre's bend points, without the two ends maxGraph attaches to the state borders itself.
    const bends = (t) => g.edge(t.from_state, t.to_state, t.id).points.slice(1, -1);
    return { at, bends };
  }

  function laidOut(shape, rankdir) {
    const g = new dagre.graphlib.Graph({ multigraph: true });
    g.setGraph(rankdir === "TB" ? { rankdir, nodesep: 60, ranksep: 70, edgesep: 30, marginx: 30, marginy: 30 }
      : { rankdir, nodesep: 60, ranksep: 120, edgesep: 30, marginx: 30, marginy: 30 });
    g.setDefaultEdgeLabel(() => ({}));
    g.setNode("__initial", { width: INITIAL, height: INITIAL });
    for (const s of shape.states) g.setNode(s, { ...STATE });
    for (const s of shape.initials) g.setEdge("__initial", s, {}, s);
    // Each label is laid out at its real size, centred on its edge, so dagre leaves room for it: the labels of a
    // back-and-forth pair, or of two transitions between the same states, never overlap (#153). liftLabels puts
    // each label in that room.
    for (const t of shape.transitions) g.setEdge(t.from_state, t.to_state, { width: textWidth(label(t)) + 16, height: 28, labelpos: "c" }, t.id);
    dagre.layout(g);
    return g;
  }

  // maxGraph puts an edge's label halfway along the line, which is not where the layout left room for it: move each
  // transition's label to its middle bend, the point dagre routed the edge through for the label (#153).
  // The Changes view (play-diff.js) uses it too, for its own transitions.
  function liftLabels(g, isTransition = (cell) => cell.id.startsWith("transition:")) {
    const v = g.view, m = g.getDataModel(), { Point } = maxgraph;
    g.batchUpdate(() => {
      for (const cell of Object.values(m.cells)) {
        if (!cell.id || !isTransition(cell) || !cell.geometry) continue;
        const points = cell.geometry.points || [], state = v.getState(cell);
        if (!points.length || !state || !state.absoluteOffset) continue;
        const room = points[Math.floor(points.length / 2)], was = cell.geometry.offset || { x: 0, y: 0 };
        const geo = cell.geometry.clone();
        geo.offset = new Point((room.x + v.translate.x) - state.absoluteOffset.x / v.scale + was.x,
          (room.y + v.translate.y) - state.absoluteOffset.y / v.scale + was.y);
        m.setGeometry(cell, geo);
      }
    });
  }

  let measure = null;
  function textWidth(text) { // as drawn on the state machine: 12px system-ui
    if (!measure) { measure = document.createElement("canvas").getContext("2d"); measure.font = "12px system-ui, sans-serif"; }
    return Math.ceil(measure.measureText(text).width);
  }

  // Where you put a state is where it stays (ADR-0174). The first gesture on the diagram (placing, moving, renaming,
  // removing) pins every shape where it is drawn, by cell id, so nothing jumps when the plan redraws; a state you
  // place goes exactly where you clicked or dropped it, and one you drag stays where you let go. Positions are
  // presentation only: they never reach the model or the plan. Tidy forgets them and lays the diagram out again.
  const placed = {}, bent = {}; // cell id -> [x, y] top-left in graph units; transition cell id -> bend points
  let layoutKey = "", lastView = null;

  function layoutStore() {
    const key = `playide.layout.v1:${packInfo ? packInfo.id : $("model-name").textContent}`; // the pack id, as the draft is kept
    if (key === layoutKey) return;
    layoutKey = key;
    for (const k of Object.keys(placed)) delete placed[k];
    for (const k of Object.keys(bent)) delete bent[k];
    try { const kept = JSON.parse(localStorage.getItem(key) || "{}"); Object.assign(placed, kept.placed || {}); Object.assign(bent, kept.bent || {}); } catch { /* storage blocked: positions last this visit only */ }
  }

  function hasMoves(which) {
    return which === "states" ? Object.keys(placed).length > 0 : Boolean(movedOn[which] && Object.keys(movedOn[which]).length);
  }

  function saveLayout() {
    try { localStorage.setItem(layoutKey, JSON.stringify({ placed, bent })); } catch { /* storage blocked */ }
    const tidy = $("tidy");
    if (tidy) tidy.hidden = !hasMoves(tab);
  }

  function pinAll() {
    if (!graph || hooks.diffGraph && hooks.diffGraph()) return;
    for (const cell of Object.values(graph.getDataModel().cells)) {
      if (!cell.id || !cell.geometry) continue;
      if (cell.id === "initial" || cell.id.startsWith("state:")) placed[cell.id] = [cell.geometry.x, cell.geometry.y];
      else if (cell.id.startsWith("transition:") && !(cell.id in bent)) bent[cell.id] = (cell.geometry.points || []).map((pt) => [pt.x, pt.y]);
    }
    saveLayout();
  }

  // Pinned shapes keep their place; any other state (one the AI added, say) goes below them, in the layout's order.
  function arrange(workflow, place) {
    layoutStore();
    const ids = ["initial", ...workflow.states.map((x) => "state:" + x)], pinned = ids.filter((id) => placed[id]);
    const dagreId = (id) => (id === "initial" ? "__initial" : id.slice(6));
    const below = pinned.length ? Math.max(...pinned.map((id) => placed[id][1])) + STATE.height + 70 : 0;
    const top = Math.min(...ids.filter((id) => !placed[id]).map((id) => place.at(dagreId(id))[1]), Infinity);
    const at = (id) => placed[id] || (pinned.length ? [place.at(dagreId(id))[0], below + place.at(dagreId(id))[1] - top] : place.at(dagreId(id)));
    const bends = (t) => {
      const id = "transition:" + t.id, ends = [placed["state:" + t.from_state], placed["state:" + t.to_state]];
      if (ends[0] && ends[1]) return (bent[id] || []).map(([x, y]) => ({ x, y }));
      return ends[0] || ends[1] ? [] : place.bends(t);
    };
    return { at, bends };
  }

  // You moved shapes: keep them there, and let the edges that touch them route straight again.
  function moved(cells) {
    const ids = new Set(cells.filter((c) => c.isVertex()).map((c) => c.id));
    if (!ids.size) return;
    pinAll();
    graph.batchUpdate(() => straighten(graph, ids));
    for (const cell of Object.values(graph.getDataModel().cells)) {
      if (cell.isEdge() && cell.id && cell.id.startsWith("transition:") && !(cell.geometry.points || []).length) bent[cell.id] = [];
    }
    saveLayout();
  }

  // The plan banner (and the panel below) change where the canvas sits on the page. Keep the drawing still on the
  // screen when that happens, so a state you just placed does not slide away from where you put it.
  let canvasTop = null, canvasSize = null;
  function holdStill() {
    if (!$("canvas").offsetParent) return; // hidden behind another tab: nothing on screen to hold
    const top = $("canvas").getBoundingClientRect().top, size = `${$("canvas").clientWidth} ${$("canvas").clientHeight}`;
    // Nobody placed a shape or moved the view since it was fitted: fit the canvas as it is now (the plan banner or a
    // panel made it shorter), so neither the top nor the foot of the diagram is cut off.
    const untouched = graph && graph.view && tab === "states" && !Object.keys(placed).length && fitted.view === viewOf(graph);
    if (untouched && canvasSize !== null && size !== canvasSize && top === canvasTop) fit(); // grew where it stands, as on first load
    else if (graph && graph.view && canvasTop !== null && top !== canvasTop) {
      const v = graph.view, was = graph.getGraphBounds(), before = was.y, high = +canvasSize.split(" ")[1];
      v.setTranslate(v.translate.x, v.translate.y - (top - canvasTop) / v.scale);
      // ... and holding still never slides the top of the diagram (the initial state) under the banner that moved it.
      const after = graph.getGraphBounds().y, floor = Math.min(before, MARGIN);
      if (before >= 0 && after < floor) v.setTranslate(v.translate.x, v.translate.y + (floor - after) / v.scale);
      // A diagram that was all on screen stays all on screen: when the banner leaves too little room, it is fitted again.
      const now = graph.getGraphBounds(), tall = $("canvas").clientHeight;
      if (was.y >= 0 && was.y + was.height <= high && (now.y < 0 || now.y + now.height > tall)) fit();
    }
    canvasTop = top;
    canvasSize = size;
  }

  // The class, use case and component diagrams are drawn from the model, but a shape you drag there stays where you
  // let go too, for this visit, through preview redraws. Edges that touch it route straight again.
  const movedOn = { classes: {}, usecases: {}, components: {} };
  function straighten(g, ids) {
    const inside = (cell) => { for (let c = cell; c; c = c.parent) if (ids.has(c.id)) return true; return false; };
    for (const cell of Object.values(g.getDataModel().cells)) {
      if (!cell.isEdge() || !(inside(cell.source) || inside(cell.target)) || !cell.geometry) continue;
      const geo = cell.geometry.clone();
      geo.points = [];
      if (cell.id && cell.id.startsWith("transition:")) geo.offset = null; // a straight line's label sits halfway again
      g.getDataModel().setGeometry(cell, geo);
    }
  }

  function keepMoves(g, key) {
    const kept = movedOn[key], m = g.getDataModel(), handler = g.getPlugin("SelectionHandler");
    g.isCellMovable = (cell) => cell.isVertex() && cell.style.movable !== false;
    if (handler) { // pressing on a class's attribute row (or any fixed part of a shape) takes hold of the shape itself
      const initial = handler.getInitialCellForEvent.bind(handler);
      handler.getInitialCellForEvent = (me) => {
        let cell = initial(me);
        while (cell && cell.style && cell.style.selectable === false && cell.parent && cell.parent.isVertex()) cell = cell.parent;
        return cell;
      };
    }
    g.batchUpdate(() => {
      for (const [id, [x, y]] of Object.entries(kept)) {
        const cell = m.getCell(id);
        if (!cell || !cell.geometry) continue;
        const geo = cell.geometry.clone();
        geo.x = x;
        geo.y = y;
        m.setGeometry(cell, geo);
      }
      straighten(g, new Set(Object.keys(kept)));
    });
    g.addListener(maxgraph.InternalEvent.CELLS_MOVED, (_sender, evt) => {
      const cells = (evt.getProperty("cells") || []).filter((c) => c.isVertex() && c.id);
      for (const c of cells) kept[c.id] = [c.geometry.x, c.geometry.y];
      g.batchUpdate(() => straighten(g, new Set(cells.map((c) => c.id))));
      $("tidy").hidden = !hasMoves(tab);
    });
  }

  function tidy() {
    for (const kept of Object.values(movedOn)) for (const k of Object.keys(kept)) delete kept[k];
    for (const k of Object.keys(placed)) delete placed[k];
    for (const k of Object.keys(bent)) delete bent[k];
    saveLayout();
    redrawAll(model);
    if (plan && plan.previewing && plan.result) highlight(plan.result.diff);
    for (const which of Object.keys(DIAGRAMS)) markRipple(which);
  }

  function label(t) { return `${t.action} [${t.role}]`; }

  function draw(workflow) {
    const { Graph, InternalEvent } = maxgraph;
    const box = $("canvas");
    InternalEvent.disableContextMenu(box);
    graph = new Graph(box);
    graph.setConnectable(false);
    graph.setCellsEditable(false);
    graph.setCellsDisconnectable(false);
    graph.setDropEnabled(false);
    graph.setPanning(true);
    graph.getPlugin("SelectionHandler").scrollOnMove = false; // a state dropped near the edge stays there; the view does not slide to show all of it
    graph.setTooltips(true);
    graph.getTooltipForCell = (cell) => tooltip(cell);
    graph.isCellMovable = (cell) => cell.isVertex(); // states and the initial dot move; edges follow
    const parent = graph.getDefaultParent(), place = arrange(workflow, layout(workflow)), cells = {};
    const font = { fontFamily: "system-ui, sans-serif", fontColor: "#1b2130" };
    graph.batchUpdate(() => {
      const initial = graph.insertVertex({ parent, id: "initial", position: place.at("initial"), size: [INITIAL, INITIAL],
        style: { shape: "ellipse", fillColor: "#1b2130", strokeColor: "#1b2130", resizable: false, editable: false } });
      for (const s of workflow.states) {
        cells[s] = graph.insertVertex({ parent, id: "state:" + s, value: s, position: place.at("state:" + s), size: [STATE.width, STATE.height],
          style: { ...font, rounded: true, arcSize: 22, fillColor: "#eef2ff", strokeColor: "#5b74d6", strokeWidth: 1.5, fontSize: 14, fontStyle: 1, resizable: false } });
      }
      graph.insertEdge({ parent, id: "initial-edge", source: initial, target: cells[workflow.initial_state],
        style: { strokeColor: "#1b2130", endArrow: "open", endSize: 8, edgeStyle: "orthogonalEdgeStyle", rounded: true } });
      for (const t of workflow.transitions) {
        const edge = graph.insertEdge({ parent, id: "transition:" + t.id, value: label(t), source: cells[t.from_state], target: cells[t.to_state],
          style: { ...font, fontSize: 12, strokeColor: "#4a5568", endArrow: "open", endSize: 9, curved: true,
            labelBackgroundColor: "#fbfcfe", labelPosition: "center" } });
        edge.geometry.points = place.bends(t).map((p) => new maxgraph.Point(p.x, p.y));
      }
    });
    liftLabels(graph);
    for (const cell of Object.values(graph.getDataModel().cells)) if (cell.id) base[cell.id] = { style: { ...cell.style }, value: cell.value };
    graph.getSelectionModel().addListener(InternalEvent.CHANGE, () => {
      const cell = graph.getSelectionCell();
      select(cell ? cell.id : "", false);
    });
    wireCanvas(graph);
    if (lastView && Object.keys(placed).length) graph.view.scaleAndTranslate(lastView.scale, lastView.x, lastView.y);
    else fit();
    lastView = null;
    canvasTop = box.offsetParent ? box.getBoundingClientRect().top : null; // the drawing is placed for where the canvas is now
    canvasSize = box.offsetParent ? `${box.clientWidth} ${box.clientHeight}` : null;
    for (const f of hooks.redraw) f();
  }

  function tooltip(cell) {
    if (!cell || !cell.id) return "";
    if (cell.id.startsWith("transition:")) {
      const t = transition(cell.id.slice(11));
      return `${t.action}: ${t.from_state} → ${t.to_state}, by ${t.role}`;
    }
    return cell.id.startsWith("state:") ? `State ${cell.id.slice(6)}` : "Initial state";
  }

  function transition(id) { return model.transitions.find((t) => t.id === id); }

  const current = () => (hooks.diffGraph && hooks.diffGraph()) || ({ states: graph, classes: classGraph, usecases: useCaseGraph, review: PlayReview.graph(),
    components: (hooks.componentGraph && hooks.componentGraph()) || componentGraph, // the System lens (play-landscape.js, ADR-0203)
    sequences: hooks.sequenceGraph && hooks.sequenceGraph() })[tab];
  const PANELS = { states: "canvas", sequences: "sequences", classes: "class-canvas", usecases: "usecase-canvas", screens: "screens", components: "component-canvas", laws: "laws", tests: "tests", review: "review", access: "access-panel" };
  const HINTS = {
    states: "Pick State, Transition or Initial in the palette, then click the diagram (or drag it there). Double-click empty space for a new state, a state to rename it. Changes join the plan for you to preview; nothing is saved.",
    sequences: "The Tests tab's scenarios as UML sequences, each step run through the kernel: a step the model can't do is red with the kernel's reason. Select one to change it; a step in a neg must be refused.",
    classes: "Select a class to see its attributes and associations. Only the «record» class is built: its attributes are the app's form. Grey classes and the associations are drawn, not built. An amber attribute stands in for an association: the app checks its value, not that the other object exists.",
    usecases: "Select a use case to inspect it. Double-click one to design its screen.",
    screens: "Design each use case's screen. The design check runs as you edit; Build & run uses these screens.",
    components: "The built app's components, read from its generated files: every line is an import, a route or a file read.",
    laws: "The pack's laws: what this model must never do, whatever is drawn. Each is proved over every run the kernel allows, by every class of actor (each role, active or not, assigned or not).",
    tests: "The pack's test cases: scenarios of who does what and what must happen, each step run by the kernel on the model shown.",
    access: "Who can do what, from each state. Every cell is tried in the kernel with the pack's fixture actors; a previewed plan's changes are flagged.",
    review: "Review the change shown against the model in force: look at each change, predict what the kernel does, then decide. Nothing is approved from here.",
  };

  // Fitting never shrinks a diagram below READABLE (labels of about 10px and up): when the canvas is short, as with the
  // Simulation panel open, the diagram keeps that size and starts at its top left (where the initial state is), and the
  // rest is a drag away. Only the Fit button, asked for "all of it", may go smaller (#139).
  const READABLE = 0.8, MARGIN = 24;
  function fit(all) {
    const g = current();
    if (!g) return;
    // The Components tab's lens bar floats over the top of its diagram: leave room for it, and draw a small system no
    // larger than life, so one workflow is not blown up beside the other tabs.
    const bar = tab === "components" && !$("component-bar").hidden ? $("component-bar").offsetHeight + 16 : 0;
    const margin = Math.max(MARGIN, bar), most = bar ? 1 : 1.4, v = g.view, box = g.container;
    // Measured, not maxGraph's fitCenter: labels do not scale exactly with the view, so measure again after scaling
    // and take off what still overflows (a 1280-pixel screen clipped the foot of the state machine by 3 pixels).
    const floor = all === true ? 0 : Math.min(READABLE, most);
    for (let pass = 0; pass < 2; pass++) {
      const b = g.getGraphBounds();
      if (!b.width || !b.height) return;
      const w = b.width / v.scale, h = b.height / v.scale, x0 = b.x / v.scale - v.translate.x, y0 = b.y / v.scale - v.translate.y;
      const wide = box.clientWidth - 2 * margin, high = box.clientHeight - 2 * margin;
      const k = Math.max(floor, pass ? v.scale * Math.min(1, wide / b.width, high / b.height) : Math.min(most, wide / w, high / h));
      if (pass && k === v.scale) break;
      const along = (space, size, start) => (size * k <= space - 2 * margin ? (space / k - size) / 2 - start : margin / k - start);
      v.scaleAndTranslate(k, along(box.clientWidth, w, x0), along(box.clientHeight, h, y0));
    }
    fitted.view = g === graph ? viewOf(g) : null;
  }
  const fitted = { view: null }; // the state machine's view as fit() left it, so holdStill can tell a view nobody moved
  const viewOf = (g) => `${g.view.scale.toFixed(4)} ${g.view.translate.x.toFixed(2)} ${g.view.translate.y.toFixed(2)}`;

  // Bring cells into view, as a debugger follows the current line: the view pans (never zooms) only when one is outside
  // the canvas, so a short canvas (the Run or Simulation panel open) still shows what the run is doing (play-run.js).
  function follow(ids) {
    if (!graph || !$("canvas").offsetParent) return;
    const v = graph.view, box = graph.container, m = graph.getDataModel(), pad = 16;
    const boxes = ids.map((id) => m.getCell(id)).filter(Boolean).map((c) => v.getState(c)).filter(Boolean).map((st) => st.text && st.cell.isEdge() ? st.text.boundingBox || st : st);
    if (!boxes.length) return;
    // Keep them all in view; when they do not fit together, the first (the current state) wins over the line taken.
    const shift = (lo, hi, size) => (lo >= pad && hi <= size - pad ? 0 : lo < pad ? pad - lo : size - pad - hi);
    const along = (start, length, size) => {
      const lo = Math.min(...boxes.map((b) => b[start])), hi = Math.max(...boxes.map((b) => b[start] + b[length]));
      return hi - lo <= size - 2 * pad ? shift(lo, hi, size) : shift(boxes[0][start], boxes[0][start] + boxes[0][length], size);
    };
    const dx = along("x", "width", box.clientWidth), dy = along("y", "height", box.clientHeight);
    if (dx || dy) v.setTranslate(v.translate.x + dx / v.scale, v.translate.y + dy / v.scale);
  }

  function row(dl, term, value) { dl.append(el("dt", term), el("dd", value)); }

  function inspect(id) {
    const box = $("inspector");
    box.replaceChildren();
    if (!id || id === "initial" || id === "initial-edge") {
      box.append(el("p", id ? `Every record starts in ${model.initial_state}.` : "Select a state or transition.", { class: "muted" }));
      return;
    }
    const dl = el("dl");
    if (id.startsWith("class:")) {
      inspectClass(id.slice(6), box);
      return;
    }
    if (id.startsWith("enum:")) {
      box.append(el("h3", `«enumeration» ${id.slice(5)}`), el("p", `The states a ${data.record} can be in: ${model.states.join(", ")}. Read from the state machine, so a state you draw there appears here.`, { class: "muted" }));
      return;
    }
    if (id.startsWith("system:") && window.PlayLandscape) { // the System lens of the Components tab (ADR-0203)
      window.PlayLandscape.inspect(id.slice(7), box);
      return;
    }
    if (id.startsWith("deploy:") && window.PlayDeployment) { // the Deployment lens of the Components tab (ADR-0206)
      window.PlayDeployment.inspect(id.slice(7), box);
      return;
    }
    if (id.startsWith("component:")) {
      inspectComponent(id.slice(10), box);
      return;
    }
    if (id.startsWith("role:")) { // an actor: play-roles.js says what it may do and runs the app as one (ADR-0215)
      box.append(el("h3", "Actor " + id.slice(5)));
      for (const f of hooks.inspect) f(id, box);
      return;
    }
    if (id === "usecase:create") {
      box.append(el("h3", "Use case: create a record"), el("p", `Any fixture actor may start a record. It starts in ${model.initial_state}.`, { class: "muted" }));
      box.append(screenLink(null));
      return;
    }
    if (id.startsWith("state:")) {
      const s = id.slice(6);
      const out = model.transitions.filter((t) => t.from_state === s), into = model.transitions.filter((t) => t.to_state === s);
      box.append(el("h3", "State " + s));
      row(dl, "Initial", s === model.initial_state ? "yes" : "no");
      row(dl, "Leaves by", out.map(label).join(", ") || "nothing (an end state)");
      row(dl, "Entered by", into.map(label).join(", ") || (s === model.initial_state ? "creation" : "nothing (unreachable)"));
      box.append(dl, stateTools(s));
      for (const f of hooks.inspect) f(id, box);
      return;
    } else {
      const t = transition(id.slice(11));
      box.append(el("h3", `${t.action} (${t.id})`));
      row(dl, "Path", `${t.from_state} → ${t.to_state}`);
      row(dl, "Who", t.role + kindNote(t.role));
      row(dl, "Guards", t.guards.join(", "));
      row(dl, "Effects", t.required_effects.join(", ") || "none");
      row(dl, "Never", t.forbidden_effects.join(", ") || "nothing listed");
      box.append(dl, screenLink(t.action), transitionTools(t));
      for (const f of hooks.inspect) f(id, box);
      return;
    }
    box.append(dl);
  }

  function select(id, fromOutline) {
    // Choosing in the outline moves the selection: the other diagram lets go of what it had, so going back to it shows
    // nothing selected rather than a stale handle beside an inspector that says something else.
    if (fromOutline) {
      const other = id.startsWith("class:") ? graph : classGraph;
      if (other && !other.isSelectionEmpty()) other.clearSelection();
    }
    selected = id;
    for (const b of document.querySelectorAll(".outline button")) b.setAttribute("aria-current", String(b.dataset.id === id));
    inspect(id);
    document.dispatchEvent(new CustomEvent("playide:select", { detail: id }));
    if (fromOutline) {
      showTab(id.startsWith("class:") ? "classes" : "states");
      const target = current(), cell = target && target.getDataModel().getCell(id);
      if (cell) target.setSelectionCell(cell);
    }
  }

  function outline() {
    const fill = (list, items) => {
      $(list).replaceChildren();
      for (const [id, text] of items) {
        const button = el("button", text, { type: "button", "data-id": id, "aria-current": "false" });
        button.addEventListener("click", () => select(id, true));
        const li = el("li");
        li.append(button);
        $(list).append(li);
      }
    };
    fill("outline-states", model.states.map((s) => ["state:" + s, s + (s === model.initial_state ? " (initial)" : "")]));
    fill("outline-transitions", model.transitions.map((t) => ["transition:" + t.id, label(t)]));
    fill("outline-classes", data ? data.entities.map((e) => ["class:" + e.name, e.name + (e.name === data.record ? " «record»" : "")]) : []);
    if (!data) $("outline-classes").replaceChildren(el("li", "No data model yet", { class: "muted" }));
    // A role is an actor of the use case diagram: choosing one shows what it may do, its screens and its fixture
    // actors in the inspector (play-roles.js, ADR-0215), without leaving the diagram on screen.
    $("outline-roles").replaceChildren(...[...new Set(model.transitions.map((t) => t.role))].map((r) => {
      const button = el("button", r, { type: "button", "data-id": "role:" + r, "aria-current": "false", title: `What ${r} may do and sees` });
      button.addEventListener("click", () => select("role:" + r, false));
      const li = el("li");
      li.append(button);
      return li;
    }));
  }

  // Class diagram (ADR-0153): the pack's data model in UML class notation. The record class is what moves through
  // the state machine; its attributes become the built app's form, checked by the data model on the server.
  const typeName = { text: "String", number: "Number", date: "Date", boolean: "Boolean" };
  // UML attribute notation: name: Type [multiplicity]; an optional value is [0..1], a choice lists its literals.
  const attributeLine = (a) => `${a.name}: ${a.type === "choice" ? `{${a.choices.join(", ")}}` : typeName[a.type]}${a.required ? "" : " [0..1]"}`;
  const ROW = 20, HEAD = 34;
  const enumName = () => data.record + "State"; // the record's states as a UML enumeration, read from the state machine
  // The enumeration's literals: the states, or while the Changes view is on, the states of both models with their status.
  const literalsOf = () => (shownChange ? shownChange.states.map((x) => [x.name, x.status]) : model.states.map((x) => [x, "same"]));
  // A class's attribute rows. While a plan that changes the class diagram is previewed (ADR-0202), each row says whether
  // the plan adds or changes it, and an attribute the plan removes stays as a struck-through ghost row.
  function rowsOf(e) {
    const old = savedData && data !== savedData ? savedData.entities.find((x) => x.name === e.name) : null;
    if (!old) return e.attributes.map((a) => [a, "same"]);
    const was = new Map(old.attributes.map((a) => [a.name, a]));
    const rows = e.attributes.map((a) => [a, !was.has(a.name) ? "added" : attributeLine(was.get(a.name)) !== attributeLine(a) ? "changed" : "same"]);
    return rows.concat(old.attributes.filter((a) => !e.attributes.some((x) => x.name === a.name)).map((a) => [a, "removed"]));
  }
  const ROW_LOOK = { added: { fontColor: "#17734a", fontStyle: 1 }, changed: { fontColor: "#a35f00", fontStyle: 1 }, removed: { fontColor: "#8a94a6", fontStyle: 8 } };
  const ROW_MARK = { added: "+ ", changed: "~ ", removed: "− " };
  // What the built app does with the class diagram (#145): the server says which classes and associations are drawn but
  // not built, and which record attributes stand in for an association. A previewed plan carries its own report.
  let savedBuild = null;
  const classBuild = () => (plan && plan.previewing && plan.result.class_build) || (data === savedData ? savedBuild : null);
  const standsIn = (name) => ((classBuild() || {}).findings || []).filter((f) => f.subject[1] === "attribute:" + name);
  const widthOf = (e) => Math.max(200, e.name.length * 9 + 60, ...rowsOf(e).map(([a]) => attributeLine(a).length * 7 + 40));

  function classLayout() {
    const g = new dagre.graphlib.Graph({ multigraph: true });
    g.setGraph({ rankdir: "LR", nodesep: 50, ranksep: 140, marginx: 30, marginy: 30 });
    g.setDefaultEdgeLabel(() => ({}));
    for (const e of data.entities) g.setNode(e.name, { width: widthOf(e), height: HEAD + ROW * Math.max(1, rowsOf(e).length) + 8 });
    data.associations.forEach((a, i) => g.setEdge(a.source, a.target, { width: 90, height: 20 }, "a" + i));
    const literals = literalsOf();
    g.setNode(enumName(), { width: Math.max(200, ...literals.map(([x]) => x.length * 8 + 30)), height: HEAD + ROW * literals.length + 8 });
    g.setEdge(data.record, enumName(), { width: 90, height: 20 }, "state");
    dagre.layout(g);
    return (name) => { const n = g.node(name); return [n.x - n.width / 2, n.y - n.height / 2, n.width, n.height]; };
  }

  // Every vertex here is placed at a fixed size, so the browser need not measure it: maxGraph asks the SVG for each
  // shape's box (getBBox) and for each attribute or literal row's text, and at the kernel's limits (40 classes of up
  // to 40 attributes) those measurements were most of the time a diagram took to draw (ADR-0199).
  function lean(g) {
    const renderer = g.cellRenderer, createShape = renderer.createShape.bind(renderer), createLabel = renderer.createLabel.bind(renderer);
    renderer.createShape = (state) => {
      const shape = createShape(state);
      if (shape && state.cell.isVertex()) shape.useSvgBoundingBox = false;
      return shape;
    };
    renderer.createLabel = (state, value) => {
      createLabel(state, value);
      if (state.text && /^(attr|literal):/.test(state.cell.id || "")) state.text.ignoreStringSize = true;
    };
  }

  function drawClasses() {
    if (classGraph || !data) return;
    const { Graph, InternalEvent, Point } = maxgraph;
    const box = $("class-canvas");
    InternalEvent.disableContextMenu(box);
    classGraph = new Graph(box);
    classGraph.options.foldingEnabled = false; // classes are not collapsible, and the fold icon is not shipped
    classGraph.setConnectable(false);
    classGraph.setCellsEditable(false);
    classGraph.setCellsDisconnectable(false);
    classGraph.setCellsResizable(false);
    classGraph.setDropEnabled(false);
    classGraph.setPanning(true);
    lean(classGraph);
    const parent = classGraph.getDefaultParent(), at = classLayout(), cells = {}, drawnOnly = new Set((classBuild() || {}).drawn_only || []);
    const font = { fontFamily: "system-ui, sans-serif", fontColor: "#1b2130" };
    const DRAWN_ONLY = { fillColor: "#f4f5f8", strokeColor: "#9aa3b5", fontColor: "#4a5568" }; // drawn, not built
    classGraph.batchUpdate(() => {
      for (const e of data.entities) {
        const [x, y, w, h] = at(e.name), record = e.name === data.record;
        const box = cells[e.name] = classGraph.insertVertex({ parent, id: "class:" + e.name, value: (record ? "«record»\n" : "") + e.name,
          position: [x, y], size: [w, h], style: { ...font, shape: "swimlane", startSize: HEAD, horizontal: true, fontStyle: 1, fontSize: 13,
            fillColor: record ? "#dfe6ff" : "#eef2ff", swimlaneFillColor: "#ffffff", strokeColor: "#5b74d6", rounded: false, collapsible: false,
            ...(drawnOnly.has(e.name) ? DRAWN_ONLY : {}) } });
        rowsOf(e).forEach(([a, status], i) => classGraph.insertVertex({ parent: box, id: `attr:${e.name}.${a.name}`, value: (ROW_MARK[status] || "") + attributeLine(a),
          position: [8, HEAD + 4 + i * ROW], size: [w - 16, ROW], style: { ...font, fontSize: 12, align: "left", strokeColor: "none",
            fillColor: "none", movable: false, selectable: false, ...(status === "same" && standsIn(`${e.name}.${a.name}`).length ? { fontColor: "#a35f00" } : {}),
            ...(ROW_LOOK[status] || {}) } }));
      }
      const [ex, ey, ew, eh] = at(enumName());
        const literals = cells[enumName()] = classGraph.insertVertex({ parent, id: "enum:" + enumName(), value: `«enumeration»\n${enumName()}`,
          position: [ex, ey], size: [ew, eh], style: { ...font, shape: "swimlane", startSize: HEAD, horizontal: true, fontStyle: 1, fontSize: 13,
            fillColor: "#f4f1ff", swimlaneFillColor: "#ffffff", strokeColor: "#7a5bd6", rounded: false, collapsible: false } });
        literalsOf().forEach(([x, status], i) => classGraph.insertVertex({ parent: literals, id: "literal:" + x, value: changeMark(status) + x,
          position: [8, HEAD + 4 + i * ROW], size: [ew - 16, ROW], style: { ...font, fontSize: 12, align: "left", strokeColor: "none", fillColor: "none",
            movable: false, selectable: false, ...changeLook(status, "text") } }));
      classGraph.insertEdge({ parent, id: "enum-edge", value: "state", source: cells[data.record], target: literals,
        style: { ...font, fontSize: 12, strokeColor: "#7a5bd6", endArrow: "open", labelBackgroundColor: "#fbfcfe" } });
      data.associations.forEach((a, i) => {
        const diamond = a.kind === "association" ? {} : { startArrow: "diamond", startSize: 14, startFill: a.kind === "composition" };
        const edge = classGraph.insertEdge({ parent, id: "assoc:" + i, value: a.role, source: cells[a.source], target: cells[a.target],
          style: { ...font, fontSize: 12, strokeColor: "#4a5568", endArrow: "none", labelBackgroundColor: "#fbfcfe", ...diamond } });
        for (const [where, text] of [[-0.8, a.source_multiplicity], [0.8, a.target_multiplicity]]) {
          const end = classGraph.insertVertex({ parent: edge, value: text, position: [where, 0], size: [0, 0], relative: true,
            style: { ...font, fontSize: 11, labelBackgroundColor: "#fbfcfe", selectable: false, movable: false } });
          end.geometry.offset = new Point(0, -12);
        }
      });
    });
    classGraph.getSelectionModel().addListener(InternalEvent.CHANGE, () => {
      const cell = classGraph.getSelectionCell();
      const id = cell && cell.id && cell.id.startsWith("assoc:") ? "class:" + data.associations[+cell.id.slice(6)].source : cell ? cell.id : "";
      select(id && (id.startsWith("class:") || id.startsWith("enum:")) ? id : "", false);
    });
    keepMoves(classGraph, "classes");
  }

  function inspectClass(name, box) {
    const e = data.entities.find((x) => x.name === name);
    box.append(el("h3", `Class ${name}${name === data.record ? " «record»" : ""}`));
    if (e.description) box.append(el("p", e.description, { class: "muted" }));
    const dl = el("dl");
    for (const a of e.attributes) row(dl, a.name, `${a.type === "choice" ? "one of " + a.choices.join(", ") : a.type}${a.required ? ", required" : ""}${a.type === "text" ? `, ≤ ${a.max_length}` : ""}`);
    for (const a of data.associations.filter((x) => x.source === name || x.target === name)) {
      row(dl, a.kind, `${a.source} [${a.source_multiplicity}] — ${a.role || ""} → ${a.target} [${a.target_multiplicity}]`);
    }
    box.append(dl);
    if (name === data.record) box.append(el("p", "Records of this class move through the state machine. Its attributes are the built app's form, checked on the server.", { class: "muted" }));
    const build = classBuild();
    if (!build) return;
    for (const f of build.findings.filter((x) => x.subject[0] === "class:" + name)) box.insertBefore(el("p", "To consider: " + f.message, { class: "consider" }), dl);
    if (build.drawn_only.includes(name)) box.append(el("p", `Drawn, not built: the app stores ${data.record} records only, so it never stores or looks up a ${name}.`, { class: "muted" }));
    const links = build.associations.filter((a) => a.source === name || a.target === name);
    if (links.length) box.append(el("p", links.map((a) => a.message).join(" "), { class: "muted small" }));
    box.append(el("p", build.limits.join(" "), { class: "muted small" }));
  }

  // Use case diagram: a view of the same workflow. Each role is an actor; each transition's action is a use case
  // inside the system boundary, associated with the role allowed to take it. Nothing here is a second source.
  function workflowOrder() {
    const order = [], seen = new Set([model.initial_state]), queue = [model.initial_state];
    while (queue.length) {
      const s = queue.shift();
      for (const t of model.transitions.filter((x) => x.from_state === s).sort((a, b) => a.id.localeCompare(b.id))) {
        order.push(t);
        if (!seen.has(t.to_state)) { seen.add(t.to_state); queue.push(t.to_state); }
      }
    }
    return [...order, ...model.transitions.filter((t) => !order.includes(t))];
  }

  // What the use case diagram draws: the model's use cases, or while the Changes view is on, the server's union of both
  // models (ADR-0176), where a use case or actor the change removes stays as a ghost and a moved association keeps its old line.
  function useCaseShape() {
    if (!shownChange) {
      const flow = workflowOrder();
      return { cases: flow.map((t) => ({ ...t, status: "same" })), actors: [...new Set(flow.map((t) => t.role))].map((name) => ({ name, status: "same" })),
        links: flow.map((t) => ({ role: t.role, case: t.id, status: "same" })) };
    }
    const order = workflowOrder().map((t) => t.action), rank = (c) => (order.includes(c.action) ? order.indexOf(c.action) : order.length);
    const u = shownChange.use_cases;
    return { cases: [...u.cases].sort((a, b) => rank(a) - rank(b)), actors: u.actors, links: u.links };
  }

  const ACTOR_LOOK = { human: {}, agent: { fill: "#f3edff", stroke: "#6b46c1" }, timer: { fill: "#fff7e6", stroke: "#b7791f" },
    system: { fill: "#eef2f6", stroke: "#4a5568" } };

  function drawUseCases() {
    if (useCaseGraph) return;
    const { Graph, InternalEvent } = maxgraph;
    const box = $("usecase-canvas");
    InternalEvent.disableContextMenu(box);
    useCaseGraph = new Graph(box);
    for (const setting of ["setConnectable", "setCellsEditable", "setCellsDisconnectable", "setCellsResizable", "setDropEnabled"]) useCaseGraph[setting](false);
    useCaseGraph.setPanning(true);
    const parent = useCaseGraph.getDefaultParent(), shape = useCaseShape();
    const roles = shape.actors.map((a) => a.name), actorStatus = Object.fromEntries(shape.actors.map((a) => [a.name, a.status]));
    // Group each role's use cases together, in workflow order, and put the actor beside its group: no line crosses a use case.
    // A use case whose association moves sits with its new actor; a removed one with the actor it had.
    const cases = roles.flatMap((role) => shape.cases.filter((t) => t.role === role));
    const font = { fontFamily: "system-ui, sans-serif", fontColor: "#1b2130" };
    const GAP = 76, TOP = 70, boundary = { x: 260, w: 360 }, height = TOP + (cases.length + 1) * GAP;
    const rowY = (i) => TOP + (i + 1) * GAP - 4;
    useCaseGraph.batchUpdate(() => {
      useCaseGraph.insertVertex({ parent, id: "system", value: document.getElementById("model-name").textContent.split(" · ")[0],
        position: [boundary.x, 10], size: [boundary.w, height], style: { ...font, verticalAlign: "top", fontStyle: 1, fontSize: 13,
          fillColor: "#fbfcfe", strokeColor: "#4a5568", selectable: false, movable: false } });
      const cells = {};
      // Starting a record is a use case too; any fixture actor may start one, so it has no association.
      useCaseGraph.insertVertex({ parent, id: "uc:create", value: `Create ${data ? data.record : "record"}`, position: [boundary.x + 60, TOP - 4],
        size: [boundary.w - 120, 48], style: { ...font, shape: "ellipse", fillColor: "#ffffff", strokeColor: "#5b74d6", fontSize: 13 } });
      cases.forEach((t, i) => {
        cells[t.id] = useCaseGraph.insertVertex({ parent, id: "uc:" + t.id, value: changeMark(t.status) + t.action, position: [boundary.x + 60, rowY(i)],
          size: [boundary.w - 120, 48], style: { ...font, shape: "ellipse", fillColor: "#eef2ff", strokeColor: "#5b74d6", fontSize: 13, ...changeLook(t.status, "box") } });
      });
      roles.forEach((role, i) => {
        const mine = cases.map((t, j) => [t, j]).filter(([t]) => t.role === role);
        const near = mine.length ? mine : cases.map((t, j) => [t, j]).filter(([t]) => t.was_role === role); // an actor left with only a moved line
        const y = near.reduce((sum, [, j]) => sum + rowY(j), 0) / Math.max(1, near.length) - 8;
        const left = i % 2 === 0, kind = roleKind(role), look = ACTOR_LOOK[kind];
        const actor = kind === "human"
          ? useCaseGraph.insertVertex({ parent, id: "role:" + role, value: role, position: [left ? 90 : boundary.x + boundary.w + 120, y],
            size: [36, 64], style: { ...font, shape: "actor", fillColor: "#ffffff", strokeColor: "#1b2130", verticalLabelPosition: "bottom",
              verticalAlign: "top", fontSize: 13, ...changeLook(actorStatus[role], "actor") } })
          : useCaseGraph.insertVertex({ parent, id: "role:" + role, value: `«${kind}»\n${role}`, position: [left ? 40 : boundary.x + boundary.w + 70, y + 8],
            size: [136, 48], style: { ...font, shape: "rectangle", rounded: kind === "agent", whiteSpace: "wrap", fillColor: look.fill,
              strokeColor: look.stroke, fontSize: 12, ...changeLook(actorStatus[role], "actor") } });
        for (const link of shape.links.filter((l) => l.role === role)) {
          useCaseGraph.insertEdge({ parent, source: actor, target: cells[link.case], style: { strokeColor: "#4a5568", endArrow: "none", ...changeLook(link.status, "line") } });
        }
      });
    });
    useCaseGraph.getSelectionModel().addListener(InternalEvent.CHANGE, () => {
      const cell = useCaseGraph.getSelectionCell(), id = cell && cell.id && cell.id.startsWith("uc:") ? cell.id.slice(3) : "";
      if (shownChange) { for (const f of hooks.changeSelect) f(cell ? cell.id : ""); return; } // the Changes view reads its own cells
      if (cell && cell.id && cell.id.startsWith("role:")) { select(cell.id, false); return; } // an actor (ADR-0215)
      select(id === "create" ? "usecase:create" : id ? "transition:" + id : "", false);
    });
    useCaseGraph.addListener(InternalEvent.DOUBLE_CLICK, (_sender, event) => {
      const cell = event.getProperty("cell");
      if (!cell || !cell.id.startsWith("uc:") || shownChange) return;
      const id = cell.id.slice(3);
      openScreen(id === "create" ? null : transition(id).action);
    });
    keepMoves(useCaseGraph, "usecases");
  }

  function showTab(which) {
    if (which === "system") { // the System lens of the Components tab (ADR-0203), which the ripple names as a diagram
      if (window.PlayLandscape) window.PlayLandscape.setLens("system");
      which = "components";
    }
    tab = which;
    for (const [name, panel] of Object.entries(PANELS)) {
      $("tab-" + name).setAttribute("aria-selected", String(which === name));
      $(panel).hidden = which !== name;
    }
    $("canvas-help").textContent = HINTS[which];
    for (const id of ["fit", "zoom-in", "zoom-out"]) $(id).hidden = which === "screens" || which === "laws" || which === "tests" || which === "access";
    $("tidy").hidden = !hasMoves(which);
    $("draw-palette").hidden = which !== "states";
    $("plan-review").hidden = which === "review";
    for (const f of hooks.tab) f(which);
    if (which === "access" || which === "tests" || which === "sequences") return; // play-access.js, play-tests.js and play-sequence.js draw these on hooks.tab
    if (which === "screens") { renderDesigner(); return; }
    if (which === "laws") { for (const show of hooks.laws) show(); return; }
    if (which === "usecases") drawUseCases();
    if (which === "components") { drawComponents().then(() => markRipple("components")); return; }
    if (which === "review") { PlayReview.show(); return; }
    if (which === "classes") {
      if (!data) { $("class-canvas").replaceChildren(el("p", "This pack has no data model yet. Add a data.json beside its pack.json.", { class: "muted empty" })); return; }
      drawClasses();
    }
    markRipple(which);
    fit();
  }

  // Chat in plan mode (ADR-0156). The AI only proposes: a plan of typed steps the person accepts or rejects one by
  // one. The server re-checks every step and previews the accepted ones through the policy; while a plan is
  // previewed, every view (diagrams, screens, components, Build & run, Simulate) shows the model with those steps
  // applied. Nothing is saved: a plan from a modelled meaning can become a change case, decided in the review workbench.
  const accepted = () => (plan ? plan.steps.filter((_, i) => plan.accepted[i]).map((s) => s.transaction) : []);
  const about = () => ({ case_id: caseId, model: baseModel, plan: plan && plan.previewing ? accepted() : null });

  function say(who, node) {
    const li = el("li", undefined, { class: "msg " + who });
    li.append(node);
    $("chat-log").append(li);
    li.scrollIntoView({ block: "nearest" });
    return li;
  }

  // Building a system in chat (ADR-0201): each ask is a round planned on top of the steps accepted so far, so the
  // work grows round after round instead of each plan replacing the last. The card moves under the latest ask and
  // lists every round with what was asked; going back on an earlier round is unticking its steps or asking again.
  const roundOf = (step) => step.round || 1;
  const rounds = () => (plan ? new Set(plan.steps.map(roundOf)).size : 0);
  const lastRound = () => (plan && plan.steps.length ? Math.max(...plan.steps.map(roundOf)) : 1); // a drawn step joins the round it follows

  async function ask(event) {
    event.preventDefault();
    const input = $("chat-input"), text = input.value.trim();
    if (!text) return;
    input.value = "";
    say("you", el("p", text));
    const button = $("chat-send");
    button.disabled = true;
    const earlier = plan && plan.result && plan.result.legal && plan.result.accepted ? plan : null;
    try {
      const result = await api("/api/play/plan", { case_id: caseId, model: baseModel, request: text, plan: earlier ? accepted() : null });
      if (result.on_top && earlier && earlier === plan) { await addRound(result, text); return; }
      retire();
      plan = { ...result, steps: result.steps.map((step) => ({ ...step, author: "ai", checked: false, caught: false, round: 1, request: text })),
        accepted: result.steps.map(() => true), previewing: false, card: null, rewarded: new Set(), uid: ++planUid };
      plan.card = say("ai", planCard());
      commit(`take the AI's plan: ${result.summary || text}`);
      renderPlan(result.preview);
      refreshRipple();
    } catch (error) {
      say("ai", el("p", `${error.code || "ERROR"}: ${error.message}`, { class: "refusal" }));
    } finally {
      button.disabled = false;
    }
  }

  // A round's steps join the plan; the card is redrawn and moved below the ask, and the server checks every step again.
  async function addRound(result, text) {
    const n = lastRound() + 1;
    for (const step of result.steps) {
      plan.steps.push({ ...step, n: plan.steps.length + 1, author: "ai", checked: false, caught: false, round: n, request: text });
      plan.accepted.push(true);
    }
    Object.assign(plan, { meaning: null, scope: "plan-proposal", provider: result.provider, live: result.live });
    commit(`round ${n}: ${result.summary || text}`);
    plan.card.className = "msg ai";
    $("chat-log").append(plan.card);
    plan.card.replaceChildren(planCard());
    plan.card.scrollIntoView({ block: "nearest" });
    const checked = await refreshPlan();
    if (checked && checked.legal && !plan.previewing) enterPreview();
  }

  // A newer plan replaces this one: its card stays in the chat as a record, with every control disabled, so no tick or
  // button on it can act on the newer plan.
  function retire() {
    if (!plan) return;
    ripple = null;
    rippleSeq += 1;
    renderBadges();
    leavePreview();
    for (const control of plan.card.querySelectorAll("input, button")) control.disabled = true;
    plan.card.firstChild.append(el("p", "Replaced by the newer plan below.", { class: "muted small" }));
    plan = null;
    document.dispatchEvent(new CustomEvent("playide:plan"));
  }

  function planCard() {
    const box = el("div", undefined, { class: "plan" }), many = rounds() > 1;
    const both = plan.steps.some((s) => s.author === "ai") && plan.steps.some((s) => s.author === "you");
    box.append(el("p", many ? `The plan so far: ${rounds()} rounds, ${plan.steps.length} steps` : plan.summary || "A plan", { class: "plan-summary" }),
      el("p", plan.saved ? "Saved on this system · checked by the server again, like any plan" : plan.scope === "plan-draft" ? (plan.provider === "imported" ? "Imported from a UML file · checked by the server like any plan"
        : "Drawn by you on the diagram · checked by the server like any plan")
        : `${plan.provider}${plan.live ? "" : " · offline fixture, not a live model"}${both ? " · with your own steps" : ""} · untrusted until you check it`, { class: "muted small" }));
    cards += 1;
    const list = el("ol", undefined, { class: "plan-steps" });
    plan.steps.forEach((step, i) => {
      const li = el("li"), id = `plan-${cards}-${i}`, check = el("input", undefined, { type: "checkbox", id });
      check.checked = plan.accepted[i];
      check.addEventListener("change", () => toggleStep(i, check.checked));
      const text = el("label", undefined, { for: id });
      text.append(el("span", step.author === "ai" ? "AI" : "You", { class: "who " + step.author }), el("span", step.text, { class: "step-text" }));
      const show = el("button", "Show me", { type: "button", class: "quiet show", title: "Show this step on the diagram" });
      show.addEventListener("click", () => showStep(i));
      if (many && (i === 0 || roundOf(plan.steps[i - 1]) !== roundOf(step))) { // each round opens with what was asked
        li.classList.add("round-start");
        li.append(el("p", `Round ${roundOf(step)}${step.request ? `: “${step.request}”` : step.author === "you" ? ": drawn on the diagram" : ""}`, { class: "round-head" }));
      }
      li.append(check, text, el("span", "", { class: "step-status" }));
      const echo = many && step.why === `You asked: “${step.request}”`; // the round's heading already says it
      if (step.why && !echo) li.append(el("p", step.why, { class: "muted small why" }));
      li.append(show);
      list.append(li);
    });
    const verdict = el("p", "", { class: "plan-verdict", role: "status" });
    const tools = el("div", undefined, { class: "plan-tools" });
    const preview = el("button", "Preview on the diagram", { type: "button", class: "primary" });
    preview.addEventListener("click", () => (plan.previewing ? leavePreview() : enterPreview()));
    const review = el("button", "Review it", { type: "button", class: "review-it", title: "Review the previewed change: what changed, how risky, what the kernel does differently" });
    review.addEventListener("click", () => { if (!plan.previewing) enterPreview(); if (plan.previewing) showTab("review"); });
    tools.append(preview, review);
    if (plan.meaning && plan.steps.every((step) => step.author === "ai" && !step.followOn)) {
      const keep = el("button", "Make it a change case", { type: "button" });
      keep.addEventListener("click", makeCase);
      tools.append(keep);
    }
    box.append(list, verdict, el("div", undefined, { class: "ripple", "aria-live": "polite" }), tools);
    return box;
  }

  async function refreshPlan() {
    const mine = plan, seq = (mine.seq = (mine.seq || 0) + 1); // only the answer for the latest ticks is shown
    try {
      const result = await api("/api/play/plan/preview", { case_id: caseId, model: baseModel, steps: mine.steps.map((s) => s.transaction), accepted: [...mine.accepted] });
      if (mine !== plan || seq !== mine.seq) return null;
      renderPlan(result);
      refreshRipple(); // first, so the redrawn preview is not marked with the previous ripple
      if (plan.previewing) (result.legal ? enterPreview : leavePreview)();
      return result;
    } catch (error) {
      if (mine === plan && seq === mine.seq) plan.card.querySelector(".plan-verdict").textContent = `${error.code || "ERROR"}: ${error.message}`;
      return null;
    }
  }

  function renderPlan(result) {
    plan.result = result;
    const marks = { applies: "✓", rejected: "–", does_not_apply: "✗" };
    plan.card.querySelectorAll(".plan-steps > li").forEach((li, i) => {
      const s = result.steps[i];
      plan.steps[i].text = s.text;
      li.querySelector(".step-text").textContent = s.text;
      li.className = s.status + (plan.steps[i].checked ? " checked" : "") + (li.querySelector(".round-head") ? " round-start" : "");
      li.querySelector(".step-status").textContent = marks[s.status] + (s.code ? ` ${s.code}` : "");
      li.querySelector(".step-status").title = s.message || "";
    });
    const verdict = plan.card.querySelector(".plan-verdict");
    verdict.className = "plan-verdict " + (result.legal ? "ok" : "bad");
    verdict.textContent = !result.accepted ? "No step accepted: nothing would change."
      : result.legal ? `${result.accepted} of ${plan.steps.length} step${plan.steps.length === 1 ? "" : "s"} accepted. The policy allows the result: ${changesOf(result)}.${declaredText(result.declared)}`
      : result.codes.includes("PLAN_STEP_DOES_NOT_APPLY")
        ? `Step ${result.steps.findIndex((x) => x.status === "does_not_apply") + 1} does not apply after the steps you kept (${result.steps.find((x) => x.status === "does_not_apply").message}).`
        : (result.laws && result.laws.length
          ? `The policy refuses the accepted steps. They would break: ${result.laws.join(" ")} (${result.codes.join(", ")})`
          : `The policy refuses the accepted steps: ${result.codes.join(", ") || result.message}.`);
    plan.card.querySelector(".plan-tools .primary").disabled = !result.legal && !plan.previewing;
    plan.card.querySelector(".plan-tools .review-it").disabled = !result.legal;
    renderHealth();
    document.dispatchEvent(new CustomEvent("playide:plan")); // the change shown is different now (ADR-0176)
  }

  // What the accepted steps add to the system's vocabulary (ADR-0201): declared as a sketch declares them, in the draft only.
  function declaredText(declared) {
    if (!declared) return "";
    const named = (one, list) => (list.length ? `${one}${list.length > 1 ? "s" : ""} ${list.join(", ")}` : "");
    const parts = [named("action", declared.actions), named("role", declared.roles)].filter(Boolean);
    return ` New in this system: ${parts.join("; ")}, declared as a sketch declares them.`;
  }

  // The state machine's changes, then the class diagram's (ADR-0202).
  function changesOf(result) {
    const kinds = accepted().filter((t) => t.kind === "set_role_kind").map((t) => `makes ${t.role} ${A_KIND[t.to]}`);
    const states = changes(result.diff), classes = [...(result.data_changes || []), ...kinds].join("; ");
    return states === "no visible change" && classes ? classes : [states, classes].filter(Boolean).join("; ");
  }

  function changes(diff) {
    const parts = [];
    if (diff.added_states.length) parts.push(`adds ${diff.added_states.join(", ")}`);
    if (diff.removed_states.length) parts.push(`removes ${diff.removed_states.join(", ")}`);
    if (diff.added_actions.length) parts.push(`adds ${diff.added_actions.join(", ")}`);
    if (diff.removed_actions.length) parts.push(`removes ${diff.removed_actions.join(", ")}`);
    const changed = Object.keys(diff.changed_actions);
    if (changed.length) parts.push(`changes ${changed.join(", ")}`);
    if (diff.initial_state) parts.push(`starts in ${diff.initial_state.after || diff.initial_state}`);
    return parts.join("; ") || "no visible change";
  }

  function redrawAll(workflow) {
    model = workflow;
    lastView = graph && graph.view ? { scale: graph.view.scale, x: graph.view.translate.x, y: graph.view.translate.y } : null;
    for (const g of [graph, classGraph, useCaseGraph, componentGraph]) if (g) g.destroy();
    for (const box of ["canvas", "class-canvas", "usecase-canvas", "component-canvas"]) $(box).replaceChildren();
    classGraph = useCaseGraph = componentGraph = components = null;
    for (const key of Object.keys(base)) delete base[key];
    clearSimPanel();
    outline();
    draw(model);
    inspect("");
    const kept = screensEdited ? screens : null; // screen edits survive a preview: they are re-checked against the shown model
    loadScreens(kept).then(() => { screensEdited = Boolean(kept); if (tab === "screens") renderDesigner(); });
    if (tab !== "states") showTab(tab);
  }

  function enterPreview() {
    if (!plan || !plan.result || !plan.result.legal) return;
    plan.previewing = true;
    data = plan.result.data || savedData; // the class diagram as the plan's data-model steps leave it (ADR-0202)
    redrawAll(plan.result.candidate);
    highlight(plan.result.diff);
    for (const which of Object.keys(DIAGRAMS)) markRipple(which);
    $("plan-banner").hidden = false;
    $("plan-banner-text").textContent = `Previewing the plan: ${changesOf(plan.result)}. Nothing is applied to the model.`;
    plan.card.querySelector(".plan-tools .primary").textContent = "Back to the model";
  }

  function leavePreview() {
    if (!plan || !plan.previewing) return;
    plan.previewing = false;
    data = savedData;
    redrawAll(baseModel);
    for (const which of Object.keys(DIAGRAMS)) markRipple(which);
    $("plan-banner").hidden = true;
    plan.card.querySelector(".plan-tools .primary").textContent = "Preview on the diagram";
    renderPlan(plan.result);
  }

  function highlight(diff) {
    const added = { fillColor: "#e5f5ec", strokeColor: "#17734a", strokeWidth: 2.5 };
    graph.batchUpdate(() => {
      for (const s of diff.added_states) restyle("state:" + s, added);
      for (const t of model.transitions) {
        if (diff.added_actions.includes(t.action)) restyle("transition:" + t.id, { strokeColor: "#17734a", strokeWidth: 3 });
        else if (diff.changed_actions[t.action]) restyle("transition:" + t.id, { strokeColor: "#c27c0e", strokeWidth: 3 });
      }
      if (diff.initial_state) restyle("initial-edge", { strokeColor: "#c27c0e", strokeWidth: 3 });
    });
  }

  // Ripple (ADR-0158). The diagrams are views of one system, so a change to the state machine changes the others: a
  // new action is a new use case that needs a screen, a removed one strands its screen, a new state is a new literal of
  // the record's state enumeration, and the generated code changes. The server works out what the accepted steps do
  // to every diagram and asks the proposer for follow-on edits, each re-checked by the policy or the screen design
  // check. Tabs carry a badge; the affected elements are marked on each diagram while the plan is previewed.
  const DIAGRAMS = { states: "State machine", classes: "Class diagram", usecases: "Use cases", screens: "Screens", components: "Components" };
  const RIPPLE = { ...DIAGRAMS, sequences: "Sequences", system: "System" }; // sequence diagrams are listed in the ripple; play-sequence.js marks its own tab
  // "System" is the other workflows of the system (ADR-0203, #146): the Components tab's System lens shows it.
  const MARK = { added: "+", removed: "−", changed: "~", warning: "⚠", problem: "✗" };
  const TINT = { added: { strokeColor: "#17734a", fillColor: "#e5f5ec", strokeWidth: 2.5 }, changed: { strokeColor: "#c27c0e", strokeWidth: 2.5 },
    warning: { strokeColor: "#c27c0e", dashed: true, strokeWidth: 2.5 }, problem: { strokeColor: "#a12f2f", strokeWidth: 3 },
    removed: { strokeColor: "#a12f2f", dashed: true, strokeWidth: 3 } };
  const rippleKey = () => JSON.stringify([accepted(), screensEdited ? screens : null]);

  async function refreshRipple() {
    const mine = plan, seq = (rippleSeq += 1), key = rippleKey();
    ripple = null;
    renderRipple();
    renderBadges();
    renderHealth();
    if (!mine || !mine.result || !mine.result.legal) return;
    let result;
    try {
      result = await api("/api/play/ripple", { case_id: caseId, model: baseModel, plan: accepted(), screens: screensEdited ? screens : null });
    } catch (error) {
      result = { error };
    }
    if (seq !== rippleSeq || mine !== plan) return; // a newer change asked again
    ripple = { ...result, key };
    renderRipple();
    renderBadges();
    renderHealth();
    for (const which of Object.keys(DIAGRAMS)) markRipple(which);
    document.dispatchEvent(new CustomEvent("playide:ripple")); // the Changes view lists what to consider (ADR-0176)
  }

  function renderRipple() {
    const box = plan && plan.card && plan.card.querySelector(".ripple");
    if (!box) return;
    box.replaceChildren();
    if (!ripple) {
      if (plan.result && plan.result.legal) box.append(el("p", "Working out what this does to the other diagrams…", { class: "muted small" }));
      return;
    }
    if (ripple.error) { box.append(el("p", `${ripple.error.code || "ERROR"}: ${ripple.error.message}`, { class: "refusal" })); return; }
    box.append(el("h4", ripple.agree ? "Ripple: every diagram still agrees" : "Ripple: the diagrams no longer agree", { class: ripple.agree ? "ok" : "bad" }));
    const list = el("ul", undefined, { class: "ripple-list" });
    for (const [key, name] of Object.entries(RIPPLE)) {
      for (const item of ripple.diagrams[key] || []) {
        const b = el("button", undefined, { type: "button", class: "ripple-item " + item.change, title: item.code || "" });
        b.append(el("span", MARK[item.change], { class: "mark" }), el("span", name, { class: "where" }), el("span", item.text, { class: "what" }));
        b.addEventListener("click", () => showRipple(key, item));
        const li = el("li");
        li.append(b);
        list.append(li);
      }
    }
    const c = ripple.conformance;
    list.append(el("li", `Conformance cases: ${c.cases_before ?? "none"} → ${c.cases_after ?? "none, the app cannot be built"}`, { class: "muted small cases" }));
    box.append(list);
    if (ripple.follow_ons.length) box.append(followOnList());
    else if (ripple.problems.length) box.append(el("p", "The AI has no follow-on for these. Change the model yourself, or untick a step.", { class: "muted small" }));
  }

  function followOnList() {
    const wrap = el("div", undefined, { class: "follow-ons" });
    wrap.append(el("h4", "AI follow-ons"),
      el("p", `${ripple.provider}${ripple.live ? "" : " · offline fixture, not a live model"} · each re-checked by the server`, { class: "muted small" }));
    const list = el("ol");
    for (const f of ripple.follow_ons) {
      const li = el("li", undefined, { class: f.status }), take = el("button", f.status === "applies" ? "Add" : "Refused", { type: "button", class: "quiet" });
      take.disabled = f.status !== "applies";
      take.addEventListener("click", () => takeFollowOn(f, take));
      li.append(el("span", "AI", { class: "who ai" }), el("span", f.text, { class: "step-text" }), take);
      if (f.why) li.append(el("p", f.why, { class: "muted small why" }));
      if (f.status !== "applies") li.append(el("p", `${f.code}: ${f.message}`, { class: "muted small" }));
      list.append(li);
    }
    wrap.append(list);
    return wrap;
  }

  // A state-machine follow-on joins the plan as an AI step; a screen follow-on changes the designer's screens. Either
  // way the server checks the result again, and the ripple is worked out afresh.
  async function takeFollowOn(f, button) {
    button.disabled = true;
    if (f.transaction) {
      plan.steps.push({ n: plan.steps.length + 1, transaction: f.transaction, text: f.text, why: f.why, author: "ai", checked: false, caught: false, followOn: true, round: lastRound() });
      plan.accepted.push(true);
      commit(`add the AI follow-on: ${f.text}`);
      plan.card.replaceChildren(planCard());
      const result = await refreshPlan();
      if (result && result.legal && !plan.previewing) enterPreview();
      return;
    }
    screens = f.screens;
    screensEdited = true;
    useCase = f.screen_step.op === "add" ? f.screen_step.screen.use_case : null;
    if (!plan.previewing) enterPreview();
    changed(`add the AI follow-on: ${f.text}`);
  }

  function cellsFor(key, ref) {
    const kind = ref.slice(0, ref.indexOf(":")), name = ref.slice(ref.indexOf(":") + 1);
    const of = (prefix) => model.transitions.filter((t) => t.action === name).map((t) => prefix + t.id);
    if (kind === "action" && key === "states") return of("transition:");
    if (kind === "action" && key === "usecases") return of("uc:");
    return [ref];
  }

  function markRipple(key) {
    const g = { states: graph, classes: classGraph, usecases: useCaseGraph, components: componentGraph }[key];
    if (!g || !ripple || ripple.error || !plan || (shownChange && key !== "components")) return; // the Changes view draws its own marks
    // The preview shows what the plan adds and changes; the model without it shows, in red, what the plan removes.
    const shown = (item) => item.ref && (item.change === "removed") !== plan.previewing;
    const literal = { fontColor: "#17734a", fontStyle: 1, strokeColor: "none", fillColor: "#e5f5ec" };
    g.batchUpdate(() => {
      for (const item of ripple.diagrams[key]) {
        if (!shown(item)) continue;
        for (const id of cellsFor(key, item.ref)) {
          const cell = g.getDataModel().getCell(id);
          const extra = id.startsWith("literal:") ? (item.change === "removed" ? { fontColor: "#a12f2f", fontStyle: 4 } : literal) : {};
          if (cell) g.getDataModel().setStyle(cell, { ...cell.style, ...TINT[item.change], ...extra });
        }
      }
    });
  }

  function showRipple(key, item) {
    if (item.change === "removed") leavePreview(); // gone from the preview, so it is shown, in red, on the model
    else if (!plan.previewing && plan.result && plan.result.legal) enterPreview();
    if (key === "screens") {
      const name = item.ref ? item.ref.slice(7) : "None", known = screens.screens.some((x) => x.use_case === name) || useCaseList.includes(name);
      useCase = name !== "None" && known ? name : null;
    }
    if (key === "sequences" && item.ref && window.PlaySequence) window.PlaySequence.open(item.ref.slice(9));
    showTab(key);
    if (key === "system" && item.ref && window.PlayLandscape) window.PlayLandscape.focus(item.ref.slice(7)); // drawn once it loads
    const g = key === "system" ? null : current(), ids = key === "screens" || !item.ref ? [] : cellsFor(key, item.ref);
    const cell = g && ids.map((id) => g.getDataModel().getCell(id)).find(Boolean);
    if (cell && cell.isVertex() && !cell.id.startsWith("literal:")) g.setSelectionCell(cell);
    else if (cell && cell.isEdge()) g.setSelectionCell(cell);
    if (cell) g.scrollCellToVisible(cell, true);
    const note = el("div", undefined, { class: "step-note" });
    note.append(el("p", `${RIPPLE[key]}: ${item.text}`, { class: "ripple-note " + item.change }));
    if (item.change === "removed") note.append(el("p", "Shown on the model, marked in red: the plan removes it.", { class: "muted" }));
    $("inspector").prepend(note);
    const seen = `ripple:${key}:${ripple.key}`; // checking, not making: once per diagram for each version of the plan
    if (key !== "states" && !plan.rewarded.has(seen)) {
      plan.rewarded.add(seen);
      earn(1, `Checked the ripple on the ${RIPPLE[key].toLowerCase()}`);
    }
  }

  function renderBadges() {
    for (const key of Object.keys(DIAGRAMS)) {
      const badge = $("tab-" + key).querySelector(".badge");
      if (!badge) continue;
      // The Components tab also shows the System lens, so it counts what the change does to the other workflows (#146).
      const items = ripple && !ripple.error ? [...ripple.diagrams[key], ...(key === "components" ? ripple.diagrams.system || [] : [])] : [];
      badge.hidden = !items.length;
      badge.textContent = String(items.length);
      badge.className = "badge" + (items.some((i) => i.change === "problem") ? " bad" : items.some((i) => i.change === "warning") ? " warn" : "");
      badge.title = items.map((i) => `${MARK[i.change]} ${i.text}`).join("\n");
    }
  }

  function rippleCheck() {
    const name = "Diagrams agree", id = "ripple";
    if (!plan || !plan.steps.length) return { id, name, ok: true, detail: "No change, so nothing ripples" };
    if (!plan.result || !plan.result.legal) return { id, name, ok: false, detail: "The plan is refused or empty: nothing to ripple" };
    if (!ripple || ripple.key !== rippleKey()) return { id, name, ok: false, detail: "Working out the ripple…" };
    if (ripple.error) return { id, name, ok: false, detail: `${ripple.error.code || "ERROR"}: ${ripple.error.message}` };
    const bad = ripple.problems.filter((p) => p.change === "problem").length, warn = ripple.problems.length - bad;
    return { id, name, ok: ripple.agree, detail: bad ? `${bad} diagram(s) out of step: see the plan's ripple` : warn ? `They agree; ${warn} warning(s) to look at` : "Every diagram agrees with the change" };
  }

  async function makeCase() {
    try {
      const created = await api("/api/cases", { request: plan.request });
      const link = el("a", "Open it in PlayIDE", { href: `/play?case=${encodeURIComponent(created.id)}` });
      const note = el("p", `Change case created. In the review workbench, ask for a proposal and choose “${plan.summary}”: that is where the meaning is chosen, checked and approved. `);
      note.append(link);
      say("ai", note);
    } catch (error) {
      say("ai", el("p", `${error.code || "ERROR"}: ${error.message}`, { class: "refusal" }));
    }
  }

  // Drawing and checks (ADR-0157). The palette and the inspector turn mouse gestures into typed steps of your own,
  // added to the plan beside any AI steps: the server checks and previews them exactly like the AI's, and nothing is
  // saved from here. The checks ring fills only from real results on the model you are looking at (the screen design
  // check, a conformance pass, a simulation, every AI step looked at), and points come from checking AI steps, never
  // from making changes.
  const viewKey = () => JSON.stringify([about().plan, screensEdited ? screens : null]);
  const screensKey = () => JSON.stringify([about().plan, screens]); // what the last design check was about
  const KINDS = { state: "a state", transition: "a transition", initial: "the initial state", rename: "a new name", move: "a moved transition" };

  async function addStep(transaction) {
    pinAll(); // nothing you did not touch moves when the plan redraws
    if (transaction.kind === "rename_state" && placed["state:" + transaction.state]) placed["state:" + transaction.to] = placed["state:" + transaction.state];
    if (!plan) {
      plan = { scope: "plan-draft", provider: "drawn by you", live: false, summary: "Your changes", meaning: null, request: "",
        model: "draft", steps: [], accepted: [], previewing: false, card: null, rewarded: new Set(), uid: ++planUid };
      plan.card = say("draft", el("div"));
    }
    plan.steps.push({ n: plan.steps.length + 1, transaction, text: "", why: "", author: "you", checked: false, caught: false, round: lastRound() });
    plan.accepted.push(true);
    commit(stepLabel(transaction));
    plan.card.replaceChildren(planCard());
    const result = await refreshPlan();
    if (result && result.legal && !plan.previewing) enterPreview();
    plan.card.scrollIntoView({ block: "nearest" });
  }

  // Saving and reopening the work in progress (ADR-0185, play-systems.js). The draft is the plan's steps, as typed
  // transactions with who wrote them, and the screens if edited. Restoring it rebuilds the plan and asks the server to
  // check every step again, exactly as if it had just been drawn: a saved step is never trusted for having been saved.
  function draft() {
    return { steps: plan ? plan.steps.map((s) => ({ transaction: s.transaction, author: s.author === "ai" ? "ai" : "you",
      ...(s.round ? { round: s.round } : {}), ...(s.request ? { request: s.request } : {}) })) : [],
      accepted: plan ? [...plan.accepted] : [], screens: screensEdited ? screens : null };
  }

  // Work this browser kept since (ADR-0198) is newer than any save: every edit is kept as it is made, and a save
  // never clears it. So when it came back on load, the saved draft is not opened over it.
  async function restoreDraft(saved) {
    if (recoveredWork) return null;
    if (saved.screens) { screens = saved.screens; changed("open the saved screens"); }
    if (!saved.steps || !saved.steps.length) return null;
    retire();
    plan = { scope: "plan-draft", provider: "drawn by you", live: false, summary: "Your saved changes", meaning: null, request: "",
      model: "draft", steps: [], accepted: [], previewing: false, card: null, rewarded: new Set(), saved: true, uid: ++planUid };
    plan.card = say("draft", el("div"));
    saved.steps.forEach((step, i) => {
      plan.steps.push({ n: i + 1, transaction: step.transaction, text: "", why: "", author: step.author === "ai" ? "ai" : "you", checked: false, caught: false,
        round: step.round || undefined, request: step.request || undefined });
      plan.accepted.push(saved.accepted && i < saved.accepted.length ? Boolean(saved.accepted[i]) : true);
    });
    commit("open the saved work");
    plan.card.replaceChildren(planCard());
    const result = await refreshPlan();
    if (result && result.legal && !plan.previewing) enterPreview();
    return result;
  }

  // An imported UML file's edits (ADR-0190) become the plan, as the person's own steps like drawn edits: the server
  // re-checks each one and previews them through the policy, and nothing is saved from here.
  async function importPlan(transactions, summary) {
    retire();
    plan = { scope: "plan-draft", provider: "imported", live: false, summary, meaning: null, request: "", model: "draft",
      steps: transactions.map((transaction, i) => ({ n: i + 1, transaction, text: "", why: "", author: "you", checked: false, caught: false })),
      accepted: transactions.map(() => true), previewing: false, card: null, rewarded: new Set(), uid: ++planUid };
    plan.card = say("draft", planCard());
    commit("import a UML file");
    const result = await refreshPlan();
    if (result && result.legal && !plan.previewing) enterPreview();
    plan.card.scrollIntoView({ block: "nearest" });
    return result;
  }

  async function toggleStep(i, on) {
    const was = plan.result, step = plan.steps[i];
    plan.accepted[i] = on;
    commit(`${on ? "accept" : "reject"} step ${i + 1}`);
    const now = await refreshPlan();
    if (now && step.author === "ai" && !on && !step.caught && was && was.accepted && !was.legal && now.legal) {
      step.caught = true;
      earn(3, `Caught AI step ${i + 1}: without it the policy allows the plan`, "caught");
    }
  }

  function cellOf(tx) {
    if (tx.kind === "rename_state") return "state:" + (plan.previewing ? tx.to : tx.state);
    if (tx.state && tx.kind !== "retarget_transition") return "state:" + tx.state;
    return "transition:" + (tx.kind === "add_transition" ? tx.id : tx.transition);
  }

  function stepNote(i) {
    const step = plan.steps[i], status = plan.result && plan.result.steps[i], note = el("div", undefined, { class: "step-note" });
    const head = el("p");
    head.append(el("strong", `Step ${i + 1} (${step.author === "ai" ? "AI" : "you"}): `), document.createTextNode(step.text));
    note.append(head);
    if (step.why) note.append(el("p", step.why, { class: "muted" }));
    const where = !status ? "" : status.status === "rejected" ? "You rejected this step."
      : status.status === "does_not_apply" ? `It does not apply: ${status.message}`
      : plan.previewing ? "The diagram shows the plan with this step applied."
      : plan.result.legal ? "Shown on the model, marked in red: the plan removes it."
      : "It applies, but the policy refuses the accepted steps together: see the plan's verdict.";
    note.append(el("p", where));
    return note;
  }

  const DATA_STEPS = ["add_attribute", "remove_attribute", "set_required"];

  // A data-model step is shown on the class diagram, on the class it changes (ADR-0202).
  function showClassStep(i) {
    const step = plan.steps[i];
    showTab("classes");
    const cell = classGraph && classGraph.getDataModel().getCell("class:" + step.transaction.entity);
    if (cell) { classGraph.setSelectionCell(cell); classGraph.scrollCellToVisible(cell, true); }
    $("inspector").prepend(stepNote(i));
    if (cell && step.author === "ai" && !step.checked) { step.checked = true; earn(1, `Looked at AI step ${i + 1} on the diagram`); }
    if (plan.result) renderPlan(plan.result);
  }

  // A role-kind step is shown on the use case diagram, on the actor it changes (ADR-0210, #156).
  function showRoleStep(i) {
    showTab("usecases");
    select("role:" + plan.steps[i].transaction.role, false);
    $("inspector").prepend(stepNote(i));
    if (plan.steps[i].author === "ai" && !plan.steps[i].checked) { plan.steps[i].checked = true; earn(1, `Looked at AI step ${i + 1} on the diagram`); }
    if (plan.result) renderPlan(plan.result);
  }

  function showStep(i) {
    const step = plan.steps[i];
    if (!plan.previewing && plan.result && plan.result.legal) enterPreview();
    if (DATA_STEPS.includes(step.transaction.kind)) { showClassStep(i); return; }
    if (step.transaction.kind === "set_role_kind") { showRoleStep(i); return; }
    if (tab !== "states") showTab("states");
    const id = cellOf(step.transaction);
    let cell = graph.getDataModel().getCell(id);
    if (!cell && plan.previewing) { // a removal: the element is gone from the preview, so show it on the model
      leavePreview();
      cell = graph.getDataModel().getCell(id);
      if (cell) restyle(id, { strokeColor: "#a12f2f", dashed: true, strokeWidth: 3 });
    }
    if (cell) {
      graph.setSelectionCell(cell);
      graph.scrollCellToVisible(cell, true);
    } else {
      graph.clearSelection();
      inspect("");
    }
    const note = stepNote(i);
    if (!cell) note.append(el("p", "Its element is not on the diagram: preview a plan the policy allows to see it.", { class: "muted" }));
    $("inspector").prepend(note);
    if (cell && step.author === "ai" && !step.checked) { // credit only for a step actually shown
      step.checked = true;
      earn(1, `Looked at AI step ${i + 1} on the diagram`);
    }
    if (plan.result) renderPlan(plan.result);
  }

  // `ran` is the view the build or simulation was of: nothing is earned if the view changed while it ran.
  function rewardTrying(kind, n, why, ran) {
    if (ran !== viewKey() || !plan || !plan.previewing || !plan.steps.some((s, i) => s.author === "ai" && plan.accepted[i])) return;
    const key = kind + ran;
    if (plan.rewarded.has(key)) return;
    plan.rewarded.add(key);
    earn(n, why);
  }

  // The game layer (play-game.js, ADR-0208) hears every award and every change to the checks; it adds motion and the
  // next check to run, and awards nothing itself.
  function earn(n, why, kind = "") {
    points += n;
    earned.unshift({ n, why });
    document.dispatchEvent(new CustomEvent("playide:earn", { detail: { n, why, kind, points } }));
    const toast = $("toast");
    toast.textContent = `+${n} ${why}`;
    toast.classList.add("show");
    clearTimeout(earn.timer);
    earn.timer = setTimeout(() => toast.classList.remove("show"), 2600);
    renderHealth();
  }

  function checksNow() {
    const key = viewKey(), ai = plan ? plan.steps.filter((s) => s.author === "ai") : [];
    const seen = ai.filter((s) => s.checked).length, built = lastBuild && lastBuild.key === key ? lastBuild : null;
    const simulated = sim && simKey === key ? sim : null;
    return [
      { id: "ai", name: "AI steps checked", ok: seen === ai.length, detail: ai.length ? `${seen} of ${ai.length} AI steps looked at on the diagram` : "No AI plan to check" },
      { id: "screens", name: "Screens pass the design check", ok: problemsFor === screensKey() && !problems.length && Boolean(a11y) && !a11y.failed,
        detail: problemsFor !== screensKey() ? "Checking the screens…" : problems.length ? `${problems.length} design problem(s): see Screens`
          : a11y && a11y.failed ? `${a11y.failed} accessibility check(s) fail: see Screens` : "Every screen can be built and meets the accessibility checks" },
      { id: "conformance", name: "Conformance", ok: Boolean(built) && built.conformance.status === "PASS",
        detail: built ? `${built.conformance.status}: ${built.cases} cases checked against the kernel` : "Not built since the last change: press Build & run" },
      rippleCheck(),
      { id: "simulated", name: "Simulated", ok: Boolean(simulated),
        detail: simulated ? `${simulated.attempts} attempts, ${simulated.refused} refused by the kernel` : "Not simulated since the last change: press Simulate" },
    ];
  }

  function renderHealth() {
    const checks = checksNow(), done = checks.filter((c) => c.ok).length, ring = $("health-ring"), ns = "http://www.w3.org/2000/svg";
    const r = 14, length = 2 * Math.PI * r, part = length / checks.length;
    if (ring.children.length !== checks.length) ring.replaceChildren(...checks.map(() => document.createElementNS(ns, "circle")));
    checks.forEach((c, i) => { // the same arcs are kept, so a part filling or emptying can be animated
      const attrs = { cx: 18, cy: 18, r, stroke: c.ok ? "#17734a" : "#dfe3ea", "stroke-dasharray": `${part - 2} ${length - part + 2}`,
        "stroke-dashoffset": String(-i * part), transform: "rotate(-90 18 18)", "data-check": c.id || "" };
      for (const [k, v] of Object.entries(attrs)) ring.children[i].setAttribute(k, v);
    });
    $("health-text").textContent = `${done}/${checks.length} checks · ${points} pts`;
    $("health").title = checks.map((c) => `${c.ok ? "✓" : "○"} ${c.name}: ${c.detail}`).join("\n");
    $("points").textContent = `${points} pts`;
    $("check-list").replaceChildren(...checks.map((c) => {
      const li = el("li", undefined, { class: c.ok ? "ok" : "" });
      li.append(el("span", c.ok ? "✓" : "○", { class: "mark" }), el("span", c.name), el("span", c.detail, { class: "detail" }));
      return li;
    }));
    $("earned").replaceChildren(...(earned.length ? earned.slice(0, 20).map((e) => {
      const li = el("li");
      li.append(el("strong", `+${e.n}`), document.createTextNode(e.why));
      return li;
    }) : [el("li", "Nothing yet. Look at an AI step on the diagram, untick one the policy refuses, or build and simulate an AI change.")]));
    document.dispatchEvent(new CustomEvent("playide:checks", { detail: { checks, points, key: viewKey(), plan: Boolean(plan && plan.steps.length) } }));
  }

  // Adding without dragging (ADR-0174), after draw.io and Visio: click a palette item, then the diagram, to place it;
  // double-click empty space for a state, a state to rename it, a transition to change who may take it. Each opens a
  // small editor where it happens: Enter adds the step to the plan, Escape drops it. Dragging from the palette still works.
  let tool = null, toolFrom = null, editor = null;
  const reviewing = () => document.body.dataset.view === "review";
  const TOOL_HINTS = { state: "Click the diagram to place a state, or a state to put it after that one.",
    transition: "Click the state the transition leaves.", initial: "Click the state records start in." };

  function arm(kind) {
    if (reviewing()) return;
    closeEditor();
    tool = tool === kind ? null : kind;
    toolFrom = null;
    for (const b of $("draw-palette").querySelectorAll("button")) b.setAttribute("aria-pressed", String(b.dataset.kind === tool));
    $("canvas").classList.toggle("placing", Boolean(tool));
    if (!tool && graph) preview("", 0, 0);
    $("canvas-help").textContent = tool ? TOOL_HINTS[tool] + " Escape cancels." : HINTS.states;
    if (tool) {
      if (tab !== "states") showTab("states");
      $("canvas").focus({ preventScroll: true });
    }
  }

  function closeEditor() {
    if (!editor) return;
    editor.remove();
    editor = null;
    if (!tool) $("canvas-help").textContent = HINTS.states;
  }

  // The editor sits over the diagram at (x, y), in the canvas's own pixels. `show` names the fields of formFor's spec to
  // show; the others keep their values.
  function inlineEdit(title, spec, x, y, show = spec.fields.map(([text]) => text)) {
    closeEditor();
    preview("", 0, 0);
    const box = $("canvas"), form = el("form", undefined, { class: "draft-form inline-edit", "aria-label": title });
    form.append(el("p", title, { class: "inline-title" }));
    for (const [text, control] of spec.fields) if (show.includes(text)) form.append(field(text, control));
    const tools = el("div", undefined, { class: "draft-tools" }), cancel = el("button", "×", { type: "button", class: "quiet", "aria-label": "Drop it", title: "Drop it (Escape)" });
    tools.append(el("button", "Add to the plan", { type: "submit", class: "primary" }), cancel);
    form.append(tools);
    cancel.addEventListener("click", () => { closeEditor(); box.focus({ preventScroll: true }); });
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const step = spec.make();
      closeEditor();
      box.focus({ preventScroll: true });
      addStep(step);
    });
    // The editor lives inside the canvas: keep its pointer gestures (selecting a word with a double-click, opening a
    // select) away from the diagram, which would otherwise pan or treat them as clicks on empty space.
    for (const type of ["pointerdown", "pointermove", "pointerup", "mousedown", "mousemove", "mouseup", "click", "dblclick", "touchstart", "touchmove", "touchend", "wheel"]) {
      form.addEventListener(type, (event) => event.stopPropagation());
    }
    form.addEventListener("keydown", (event) => {
      event.stopPropagation(); // Delete and Backspace edit the name, not the diagram
      if (event.key === "Escape") { event.preventDefault(); closeEditor(); box.focus({ preventScroll: true }); }
      else if (event.key === "Enter" && event.target.tagName === "SELECT") { event.preventDefault(); form.requestSubmit(); }
    });
    box.append(form);
    editor = form;
    const w = form.offsetWidth, h = form.offsetHeight;
    form.style.left = Math.max(6, Math.min(x, box.clientWidth - w - 6)) + "px";
    form.style.top = Math.max(6, Math.min(y, box.clientHeight - h - 6)) + "px";
    $("canvas-help").textContent = "Enter adds it to the plan; Escape cancels. The plan previews it; nothing is saved.";
    const first = form.querySelector("input, select");
    first.focus();
    if (first.select) first.select();
  }

  function stateAt(cell) { return cell && cell.id && cell.id.startsWith("state:") ? cell.id.slice(6) : null; }

  function cellBox(cell) {
    const s = graph.view.getState(cell);
    return s ? { x: s.x, y: s.y, width: s.width, height: s.height } : null;
  }

  function pointIn(event) {
    const r = $("canvas").getBoundingClientRect();
    return [event.clientX - r.left, event.clientY - r.top];
  }

  function toGraph(x, y) {
    const v = graph.view;
    return [x / v.scale - v.translate.x - STATE.width / 2, y / v.scale - v.translate.y - STATE.height / 2];
  }

  // A state put after another goes just to its right, level with it; on empty space, centred where you clicked.
  function spotFor(x, y, after) {
    const cell = after && graph.getDataModel().getCell("state:" + after);
    return cell ? [cell.geometry.x + STATE.width + 70, cell.geometry.y] : toGraph(x, y);
  }

  function newState(x, y, after) {
    const spec = formFor("state", after), make = spec.make, spot = spotFor(x, y, after);
    spec.make = () => {
      const step = make();
      pinAll();
      placed["state:" + step.state] = spot; // centred where you clicked or dropped
      saveLayout();
      return step;
    };
    inlineEdit(after ? `New state after ${after}` : "New state", spec, x, y, ["Name"]);
  }

  function renameState(cell) {
    const s = stateAt(cell), b = cellBox(cell);
    if (!s || !b) return;
    inlineEdit(`Rename ${s}`, formFor("rename", s), b.x, b.y + b.height + 4);
  }

  function changeRole(cell) {
    const t = transition(cell.id.slice(11)), [x, y] = cellBox(cell) ? [cellBox(cell).x, cellBox(cell).y] : [20, 20];
    if (!t) return; // drawn in this plan: change it in the plan instead
    const role = choose(packInfo.roles, t.role, (r) => r + kindNote(r));
    inlineEdit(`Who may take ${t.action}`, { fields: [["Who may take it", role]], make: () => ({ kind: "set_role", transition: t.id, role: role.value }) },
      x + 8, y + 8);
  }

  function onCanvasClick(cell, event) {
    if (!tool || !event || reviewing() || (event.target && event.target.closest && event.target.closest(".inline-edit"))) return;
    const [x, y] = pointIn(event), s = stateAt(cell);
    if (tool === "state") {
      arm(null);
      newState(x, y, s);
    } else if (tool === "initial") {
      if (!s) return;
      arm(null);
      addStep({ kind: "set_initial", state: s });
    } else if (!s) {
      $("canvas-help").textContent = (toolFrom ? `From ${toolFrom}: click the state it goes to.` : TOOL_HINTS.transition) + " Escape cancels.";
    } else if (!toolFrom) {
      toolFrom = s;
      preview("transition", x, y);
      $("canvas-help").textContent = `From ${s}: now click the state it goes to (the same state for a self-transition). Escape cancels.`;
    } else {
      const from = toolFrom, spec = formFor("transition", s), b = cellBox(cell); // below the target, leaving it in view
      spec.fields[0][1].value = from;
      arm(null);
      inlineEdit(`Transition ${from} → ${s}`, spec, b ? b.x : x, b ? b.y + b.height + 6 : y, ["Action", "Who may take it"]);
    }
  }

  function onCanvasDoubleClick(cell, event) {
    if (tool || !event || reviewing() || (event.target && event.target.closest && event.target.closest(".inline-edit"))) return;
    if (!cell) {
      const [x, y] = pointIn(event);
      newState(x, y, null);
    } else if (stateAt(cell)) renameState(cell);
    else if (cell.id && cell.id.startsWith("transition:")) changeRole(cell);
    else return;
    event.preventDefault();
  }

  function wireCanvas(g) {
    const { InternalEvent } = maxgraph;
    g.addListener(InternalEvent.CLICK, (_sender, evt) => onCanvasClick(evt.getProperty("cell"), evt.getProperty("event")));
    g.addListener(InternalEvent.DOUBLE_CLICK, (_sender, evt) => onCanvasDoubleClick(evt.getProperty("cell"), evt.getProperty("event")));
    g.addListener(InternalEvent.CELLS_MOVED, (_sender, evt) => moved(evt.getProperty("cells") || []));
  }

  // What a click or a drop will do, drawn under the pointer before you commit: the outline of the new state where
  // it will land, the state a transition or the initial arrow will attach to, and a line from a transition's source.
  let dragKind = "";
  function overlay() {
    const box = $("canvas");
    let svg = box.querySelector(".place-preview");
    if (!svg) {
      svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.setAttribute("class", "place-preview");
      svg.setAttribute("aria-hidden", "true");
      box.append(svg);
    }
    return svg;
  }

  function preview(kind, x, y) {
    const svg = overlay(), ns = "http://www.w3.org/2000/svg", parts = [];
    const shape = (name, attrs) => { const n = document.createElementNS(ns, name); for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v); parts.push(n); };
    const cell = kind && graph.getCellAt(x, y), s = stateAt(cell), box = s && cellBox(cell);
    if (kind === "state") {
      const k = graph.view.scale, v = graph.view, w = STATE.width * k, h = STATE.height * k, [gx, gy] = spotFor(x, y, s);
      shape("rect", { x: (gx + v.translate.x) * k, y: (gy + v.translate.y) * k, width: w, height: h, rx: 10 * k, class: "ghost-state" });
      if (box) shape("rect", { x: box.x - 4, y: box.y - 4, width: box.width + 8, height: box.height + 8, rx: 12, class: "ghost-target" });
    } else if (kind === "transition" || kind === "initial") {
      if (box) shape("rect", { x: box.x - 4, y: box.y - 4, width: box.width + 8, height: box.height + 8, rx: 12, class: "ghost-target" });
      const from = kind === "transition" && toolFrom && graph.getDataModel().getCell("state:" + toolFrom), fb = from && cellBox(from);
      if (fb) shape("line", { x1: fb.x + fb.width / 2, y1: fb.y + fb.height / 2, x2: x, y2: y, class: "ghost-edge" });
    }
    svg.replaceChildren(...parts);
  }


  function startDrawing() {
    const box = $("canvas");
    new ResizeObserver(holdStill).observe(box);
    for (const b of $("draw-palette").querySelectorAll("button")) {
      b.setAttribute("aria-pressed", "false");
      b.addEventListener("dragstart", (event) => { arm(null); dragKind = b.dataset.kind; event.dataTransfer.setData("text/x-eija-kind", b.dataset.kind); event.dataTransfer.effectAllowed = "copy"; });
      b.addEventListener("dragend", () => { dragKind = ""; preview("", 0, 0); });
      // A pointer click arms the tool; Enter or Space on the button opens the full form, so the keyboard needs no pointing.
      b.addEventListener("click", (event) => (event.detail > 0 ? arm(b.dataset.kind) : drawForm(b.dataset.kind, null)));
    }
    box.addEventListener("dragover", (event) => {
      if (!event.dataTransfer.types.includes("text/x-eija-kind")) return;
      event.preventDefault();
      event.dataTransfer.dropEffect = "copy";
      box.classList.add("drop-over");
      preview(dragKind, ...pointIn(event));
    });
    box.addEventListener("dragleave", (event) => {
      if (box.contains(event.relatedTarget)) return; // moving over a child of the canvas, still inside it
      box.classList.remove("drop-over");
      preview("", 0, 0);
    });
    box.addEventListener("pointermove", (event) => { if (tool && !editor) preview(tool, ...pointIn(event)); });
    box.addEventListener("pointerleave", () => preview("", 0, 0));
    box.addEventListener("drop", (event) => {
      const kind = event.dataTransfer.getData("text/x-eija-kind");
      box.classList.remove("drop-over");
      preview("", 0, 0);
      if (!kind) return;
      event.preventDefault();
      const [x, y] = pointIn(event), s = stateAt(graph.getCellAt(x, y));
      if (kind === "state") newState(x, y, s);
      else if (kind === "initial" && s) addStep({ kind: "set_initial", state: s });
      else if (kind === "transition" && s) { // dropped on the state it leaves: now pick where it goes
        arm("transition");
        onCanvasClick(graph.getCellAt(x, y), event);
      } else drawForm(kind, s);
    });
    box.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && (tool || editor)) {
        arm(null);
        closeEditor();
        event.preventDefault();
        return;
      }
      if (event.key !== "Delete" && event.key !== "Backspace") return;
      if (selected.startsWith("state:")) addStep({ kind: "remove_state", state: selected.slice(6) });
      else if (selected.startsWith("transition:")) addStep({ kind: "remove_transition", transition: selected.slice(11) });
      else return;
      event.preventDefault();
    });
    // Clicking elsewhere drops an empty editor; one with something typed stays until Enter or Escape.
    document.addEventListener("pointerdown", (event) => {
      if (editor && !editor.contains(event.target) && !editor.querySelector("input")?.value.trim()) closeEditor();
    }, true);
  }

  function choose(values, chosen, text = (v) => v) {
    const select = el("select");
    for (const v of values) {
      const option = el("option", text(v), { value: v });
      option.selected = v === chosen;
      select.append(option);
    }
    return select;
  }

  // On a system you started (ADR-0201), an action or role can be one it declares or a new name, which the step then
  // declares as a sketch would: a text box that suggests the declared names and says when a name is new.
  function named(values, value, what, used = new Set()) {
    const id = `names-${what}-${++named.n}`, list = el("datalist", undefined, { id });
    for (const v of values) list.append(el("option", undefined, { value: v, label: used.has(v) ? `${v} (already used)` : what === "role" ? v + kindNote(v) : v }));
    const input = el("input", undefined, { list: id, value, required: "", maxlength: "40", pattern: "[A-Za-z][A-Za-z0-9_]{0,39}",
      placeholder: `A ${what}, or a new name`, autocomplete: "off", title: "Letters, digits and _; starts with a letter" });
    const note = el("span", "", { class: "muted small new-name" });
    const say = () => { const v = input.value.trim(); note.textContent = v && !values.includes(v) ? `New ${what}: the step declares ${v}` : ""; };
    input.addEventListener("input", say);
    say();
    const wrap = el("span", undefined, { class: "named" });
    wrap.append(input, list, note);
    Object.defineProperty(wrap, "value", { get: () => input.value.trim(), set: (v) => { input.value = v; say(); } });
    wrap.focus = () => input.focus();
    return wrap;
  }
  named.n = 0;

  function field(text, control) {
    const wrap = el("label", text);
    wrap.append(control);
    return wrap;
  }

  function newId(action) {
    const stem = "TR-" + action.toUpperCase().replace(/[^A-Z0-9]+/g, "_").replace(/^_+|_+$/g, "");
    const taken = new Set([...model.transitions.map((t) => t.id), ...(plan ? plan.steps.map((s) => s.transaction.id).filter(Boolean) : [])]);
    let n = 0;
    while (taken.has(stem + (n || ""))) n += 1;
    return stem + (n || "");
  }

  // Each form: its fields (label, control) and the typed step it makes from them.
  function formFor(kind, at) {
    const used = new Set(model.transitions.map((t) => t.action)), t = at && kind === "move" ? transition(at) : null;
    if (kind === "state") {
      const name = el("input", undefined, { required: "", maxlength: "60", placeholder: "Name, e.g. Archived" });
      const after = choose(["", ...model.states], at || "", (v) => v || "(at the end)");
      return { fields: [["Name", name], ["Place after", after]], make: () => ({ kind: "add_state", state: name.value.trim(), after: after.value || null }) };
    }
    if (kind === "rename") {
      const name = el("input", undefined, { required: "", maxlength: "60", value: at });
      return { fields: [[`Rename ${at} to`, name]], make: () => ({ kind: "rename_state", state: at, to: name.value.trim() }) };
    }
    if (kind === "initial") {
      const state = choose(model.states, at || model.initial_state);
      return { fields: [["Records start in", state]], make: () => ({ kind: "set_initial", state: state.value }) };
    }
    if (kind === "move") {
      const end = choose(["target", "source"], "target"), state = choose(model.states, t.to_state);
      return { fields: [[`Move ${t.action}'s`, end], ["to state", state]], make: () => ({ kind: "retarget_transition", transition: t.id, end: end.value, state: state.value }) };
    }
    const from = choose(model.states, at || model.states[0]), to = choose(model.states, at || model.states[0]);
    const fresh = packInfo.actions.find((a) => !used.has(a));
    const action = packInfo.own_system ? named(packInfo.actions, fresh || "", "action", used) // your own system can name a new one
      : choose(packInfo.actions, fresh || packInfo.actions[0], (a) => a + (used.has(a) ? " (already used)" : ""));
    const role = packInfo.own_system ? named(packInfo.roles, packInfo.roles[0], "role") : choose(packInfo.roles, packInfo.roles[0], (r) => r + kindNote(r));
    return { fields: [["From", from], ["To", to], ["Action", action], ["Who may take it", role]],
      make: () => ({ kind: "add_transition", id: newId(action.value), action: action.value, from_state: from.value, to_state: to.value, role: role.value }) };
  }

  function drawForm(kind, at) {
    if (tab !== "states") showTab("states");
    const box = $("inspector"), form = el("form", undefined, { class: "draft-form" }), spec = formFor(kind, at);
    for (const [text, control] of spec.fields) form.append(field(text, control));
    const tools = el("div", undefined, { class: "draft-tools" }), cancel = el("button", "Never mind", { type: "button", class: "quiet" });
    cancel.addEventListener("click", () => inspect(selected));
    tools.append(el("button", "Add to the plan", { type: "submit", class: "primary" }), cancel);
    form.append(tools, el("p", "It joins the plan as your step. The server checks it and the diagram previews it; nothing is saved.", { class: "muted small" }));
    form.addEventListener("submit", (event) => { event.preventDefault(); addStep(spec.make()); });
    box.replaceChildren(el("h3", "Draw " + KINDS[kind]), form);
    form.querySelector("input, select").focus();
  }

  function draftTools(buttons) {
    const tools = el("div", undefined, { class: "draft-tools edit-tools" }); // edit-tools: hidden in the review view (ADR-0172)
    for (const [text, run] of buttons) {
      const b = el("button", text, { type: "button" });
      b.addEventListener("click", run);
      tools.append(b);
    }
    return tools;
  }

  function stateTools(s) {
    return draftTools([
      ["Add a transition from here", () => drawForm("transition", s)],
      ...(s === model.initial_state ? [] : [["Start records here", () => addStep({ kind: "set_initial", state: s })]]),
      ["Rename…", () => drawForm("rename", s)],
      ["Remove", () => addStep({ kind: "remove_state", state: s })],
    ]);
  }

  function transitionTools(t) {
    const others = packInfo.roles.filter((r) => r !== t.role);
    return draftTools([
      ...others.map((r) => [`Let ${r}${kindNote(r)} take it`, () => addStep({ kind: "set_role", transition: t.id, role: r })]),
      ["Move an end…", () => drawForm("move", t.id)],
      ["Remove", () => addStep({ kind: "remove_transition", transition: t.id })],
    ]);
  }

  // Component diagram (ADR-0155): the app this model builds, read by the server from the generated files. Components
  // are modules, the EIJA modules they import, infrastructure and generated files; each dependency is a real import,
  // route or file read. A provider's interface (the lollipop) lists the names its users import from it.
  const COMPONENT_FILL = { component: "#eef2ff", executable: "#eef2ff", test: "#e5f5ec", browser: "#fff7e6", kernel: "#dfe6ff",
    database: "#f1f3f7", framework: "#f1f3f7", artifact: "#ffffff" };
  const shortNames = (names) => names.length > 2 ? names.slice(0, 2).join(", ") + ` +${names.length - 2}` : names.join(", ");
  const isLollipop = (d) => !d.names.some((n) => n === "reads" || n === "serves") && d.names.length > 0;

  // Build evidence belongs to the exact model and screens it was built from; the structure of other screens gets none.
  const evidence = () => (lastBuild && components && lastBuild.model === components.model && lastBuild.screens === components.screens ? lastBuild : null);

  function componentLabel(c) {
    const lastBuild = evidence();
    const badge = c.id.startsWith("tests.") && lastBuild ? `\n${lastBuild.conformance.status === "PASS" ? "✓" : "✗"} ${lastBuild.cases} cases`
      : c.id === "app.server" && lastBuild && lastBuild.url ? "\n● running" : "";
    return `«${c.stereotype}»\n${c.name}${badge}`;
  }

  // Kernel modules sit in the installed package, generated documents in a package of their own (UML packages).
  const RANK = { browser: 0, executable: 1, component: 2, framework: 3, database: 4, test: 5, kernel: 6, artifact: 7 };
  const GROUPS = { kernel: ["pkg:eija", "eija_studio (installed package)"], artifact: ["pkg:files", "Generated model files"] };

  // Columns by depth of use (a user sits left of what it uses; the page's "serves" back-edge is ignored), stacked in
  // id order within a column, with each package's members kept together. Deterministic and compact, no layout engine.
  function componentLayout() {
    const COLUMN = 300, GAP = 18, PACKAGE_HEAD = 30, edges = components.dependencies.filter((d) => !d.names.includes("serves"));
    const depth = {}, visit = (id, seen = new Set()) => {
      if (depth[id] !== undefined) return depth[id];
      if (seen.has(id)) return 0;
      seen.add(id);
      const users = edges.filter((d) => d.target === id).map((d) => d.source);
      return (depth[id] = users.length ? 1 + Math.max(...users.map((u) => visit(u, seen))) : 0);
    };
    const size = (c) => [Math.min(220, Math.max(150, c.name.length * 7 + 30)), c.stereotype === "artifact" ? 38 : 54];
    const boxes = {}, columns = {};
    // A package's members share one column, the deepest of theirs, so the package is one box.
    const deepest = {};
    for (const c of components.components) if (GROUPS[c.stereotype]) deepest[c.stereotype] = Math.max(deepest[c.stereotype] || 0, visit(c.id));
    // The framework a module runs on sits under that module, out of the way of the module's own uses (a framework in
    // the next column stood under every edge that column sends on).
    const runsOn = (c) => Math.min(...edges.filter((d) => d.target === c.id).map((d) => visit(d.source)));
    const column = (c) => GROUPS[c.stereotype] ? deepest[c.stereotype] : c.stereotype === "framework" && visit(c.id) > 0 ? runsOn(c) : visit(c.id);
    for (const c of components.components) (columns[column(c)] ||= []).push(c);
    for (const [col, members] of Object.entries(columns)) {
      let y = 20;
      const x = 40 + Number(col) * COLUMN;
      const order = [...members].sort((a, b) => (GROUPS[a.stereotype] ? 1 : 0) - (GROUPS[b.stereotype] ? 1 : 0) || RANK[a.stereotype] - RANK[b.stereotype] || a.id.localeCompare(b.id));
      let open = null;
      for (const c of order) {
        const group = GROUPS[c.stereotype];
        if (group && open !== group[0]) {
          if (open) y += GAP;
          boxes[group[0]] = [x - 12, y, 0, 0];
          y += PACKAGE_HEAD;
          open = group[0];
        }
        const [w, h] = size(c);
        boxes[c.id] = [x, y, w, h];
        if (group) { const b = boxes[group[0]]; b[2] = Math.max(b[2], w + 24); b[3] = y + h + 12 - b[1]; }
        y += h + GAP;
      }
    }
    for (const c of components.components) if (c.stereotype === "framework") clearOfLines(c.id, boxes, edges);
    return (id) => {
      if (id.startsWith("iface:")) { const [x, y, , h] = boxes[id.slice(6)]; return [x - 34, y + h / 2 - 8, 16, 16]; } // the ball, left of its provider
      return boxes[id] || [0, 0, 0, 0];
    };
  }

  // Moves a box (and its interface ball and label, to its left) down until no other line crosses it or another box.
  function clearOfLines(id, boxes, edges) {
    const centre = (key) => { const [x, y, w, h] = boxes[key]; return [x + w / 2, y + h / 2]; };
    const lines = edges.filter((d) => d.source !== id && d.target !== id && boxes[d.source] && boxes[d.target]).map((d) => [centre(d.source), centre(d.target)]);
    const others = Object.entries(boxes).filter(([key]) => key !== id && !key.startsWith("pkg:")).map(([, b]) => b);
    const b = boxes[id], hits = ([x, y, w, h]) => others.some(([ox, oy, ow, oh]) => ox < x + w && x < ox + ow && oy < y + h && y < oy + oh)
      || lines.some(([[x1, y1], [x2, y2]]) => Array.from({ length: 41 }, (_, i) => [x1 + (x2 - x1) * i / 40, y1 + (y2 - y1) * i / 40])
        .some(([px, py]) => px > x && px < x + w && py > y && py < y + h));
    for (let tries = 0; tries < 60 && hits([b[0] - 120, b[1] - 16, b[2] + 150, b[3] + 22]); tries++) b[1] += 18;
  }

  // The components report of the model on screen, read once per view: the component diagram and the deployment
  // diagram (ADR-0206) are both read from it.
  async function loadComponents() {
    if (!components) components = await api("/api/play/components", { ...about(), screens: screensEdited ? screens : null });
    return components;
  }

  async function drawComponents() {
    const box = $("component-canvas");
    if (!components) {
      try {
        await loadComponents();
      } catch (error) {
        box.replaceChildren(el("p", `Could not read the app's components (${error.code || "ERROR"}): ${error.message}`, { class: "muted empty" }));
        return;
      }
    }
    if (componentGraph) { restyleComponents(); fit(); return; }
    const { Graph, InternalEvent } = maxgraph;
    InternalEvent.disableContextMenu(box);
    componentGraph = new Graph(box);
    componentGraph.options.foldingEnabled = false; // packages are not collapsible, and the fold icon is not shipped
    for (const setting of ["setConnectable", "setCellsEditable", "setCellsDisconnectable", "setCellsResizable", "setDropEnabled"]) componentGraph[setting](false);
    componentGraph.setPanning(true);
    const root = componentGraph.getDefaultParent(), at = componentLayout(), cells = {}, groups = {};
    const font = { fontFamily: "system-ui, sans-serif", fontColor: "#1b2130", fontSize: 12 };
    componentGraph.batchUpdate(() => {
      for (const [stereotype, [id, name]] of Object.entries(GROUPS)) {
        if (!components.components.some((c) => c.stereotype === stereotype)) continue;
        const [x, y, w, h] = at(id);
        groups[stereotype] = { cell: componentGraph.insertVertex({ parent: root, id, value: name, position: [x, y], size: [w, h],
          style: { ...font, shape: "swimlane", startSize: 24, fontStyle: 1, fillColor: "#f4f5f8", swimlaneFillColor: "#fbfcfe",
            strokeColor: "#9aa3b5", collapsible: false, movable: false, selectable: false } }), x, y };
      }
      for (const c of components.components) {
        let [x, y, w, h] = at(c.id), parent = root;
        if (groups[c.stereotype]) { parent = groups[c.stereotype].cell; x -= groups[c.stereotype].x; y -= groups[c.stereotype].y; }
        cells[c.id] = componentGraph.insertVertex({ parent, id: "component:" + c.id, value: componentLabel(c), position: [x, y], size: [w, h],
          style: { ...font, shape: c.stereotype === "database" ? "cylinder" : "rectangle", fillColor: COMPONENT_FILL[c.stereotype],
            strokeColor: c.stereotype === "kernel" ? "#3157d5" : "#5b74d6", dashed: c.stereotype === "artifact", whiteSpace: "wrap" } });
      }
      for (const i of components.interfaces) {
        if (!components.dependencies.some((d) => d.target === i.provider && isLollipop(d))) continue;
        const [x, y, w, h] = at("iface:" + i.provider);
        cells["iface:" + i.provider] = componentGraph.insertVertex({ parent: root, id: "iface:" + i.provider, value: shortNames(i.names), position: [x, y], size: [w, h],
          style: { ...font, shape: "ellipse", fillColor: "#ffffff", strokeColor: "#1b2130", fontSize: 9,
            verticalLabelPosition: "top", verticalAlign: "bottom", labelBackgroundColor: "#fbfcfe" } });
        componentGraph.insertEdge({ parent: root, source: cells[i.provider], target: cells["iface:" + i.provider], style: { strokeColor: "#1b2130", endArrow: "none" } });
      }
      for (const d of components.dependencies) {
        const lollipop = isLollipop(d), target = cells[lollipop ? "iface:" + d.target : d.target];
        componentGraph.insertEdge({ parent: root, source: cells[d.source], target, value: lollipop ? "" : `«${d.names[0] === "reads" ? "read" : d.names[0] === "serves" ? "serve" : "use"}»`,
          style: { ...font, fontSize: 10, strokeColor: "#4a5568", dashed: true, endArrow: "open", labelBackgroundColor: "#fbfcfe" } });
      }
    });
    componentGraph.getSelectionModel().addListener(InternalEvent.CHANGE, () => {
      const cell = componentGraph.getSelectionCell();
      const id = cell && cell.id ? (cell.id.startsWith("iface:") ? "component:" + cell.id.slice(6) : cell.id) : "";
      select(id.startsWith("component:") ? id : "", false);
    });
    keepMoves(componentGraph, "components");
    fit();
  }

  function restyleComponents() {
    if (window.PlayDeployment) window.PlayDeployment.restyle(); // the deployment diagram shows the same build evidence
    if (!componentGraph) return;
    componentGraph.batchUpdate(() => {
      for (const c of components.components) {
        const cell = componentGraph.getDataModel().getCell("component:" + c.id);
        if (cell) componentGraph.getDataModel().setValue(cell, componentLabel(c));
      }
    });
  }

  function inspectComponent(id, box) {
    const c = components.components.find((x) => x.id === id), dl = el("dl");
    box.append(el("h3", `«${c.stereotype}» ${c.name}`));
    if (c.files.length) row(dl, "Files", `${c.files.join(", ")}${c.lines ? ` (${c.lines} lines)` : ""}`);
    const provides = components.interfaces.find((i) => i.provider === id);
    if (provides && provides.names.length) row(dl, "Provides", provides.names.join(", "));
    for (const d of components.dependencies.filter((x) => x.source === id)) row(dl, "Uses " + d.target, d.names.join(", ") || "(imported)");
    for (const d of components.dependencies.filter((x) => x.target === id)) row(dl, "Used by", `${d.source}: ${d.names.join(", ") || "(imported)"}`);
    box.append(dl);
    if (c.stereotype === "kernel") box.append(el("p", "The installed EIJA package: the app asks it for every decision, so there is no second interpreter.", { class: "muted" }));
    if (components.not_drawn.length) box.append(el("p", `Not drawn (utility imports): ${components.not_drawn.join(", ")}.`, { class: "muted small" }));
  }

  // Screen designer (ADR-0154): each use case's screen, bound to the record class's attributes. The server's design
  // check (`check_screens`) runs on every edit; Build & run builds the app with these screens. Screens decide how the
  // app looks, never what it may do: the kernel still decides every action.
  function screenLink(action) {
    const button = el("button", "Design its screen", { type: "button", class: "quiet" });
    button.addEventListener("click", () => openScreen(action));
    return button;
  }

  function openScreen(action) {
    useCase = action;
    showTab("screens");
  }

  const record = () => (data ? data.entities.find((e) => e.name === data.record) : null);
  const screenOf = (name) => screens.screens.find((s) => s.use_case === name);

  // With edits, only the problems come back into the page: the designer keeps editing its own objects.
  async function loadScreens(edited) {
    const planAt = JSON.stringify(about().plan), sent = edited ? JSON.stringify(edited) : null;
    const result = await api("/api/play/screens", { ...about(), screens: edited || null });
    // A newer model or design replaced the one checked: its own check is on the way, so this answer is not shown.
    if (JSON.stringify(about().plan) !== planAt || (sent !== null && JSON.stringify(screens) !== sent)) return result;
    if (!edited) screens = result.screens;
    problems = result.problems;
    a11y = result.accessibility;
    problemsFor = screensKey();
    useCaseList = result.use_cases;
    renderHealth();
    return result;
  }

  function changed(label = "edit a screen") {
    screensEdited = true;
    commit(label);
    lastBuild = null; // the last build was of other screens
    restyleComponents();
    components = null;
    renderDesigner();
    clearTimeout(checkTimer);
    problemsFor = null; // pending until the check of this design answers
    renderHealth();
    checkTimer = setTimeout(async () => {
      try {
        await loadScreens(screens);
      } catch (error) {
        problems = [{ code: error.code || "ERROR", use_case: useCase, text: error.message }];
        a11y = null;
        problemsFor = screensKey();
      }
      renderProblems();
      renderAccessibility();
      renderScreenList();
      renderHealth();
      if (plan) refreshRipple();
    }, 250);
  }

  function renderProblems() {
    const box = $("screen-problems");
    box.replaceChildren();
    box.className = "problems " + (problems.length ? "bad" : "ok");
    if (!problems.length) { box.append(el("span", "✓ Design check passed: every screen can be built.")); return; }
    for (const p of problems) {
      const b = el("button", `${p.code}: ${p.text}`, { type: "button" });
      b.addEventListener("click", () => { useCase = p.use_case; renderDesigner(); });
      box.append(b);
    }
  }

  // The accessibility check (ADR-0218): the server judges the screens and the built app's page against WCAG 2.2 AA
  // success criteria; each check shows its criteria, its verdict and, for contrast, the measured ratios.
  function renderAccessibility() {
    const box = $("screen-a11y");
    if (!box) return;
    if (!a11y) { box.hidden = true; return; }
    const warned = a11y.checks.filter((c) => c.status === "WARN").length;
    box.hidden = false;
    box.className = "a11y " + (a11y.failed ? "bad" : warned ? "warn" : "ok");
    box.open = Boolean(a11y.failed) || box.open;
    const summary = el("summary");
    summary.append(el("span", a11y.failed ? "✗" : "✓", { class: "a11y-mark" }),
      el("span", `Accessibility (${a11y.standard}): ${a11y.passed} of ${a11y.checks.length} checks pass` + (a11y.failed ? `, ${a11y.failed} fail` : "") + (warned ? `, ${warned} to look at` : "")));
    const list = el("ul", undefined, { class: "a11y-checks" });
    for (const c of a11y.checks) {
      const li = el("li", undefined, { class: "a11y-" + c.status.toLowerCase(), "data-check": c.check });
      li.append(el("span", c.status, { class: "a11y-status" }), el("span", c.text), el("span", `SC ${c.wcag}`, { class: "a11y-sc muted" }));
      if (c.detail && c.detail.pairs) {
        const pairs = el("ul", undefined, { class: "a11y-pairs" });
        for (const p of c.detail.pairs) {
          const swatch = el("span", "Aa", { class: "a11y-swatch", "aria-hidden": "true" });
          swatch.style.color = p.foreground;
          swatch.style.background = p.background;
          const row = el("li", undefined, { class: p.ratio < 4.5 ? "low" : "" });
          row.append(swatch, el("span", `${p.what}: ${p.ratio}:1`));
          pairs.append(row);
        }
        li.append(pairs);
      }
      list.append(li);
    }
    box.replaceChildren(summary, list, el("p", a11y.limits, { class: "muted small" }));
  }

  function renderScreenList() {
    const list = $("screen-list");
    list.replaceChildren();
    // Every use case of the model, then any screen for a use case the model no longer has.
    const names = [...useCaseList, ...screens.screens.map((x) => x.use_case).filter((u) => !useCaseList.includes(u))];
    for (const name of names) {
      const bad = problems.some((p) => p.use_case === name);
      const b = el("button", undefined, { type: "button", "aria-current": String(name === useCase) });
      b.append(el("span", name === null ? "Create" : name), el("span", bad ? "⚠" : "✓", { class: bad ? "mark bad" : "mark ok" }));
      b.addEventListener("click", () => { useCase = name; renderDesigner(); });
      const li = el("li");
      li.append(b);
      list.append(li);
    }
    for (const f of hooks.screens) f({ list, names });
  }

  function addField(name, at) {
    const screen = screenOf(useCase);
    if (!screen || screen.fields.some((f) => f.attribute === name)) return;
    const fields = [...screen.fields];
    fields.splice(at === undefined ? fields.length : at, 0, { attribute: name, label: "" });
    screen.fields = fields;
    changed(`add ${name} to the ${screen.title} screen`);
  }

  function moveField(from, to) {
    const screen = screenOf(useCase), fields = [...screen.fields];
    const [moved] = fields.splice(from, 1);
    fields.splice(to > from ? to - 1 : to, 0, moved);
    screen.fields = fields;
    changed(`move ${moved.attribute} on the ${screen.title} screen`);
  }

  function input(value, label, onChange) {
    const node = el("input", undefined, { type: "text", value, "aria-label": label, maxlength: "60" });
    node.addEventListener("change", () => onChange(node.value));
    return node;
  }

  function fieldRow(screen, f, i) {
    const a = record() && record().attributes.find((x) => x.name === f.attribute);
    const li = el("li", undefined, { class: "screen-field", draggable: "true", "data-index": String(i) });
    li.addEventListener("dragstart", (event) => event.dataTransfer.setData("text/eija-field", String(i)));
    const grip = el("span", "⠿", { class: "grip", "aria-hidden": "true" });
    const name = input(f.label, `Label for ${f.attribute}`, (v) => { f.label = v; changed(`relabel ${f.attribute}`); });
    name.placeholder = f.attribute;
    const preview = el("span", a ? (a.type === "choice" ? `one of ${a.choices.join(", ")}` : a.type) + (a.required ? " · required" : "") : "not in the record", { class: "muted small field-meta" });
    const up = el("button", "↑", { type: "button", class: "quiet", "aria-label": `Move ${f.attribute} up` });
    up.disabled = i === 0;
    up.addEventListener("click", () => moveField(i, i - 1));
    const remove = el("button", "×", { type: "button", class: "quiet", "aria-label": `Remove ${f.attribute}` });
    remove.addEventListener("click", () => { screen.fields = screen.fields.filter((_, j) => j !== i); changed(`remove ${f.attribute} from the ${screen.title} screen`); });
    li.append(grip, el("code", f.attribute), name, preview, up, remove);
    return li;
  }

  function dropZone(list) {
    // A line shows where the field will go before you let go: above the row under the pointer's upper half, or last.
    const slot = (event) => {
      const rows = [...list.querySelectorAll(".screen-field")];
      const target = rows.findIndex((r) => event.clientY < r.getBoundingClientRect().top + r.offsetHeight / 2);
      return [rows, target === -1 ? rows.length : target];
    };
    const clear = () => {
      list.classList.remove("over", "drop-end");
      for (const r of list.querySelectorAll(".drop-before")) r.classList.remove("drop-before");
    };
    list.addEventListener("dragover", (event) => {
      event.preventDefault();
      const [rows, at] = slot(event);
      clear();
      list.classList.add("over");
      if (at < rows.length) rows[at].classList.add("drop-before");
      else if (rows.length) list.classList.add("drop-end");
    });
    list.addEventListener("dragleave", (event) => { if (!list.contains(event.relatedTarget)) clear(); });
    list.addEventListener("drop", (event) => {
      event.preventDefault();
      clear();
      const [, at] = slot(event);
      const moving = event.dataTransfer.getData("text/eija-field"), adding = event.dataTransfer.getData("text/eija-attribute");
      if (moving !== "") moveField(Number(moving), at);
      else if (adding) addField(adding, at);
    });
  }

  function renderCard() {
    const card = $("screen-card"), screen = screenOf(useCase);
    card.replaceChildren();
    if (!screen) {
      const add = el("button", "Give it a screen", { type: "button" });
      add.addEventListener("click", () => {
        screens.screens = [...screens.screens, { use_case: useCase, title: useCase, fields: [], button: useCase }];
        changed(`give ${useCase} a screen`);
      });
      card.append(el("p", `${useCase} has no screen yet.`, { class: "muted" }), add);
      return;
    }
    const t = model.transitions.find((x) => x.action === useCase);
    if (useCase !== null && !t) {
      const remove = el("button", "Remove this screen", { type: "button" });
      remove.addEventListener("click", () => { screens.screens = screens.screens.filter((x) => x !== screen); useCase = null; changed(`remove the ${screen.title} screen`); });
      card.append(el("p", `The model has no use case ${useCase}, so this screen cannot be built.`, { class: "muted" }), remove);
      return;
    }
    card.append(el("p", useCase === null ? "Starts a record · any actor" : `${t.from_state} → ${t.to_state} · ${t.role}`, { class: "muted small" }));
    card.append(input(screen.title, "Screen title", (v) => { screen.title = v || screen.title; changed("retitle a screen"); }));
    card.lastChild.classList.add("screen-title");
    const list = el("ul", undefined, { class: "screen-fields", "aria-label": "Fields on this screen" });
    screen.fields.forEach((f, i) => list.append(fieldRow(screen, f, i)));
    if (!screen.fields.length) list.append(el("li", "Drop record attributes here.", { class: "muted drop-hint" }));
    dropZone(list);
    const button = input(screen.button, "Button label", (v) => { screen.button = v; changed(`relabel the ${screen.title} button`); });
    button.placeholder = useCase === null ? "Create" : useCase;
    button.classList.add("screen-button");
    card.append(list, button);
    for (const f of hooks.screens) f({ card, useCase });
  }

  function renderPalette() {
    const list = $("palette"), screen = screenOf(useCase);
    list.replaceChildren();
    if (!record()) { list.append(el("li", "This pack has no data model, so screens have no fields.", { class: "muted" })); return; }
    for (const a of record().attributes) {
      const used = screen && screen.fields.some((f) => f.attribute === a.name);
      const li = el("li", undefined, { class: "chip-row", draggable: String(!used) });
      li.addEventListener("dragstart", (event) => event.dataTransfer.setData("text/eija-attribute", a.name));
      const add = el("button", used ? "On screen" : "Add", { type: "button", class: "quiet" });
      add.disabled = used;
      add.addEventListener("click", () => addField(a.name));
      li.append(el("span", attributeLine(a)), add);
      list.append(li);
    }
  }

  function renderDesigner() {
    if (!screens) return;
    renderScreenList();
    renderProblems();
    renderAccessibility();
    renderCard();
    renderPalette();
    const link = $("screens-download");
    if (link.href.startsWith("blob:")) URL.revokeObjectURL(link.href);
    link.href = URL.createObjectURL(new Blob([JSON.stringify(screens, null, 2) + "\n"], { type: "application/json" }));
  }

  // The running app opens acting as `actor` when one is given (ADR-0215): the generated page reads #actor=<id>.
  function showRun(url, actor) {
    const at = url + (actor ? "#actor=" + encodeURIComponent(actor) : "");
    $("run").hidden = false;
    $("run-frame").src = at;
    $("run-open").href = at;
  }

  // Run the app as one fixture actor: the last build when it is of the model and screens on show, else a new one.
  async function runAs(actor) {
    // Reuse it only while its app still runs in the frame: the run bar's Stop ends the process and blanks the frame.
    const running = Boolean(lastBuild && lastBuild.url) && !$("run").hidden && $("run-frame").src.startsWith(lastBuild.url);
    if (running && lastBuild.key === viewKey() && lastBuild.conformance.status === "PASS") showRun(lastBuild.url, actor);
    else await build(actor);
  }

  async function build(actor) {
    const button = $("build"), score = $("score");
    button.disabled = true;
    score.hidden = false;
    score.className = "score";
    score.textContent = "Building and checking against the kernel…";
    try {
      // Send the model on screen; the server refuses (MODEL_CHANGED) if it is no longer the one it would build.
      const key = viewKey();
      const result = await api("/api/play/build", { ...about(), screens: screensEdited ? screens : null });
      const pass = result.conformance.status === "PASS";
      lastBuild = { ...result, key };
      if (pass) rewardTrying("build", 3, `Built the AI's change and ran its ${result.cases} conformance cases`, key);
      renderHealth();
      restyleComponents();
      score.className = "score " + (pass ? "ok" : "bad");
      score.textContent = pass ? `✓ ${result.cases}/${result.cases} cases match the kernel` : `✗ Conformance ${result.conformance.status}: not started`;
      score.title = `Model ${result.model.slice(0, 12)} · ${result.files} files · kernel source review: ${result.kernel_source_review}`;
      if (result.url) showRun(result.url, typeof actor === "string" ? actor : "");
    } catch (error) {
      score.className = "score bad";
      score.textContent = error.code === "MODEL_CHANGED"
        ? "The model changed since this page loaded. Reload to see it, then build again."
        : `Build refused (${error.code || "ERROR"}): ${error.message}`;
    } finally {
      button.disabled = false;
    }
  }

  // Simulate (ADR-0152): the server runs seeded fixture users through the kernel; the page only paints the counts.
  function restyle(id, extra, value) {
    const cell = graph.getDataModel().getCell(id);
    if (!cell || !base[id]) return;
    graph.getDataModel().setStyle(cell, { ...base[id].style, ...extra });
    graph.getDataModel().setValue(cell, value === undefined ? base[id].value : value);
  }

  function paint(result) {
    const maxCommits = Math.max(1, ...Object.values(result.transitions).map((t) => t.committed));
    const maxNow = Math.max(1, ...Object.values(result.states).map((s) => s.now));
    graph.batchUpdate(() => {
      for (const t of model.transitions) {
        const r = result.transitions[t.id], refused = Object.values(r.refused).reduce((a, b) => a + b, 0);
        const width = 1 + 5 * (r.committed / maxCommits);
        restyle("transition:" + t.id, { strokeWidth: width, strokeColor: r.committed ? "#2f6f4f" : "#c27c0e", dashed: !r.committed },
          `${label(t)}\n✓ ${r.committed}${refused ? `  ✗ ${refused}` : ""}`);
      }
      for (const s of model.states) {
        const r = result.states[s], heat = r.now / maxNow;
        const fill = r.entered ? `rgba(49,87,213,${(0.08 + 0.42 * heat).toFixed(2)})` : "#fdf4e3";
        restyle("state:" + s, { fillColor: fill, strokeColor: r.entered ? "#5b74d6" : "#c27c0e" }, `${s}\n${r.now} here · ${r.entered} in`);
      }
    });
  }

  function clearSimPanel() {
    clearInterval(replayTimer);
    sim = null;
    $("sim").hidden = true;
    renderHealth();
  }

  function clearSim() {
    clearSimPanel();
    graph.batchUpdate(() => { for (const id of Object.keys(base)) restyle(id, {}); });
    if (plan && plan.previewing) highlight(plan.result.diff);
  }

  function step(entry) {
    const kind = roleKind(entry.role), parts = [entry.actor + (kind === "human" ? "" : ` (${ACTOR_KINDS[kind]})`), entry.outcome === "CREATED" ? `created ${entry.record}` : `${entry.action} on ${entry.record}`];
    if (entry.outcome === "COMMITTED") parts.push(`→ ${entry.to}`);
    if (entry.outcome === "REFUSED") parts.push(`refused: ${entry.code}`);
    return parts.join(" ");
  }

  function showSim(result) {
    sim = result;
    $("sim").hidden = false;
    $("sim-summary").replaceChildren(el("strong", String(result.attempts)), document.createTextNode(" attempts by simulated users on "),
      el("strong", String(result.records)), document.createTextNode(" records: "), el("strong", String(result.committed)),
      document.createTextNode(" went through, "), el("strong", String(result.refused)), document.createTextNode(" refused by the kernel."));
    $("sim-codes").replaceChildren(...Object.entries(result.codes).map(([code, n]) => el("span", `${code} ${n}`, { class: "chip" })));
    showKinds(result.by_kind || {});
    $("sim-findings").replaceChildren(...(result.findings.length ? result.findings.map((f) => {
      const li = el("li", undefined, { class: f.severity }), b = el("button", f.text, { type: "button" });
      b.addEventListener("click", () => select(f.element, true));
      li.append(b);
      return li;
    }) : [el("li", "Nothing stood out in this run.", { class: "muted" })]));
    $("sim-log").replaceChildren(...result.trace.map((entry) => {
      const li = el("li", undefined, { class: entry.outcome.toLowerCase() });
      li.append(el("span", String(entry.step), { class: "n" }), el("span", step(entry)));
      return li;
    }));
    $("sim-limits").textContent = `Seed ${result.seed}, ${result.steps} steps. ` + result.limits.join(" ");
    paint(result);
    document.dispatchEvent(new CustomEvent("playide:simulated", { detail: result }));
  }

  // Who acted, by kind of actor (ADR-0210): what the AI agents, timers and external systems tried and what the kernel
  // said, beside the people. Shown only when the system has an actor that is not a person.
  function showKinds(byKind) {
    const kinds = Object.keys(byKind), box = $("sim-kinds");
    box.hidden = !kinds.some((k) => k !== "human");
    box.replaceChildren(...(box.hidden ? [] : kinds.map((kind) => {
      const k = byKind[kind], row = el("li", undefined, { class: "kind-" + kind });
      const codes = Object.entries(k.codes).slice(0, 2).map(([code, n]) => `${code} ${n}`).join(", ");
      row.title = Object.entries(k.codes).map(([code, n]) => `${code} ${n}`).join(", ");
      row.append(el("strong", ACTOR_GROUPS[kind]), el("span", ` (${k.roles.join(", ")}) `, { class: "muted" }),
        document.createTextNode(`${k.attempts} tries · ${k.committed} went through · ${k.refused} refused` + (codes ? `: ${codes}` : "")));
      return row;
    })));
  }

  function replay() {
    if (!sim) return;
    clearInterval(replayTimer);
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) { paint(sim); return; } // no animation: the log has every step
    const rows = [...$("sim-log").children];
    let i = 0;
    replayTimer = setInterval(() => {
      rows.forEach((row) => row.classList.remove("current"));
      if (i >= sim.trace.length) { clearInterval(replayTimer); paint(sim); return; }
      const entry = sim.trace[i];
      rows[i].classList.add("current");
      const log = $("sim-log"); // scroll the log alone, so the panel keeps its summary in view
      log.scrollTop = Math.max(0, rows[i].offsetTop - log.clientHeight / 2);
      paint(sim);
      graph.batchUpdate(() => {
        const t = entry.action && model.transitions.find((x) => x.action === entry.action);
        if (t) restyle("transition:" + t.id, { strokeColor: entry.outcome === "REFUSED" ? "#a12f2f" : "#3157d5", strokeWidth: 6 }, graph.getDataModel().getCell("transition:" + t.id).value);
        const at = entry.outcome === "REFUSED" ? entry.from : entry.to;
        if (at) restyle("state:" + at, { strokeColor: entry.outcome === "REFUSED" ? "#a12f2f" : "#3157d5", strokeWidth: 4 }, graph.getDataModel().getCell("state:" + at).value);
        document.dispatchEvent(new CustomEvent("playide:step", { detail: { ...entry, transition: t ? t.id : null, ms: 450 } }));
      });
      const here = entry.outcome === "REFUSED" ? entry.from : entry.to, step = entry.action && model.transitions.find((x) => x.action === entry.action);
      if (here) follow(["state:" + here, ...(step ? ["transition:" + step.id] : [])]); // the state and the line taken, as Run does
      i += 1;
    }, 450);
  }

  async function simulate() {
    const button = $("simulate");
    button.disabled = true;
    try {
      const key = viewKey();
      showSim(await api("/api/play/simulate", { ...about(), seed: 1, steps: 500 }));
      simKey = key;
      rewardTrying("simulate", 2, "Simulated users on the AI's change", key);
      renderHealth();
    } catch (error) {
      $("sim").hidden = false;
      $("sim-summary").textContent = error.code === "MODEL_CHANGED"
        ? "The model changed since this page loaded. Reload to see it, then simulate again."
        : `Simulation refused (${error.code || "ERROR"}): ${error.message}`;
    } finally {
      button.disabled = false;
    }
  }

  // Undo, redo and autosave (ADR-0198). What a person edits in PlayIDE is a document of two parts: the plan (its typed
  // steps, AI or drawn, and which are accepted) and the screens edited in the designer. The model in force is never
  // edited here, so every edit (drawing on the diagram, the inspector's tools, the palette, the Delete key, an AI plan,
  // ticking a step, taking a follow-on, any screen edit) is one snapshot of that document. Undo and redo move between
  // snapshots and ask the server to check the restored plan again, as for any other edit: nothing is trusted from the
  // edits. Each snapshot is also written to this browser's storage as it is made, so a crash or a reload loses
  // nothing; on the next load the work comes back, with its history. Saving a system to a file is not this: it is
  // the document's job of another feature, which reads document() and listens for "playide:edit".
  const REVIEW_VIEW = new URLSearchParams(location.search).get("view") === "review"; // read-only: no history, no draft
  const HISTORY_LIMIT = 100, STORED = 30; // snapshots kept in the page, and in storage beside the current one
  const edits = { stack: [], at: -1 }; // the snapshots, and the one shown
  let restoring = false, planUid = 0, recoveredWork = false;
  const clone = (value) => (value == null ? null : JSON.parse(JSON.stringify(value)));
  const draftKey = () => `playide.draft.v1:${packInfo.id}:${caseId || ""}`;
  // A short fingerprint of the model in force, so a restored draft can say when it was made on another model.
  const modelPrint = () => { let h = 2166136261; for (const c of JSON.stringify(baseModel)) h = Math.imul(h ^ c.charCodeAt(0), 16777619) >>> 0; return h.toString(16); };

  function documentNow() {
    let kept = null;
    if (plan) {
      const { card, result, seq, rewarded, preview, previewing, ...rest } = plan; // view state stays out of the document
      kept = clone(rest);
    }
    return { plan: kept, screens: screensEdited ? clone(screens) : null };
  }

  function stepLabel(tx) {
    const t = tx.transition && model.transitions.find((x) => x.id === tx.transition), name = t ? t.action : tx.transition;
    return ({
      add_state: () => `add state ${tx.state}`, remove_state: () => `remove state ${tx.state}`, rename_state: () => `rename ${tx.state} to ${tx.to}`,
      set_initial: () => `start records in ${tx.state}`, add_transition: () => `add ${tx.action}`, remove_transition: () => `remove ${name}`,
      set_role: () => `let ${tx.role} take ${name}`, set_role_kind: () => `make ${tx.role} ${A_KIND[tx.to]}`, retarget_transition: () => `move ${name}'s ${tx.end} to ${tx.state}`,
    }[tx.kind] || (() => tx.kind.replace(/_/g, " ")))();
  }

  function commit(label) {
    if (restoring || REVIEW_VIEW || edits.at < 0) return;
    edits.stack.splice(edits.at + 1);
    edits.stack.push({ label, doc: documentNow(), card: plan && plan.card, at: Date.now() });
    if (edits.stack.length > HISTORY_LIMIT) edits.stack.shift();
    edits.at = edits.stack.length - 1;
    persist();
    renderHistory();
    for (const f of hooks.edit) f(label);
    document.dispatchEvent(new CustomEvent("playide:edit", { detail: { label } }));
  }

  function renderHistory() {
    const back = edits.stack[edits.at], next = edits.stack[edits.at + 1];
    $("undo").disabled = edits.at <= 0;
    $("redo").disabled = !next;
    $("undo").title = edits.at > 0 ? `Undo ${back.label} (Ctrl+Z)` : "Nothing to undo (Ctrl+Z)";
    $("redo").title = next ? `Redo ${next.label} (Ctrl+Shift+Z)` : "Nothing to redo (Ctrl+Shift+Z)";
  }

  function notify(text) {
    const toast = $("toast");
    toast.textContent = text;
    toast.classList.add("show");
    clearTimeout(earn.timer);
    earn.timer = setTimeout(() => toast.classList.remove("show"), 2600);
  }

  async function undo() {
    if (edits.at <= 0) return;
    const undone = edits.stack[edits.at];
    edits.at -= 1;
    notify(`Undid: ${undone.label}`);
    await restore(edits.stack[edits.at]);
  }

  async function redo() {
    if (edits.at + 1 >= edits.stack.length) return;
    edits.at += 1;
    notify(`Redid: ${edits.stack[edits.at].label}`);
    await restore(edits.stack[edits.at]);
  }

  // A plan card that leaves the document: a drawn draft disappears from the chat; an AI plan stays as a record.
  function setAside(gone) {
    if (gone.scope === "plan-draft") { gone.card.remove(); return; }
    for (const control of gone.card.querySelectorAll("input, button")) control.disabled = true;
    gone.card.firstChild.append(el("p", "Undone.", { class: "muted small" }));
  }

  async function restore(entry) {
    persist();
    renderHistory();
    restoring = true;
    let pending = null;
    try {
      const doc = entry.doc, old = plan;
      if (old && old.previewing) leavePreview();
      ripple = null;
      rippleSeq += 1;
      if (old && (!doc.plan || doc.plan.uid !== old.uid)) setAside(old);
      if (!doc.plan) {
        plan = null;
      } else {
        const same = old && doc.plan.uid === old.uid;
        plan = { ...clone(doc.plan), previewing: false, result: null, card: same ? old.card : entry.card || null, rewarded: same ? old.rewarded : new Set() };
        if (plan.card && !plan.card.isConnected) $("chat-log").append(plan.card);
        if (!plan.card) plan.card = say(plan.scope === "plan-draft" ? "draft" : "ai", el("div"));
        plan.card.replaceChildren(planCard());
        pending = plan;
      }
      renderBadges();
      renderHealth();
      document.dispatchEvent(new CustomEvent("playide:plan"));
      if (doc.screens) { screens = clone(doc.screens); changed(); }
      else if (screensEdited) await resetScreens();
    } finally {
      restoring = false;
    }
    if (pending && pending === plan) {
      const result = await refreshPlan();
      if (result && result.legal && result.accepted && pending === plan && !plan.previewing) enterPreview();
    }
  }

  // Every snapshot is written as it is made, so a crash loses nothing. Storage can be full or blocked: the page still
  // works, and the status bar says the work is not kept.
  // The status bar is the one place that states the save state: the system's own save (play-systems.js, which
  // dispatches playide:savestate) and the browser's kept-edits note, joined with a separator.
  let browserNote = { bad: false, text: "", title: "" };
  function renderSaveStatus() {
    const status = $("status-saved");
    if (!status) return;
    const system = $("system-saved")?.textContent || "";
    status.textContent = [system, browserNote.text].filter(Boolean).join(" · ");
    status.className = browserNote.bad ? "saved bad" : "saved";
    status.title = [browserNote.title, system && "Save your work on this system with Save (Ctrl+S)."].filter(Boolean).join(" ");
  }
  document.addEventListener("playide:savestate", renderSaveStatus);

  function persist() {
    if (REVIEW_VIEW || !packInfo) return;
    const now = edits.stack[edits.at], empty = !now || (!now.doc.plan && !now.doc.screens); // nothing to keep
    try {
      if (empty) { localStorage.removeItem(draftKey()); browserNote = { bad: false, text: "", title: "" }; renderSaveStatus(); return; }
      const from = Math.max(0, edits.at - STORED), keep = edits.stack.slice(from, edits.at + STORED + 1);
      const draft = { v: 1, model: modelPrint(), saved: Date.now(), at: edits.at - from, stack: keep.map(({ label, doc, at }) => ({ label, doc, at })) };
      try { localStorage.setItem(draftKey(), JSON.stringify(draft)); } catch {
        localStorage.setItem(draftKey(), JSON.stringify({ ...draft, at: 0, stack: [keep[edits.at - from]] })); // the current work, without its history
      }
      browserNote = { bad: false, text: "Edits kept in this browser", title: `Your plan and screen edits are kept in this browser as you work (${new Date(draft.saved).toLocaleTimeString()}). Nothing is applied.` };
    } catch {
      browserNote = { bad: true, text: "Not kept: browser storage is unavailable", title: "Undo still works, but a reload or crash would lose these edits." };
    }
    renderSaveStatus();
  }

  // On load: the draft this browser kept for this model, if any, comes back with its history. The server checks the
  // restored plan again; a step that no longer applies (the model in force changed) is shown as such.
  async function recover() {
    edits.stack = [{ label: "open the model", doc: { plan: null, screens: null }, card: null, at: Date.now() }];
    edits.at = 0;
    renderHistory();
    if (REVIEW_VIEW) return;
    let draft = null;
    try { draft = JSON.parse(localStorage.getItem(draftKey()) || "null"); } catch { draft = null; }
    if (!draft || draft.v !== 1 || !Array.isArray(draft.stack) || !draft.stack[draft.at]) return;
    planUid = Math.max(0, ...draft.stack.map((e) => (e.doc.plan && e.doc.plan.uid) || 0));
    edits.stack = [...(draft.stack[0].doc.plan || draft.stack[0].doc.screens ? [edits.stack[0]] : []), ...draft.stack.map((e) => ({ ...e, card: null }))];
    edits.at = edits.stack.length - draft.stack.length + draft.at;
    const entry = edits.stack[edits.at], steps = entry.doc.plan ? entry.doc.plan.steps.length : 0;
    const note = el("p", `Recovered your unsaved work from ${new Date(draft.saved).toLocaleString()}: ${steps} plan step${steps === 1 ? "" : "s"}${entry.doc.screens ? " and screen edits" : ""}. Undo still steps back through it.`);
    if (draft.model !== modelPrint()) note.append(el("span", " The model in force has changed since, so every step is checked against it again.", { class: "muted" }));
    const discard = el("button", "Discard it", { type: "button", class: "quiet" });
    discard.addEventListener("click", async () => {
      discard.disabled = true;
      await restore({ doc: { plan: null, screens: null }, card: null });
      commit("discard the recovered work"); // undoable, like any edit
    });
    note.append(" ", discard);
    say("ai", note).classList.add("recovered");
    recoveredWork = true;
    await restore(entry);
  }

  async function resetScreens() {
    screensEdited = false;
    lastBuild = null;
    restyleComponents();
    components = null;
    await loadScreens(null);
    renderDesigner();
    if (plan) refreshRipple();
  }

  function historyKeys(event) {
    if (!(event.ctrlKey || event.metaKey) || event.altKey || event.defaultPrevented || REVIEW_VIEW) return;
    const key = event.key.toLowerCase(), target = event.target;
    if (key !== "z" && key !== "y") return;
    // Text boxes keep the browser's own undo for the text being typed.
    if (target && (target.closest("input, textarea, select, [contenteditable=true]"))) return;
    event.preventDefault();
    if (key === "y" || event.shiftKey) redo(); else undo();
  }

  async function start() {
    if (caseId) {
      const view = await api(`/api/cases/${encodeURIComponent(caseId)}`);
      model = view.case.candidate || view.case.baseline;
    } else {
      model = (await api("/api/status")).baseline;
    }
    baseModel = model;
    const status = await api("/api/status");
    $("model-name").textContent = status.pack.name + (caseId ? " · change case" : "");
    packInfo = status.pack;
    const dataDoc = await api("/api/play/data");
    data = savedData = dataDoc.data;
    savedBuild = dataDoc.build;
    roleKinds = Object.fromEntries((await api("/api/play/roles")).roles.map((r) => [r.id, r.kind]));
    await loadScreens(null);
    outline();
    draw(model);
    inspect("");
    const t = model.transitions[model.transitions.length - 1];
    // The example has to pass as it stands. On the model in force that is the pack's own demo request, when the pack
    // models it (a system started here has no modelled changes yet). Otherwise, and on a change case's candidate, typed steps: an action names one transition, so the second step takes a
    // declared action no transition uses yet, and it leaves a state that already has a way out (a pack's laws may keep
    // its end states closed).
    const free = t && packInfo.actions.find((a) => !model.transitions.some((u) => u.action === a));
    if (!caseId && packInfo.demo_request && packInfo.demo_modelled) $("chat-example").textContent = packInfo.demo_request.replace(/[.\s]+$/, "");
    else if (t) $("chat-example").textContent = `add state Archived after ${t.from_state}` + (free ? ` then add ${free} from ${t.from_state} to Archived for ${t.role}` : "");
    $("build").addEventListener("click", build);
    $("simulate").addEventListener("click", simulate);
    $("sim-replay").addEventListener("click", replay);
    $("sim-clear").addEventListener("click", clearSim);
    $("fit").addEventListener("click", () => fit(true));
    $("tidy").addEventListener("click", tidy);
    $("zoom-in").addEventListener("click", () => current() && current().zoomIn());
    $("zoom-out").addEventListener("click", () => current() && current().zoomOut());
    $("tab-states").addEventListener("click", () => showTab("states"));
    $("tab-sequences").addEventListener("click", () => showTab("sequences"));
    $("tab-classes").addEventListener("click", () => showTab("classes"));
    $("tab-usecases").addEventListener("click", () => showTab("usecases"));
    $("tab-screens").addEventListener("click", () => showTab("screens"));
    $("tab-components").addEventListener("click", () => showTab("components"));
    $("tab-laws").addEventListener("click", () => showTab("laws"));
    $("tab-tests").addEventListener("click", () => showTab("tests"));
    $("tab-access").addEventListener("click", () => showTab("access"));
    $("chat-form").addEventListener("submit", ask);
    for (const key of Object.keys(DIAGRAMS)) $("tab-" + key).append(el("span", "", { class: "badge", hidden: "" }));
    startDrawing();
    $("health").addEventListener("click", () => {
      const open = $("checks").hidden;
      $("checks").hidden = !open;
      $("health").setAttribute("aria-expanded", String(open));
    });
    renderHealth();
    $("plan-back").addEventListener("click", leavePreview);
    $("plan-review").addEventListener("click", () => showTab("review"));
    $("tab-review").addEventListener("click", () => showTab("review"));
    PlayReview.init({ api, about, earn, el });
    $("screens-reset").addEventListener("click", async () => { await resetScreens(); commit("reset the screens"); });
    $("undo").addEventListener("click", undo);
    $("redo").addEventListener("click", redo);
    document.addEventListener("keydown", historyKeys);
    $("canvas-help").textContent = HINTS.states;
    window.addEventListener("resize", fit);
    await recover();
    document.body.dataset.ready = "true";
    document.dispatchEvent(new CustomEvent("playide:ready"));
  }

  // What the run bar (play-run.js, ADR-0160) may use. It holds no rules either: it moves through the server's run log.
  // The assist layer (play-assist.js, ADR-0170) reads only base(), pack() and selected(): base() is the model a chat
  // request is planned against, not a previewed candidate.
  // The Changes view (play-diff.js, ADR-0176) hands over the union to draw on the class and use case diagrams, or null.
  function setChanges(ghost) {
    if (ghost === shownChange) return;
    shownChange = ghost;
    for (const [g, box] of [[classGraph, "class-canvas"], [useCaseGraph, "usecase-canvas"]]) if (g) { g.destroy(); $(box).replaceChildren(); }
    classGraph = useCaseGraph = null;
  }
  const changeMark = (status) => (window.PlayDiff && status !== "same" ? window.PlayDiff.mark(status) : "");
  const changeLook = (status, part) => (window.PlayDiff && shownChange ? window.PlayDiff.look(status, part) : {});

  window.PlayIDE = {
    api, el, hooks, about, textWidth, liftLabels, follow, roleKind, kinds: ACTOR_KINDS, actorLook: ACTOR_LOOK, inForce: (role) => roleKinds[role] || "human",
    // Change who holds a role: a step in the plan like any drawn edit, checked by the server against the laws about
    // kinds of actor; nothing is saved (#156). The review view changes nothing.
    setKind: (role, to) => (REVIEW_VIEW ? null : addStep({ kind: "set_role_kind", role, to })), reviewing: () => REVIEW_VIEW, viewKey, label, restyle, clearSim, select, showTab, fit, importPlan, runAs, openScreen,
    components: loadComponents, buildEvidence: () => evidence(), // the deployment lens (ADR-0206) reads both
    screens: () => screens, data: () => data, // the screen designer's screens and the class diagram (play-roles.js reads them)
    graph: () => graph, tab: () => tab, model: () => model, selected: () => selected, pack: () => packInfo, base: () => baseModel,
    direction: () => direction || "LR", // the state machine's layout, which the Changes view follows
    planned: () => (plan && plan.result && plan.result.legal ? accepted() : null), // the change the Changes view draws (ADR-0176)
    // The rounds of a system built in chat (ADR-0201): how many, and the accepted steps before the last one, so the
    // Changes view can show the last round alone. Null with fewer than two rounds.
    rounds: () => {
      if (!plan || !plan.result || !plan.result.legal || rounds() < 2) return null;
      const last = lastRound(), ask = plan.steps.find((x) => roundOf(x) === last && x.request);
      return { count: rounds(), last, request: ask ? ask.request : "",
        since: plan.steps.filter((x, i) => plan.accepted[i] && roundOf(x) < last).map((x) => x.transaction) };
    },
    changes: () => shownChange, // the union while the Changes view is on (ADR-0176), else null
    draft, restoreDraft, // saving and reopening the work in progress (ADR-0185)
    recovered: () => recoveredWork, // work this browser kept came back on load, so the saved draft was not opened over it
    // What the Changes view says about the change: who made each accepted step, and the ripple for exactly these steps.
    steps: () => (plan && plan.result && plan.result.legal ? plan.steps.filter((_, i) => plan.accepted[i]).map((x) => ({ author: x.author, transaction: x.transaction })) : []),
    ripple: () => (ripple && !ripple.error && ripple.key === rippleKey() ? ripple : null), diagramNames: RIPPLE,
    setChanges, diagram: (key) => ({ states: graph, classes: classGraph, usecases: useCaseGraph, components: (hooks.componentGraph && hooks.componentGraph()) || componentGraph, sequences: hooks.sequenceGraph && hooks.sequenceGraph() })[key],
    // Undo, redo and the edited document (ADR-0198): document() is what a save writes; restore(doc, label) opens one as
    // an undoable edit, checked by the server like any other.
    undo, redo, document: documentNow, history: () => ({ at: edits.at, labels: edits.stack.map((e) => e.label) }),
    restore: async (doc, label = "open a saved document") => {
      const opened = { plan: clone(doc.plan || null), screens: clone(doc.screens || null) };
      if (opened.plan) opened.plan.uid = ++planUid; // a new plan in this page, whatever it was where it was saved
      await restore({ doc: opened, card: null });
      commit(label);
    },
  };

  start().catch((error) => {
    $("inspector").replaceChildren(el("p", `Could not load the model (${error.code || "ERROR"}): ${error.message}. If the session expired, open PlayIDE from the private launch link.`, { class: "muted" }));
  });
})();
