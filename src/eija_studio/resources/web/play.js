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
  let graph, model, selected = "", sim = null, replayTimer = 0, data = null, classGraph = null, useCaseGraph = null, tab = "states";
  let components = null, componentGraph = null, lastBuild = null;
  let baseModel = null, plan = null; // the server's model, and the chat plan being previewed on top of it (if any)
  let packInfo = null, points = 0, simKey = null, cards = 0, problemsFor = null; // the pack's actions and roles; check points; what was simulated
  let shownChange = null; // while the Changes view is on: the union of the model in force and the change (ADR-0176), drawn on the class and use case diagrams too
  let ripple = null, rippleSeq = 0; // what the accepted plan does to every diagram, with the proposer's follow-ons (ADR-0158)
  const earned = [];
  let screens = null, screensEdited = false, useCase = null, checkTimer = 0, problems = [], useCaseList = [];
  const base = {}; // each cell's own style and label, so overlays can be cleared
  const hooks = { redraw: [], inspect: [], laws: [], tab: [], changeSelect: [] }; // the run bar (play-run.js) redraws its marks and adds inspector tools; play-laws.js and play-access.js draw their tabs
  // the Changes view (play-diff.js, ADR-0176) closes when another tab is shown and answers current() while open

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

  function layout(workflow) {
    const g = new dagre.graphlib.Graph({ multigraph: true }), shape = basis(workflow);
    g.setGraph({ rankdir: "LR", nodesep: 60, ranksep: 120, edgesep: 30, marginx: 30, marginy: 30 });
    g.setDefaultEdgeLabel(() => ({}));
    g.setNode("__initial", { width: INITIAL, height: INITIAL });
    for (const s of shape.states) g.setNode(s, { ...STATE });
    for (const s of shape.initials) g.setEdge("__initial", s, {}, s);
    for (const t of shape.transitions) g.setEdge(t.from_state, t.to_state, { width: 120, height: 20 }, t.id);
    dagre.layout(g);
    const at = (id) => { const n = g.node(id); return [n.x - n.width / 2, n.y - n.height / 2]; };
    // dagre's bend points, without the two ends maxGraph attaches to the state borders itself.
    const bends = (t) => g.edge(t.from_state, t.to_state, t.id).points.slice(1, -1);
    return { at, bends };
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
    graph.setTooltips(true);
    graph.getTooltipForCell = (cell) => tooltip(cell);
    const parent = graph.getDefaultParent(), place = layout(workflow), cells = {};
    const font = { fontFamily: "system-ui, sans-serif", fontColor: "#1b2130" };
    graph.batchUpdate(() => {
      const initial = graph.insertVertex({ parent, id: "initial", position: place.at("__initial"), size: [INITIAL, INITIAL],
        style: { shape: "ellipse", fillColor: "#1b2130", strokeColor: "#1b2130", resizable: false, editable: false } });
      for (const s of workflow.states) {
        cells[s] = graph.insertVertex({ parent, id: "state:" + s, value: s, position: place.at(s), size: [STATE.width, STATE.height],
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
    for (const cell of Object.values(graph.getDataModel().cells)) if (cell.id) base[cell.id] = { style: { ...cell.style }, value: cell.value };
    graph.getSelectionModel().addListener(InternalEvent.CHANGE, () => {
      const cell = graph.getSelectionCell();
      select(cell ? cell.id : "", false);
    });
    wireCanvas(graph);
    fit();
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

  const current = () => (hooks.diffGraph && hooks.diffGraph()) || ({ states: graph, classes: classGraph, usecases: useCaseGraph, components: componentGraph, review: PlayReview.graph() })[tab];
  const PANELS = { states: "canvas", classes: "class-canvas", usecases: "usecase-canvas", screens: "screens", components: "component-canvas", laws: "laws", tests: "tests", review: "review", access: "access-panel" };
  const HINTS = {
    states: "Pick State, Transition or Initial in the palette, then click the diagram (or drag it there). Double-click empty space for a new state, a state to rename it. Changes join the plan for you to preview; nothing is saved.",
    classes: "Select a class to see its attributes and associations.",
    usecases: "Select a use case to inspect it. Double-click one to design its screen.",
    screens: "Design each use case's screen. The design check runs as you edit; Build & run uses these screens.",
    components: "The built app's components, read from its generated files: every line is an import, a route or a file read.",
    laws: "The pack's laws: what this model must never do, whatever is drawn. Each is proved over every run the kernel allows, by every kind of actor.",
    tests: "The pack's test cases: scenarios of who does what and what must happen, each step run by the kernel on the model shown.",
    access: "Who can do what, from each state. Every cell is tried in the kernel with the pack's fixture actors; a previewed plan's changes are flagged.",
    review: "Review the change shown against the model in force: look at each change, predict what the kernel does, then decide. Nothing is approved from here.",
  };

  function fit() {
    if (!current()) return;
    const plugin = current().getPlugin("fit");
    plugin.maxFitScale = 1.4;
    plugin.fitCenter({ margin: 24 });
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
    if (id.startsWith("component:")) {
      inspectComponent(id.slice(10), box);
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
      row(dl, "From → to", `${t.from_state} → ${t.to_state}`);
      row(dl, "Who", t.role);
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
    // A role is not a diagram element; what it may do is the Permissions tab's column, so that is where a role opens.
    $("outline-roles").replaceChildren(...[...new Set(model.transitions.map((t) => t.role))].map((r) => {
      const button = el("button", r, { type: "button", title: `What ${r} may do, on the Permissions tab` });
      button.addEventListener("click", () => showTab("access"));
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
  const widthOf = (e) => Math.max(200, e.name.length * 9 + 60, ...e.attributes.map((a) => attributeLine(a).length * 7 + 24));

  function classLayout() {
    const g = new dagre.graphlib.Graph({ multigraph: true });
    g.setGraph({ rankdir: "LR", nodesep: 50, ranksep: 140, marginx: 30, marginy: 30 });
    g.setDefaultEdgeLabel(() => ({}));
    for (const e of data.entities) g.setNode(e.name, { width: widthOf(e), height: HEAD + ROW * Math.max(1, e.attributes.length) + 8 });
    data.associations.forEach((a, i) => g.setEdge(a.source, a.target, { width: 90, height: 20 }, "a" + i));
    const literals = literalsOf();
    g.setNode(enumName(), { width: Math.max(200, ...literals.map(([x]) => x.length * 8 + 30)), height: HEAD + ROW * literals.length + 8 });
    g.setEdge(data.record, enumName(), { width: 90, height: 20 }, "state");
    dagre.layout(g);
    return (name) => { const n = g.node(name); return [n.x - n.width / 2, n.y - n.height / 2, n.width, n.height]; };
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
    const parent = classGraph.getDefaultParent(), at = classLayout(), cells = {};
    const font = { fontFamily: "system-ui, sans-serif", fontColor: "#1b2130" };
    classGraph.batchUpdate(() => {
      for (const e of data.entities) {
        const [x, y, w, h] = at(e.name), record = e.name === data.record;
        const box = cells[e.name] = classGraph.insertVertex({ parent, id: "class:" + e.name, value: (record ? "«record»\n" : "") + e.name,
          position: [x, y], size: [w, h], style: { ...font, shape: "swimlane", startSize: HEAD, horizontal: true, fontStyle: 1, fontSize: 13,
            fillColor: record ? "#dfe6ff" : "#eef2ff", swimlaneFillColor: "#ffffff", strokeColor: "#5b74d6", rounded: false, collapsible: false } });
        e.attributes.forEach((a, i) => classGraph.insertVertex({ parent: box, id: `attr:${e.name}.${a.name}`, value: attributeLine(a),
          position: [8, HEAD + 4 + i * ROW], size: [w - 16, ROW], style: { ...font, fontSize: 12, align: "left", strokeColor: "none",
            fillColor: "none", movable: false, selectable: false } }));
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
        const left = i % 2 === 0;
        const actor = useCaseGraph.insertVertex({ parent, id: "role:" + role, value: role, position: [left ? 90 : boundary.x + boundary.w + 120, y],
          size: [36, 64], style: { ...font, shape: "actor", fillColor: "#ffffff", strokeColor: "#1b2130", verticalLabelPosition: "bottom",
            verticalAlign: "top", fontSize: 13, ...changeLook(actorStatus[role], "actor") } });
        for (const link of shape.links.filter((l) => l.role === role)) {
          useCaseGraph.insertEdge({ parent, source: actor, target: cells[link.case], style: { strokeColor: "#4a5568", endArrow: "none", ...changeLook(link.status, "line") } });
        }
      });
    });
    useCaseGraph.getSelectionModel().addListener(InternalEvent.CHANGE, () => {
      const cell = useCaseGraph.getSelectionCell(), id = cell && cell.id && cell.id.startsWith("uc:") ? cell.id.slice(3) : "";
      if (shownChange) { for (const f of hooks.changeSelect) f(cell ? cell.id : ""); return; } // the Changes view reads its own cells
      select(id === "create" ? "usecase:create" : id ? "transition:" + id : "", false);
    });
    useCaseGraph.addListener(InternalEvent.DOUBLE_CLICK, (_sender, event) => {
      const cell = event.getProperty("cell");
      if (!cell || !cell.id.startsWith("uc:") || shownChange) return;
      const id = cell.id.slice(3);
      openScreen(id === "create" ? null : transition(id).action);
    });
  }

  function showTab(which) {
    tab = which;
    for (const [name, panel] of Object.entries(PANELS)) {
      $("tab-" + name).setAttribute("aria-selected", String(which === name));
      $(panel).hidden = which !== name;
    }
    $("canvas-help").textContent = HINTS[which];
    for (const id of ["fit", "zoom-in", "zoom-out"]) $(id).hidden = which === "screens" || which === "laws" || which === "tests" || which === "access";
    $("draw-palette").hidden = which !== "states";
    $("plan-review").hidden = which === "review";
    for (const f of hooks.tab) f(which);
    if (which === "access" || which === "tests") return; // play-access.js and play-tests.js draw these on hooks.tab
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

  async function ask(event) {
    event.preventDefault();
    const input = $("chat-input"), text = input.value.trim();
    if (!text) return;
    input.value = "";
    say("you", el("p", text));
    const button = $("chat-send");
    button.disabled = true;
    try {
      const result = await api("/api/play/plan", { case_id: caseId, model: baseModel, request: text });
      retire();
      plan = { ...result, steps: result.steps.map((step) => ({ ...step, author: "ai", checked: false, caught: false })),
        accepted: result.steps.map(() => true), previewing: false, card: null, rewarded: new Set() };
      plan.card = say("ai", planCard());
      renderPlan(result.preview);
      refreshRipple();
    } catch (error) {
      say("ai", el("p", `${error.code || "ERROR"}: ${error.message}`, { class: "refusal" }));
    } finally {
      button.disabled = false;
    }
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
    const box = el("div", undefined, { class: "plan" });
    box.append(el("p", plan.summary || "A plan", { class: "plan-summary" }),
      el("p", plan.scope === "plan-draft" ? (plan.provider === "imported" ? "Imported from a UML file · checked by the server like any plan"
        : "Drawn by you on the diagram · checked by the server like any plan")
        : `${plan.provider}${plan.live ? "" : " · offline fixture, not a live model"} · untrusted until you check it`, { class: "muted small" }));
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
      li.append(check, text, el("span", "", { class: "step-status" }));
      if (step.why) li.append(el("p", step.why, { class: "muted small why" }));
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
      li.className = s.status + (plan.steps[i].checked ? " checked" : "");
      li.querySelector(".step-status").textContent = marks[s.status] + (s.code ? ` ${s.code}` : "");
      li.querySelector(".step-status").title = s.message || "";
    });
    const verdict = plan.card.querySelector(".plan-verdict");
    verdict.className = "plan-verdict " + (result.legal ? "ok" : "bad");
    verdict.textContent = !result.accepted ? "No step accepted: nothing would change."
      : result.legal ? `${result.accepted} of ${plan.steps.length} steps accepted. The policy allows the result: ${changes(result.diff)}.`
      : result.codes.includes("PLAN_STEP_DOES_NOT_APPLY")
        ? `Step ${result.steps.findIndex((x) => x.status === "does_not_apply") + 1} does not apply after the steps you kept (${result.steps.find((x) => x.status === "does_not_apply").message}).`
        : `The policy refuses the accepted steps: ${result.codes.join(", ") || result.message}.`;
    plan.card.querySelector(".plan-tools .primary").disabled = !result.legal && !plan.previewing;
    plan.card.querySelector(".plan-tools .review-it").disabled = !result.legal;
    renderHealth();
    document.dispatchEvent(new CustomEvent("playide:plan")); // the change shown is different now (ADR-0176)
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
    redrawAll(plan.result.candidate);
    highlight(plan.result.diff);
    for (const which of Object.keys(DIAGRAMS)) markRipple(which);
    $("plan-banner").hidden = false;
    $("plan-banner-text").textContent = `Previewing the plan: ${changes(plan.result.diff)}. Nothing is saved.`;
    plan.card.querySelector(".plan-tools .primary").textContent = "Back to the model";
  }

  function leavePreview() {
    if (!plan || !plan.previewing) return;
    plan.previewing = false;
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
    for (const [key, name] of Object.entries(DIAGRAMS)) {
      for (const item of ripple.diagrams[key]) {
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
      plan.steps.push({ n: plan.steps.length + 1, transaction: f.transaction, text: f.text, why: f.why, author: "ai", checked: false, caught: false, followOn: true });
      plan.accepted.push(true);
      plan.card.replaceChildren(planCard());
      const result = await refreshPlan();
      if (result && result.legal && !plan.previewing) enterPreview();
      return;
    }
    screens = f.screens;
    screensEdited = true;
    useCase = f.screen_step.op === "add" ? f.screen_step.screen.use_case : null;
    if (!plan.previewing) enterPreview();
    changed();
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
    showTab(key);
    const g = current(), ids = key === "screens" || !item.ref ? [] : cellsFor(key, item.ref);
    const cell = g && ids.map((id) => g.getDataModel().getCell(id)).find(Boolean);
    if (cell && cell.isVertex() && !cell.id.startsWith("literal:")) g.setSelectionCell(cell);
    else if (cell && cell.isEdge()) g.setSelectionCell(cell);
    if (cell) g.scrollCellToVisible(cell, true);
    const note = el("div", undefined, { class: "step-note" });
    note.append(el("p", `${DIAGRAMS[key]}: ${item.text}`, { class: "ripple-note " + item.change }));
    if (item.change === "removed") note.append(el("p", "Shown on the model, marked in red: the plan removes it.", { class: "muted" }));
    $("inspector").prepend(note);
    const seen = `ripple:${key}:${ripple.key}`; // checking, not making: once per diagram for each version of the plan
    if (key !== "states" && !plan.rewarded.has(seen)) {
      plan.rewarded.add(seen);
      earn(1, `Checked the ripple on the ${DIAGRAMS[key].toLowerCase()}`);
    }
  }

  function renderBadges() {
    for (const key of Object.keys(DIAGRAMS)) {
      const badge = $("tab-" + key).querySelector(".badge");
      if (!badge) continue;
      const items = ripple && !ripple.error ? ripple.diagrams[key] : [];
      badge.hidden = !items.length;
      badge.textContent = String(items.length);
      badge.className = "badge" + (items.some((i) => i.change === "problem") ? " bad" : items.some((i) => i.change === "warning") ? " warn" : "");
      badge.title = items.map((i) => `${MARK[i.change]} ${i.text}`).join("\n");
    }
  }

  function rippleCheck() {
    const name = "Diagrams agree";
    if (!plan || !plan.steps.length) return { name, ok: true, detail: "No change, so nothing ripples" };
    if (!plan.result || !plan.result.legal) return { name, ok: false, detail: "The plan is refused or empty: nothing to ripple" };
    if (!ripple || ripple.key !== rippleKey()) return { name, ok: false, detail: "Working out the ripple…" };
    if (ripple.error) return { name, ok: false, detail: `${ripple.error.code || "ERROR"}: ${ripple.error.message}` };
    const bad = ripple.problems.filter((p) => p.change === "problem").length, warn = ripple.problems.length - bad;
    return { name, ok: ripple.agree, detail: bad ? `${bad} diagram(s) out of step: see the plan's ripple` : warn ? `They agree; ${warn} warning(s) to look at` : "Every diagram agrees with the change" };
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
    if (!plan) {
      plan = { scope: "plan-draft", provider: "drawn by you", live: false, summary: "Your changes", meaning: null, request: "",
        model: "draft", steps: [], accepted: [], previewing: false, card: null, rewarded: new Set() };
      plan.card = say("draft", el("div"));
    }
    plan.steps.push({ n: plan.steps.length + 1, transaction, text: "", why: "", author: "you", checked: false, caught: false });
    plan.accepted.push(true);
    plan.card.replaceChildren(planCard());
    const result = await refreshPlan();
    if (result && result.legal && !plan.previewing) enterPreview();
    plan.card.scrollIntoView({ block: "nearest" });
  }

  // An imported UML file's edits (ADR-0190) become the plan, as the person's own steps like drawn edits: the server
  // re-checks each one and previews them through the policy, and nothing is saved from here.
  async function importPlan(transactions, summary) {
    retire();
    plan = { scope: "plan-draft", provider: "imported", live: false, summary, meaning: null, request: "", model: "draft",
      steps: transactions.map((transaction, i) => ({ n: i + 1, transaction, text: "", why: "", author: "you", checked: false, caught: false })),
      accepted: transactions.map(() => true), previewing: false, card: null, rewarded: new Set() };
    plan.card = say("draft", planCard());
    const result = await refreshPlan();
    if (result && result.legal && !plan.previewing) enterPreview();
    plan.card.scrollIntoView({ block: "nearest" });
    return result;
  }

  async function toggleStep(i, on) {
    const was = plan.result, step = plan.steps[i];
    plan.accepted[i] = on;
    const now = await refreshPlan();
    if (now && step.author === "ai" && !on && !step.caught && was && was.accepted && !was.legal && now.legal) {
      step.caught = true;
      earn(3, `Caught AI step ${i + 1}: without it the policy allows the plan`);
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

  function showStep(i) {
    const step = plan.steps[i];
    if (!plan.previewing && plan.result && plan.result.legal) enterPreview();
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

  function earn(n, why) {
    points += n;
    earned.unshift({ n, why });
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
      { name: "AI steps checked", ok: seen === ai.length, detail: ai.length ? `${seen} of ${ai.length} AI steps looked at on the diagram` : "No AI plan to check" },
      { name: "Screens pass the design check", ok: problemsFor === screensKey() && !problems.length,
        detail: problemsFor !== screensKey() ? "Checking the screens…" : problems.length ? `${problems.length} design problem(s): see Screens` : "Every screen can be built" },
      { name: "Conformance", ok: Boolean(built) && built.conformance.status === "PASS",
        detail: built ? `${built.conformance.status}: ${built.cases} cases checked against the kernel` : "Not built since the last change: press Build & run" },
      rippleCheck(),
      { name: "Simulated", ok: Boolean(simulated),
        detail: simulated ? `${simulated.attempts} attempts, ${simulated.refused} refused by the kernel` : "Not simulated since the last change: press Simulate" },
    ];
  }

  function renderHealth() {
    const checks = checksNow(), done = checks.filter((c) => c.ok).length, ring = $("health-ring"), ns = "http://www.w3.org/2000/svg";
    const r = 14, length = 2 * Math.PI * r, part = length / checks.length;
    ring.replaceChildren(...checks.map((c, i) => {
      const arc = document.createElementNS(ns, "circle");
      const attrs = { cx: 18, cy: 18, r, stroke: c.ok ? "#17734a" : "#dfe3ea", "stroke-dasharray": `${part - 2} ${length - part + 2}`,
        "stroke-dashoffset": String(-i * part), transform: "rotate(-90 18 18)" };
      for (const [k, v] of Object.entries(attrs)) arc.setAttribute(k, v);
      return arc;
    }));
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

  function newState(x, y, after) {
    const spec = formFor("state", after);
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
    const role = choose(packInfo.roles, t.role);
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
  }

  function startDrawing() {
    const box = $("canvas");
    for (const b of $("draw-palette").querySelectorAll("button")) {
      b.setAttribute("aria-pressed", "false");
      b.addEventListener("dragstart", (event) => { arm(null); event.dataTransfer.setData("text/x-eija-kind", b.dataset.kind); event.dataTransfer.effectAllowed = "copy"; });
      // A pointer click arms the tool; Enter or Space on the button opens the full form, so the keyboard needs no pointing.
      b.addEventListener("click", (event) => (event.detail > 0 ? arm(b.dataset.kind) : drawForm(b.dataset.kind, null)));
    }
    box.addEventListener("dragover", (event) => {
      if (!event.dataTransfer.types.includes("text/x-eija-kind")) return;
      event.preventDefault();
      event.dataTransfer.dropEffect = "copy";
      box.classList.add("drop-over");
    });
    box.addEventListener("dragleave", () => box.classList.remove("drop-over"));
    box.addEventListener("drop", (event) => {
      const kind = event.dataTransfer.getData("text/x-eija-kind");
      box.classList.remove("drop-over");
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
    const action = choose(packInfo.actions, packInfo.actions.find((a) => !used.has(a)) || packInfo.actions[0], (a) => a + (used.has(a) ? " (already used)" : ""));
    const role = choose(packInfo.roles, packInfo.roles[0]);
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
      ...others.map((r) => [`Let ${r} take it`, () => addStep({ kind: "set_role", transition: t.id, role: r })]),
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
    for (const c of components.components) (columns[GROUPS[c.stereotype] ? deepest[c.stereotype] : visit(c.id)] ||= []).push(c);
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
    return (id) => {
      if (id.startsWith("iface:")) { const [x, y, , h] = boxes[id.slice(6)]; return [x - 34, y + h / 2 - 8, 16, 16]; } // the ball, left of its provider
      return boxes[id] || [0, 0, 0, 0];
    };
  }

  async function drawComponents() {
    const box = $("component-canvas");
    if (!components) {
      try {
        components = await api("/api/play/components", { ...about(), screens: screensEdited ? screens : null });
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
    fit();
  }

  function restyleComponents() {
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
    problemsFor = screensKey();
    useCaseList = result.use_cases;
    renderHealth();
    return result;
  }

  function changed() {
    screensEdited = true;
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
        problemsFor = screensKey();
      }
      renderProblems();
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
  }

  function addField(name, at) {
    const screen = screenOf(useCase);
    if (!screen || screen.fields.some((f) => f.attribute === name)) return;
    const fields = [...screen.fields];
    fields.splice(at === undefined ? fields.length : at, 0, { attribute: name, label: "" });
    screen.fields = fields;
    changed();
  }

  function moveField(from, to) {
    const screen = screenOf(useCase), fields = [...screen.fields];
    const [moved] = fields.splice(from, 1);
    fields.splice(to > from ? to - 1 : to, 0, moved);
    screen.fields = fields;
    changed();
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
    const name = input(f.label, `Label for ${f.attribute}`, (v) => { f.label = v; changed(); });
    name.placeholder = f.attribute;
    const preview = el("span", a ? (a.type === "choice" ? `one of ${a.choices.join(", ")}` : a.type) + (a.required ? " · required" : "") : "not in the record", { class: "muted small" });
    const up = el("button", "↑", { type: "button", class: "quiet", "aria-label": `Move ${f.attribute} up` });
    up.disabled = i === 0;
    up.addEventListener("click", () => moveField(i, i - 1));
    const remove = el("button", "×", { type: "button", class: "quiet", "aria-label": `Remove ${f.attribute}` });
    remove.addEventListener("click", () => { screen.fields = screen.fields.filter((_, j) => j !== i); changed(); });
    li.append(grip, el("code", f.attribute), name, preview, up, remove);
    return li;
  }

  function dropZone(list) {
    list.addEventListener("dragover", (event) => { event.preventDefault(); list.classList.add("over"); });
    list.addEventListener("dragleave", () => list.classList.remove("over"));
    list.addEventListener("drop", (event) => {
      event.preventDefault();
      list.classList.remove("over");
      const rows = [...list.querySelectorAll(".screen-field")];
      const target = rows.findIndex((r) => event.clientY < r.getBoundingClientRect().top + r.offsetHeight / 2);
      const at = target === -1 ? rows.length : target;
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
        changed();
      });
      card.append(el("p", `${useCase} has no screen yet.`, { class: "muted" }), add);
      return;
    }
    const t = model.transitions.find((x) => x.action === useCase);
    if (useCase !== null && !t) {
      const remove = el("button", "Remove this screen", { type: "button" });
      remove.addEventListener("click", () => { screens.screens = screens.screens.filter((x) => x !== screen); useCase = null; changed(); });
      card.append(el("p", `The model has no use case ${useCase}, so this screen cannot be built.`, { class: "muted" }), remove);
      return;
    }
    card.append(el("p", useCase === null ? "Starts a record · any actor" : `${t.from_state} → ${t.to_state} · ${t.role}`, { class: "muted small" }));
    card.append(input(screen.title, "Screen title", (v) => { screen.title = v || screen.title; changed(); }));
    card.lastChild.classList.add("screen-title");
    const list = el("ul", undefined, { class: "screen-fields", "aria-label": "Fields on this screen" });
    screen.fields.forEach((f, i) => list.append(fieldRow(screen, f, i)));
    if (!screen.fields.length) list.append(el("li", "Drop record attributes here.", { class: "muted drop-hint" }));
    dropZone(list);
    const button = input(screen.button, "Button label", (v) => { screen.button = v; changed(); });
    button.placeholder = useCase === null ? "Create" : useCase;
    button.classList.add("screen-button");
    card.append(list, button);
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
    renderCard();
    renderPalette();
    const link = $("screens-download");
    if (link.href.startsWith("blob:")) URL.revokeObjectURL(link.href);
    link.href = URL.createObjectURL(new Blob([JSON.stringify(screens, null, 2) + "\n"], { type: "application/json" }));
  }

  async function build() {
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
      if (result.url) {
        $("run").hidden = false;
        $("run-frame").src = result.url;
        $("run-open").href = result.url;
      }
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
    const parts = [entry.actor, entry.outcome === "CREATED" ? `created ${entry.record}` : `${entry.action} on ${entry.record}`];
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
      });
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
    data = (await api("/api/play/data")).data;
    await loadScreens(null);
    outline();
    draw(model);
    inspect("");
    const t = model.transitions[model.transitions.length - 1];
    // The example has to pass as it stands. On the model in force that is the pack's own demo request, a change the pack
    // models. On a change case's candidate, typed steps: an action names one transition, so the second step takes a
    // declared action no transition uses yet, and it leaves a state that already has a way out (a pack's laws may keep
    // its end states closed).
    const free = t && packInfo.actions.find((a) => !model.transitions.some((u) => u.action === a));
    if (!caseId && packInfo.demo_request) $("chat-example").textContent = packInfo.demo_request.replace(/[.\s]+$/, "");
    else if (t) $("chat-example").textContent = `add state Archived after ${t.from_state}` + (free ? ` then add ${free} from ${t.from_state} to Archived for ${t.role}` : "");
    $("build").addEventListener("click", build);
    $("simulate").addEventListener("click", simulate);
    $("sim-replay").addEventListener("click", replay);
    $("sim-clear").addEventListener("click", clearSim);
    $("fit").addEventListener("click", fit);
    $("zoom-in").addEventListener("click", () => current() && current().zoomIn());
    $("zoom-out").addEventListener("click", () => current() && current().zoomOut());
    $("tab-states").addEventListener("click", () => showTab("states"));
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
    $("screens-reset").addEventListener("click", async () => { screensEdited = false; lastBuild = null; restyleComponents(); components = null; await loadScreens(null); renderDesigner(); if (plan) refreshRipple(); });
    $("canvas-help").textContent = HINTS.states;
    window.addEventListener("resize", fit);
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
    api, el, hooks, about, viewKey, label, restyle, clearSim, select, showTab, fit, importPlan,
    graph: () => graph, tab: () => tab, model: () => model, selected: () => selected, pack: () => packInfo, base: () => baseModel,
    planned: () => (plan && plan.result && plan.result.legal ? accepted() : null), // the change the Changes view draws (ADR-0176)
    setChanges, diagram: (key) => ({ states: graph, classes: classGraph, usecases: useCaseGraph, components: componentGraph })[key],
  };

  start().catch((error) => {
    $("inspector").replaceChildren(el("p", `Could not load the model (${error.code || "ERROR"}): ${error.message}. If the session expired, open PlayIDE from the private launch link.`, { class: "muted" }));
  });
})();
