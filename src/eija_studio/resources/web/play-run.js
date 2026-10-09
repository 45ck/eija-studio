// PlayIDE run bar (ADR-0160): Run, Pause, Step, Stop and Restart, like a debugger's toolbar, over one seeded run of
// simulated users. The server runs every step through the kernel and says where the breakpoints stop it; this page
// only moves through that log, paints it on the state machine and keeps the breakpoints the person sets.
"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  const SEED = 1, STEPS = 500;
  const DOT = "data:image/svg+xml," + encodeURIComponent(
    "<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16'><circle cx='8' cy='8' r='6.5' fill='#e51400' stroke='#fff' stroke-width='1.5'/></svg>");
  const NOW = "#d99a00", REFUSED = "#a12f2f"; // the current step, as a debugger marks the current line
  let P = null, log = null, logKey = null, pos = 0, timer = 0, mode = "idle", stopNote = "", fetching = null;
  const marks = new Set(), overlays = new Map();
  let shownPos = 0; // the step last drawn

  const name = (id) => (id.startsWith("state:") ? id.slice(6) : (P.model().transitions.find((t) => "transition:" + t.id === id) || {}).action || id);
  const exists = (id) => (id.startsWith("state:") ? P.model().states.includes(id.slice(6)) : P.model().transitions.some((t) => "transition:" + t.id === id));
  const reducedMotion = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
  const appRunning = () => !$("run").hidden;

  // The run log for the model on screen, with the current breakpoints. Re-fetched when breakpoints change: the same
  // seed and model give the same steps, so the position is kept; a different model starts again from step 0.
  async function load() {
    const key = P.viewKey(), before = log;
    const body = { ...P.about(), seed: SEED, steps: STEPS, breakpoints: [...marks].filter(exists), break_on_refusal: $("break-refusal").checked };
    fetching = P.api("/api/play/run", body);
    try {
      log = await fetching;
    } finally {
      fetching = null;
    }
    if (!before || before.model !== log.model || logKey !== key) pos = 0;
    logKey = key;
    $("debug-limits").textContent = `Seed ${log.seed}, ${log.steps} steps. ` + log.limits.join(" ");
  }

  async function ready() {
    if (!log || logKey !== P.viewKey()) await load();
  }

  const stopAt = (n) => log && log.stops.find((s) => s.step === n);

  function stopText(stop) {
    if (stop.reason === "exception") return `the kernel refused ${name(stop.elements[0])} (${stop.code})`;
    return "breakpoint on " + stop.elements.map(name).join(", ");
  }

  // Run: move one step at a time at the chosen speed until a stop or the end. With reduced motion, or at the
  // fastest speed, go straight there.
  async function run() {
    if (mode === "running") return;
    try {
      if (mode === "ended") { pos = 0; P.clearSim(); }
      await ready();
    } catch (error) { return failed(error); }
    mode = "running";
    stopNote = "";
    const delay = Number($("run-speed").value);
    if (reducedMotion() || delay === 0) {
      while (pos < log.trace.length && !advance()) { /* to the next stop */ }
      return render();
    }
    const tick = () => {
      if (mode !== "running") return;
      if (advance()) return render();
      render();
      timer = setTimeout(tick, delay);
    };
    tick();
  }

  // One step forward. Returns true when the run stops here (a stop, or the end).
  function advance() {
    if (pos >= log.trace.length) { mode = "ended"; return true; }
    pos += 1;
    const stop = stopAt(pos);
    if (stop) { mode = "paused"; stopNote = stopText(stop); return true; }
    if (pos >= log.trace.length) { mode = "ended"; return true; }
    return false;
  }

  function pause() {
    if (mode !== "running") return;
    clearTimeout(timer);
    mode = "paused";
    stopNote = "paused";
    render();
  }

  async function step() {
    if (mode === "running" || mode === "ended") return;
    try { await ready(); } catch (error) { return failed(error); }
    mode = "paused";
    stopNote = "";
    advance();
    render();
  }

  async function stop() {
    clearTimeout(timer);
    const was = mode;
    mode = "idle";
    pos = 0;
    stopNote = "";
    if (was !== "idle") P.clearSim();
    let note = was !== "idle" ? "Stopped the run." : "";
    if (appRunning()) {
      try {
        if ((await P.api("/api/play/stop", {})).stopped) note += " Stopped the running app.";
      } catch (error) { note += ` Could not stop the app (${error.code || "ERROR"}).`; }
      $("run").hidden = true;
      $("run-frame").src = "about:blank";
    }
    render(note.trim() || "Ready");
  }

  async function restart() {
    clearTimeout(timer);
    mode = "idle";
    pos = 0;
    P.clearSim();
    await run();
  }

  function failed(error) {
    mode = "idle";
    render(error.code === "MODEL_CHANGED" ? "The model changed since this page loaded. Reload, then run again."
      : `Run refused (${error.code || "ERROR"}): ${error.message}`);
  }

  // What the first `pos` steps did, in the shape Simulate paints, so the diagram fills in as the run goes.
  function sofar() {
    const model = P.model(), transitions = {}, states = {}, records = {};
    for (const t of model.transitions) transitions[t.id] = { committed: 0, refused: {} };
    for (const s of model.states) states[s] = { entered: 0, now: 0 };
    for (const e of log.trace.slice(0, pos)) {
      if (e.outcome === "REFUSED") { const r = transitions[e.transition].refused; r[e.code] = (r[e.code] || 0) + 1; continue; }
      if (e.outcome === "COMMITTED") transitions[e.transition].committed += 1;
      states[e.to].entered += 1;
      records[e.record] = e.to;
    }
    for (const s of Object.values(records)) states[s].now += 1;
    return { transitions, states, records };
  }

  function render(note) {
    buttons();
    const shown = log && pos > 0 && logKey === P.viewKey();
    $("run-status").textContent = $("run-status").title = note || status();
    $("debug").hidden = !shown && !marks.size;
    breakpointList();
    if (!shown) {
      shownPos = 0;
      $("debug-pos").textContent = "";
      $("debug-now").replaceChildren(document.createTextNode("Press Run (F5) or Step (F10) to start."));
      $("debug-records").replaceChildren();
      $("debug-log").replaceChildren();
      return;
    }
    const now = log.trace[pos - 1], { records, ...counts } = sofar(), graph = P.graph();
    // The game layer (play-game.js, ADR-0208) moves a dot along this step's transition, once per single step forward.
    // A jump straight to the next stop (the fastest speed, or reduced motion) draws no traffic for the steps it skips.
    if (pos === shownPos + 1) document.dispatchEvent(new CustomEvent("playide:step", { detail: { ...now, ms: Number($("run-speed").value) } }));
    shownPos = pos;
    graph.batchUpdate(() => {
      paint(counts);
      const t = now.transition, at = now.outcome === "REFUSED" ? now.from : now.to, colour = now.outcome === "REFUSED" ? REFUSED : NOW;
      if (t) P.restyle("transition:" + t, { strokeColor: colour, strokeWidth: 6 }, graph.getDataModel().getCell("transition:" + t).value);
      else P.restyle("initial-edge", { strokeColor: NOW, strokeWidth: 4 });
      P.restyle("state:" + at, { strokeColor: colour, strokeWidth: 4, fillColor: "#fff6d6" }, graph.getDataModel().getCell("state:" + at).value);
    });
    $("debug-pos").textContent = `Step ${pos} of ${log.trace.length}`;
    $("debug-now").replaceChildren(current(now));
    $("debug-records").replaceChildren(...Object.entries(records).map(([r, s]) => {
      const tr = P.el("tr", undefined, r === now.record ? { class: "now" } : {});
      const go = P.el("button", s, { type: "button", class: "link" });
      go.addEventListener("click", () => P.select("state:" + s, true));
      const cell = P.el("td");
      cell.append(go);
      tr.append(P.el("th", r, { scope: "row" }), cell);
      return tr;
    }));
    $("debug-log").replaceChildren(...log.trace.slice(Math.max(0, pos - 40), pos).map((e) => {
      const li = P.el("li", undefined, { class: e.outcome.toLowerCase() + (e.step === pos ? " current" : "") });
      li.append(P.el("span", String(e.step), { class: "n" }), P.el("span", describe(e)));
      return li;
    }));
    // The newest step shows at the foot of the log; the log scrolls, not the panel, so who tried what stays in view.
    $("debug-log").scrollTop = $("debug-log").scrollHeight;
  }

  // Like Simulate's paint, but mid-run: a transition nobody has taken yet is only not taken yet, not a finding.
  function paint(counts) {
    const model = P.model(), most = Math.max(1, ...Object.values(counts.transitions).map((t) => t.committed));
    const crowd = Math.max(1, ...Object.values(counts.states).map((s) => s.now));
    for (const t of model.transitions) {
      const r = counts.transitions[t.id], refused = Object.values(r.refused).reduce((a, b) => a + b, 0);
      const style = r.committed ? { strokeWidth: 1 + 5 * (r.committed / most), strokeColor: "#2f6f4f" } : {};
      P.restyle("transition:" + t.id, style, r.committed || refused ? `${P.label(t)}\n✓ ${r.committed}${refused ? `  ✗ ${refused}` : ""}` : undefined);
    }
    for (const s of model.states) {
      const r = counts.states[s];
      P.restyle("state:" + s, r.entered ? { fillColor: `rgba(49,87,213,${(0.08 + 0.42 * r.now / crowd).toFixed(2)})` } : {},
        r.entered ? `${s}\n${r.now} here · ${r.entered} in` : undefined);
    }
    P.restyle("initial-edge", {});
  }

  function status() {
    if (!log || logKey !== P.viewKey() || mode === "idle") return "Ready";
    if (mode === "running") return `Running · step ${pos} of ${log.trace.length}`;
    if (mode === "ended") return `Finished · ${log.trace.length} steps`;
    return `Paused at step ${pos}` + (stopNote && stopNote !== "paused" ? `: ${stopNote}` : "");
  }

  function describe(e) {
    if (e.outcome === "CREATED") return `${e.actor} created ${e.record} in ${e.to}`;
    return `${e.actor} ${e.action} on ${e.record}: ` + (e.outcome === "REFUSED" ? `refused, ${e.code}` : `${e.from} → ${e.to}`);
  }

  // The step the run is on, as a debugger shows the current frame: who did what, and what the kernel answered.
  function current(e) {
    const dl = P.el("dl");
    const row = (term, value) => dl.append(P.el("dt", term), P.el("dd", value));
    row("Who", `${e.actor} (${e.role})`);
    row("Record", e.record);
    if (e.outcome === "CREATED") {
      row("Did", `created it in ${e.to}`);
    } else {
      row("Tried", `${e.action} from ${e.from}`);
      row("Kernel", e.outcome === "REFUSED" ? `refused: ${e.code}` : `committed → ${e.to}`);
      if (e.effects && e.effects.length) row("Effects", e.effects.join(", "));
    }
    return dl;
  }

  function buttons() {
    const idle = mode === "idle", running = mode === "running", ended = mode === "ended";
    const play = $("run-play");
    play.disabled = running;
    play.querySelector("span").textContent = mode === "paused" ? "Continue" : ended ? "Run again" : "Run";
    play.title = mode === "paused" ? "Continue (F5) to the next breakpoint" : "Run (F5): simulated users act, the kernel decides every step, and it stops at breakpoints";
    $("run-pause").disabled = !running;
    $("run-step").disabled = running || ended;
    $("run-stop").disabled = idle && !appRunning();
    $("run-restart").disabled = idle;
    document.body.dataset.run = mode;
  }

  // Breakpoints are diagram elements: a state stops the run when a record enters it, a transition when someone
  // tries it. They are shown as red dots on the diagram and listed in the Run panel.
  function toggle(id) {
    if (!id || !(id.startsWith("state:") || id.startsWith("transition:")) || !exists(id)) return;
    if (marks.has(id)) marks.delete(id); else marks.add(id);
    dots();
    if (P.selected() === id) P.select(id, false);
    if (log) load().then(() => render()).catch(failed); else render();
  }

  function dots() {
    const graph = P.graph(), { CellOverlay, ImageBox, InternalEvent } = maxgraph;
    if (!graph) return;
    for (const [id, overlay] of overlays) {
      const cell = graph.getDataModel().getCell(id);
      if (cell) graph.removeCellOverlay(cell, overlay);
    }
    overlays.clear();
    for (const id of marks) {
      const cell = graph.getDataModel().getCell(id);
      if (!cell) continue;
      const overlay = new CellOverlay(new ImageBox(DOT, 16, 16), `Breakpoint on ${name(id)}: click to remove`, "left", "top");
      overlay.addListener(InternalEvent.CLICK, () => toggle(id));
      graph.addCellOverlay(cell, overlay);
      overlays.set(id, overlay);
    }
  }

  function breakpointList() {
    $("debug-breakpoints").replaceChildren(...[...marks].map((id) => {
      const li = P.el("li"), go = P.el("button", (id.startsWith("state:") ? "Enters " : "Tries ") + name(id), { type: "button", class: "link" });
      go.addEventListener("click", () => P.select(id, true));
      const off = P.el("button", "Remove", { type: "button", class: "quiet small" });
      off.addEventListener("click", () => toggle(id));
      li.append(P.el("span", "", { class: "dot", "aria-hidden": "true" }), go, off);
      return li;
    }));
    if (!marks.size) $("debug-breakpoints").replaceChildren(P.el("li", "None. Select a state or transition and press F9.", { class: "muted small" }));
  }

  function inspectorTool(id, box) {
    const on = marks.has(id), b = P.el("button", on ? "Remove breakpoint" : "Add breakpoint", { type: "button", class: "quiet", "aria-keyshortcuts": "F9" });
    b.title = id.startsWith("state:") ? "Stop the run when a record enters this state (F9)" : "Stop the run when someone tries this transition (F9)";
    b.addEventListener("click", () => toggle(id));
    const tools = P.el("div", undefined, { class: "draft-tools" });
    tools.append(b);
    box.append(tools);
  }

  // A redraw means another model is on screen (a plan previewed or left): start again, keeping breakpoints that exist.
  function redrawn() {
    clearTimeout(timer);
    mode = "idle";
    pos = 0;
    log = null;
    for (const id of [...marks]) if (!exists(id)) marks.delete(id);
    overlays.clear();
    dots();
    render();
  }

  function keys(event) {
    const typing = event.target.closest && event.target.closest("input, textarea, select, [contenteditable]");
    const k = event.key;
    if (k === "F5" && event.ctrlKey && event.shiftKey) { event.preventDefault(); restart(); return; }
    if (k === "F5" && event.shiftKey) { event.preventDefault(); stop(); return; }
    if (k === "F5") { event.preventDefault(); if (mode !== "running") run(); return; }
    if (k === "F6") { event.preventDefault(); pause(); return; }
    if (k === "F10") { event.preventDefault(); step(); return; }
    if (k === "F9" && !typing) { event.preventDefault(); toggle(P.selected()); }
  }

  function init(bridge) {
    P = bridge;
    P.hooks.redraw.push(redrawn);
    P.hooks.inspect.push(inspectorTool);
    $("run-play").addEventListener("click", run);
    $("run-pause").addEventListener("click", pause);
    $("run-step").addEventListener("click", step);
    $("run-stop").addEventListener("click", stop);
    $("run-restart").addEventListener("click", restart);
    $("break-refusal").addEventListener("change", () => { if (log) load().then(() => render()).catch(failed); });
    new MutationObserver(buttons).observe($("run"), { attributes: true, attributeFilter: ["hidden"] });
    document.addEventListener("keydown", keys);
    render();
  }

  if (window.PlayIDE) init(window.PlayIDE);
})();
