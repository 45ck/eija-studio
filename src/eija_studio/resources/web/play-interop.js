// PlayIDE UML interchange (ADR-0190): export the model on screen as XMI, PlantUML, Mermaid or draw.io, and import a UML
// file as a report. An import's state machine edits become the plan, as the person's own steps, so the server
// re-checks and previews them through the policy like drawn edits; nothing is applied or saved from here. What could
// not be imported is listed with the reason, never dropped.
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const REVIEW = new URLSearchParams(location.search).get("view") === "review"; // the read-only review view (ADR-0172)
  const view = () => window.PlayIDE;
  const MAX_PLAN = 12; // a plan previews at most this many steps (ADR-0156)
  const FORMATS = [
    ["xmi", "XMI (UML 2.5)", "Enterprise Architect, Cameo, Papyrus, Visual Paradigm, StarUML"],
    ["plantuml", "PlantUML", "docs-as-code, wikis, IDE plugins"],
    ["mermaid", "Mermaid (Markdown)", "GitHub, GitLab, README files"],
    ["drawio", "draw.io", "diagrams.net, Confluence, VS Code"],
  ];
  const ACCEPT = ".xmi,.uml,.xml,.puml,.plantuml,.pu,.iuml,.wsd,.mmd,.mermaid,.md,.drawio,.dio";

  function el(tag, text, attrs = {}) {
    return view().el(tag, text, attrs);
  }

  function status(text) {
    const box = $("uml-status");
    box.textContent = text;
    box.hidden = !text;
  }

  function download(name, text, type) {
    const link = el("a", undefined, { href: URL.createObjectURL(new Blob([text], { type })), download: name });
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(link.href), 1000);
  }

  async function exportAs(format) {
    closeMenu();
    try {
      const result = await view().api("/api/play/export", { ...view().about(), format });
      download(result.filename, result.text, result.media_type);
      status(`Exported ${result.filename}. Not in any UML file: ${result.report.not_carried.join("; ")}.`);
    } catch (error) {
      status(`Export failed (${error.code || "ERROR"}): ${error.message}`);
    }
  }

  // ---- the menu -----------------------------------------------------------------------------------------------
  function closeMenu() {
    $("uml-pop").hidden = true;
    $("uml-menu").setAttribute("aria-expanded", "false");
  }

  function menu() {
    const anchor = el("div", undefined, { class: "uml-anchor" });
    const opener = el("button", "Import / Export", { id: "uml-menu", type: "button", class: "quiet", "aria-haspopup": "menu",
      "aria-expanded": "false", "aria-controls": "uml-pop", title: "Export the model as UML, or import a UML file" });
    const pop = el("div", undefined, { id: "uml-pop", class: "uml-pop", role: "menu", "aria-label": "UML import and export" });
    pop.hidden = true;
    pop.append(el("p", "Export the model on screen", { class: "uml-head" }));
    for (const [format, name, where] of FORMATS) {
      const item = el("button", undefined, { type: "button", role: "menuitem", id: `uml-export-${format}` });
      item.append(el("span", name), el("span", where, { class: "muted small" }));
      item.addEventListener("click", () => exportAs(format));
      pop.append(item);
    }
    if (!REVIEW) {
      pop.append(el("p", "Import", { class: "uml-head" }));
      const item = el("button", undefined, { type: "button", role: "menuitem", id: "uml-import" });
      item.append(el("span", "Import a UML file…"), el("span", "checked by the kernel; nothing is saved", { class: "muted small" }));
      item.addEventListener("click", () => { closeMenu(); $("uml-file").click(); });
      pop.append(item);
      if (window.PlaySystems) { // a new system from a file goes through the Systems dialog (ADR-0185)
        const start = el("button", undefined, { type: "button", role: "menuitem", id: "uml-new-system" });
        start.append(el("span", "Start a new system from a UML file…"), el("span", "the file's model, checked by the kernel", { class: "muted small" }));
        start.addEventListener("click", () => { closeMenu(); window.PlaySystems.new("uml"); });
        pop.append(start);
      }
    }
    const file = el("input", undefined, { id: "uml-file", type: "file", accept: ACCEPT, hidden: "" });
    file.addEventListener("change", () => { if (file.files[0]) readFile(file.files[0]); file.value = ""; });
    opener.addEventListener("click", () => {
      const open = pop.hidden, start = $("uml-new-system");
      if (start) start.hidden = Boolean($("system-controls") && $("system-controls").hidden); // no systems on this server
      const items = [...pop.querySelectorAll("button")].filter((b) => !b.hidden);
      pop.hidden = !open;
      opener.setAttribute("aria-expanded", String(open));
      if (open) items[0].focus();
    });
    pop.addEventListener("keydown", (event) => {
      const items = [...pop.querySelectorAll("button")].filter((b) => !b.hidden), i = items.indexOf(document.activeElement);
      if (event.key === "Escape") { closeMenu(); opener.focus(); }
      if (event.key === "ArrowDown" || event.key === "ArrowUp") {
        event.preventDefault();
        items[(i + (event.key === "ArrowDown" ? 1 : items.length - 1)) % items.length].focus();
      }
    });
    document.addEventListener("click", (event) => { if (!anchor.contains(event.target)) closeMenu(); });
    anchor.append(opener, pop, file);
    const end = document.querySelector(".bar-end");
    end.insertBefore(anchor, end.querySelector("a.quiet"));
    const note = el("p", "", { id: "uml-status", class: "uml-status muted small", role: "status", "aria-live": "polite" });
    note.hidden = true;
    document.querySelector(".toolbar").after(note);
  }

  // ---- import -------------------------------------------------------------------------------------------------
  async function readFile(file) {
    if (file.size > 2_000_000) { status(`${file.name} is too large to import (over 2 MB).`); return; }
    const base = view().about();
    try {
      const report = await view().api("/api/play/import", { case_id: base.case_id, model: base.model, filename: file.name, text: await file.text() });
      showReport(file.name, report);
    } catch (error) {
      status(`Could not import ${file.name} (${error.code || "ERROR"}): ${error.message}`);
    }
  }

  const VERDICT = {
    CLEAN: "Everything in the file was read, and the kernel accepts the result.",
    PARTIAL: "Most of the file was read. What could not be imported is listed below with the reason.",
    REFUSED: "The kernel does not accept this model as it stands. The reasons are below.",
    EMPTY: "The file has no UML state machine or class diagram that PlayIDE reads.",
  };

  function entries(title, items, open) {
    if (!items.length) return null;
    const box = el("details", undefined, { class: "uml-list" });
    box.open = open;
    box.append(el("summary", `${title} (${items.length})`));
    const list = el("ul");
    for (const item of items) {
      const li = el("li");
      li.append(el("strong", item.element), document.createTextNode(item.reason ? `: ${item.reason}` : ""), el("span", item.where, { class: "muted small" }));
      list.append(li);
    }
    box.append(list);
    return box;
  }

  function machine(report, close) {
    const sm = report.state_machine, box = el("section", undefined, { class: "uml-part" });
    box.append(el("h3", "State machine"));
    if (!sm.found) { box.append(el("p", "Not in this file.", { class: "muted" })); return box; }
    const steps = sm.transactions || [];
    const verdict = sm.policy && sm.policy.length ? `The policy refuses it: ${sm.policy.join(", ")}.`
      : sm.laws ? `Laws: ${sm.laws}.` : "";
    box.append(el("p", steps.length ? `${steps.length} edit${steps.length === 1 ? "" : "s"} to the model in force. ${verdict}`
      : `The same as the model in force. ${verdict}`));
    if (steps.length && !REVIEW) {
      const add = el("button", steps.length > MAX_PLAN ? `Too many edits for one plan (${steps.length} of ${MAX_PLAN})` : "Preview as a plan", { type: "button", class: "primary", id: "uml-plan" });
      add.disabled = steps.length > MAX_PLAN;
      const partial = report.status === "PARTIAL";  // issue #165: say the plan is only what was read
      add.addEventListener("click", async () => { close(); await view().importPlan(steps, `${partial ? "Partly imported" : "Imported"} from ${report.filename}`); });
      if (partial) box.append(el("p", "Only the parts that were read are in this plan, and it removes nothing while part of the file could not be read.", { class: "muted small", id: "uml-partial" }));
      box.append(add);
      if (steps.length > MAX_PLAN) box.append(el("p", "Import it in parts, or run eija uml import to get the whole candidate model.", { class: "muted small" }));
    }
    return box;
  }

  function classes(report) {
    const cm = report.class_model, box = el("section", undefined, { class: "uml-part" });
    box.append(el("h3", "Class model"));
    if (!cm.found) { box.append(el("p", "Not in this file.", { class: "muted" })); return box; }
    if (!cm.candidate) { box.append(el("p", "Not imported: see the reasons below.", { class: "muted" })); return box; }
    const c = cm.changes || { added: [], removed: [], changed: [] };
    const parts = [["added", c.added], ["removed", c.removed], ["changed", c.changed]].filter(([, list]) => list.length)
      .map(([what, list]) => `${what} ${list.join(", ")}`);
    box.append(el("p", cm.changed ? `Classes ${parts.join("; ") || "reordered"}.` : "The same as the pack's class model."));
    if (cm.changed) {
      box.append(el("p", "Class model changes are shown, not applied: keeping one is part of saving a system.", { class: "muted small" }));
      const save = el("button", "Download data.json", { type: "button", id: "uml-data" });
      save.addEventListener("click", () => download("data.json", JSON.stringify(cm.candidate, null, 2) + "\n", "application/json"));
      box.append(save);
    }
    return box;
  }

  function showReport(name, report) {
    report.filename = name;
    let dialog = $("uml-import-dialog");
    if (!dialog) {
      dialog = el("dialog", undefined, { id: "uml-import-dialog", class: "uml-dialog", "aria-labelledby": "uml-import-title" });
      document.body.append(dialog);
    }
    const close = () => dialog.close();
    const shut = el("button", "Close", { type: "button", id: "uml-close" });
    shut.addEventListener("click", close);
    dialog.replaceChildren(
      el("h2", `Import ${name}`, { id: "uml-import-title" }),
      el("p", `${VERDICT[report.status]} Read as ${report.from}.`, { class: `uml-verdict ${report.status.toLowerCase()}` }),
      machine(report, close), classes(report),
      ...[entries("Not imported", report.unmapped, true), entries("Kept or filled in by PlayIDE", report.defaulted, report.unmapped.length === 0),
        entries("Read", report.mapped, false), entries("Derived, so redrawn from the model", report.derived, false)].filter(Boolean),
      el("div", undefined, { class: "uml-actions" }));
    dialog.querySelector(".uml-actions").append(shut);
    dialog.showModal();
  }

  window.PlayInterop = { entries }; // the Systems dialog shows a new system's import report the same way

  function start() {
    if (!window.PlayIDE) { setTimeout(start, 50); return; }
    menu();
  }
  document.readyState === "loading" ? document.addEventListener("DOMContentLoaded", start) : start();
})();
