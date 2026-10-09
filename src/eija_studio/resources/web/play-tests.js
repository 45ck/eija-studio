// PlayIDE Tests tab (ADR-0177): the pack's scenarios, its test cases, each step run by the kernel on the model on
// screen. A failing step is shown on the state machine. Tests can be added by trying steps (the kernel answers each)
// or by editing scenarios.json as a draft; nothing is saved from here, and the draft file can be downloaded.
"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  const BADGE = { PASS: "Pass", FAIL: "Fail", NOT_RUN: "Not run" };
  const OK = { strokeColor: "#1f7a4d", strokeWidth: 3 };
  const BAD = { strokeColor: "#a12f2f", strokeWidth: 3.5, dashed: 0 };
  let P = null, report = null, key = null, draft = null, download = null, steps = [];

  const now = () => P.viewKey() + JSON.stringify(P.model()) + JSON.stringify(draft);
  const document_ = () => draft || (report && report.file.document);
  const said = (then) => (then.state ? `moves to ${then.state}` : `is refused (${then.refused})`);
  const who = (step) => step.role ? `${step.actor} (${step.role})` : step.actor;

  function showOnDiagram(result) {
    const changes = $("show-changes"); // the Changes view hides the canvas: leave it, or the painted path is never seen
    if (changes && changes.getAttribute("aria-pressed") === "true") changes.click();
    P.showTab("states");
    P.clearSim();
    P.graph().batchUpdate(() => {
      result.steps.forEach((step, i) => {
        if (step.status === "NOT_RUN") return;
        const style = step.status === "PASS" ? OK : BAD;
        // A failing step is drawn from where the passing steps left off: its transition and where it ended up.
        const cells = step.status === "FAIL" && step.cells.length > 1 ? step.cells.filter((id) => id !== "state:" + step.from) : step.cells;
        for (const id of cells) P.restyle(id, id.startsWith("state:") ? { ...style, strokeWidth: 2.5 } : style,
          id.startsWith("transition:") ? `${i + 1}. ${step.action}` : undefined);
      });
    });
    P.fit();
  }

  function stepLine(step, i) {
    const mark = { PASS: "✓", FAIL: "✗", NOT_RUN: "·" }[step.status];
    const line = P.el("li", undefined, { class: "test-step " + step.status.toLowerCase() });
    line.append(P.el("span", mark, { class: "mark", "aria-hidden": "true" }),
      P.el("span", `When ${who(step)} takes ${step.action}, it ${said(step.expect)}`));
    if (step.status === "FAIL") line.append(P.el("p", `Step ${i + 1} failed: ${step.why}`, { class: "small test-why" }));
    return line;
  }

  function card(result) {
    const status = result.status || "NOT_RUN";
    const item = P.el("li", undefined, { class: "law test " + { PASS: "holds", FAIL: "broken", NOT_RUN: "unknown" }[status] });
    const head = P.el("div", undefined, { class: "law-head" });
    head.append(P.el("span", BADGE[status], { class: "law-badge" }), P.el("span", result.title, { class: "law-text" }));
    item.append(head);
    if (!result.steps) return item;
    const story = P.el("ol", undefined, { class: "test-story" });
    story.append(P.el("li", `Given a new record in ${result.start}`, { class: "test-given" }), ...result.steps.map(stepLine));
    item.append(story);
    if (status === "FAIL" && result.failed_step === null) item.append(P.el("p", result.why, { class: "small test-why" }));
    const tools = P.el("div", undefined, { class: "law-tools" });
    const show = P.el("button", "Show on diagram", { type: "button", class: "quiet" });
    show.addEventListener("click", () => showOnDiagram(result));
    tools.append(show);
    if (draft) {
      const remove = P.el("button", "Remove", { type: "button", class: "quiet" });
      remove.addEventListener("click", () => { setDraft({ ...draft, scenarios: draft.scenarios.filter((s) => s.id !== result.id) }); });
      tools.append(remove);
    }
    item.append(tools);
    return item;
  }

  function summary() {
    if (report.status === "REFUSED") return ["bad", `The kernel refuses this model, so no test runs (${report.policy.join(", ")}).`];
    if (report.status === "EMPTY") return ["", "This pack has no tests yet. Press New test to add one."];
    const total = report.passed + report.failed;
    return report.failed ? ["bad", `${report.failed} of ${total} tests fail on the model shown. Show one on the diagram to see where.`]
      : ["ok", `All ${total} tests pass on the model shown: every step does what its scenario says.`];
  }

  function render() {
    if (!report) return;
    const [tone, text] = summary();
    $("tests-summary").className = "laws-summary " + tone;
    $("tests-summary").textContent = text;
    $("tests-file").textContent = report.file.path;
    $("tests-draft").hidden = !draft;
    if (download) URL.revokeObjectURL(download);
    download = draft ? URL.createObjectURL(new Blob([JSON.stringify(draft, null, 2) + "\n"], { type: "application/json" })) : null;
    $("tests-download").hidden = !download;
    if (download) $("tests-download").href = download;
    $("tests-list").replaceChildren(...report.scenarios.map(card));
    if ($("tests-editor").hidden) $("tests-source").value = JSON.stringify(document_(), null, 2);
    fillRecorder();
  }

  async function run() {
    const asked = now();
    $("tests-run").disabled = true;
    $("tests-summary").className = "laws-summary";
    $("tests-summary").textContent = "Running every test through the kernel…";
    try {
      const result = await P.api("/api/play/tests", draft ? { ...P.about(), scenarios: draft } : P.about());
      if (asked !== now()) return;
      report = result;
      key = asked;
      $("tests-problems").textContent = "";
      render();
    } catch (error) {
      const target = error.code === "SCENARIOS_INVALID" || error.code === "SCENARIOS_PACK_MISMATCH" ? "tests-problems" : "tests-summary";
      $(target).textContent = `Could not run the tests (${error.code || "ERROR"}): ${error.message}`;
      $("tests-summary").className = "laws-summary bad";
    } finally {
      $("tests-run").disabled = false;
    }
  }

  function setDraft(next) {
    draft = next;
    $("tests-source").value = JSON.stringify(next, null, 2);
    run();
  }

  // ---- the file editor -------------------------------------------------------------------------------------------

  function toggle(panel, button) {
    const open = $(panel).hidden;
    $(panel).hidden = !open;
    $(button).setAttribute("aria-expanded", String(open));
    return open;
  }

  function tryDraft() {
    let parsed;
    try {
      parsed = JSON.parse($("tests-source").value);
    } catch (error) {
      $("tests-problems").textContent = `The draft is not JSON: ${error.message}`;
      return;
    }
    setDraft(parsed);
  }

  // ---- the recorder ----------------------------------------------------------------------------------------------

  function fillRecorder() {
    if (!report) return;
    const actor = $("rec-actor").value, action = $("rec-action").value;
    $("rec-actor").replaceChildren(...report.actors.map((a) => P.el("option", `${a.id} (${a.role}${a.active ? "" : ", revoked"}${a.assigned ? ", assigned" : ""})`, { value: a.id })));
    const actions = [...new Set(P.model().transitions.map((t) => t.action))].sort();
    $("rec-action").replaceChildren(...actions.map((a) => P.el("option", a, { value: a })));
    if (actor) $("rec-actor").value = actor;
    if (action && actions.includes(action)) $("rec-action").value = action;
  }

  function renderSteps() {
    $("rec-steps").replaceChildren(P.el("li", `Given a new record in ${P.model().initial_state}`, { class: "test-given" }),
      ...steps.map((s) => P.el("li", `When ${s.actor} takes ${s.action}, it ${said(s.then)}`)));
    $("rec-keep").disabled = !steps.length || !$("rec-title").value.trim();
    $("rec-undo").disabled = !steps.length;
  }

  async function tryStep() {
    const wanted = [...steps.map((s) => [s.actor, s.action]), [$("rec-actor").value, $("rec-action").value]];
    try {
      steps = (await P.api("/api/play/tests/try", { ...P.about(), steps: wanted })).steps;
    } catch (error) {
      $("tests-summary").className = "laws-summary bad";
      $("tests-summary").textContent = `Could not try that step (${error.code || "ERROR"}): ${error.message}`;
      return;
    }
    renderSteps();
  }

  function slug(title, taken) {
    const base = (title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "") || "test").slice(0, 50).replace(/^[^a-z]+/, "t-");
    let id = base, n = 2;
    while (taken.has(id)) id = `${base}-${n++}`;
    return id;
  }

  function keep() {
    const current = document_();
    const id = slug($("rec-title").value, new Set(current.scenarios.map((s) => s.id)));
    setDraft({ ...current, scenarios: [...current.scenarios, { id, title: $("rec-title").value.trim(), steps }] });
    closeRecorder();
  }

  function closeRecorder() {
    steps = [];
    $("rec-title").value = "";
    renderSteps();
    $("tests-recorder").hidden = true;
    $("tests-new").setAttribute("aria-expanded", "false");
  }

  function shown(which) {
    if (which !== "tests") return;
    if (!report || key !== now()) run();
    else render();
  }

  function init(bridge) {
    P = bridge;
    P.hooks.tab.push(shown);
    P.hooks.redraw.push(() => { if (!$("tests").hidden) shown("tests"); });
    $("tests-run").addEventListener("click", run);
    $("tests-edit").addEventListener("click", () => { if (toggle("tests-editor", "tests-edit")) { $("tests-source").value = JSON.stringify(document_(), null, 2); $("tests-source").focus(); } });
    $("tests-new").addEventListener("click", () => { if (toggle("tests-recorder", "tests-new")) { fillRecorder(); renderSteps(); $("rec-title").focus(); } });
    $("tests-try").addEventListener("click", tryDraft);
    $("tests-reset").addEventListener("click", () => { draft = null; $("tests-problems").textContent = ""; run(); });
    $("tests-source").addEventListener("keydown", (event) => { if ((event.ctrlKey || event.metaKey) && event.key === "Enter") { event.preventDefault(); tryDraft(); } });
    $("rec-step").addEventListener("click", tryStep);
    $("rec-undo").addEventListener("click", () => { steps = steps.slice(0, -1); renderSteps(); });
    $("rec-title").addEventListener("input", renderSteps);
    $("rec-keep").addEventListener("click", keep);
    $("rec-cancel").addEventListener("click", closeRecorder);
    // The Sequences tab (ADR-0195) draws the same scenarios and edits this one draft.
    window.PlayTests = { draft: () => draft, edit: (next) => { if (next) setDraft(next); else { draft = null; $("tests-problems").textContent = ""; run(); } } };
  }

  if (window.PlayIDE) init(window.PlayIDE);
})();
