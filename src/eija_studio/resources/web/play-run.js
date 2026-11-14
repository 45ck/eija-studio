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
  let P = null, log = null, logKey = null, pos = 0, timer = 0, mode = "idle", stopNote = "", loads = 0, pending = null;
  let loading = false; // a Run or Step is waiting for its log: Stop can cancel it, so it is enabled
  let generation = 0; // bumped by Stop, Restart and a redraw, so a Run or Step still loading its log does not start after them
  const marks = new Set(), overlays = new Map();
  let shownPos = 0; // the step last drawn

  const name = (id) => (id.startsWith("state:") ? id.slice(6) : (P.model().transitions.find((t) => "transition:" + t.id === id) || {}).action || id);
  const exists = (id) => (id.startsWith("state:") ? P.model().states.includes(id.slice(6)) : P.model().transitions.some((t) => "transition:" + t.id === id));
  const reducedMotion = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
  const appRunning = () => !$("run").hidden;

  // The run log for the model on screen, with the current breakpoints. Re-fetched when breakpoints change: the same
  // seed and model give the same steps, so the position is kept; a different model starts again from step 0.
  // Only the log for the newest breakpoints, on the model on show, is kept: an earlier one landing late would run
  // without a breakpoint the bar shows as set. A superseded load waits for the newest load instead.
  function load() {
    const n = ++loads;
    pending = fetchLog(n);
    return pending;
  }

  async function fetchLog(n) {
    const key = P.viewKey(), before = log;
    const body = { ...P.about(), seed: SEED, steps: STEPS, breakpoints: [...marks].filter(exists), break_on_refusal: $("break-refusal").checked };
    const mine = P.ticket("run-log", () => JSON.stringify([[...marks].filter(exists), $("break-refusal").checked]));
    const later = () => (n !== loads ? pending : load()); // the newest load, or one for what is on show now
    let answer;
    try {
      answer = await P.api("/api/play/run", body);
    } catch (error) {
      if (mine.current()) throw error;
      return later(); // a refusal of an earlier question is not this one's
    }
    if (!mine.current()) return later();
    log = answer;
    if (!before || before.model !== log.model || logKey !== key) pos = 0;
    logKey = key;
    $("debug-limits").textContent = `Seed ${log.seed}, ${log.steps} steps. ` + log.limits.join(" ");
  }

  async function ready() {
    if (!log || logKey !== P.viewKey()) await load();
  }

  // `pos` counts entries of the trace; a stop names the run's step number. They differ when a turn logs nothing (a
  // user who may not start a record, with none to work on, ADR-0231), so a stop is found by the entry's own step.
  // `ready()`, with Stop enabled while the log loads (it cancels the run), for the newest Run or Step only.
  async function waiting(mine) {
    if (log && logKey === P.viewKey()) return;
    loading = true;
    buttons();
    try { await ready(); } finally { if (mine === generation) { loading = false; buttons(); } }
  }

  const stepOf = (n) => (log && n > 0 && n <= log.trace.length ? log.trace[n - 1].step : 0);
  const stopAt = (n) => log && log.stops.find((s) => s.step === stepOf(n));

  function stopText(stop) {
    if (stop.reason === "exception") return stop.elements[0].startsWith("state:")
      ? `the kernel refused ${stop.action || "an action"} from ${name(stop.elements[0])} (${stop.code})` : `the kernel refused ${name(stop.elements[0])} (${stop.code})`;
    return "breakpoint on " + stop.elements.map(name).join(", ");
  }

  // Run: move one step at a time at the chosen speed until a stop or the end. With reduced motion, or at the
  // fastest speed, go straight there.
  async function run() {
    if (mode === "running") return;
    const mine = ++generation;
    try {
      if (mode === "ended") { pos = 0; P.clearSim(); }
      await waiting(mine);
    } catch (error) { return mine === generation ? failed(error) : undefined; }
    if (mine !== generation || !log) return; // stopped, restarted, pressed again or redrawn while the log loaded
    yieldSimulate();
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

  // The diagram shows one run at a time. Run and Step take it from a Simulate result on show (its panel would claim
  // totals the diagram no longer shows); a Simulate result shown takes it from the run bar, which ends its run.
  function yieldSimulate() {
    if (!$("sim").hidden) P.clearSim();
  }

  function simulated() {
    if (mode === "idle") return;
    generation += 1;
    loading = false;
    clearTimeout(timer);
    mode = "idle";
    pos = 0;
    stopNote = "";
    P.restyle("initial-edge", {}); // Simulate repaints every state and transition; the run's mark on the start is the one left
    render("Ended the run: the diagram shows Simulate's run");
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
    const mine = ++generation;
    try { await waiting(mine); } catch (error) { return mine === generation ? failed(error) : undefined; }
    if (mine !== generation || !log) return;
    yieldSimulate();
    mode = "paused";
    stopNote = "";
    advance();
    render();
  }

  async function stop() {
    generation += 1;
    loading = false;
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
    generation += 1;
    loading = false;
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
      if (e.outcome === "REFUSED") { // a slip (an action that does not leave the record's state) names no transition
        if (e.transition) { const r = transitions[e.transition].refused; r[e.code] = (r[e.code] || 0) + 1; }
        continue;
      }
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
      else if (now.outcome === "CREATED") P.restyle("initial-edge", { strokeColor: NOW, strokeWidth: 4 });
      P.restyle("state:" + at, { strokeColor: colour, strokeWidth: 4, fillColor: "#fff6d6" }, graph.getDataModel().getCell("state:" + at).value);
    });
    const here = now.outcome === "REFUSED" ? now.from : now.to; // keep the current step on screen with the panel open
    if (P.follow) P.follow(["state:" + here, now.transition ? "transition:" + now.transition : "initial"]);
    $("debug-pos").textContent = `Step ${now.step} of ${log.steps}`;
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
    const first = Math.max(0, pos - 40);
    $("debug-log").replaceChildren(...log.trace.slice(first, pos).map((e, k) => {
      const at = first + k + 1; // this entry's place in the trace, which is what `pos` counts
      const li = P.el("li", undefined, { class: e.outcome.toLowerCase() + (at === pos ? " current" : "") });
      const pick = P.el("button", describe(e), { type: "button", class: "link trace-step", "aria-label": `Inspect recorded step ${e.step}: ${describe(e)}` });
      pick.addEventListener("click", () => {
        clearTimeout(timer); mode = "paused"; pos = at; stopNote = "inspecting recorded step"; render();
      });
      li.append(P.el("span", String(e.step), { class: "n" }), pick);
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
    if (mode === "running") return `Running · step ${stepOf(pos)} of ${log.steps}`;
    if (mode === "ended") return `Finished · ${log.steps} steps`;
    return `Paused at step ${stepOf(pos)}` + (stopNote && stopNote !== "paused" ? `: ${stopNote}` : "");
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
      if (e.outcome === "REFUSED" && e.transition) {
        const inspect = P.el("button", "Inspect the refused transition", { type: "button", class: "quiet small" });
        inspect.addEventListener("click", () => { pause(); P.showTab("states"); P.select("transition:" + e.transition, true); });
        const laws = P.el("button", "Inspect its laws", { type: "button", class: "quiet small" });
        laws.addEventListener("click", () => { pause(); if (window.PlayLaws) window.PlayLaws.showFor("transition:" + e.transition); else P.showTab("laws"); });
        const tools = P.el("dd", undefined, { class: "trace-tools" }); tools.append(inspect, laws); dl.append(P.el("dt", "Investigate"), tools);
      }
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
    $("run-stop").disabled = idle && !loading && !appRunning();
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
    if (!id.startsWith("state:") && !id.startsWith("transition:")) return; // a breakpoint is on a state or a transition, never an actor
    const on = marks.has(id), b = P.el("button", on ? "Remove breakpoint" : "Add breakpoint", { type: "button", class: "quiet", "aria-keyshortcuts": "F9" });
    b.title = id.startsWith("state:") ? "Stop the run when a record enters this state (F9)" : "Stop the run when someone tries this transition (F9)";
    b.addEventListener("click", () => toggle(id));
    const tools = P.el("div", undefined, { class: "draft-tools" });
    tools.append(b);
    box.append(tools);
  }

  // A redraw means another model is on screen (a plan previewed or left): start again, keeping breakpoints that exist.
  function redrawn() {
    generation += 1;
    loading = false;
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
    document.addEventListener("playide:simulated", simulated);
    render();
  }

  if (window.PlayIDE) init(window.PlayIDE);
})();
