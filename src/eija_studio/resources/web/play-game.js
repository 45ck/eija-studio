// PlayIDE game layer (ADR-0208): motion and feedback that make checking the model satisfying. It awards nothing and
// decides nothing. Every moment it draws comes from an event play.js or the run bar sends after a real result: a check
// on the checks ring passing or going stale, points play.js awarded for checking (ADR-0157), or a step the kernel
// decided in a simulation or a run. Without that result there is no moment.
"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  const NS = "http://www.w3.org/2000/svg";
  const GO = "#17734a", REFUSED = "#a12f2f", NOW = "#3157d5";
  // What to press next for each check, in the order a person usually goes. The button is the page's own control.
  const NEXT = {
    ai: { say: "Look at each AI step on the diagram: press Show me on the plan's steps.", button: null },
    screens: { say: "Fix the screens the design check flags.", button: null, tab: "screens" },
    ripple: { say: "Look at what the change does to the other diagrams in the plan's ripple.", button: null },
    conformance: { say: "Build & run checks the app against the kernel on this view.", button: "build", label: "Build & run" },
    simulated: { say: "Simulate sends seeded users through the kernel on this view.", button: "simulate", label: "Simulate" },
  };
  const STALE = { conformance: "build", simulated: "simulate" }; // the checks a button re-runs
  let P = null, shownChecks = null, live = false, last = null, readyFor = null, pop = null, flowTimer = 0;
  const everPassed = new Set(); // checks that passed on some view in this page, so a stale one is worth a nudge

  const still = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

  // A short note that rises from the ring: what just passed, or what was earned. It is also read out (role=status).
  function note(text, kind) {
    if (!pop) return;
    const item = document.createElement("span");
    item.className = "game-note " + kind;
    item.textContent = text;
    pop.append(item);
    while (pop.children.length > 3) pop.firstChild.remove();
    setTimeout(() => item.remove(), still() ? 4000 : 3200);
  }

  function flash(element, cls) {
    if (!element || still()) return;
    element.classList.remove(cls);
    void element.getBoundingClientRect(); // restart the animation
    element.classList.add(cls);
    element.addEventListener("animationend", () => element.classList.remove(cls), { once: true });
  }

  // The checks changed. A part that now passes pops and says so; a part that passed on this view's last state and no
  // longer does drains, and the button that runs it again glows until it is run. Every check passing on a view is
  // the one big moment, once per view.
  function checks(event) {
    const { checks: now, key } = event.detail, health = $("health"), ring = $("health-ring");
    const all = now.every((c) => c.ok);
    for (const c of now) if (c.ok) everPassed.add(c.id);
    if (live && last && last.key === key) {
      now.forEach((c, i) => {
        const was = last.checks.find((x) => x.id === c.id);
        if (!was || was.ok === c.ok || !c.ok) return;
        flash(ring && ring.children[i], "game-pop");
        if (!was.detail.endsWith("…")) note(`✓ ${c.name}. ${c.detail}`, "pass"); // not for a check that was only still working
      });
    } else if (live && last) { // the view changed: the build and the simulation were of something else
      const lost = now.filter((c) => !c.ok && STALE[c.id] && last.checks.some((x) => x.id === c.id && x.ok));
      if (lost.length) {
        flash(health, "game-drain");
        note(`Changed since the last ${lost.map((c) => (c.id === "conformance" ? "build" : "simulation")).join(" and ")}: run ${lost.length > 1 ? "them" : "it"} again`, "stale");
      }
    }
    for (const [id, button] of Object.entries(STALE)) {
      const c = now.find((x) => x.id === id), b = $(button);
      if (b) b.classList.toggle("game-stale", Boolean(c && !c.ok && everPassed.has(id)));
    }
    health.classList.toggle("game-ready", all);
    if (all && readyFor !== key) {
      readyFor = key;
      if (live) { // not on load: only a check the person ran makes the moment
        flash(health, "game-burst");
        note(event.detail.plan ? "Every check passes on this change" : "Every check passes on this model", "ready");
      }
    }
    if (!all && readyFor === key) readyFor = null;
    last = { key, checks: now.map((c) => ({ id: c.id, ok: c.ok, detail: c.detail })) };
    nextCheck(now);
  }

  // The checks panel says which check to run next, with the page's own button for it where there is one.
  function nextCheck(now) {
    const box = $("check-next");
    if (!box) return;
    shownChecks = now;
    if (missing && missing.items.length) { // a new system's gaps come before its checks
      box.className = "check-next";
      box.replaceChildren(P.el("strong", `Next (${missing.items.length} missing): `), document.createTextNode(missing.items[0].text));
      return;
    }
    const todo = now.find((c) => !c.ok);
    if (!todo) {
      box.className = "check-next done";
      box.replaceChildren(P.el("strong", "Ready."), document.createTextNode(" Every check passes on what you are looking at. Any change empties the build and simulation parts again."));
      return;
    }
    const next = NEXT[todo.id] || { say: todo.detail };
    box.className = "check-next";
    box.replaceChildren(P.el("strong", "Next: "), document.createTextNode(next.say + " "));
    if (next.button && $(next.button) && !$(next.button).disabled && !$(next.button).hidden) {
      const go = P.el("button", next.label, { type: "button", class: "quiet small" });
      go.addEventListener("click", () => $(next.button).click());
      box.append(go);
    } else if (next.tab) {
      const go = P.el("button", "Open Screens", { type: "button", class: "quiet small" });
      go.addEventListener("click", () => P.showTab(next.tab));
      box.append(go);
    }
  }

  function earned(event) {
    const { n, why, kind } = event.detail;
    flash($("health"), "game-bump");
    if (kind === "caught") {
      note(`Caught it: ${why.replace(/^Caught /, "")} (+${n})`, "caught");
      const card = document.querySelector("#chat-log .plan:last-of-type");
      flash(card, "game-caught");
    } else {
      note(`+${n} ${why}`, "earn");
    }
  }

  // Traffic on the state machine. A step the kernel decided sends a dot along its transition: green when it went
  // through, red when the kernel stopped it, halfway, with a cross. A try from a state the transition does not leave
  // flashes the record's state instead. The dot follows the drawn edge, sampled when it starts.
  function overlay() {
    const graph = P.graph();
    return graph && graph.getView && graph.getView().getOverlayPane ? graph.getView().getOverlayPane() : null;
  }

  function track(cellId) {
    const graph = P.graph(), cell = graph && graph.getDataModel().getCell(cellId);
    const state = cell && graph.getView().getState(cell);
    const node = state && state.shape && state.shape.node;
    if (!node) return null;
    let best = null, most = 0;
    for (const path of node.querySelectorAll("path, polyline")) {
      const length = path.getTotalLength ? path.getTotalLength() : 0;
      if (length > most) { most = length; best = path; }
    }
    if (!best || most < 4) return null;
    const points = [];
    for (let i = 0; i <= 24; i += 1) { const p = best.getPointAtLength((most * i) / 24); points.push([p.x, p.y]); }
    return points;
  }

  function centre(cellId) {
    const graph = P.graph(), cell = graph && graph.getDataModel().getCell(cellId);
    const state = cell && graph.getView().getState(cell);
    return state ? [state.getCenterX(), state.getCenterY(), state.width, state.height] : null;
  }

  function at(points, f) {
    const x = Math.max(0, Math.min(1, f)) * (points.length - 1), i = Math.min(points.length - 2, Math.floor(x)), t = x - i;
    return [points[i][0] + (points[i + 1][0] - points[i][0]) * t, points[i][1] + (points[i + 1][1] - points[i][1]) * t];
  }

  function shape(tag, attrs) {
    const node = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, String(v));
    node.setAttribute("class", "game-traffic " + (attrs.class || ""));
    return node;
  }

  function ripple(pane, x, y, colour, r = 18) {
    const ring = shape("circle", { cx: x, cy: y, r: 4, fill: "none", stroke: colour, "stroke-width": 2.5 });
    pane.append(ring);
    const start = performance.now(), ms = 520;
    const frame = (t) => {
      const f = Math.min(1, (t - start) / ms);
      ring.setAttribute("r", String(4 + r * f));
      ring.setAttribute("opacity", String(1 - f));
      if (f < 1) requestAnimationFrame(frame); else ring.remove();
    };
    requestAnimationFrame(frame);
  }

  function cross(pane, x, y) {
    const mark = shape("g", { class: "game-cross", transform: `translate(${x} ${y})` });
    mark.append(shape("circle", { r: 8, fill: REFUSED, stroke: "#fff", "stroke-width": 1.5 }),
      shape("path", { d: "M-3.2-3.2L3.2 3.2M3.2-3.2L-3.2 3.2", stroke: "#fff", "stroke-width": 2, "stroke-linecap": "round" }));
    pane.append(mark);
    setTimeout(() => mark.remove(), 700);
  }

  function travel(entry, ms) {
    const pane = overlay();
    if (!pane || still() || P.tab() !== "states") return;
    const refused = entry.outcome === "REFUSED";
    const transition = entry.transition && P.model().transitions.find((t) => t.id === entry.transition);
    const leaves = transition && transition.from_state === entry.from;
    const points = entry.outcome === "CREATED" ? track("initial-edge") : leaves ? track("transition:" + transition.id) : null;
    if (!points) { // a create with no initial arrow drawn, or a try from a state the transition does not leave
      const c = centre("state:" + (entry.outcome === "CREATED" ? entry.to : entry.from));
      if (!c) return;
      if (refused) { // a small mark on the state's corner: many of these in a run must not hide the diagram
        const x = c[0] + c[2] / 2 - 6, y = c[1] - c[3] / 2 + 6;
        cross(pane, x, y);
        ripple(pane, x, y, REFUSED, 10);
      } else ripple(pane, c[0], c[1], GO, Math.max(c[2], c[3]) / 2);
      return;
    }
    const dot = token(entry, refused ? REFUSED : GO);
    pane.append(dot);
    const start = performance.now(), end = refused ? 0.5 : 1;
    const frame = (t) => {
      const f = Math.min(1, (t - start) / ms), eased = 1 - (1 - f) * (1 - f);
      const [x, y] = at(points, eased * end);
      dot.setAttribute("transform", `translate(${x.toFixed(1)} ${y.toFixed(1)})`);
      if (f < 1) { requestAnimationFrame(frame); return; }
      dot.remove();
      if (refused) { cross(pane, x, y); return; }
      const to = centre("state:" + entry.to);
      ripple(pane, x, y, entry.outcome === "CREATED" ? NOW : GO);
      if (to) flashState(entry.to);
    };
    requestAnimationFrame(frame);
  }

  // The dot's shape says who acted (ADR-0210): a circle for a person, a diamond for an AI agent, a square for a timer
  // or an external system. Its colour is the kernel's answer.
  const kindOf = (entry) => (P.roleKind && entry.role ? P.roleKind(entry.role) : "human");
  function token(entry, fill) {
    const kind = kindOf(entry), g = shape("g", {}), paint = { fill, stroke: "#fff", "stroke-width": 1.5 };
    if (kind === "agent") g.append(shape("path", { d: "M0-7.5L7.5 0 0 7.5-7.5 0z", ...paint }));
    else if (kind === "timer" || kind === "system") g.append(shape("rect", { x: -5.5, y: -5.5, width: 11, height: 11, rx: 2, ...paint }));
    else g.append(shape("circle", { r: 5.5, ...paint }));
    g.setAttribute("transform", "translate(-99 -99)");
    return g;
  }

  function flashState(name) {
    const graph = P.graph(), cell = graph.getDataModel().getCell("state:" + name);
    const state = cell && graph.getView().getState(cell);
    const node = state && state.shape && state.shape.node;
    if (node) flash(node, "game-arrive");
  }

  function stepped(event) {
    const entry = event.detail, speed = Number(($("run-speed") || {}).value || 250);
    travel(entry, Math.max(260, Math.min(900, (entry.ms || speed) * 1.4)));
  }

  // After Simulate, the first tries of the run go by as traffic, several at once: the real log, sped up.
  function simulated(event) {
    const result = event.detail;
    clearInterval(flowTimer);
    countUp();
    legend(result.by_kind || {});
    guarded(result.by_kind || {});
    if (still() || !result.trace || !result.trace.length) return;
    const shown = result.trace.slice(0, 120), key = P.viewKey();
    let i = 0;
    flowTimer = setInterval(() => {
      if (P.viewKey() !== key || $("sim").hidden) { clearInterval(flowTimer); return; } // that run was of another view
      for (let k = 0; k < 2 && i < shown.length; k += 1, i += 1) travel(shown[i], 700);
      if (i >= shown.length) clearInterval(flowTimer);
    }, 70);
  }

  // Which shape is which, shown only when the run had actors that are not people.
  function legend(kinds) {
    let line = $("game-legend");
    if (!line) {
      line = P.el("p", "", { id: "game-legend", class: "game-legend muted small" });
      $("sim-summary").after(line);
    }
    const others = Object.keys(kinds).filter((k) => k !== "human");
    line.hidden = !others.length;
    if (!others.length) return;
    const names = { agent: "◆ an AI agent", timer: "■ a timer", system: "■ an external system" };
    line.textContent = `On the diagram: ● a person, ${others.map((k) => names[k] || k).join(", ")}. Red stops where the kernel refused.`;
  }

  // An AI agent the kernel refused is the guardrail working: say how often, from the run's own counts.
  function guarded(kinds) {
    const agent = kinds.agent;
    if (!live || !agent || !agent.refused) return;
    const top = Object.entries(agent.codes || {}).sort((a, b) => b[1] - a[1])[0];
    note(`The kernel stopped AI agents ${agent.refused} time${agent.refused === 1 ? "" : "s"} in this run${top ? `, mostly ${top[0]}` : ""}`, "guard");
  }

  // The system's class diagrams (ADR-0203): a disagreement resolved is progress; none left is a moment.
  let system = null;
  function landscape(event) {
    const { warning = 0 } = event.detail || {}, pack = (P.pack() && P.pack().id) || "";
    if (system && system.pack === pack && live) {
      if (system.warning > 0 && warning === 0) { note("The system's class diagrams agree now", "ready"); flash($("health"), "game-burst"); }
      else if (warning < system.warning) note(`✓ ${system.warning - warning} disagreement${system.warning - warning === 1 ? "" : "s"} resolved, ${warning} left`, "pass");
    }
    system = { pack, warning };
  }

  // What a new system still needs (owned by the greenfield start flow): each item comes from a real check, and this
  // only marks one going away and the list emptying.
  let missing = null;
  function gaps(event) {
    const { key = "", items = [] } = event.detail || {}, ids = new Set(items.map((x) => x.id));
    if (missing && missing.key === key && live) {
      for (const was of missing.items) if (!ids.has(was.id)) note(`✓ ${was.text}`, "pass");
      if (missing.items.length && !items.length) { note("Nothing missing: ready to build", "ready"); flash($("health"), "game-burst"); }
    }
    missing = { key, items: items.map((x) => ({ id: x.id, text: x.text })) };
    if (shownChecks) nextCheck(shownChecks);
  }

  // The simulation's counts count up, so the result lands rather than appears.
  function countUp() {
    if (still()) return;
    for (const strong of $("sim-summary").querySelectorAll("strong")) {
      const target = Number(strong.textContent);
      if (!Number.isFinite(target) || target < 2) continue;
      const start = performance.now(), ms = 900;
      const frame = (t) => {
        const f = Math.min(1, (t - start) / ms);
        strong.textContent = String(Math.round(target * (1 - (1 - f) ** 3)));
        if (f < 1) requestAnimationFrame(frame); else strong.textContent = String(target);
      };
      requestAnimationFrame(frame);
    }
  }

  function init() {
    if (P || !window.PlayIDE || !window.PlayIDE.graph) return;
    P = window.PlayIDE;
    pop = document.createElement("div");
    pop.id = "game-notes";
    pop.className = "game-notes";
    pop.setAttribute("role", "status");
    pop.setAttribute("aria-live", "polite");
    $("health").closest(".checks-anchor").append(pop);
    const next = P.el("p", "", { id: "check-next", class: "check-next" });
    $("check-list").before(next);
    document.addEventListener("playide:simulated", simulated);
    $("sim-replay").addEventListener("click", () => clearInterval(flowTimer));
    document.dispatchEvent(new CustomEvent("playide:game"));
  }

  // Listen from the start: play.js renders the checks before it says it is ready.
  document.addEventListener("playide:checks", (event) => { init(); if (P) checks(event); });
  document.addEventListener("playide:earn", (event) => { init(); if (P) earned(event); });
  document.addEventListener("playide:step", (event) => { init(); if (P) stepped(event); });
  document.addEventListener("playide:landscape", (event) => { init(); if (P) landscape(event); });
  document.addEventListener("playide:missing", (event) => { init(); if (P) gaps(event); });
  document.addEventListener("playide:ready", () => { init(); live = true; });
})();
