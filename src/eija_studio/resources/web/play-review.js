// PlayIDE Review (ADR-0175): review a change as a UML diff you can run, instead of reading a pull request.
// The server compares the model in force with the one shown (a change case's candidate and any previewed plan): what
// changed, how risky each change is by fixed rules, and what the kernel does differently when every fixture actor
// tries every action on both models. The page asks the reviewer to predict before it shows the kernel's answer, and
// a change can be marked as looking right only after it has been looked at on the diagram and its question answered.
// Nothing here saves, approves or applies anything; points reward checking, as in the checks ring (ADR-0157).
"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  const RISK_TEXT = { high: "High risk", medium: "Medium", low: "Low" };
  const CHANGE_TEXT = { added: "added", removed: "removed", changed: "changed", unreachable: "knock-on", dead_end: "knock-on" };
  const reviews = new Map(); // one review per change shown, so going back to a change keeps what was checked
  let ide = null, review = null, graph = null, focusTimer = 0, shownKey = null;

  const el = (...args) => ide.el(...args);
  const keyOf = (about) => JSON.stringify([about.case_id, about.plan]);

  // The diagram: both models on one canvas, drawn by the shared change renderer (play-diff.js, ADR-0176) from the
  // server's union of the two. Removed elements stay as ghosts, so a deleted path is seen, not missed; states nobody
  // edited but the change affects (knock-on items) are tinted amber. The lenses (Before, Changes, After, onion skin)
  // stay off here: the review asks about one picture of the change.
  function draw(r) {
    if (graph) graph.destroy();
    const knock = r.items.filter((i) => !i.edited).flatMap((i) => i.states);
    graph = window.PlayDiff.mount($("review-canvas"), r.ghost, { direction: "TB", knockOn: knock }).graph; // the review canvas is tall
    fit();
  }

  function fit() {
    if (!graph) return;
    const plugin = graph.getPlugin("fit");
    plugin.maxFitScale = 1.2;
    plugin.fitCenter({ margin: 24 });
  }

  function cellsOf(item) { // the renderer keys a transition by its side: t:<id> as it is now, was:<id> as it was
    const id = item.element.startsWith("transition:") ? item.element.slice(11) : null;
    const ids = id ? (item.change === "removed" ? ["was:" + id] : ["t:" + id, "was:" + id])
      : item.element === "initial" ? ["initial-edge", "was:initial-edge"] : [item.element];
    return ids.map((id) => graph.getDataModel().getCell(id)).filter(Boolean);
  }

  // Show me: select and pulse the item's element. Looking is what unlocks the verdict, and the first look earns a point.
  function showItem(item) {
    const cells = cellsOf(item);
    if (cells.length) {
      graph.setSelectionCells(cells);
      clearTimeout(focusTimer);
      $("review-canvas").classList.add("focus");
      focusTimer = setTimeout(() => $("review-canvas").classList.remove("focus"), 900);
    }
    const state = review.state[item.n];
    if (!state.looked) {
      state.looked = true;
      ide.earn(1, `Looked at change ${item.n} on the diagram`);
    }
    render();
  }

  function predict(item, answer) {
    const state = review.state[item.n];
    if (state.predicted) return;
    state.predicted = answer;
    if (answer === item.question.answer) ide.earn(2, `Predicted what the kernel does for change ${item.n}`);
    render();
  }

  function verdict(item, value) {
    const state = review.state[item.n];
    state.verdict = state.verdict === value ? null : value;
    render();
    if (value === "concern" && state.verdict) setTimeout(() => { const note = document.querySelector(`#review-item-${item.n} textarea`); if (note) note.focus(); }, 0);
  }

  const ready = (item) => review.state[item.n].looked && (!item.question || review.state[item.n].predicted);

  function rowsOf(item) { return review.result.behaviour.rows.filter((r) => item.rows.includes(r.n)); }

  const outcome = (o) => o.outcome === "NO_STATE" ? "no such state" : o.outcome === "REFUSED" ? `refused (${o.code})`
    : `→ ${o.to}` + (o.effects.length ? ` · ${o.effects.join(", ")}` : "");

  function behaviourList(rows) {
    const list = el("ul", undefined, { class: "review-rows" });
    for (const r of rows) {
      const li = el("li"), allowed = (o) => o.outcome === "COMMITTED", what = el("span");
      what.append(el("strong", `${r.role} tries ${r.action} in ${r.state}`), el("span", ` (${r.actors.join(", ")})`, { class: "muted small" }),
        el("br"), document.createTextNode("before " + outcome(r.before)), el("br"), document.createTextNode("after " + outcome(r.after)));
      li.append(what, el("span", `${allowed(r.before) ? "allowed" : "refused"} → ${allowed(r.after) ? "allowed" : "refused"}`,
        { class: "flip " + (allowed(r.after) ? "now-ok" : "now-refused") }));
      list.append(li);
    }
    return list;
  }

  function itemCard(item) {
    const state = review.state[item.n], li = el("li", undefined, { id: `review-item-${item.n}`, class: `review-item risk-${item.risk}` + (state.verdict ? " " + state.verdict : "") });
    const head = el("div", undefined, { class: "review-item-head" });
    head.append(el("span", RISK_TEXT[item.risk], { class: "risk " + item.risk }), el("span", CHANGE_TEXT[item.change], { class: "change " + item.change }),
      el("strong", item.text));
    const show = el("button", state.looked ? "Shown ✓" : "Show me", { type: "button", class: "quiet show" });
    show.addEventListener("click", () => showItem(item));
    head.append(show);
    li.append(head);
    if (!item.edited) li.append(el("p", "Nobody edited this directly: it follows from the changes above.", { class: "muted small" }));
    const reasons = el("ul", undefined, { class: "reasons" });
    for (const reason of item.reasons) reasons.append(el("li", reason));
    li.append(reasons);
    if (item.question) {
      const q = el("div", undefined, { class: "predict" });
      q.append(el("p", "Predict, then run: " + item.question.text, { class: "q" }));
      if (!state.predicted) {
        const tools = el("div", undefined, { class: "predict-tools" });
        for (const answer of ["yes", "no"]) {
          const b = el("button", answer === "yes" ? "Yes" : "No", { type: "button" });
          b.addEventListener("click", () => predict(item, answer));
          tools.append(b);
        }
        q.append(tools);
      } else {
        const right = state.predicted === item.question.answer;
        q.append(el("p", (right ? "✓ Right. " : "✗ Not what you expected. Worth a second look. ") + item.question.because, { class: right ? "answer ok" : "answer surprised" }));
      }
      li.append(q);
    }
    const rows = rowsOf(item);
    if (rows.length && (state.predicted || !item.question)) {
      li.append(el("p", `What the kernel does differently (${rows.length}):`, { class: "small rows-title" }), behaviourList(rows));
    } else if (!rows.length) {
      li.append(el("p", "No fixture actor's attempt turns out differently because of this change.", { class: "muted small" }));
    }
    const tools = el("div", undefined, { class: "verdict-tools" });
    const ok = el("button", "Looks right", { type: "button", "aria-pressed": String(state.verdict === "ok") });
    const concern = el("button", "Needs a change", { type: "button", "aria-pressed": String(state.verdict === "concern") });
    ok.disabled = concern.disabled = !ready(item);
    if (!ready(item)) ok.title = concern.title = item.question ? "Look at it on the diagram and answer the question first" : "Look at it on the diagram first";
    ok.addEventListener("click", () => verdict(item, "ok"));
    concern.addEventListener("click", () => verdict(item, "concern"));
    tools.append(ok, concern);
    if (!ready(item)) tools.append(el("span", item.question ? "Show it and answer the question to decide." : "Show it to decide.", { class: "muted small" }));
    li.append(tools);
    if (state.verdict === "concern") {
      const label = el("label", "What should change?", { class: "small" }), note = el("textarea", undefined, { rows: "2", maxlength: "500" });
      note.value = state.note || "";
      note.addEventListener("input", () => { state.note = note.value; });
      label.append(note);
      li.append(label);
    }
    return li;
  }

  function simulationLine(sim) {
    const p = el("p", undefined, { class: "small" });
    p.append(el("strong", "Seeded simulation "), document.createTextNode(`(seed ${sim.seed}, ${sim.steps} steps, on both models): `
      + `went through ${sim.before.committed} → ${sim.after.committed}, refused ${sim.before.refused} → ${sim.after.refused}.`));
    if (sim.new_findings.length) p.append(document.createTextNode(" New: " + sim.new_findings.join("; ") + "."));
    if (sim.gone_findings.length) p.append(document.createTextNode(" Gone: " + sim.gone_findings.join("; ") + "."));
    return p;
  }

  function progress() {
    const items = review.result.items, decided = items.filter((i) => review.state[i.n].verdict);
    const concerns = items.filter((i) => review.state[i.n].verdict === "concern").length;
    const predicted = items.filter((i) => i.question && review.state[i.n].predicted), right = predicted.filter((i) => review.state[i.n].predicted === i.question.answer);
    return { items, decided: decided.length, concerns, predicted: predicted.length, right: right.length };
  }

  function render() {
    const r = review.result, box = $("review-items");
    const p = progress();
    $("review-progress").textContent = `${p.decided} of ${p.items.length} decided` + (p.concerns ? ` · ${p.concerns} need a change` : "")
      + (p.predicted ? ` · ${p.right} of ${p.predicted} predictions right` : "");
    $("review-finish").disabled = review.finished || p.decided < p.items.length;
    $("review-finish").textContent = review.finished ? "Review finished" : "Finish review";
    $("review-finish").title = p.decided < p.items.length ? "Decide every change first" : "";
    box.replaceChildren(...r.items.map(itemCard));
    if (review.finished) summary();
  }

  function markdown() {
    const r = review.result, p = progress(), shown = ide.about();
    const lines = [`# Review: ${p.concerns ? `changes requested (${p.concerns})` : "looks right"}`, "",
      `- Pack: ${r.pack}`, `- Before: \`${r.before.slice(0, 16)}\``, `- After: \`${r.after.slice(0, 16)}\``,
      `- Change: ${shown.case_id ? `change case ${shown.case_id}` : "a chat plan previewed in PlayIDE"}${shown.plan ? ` with ${shown.plan.length} plan step(s)` : ""}`,
      `- Behaviour: ${r.behaviour.attempts} kernel attempts, ${r.behaviour.rows.length} turned out differently`,
      `- Predictions: ${p.right} of ${p.predicted} right`, "", "## Changes", ""];
    for (const item of r.items) {
      const s = review.state[item.n];
      lines.push(`${item.n}. **${s.verdict === "ok" ? "Looks right" : "Needs a change"}** (${RISK_TEXT[item.risk].toLowerCase()}, ${CHANGE_TEXT[item.change]}): ${item.text}`);
      for (const reason of item.reasons) lines.push(`   - ${reason}`);
      if (item.question) lines.push(`   - Predicted ${s.predicted}; the kernel says ${item.question.answer}.`);
      if (s.note) lines.push(`   - Reviewer: ${s.note.replace(/\n/g, " ")}`);
    }
    lines.push("", "## What the kernel does differently", "", ...(r.behaviour.rows.length ? r.behaviour.rows.map((row) => `- ${row.text}`) : ["- Nothing."]),
      "", "## Limits", "", ...r.limits.map((l) => `- ${l}`), "");
    return lines.join("\n");
  }

  function summary() {
    const p = progress(), box = $("review-summary"), text = markdown();
    box.hidden = false;
    box.replaceChildren();
    box.append(el("h3", p.concerns ? `Changes requested: ${p.concerns} of ${p.items.length}` : `Every change looks right (${p.items.length})`),
      el("p", ide.about().case_id
        ? "This review is your record of what you checked. Approving and applying the change stays with the owner in the review workbench, after its evidence is verified."
        : "This review is your record of what you checked. A previewed plan is not saved: to make it real it becomes a change case, approved by the owner in the review workbench.", { class: "muted small" }));
    const tools = el("div", undefined, { class: "verdict-tools" });
    const download = el("a", "Download review.md", { class: "quiet", download: "review.md", href: URL.createObjectURL(new Blob([text], { type: "text/markdown" })) });
    tools.append(download, el("a", "Open the review workbench", { class: "quiet", href: "/" }));
    box.append(tools, el("pre", text, { class: "review-md" }));
  }

  function finish() {
    if (review.finished) return;
    review.finished = true;
    const p = progress();
    if (p.items.some((i) => i.risk === "high")) ide.earn(2, "Finished a review that decided every high-risk change");
    render();
    $("review-summary").scrollIntoView({ block: "nearest" });
  }

  function empty(text) {
    if (graph) { graph.destroy(); graph = null; }
    $("review").dataset.empty = "true";  // nothing beside the message: it takes the whole tab
    $("review-canvas").replaceChildren(el("p", text, { class: "muted empty" }));
    $("review-items").replaceChildren();
    $("review-head-text").textContent = "Nothing to review";
    $("review-progress").textContent = "";
    $("review-sim").replaceChildren();
    $("review-finish").disabled = true;
    $("review-finish").textContent = "Finish review";
    $("review-summary").hidden = true;
    shownKey = null;
  }

  async function show() {
    const about = ide.about();
    if (!about.case_id && !about.plan) {
      empty("No change to review. Ask the chat for a change or draw one, then preview it; or open a change case from the review workbench.");
      review = null;
      return;
    }
    // Always ask the server: it refuses (MODEL_CHANGED) a model edited elsewhere since the page loaded, so a review is
    // never shown or written for an obsolete change. What was checked is kept per exact pair of models.
    delete $("review").dataset.empty;
    $("review-head-text").textContent = "Running both models through the kernel…";
    let result;
    try {
      result = await ide.api("/api/play/review", about);
    } catch (error) {
      empty(error.code === "MODEL_CHANGED" ? "The model changed since this page loaded. Reload to review the current change."
        : `The review could not run (${error.code || "ERROR"}): ${error.message}`);
      return;
    }
    if (keyOf(ide.about()) !== keyOf(about)) return; // the change shown moved on while the kernel ran
    const key = keyOf(about) + result.before + result.after;
    if (!reviews.has(key)) reviews.set(key, { result, state: Object.fromEntries(result.items.map((i) => [i.n, { looked: false, predicted: null, verdict: null, note: "" }])), finished: false });
    review = reviews.get(key);
    const r = review.result;
    if (!r.changed || !r.items.length) { empty("The model shown is the model in force: nothing changed."); return; }
    $("review-summary").hidden = !review.finished;
    $("review-head-text").textContent = `${r.items.length} change${r.items.length === 1 ? "" : "s"}: ${r.risk.high} high risk, ${r.risk.medium} medium, ${r.risk.low} low · `
      + `${r.behaviour.rows.length} kernel outcome${r.behaviour.rows.length === 1 ? " differs" : "s differ"} in ${r.behaviour.attempts} attempts`;
    $("review-sim").replaceChildren(simulationLine(r.simulation));
    const fresh = shownKey !== key;
    shownKey = key;
    draw(r);
    render();
    if (fresh) $("review-items").parentElement.scrollTop = 0; // a different change starts at its riskiest item
  }

  window.PlayReview = {
    init(hooks) {
      ide = hooks;
      $("review-finish").addEventListener("click", finish);
    },
    show,
    graph: () => graph,
    fit,
  };
})();
