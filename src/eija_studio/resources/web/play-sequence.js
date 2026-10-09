// PlayIDE sequence diagrams (ADR-0195): the pack's scenarios (scenarios.json, the Tests tab's test cases, ADR-0177)
// drawn as UML interactions between the actors and the record, each step run through the kernel on the server.
// Lifelines, call arrows, refusal replies, state invariants on the record's lifeline, effects as asynchronous messages,
// and a neg combined fragment around each step that must be refused, drawn on maxGraph at the coordinates the server
// lays out. Edits change the one scenarios draft the Tests tab also shows (add, change, move, delete a step, change
// what it expects); every edit is checked again by the server. Nothing is saved: Download gives scenarios.json.
// A step the model can't do is red with the kernel's reason; while a plan or change is shown, each message says what
// it was on the model in force, and the Changes view (ADR-0176) colours the actions the change touches.
"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  const INK = "#1b2130", LINE = "#4a5568", BAD = "#a12f2f", OK = "#17734a", FAINT = "#9aa3b5";
  const FONT = { fontFamily: "system-ui, sans-serif", fontColor: INK };
  const REFUSALS = ["ROLE_DENIED", "STATE_DENIED", "ASSIGNMENT_DENIED", "ACTOR_REVOKED", "ACTION_DENIED", "UNKNOWN_ACTOR"];
  const REVIEW = new URLSearchParams(location.search).get("view") === "review";
  let P = null, graph = null, result = null, doc = null, at = 0, picked = "", seq = 0, kept = null, asked = "";

  const shown = () => (result && result.sequences.length ? result.sequences[Math.min(at, result.sequences.length - 1)] : null);
  const authored = () => (doc && doc.scenarios.length ? doc.scenarios[Math.min(at, doc.scenarios.length - 1)] : null);
  const draft = () => (window.PlayTests ? window.PlayTests.draft() : null);
  const edited = () => Boolean(draft());

  // ---- The check ----------------------------------------------------------------------------------------------------
  async function check() {
    const mine = ++seq;
    asked = JSON.stringify(draft());
    try {
      const r = await P.api("/api/play/sequences", draft() ? { ...P.about(), scenarios: draft() } : P.about());
      if (mine !== seq) return; // a newer edit or preview asked again
      result = r;
      doc = r.document;
      badge();
      if (P.tab() === "sequences") render();
    } catch (error) {
      if (mine !== seq) return;
      $("seq-verdict").replaceChildren(P.el("span", `${error.code || "ERROR"}: ${error.message}`, { class: "refusal" }));
    }
  }

  // One draft for both tabs: the Tests tab keeps it and runs it; this tab draws and checks it.
  function save(next) {
    doc = next;
    window.PlayTests.edit(next);
    check();
  }

  function edit(change) {
    const next = structuredClone(doc);
    change(next.scenarios[Math.min(at, next.scenarios.length - 1)], next);
    save(next);
  }

  // What the kernel does for these (actor, action) steps from `start`: a new step expects exactly that.
  async function tried(start, steps) {
    return (await P.api("/api/play/tests/try", { ...P.about(), start: start || null, steps })).steps;
  }

  function badge() {
    const b = $("tab-sequences").querySelector(".badge");
    const n = result.counts.broken;
    b.hidden = !n;
    b.className = "badge" + (n ? " bad" : "");
    b.textContent = n ? `✗ ${n}` : "";
    $("tab-sequences").title = n ? `${n} scenario${n === 1 ? "" : "s"} the model can't produce` : "The model produces every scenario";
  }

  // ---- The page -----------------------------------------------------------------------------------------------------
  function render() {
    const s = shown();
    list();
    if (!s) {
      $("seq-verdict").className = "seq-verdict";
      $("seq-verdict").textContent = "This pack has no scenarios yet. Press New scenario to add one.";
      if (graph) { graph.destroy(); graph = null; }
      $("sequence-canvas").replaceChildren();
      $("inspector").replaceChildren();
      return;
    }
    verdict(s);
    composer();
    draw(s);
    exports(s);
    if (picked) inspect(picked);
  }

  function list() {
    $("seq-list").replaceChildren(...result.sequences.map((s, i) => {
      const b = P.el("button", undefined, { type: "button", "aria-current": String(i === at), title: s.first_problem || "The kernel does every step as written" });
      b.append(P.el("span", s.verdict === "BROKEN" ? "✗" : "✓", { class: "seq-mark " + (s.verdict === "BROKEN" ? "bad" : "ok"), "aria-hidden": "true" }), P.el("span", s.title));
      if (s.change && s.change !== "same") b.append(P.el("span", s.change, { class: "tag " + (s.change === "breaks" ? "bad" : "ok") }));
      b.addEventListener("click", () => { at = i; picked = ""; kept = null; render(); });
      const li = P.el("li");
      li.append(b);
      return li;
    }));
  }

  function verdict(s) {
    const line = $("seq-verdict"), bad = s.verdict === "BROKEN";
    line.className = "seq-verdict " + (bad ? "bad" : "ok");
    const text = bad ? `The model can't produce this scenario: ${s.first_problem}.` : "The kernel did every step as written, and refused every neg.";
    line.replaceChildren(P.el("strong", s.title), " ", text);
    if (s.change === "breaks") line.append(P.el("span", " The change shown breaks it; the model in force produces it.", { class: "small" }));
    if (s.change === "fixes") line.append(P.el("span", " The change shown fixes it; the model in force can't produce it.", { class: "small" }));
    if (edited()) line.append(P.el("span", " Edited, not saved (the Tests tab shows the same draft).", { class: "muted small" }));
  }

  function select(node, options, value) {
    node.replaceChildren(...options.map(([v, text]) => Object.assign(P.el("option", text), { value: v, selected: v === value })));
    return node;
  }

  function composer() {
    const actors = result.actors.map((x) => [x.id, `${x.id} : ${x.role}`]);
    select($("seq-actor"), actors, $("seq-actor").value || (actors[0] || [""])[0]);
    select($("seq-action"), result.actions.map((x) => [x, x]), $("seq-action").value || result.actions[0]);
  }

  function exports(s) {
    const link = $("seq-download");
    if (link.href.startsWith("blob:")) URL.revokeObjectURL(link.href);
    link.href = URL.createObjectURL(new Blob([JSON.stringify(doc, null, 2) + "\n"], { type: "application/json" }));
    $("seq-reset").disabled = !edited();
    $("seq-copy-mermaid").dataset.text = s.export.mermaid;
    $("seq-copy-plantuml").dataset.text = s.export.plantuml;
  }

  // ---- The diagram --------------------------------------------------------------------------------------------------
  function registerFrameTab() {
    const { Shape, ShapeRegistry } = maxgraph;
    if (registerFrameTab.done || !Shape || !ShapeRegistry) return;
    // The pentagon label of a UML combined fragment, as draw.io's umlFrame shape draws it (Apache-2.0, geometry only).
    class FrameTab extends Shape {
      paintVertexShape(c, x, y, w, h) {
        const cut = Math.min(9, h / 2);
        c.begin(); c.moveTo(x, y); c.lineTo(x + w, y); c.lineTo(x + w, y + h - cut); c.lineTo(x + w - cut, y + h); c.lineTo(x, y + h); c.close();
        c.fillAndStroke();
      }
    }
    ShapeRegistry.add("umlFrameTab", FrameTab);
    registerFrameTab.done = true;
  }

  function line(parent, id, value, from, to, style) {
    const { Point } = maxgraph;
    const edge = graph.insertEdge({ parent, id, value, style: { ...FONT, fontSize: 12, verticalAlign: "bottom", labelBackgroundColor: "none", ...style } });
    edge.geometry.setTerminalPoint(new Point(from[0], from[1]), true);
    edge.geometry.setTerminalPoint(new Point(to[0], to[1]), false);
    return edge;
  }

  function messageLook(m) {
    const changes = P.changes(), status = m.change || "same";
    let style = { strokeColor: LINE, strokeWidth: 1.5, endArrow: "block", endFill: true, endSize: 8 };
    if (m.verdict === "BROKEN") style = { ...style, strokeColor: BAD, fontColor: BAD, strokeWidth: 2.5, fontStyle: 1 };
    if (m.verdict === "NOT_REACHED") style = { ...style, strokeColor: FAINT, fontColor: FAINT, dashed: true };
    if (changes && window.PlayDiff && status !== "same") style = { ...style, ...window.PlayDiff.look(status, "line"), fontColor: style.fontColor };
    const mark = changes && window.PlayDiff && status !== "same" ? window.PlayDiff.mark(status) : "";
    const was = m.was && m.was !== m.verdict ? `  (was ${{ OK: "produced", HOLDS: "refused" }[m.was] || m.was.toLowerCase().replace("_", " ")})` : "";
    return { style, value: (m.verdict === "BROKEN" ? "✗ " : "") + mark + m.label + was };
  }

  function draw(s) {
    const { Graph, InternalEvent } = maxgraph;
    const box = $("sequence-canvas");
    registerFrameTab();
    // An edit redraws the sequence: keep the zoom and scroll the person chose; another sequence starts from place().
    kept = graph && kept && kept.at === at ? { at, scale: graph.view.scale, x: graph.view.translate.x, y: graph.view.translate.y } : null;
    if (graph) graph.destroy();
    box.replaceChildren();
    InternalEvent.disableContextMenu(box);
    graph = new Graph(box);
    for (const off of ["setConnectable", "setCellsEditable", "setCellsDisconnectable", "setDropEnabled", "setCellsMovable", "setCellsResizable", "setCellsBendable"]) graph[off](false);
    graph.setPanning(true);
    graph.setTooltips(true);
    graph.getTooltipForCell = (cell) => tooltip(cell);
    const parent = graph.getDefaultParent(), x = Object.fromEntries(s.lifelines.map((l) => [l.id, l.x]));
    graph.batchUpdate(() => {
      for (const f of s.fragments) frame(parent, f);
      for (const l of s.lifelines) lifeline(parent, l, s);
      for (const v of s.invariants) {
        graph.insertVertex({ parent, id: `inv:${v.ref}`, value: v.text, position: [x[v.lifeline] - 60, v.y - 13], size: [120, 26],
          style: { ...FONT, fontSize: 12, rounded: true, arcSize: 40, selectable: false,
            ...(v.tone === "bad" ? { fillColor: "#fdecec", strokeColor: BAD, fontColor: BAD } : { fillColor: "#eef2ff", strokeColor: "#5b74d6" }) } });
      }
      for (const m of s.messages) {
        const { style, value } = messageLook(m);
        line(parent, `msg:${m.ref}`, value, [x[m.from], m.y], [x[m.to], m.y], style);
      }
      for (const r of s.replies) {
        const tone = r.tone === "bad" ? BAD : OK;
        line(parent, `reply:${r.ref}`, r.label, [x[r.from], r.y], [x[r.to], r.y],
          { strokeColor: tone, fontColor: tone, dashed: true, endArrow: "open", endSize: 8, fontSize: 11 });
      }
      s.effects.forEach((e, i) => line(parent, `effect:${e.ref}:${i}`, e.label, [x[e.from], e.y], [x[e.to], e.y],
        { strokeColor: "#7a8396", fontColor: "#5f687a", endArrow: "open", endSize: 7, fontSize: 11, selectable: false }));
    });
    graph.getSelectionModel().addListener(InternalEvent.CHANGE, () => {
      const cell = graph.getSelectionCell(), id = cell ? cell.id : "";
      const ref = id.startsWith("msg:") || id.startsWith("reply:") ? "msg:" + id.split(":")[1] : id.startsWith("frame") ? "frame:" + id.split(":")[1] : "";
      picked = ref;
      inspect(ref);
    });
    if (kept) graph.view.scaleAndTranslate(kept.scale, kept.x, kept.y);
    else place();
    kept = { at };
    if (picked) {
      const cell = graph.getDataModel().getCell(picked) || graph.getDataModel().getCell(picked.replace("frame:", "frame-tab:"));
      if (cell) graph.setSelectionCell(cell);
    }
  }

  // Readable first: the sequence fills the width down to 70% scale, top aligned; wider ones pan (Fit shows all of it).
  function place() {
    const s = shown(), box = $("sequence-canvas");
    if (!graph || !s || !box.clientWidth) return;
    const scale = Math.max(0.7, Math.min(1.1, (box.clientWidth - 24) / s.width));
    graph.view.scaleAndTranslate(scale, Math.max(12 / scale, (box.clientWidth / scale - s.width) / 2), 8 / scale);
  }

  function lifeline(parent, l, s) {
    const top = s.head.y, h = s.head.height;
    const look = { agent: ["#f3edff", "#6b46c1"], timer: ["#fff7e6", "#b7791f"], system: ["#eef2f6", "#4a5568"] }[l.actor_kind];
    if (l.kind === "actor" && look) { // an AI agent, timer or external system (ADR-0210): an actor box with its keyword
      graph.insertVertex({ parent, id: `head:${l.id}`, value: l.label.replace(/^(«\w+») /, "$1\n"), position: [l.x - 80, top], size: [160, h - 6],
        style: { ...FONT, fillColor: look[0], strokeColor: look[1], rounded: l.actor_kind === "agent", whiteSpace: "wrap", fontSize: 12, selectable: false } });
    } else if (l.kind === "actor") {
      graph.insertVertex({ parent, id: `head:${l.id}`, value: l.label, position: [l.x - 14, top - 4], size: [28, h - 8],
        style: { ...FONT, shape: "actor", fillColor: "#ffffff", strokeColor: INK, verticalLabelPosition: "bottom", verticalAlign: "top", fontSize: 12, selectable: false } });
    } else {
      graph.insertVertex({ parent, id: `head:${l.id}`, value: l.label, position: [l.x - 80, top], size: [160, h - 6],
        style: { ...FONT, fillColor: l.kind === "record" ? "#eef2ff" : "#f4f5f8", strokeColor: l.kind === "record" ? "#5b74d6" : "#8a93a6",
          fontSize: 12, fontStyle: l.kind === "record" ? 1 : 0, selectable: false } });
    }
    line(parent, `ll:${l.id}`, "", [l.x, top + h + (l.kind === "actor" && !look ? 14 : 0)], [l.x, s.height],
      { strokeColor: "#9aa3b5", dashed: true, dashPattern: "4 4", endArrow: "none", startArrow: "none", selectable: false });
  }

  function frame(parent, f) {
    const bad = f.verdict === "BROKEN", tone = bad ? BAD : f.operator === "neg" && f.verdict === "HOLDS" ? OK : LINE;
    graph.insertVertex({ parent, id: `frame:${f.ref}`, value: "", position: [f.x0, f.y0], size: [f.x1 - f.x0, f.y1 - f.y0],
      style: { fillColor: f.operator === "neg" ? "#fbfbfd" : "none", strokeColor: tone, strokeWidth: bad ? 2.5 : 1.2 } });
    const tag = f.operator === "neg" ? `neg${f.verdict === "HOLDS" ? " ✓" : f.verdict === "BROKEN" ? " ✗" : ""}` : f.operator;
    graph.insertVertex({ parent, id: `frame-tab:${f.ref}`, value: tag, position: [f.x0, f.y0], size: [Math.max(44, tag.length * 8 + 16), 22],
      style: { ...FONT, shape: "umlFrameTab", fillColor: "#ffffff", strokeColor: tone, fontColor: tone, fontSize: 12, fontStyle: 1 } });
    f.operands.forEach((o, k) => {
      if (k) line(parent, `operand:${f.ref}:${k}`, "", [f.x0, o.y - 15], [f.x1, o.y - 15],
        { strokeColor: LINE, dashed: true, dashPattern: "6 4", endArrow: "none", selectable: false });
      if (o.guard || f.operator !== "neg") {
        graph.insertVertex({ parent, id: `guard:${f.ref}:${k}`, value: `[${o.guard || (f.operator === "alt" && k ? "else" : "guard")}]`,
          position: [f.x0 + (k ? 8 : 70), o.y - 11], size: [170, 18],
          style: { ...FONT, fillColor: "none", strokeColor: "none", fontSize: 11, align: "left", fontColor: "#5f687a", selectable: false } });
      }
    });
  }

  function tooltip(cell) {
    if (!cell || !cell.id) return "";
    const s = shown(), ref = cell.id.split(":")[1];
    const m = s.messages.find((x) => x.ref === ref);
    if ((cell.id.startsWith("msg:") || cell.id.startsWith("reply:")) && m) return `${m.actor} → ${m.to.slice(7)}: ${m.action}\n${m.why}`;
    const f = s.fragments.find((x) => x.ref === ref);
    return f && f.why ? `${f.operator}: ${f.why}` : "";
  }

  // ---- The inspector: what the kernel said, and the edits -------------------------------------------------------
  function button(text, run, attrs = {}) {
    const b = P.el("button", text, { type: "button", class: "quiet", ...attrs });
    b.addEventListener("click", run);
    return b;
  }

  function inspect(ref) {
    const box = $("inspector");
    if (!ref) { box.replaceChildren(...overview()); return; }
    const s = shown();
    if (ref.startsWith("msg:")) {
      const m = s.messages.find((x) => x.ref === ref.slice(4));
      if (m) { box.replaceChildren(...messagePane(m)); return; }
    }
    const f = s.fragments.find((x) => x.ref === ref.slice(6));
    box.replaceChildren(...(f ? fragmentPane(f) : overview()));
  }

  function facts(rows) {
    const dl = P.el("dl");
    for (const [k, v] of rows) if (v) dl.append(P.el("dt", k), P.el("dd", v));
    return dl;
  }

  const said = (then) => (then.state ? `moves to ${then.state}` : `is refused (${then.refused})`);

  // One choice for what a step must do: the state it moves the record to, or the refusal it gets.
  function expectation(then, label) {
    const options = [...result.states.map((x) => [`state:${x}`, `moves to ${x}`]), ...REFUSALS.map((c) => [`refused:${c}`, `is refused (${c})`])];
    return select(P.el("select", undefined, { "aria-label": label }), options, then.state ? `state:${then.state}` : `refused:${then.refused}`);
  }

  function messagePane(m) {
    const verdictText = { OK: `Produced: the record is ${m.states.join(" or ")} after it`, BROKEN: `Can't be produced${m.code ? `: ${m.code}` : ""}`,
      HOLDS: `Refused by the kernel (${m.code}), as the neg asks`, NOT_REACHED: "Not reached" }[m.verdict];
    const out = [P.el("h3", "Message"), facts([["From", `${m.actor}${m.role ? ` : ${m.role}` : ""}`], ["To", m.to.slice(7)], ["Calls", m.label],
      ["Expects", `It ${said(m.expect)}`], ["Kernel", verdictText], ["Why", m.why], ["Before the change", m.was && m.was !== m.verdict ? m.was : ""]])];
    if (m.transition) out.push(button("Show on the state machine", () => P.select("transition:" + m.transition, true)));
    if (REVIEW) return out;
    const i = Number(m.ref), steps = authored().steps, now = steps[i];
    const form = P.el("div", undefined, { class: "seq-form" });
    const actor = select(P.el("select", undefined, { "aria-label": "From actor" }), result.actors.map((x) => [x.id, `${x.id} : ${x.role}`]), now.actor);
    const action = select(P.el("select", undefined, { "aria-label": "Action" }), [...new Set([...result.actions, now.action])].map((x) => [x, x]), now.action);
    const then = expectation(now.then, "What it must do");
    actor.addEventListener("change", () => edit((a) => { a.steps[i].actor = actor.value; }));
    action.addEventListener("change", () => edit((a) => { a.steps[i].action = action.value; }));
    then.addEventListener("change", () => edit((a) => { const [k, v] = then.value.split(":"); a.steps[i].then = { [k]: v }; }));
    form.append(P.el("label", "From"), actor, P.el("label", "Action"), action, P.el("label", "It must"), then);
    const tools = P.el("div", undefined, { class: "seq-tools" });
    const move = (by) => edit((a) => { const [x] = a.steps.splice(i, 1); a.steps.splice(i + by, 0, x); picked = `msg:${i + by}`; });
    const actual = m.verdict === "BROKEN" && (m.code || m.states.length) ? (m.code ? { refused: m.code } : { state: m.states[0] }) : null;
    if (actual) tools.append(button("Expect what the kernel does", () => edit((a) => { a.steps[i].then = actual; }), { title: `It ${said(actual)}` }));
    tools.append(button("Move up", () => move(-1), i ? {} : { disabled: "" }), button("Move down", () => move(1), i < steps.length - 1 ? {} : { disabled: "" }),
      button("Delete", () => edit((a) => { a.steps.splice(i, 1); picked = ""; }), steps.length > 1 ? {} : { disabled: "" }));
    return [...out, P.el("h3", "Change it"), form, tools];
  }

  function fragmentPane(f) {
    const m = shown().messages.find((x) => x.ref === f.ref);
    const kernel = { HOLDS: `Refused (${m.code})`, BROKEN: m.code ? `Refused with ${m.code} instead` : "Let through", NOT_REACHED: "Not reached" }[f.verdict];
    const out = [P.el("h3", "neg fragment"), P.el("p", "A trace that must not happen: the kernel has to refuse this step.", { class: "muted small" }),
      facts([["Refused with", f.refused], ["Kernel", kernel], ["Why", f.why || ""], ["Before the change", m.was && m.was !== m.verdict ? m.was : ""]])];
    if (REVIEW) return out;
    const i = Number(f.ref), form = P.el("div", undefined, { class: "seq-form" });
    const code = select(P.el("select", undefined, { "aria-label": "Refusal expected" }), REFUSALS.map((c) => [c, c]), f.refused);
    code.addEventListener("change", () => edit((a) => { a.steps[i].then = { refused: code.value }; }));
    form.append(P.el("label", "Refused with"), code);
    const tools = P.el("div", undefined, { class: "seq-tools" });
    if (m.states.length) tools.append(button(`Unwrap: it moves to ${m.states[0]}`, () => edit((a) => { a.steps[i].then = { state: m.states[0] }; picked = `msg:${i}`; })));
    tools.append(button("Delete", () => edit((a) => { a.steps.splice(i, 1); picked = ""; }), authored().steps.length > 1 ? {} : { disabled: "" }));
    return [...out, P.el("h3", "Change it"), form, tools];
  }

  function overview() {
    const s = shown(), a = authored();
    const out = [P.el("h3", "Scenario"), facts([["Steps", String(s.steps)], ["Starts in", s.invariants[0].text],
      ["Kernel", s.verdict === "BROKEN" ? s.first_problem : "Every step does what it says"],
      ["Source", result.source === "edited" ? "a draft of scenarios.json, not saved" : "the pack's scenarios.json"]])];
    out.push(P.el("p", "Select a message or a neg fragment to see what the kernel said about it. The Tests tab runs the same scenarios.", { class: "muted small" }));
    if (REVIEW) return out;
    const title = P.el("input", undefined, { type: "text", maxlength: "120", "aria-label": "Title", value: a.title });
    title.addEventListener("change", () => title.value.trim() && edit((b) => { b.title = title.value.trim(); }));
    const start = select(P.el("select", undefined, { "aria-label": "Start state" }), [["", `${result.initial} (where a new record starts)`],
      ...result.states.filter((x) => x !== result.initial).map((x) => [x, x])], a.start || "");
    start.addEventListener("change", () => edit((b) => { if (start.value) b.start = start.value; else delete b.start; }));
    const form = P.el("div", undefined, { class: "seq-form" });
    form.append(P.el("label", "Title"), title, P.el("label", "Starts in"), start);
    const remove = button("Delete this scenario", () => { const next = structuredClone(doc); next.scenarios.splice(at, 1); at = 0; picked = ""; save(next); },
      doc.scenarios.length > 1 ? {} : { disabled: "" });
    return [...out, form, remove];
  }

  // ---- Adding ---------------------------------------------------------------------------------------------------
  function failed(error) {
    $("seq-verdict").replaceChildren(P.el("span", `${error.code || "ERROR"}: ${error.message}`, { class: "refusal" }));
  }

  // A new step expects what the kernel does now, after the steps before it; the inspector changes that expectation.
  async function add(event) {
    event.preventDefault();
    const a = authored(), after = picked.startsWith("msg:") ? Number(picked.slice(4)) + 1 : a.steps.length;
    const steps = [...a.steps.slice(0, after).map((x) => [x.actor, x.action]), [$("seq-actor").value, $("seq-action").value]];
    try {
      const made = (await tried(a.start, steps)).at(-1);
      edit((b) => { b.steps.splice(after, 0, made); picked = `msg:${after}`; });
    } catch (error) {
      failed(error);
    }
  }

  async function addSequence() {
    const next = structuredClone(doc), taken = new Set(next.scenarios.map((s) => s.id));
    let n = next.scenarios.length + 1;
    while (taken.has(`scenario-${n}`)) n += 1;
    try {
      next.scenarios.push({ id: `scenario-${n}`, title: `New scenario ${n}`, steps: await tried(null, [[$("seq-actor").value, $("seq-action").value]]) });
    } catch (error) {
      failed(error);
      return;
    }
    at = next.scenarios.length - 1;
    picked = "";
    save(next);
  }

  function copy(id) {
    const text = $(id).dataset.text || "";
    const done = () => { $("toast").textContent = "Copied"; $("toast").classList.add("show"); setTimeout(() => $("toast").classList.remove("show"), 1600); };
    if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, () => {});
    $(id).closest("details").open = false;
  }

  function init() {
    if (P || !window.PlayIDE || !window.PlayIDE.tab) return;
    P = window.PlayIDE;
    $("tab-sequences").append(P.el("span", "", { class: "badge", hidden: "" }));
    P.hooks.sequenceGraph = () => graph;
    P.hooks.tab.push((which) => {
      if (which !== "sequences") return;
      kept = null;
      if (result && asked === JSON.stringify(draft())) render(); else check(); // the Tests tab may have changed the draft
    });
    P.hooks.redraw.push(() => { picked = ""; check(); }); // a preview entered or left: check the same sequences on the shown model
    $("seq-add").addEventListener("submit", add);
    $("seq-new").addEventListener("click", addSequence);
    $("seq-reset").addEventListener("click", () => { picked = ""; at = 0; window.PlayTests.edit(null); check(); });
    $("seq-copy-mermaid").addEventListener("click", () => copy("seq-copy-mermaid"));
    $("seq-copy-plantuml").addEventListener("click", () => copy("seq-copy-plantuml"));
    if (REVIEW) for (const node of document.querySelectorAll(".seq-edit")) node.hidden = true;
    window.PlaySequence = {
      cellsFor: (transitions) => (shown() ? shown().messages.filter((m) => transitions.includes(m.transition)).map((m) => `msg:${m.ref}`) : []),
      result: () => result,
      open: (id) => { const i = result ? result.sequences.findIndex((x) => x.id === id) : -1; if (i >= 0) { at = i; picked = ""; kept = null; } },
    };
    check();
  }

  init();
  document.addEventListener("playide:ready", init);
})();
