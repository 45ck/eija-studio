// PlayIDE system landscape (ADR-0203): the Components tab's System lens. The workflows the open one forms a system
// with (the packs beside it whose class diagrams name a class it names) drawn as one UML component diagram: each
// workflow a «workflow» component with its provided interface (its actions, as a lollipop), the roles as actors using
// it, a class two workflows share but neither moves as a «class», and «use» dependencies from a workflow to the one
// that owns a class it names. Where the class diagrams disagree, the shapes are marked and the inspector says how.
// The server decides all of it (/api/play/landscape); the page only draws what it returns. "This app's code" is the
// component diagram read from the generated files (ADR-0155), drawn by play.js as before.
"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  const INK = "#1b2130", LINE = "#4a5568", WARN = "#b7791f", CONSIDER = "#3157d5";
  const FONT = { fontFamily: "system-ui, sans-serif", fontColor: INK, fontSize: 12 };
  const SEVERITY = { warning: "Disagrees", consider: "To consider" };
  let P = null, lens = "app", result = null, graph = null, asked = "", seq = 0, pending = "";

  const short = (names) => (names.length > 3 ? names.slice(0, 3).join(", ") + ` +${names.length - 3}` : names.join(", "));
  const about = (subject) => (result ? result.findings.filter((f) => f.subject.includes(subject) || (subject.startsWith("workflow:") && f.workflows.includes(subject.slice(9)))) : []);
  const worst = (subject) => {
    const found = result.findings.filter((f) => f.subject.includes(subject));
    return found.some((f) => f.severity === "warning") ? "warning" : found.length ? "consider" : "";
  };

  // ---- Lens ------------------------------------------------------------------------------------------------------
  function setLens(next) {
    lens = next;
    for (const b of document.querySelectorAll("#component-lens button")) b.setAttribute("aria-pressed", String(b.dataset.lens === lens));
    if (P.tab() !== "components") return;
    $("component-canvas").hidden = lens !== "app";
    $("landscape").hidden = lens !== "system";
    $("landscape-summary").hidden = lens !== "system";
    $("canvas-help").textContent = lens === "system"
      ? "The workflows this one forms a system with: they share a class on their class diagrams. Each provides its actions to the roles that hold them; a marked shape is where their class diagrams disagree."
      : "The built app's components, read from its generated files: every line is an import, a route or a file read.";
    if (lens === "system") draw();
    else P.fit();
  }

  function onTab(which) {
    $("component-bar").hidden = which !== "components";
    if (which !== "components") { $("landscape").hidden = true; return; }
    setLens(lens);
  }

  // ---- Fetch and draw --------------------------------------------------------------------------------------------
  async function draw() {
    const key = P.viewKey(), mine = ++seq;
    if (!result || key !== asked) {
      try {
        const next = await P.api("/api/play/landscape", P.about());
        if (mine !== seq) return;
        result = next;
        asked = key;
        if (graph) { graph.destroy(); graph = null; }
      } catch (error) {
        if (mine === seq) $("landscape").replaceChildren(P.el("p", `Could not read the system (${error.code || "ERROR"}): ${error.message}`, { class: "muted empty" }));
        return;
      }
    }
    summary();
    if (!graph) render();
    P.fit();
    if (pending) { const id = pending; pending = ""; select(id); }
  }

  function summary() {
    const n = result.workflows.length, c = result.counts;
    const parts = [`${n} workflow${n === 1 ? "" : "s"}`, `${result.actors.length} actor${result.actors.length === 1 ? "" : "s"}`];
    if (c.warning) parts.push(`${c.warning} disagree${c.warning === 1 ? "s" : ""}`);
    if (c.consider) parts.push(`${c.consider} to consider`);
    if (!c.warning && !c.consider && n > 1) parts.push("class diagrams agree");
    const line = $("landscape-summary");
    line.textContent = parts.join(" · ");
    line.className = "landscape-summary" + (c.warning ? " warn" : "");
    document.dispatchEvent(new CustomEvent("playide:landscape", { detail: { warning: c.warning || 0, consider: c.consider || 0 } })); // play-game.js (ADR-0208)
  }

  // The kind of actor holding a role, as the workflows declaring it say: "mixed" where they differ (a person in one, an
  // AI agent in another), drawn as a box naming each.
  const kindOf = (a) => (a.kinds.length === 1 ? a.kinds[0] : a.kinds.length ? "mixed" : "human");

  // Actors on the left, workflows stacked in the middle with their interface balls, shared classes on the right.
  function layout() {
    const WF_X = 330, WF_W = 250, WF_H = 96, GAP = 70, at = {};
    result.workflows.forEach((w, i) => { at["workflow:" + w.id] = [WF_X, 30 + i * (WF_H + GAP), WF_W, WF_H]; });
    const height = Math.max(1, result.workflows.length) * (WF_H + GAP) - GAP;
    const step = (count, span) => (count > 1 ? Math.max(100, span / (count - 1)) : 0);
    // Each actor sits level with the workflows it uses, so its lines cross as few others as they can.
    const row = Object.fromEntries(result.workflows.map((w, i) => [w.id, i]));
    const level = (a) => { const used = Object.keys(a.workflows).filter((w) => w in row); return used.reduce((s, w) => s + row[w], 0) / Math.max(1, used.length); };
    const actors = [...result.actors].sort((a, b) => level(a) - level(b) || a.name.localeCompare(b.name));
    const actorStep = step(actors.length, height - 70);
    // A person is a stick figure; an AI agent, a timer or an external system is a box, as on the use case diagram.
    actors.forEach((a, i) => { at["actor:" + a.name] = kindOf(a) === "human" ? [40, 30 + i * actorStep + (result.actors.length === 1 ? height / 2 - 40 : 0), 36, 64]
      : [-10, 38 + i * actorStep + (result.actors.length === 1 ? height / 2 - 40 : 0), 136, 48]; });
    const loose = result.classes.filter((c) => !c.owner), classStep = step(loose.length, height - 60);
    loose.forEach((c, i) => { at["class:" + c.name] = [WF_X + WF_W + 150, 30 + i * classStep + (loose.length === 1 ? height / 2 - 30 : 0), 150, 56]; });
    return at;
  }

  function render() {
    const box = $("landscape");
    box.replaceChildren();
    const { Graph, InternalEvent } = maxgraph;
    InternalEvent.disableContextMenu(box);
    graph = new Graph(box);
    for (const setting of ["setConnectable", "setCellsEditable", "setCellsDisconnectable", "setCellsResizable", "setDropEnabled"]) graph[setting](false);
    graph.setPanning(true);
    const root = graph.getDefaultParent(), at = layout(), cells = {};
    const mark = (subject) => ({ warning: { strokeColor: WARN, strokeWidth: 2.5 }, consider: { strokeColor: CONSIDER, strokeWidth: 2, dashed: true } })[worst(subject)] || {};
    const edge = (source, target, value, extra = {}) => graph.insertEdge({ parent: root, source, target, value,
      style: { ...FONT, fontSize: 10, strokeColor: LINE, dashed: true, endArrow: "open", labelBackgroundColor: "#fbfcfe", ...extra } });
    graph.batchUpdate(() => {
      for (const w of result.workflows) {
        const id = "workflow:" + w.id, [x, y, wd, h] = at[id];
        const label = `«workflow»\n${w.name}${w.id === result.focus ? " (open)" : ""}\nmoves ${w.record || "no record class"} · ${w.states} states`;
        cells[id] = graph.insertVertex({ parent: root, id: "system:" + id, value: label, position: [x, y], size: [wd, h],
          style: { ...FONT, shape: "rectangle", fillColor: w.id === result.focus ? "#e3e9ff" : "#eef2ff", strokeColor: "#5b74d6", whiteSpace: "wrap",
            fontStyle: w.id === result.focus ? 1 : 0, ...mark(id) } });
        const ball = graph.insertVertex({ parent: root, id: "system:iface:" + w.id, value: short(w.provides.map((p) => p.action)), position: [x - 46, y + h / 2 - 8], size: [16, 16],
          style: { ...FONT, shape: "ellipse", fillColor: "#ffffff", strokeColor: INK, fontSize: 9, verticalLabelPosition: "top", verticalAlign: "bottom", labelBackgroundColor: "#fbfcfe" } });
        graph.insertEdge({ parent: root, source: cells[id], target: ball, style: { strokeColor: INK, endArrow: "none" } });
        cells["iface:" + w.id] = ball;
      }
      for (const a of result.actors) {
        const id = "actor:" + a.name, [x, y, wd, h] = at[id];
        const kind = kindOf(a), look = P.actorLook[kind] || P.actorLook.system;
        cells[id] = kind === "human"
          ? graph.insertVertex({ parent: root, id: "system:" + id, value: a.name, position: [x, y], size: [wd, h],
            style: { ...FONT, shape: "actor", fillColor: "#ffffff", strokeColor: INK, verticalLabelPosition: "bottom", verticalAlign: "top" } })
          : graph.insertVertex({ parent: root, id: "system:" + id, value: `«${kind === "mixed" ? a.kinds.join(" | ") : kind}»\n${a.name}`, position: [x, y], size: [wd, h],
            style: { ...FONT, shape: "rectangle", rounded: kind === "agent", whiteSpace: "wrap", fillColor: look.fill, strokeColor: look.stroke } });
        for (const [wid, actions] of Object.entries(a.workflows)) if (actions.length) edge(cells[id], cells["iface:" + wid], "«use»");
      }
      for (const c of result.classes.filter((x) => !x.owner)) {
        const id = "class:" + c.name, [x, y, wd, h] = at[id];
        cells[id] = graph.insertVertex({ parent: root, id: "system:" + id, value: `«class»\n${c.name}\nshared, no owner`, position: [x, y], size: [wd, h],
          style: { ...FONT, shape: "rectangle", fillColor: "#ffffff", strokeColor: INK, whiteSpace: "wrap", ...mark(id) } });
        for (const wid of c.in) edge(cells["workflow:" + wid], cells[id], "«use»");
      }
      for (const l of result.links) {
        const owned = "class:" + l.class, look = mark(owned);
        edge(cells["workflow:" + l.source], cells["workflow:" + l.target], `«use» ${l.class}`, look.strokeColor ? { strokeColor: look.strokeColor } : {});
      }
    });
    graph.getSelectionModel().addListener(InternalEvent.CHANGE, () => {
      const cell = graph.getSelectionCell();
      const id = cell && cell.id ? cell.id.replace("system:iface:", "system:workflow:") : "";
      P.select(id.startsWith("system:") ? id : "", false);
    });
  }

  // Select one shape (a ripple item names it, #146): now if it is drawn, else once the system has loaded.
  function select(id) {
    const owned = id.startsWith("class:") && result && result.classes.find((c) => c.name === id.slice(6) && c.owner);
    if (owned) id = "workflow:" + owned.owner; // an owned class is drawn as its workflow
    const cell = graph && asked === P.viewKey() && graph.getDataModel().getCell("system:" + id); // not a graph about to be redrawn
    if (!cell) { pending = id; return; }
    graph.setSelectionCell(cell);
    graph.scrollCellToVisible(cell, true);
  }

  // ---- Inspector -------------------------------------------------------------------------------------------------
  function row(dl, term, value) { dl.append(P.el("dt", term), P.el("dd", value)); }

  function findings(box, list) {
    if (!list.length) return;
    const ul = P.el("ul", undefined, { class: "landscape-findings" });
    for (const f of list) {
      const li = P.el("li", undefined, { class: f.severity });
      li.append(P.el("strong", SEVERITY[f.severity] + ": "), document.createTextNode(f.message));
      ul.append(li);
    }
    box.append(ul);
  }

  function inspect(id, box) {
    if (!result) return;
    const dl = P.el("dl");
    if (id.startsWith("workflow:")) {
      const w = result.workflows.find((x) => x.id === id.slice(9));
      box.append(P.el("h3", `«workflow» ${w.name}`));
      row(dl, "Moves", w.record ? `${w.record} through ${w.states} states (ends: ${w.final_states.join(", ") || "none"})` : "no record class: it has no class diagram");
      row(dl, "Provides", w.provides.map((p) => `${p.action} (${p.roles.join(", ") || "no role yet"})`).join(", ") || "nothing");
      row(dl, "Publishes", w.publishes.map((p) => `${p.effect.replace(/^Notification:/, "")} to ${p.recipient}`).join(", ") || "no notifications");
      row(dl, "Classes", w.classes.join(", ") || "none");
      const uses = result.links.filter((l) => l.source === w.id), used = result.links.filter((l) => l.target === w.id);
      if (uses.length) row(dl, "Uses", uses.map((l) => `${l.target} (${l.class})`).join(", "));
      if (used.length) row(dl, "Used by", used.map((l) => `${l.source} (${l.class})`).join(", "));
      box.append(dl);
      findings(box, about(id));
    } else if (id.startsWith("class:")) {
      const c = result.classes.find((x) => x.name === id.slice(6));
      box.append(P.el("h3", `«class» ${c.name}`));
      row(dl, "Owner", c.owner ? `${c.owner} (its record)` : "none: no workflow moves it");
      row(dl, "Declared in", c.in.join(", "));
      box.append(dl);
      findings(box, about(id));
    } else if (id.startsWith("actor:")) {
      const a = result.actors.find((x) => x.name === id.slice(6));
      box.append(P.el("h3", `Actor ${a.name}`));
      for (const [wid, actions] of Object.entries(a.workflows)) row(dl, wid, actions.join(", ") || "a role here, holding no action yet");
      box.append(dl);
    }
    if (result.elsewhere.length) box.append(P.el("p", `Not in this system (no class in common): ${result.elsewhere.join(", ")}.`, { class: "muted small" }));
    if (result.unreadable.length) box.append(P.el("p", `Not read (the kernel's pack check refused them): ${result.unreadable.join(", ")}.`, { class: "muted small" }));
    box.append(P.el("p", result.limits.join(" "), { class: "muted small" }));
  }

  function init() {
    if (P || !window.PlayIDE) return;
    P = window.PlayIDE;
    P.hooks.tab.push(onTab);
    P.hooks.componentGraph = () => (lens === "system" ? graph : null);
    for (const b of document.querySelectorAll("#component-lens button")) b.addEventListener("click", () => setLens(b.dataset.lens));
    if (new URLSearchParams(location.search).get("lens") === "system") lens = "system";
  }

  window.PlayLandscape = { inspect, lens: () => lens, result: () => result, setLens: (next) => setLens(next), focus: select };
  init();
  document.addEventListener("playide:ready", init);
})();
