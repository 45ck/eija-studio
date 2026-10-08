// PlayIDE sequence diagrams (ADR-0185): UML interactions between the pack's actors and its records, each message run
// through the kernel on the server. Lifelines, call arrows, refusal replies, state invariants on the record's lifeline,
// effects as asynchronous messages, and opt, alt and neg combined fragments, drawn on maxGraph at the coordinates the
// server lays out. Editing changes the sequences document only (add, change, move, delete, wrap in a fragment); every
// edit is checked again by the server. Nothing is saved: Download gives the sequences.json to keep beside the pack.
// A message the model can't produce is red with the kernel's reason; while a plan or change is shown, each message
// says what it was on the model in force, and the Changes view (ADR-0176) colours the actions the change touches.
"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  const INK = "#1b2130", LINE = "#4a5568", BAD = "#a12f2f", OK = "#17734a", FAINT = "#9aa3b5";
  const FONT = { fontFamily: "system-ui, sans-serif", fontColor: INK };
  const REFUSALS = ["ROLE_DENIED", "STATE_DENIED", "ASSIGNMENT_DENIED", "ACTOR_REVOKED", "ACTION_DENIED", "UNKNOWN_ACTOR"];
  const REVIEW = new URLSearchParams(location.search).get("view") === "review";
  let P = null, graph = null, result = null, doc = null, edited = false, at = 0, picked = "", seq = 0, kept = null;

  const shown = () => (result ? result.sequences[Math.min(at, result.sequences.length - 1)] : null);
  const authored = () => (doc ? doc.sequences[Math.min(at, doc.sequences.length - 1)] : null);

  // ---- The check ----------------------------------------------------------------------------------------------------
  async function check() {
    const mine = ++seq;
    try {
      const r = await P.api("/api/play/sequences", { ...P.about(), sequences: edited ? doc : null });
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

  function edit(change) {
    doc = structuredClone(doc);
    change(authored());
    tidy(authored());
    edited = true;
    check();
  }

  function badge() {
    const b = $("tab-sequences").querySelector(".badge");
    const n = result.counts.broken;
    b.hidden = !n;
    b.className = "badge" + (n ? " bad" : "");
    b.textContent = n ? `✗ ${n}` : "";
    $("tab-sequences").title = n ? `${n} sequence${n === 1 ? "" : "s"} the model can't produce` : "Every sequence can be produced by the model";
  }

  // ---- The page -----------------------------------------------------------------------------------------------------
  function render() {
    const s = shown();
    if (!s) return;
    list();
    verdict(s);
    composer();
    draw(s);
    exports(s);
    if (picked) inspect(picked);
  }

  function list() {
    $("seq-list").replaceChildren(...result.sequences.map((s, i) => {
      const b = P.el("button", undefined, { type: "button", "aria-current": String(i === at), title: s.first_problem || "The kernel can produce this sequence" });
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
    const text = bad ? `The model can't produce this sequence: ${s.first_problem}.` : "The kernel produced every message, and refused every neg.";
    line.replaceChildren(P.el("strong", s.title), " ", text);
    if (s.change === "breaks") line.append(P.el("span", " The change shown breaks it; the model in force produces it.", { class: "small" }));
    if (s.change === "fixes") line.append(P.el("span", " The change shown fixes it; the model in force can't produce it.", { class: "small" }));
    if (edited) line.append(P.el("span", " Edited here, not saved.", { class: "muted small" }));
  }

  function select(node, options, value) {
    node.replaceChildren(...options.map(([v, text]) => Object.assign(P.el("option", text), { value: v, selected: v === value })));
    return node;
  }

  function composer() {
    const a = authored(), actors = result.actors.map((x) => [x.id, `${x.id} : ${x.role}`]);
    select($("seq-actor"), actors, $("seq-actor").value || (actors[0] || [""])[0]);
    select($("seq-action"), result.actions.map((x) => [x, x]), $("seq-action").value || result.actions[0]);
    select($("seq-record"), a.records.map((r) => [r, r]), $("seq-record").value);
    $("seq-record").hidden = a.records.length < 2;
  }

  function exports(s) {
    const link = $("seq-download");
    if (link.href.startsWith("blob:")) URL.revokeObjectURL(link.href);
    link.href = URL.createObjectURL(new Blob([JSON.stringify(doc, null, 2) + "\n"], { type: "application/json" }));
    $("seq-reset").disabled = !edited;
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
    if (m.verdict === "NOT_REACHED" || m.verdict === "NOT_TRIED") style = { ...style, strokeColor: FAINT, fontColor: FAINT, dashed: true };
    if (changes && window.PlayDiff && status !== "same") style = { ...style, ...window.PlayDiff.look(status, "line"), fontColor: style.fontColor };
    const mark = changes && window.PlayDiff && status !== "same" ? window.PlayDiff.mark(status) : "";
    const was = m.was && m.was !== m.verdict ? `  (was ${m.was === "OK" ? "produced" : m.was.toLowerCase().replace("_", " ")})` : "";
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
          style: { ...FONT, fontSize: 12, rounded: true, arcSize: 40, fillColor: "#eef2ff", strokeColor: "#5b74d6", selectable: false } });
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
    if (l.kind === "actor") {
      graph.insertVertex({ parent, id: `head:${l.id}`, value: l.label, position: [l.x - 14, top - 4], size: [28, h - 8],
        style: { ...FONT, shape: "actor", fillColor: "#ffffff", strokeColor: INK, verticalLabelPosition: "bottom", verticalAlign: "top", fontSize: 12, selectable: false } });
    } else {
      graph.insertVertex({ parent, id: `head:${l.id}`, value: l.label, position: [l.x - 80, top], size: [160, h - 6],
        style: { ...FONT, fillColor: l.kind === "record" ? "#eef2ff" : "#f4f5f8", strokeColor: l.kind === "record" ? "#5b74d6" : "#8a93a6",
          fontSize: 12, fontStyle: l.kind === "record" ? 1 : 0, selectable: false } });
    }
    line(parent, `ll:${l.id}`, "", [l.x, top + h + (l.kind === "actor" ? 14 : 0)], [l.x, s.height],
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
    if ((cell.id.startsWith("msg:") || cell.id.startsWith("reply:")) && m) return `${m.actor} → ${m.record}: ${m.action}\n${m.why}`;
    const f = s.fragments.find((x) => x.ref === ref);
    return f && f.why ? `${f.operator}: ${f.why}` : "";
  }

  // ---- The inspector: what the kernel said, and the edits -------------------------------------------------------
  function locate(a, ref) {
    const p = ref.split(".").map(Number);
    if (p.length === 1) return { list: a.steps, i: p[0], top: true };
    return { list: a.steps[p[0]].operands[p[1]].steps, i: p[2], top: false, fragment: a.steps[p[0]] };
  }

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

  function messagePane(m) {
    const verdictText = { OK: `Produced: the record is ${(m.states || []).join(" or ")} after it`, BROKEN: `Can't be produced: ${m.code}`,
      REFUSED: `Refused by the kernel (${m.code}), as the neg asks`, COMMITTED: "Committed inside a neg: the kernel let it through",
      NOT_REACHED: "Not reached", NOT_TRIED: "Not tried" }[m.verdict];
    const out = [P.el("h3", "Message"), facts([["From", `${m.actor}`], ["To", m.record], ["Calls", m.label], ["Kernel", verdictText],
      ["Why", m.why], ["Before the change", m.was && m.was !== m.verdict ? m.was : ""]])];
    if (m.transition) out.push(button("Show on the state machine", () => P.select("transition:" + m.transition, true)));
    if (REVIEW) return out;
    const a = authored(), where = locate(a, m.ref), msg = where.list[where.i];
    const form = P.el("div", undefined, { class: "seq-form" });
    const actor = select(P.el("select", undefined, { "aria-label": "From actor" }), result.actors.map((x) => [x.id, `${x.id} : ${x.role}`]), msg.actor);
    const action = select(P.el("select", undefined, { "aria-label": "Action" }), [...new Set([...result.actions, msg.action])].map((x) => [x, x]), msg.action);
    actor.addEventListener("change", () => edit((b) => { locate(b, m.ref).list[where.i].actor = actor.value; }));
    action.addEventListener("change", () => edit((b) => { locate(b, m.ref).list[where.i].action = action.value; }));
    form.append(P.el("label", "From"), actor, P.el("label", "Action"), action);
    if (a.records.length > 1) {
      const record = select(P.el("select", undefined, { "aria-label": "To record" }), a.records.map((r) => [r, r]), msg.record || a.records[0]);
      record.addEventListener("change", () => edit((b) => { locate(b, m.ref).list[where.i].record = record.value; }));
      form.append(P.el("label", "To"), record);
    }
    const tools = P.el("div", undefined, { class: "seq-tools" });
    const move = (by) => edit((b) => { const w = locate(b, m.ref); const [x] = w.list.splice(w.i, 1); w.list.splice(w.i + by, 0, x); picked = ""; });
    tools.append(button("Move up", () => move(-1), where.i ? {} : { disabled: "" }), button("Move down", () => move(1), where.i < where.list.length - 1 ? {} : { disabled: "" }),
      button("Delete", () => edit((b) => { const w = locate(b, m.ref); w.list.splice(w.i, 1); picked = ""; }), shown().messages.length > 1 ? {} : { disabled: "" }));
    if (where.top) {
      for (const op of ["opt", "alt", "neg"]) {
        tools.append(button(`Wrap in ${op}`, () => edit((b) => {
          const w = locate(b, m.ref), x = w.list[w.i];
          const operands = op === "alt" ? [{ guard: "", steps: [x] }, { guard: "else", steps: [structuredClone(x)] }] : [{ guard: "", steps: [x] }];
          w.list[w.i] = { fragment: op, operands, refused: null };
          picked = "frame:" + m.ref;
        })));
      }
    }
    return [...out, P.el("h3", "Change it"), form, tools];
  }

  function fragmentPane(f) {
    const out = [P.el("h3", `${f.operator} fragment`), facts([["Kernel", f.verdict ? `${f.verdict}${f.code ? ` (${f.code})` : ""}` : "Each operand is checked as its own trace"],
      ["Why", f.why || ""], ["Before the change", f.was && f.was !== f.verdict ? f.was : ""]])];
    if (REVIEW) return out;
    const a = authored(), i = Number(f.ref), frag = a.steps[i], form = P.el("div", undefined, { class: "seq-form" });
    frag.operands.forEach((o, k) => {
      const input = P.el("input", undefined, { type: "text", maxlength: "60", "aria-label": `Guard of operand ${k + 1}`, value: o.guard });
      input.addEventListener("change", () => edit((b) => { b.steps[i].operands[k].guard = input.value.trim(); }));
      form.append(P.el("label", k ? `Operand ${k + 1}` : "Guard"), input);
    });
    if (frag.fragment === "neg") {
      const code = select(P.el("select", undefined, { "aria-label": "Refusal expected" }), [["", "any refusal"], ...REFUSALS.map((c) => [c, c])], frag.refused || "");
      code.addEventListener("change", () => edit((b) => { b.steps[i].refused = code.value || null; }));
      form.append(P.el("label", "Refused with"), code);
    }
    const tools = P.el("div", undefined, { class: "seq-tools" });
    if (frag.fragment === "alt" && frag.operands.length < 4) {
      tools.append(button("Add alternative", () => edit((b) => { b.steps[i].operands.push({ guard: "else", steps: [structuredClone(b.steps[i].operands[0].steps[0])] }); })));
    }
    tools.append(button("Unwrap", () => edit((b) => { b.steps.splice(i, 1, ...b.steps[i].operands[0].steps); picked = ""; })),
      button("Delete", () => edit((b) => { b.steps.splice(i, 1); picked = ""; }), a.steps.length > 1 ? {} : { disabled: "" }));
    return [...out, P.el("h3", "Change it"), form, tools];
  }

  function overview() {
    const s = shown(), out = [P.el("h3", "Sequence"), facts([["Messages", String(s.messages)], ["Kernel", s.verdict === "BROKEN" ? s.first_problem : "Every message produced"],
      ["Source", { pack: "the pack's sequences.json", default: "generated from the model in force", edited: "edited here, not saved" }[result.source]]])];
    out.push(P.el("p", "Select a message or a fragment to see what the kernel said about it.", { class: "muted small" }));
    if (REVIEW) return out;
    const title = P.el("input", undefined, { type: "text", maxlength: "80", "aria-label": "Title", value: authored().title });
    title.addEventListener("change", () => title.value.trim() && edit((b) => { b.title = title.value.trim(); }));
    const form = P.el("div", undefined, { class: "seq-form" });
    form.append(P.el("label", "Title"), title);
    const remove = button("Delete this sequence", () => { doc = structuredClone(doc); doc.sequences.splice(at, 1); at = 0; edited = true; check(); },
      doc.sequences.length > 1 ? {} : { disabled: "" });
    return [...out, form, remove];
  }

  // Fragments left with no operand go; an alt left with one operand becomes an opt; only a neg names a refusal.
  function tidy(a) {
    a.steps = a.steps.filter((step) => {
      if (!step.fragment) return true;
      step.operands = step.operands.filter((o) => o.steps.length);
      if (step.fragment === "alt" && step.operands.length === 1) step.fragment = "opt";
      if (step.fragment !== "neg") step.refused = null;
      return step.operands.length > 0;
    });
  }

  // ---- Adding ---------------------------------------------------------------------------------------------------
  function add(event) {
    event.preventDefault();
    const message = { actor: $("seq-actor").value, action: $("seq-action").value, record: $("seq-record").hidden ? "" : $("seq-record").value };
    edit((a) => {
      if (picked.startsWith("msg:")) {
        const w = locate(a, picked.slice(4));
        w.list.splice(w.i + 1, 0, message);
        const p = picked.slice(4).split(".");
        p[p.length - 1] = String(w.i + 1);
        picked = "msg:" + p.join(".");
      } else {
        a.steps.push(message);
        picked = "msg:" + (a.steps.length - 1);
      }
    });
  }

  function addSequence() {
    doc = structuredClone(doc);
    const taken = new Set(doc.sequences.map((s) => s.id));
    let n = doc.sequences.length + 1;
    while (taken.has(`sequence-${n}`)) n += 1;
    const first = result.sequences[0].messages[0];
    doc.sequences.push({ id: `sequence-${n}`, title: `New sequence ${n}`, records: [authored().records[0]],
      steps: [{ actor: first ? first.actor : result.actors[0].id, action: first ? first.action : result.actions[0], record: "" }] });
    at = doc.sequences.length - 1;
    picked = "";
    edited = true;
    check();
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
      if (result) render(); else check();
    });
    P.hooks.redraw.push(() => { picked = ""; check(); }); // a preview entered or left: check the same sequences on the shown model
    $("seq-add").addEventListener("submit", add);
    $("seq-new").addEventListener("click", addSequence);
    $("seq-reset").addEventListener("click", () => { edited = false; picked = ""; at = 0; check(); });
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
