// PlayIDE Laws tab (ADR-0166): the pack's laws, the layer above the UML, each with the server's verdict on the model on
// screen. The server proves every law over every run the kernel allows; this page only lists the verdicts and paints
// a law's subject, or the shortest run that breaks it, on the state machine. The law file can be edited here as a
// draft, which the server checks and proves; nothing is saved, and the draft pack can be downloaded (ADR-0177).
"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  const BADGE = {
    HOLDS: ["Holds", "Proved: no run by any actor breaks it."],
    BROKEN: ["Broken", "The model, or a run of it, breaks this law."],
    VACUOUS: ["Vacuous", "Nothing breaks it, but only because nothing reaches what it is about."],
    INACTIVE: ["Not in force", "This law applies only to a model with a particular action."],
    EVIDENCE: ["Needs evidence", "Judged by the evidence a review collects, not by runs."],
    UNKNOWN: ["Unknown", "The search stopped before covering every run."],
  };
  const OVERALL = {
    HOLDS: "Every law in force holds on every run the kernel allows.",
    BROKEN: "A law is broken.",
    REFUSED: "The kernel refuses this model, so it would run nothing. The broken laws are below.",
    UNKNOWN: "The search stopped before covering every run.",
  };
  const PATH = { strokeColor: "#a12f2f", strokeWidth: 3.5, dashed: 0 };
  const SUBJECT = { strokeColor: "#3157d5", strokeWidth: 3 };
  const MODES = { kernel: "the kernel itself", hand_encoded: "written by hand", generated: "generated from the laws", not_run: "not run" };
  let P = null, report = null, key = null, draft = null, download = null;

  const now = () => P.viewKey() + JSON.stringify(P.model()) + JSON.stringify(draft); // the model on screen and any draft
  const transitionFor = (action) => P.model().transitions.find((t) => t.action === action);

  function cellsOf(subject) {
    return subject.map((ref) => {
      if (ref.startsWith("state:")) return ref;
      const t = transitionFor(ref.slice(7));
      return t ? "transition:" + t.id : null;
    }).filter(Boolean);
  }

  function onDiagram(paint) {
    P.showTab("states");
    P.clearSim();
    P.graph().batchUpdate(paint);
    P.fit();
  }

  function showSubject(law) {
    onDiagram(() => { for (const id of cellsOf(law.subject)) P.restyle(id, id.startsWith("state:") ? { strokeColor: SUBJECT.strokeColor, strokeWidth: 3, fillColor: "#dfe6ff" } : SUBJECT); });
  }

  function showRun(law) {
    onDiagram(() => {
      law.counterexample.forEach((step, i) => {
        const t = transitionFor(step.action);
        if (t) P.restyle("transition:" + t.id, PATH, `${i + 1}. ${P.label(t)}`);
      });
      const last = law.counterexample[law.counterexample.length - 1];
      if (last) P.restyle("state:" + last.to, { strokeColor: PATH.strokeColor, strokeWidth: 3 });
    });
  }

  function card(law) {
    const [badge, title] = BADGE[law.status] || [law.status, ""];
    const item = P.el("li", undefined, { class: "law " + law.status.toLowerCase() });
    const head = P.el("div", undefined, { class: "law-head" });
    head.append(P.el("span", badge, { class: "law-badge", title }), P.el("span", law.description || law.id, { class: "law-text" }));
    item.append(head, P.el("p", `${law.kind.replaceAll("_", " ")} · ${law.code} · ${law.why}`, { class: "muted small law-why" }));
    const tools = P.el("div", undefined, { class: "law-tools" });
    if (law.counterexample) {
      const steps = P.el("ol", undefined, { class: "law-run" });
      for (const s of law.counterexample) steps.append(P.el("li", `${s.role} takes ${s.action}: ${s.from} → ${s.to}`));
      item.append(P.el("p", "Shortest run that breaks it:", { class: "small" }), steps);
      const button = P.el("button", "Show this run", { type: "button", class: "quiet" });
      button.addEventListener("click", () => showRun(law));
      tools.append(button);
    }
    if (law.subject.length && cellsOf(law.subject).length) {
      const button = P.el("button", "Show on diagram", { type: "button", class: "quiet" });
      button.addEventListener("click", () => showSubject(law));
      tools.append(button);
    }
    if (tools.childElementCount) item.append(tools);
    return item;
  }

  function renderFile() {
    const file = report.file;
    $("laws-file").textContent = `${file.path} › ${file.section}`;
    const changes = file.draft;
    $("laws-draft").hidden = !changes;
    if (changes) {
      const said = [["added", "added"], ["changed", "changed"], ["removed", "removed"]].filter(([k]) => changes[k].length).map(([k, w]) => `${changes[k].length} ${w}`);
      $("laws-draft").textContent = `Edited, not saved${said.length ? ": " + said.join(", ") : ""}`;
      $("laws-draft").title = changes.removed.length || changes.changed.length ? "Removing or changing a law can loosen what the kernel refuses. Review it before you replace pack.json." : "";
    }
    if (download) URL.revokeObjectURL(download);
    download = file.draft_pack ? URL.createObjectURL(new Blob([JSON.stringify(file.draft_pack, null, 2) + "\n"], { type: "application/json" })) : null;
    $("laws-download").hidden = !download;
    if (download) $("laws-download").href = download;
    $("laws-verifiers").replaceChildren(...file.verifiers.map((v) => {
      const item = P.el("li", undefined, { class: "verifier " + v.mode });
      item.append(P.el("strong", v.kind.replaceAll("_", " ")), P.el("span", MODES[v.mode] || v.mode, { class: "law-badge" }));
      if (v.reason) item.append(P.el("p", v.reason, { class: "muted small" }));
      return item;
    }));
    if ($("laws-editor").hidden || !$("laws-source").value) $("laws-source").value = JSON.stringify(draft || file.laws, null, 2);
  }

  function render() {
    if (!report) return;
    renderFile();
    const count = (status) => report.laws.filter((l) => l.status === status).length;
    const parts = ["HOLDS", "BROKEN", "VACUOUS", "INACTIVE", "EVIDENCE", "UNKNOWN"].filter(count).map((s) => `${count(s)} ${BADGE[s][0].toLowerCase()}`);
    const search = report.search;
    const scope = search.status === "NOT_RUN" ? (report.status === "REFUSED" ? "" : search.why)
      : `Searched ${search.configurations} reachable configurations with ${search.actor_classes} kinds of actor` +
        (search.status === "COMPLETE" ? ", every one." : ", then stopped.") +
        (search.unreached.length ? ` Never reached: ${search.unreached.join(", ")}.` : "");
    $("laws-summary").className = "laws-summary " + (!report.laws.length ? "" : report.status === "HOLDS" ? "ok" : "bad");
    // With no laws there is nothing to hold: say so rather than "every law holds".
    $("laws-summary").textContent = !report.laws.length ? `This system has no laws yet. Press Edit the law file to add one. ${scope}`
      : `${OVERALL[report.status]} ${parts.join(", ")}. ${scope}`;
    $("laws-list").replaceChildren(...report.laws.map(card));
    $("laws-limits").textContent = report.limits.join(" ");
  }

  async function prove() {
    const asked = now();
    $("laws-prove").disabled = true;
    $("laws-summary").className = "laws-summary";
    $("laws-summary").textContent = "Proving every law over every run…";
    try {
      const result = await P.api("/api/play/laws", draft ? { ...P.about(), laws: draft } : P.about());
      if (asked !== now()) return; // the model changed while proving; the next look proves again
      report = result;
      key = asked;
      $("laws-problems").textContent = "";
      render();
    } catch (error) {
      if (error.code === "LAWS_INVALID") {
        $("laws-problems").textContent = `The draft is not a valid law file: ${error.message}`;
        $("laws-summary").className = "laws-summary bad";
        $("laws-summary").textContent = "The draft law file has problems; nothing was proved.";
        return;
      }
      $("laws-summary").className = "laws-summary bad";
      $("laws-summary").textContent = `Could not prove the laws (${error.code || "ERROR"}): ${error.message}`;
    } finally {
      $("laws-prove").disabled = false;
    }
  }

  function shown() {
    if (!report || key !== now()) prove();
    else render();
  }

  function redrawn() {
    if (!$("laws").hidden) shown();
  }

  function toggleEditor() {
    const open = $("laws-editor").hidden;
    $("laws-editor").hidden = !open;
    $("laws-edit").setAttribute("aria-expanded", String(open));
    if (open && report) { $("laws-source").value = JSON.stringify(draft || report.file.laws, null, 2); $("laws-source").focus(); }
  }

  function tryDraft() {
    let laws;
    try {
      laws = JSON.parse($("laws-source").value);
    } catch (error) {
      $("laws-problems").textContent = `The draft is not JSON: ${error.message}`;
      return;
    }
    if (!Array.isArray(laws)) { $("laws-problems").textContent = "The law file is a JSON list of laws."; return; }
    draft = laws;
    prove();
  }

  function reset() {
    draft = null;
    if (report) $("laws-source").value = JSON.stringify(report.file.laws, null, 2);
    $("laws-problems").textContent = "";
    prove();
  }

  function init(bridge) {
    P = bridge;
    P.hooks.laws.push(shown);
    P.hooks.redraw.push(redrawn);
    $("laws-prove").addEventListener("click", prove);
    $("laws-edit").addEventListener("click", toggleEditor);
    $("laws-try").addEventListener("click", tryDraft);
    $("laws-reset").addEventListener("click", reset);
    $("laws-source").addEventListener("keydown", (event) => { if ((event.ctrlKey || event.metaKey) && event.key === "Enter") { event.preventDefault(); tryDraft(); } });
  }

  if (window.PlayIDE) init(window.PlayIDE);
})();
