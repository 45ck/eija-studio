// PlayIDE roles (ADR-0215): the human side of the model as one view. Each role is an actor: choosing one (on the use
// case diagram, in the outline or on the Permissions tab) says what it may do, which screens it sees and which fixture
// actors play it, and runs the built app as one of them. On the Screens tab, "See the app as" dims the screens a role
// never sees. What a role may do is the kernel's answer (`/api/play/access`, ADR-0171), never a reading of the page;
// starting a record is open to any active actor, because the model does not say who may.
"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  let P = null, lens = "", access = null, accessKey = "", loading = null, lastList = null, lastCard = null;

  // ---- The kernel's answer, per role --------------------------------------------------------------------------------
  async function permissions() {
    const key = P.viewKey();
    if (access && accessKey === key) return access;
    if (!loading || loading.key !== key) {
      const promise = P.api("/api/play/access", P.about()).then((result) => {
        if (P.viewKey() === key) { access = result; accessKey = key; }
        return result;
      });
      loading = { key, promise };
    }
    return loading.promise;
  }

  const current = () => (access && accessKey === P.viewKey() ? access : null);

  // A role's use cases: each action the kernel lets some fixture actor of that role take, with the states it leaves
  // from and which of the role's actors were let through. Use cases the role holds in the model but no actor could
  // take still count: the role holds them, and its actors' refusals say why.
  function useCasesOf(result, role) {
    const byAction = new Map();
    for (const state of result.states) {
      for (const c of (result.cells[state] || {})[role] || []) {
        const u = byAction.get(c.action) || { action: c.action, steps: [], assignedOnly: false, actors: new Map() };
        u.steps.push({ from: state, to: c.to, transition: c.transition });
        u.assignedOnly = u.assignedOnly || c.assigned_only;
        for (const a of c.actors) if (!u.actors.has(a.actor) || !a.refused) u.actors.set(a.actor, a.refused || "");
        byAction.set(c.action, u);
      }
    }
    return [...byAction.values()];
  }

  function roleOfAction(action) {
    const t = P.model().transitions.find((x) => x.action === action);
    return t ? t.role : "";
  }

  const actorsOf = (role) => ((P.pack() && P.pack().actors) || []).filter((a) => a.role === role);
  const titleOf = (action) => {
    const s = P.screens() && P.screens().screens.find((x) => x.use_case === action);
    return s ? s.title : action === null ? "Create" : action;
  };
  const article = (word) => (/^[AEIOU]/i.test(word) ? "An " : "A ") + word;
  const a = (word) => (/^[AEIOU]/i.test(word) ? "an " : "a ") + word;
  // An AI agent, a timer or an external system holds a role too (ADR-0210), but it has no screens: it calls the built
  // app's API, and the kernel decides each call exactly as it decides a click.
  const KIND_WORDS = { agent: "AI agent", timer: "timer", system: "external system" };
  const kindOf = (role) => (P.roleKind ? P.roleKind(role) : "human");
  const machine = (role) => kindOf(role) !== "human";
  const who = (role) => (machine(role) ? `${a(KIND_WORDS[kindOf(role)])} (${role})` : a(role));
  const Who = (role) => who(role).replace(/^a/, "A");

  // The calls a role without screens makes, written as the built app's own endpoints (resources/appgen/server.py.tmpl).
  function apiCalls(role, actions) {
    const actor = (actorsOf(role).find((x) => x.active) || actorsOf(role)[0] || { id: "<actor>" }).id;
    const list = P.el("ul", undefined, { class: "role-calls", "aria-label": `API calls ${role} makes` });
    for (const action of actions) {
      const li = P.el("li");
      li.append(P.el("code", "POST /api/records/{id}/act"), " ",
        P.el("code", JSON.stringify({ action, actor, expected_version: "n" }).replace('"n"', "n"), { class: "body" }));
      list.append(li);
    }
    if (!actions.length) list.append(P.el("li", `${role} takes no step of the workflow.`, { class: "muted" }));
    const start = P.el("li", undefined, { class: "muted" }); // any active actor may start a record (issue #142)
    start.append(P.el("code", "POST /api/records"), " ", P.el("code", JSON.stringify({ title: "…", actor, fields: {} }), { class: "body" }));
    list.append(start);
    return list;
  }

  // ---- Run the app as one actor -------------------------------------------------------------------------------------
  function runButton(actor, primary) {
    const stand = machine(actor.role);
    const label = `▶ ${stand ? "Stand in for" : "Run as"} ${actor.id}` + (actor.active ? "" : " (inactive)");
    const b = P.el("button", label, { type: "button", class: primary ? "primary run-as" : "quiet run-as", "data-actor": actor.id,
      title: !actor.active ? `${actor.id} is inactive: the kernel refuses every step it tries`
        : stand ? `Open the built app acting as ${actor.id}: each press is the API call it would make` : `Build and run the app acting as ${actor.id}` });
    b.addEventListener("click", () => P.runAs(actor.id));
    return b;
  }

  function runTools(role) {
    const box = P.el("div", undefined, { class: "run-as-tools" });
    const actors = actorsOf(role);
    if (!actors.length) {
      box.append(P.el("span", `No fixture actor has the role ${role}, so the built app cannot act as one.`, { class: "muted small" }));
      return box;
    }
    const first = actors.find((a) => a.active) || actors[0];
    box.append(runButton(first, true), ...actors.filter((a) => a !== first).map((a) => runButton(a, false)));
    return box;
  }

  // Who holds the role, as a choice: changing it adds a step to the plan, which the server checks against the laws about
  // kinds of actor (only a person approves, ...), like any drawn edit. Nothing is saved (ADR-0210, #156).
  function kindPicker(role, kind) {
    const label = P.el("label", "Held by ", { class: "role-kind" }), select = P.el("select", undefined, { "aria-label": `Who holds ${role}` });
    for (const [k, words] of Object.entries(P.kinds)) {
      const option = P.el("option", words + (k === kind && k !== P.inForce(role) ? " (in the plan)" : ""), { value: k });
      option.selected = k === kind;
      select.append(option);
    }
    select.addEventListener("change", () => P.setKind(role, select.value));
    label.append(select);
    return label;
  }

  // ---- The inspector for an actor -----------------------------------------------------------------------------------
  async function inspectRole(id, box) {
    if (!id.startsWith("role:")) return;
    const role = id.slice(5), notes = (P.pack() && P.pack().role_notes) || {};
    const kind = P.roleKind ? P.roleKind(role) : "human"; // a person, an AI agent, a timer or an external system (ADR-0210)
    if (kind !== "human" && P.kinds) box.append(P.el("p", `«${P.kinds[kind]}»`, { class: "role-kind" }));
    if (P.setKind && P.kinds && !P.reviewing()) box.append(kindPicker(role, kind));
    if (notes[role]) box.append(P.el("p", notes[role], { class: "muted" }));
    const body = P.el("div", undefined, { class: "role-inspect", "aria-live": "polite" });
    body.append(P.el("p", "Asking the kernel…", { class: "muted small" }));
    box.append(body);
    let result;
    try { result = await permissions(); } catch (error) {
      body.replaceChildren(P.el("p", `${error.code || "ERROR"}: ${error.message}`, { class: "refusal" }));
      return;
    }
    if (P.selected() !== id) return; // another selection replaced this one while the kernel answered
    const cases = useCasesOf(result, role);
    const list = P.el("ul", undefined, { class: "role-cases", "aria-label": `Use cases of ${role}` });
    for (const u of cases) {
      const li = P.el("li");
      const b = P.el("button", u.action, { type: "button", class: "quiet", title: "Show it on the state machine" });
      b.addEventListener("click", () => P.select("transition:" + u.steps[0].transition, true));
      li.append(b, P.el("span", ` ${u.steps.map((s) => `${s.from} → ${s.to}`).join(", ")}${u.assignedOnly ? " · assigned only" : ""}`, { class: "muted small" }));
      list.append(li);
    }
    if (!cases.length) list.append(P.el("li", `${role} may take no step of the workflow: only start a record.`, { class: "muted" }));
    const actors = P.el("ul", undefined, { class: "role-actors", "aria-label": `Fixture actors with the role ${role}` });
    for (const a of actorsOf(role)) {
      const flags = [a.active ? "active" : "inactive", a.assigned ? "assigned" : ""].filter(Boolean).join(", ");
      actors.append(P.el("li", `${a.id} (${flags})`, { class: a.active ? "" : "no" }));
    }
    const tools = P.el("div", undefined, { class: "inspector-tools" });
    const see = P.el("button", "See their screens", { type: "button" });
    see.addEventListener("click", () => { lens = role; P.showTab("screens"); renderLens(); });
    const who = P.el("button", "Who can do what", { type: "button", class: "quiet" });
    who.addEventListener("click", () => P.showTab("access"));
    tools.append(see, who);
    const parts = [P.el("h4", "May"), list, P.el("p", "Any active actor may start a record.", { class: "muted small" })];
    if (machine(role)) {
      parts.push(P.el("h4", "No screens: it calls"), apiCalls(role, cases.map((u) => u.action)));
      see.textContent = "See what it calls";
    }
    body.replaceChildren(...parts, P.el("h4", "Played by"), actors, tools, runTools(role));
  }

  // ---- "See the app as" on the Screens tab --------------------------------------------------------------------------
  function theirs(result, role) {
    return new Set(useCasesOf(result, role).map((u) => u.action));
  }

  function renderLens() {
    const bar = $("role-lens"), strip = $("role-app");
    if (!bar || !P.screens()) return;
    const result = current();
    if (!result) { permissions().then(renderLens, () => {}); return; }
    if (lens && !result.roles.includes(lens)) lens = "";
    bar.replaceChildren(P.el("span", "See the app as", { class: "lens-label" }));
    for (const role of ["", ...result.roles]) {
      const b = P.el("button", role || "Everyone", { type: "button", class: "lens-role" + (role && machine(role) ? " machine" : ""), "aria-pressed": String(role === lens), "data-role": role,
        title: role && machine(role) ? `${Who(role)}: no screens, only API calls` : "" });
      b.addEventListener("click", () => { lens = role; renderLens(); });
      bar.append(b);
    }
    const toggle = P.el("button", "Screen flow", { type: "button", id: "screen-flow-toggle", class: "flow-toggle", "aria-pressed": String(flowOpen),
      "aria-controls": "screen-flow", title: "Every screen as a wireframe, in the order a record meets them" });
    toggle.addEventListener("click", () => { flowOpen = !flowOpen; renderFlow(); });
    bar.append(toggle);
    strip.replaceChildren();
    strip.hidden = !lens;
    if (lens && machine(lens)) {
      const actions = useCasesOf(result, lens).map((u) => u.action);
      const head = P.el("p", undefined, { class: "role-app-head" });
      head.append(P.el("strong", `${Who(lens)} has no screens.`),
        " It calls the built app's API, and the kernel decides each call exactly as it decides a click. Standing in for it opens the app as it, so each press is one of these calls.");
      strip.append(head, apiCalls(lens, actions), runTools(lens));
    } else if (lens) {
      const mine = theirs(result, lens), cases = [null, ...useCasesOf(result, lens).map((u) => u.action)];
      const all = [null, ...new Set(P.model().transitions.map((t) => t.action))];
      const never = all.filter((a) => a !== null && !mine.has(a));
      const head = P.el("p", undefined, { class: "role-app-head" });
      head.append(P.el("strong", `${article(lens)} sees ${cases.length} of ${all.length} screens.`),
        " Starting a record is open to any active actor; the rest are what the kernel lets the role do.");
      const flow = P.el("ol", undefined, { class: "role-flow", "aria-label": `Screens ${lens} sees` });
      for (const action of cases) {
        const b = P.el("button", titleOf(action), { type: "button", title: action === null ? "Starts a record" : action });
        b.addEventListener("click", () => P.openScreen(action));
        const li = P.el("li");
        li.append(b);
        flow.append(li);
      }
      strip.append(head, flow);
      if (never.length) strip.append(P.el("p", `Never sees: ${never.map((a) => `${titleOf(a)} (${roleOfAction(a)})`).join(", ")}.`, { class: "muted small role-never" }));
      strip.append(runTools(lens));
    }
    decorate();
    renderFlow();
  }

  // Dim the screens the chosen role never sees, and say on the card who sees the one open.
  function decorate(event) {
    if (event && event.list) lastList = event;
    const result = current(), mine = result && lens ? (machine(lens) ? new Set() : theirs(result, lens)) : null;
    const calls = result && lens && machine(lens) ? theirs(result, lens) : new Set();
    if (lastList && lastList.list.isConnected) {
      [...lastList.list.children].forEach((li, i) => {
        const name = lastList.names[i], hide = mine !== null && (machine(lens) || (name !== null && !mine.has(name)));
        li.classList.toggle("not-theirs", hide);
        const b = li.querySelector("button");
        if (b) b.title = !hide ? "" : machine(lens) ? `${Who(lens)} has no screens` : `${article(lens)} never sees this screen`;
      });
    }
    const card = $("screen-card");
    const old = card && card.querySelector(".role-note");
    if (old) old.remove();
    if (!card || !mine || !card.querySelector(".screen-title")) return;
    const open = event && "useCase" in event ? event.useCase : (lastCard || {}).useCase;
    let text;
    if (machine(lens)) text = calls.has(open) ? `${Who(lens)} takes ${open} by an API call, not on a screen. This is the screen a person standing in for it sees.` : `${Who(lens)} has no screens.`;
    else if (open === null) text = `${article(lens)} sees this screen: any active actor may start a record.`;
    else if (mine.has(open)) text = `${article(lens)} sees this screen.`;
    else text = `${article(lens)} never sees this screen: only ${roleOfAction(open) ? a(roleOfAction(open)) : "another role"} may take ${open}.`;
    card.prepend(P.el("p", text, { class: "role-note " + (!machine(lens) && (open === null || mine.has(open)) ? "ok" : "warn") }));
  }

  // ---- The screen flow ----------------------------------------------------------------------------------------------
  // The app's screens as a storyboard: each screen a wireframe drawn from its fields and the record class's attributes
  // (control, required mark, limits), and an arrow from a screen to the screens the record can reach next, labelled with
  // the state it is then in. It is read from the state machine and the screens, never drawn by hand: a transition you
  // add on the state machine adds an arrow here. Under "See the app as", the chosen role's screens stand out.
  let flowOpen = false, flowTimer = 0, flowFit = null; // null: fit when the screens stay readable, else full size
  const SVG = "http://www.w3.org/2000/svg";
  const CARD_W = 180, MAX_ROWS = 6;

  function flowShape() {
    const model = P.model(), byAction = new Map();
    for (const t of model.transitions) {
      const n = byAction.get(t.action) || { id: "uc:" + t.action, action: t.action, role: t.role, steps: [] };
      n.steps.push(t);
      byAction.set(t.action, n);
    }
    const screens = [{ id: "uc:create", action: null, role: "", steps: [{ to_state: model.initial_state }] }, ...byAction.values()];
    const leaving = new Set(model.transitions.map((t) => t.from_state)), edges = [], ends = new Set(), seen = new Set();
    for (const from of screens) {
      for (const step of from.steps) {
        const state = step.to_state, next = screens.filter((n) => n.action !== null && n.steps.some((t) => t.from_state === state));
        if (!leaving.has(state)) { ends.add(state); next.push({ id: "end:" + state }); }
        for (const to of next) {
          const key = `${from.id}|${to.id}|${state}`;
          if (!seen.has(key)) { seen.add(key); edges.push({ from: from.id, to: to.id, state }); }
        }
      }
    }
    return { screens, ends: [...ends], edges };
  }

  function attributeOf(name) {
    const data = P.data(), record = data && data.entities.find((e) => e.name === data.record);
    return record ? record.attributes.find((x) => x.name === name) : null;
  }

  // What the built app's control will be for a field, and the rule the server checks (ADR-0153).
  function control(attr) {
    if (!attr) return ["missing", "not in the record"];
    const rule = attr.type === "choice" ? `one of ${attr.choices.join(", ")}` : attr.type === "text" ? `text, up to ${attr.max_length}` : attr.type;
    const hint = { text: "", number: "0", date: "dd/mm/yyyy", boolean: "☐", choice: `${attr.choices[0]} ▾` }[attr.type];
    return [hint, rule + (attr.required ? ", required" : ", optional")];
  }

  function card(n, screen, fade) {
    const box = P.el("button", undefined, { type: "button", class: "flow-card" + (fade ? " faded" : ""), "data-use-case": n.action === null ? "" : n.action,
      title: n.action === null ? "Starts a record: open its screen" : `${n.action}: open its screen` });
    const head = P.el("span", undefined, { class: "flow-head" });
    head.append(P.el("span", screen ? screen.title : n.action || "Create", { class: "flow-title" }),
      P.el("span", n.action === null ? "any active actor" : n.role + (machine(n.role) ? ` «${kindOf(n.role)}»` : ""), { class: "flow-role" }));
    box.append(head);
    const fields = screen ? screen.fields : [];
    for (const f of fields.slice(0, MAX_ROWS)) {
      const attr = attributeOf(f.attribute), [hint, rule] = control(attr);
      const row = P.el("span", undefined, { class: "flow-field", title: rule });
      row.append(P.el("span", (f.label || f.attribute) + (attr && attr.required && n.action === null ? " *" : ""), { class: "flow-label" }),
        P.el("span", n.action === null ? hint : "value", { class: "flow-ctl " + (n.action === null ? "input " + (attr ? attr.type : "missing") : "shown") }));
      box.append(row);
    }
    if (fields.length > MAX_ROWS) box.append(P.el("span", `+ ${fields.length - MAX_ROWS} more`, { class: "flow-more" }));
    if (!fields.length) box.append(P.el("span", "No fields", { class: "flow-more" }));
    box.append(P.el("span", (screen && screen.button) || (n.action === null ? "Create" : n.action), { class: "flow-button" }));
    box.addEventListener("click", () => P.openScreen(n.action));
    return box;
  }

  function renderFlow() {
    const panel = $("screen-flow"), toggle = $("screen-flow-toggle");
    if (toggle) toggle.setAttribute("aria-pressed", String(flowOpen));
    if (!panel) return;
    panel.hidden = !flowOpen;
    if (!flowOpen || !P.screens() || !window.dagre) return;
    const { screens, ends, edges } = flowShape(), designed = P.screens();
    const result = current(), mine = result && lens && !machine(lens) ? theirs(result, lens) : null;
    const g = new dagre.graphlib.Graph({ multigraph: true });
    g.setGraph({ rankdir: "LR", nodesep: 18, ranksep: 56, marginx: 12, marginy: 12 });
    g.setDefaultEdgeLabel(() => ({}));
    // Each card is drawn first and measured, so a long title that wraps still gets the room it takes.
    const canvas = P.el("div", undefined, { class: "flow-canvas" }), nodes = new Map();
    const view = P.el("div", undefined, { class: "flow-view" }), sizer = P.el("div", undefined, { class: "flow-sizer" });
    sizer.append(canvas);
    view.append(sizer);
    const frame = P.el("div", undefined, { class: "flow-frame" });
    frame.append(view);
    panel.replaceChildren(frame);
    for (const n of screens) {
      const screen = designed.screens.find((s) => s.use_case === n.action);
      const node = card(n, screen, (mine !== null && n.action !== null && !mine.has(n.action)) || Boolean(lens && machine(lens)));
      node.style.width = `${CARD_W}px`;
      canvas.append(node);
      nodes.set(n.id, node);
    }
    for (const state of ends) {
      const node = P.el("span", `Ends in ${state}`, { class: "flow-end" });
      canvas.append(node);
      nodes.set("end:" + state, node);
    }
    for (const [id, node] of nodes) g.setNode(id, { width: Math.max(id.startsWith("end:") ? 120 : CARD_W, node.offsetWidth), height: node.offsetHeight });
    edges.forEach((e, i) => g.setEdge(e.from, e.to, { label: e.state, width: 60, height: 16 }, "e" + i));
    dagre.layout(g);
    const size = g.graph();
    canvas.style.width = `${Math.ceil(size.width)}px`;
    canvas.style.height = `${Math.ceil(size.height)}px`;
    const svg = document.createElementNS(SVG, "svg");
    svg.setAttribute("width", String(Math.ceil(size.width)));
    svg.setAttribute("height", String(Math.ceil(size.height)));
    svg.setAttribute("aria-hidden", "true");
    const defs = document.createElementNS(SVG, "defs"), marker = document.createElementNS(SVG, "marker"), tip = document.createElementNS(SVG, "path");
    for (const [k, v] of Object.entries({ id: "flow-arrow", viewBox: "0 0 10 10", refX: "9", refY: "5", markerWidth: "7", markerHeight: "7", orient: "auto-start-reverse" })) marker.setAttribute(k, v);
    tip.setAttribute("d", "M0 0 L10 5 L0 10 z");
    marker.append(tip);
    defs.append(marker);
    svg.append(defs);
    for (const e of g.edges()) {
      const edge = g.edge(e), line = document.createElementNS(SVG, "polyline");
      line.setAttribute("points", edge.points.map((pt) => `${pt.x},${pt.y}`).join(" "));
      line.setAttribute("class", "flow-edge");
      line.setAttribute("marker-end", "url(#flow-arrow)");
      const label = document.createElementNS(SVG, "text");
      label.setAttribute("x", String(edge.x));
      label.setAttribute("y", String(edge.y + 4));
      label.setAttribute("class", "flow-state");
      label.textContent = edge.label;
      svg.append(line, label);
    }
    canvas.prepend(svg);
    for (const [id, node] of nodes) {
      const at = g.node(id);
      node.style.left = `${Math.round(at.x - at.width / 2)}px`;
      node.style.top = `${Math.round(at.y - at.height / 2)}px`;
      node.style.width = `${at.width}px`;
    }
    const head = P.el("div", undefined, { class: "flow-bar" }), fit = P.el("button", "Fit to width", { type: "button", class: "quiet flow-fit", "aria-pressed": "false",
      title: "Show every screen at once, or at full size with a scroll bar" });
    fit.addEventListener("click", () => { flowFit = fit.getAttribute("aria-pressed") !== "true"; renderFlow(); });
    head.append(P.el("p", lens && !machine(lens)
      ? `The app's screens in the order a record meets them. ${article(lens)}'s screens stand out; the others are another role's turn.`
      : "The app's screens in the order a record meets them, each arrow labelled with the state the record is then in. Choose a screen to design it.", { class: "muted small" }), fit);
    panel.prepend(head);
    fit.setAttribute("aria-pressed", String(fitFlow(view, sizer, canvas, size, screens.length)));
  }

  // A flow wider than the panel (ai-ops is about 2,500px) is fitted to its width while the cards stay readable (half
  // size or more); wider still, it stays full size and scrolls, with a cue on the right edge saying how many screens are
  // still out of view. "Fit to width" turns the overview on or off by hand. Returns whether the flow is fitted.
  function fitFlow(view, sizer, canvas, size, count) {
    const room = view.clientWidth, fits = Math.min(1, room / size.width);
    const scale = (flowFit === null ? fits >= 0.5 : flowFit) ? fits : 1;
    canvas.style.transform = scale < 1 ? `scale(${scale})` : "";
    sizer.style.width = `${Math.ceil(size.width * scale)}px`;
    sizer.style.height = `${Math.ceil(size.height * scale)}px`;
    view.classList.toggle("fitted", scale < 1);
    const cue = P.el("button", "", { type: "button", class: "flow-cue", hidden: "" });
    cue.addEventListener("click", () => view.scrollBy({ left: room * 0.8, behavior: "smooth" }));
    view.parentNode.append(cue);
    const update = () => {
      const hiddenRight = view.scrollWidth - view.clientWidth - view.scrollLeft;
      if (hiddenRight <= 4) { cue.hidden = true; return; }
      const shown = Math.max(1, Math.round(count * (view.scrollLeft + view.clientWidth) / view.scrollWidth));
      cue.hidden = false;
      cue.textContent = `${Math.max(1, count - shown)} more screen${count - shown === 1 ? "" : "s"} →`;
    };
    view.addEventListener("scroll", update, { passive: true });
    update();
    return scale < 1;
  }

  function scheduleFlow() {
    clearTimeout(flowTimer);
    flowTimer = setTimeout(renderFlow, 120);
  }

  function onScreens(event) {
    if (event.card) lastCard = event;
    decorate(event);
    if (flowOpen) scheduleFlow(); // an edit to a screen redraws its wireframe
  }

  function init() {
    if (P || !window.PlayIDE || !window.PlayIDE.tab) return;
    P = window.PlayIDE;
    P.hooks.inspect.push(inspectRole);
    P.hooks.screens.push(onScreens);
    P.hooks.tab.push((which) => { if (which === "screens") renderLens(); });
    P.hooks.redraw.push(() => { if (P.tab() === "screens") renderLens(); }); // a plan previewed or left changes who may do what
  }

  init();
  document.addEventListener("playide:ready", init);
})();
