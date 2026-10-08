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
  let screens = null, screensEdited = false, useCase = null, checkTimer = 0, problems = [], useCaseList = [];
  const base = {}; // each cell's own style and label, so overlays can be cleared

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

  function layout(workflow) {
    const g = new dagre.graphlib.Graph({ multigraph: true });
    g.setGraph({ rankdir: "LR", nodesep: 60, ranksep: 120, edgesep: 30, marginx: 30, marginy: 30 });
    g.setDefaultEdgeLabel(() => ({}));
    g.setNode("__initial", { width: INITIAL, height: INITIAL });
    for (const s of workflow.states) g.setNode(s, { ...STATE });
    g.setEdge("__initial", workflow.initial_state);
    for (const t of workflow.transitions) g.setEdge(t.from_state, t.to_state, { width: 120, height: 20 }, t.id);
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
    fit();
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

  const current = () => ({ states: graph, classes: classGraph, usecases: useCaseGraph, components: componentGraph })[tab];
  const PANELS = { states: "canvas", classes: "class-canvas", usecases: "usecase-canvas", screens: "screens", components: "component-canvas" };
  const HINTS = {
    states: "Drag states to arrange them. Select an element to inspect it. Arrangement is not saved yet.",
    classes: "Select a class to see its attributes and associations.",
    usecases: "Select a use case to inspect it. Double-click one to design its screen.",
    screens: "Design each use case's screen. The design check runs as you edit; Build & run uses these screens.",
    components: "The built app's components, read from its generated files: every line is an import, a route or a file read.",
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
    } else {
      const t = transition(id.slice(11));
      box.append(el("h3", `${t.action} (${t.id})`));
      row(dl, "From → to", `${t.from_state} → ${t.to_state}`);
      row(dl, "Who", t.role);
      row(dl, "Guards", t.guards.join(", "));
      row(dl, "Effects", t.required_effects.join(", ") || "none");
      row(dl, "Never", t.forbidden_effects.join(", ") || "nothing listed");
      box.append(dl, screenLink(t.action));
      return;
    }
    box.append(dl);
  }

  function select(id, fromOutline) {
    selected = id;
    for (const b of document.querySelectorAll(".outline button")) b.setAttribute("aria-current", String(b.dataset.id === id));
    inspect(id);
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
    $("outline-roles").replaceChildren(...[...new Set(model.transitions.map((t) => t.role))].map((r) => el("li", r, { class: "muted" })));
  }

  // Class diagram (ADR-0153): the pack's data model in UML class notation. The record class is what moves through
  // the state machine; its attributes become the built app's form, checked by the data model on the server.
  const typeName = { text: "String", number: "Number", date: "Date", boolean: "Boolean" };
  // UML attribute notation: name: Type [multiplicity]; an optional value is [0..1], a choice lists its literals.
  const attributeLine = (a) => `${a.name}: ${a.type === "choice" ? `{${a.choices.join(", ")}}` : typeName[a.type]}${a.required ? "" : " [0..1]"}`;
  const ROW = 20, HEAD = 34;
  const widthOf = (e) => Math.max(200, e.name.length * 9 + 60, ...e.attributes.map((a) => attributeLine(a).length * 7 + 24));

  function classLayout() {
    const g = new dagre.graphlib.Graph({ multigraph: true });
    g.setGraph({ rankdir: "LR", nodesep: 50, ranksep: 140, marginx: 30, marginy: 30 });
    g.setDefaultEdgeLabel(() => ({}));
    for (const e of data.entities) g.setNode(e.name, { width: widthOf(e), height: HEAD + ROW * Math.max(1, e.attributes.length) + 8 });
    data.associations.forEach((a, i) => g.setEdge(a.source, a.target, { width: 90, height: 20 }, "a" + i));
    dagre.layout(g);
    return (name) => { const n = g.node(name); return [n.x - n.width / 2, n.y - n.height / 2, n.width, n.height]; };
  }

  function drawClasses() {
    if (classGraph || !data) return;
    const { Graph, InternalEvent, Point } = maxgraph;
    const box = $("class-canvas");
    InternalEvent.disableContextMenu(box);
    classGraph = new Graph(box);
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
      select(id && id.startsWith("class:") ? id : "", false);
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

  function drawUseCases() {
    if (useCaseGraph) return;
    const { Graph, InternalEvent } = maxgraph;
    const box = $("usecase-canvas");
    InternalEvent.disableContextMenu(box);
    useCaseGraph = new Graph(box);
    for (const setting of ["setConnectable", "setCellsEditable", "setCellsDisconnectable", "setCellsResizable", "setDropEnabled"]) useCaseGraph[setting](false);
    useCaseGraph.setPanning(true);
    const parent = useCaseGraph.getDefaultParent(), flow = workflowOrder();
    const roles = [...new Set(flow.map((t) => t.role))];
    // Group each role's use cases together, in workflow order, and put the actor beside its group: no line crosses a use case.
    const cases = roles.flatMap((role) => flow.filter((t) => t.role === role));
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
        cells[t.id] = useCaseGraph.insertVertex({ parent, id: "uc:" + t.id, value: t.action, position: [boundary.x + 60, rowY(i)],
          size: [boundary.w - 120, 48], style: { ...font, shape: "ellipse", fillColor: "#eef2ff", strokeColor: "#5b74d6", fontSize: 13 } });
      });
      roles.forEach((role, i) => {
        const mine = cases.map((t, j) => [t, j]).filter(([t]) => t.role === role);
        const y = mine.reduce((sum, [, j]) => sum + rowY(j), 0) / mine.length - 8;
        const left = i % 2 === 0;
        const actor = useCaseGraph.insertVertex({ parent, id: "role:" + role, value: role, position: [left ? 90 : boundary.x + boundary.w + 120, y],
          size: [36, 64], style: { ...font, shape: "actor", fillColor: "#ffffff", strokeColor: "#1b2130", verticalLabelPosition: "bottom",
            verticalAlign: "top", fontSize: 13 } });
        for (const [t] of mine) {
          useCaseGraph.insertEdge({ parent, source: actor, target: cells[t.id], style: { strokeColor: "#4a5568", endArrow: "none" } });
        }
      });
    });
    useCaseGraph.getSelectionModel().addListener(InternalEvent.CHANGE, () => {
      const cell = useCaseGraph.getSelectionCell(), id = cell && cell.id && cell.id.startsWith("uc:") ? cell.id.slice(3) : "";
      select(id === "create" ? "usecase:create" : id ? "transition:" + id : "", false);
    });
    useCaseGraph.addListener(InternalEvent.DOUBLE_CLICK, (_sender, event) => {
      const cell = event.getProperty("cell");
      if (!cell || !cell.id.startsWith("uc:")) return;
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
    for (const id of ["fit", "zoom-in", "zoom-out"]) $(id).hidden = which === "screens";
    if (which === "screens") { renderDesigner(); return; }
    if (which === "usecases") drawUseCases();
    if (which === "components") { drawComponents(); return; }
    if (which === "classes") {
      if (!data) { $("class-canvas").replaceChildren(el("p", "This pack has no data model yet. Add a data.json beside its pack.json.", { class: "muted empty" })); return; }
      drawClasses();
    }
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
      leavePreview();
      plan = { ...result, accepted: result.steps.map(() => true), previewing: false, card: null };
      plan.card = say("ai", planCard());
      renderPlan(result.preview);
    } catch (error) {
      say("ai", el("p", `${error.code || "ERROR"}: ${error.message}`, { class: "refusal" }));
    } finally {
      button.disabled = false;
    }
  }

  function planCard() {
    const box = el("div", undefined, { class: "plan" });
    box.append(el("p", plan.summary || "A plan", { class: "plan-summary" }),
      el("p", `${plan.provider}${plan.live ? "" : " · offline fixture, not a live model"} · untrusted until you check it`, { class: "muted small" }));
    const list = el("ol", undefined, { class: "plan-steps" });
    plan.steps.forEach((step, i) => {
      const li = el("li"), id = `plan-${plan.model.slice(0, 6)}-${i}`, check = el("input", undefined, { type: "checkbox", id });
      check.checked = plan.accepted[i];
      check.addEventListener("change", () => { plan.accepted[i] = check.checked; refreshPlan(); });
      const text = el("label", step.text, { for: id });
      li.append(check, text, el("span", "", { class: "step-status" }));
      if (step.why) li.append(el("p", step.why, { class: "muted small why" }));
      list.append(li);
    });
    const verdict = el("p", "", { class: "plan-verdict", role: "status" });
    const tools = el("div", undefined, { class: "plan-tools" });
    const preview = el("button", "Preview on the diagram", { type: "button", class: "primary" });
    preview.addEventListener("click", () => (plan.previewing ? leavePreview() : enterPreview()));
    tools.append(preview);
    if (plan.meaning) {
      const keep = el("button", "Make it a change case", { type: "button" });
      keep.addEventListener("click", makeCase);
      tools.append(keep);
    }
    box.append(list, verdict, tools);
    return box;
  }

  async function refreshPlan() {
    try {
      const result = await api("/api/play/plan/preview", { case_id: caseId, model: baseModel, steps: plan.steps.map((s) => s.transaction), accepted: plan.accepted });
      renderPlan(result);
      if (plan.previewing) (result.legal ? enterPreview : leavePreview)();
    } catch (error) {
      plan.card.querySelector(".plan-verdict").textContent = `${error.code || "ERROR"}: ${error.message}`;
    }
  }

  function renderPlan(result) {
    plan.result = result;
    const marks = { applies: "✓", rejected: "–", does_not_apply: "✗" };
    plan.card.querySelectorAll(".plan-steps > li").forEach((li, i) => {
      const s = result.steps[i];
      li.className = s.status;
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
    for (const g of [graph, useCaseGraph, componentGraph]) if (g) g.destroy();
    $("canvas").replaceChildren();
    $("usecase-canvas").replaceChildren();
    $("component-canvas").replaceChildren();
    useCaseGraph = componentGraph = components = null;
    for (const key of Object.keys(base)) delete base[key];
    clearSimPanel();
    outline();
    draw(model);
    inspect("");
    loadScreens(null).then(() => { screensEdited = false; if (tab === "screens") renderDesigner(); });
    if (tab !== "states") showTab(tab);
  }

  function enterPreview() {
    if (!plan || !plan.result || !plan.result.legal) return;
    plan.previewing = true;
    redrawAll(plan.result.candidate);
    highlight(plan.result.diff);
    $("plan-banner").hidden = false;
    $("plan-banner-text").textContent = `Previewing the plan: ${changes(plan.result.diff)}. Nothing is saved.`;
    plan.card.querySelector(".plan-tools .primary").textContent = "Back to the model";
  }

  function leavePreview() {
    if (!plan || !plan.previewing) return;
    plan.previewing = false;
    redrawAll(baseModel);
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
    const result = await api("/api/play/screens", { ...about(), screens: edited || null });
    if (!edited) screens = result.screens;
    problems = result.problems;
    useCaseList = result.use_cases;
    return result;
  }

  function changed() {
    screensEdited = true;
    lastBuild = null; // the last build was of other screens
    restyleComponents();
    components = null;
    renderDesigner();
    clearTimeout(checkTimer);
    checkTimer = setTimeout(async () => {
      try {
        problems = (await loadScreens(screens)).problems;
      } catch (error) {
        problems = [{ code: error.code || "ERROR", use_case: useCase, text: error.message }];
      }
      renderProblems();
      renderScreenList();
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
      const result = await api("/api/play/build", { ...about(), screens: screensEdited ? screens : null });
      const pass = result.conformance.status === "PASS";
      lastBuild = result;
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
      rows[i].scrollIntoView({ block: "nearest" });
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
      showSim(await api("/api/play/simulate", { ...about(), seed: 1, steps: 500 }));
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
    data = (await api("/api/play/data")).data;
    await loadScreens(null);
    outline();
    draw(model);
    inspect("");
    const t = model.transitions[model.transitions.length - 1];
    if (t) $("chat-example").textContent = `add state Archived after ${t.to_state} then add ${t.action} from ${t.to_state} to Archived for ${t.role}`;
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
    $("chat-form").addEventListener("submit", ask);
    $("plan-back").addEventListener("click", leavePreview);
    $("screens-reset").addEventListener("click", async () => { screensEdited = false; lastBuild = null; restyleComponents(); components = null; await loadScreens(null); renderDesigner(); });
    $("canvas-help").textContent = HINTS.states;
    window.addEventListener("resize", fit);
    document.body.dataset.ready = "true";
  }

  start().catch((error) => {
    $("inspector").replaceChildren(el("p", `Could not load the model (${error.code || "ERROR"}): ${error.message}. If the session expired, open PlayIDE from the private launch link.`, { class: "muted" }));
  });
})();
