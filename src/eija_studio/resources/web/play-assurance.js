// Capability and requirement review reads kernel responses. Prose drafts never become executable rules.
"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  const LABELS = { executable: "Executable", checked_design: "Checked design", unsupported: "Unsupported" };
  let P, report, request = 0, aspect = "requirements", requirement = "AC08", section = "capabilities";
  const prose = {};

  function button(text, action, attrs = {}) {
    const node = P.el("button", text, { type: "button", ...attrs });
    node.addEventListener("click", action);
    return node;
  }

  function subject() { return JSON.stringify([P.about(), window.PlayLaws?.draft?.(), prose]); }

  async function refresh() {
    const own = ++request, key = subject();
    $("assurance-status").textContent = "Reading the current model, pinned requirements and declared links…";
    $("assurance-refresh").disabled = true;
    try {
      const body = { ...P.about(), requirement_drafts: { ...prose } };
      const laws = window.PlayLaws?.draft?.();
      if (laws !== null && laws !== undefined) body.laws = laws;
      const next = await P.api("/api/play/assurance/compare", body);
      if (own !== request || key !== subject()) return;
      report = next;
      render();
      $("assurance-status").textContent = `Viewing ${next.model_scope.toLowerCase()} · baseline revision ${next.baseline_version}. Links are declarations; current service-test results are not produced here.`;
    } catch (error) {
      if (own !== request) return;
      report = null;
      $("assurance-content").replaceChildren(P.el("p", `Could not review this subject (${error.code || "ERROR"}): ${error.message}`, { class: "assurance-error", role: "alert" }));
      $("assurance-status").textContent = "Review unavailable. Your prose draft remains available; retry after fixing the model or law draft.";
    } finally {
      if (own === request) $("assurance-refresh").disabled = false;
    }
  }

  function showSection(next) {
    section = next;
    $("assurance-capabilities-tab").setAttribute("aria-selected", String(next === "capabilities"));
    $("assurance-requirements-tab").setAttribute("aria-selected", String(next === "requirements"));
    render();
  }

  function capabilities(box) {
    const layout = P.el("div", undefined, { class: "assurance-layout" });
    const nav = P.el("nav", undefined, { class: "assurance-aspects", "aria-label": "Software aspects" });
    for (const item of report.capabilities.aspects) {
      nav.append(button(item.name, () => { aspect = item.id; render(); }, { "aria-pressed": String(aspect === item.id), "data-aspect": item.id }));
    }
    const detail = P.el("section", undefined, { class: "assurance-detail", "aria-live": "polite" });
    const selected = report.capabilities.aspects.find((item) => item.id === aspect);
    detail.append(P.el("h3", selected.name));
    for (const construct of selected.constructs) {
      const card = P.el("article", undefined, { class: "assurance-construct " + construct.level });
      card.append(P.el("span", LABELS[construct.level], { class: "assurance-level" }), P.el("h4", construct.name), P.el("p", construct.scope));
      detail.append(card);
    }
    const supported = report.capabilities.activation;
    detail.append(P.el("h4", "What can become active"), P.el("p", supported.supported),
      P.el("p", `Draft only: ${supported.draft_only.join(", ")}. ${supported.reason}`, { class: "muted small" }));
    if (aspect === "requirements" || aspect === "assurance") detail.append(button("Inspect connected requirements", () => showSection("requirements"), { class: "primary" }));
    layout.append(nav, detail);
    box.append(layout);
  }

  function linkedRule(link) {
    const row = P.el("li", undefined, { class: link.resolved ? "assurance-link" : "assurance-link unresolved" });
    const name = link.ref || link.from;
    row.append(P.el("strong", `${link.kind} · ${link.resolved ? "resolved" : "unresolved"}`), P.el("span", name, { class: "assurance-reference" }),
      P.el("p", link.scope, { class: "muted small" }));
    if (name.startsWith("law:") && link.resolved) row.append(button("Inspect this law", () => {
      $("assurance").close();
      window.PlayLaws?.showLaw?.(name.slice(4));
    }));
    return row;
  }

  function requirementDetails(box, item) {
    box.append(P.el("h3", `${item.id} · ${item.area}`), P.el("p", item.required_evidence, { class: "muted" }));
    const before = P.el("section", undefined, { class: "assurance-before", "aria-label": "Pinned requirement" });
    before.append(P.el("h4", "Pinned requirement"), P.el("p", item.before));
    box.append(before);
    const label = P.el("label", "Prose draft for review", { for: "assurance-prose" });
    const editor = P.el("textarea", undefined, { id: "assurance-prose", rows: "4", maxlength: "2000" });
    editor.value = prose[item.id] ?? item.before;
    editor.addEventListener("input", () => {
      if (editor.value === item.before) delete prose[item.id]; else prose[item.id] = editor.value;
      $("assurance-status").textContent = "Prose draft kept in this browser session. Compare it to refresh the row identity and affected links; active policy is unchanged.";
    });
    box.append(label, editor, P.el("p", "This text stays a draft in this browser session. It does not change the law or the model in force.", { class: "muted small" }));
    const tools = P.el("div", undefined, { class: "assurance-tools" });
    tools.append(button("Compare prose draft", () => {
      if (!editor.value.trim()) { $("assurance-status").textContent = "Give the draft some text before comparing."; editor.focus(); return; }
      prose[item.id] = editor.value;
      refresh();
    }, { id: "assurance-prose-compare", class: "primary" }), button("Discard prose draft", () => { delete prose[item.id]; refresh(); }, { id: "assurance-prose-discard" }));
    box.append(tools);
    if (item.changed) box.append(P.el("p", "Requirement wording changed. Review the declared links against the new text; policy is unchanged.", { class: "assurance-warning" }));
    const evidence = P.el("details", undefined, { class: "assurance-identities" });
    evidence.append(P.el("summary", "Requirement identity and historical status"),
      P.el("p", `Hash method: ${item.hash_method}. Before ${item.before_hash}; draft ${item.after_hash}.`, { class: "assurance-reference small" }),
      P.el("p", `Historical v0.2 status: ${item.historical_status}. ${item.historical_scope}`),
      P.el("p", `Current observed service/test status: ${item.observed_status}. This panel does not run tests.`));
    box.append(evidence, P.el("h4", "Declared connections"));
    const links = P.el("ul", undefined, { class: "assurance-links" });
    for (const link of item.links) links.append(linkedRule(link));
    box.append(links);
    for (const link of item.model_links) {
      const b = button(`Inspect ${link.ref}`, () => { $("assurance").close(); P.showTab("states"); P.select(link.ref); P.follow([link.ref]); }, { class: "quiet" });
      b.disabled = !link.resolved;
      box.append(b);
    }
    if (item.unresolved.length) box.append(P.el("h4", "Unresolved coverage"), P.el("p", item.unresolved.join(" "), { class: "assurance-warning" }));
    if (item.affected) {
      box.append(P.el("p", item.review_required, { class: "assurance-warning" }));
      if (item.affected_checks.length) box.append(P.el("p", "Checks to revisit: " + item.affected_checks.join(", "), { class: "assurance-reference" }));
    }
  }

  function lawDiff(box) {
    const changed = report.traceability.laws.items.filter((law) => law.status !== "unchanged");
    const details = P.el("details", undefined, { class: "assurance-law-diff" });
    details.append(P.el("summary", changed.length ? `${changed.length} law drafts: compare fields` : "Law policy: unchanged"));
    details.append(P.el("p", "Law edits are typed drafts. Nothing in this panel activates them or silently weakens policy.", { class: "muted small" }));
    for (const law of changed) {
      details.append(P.el("h4", `${law.id} · ${law.status}`));
      details.append(P.el("p", law.draft_policy_fields.length
        ? `Executable law draft fields changed: ${law.draft_policy_fields.join(", ")}. The active policy is unchanged.`
        : "Description wording changed; executable law fields are unchanged. This remains a pack draft.", { class: "muted small" }));
      const table = P.el("table", undefined, { class: "assurance-diff-table" });
      const head = P.el("tr");
      for (const text of ["Field", "In force", "Draft"]) head.append(P.el("th", text, { scope: "col" }));
      const thead = P.el("thead"); thead.append(head); table.append(thead);
      const body = P.el("tbody");
      const value = (v) => v === undefined ? "Absent" : typeof v === "object" ? Object.entries(v).map(([k, x]) => `${k}: ${Array.isArray(x) ? x.join(", ") : x}`).join("; ") : String(v);
      for (const field of law.fields) {
        const tr = P.el("tr");
        tr.append(P.el("th", field.replaceAll("_", " "), { scope: "row" }), P.el("td", value(law.before?.[field])), P.el("td", value(law.after?.[field])));
        body.append(tr);
      }
      table.append(body); details.append(table);
    }
    box.append(details);
  }

  function requirements(box) {
    const trace = report.traceability;
    const row = P.el("div", undefined, { class: "assurance-tools" });
    row.append(P.el("label", "Requirement", { for: "assurance-requirement" }));
    const select = P.el("select", undefined, { id: "assurance-requirement" });
    for (const item of trace.requirements) select.append(P.el("option", `${item.id} · ${item.area}${item.changed ? " · prose draft" : ""}${item.affected ? " · review links" : ""}`, { value: item.id }));
    select.value = requirement;
    select.addEventListener("change", () => { requirement = select.value; render(); });
    row.append(select);
    box.append(row, P.el("p", `${trace.coverage.linked}/${trace.coverage.requirements} requirements have explicit self-dogfood links. ${trace.coverage.scope}`, { class: "muted small" }),
      P.el("p", "Requirement wording drafts stay in this open page only. Reloading discards them; they are not included in saved workflow edits.", { class: "assurance-warning small" }));
    const selected = trace.requirements.find((item) => item.id === requirement) || trace.requirements[0];
    const detail = P.el("section", undefined, { id: "assurance-requirement-detail" });
    requirementDetails(detail, selected); box.append(detail); lawDiff(box);
    const terms = P.el("details");
    terms.append(P.el("summary", `${trace.terms.length} declared vocabulary terms`));
    for (const term of trace.terms) terms.append(P.el("h4", term.label), P.el("p", term.definition), P.el("p", `${term.model_refs.join(", ") || "No model reference"} · declared term hash ${term.hash}`, { class: "assurance-reference small" }));
    box.append(terms);
  }

  function render() {
    if (!report) return;
    $("assurance-source-status").textContent = report.source_review.status;
    $("assurance-source-status").className = "assurance-source " + (report.source_review.status === "SOURCE_REVIEW_REQUIRED" ? "required" : "");
    const content = $("assurance-content"); content.replaceChildren();
    if (section === "capabilities") capabilities(content); else requirements(content);
    const source = report.traceability.provenance;
    $("assurance-provenance").textContent = `Requirements: packaged historical acceptance snapshot ${source.revision.slice(0, 8)}. ${source.scope}`;
  }

  function init() {
    if (P || !window.PlayIDE || !$("assurance")) return;
    P = window.PlayIDE;
    const dialog = $("assurance"), header = P.el("header", undefined, { class: "assurance-header" });
    header.append(P.el("h2", "Capabilities & requirements", { id: "assurance-title" }), button("Close", () => dialog.close(), { id: "assurance-close", "aria-label": "Close capabilities and requirements" }));
    const tabs = P.el("div", undefined, { class: "assurance-tools", role: "tablist", "aria-label": "Assurance view" });
    tabs.append(button("Capabilities", () => showSection("capabilities"), { id: "assurance-capabilities-tab", role: "tab", "aria-selected": "true" }),
      button("Requirements & laws", () => showSection("requirements"), { id: "assurance-requirements-tab", role: "tab", "aria-selected": "false" }),
      button("Refresh current subject", refresh, { id: "assurance-refresh" }));
    dialog.append(header, P.el("p", "SOURCE_REVIEW_REQUIRED", { id: "assurance-source-status", class: "assurance-source required" }), tabs,
      P.el("p", "", { id: "assurance-status", role: "status", "aria-live": "polite" }),
      P.el("div", undefined, { id: "assurance-content", class: "assurance-content" }),
      P.el("p", "", { id: "assurance-provenance", class: "muted small" }));
    $("assurance-open").addEventListener("click", () => { dialog.showModal(); refresh(); });
    P.hooks.redraw.push(() => { if (dialog.open) refresh(); });
    window.PlayAssurance = { requirementDrafts: () => ({ ...prose }), refresh,
      open: (next = "capabilities") => { dialog.showModal(); showSection(next); return refresh(); } };
  }
  init();
  document.addEventListener("playide:ready", init);
})();
