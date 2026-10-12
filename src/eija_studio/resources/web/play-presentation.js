"use strict";
// A read-only lens over server-resolved screens/data/workflow. It never decides
// eligibility or creates an action, approval, route or second UI model.
const PlayPresentation = (() => {
  function matches(report, running, current = true) {
    const subject = report?.subject;
    return Boolean(current && report?.format === "eija.presentation-map.v1" && report.support === "CHECKED_DESIGN"
      && subject?.format === "eija.build-subject.v1" && /^[0-9a-f]{64}$/.test(subject.digest || "")
      && /^[0-9a-f]{64}$/.test(subject.model_hash || "")
      && running?.subject?.format === subject.format && running.subject.digest === subject.digest
      && running.model === subject.model_hash && running.subject.model_hash === subject.model_hash);
  }
  function follow(item, kind, bridge) {
    if (kind === "screen" && Object.hasOwn(item, "use_case")) bridge.openScreen(item.use_case);
    else if (kind === "usecase" && item.use_case_ref) {
      bridge.showTab("usecases"); bridge.select(item.use_case_ref, false);
    } else if (kind === "class" && item.class_ref) {
      bridge.showTab("classes"); bridge.select(item.class_ref, false);
    }
  }
  return Object.freeze({matches, follow});
})();
if (typeof module !== "undefined" && module.exports) module.exports = PlayPresentation;

if (typeof window !== "undefined" && typeof document !== "undefined") (() => {
  const $ = id => document.getElementById(id);
  let P, report = null, asked = "", selected = "new-record", serial = 0;
  const body = () => ({...P.about(), screens: P.editedScreens()});
  const key = () => JSON.stringify(body());
  const button = (text, action, attrs = {}) => {
    const node = P.el("button", text, {type: "button", ...attrs});
    node.addEventListener("click", action); return node;
  };
  function freshness() {
    if (!report) return;
    const current = asked === key(), exact = PlayPresentation.matches(report, P.runningBuild(), current);
    $("presentation-subject").textContent = current
      ? `${report.model_scope} · ${report.frontend.framework} / ${report.frontend.library} · build ${report.subject.digest.slice(0, 12)}`
      : "Model changed · refresh this design map";
    $("presentation-status").textContent = exact
      ? "Exact subject matches the local app. Design projection; runtime behaviour is checked by its service."
      : "Checked design only. No current app with this exact subject is reported.";
    $("presentation-status").dataset.match = String(exact);
  }
  function choose(id) {
    if (!report || asked !== key()) return;
    selected = id; render();
  }
  function card(title, text, id, attrs = {}) {
    const node = button("", () => choose(id), {class: "presentation-card", "data-presentation-node": id,
      "aria-pressed": String(selected === id), ...attrs});
    node.append(P.el("strong", title), P.el("span", text)); return node;
  }
  function inspect(item) {
    const box = $("presentation-inspector");
    box.replaceChildren(P.el("h4", item.title), P.el("p", item.kind === "create"
      ? `Create a ${report.record.name}. The service starts it in ${item.authority.to_state}.`
      : `${item.authority.from_state} → ${item.authority.to_state} · ${item.authority.role}`, {class: "presentation-consequence"}));
    const fields = P.el("ul", undefined, {class: "presentation-fields"});
    for (const field of item.fields) {
      const row = P.el("li");
      row.append(P.el("strong", field.label), P.el("span", `${field.attribute} · ${field.type}${field.required ? " · required" : ""}`),
        P.el("span", `${field.control.component} · ${field.editable ? "editable on creation" : "read-only value"}`, {class: "presentation-control"}));
      fields.append(row);
    }
    box.append(fields.children.length ? fields : P.el("p", "No declared record fields on this screen."));
    const links = P.el("div", undefined, {class: "presentation-links"});
    links.append(button("Design screen", () => PlayPresentation.follow(item, "screen", P)),
      button("Use case", () => PlayPresentation.follow(item, "usecase", P)));
    if (item.class_ref) links.append(button("Record class", () => PlayPresentation.follow(item, "class", P)));
    box.append(links, P.el("p", `Confirm: ${item.button}. Authority is checked at the action, not by this map.`, {class: "presentation-help"}));
    if (item.authority.required_effects.length) box.append(P.el("p", "Declared effects: " + item.authority.required_effects.join(", "), {class: "presentation-help"}));
    box.append(P.el("p", `Sources: ${item.sources.join(", ")} · ${report.frontend.source}`, {class: "presentation-source"}));
  }
  function render() {
    if (!report || asked !== key()) return;
    const map = $("presentation-map"), flow = P.el("div", undefined, {class: "presentation-flow"});
    const records = report.navigation.destinations.find(item => item.kind === "records");
    const detail = report.navigation.destinations.find(item => item.kind === "detail");
    flow.append(card(report.create.title, "Create · editable fields", report.create.id),
      P.el("span", "→", {class: "presentation-arrow", "aria-hidden": "true"}),
      card(records.title, "Select a stored record", records.id), P.el("span", "→", {class: "presentation-arrow", "aria-hidden": "true"}),
      card(detail.title, "State, values & available actions", detail.id));
    const actions = P.el("div", undefined, {class: "presentation-actions", role: "group", "aria-label": "Declared action screens"});
    for (const action of report.actions) actions.append(card(action.title, `${action.authority.role} · ${action.authority.from_state} → ${action.authority.to_state}`, action.id));
    map.replaceChildren(flow, P.el("p", "Choose an action screen from record detail", {class: "presentation-help"}), actions);
    const item = [report.create, ...report.actions].find(screen => screen.id === selected);
    if (item) inspect(item);
    else {
      const box = $("presentation-inspector");
      box.replaceChildren(P.el("h4", selected === "records" ? "Records" : "Record detail"),
        P.el("p", selected === "records" ? "The list selects an existing local record. It does not start another workflow."
          : "The service supplies current values and action options. Choosing a screen does not commit the action."));
      if (report.record.class_ref) box.append(button("Record class", () => PlayPresentation.follow(report.record, "class", P)));
    }
    freshness();
  }
  async function refresh(force = false) {
    const now = key(), mine = ++serial;
    if (!force && report && asked === now) {freshness(); return;}
    report = null; asked = "";
    $("presentation-subject").textContent = "Reading current generated design…";
    $("presentation-status").textContent = "No current design result yet.";
    $("presentation-status").dataset.match = "false";
    $("presentation-map").replaceChildren(); $("presentation-inspector").replaceChildren();
    try {
      const next = await P.api("/api/play/presentation", body());
      if (mine !== serial || now !== key()) return;
      report = next; asked = now; render();
    } catch (error) {
      if (mine !== serial || now !== key()) return;
      $("presentation-status").textContent = `App map unavailable (${error.code || "ERROR"}): ${error.message}. Nothing was applied.`;
    }
  }
  function init(bridge) {
    P = bridge;
    const panel = $("presentation-panel");
    if (!panel) return;
    const summary = P.el("summary", "App map · screens, data & actions");
    const heading = P.el("div", undefined, {class: "presentation-heading"});
    heading.append(P.el("p", "Content → navigation → presentation", {class: "presentation-eyebrow"}),
      button("Refresh map", () => refresh(true), {class: "quiet", id: "presentation-refresh"}));
    panel.append(summary, heading, P.el("p", "", {id: "presentation-subject", class: "presentation-source"}),
      P.el("p", "", {id: "presentation-status", role: "status", "aria-live": "polite"}),
      P.el("div", undefined, {id: "presentation-map"}), P.el("section", undefined, {id: "presentation-inspector", "aria-label": "Selected app screen"}),
      P.el("p", "UWE-inspired checked design · action inputs and record updates remain unsupported. Fixture identity; no login or external delivery.", {class: "presentation-help"}));
    panel.addEventListener("toggle", () => {if (panel.open) refresh();});
    P.hooks.redraw.push(() => {if (panel.open) refresh(); else if (report) freshness();});
    document.addEventListener("playide:built", () => {if (report) freshness();});
    window.PlayPresentationMap = {refresh: () => refresh(true), current: () => report && asked === key() ? report : null};
  }
  if (window.PlayIDE) init(window.PlayIDE);
})();
