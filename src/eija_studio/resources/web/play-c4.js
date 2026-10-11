// C4 is a structural lens over server-resolved generated source. It never edits
// policy, simulates an external connection, or turns a source link into proof.
"use strict";
const PlayC4Subject = (() => {
  function matches(subject, running) {
    return Boolean(subject && subject.format === "eija.build-subject.v1" && typeof subject.digest === "string"
      && /^[0-9a-f]{64}$/.test(subject.digest) && running && running.subject
      && running.subject.format === subject.format && running.subject.digest === subject.digest
      && running.model === subject.model_hash && running.subject.model_hash === subject.model_hash);
  }
  return Object.freeze({ matches });
})();
if (typeof module !== "undefined" && module.exports) module.exports = PlayC4Subject;

if (typeof window !== "undefined" && typeof document !== "undefined") (() => {
  const $ = (id) => document.getElementById(id);
  const LEVELS = { context: "1 · Context", containers: "2 · Containers", components: "3 · Components" };
  const SUPPORT = { generated_structure: "Generated source", fixture_contract: "Fixture contract", checked_design: "Design only" };
  const ICONS = { person: "♙", external_actor: "◇", software_system: "⬡", container: "▣", database: "◉", kernel: "⚙", artifact: "▤", browser: "▣", component: "⬡" };
  const NS = "http://www.w3.org/2000/svg";
  let P, report = null, asked = "", level = "context", selected = null, serial = 0, observer;
  const subject = () => ({ ...P.about(), screens: P.editedScreens() });
  const key = () => JSON.stringify(subject());

  function button(text, action, attributes = {}) {
    const node = P.el("button", text, { type: "button", ...attributes });
    node.addEventListener("click", action);
    return node;
  }

  function setup() {
    const panel = $("c4-panel");
    const header = P.el("header", undefined, { class: "c4-header" });
    const title = P.el("div");
    title.append(P.el("p", "ARCHITECTURE / READ ONLY", { class: "c4-eyebrow" }), P.el("h2", "See the shape of your software"));
    header.append(title, button("Refresh structure", () => refresh(true), { id: "c4-refresh" }));
    const tools = P.el("div", undefined, { id: "c4-levels", role: "group", "aria-label": "C4 architecture level" });
    for (const [id, text] of Object.entries(LEVELS)) {
      tools.append(button(text, () => showLevel(id), { "data-c4-level": id, "aria-pressed": String(id === level) }));
    }
    const revision = P.el("div", undefined, { class: "c4-revision" });
    revision.append(P.el("span", "Reading structure…", { id: "c4-subject" }), P.el("span", "", { id: "c4-source", class: "c4-source" }));
    const status = P.el("p", "", { id: "c4-status", role: "status", "aria-live": "polite" });
    const layout = P.el("div", undefined, { class: "c4-layout" });
    const map = P.el("section", undefined, { class: "c4-map-column", "aria-label": "C4 architecture map" });
    map.append(P.el("p", "Select a box to inspect its source and relationships. Drill into the system, then its server.", { class: "c4-help" }),
      P.el("div", undefined, { id: "c4-map" }));
    const inspector = P.el("aside", undefined, { id: "c4-inspector", "aria-label": "Selected architecture element", tabindex: "-1" });
    layout.append(map, inspector);
    panel.append(header, tools, revision, status, layout, P.el("details", undefined, { id: "c4-limits" }));
    observer = new ResizeObserver(() => drawEdges());
    observer.observe($("c4-map"));
  }

  function freshness() {
    if (!report) return;
    const model = report.subject.model_hash, build = report.subject.digest;
    $("c4-subject").textContent = `${report.model_scope} · revision ${report.baseline_version} · build ${build.slice(0, 12)}`;
    $("c4-subject").title = `Build ${build}; workflow ${model}`;
    $("c4-source").textContent = report.source_review;
    $("c4-source").classList.toggle("required", report.source_review === "SOURCE_REVIEW_REQUIRED");
    const running = P.runningBuild();
    const built = PlayC4Subject.matches(report.subject, running);
    $("c4-status").textContent = `Current generated source · ${report.generation.oracle_cases} oracle cases defined; build verification ${report.generation.conformance}. `
      + (built ? "A local app launch with this exact build subject was reported; runtime behaviour is separate."
        : "No local app launch with this exact build subject is reported for this view.");
    const limits = $("c4-limits"), open = limits.open;
    limits.replaceChildren(P.el("summary", "Scope, identities and unsupported capabilities"));
    const list = P.el("ul");
    for (const text of report.limits) list.append(P.el("li", text));
    limits.append(list);
    if (report.data_support) limits.append(P.el("p", report.data_support.limits.join(" ")));
    const identities = P.el("dl", undefined, { class: "c4-facts" });
    for (const [name, value] of Object.entries(report.subject)) identities.append(P.el("dt", name.replaceAll("_", " ")), P.el("dd", value || "Not declared"));
    limits.append(identities, P.el("p", "Projection freshness identifies this structure. It does not approve a change or certify deployment."));
    limits.open = open;
  }

  async function refresh(force = false) {
    const now = key(), mine = ++serial;
    if (!force && report && now === asked) { freshness(); render(); return; }
    report = null; asked = "";
    $("c4-subject").textContent = "Current subject pending";
    $("c4-subject").removeAttribute("title");
    $("c4-source").textContent = "Review status pending";
    $("c4-source").classList.remove("required");
    $("c4-limits").replaceChildren(P.el("summary", "No current architecture report"));
    $("c4-status").textContent = "Reading the exact model's generated source…";
    $("c4-map").replaceChildren();
    $("c4-inspector").replaceChildren(P.el("p", "Loading current structure. Previous details are no longer shown."));
    try {
      const next = await P.api("/api/play/c4", subject());
      if (mine !== serial || now !== key()) return;
      report = next; asked = now;
      freshness(); render();
    } catch (error) {
      if (mine !== serial || now !== key()) return;
      report = null; asked = "";
      $("c4-status").textContent = `Structure unavailable (${error.code || "ERROR"}): ${error.message}. Refresh after resolving the model or session.`;
      $("c4-inspector").replaceChildren(P.el("p", "No current structural result. Nothing was applied."));
    }
  }

  function showLevel(next, focus = false) {
    if (!(next in LEVELS)) return;
    level = next; selected = null;
    for (const item of $("c4-levels").querySelectorAll("button")) item.setAttribute("aria-pressed", String(item.dataset.c4Level === level));
    if (report && asked === key()) render();
    if (focus) $("c4-levels").querySelector(`[data-c4-level="${next}"]`).focus();
  }

  function nodeCard(node) {
    const card = button("", () => inspect(node.id), { class: "c4-node " + node.kind + " " + node.support, "data-c4-node": node.id,
      "aria-pressed": String(selected === node.id), "aria-label": `${node.name}, ${SUPPORT[node.support] || node.support}` });
    card.append(P.el("span", ICONS[node.kind] || "◇", { class: "c4-icon", "aria-hidden": "true" }),
      P.el("strong", node.name), P.el("span", node.technology, { class: "c4-technology" }), P.el("span", node.summary, { class: "c4-description" }),
      P.el("span", SUPPORT[node.support] || node.support, { class: "c4-support" }));
    if (node.drill) card.append(P.el("span", "Inspect to explore inside →", { class: "c4-drill-hint" }));
    return card;
  }

  function render() {
    const view = report.levels[level], board = P.el("div", undefined, { class: "c4-board " + level, "data-c4-boundary": view.boundary });
    const boundary = P.el("p", view.name + " · " + (level === "components" ? "inside the local application server" : level === "containers" ? "inside the generated software system" : view.boundary), { class: "c4-boundary" });
    const svg = document.createElementNS(NS, "svg");
    svg.setAttribute("id", "c4-lines"); svg.setAttribute("aria-hidden", "true");
    board.append(svg);
    if (level === "context") {
      const actors = P.el("div", undefined, { class: "c4-actors" }), systems = P.el("div", undefined, { class: "c4-systems" });
      for (const node of view.nodes) (node.kind === "software_system" ? systems : actors).append(nodeCard(node));
      board.append(actors, systems);
    } else {
      for (const node of view.nodes) board.append(nodeCard(node));
    }
    $("c4-map").replaceChildren(boundary, board);
    if (!view.nodes.some((node) => node.id === selected)) selected = null;
    if (selected) inspect(selected);
    else $("c4-inspector").replaceChildren(P.el("p", "Select an element", { class: "c4-eyebrow" }),
      P.el("h3", level === "context" ? "Who uses this system?" : level === "containers" ? "Where do responsibilities live?" : "What is inside the server?"),
      P.el("p", "Each box and arrow comes from generated files or a declared fixture contract. Selecting it reveals the exact sources and capability limits."),
      P.el("p", `${view.nodes.length} elements · ${view.relationships.length} sourced relationships`, { class: "c4-count" }));
    requestAnimationFrame(drawEdges);
  }

  function drawEdges() {
    const svg = $("c4-lines");
    if (!svg || !report || asked !== key()) return;
    const board = svg.parentElement, bounds = board.getBoundingClientRect();
    svg.setAttribute("viewBox", `0 0 ${bounds.width} ${bounds.height}`);
    svg.replaceChildren();
    const defs = document.createElementNS(NS, "defs"), marker = document.createElementNS(NS, "marker");
    marker.setAttribute("id", "c4-arrow"); marker.setAttribute("viewBox", "0 0 10 10");
    marker.setAttribute("refX", "9"); marker.setAttribute("refY", "5"); marker.setAttribute("markerWidth", "6"); marker.setAttribute("markerHeight", "6"); marker.setAttribute("orient", "auto-start-reverse");
    const tip = document.createElementNS(NS, "path"); tip.setAttribute("d", "M 0 0 L 10 5 L 0 10 z"); marker.append(tip); defs.append(marker); svg.append(defs);
    const cards = new Map([...board.querySelectorAll("[data-c4-node]")].map((card) => [card.dataset.c4Node, card]));
    for (const relationship of report.levels[level].relationships) {
      const source = cards.get(relationship.source), target = cards.get(relationship.target);
      if (!source || !target) continue;
      const a = source.getBoundingClientRect(), b = target.getBoundingClientRect();
      const horizontal = Math.abs(a.left - b.left) > Math.abs(a.top - b.top);
      const x1 = (horizontal ? a.left < b.left ? a.right : a.left : a.left + a.width / 2) - bounds.left;
      const x2 = (horizontal ? a.left < b.left ? b.left : b.right : b.left + b.width / 2) - bounds.left;
      const y1 = (horizontal ? a.top + a.height / 2 : a.top < b.top ? a.bottom : a.top) - bounds.top;
      const y2 = (horizontal ? b.top + b.height / 2 : a.top < b.top ? b.top : b.bottom) - bounds.top;
      const path = document.createElementNS(NS, "path");
      path.setAttribute("d", `M ${x1} ${y1} C ${(x1 + x2) / 2} ${y1} ${(x1 + x2) / 2} ${y2} ${x2} ${y2}`);
      path.setAttribute("class", "c4-edge" + (selected && (relationship.source === selected || relationship.target === selected) ? " selected" : ""));
      path.setAttribute("marker-end", "url(#c4-arrow)");
      const title = document.createElementNS(NS, "title"); title.textContent = `${relationship.label} · ${relationship.mechanism}`; path.append(title); svg.append(path);
    }
  }

  function inspect(id) {
    if (!report || asked !== key()) return;
    const view = report.levels[level], node = view.nodes.find((item) => item.id === id);
    if (!node) return;
    selected = id;
    for (const card of $("c4-map").querySelectorAll("[data-c4-node]")) card.setAttribute("aria-pressed", String(card.dataset.c4Node === id));
    const box = $("c4-inspector");
    box.replaceChildren(P.el("p", SUPPORT[node.support] || node.support, { class: "c4-eyebrow" }), P.el("h3", node.name),
      P.el("p", node.technology, { class: "c4-technology" }), P.el("p", node.summary));
    if (node.drill) box.append(button("Explore " + (node.drill === "containers" ? "containers" : "server components") + " →", () => showLevel(node.drill, true), { id: "c4-drill" }));
    const sources = P.el("ul", undefined, { class: "c4-sources" });
    for (const source of node.sources) sources.append(P.el("li", source));
    box.append(P.el("h4", "Source of this element"), sources);
    const relations = view.relationships.filter((item) => item.source === id || item.target === id);
    const links = P.el("ul", undefined, { class: "c4-relationships" });
    for (const relation of relations) {
      const other = relation.source === id ? relation.target : relation.source;
      const otherNode = view.nodes.find((item) => item.id === other);
      const item = P.el("li");
      item.append(button((relation.source === id ? "→ " : "← ") + otherNode.name, () => inspect(other), { "data-c4-related": other }),
        P.el("span", relation.label || relation.mechanism), P.el("small", relation.mechanism + " · " + (SUPPORT[relation.support] || relation.support)));
      links.append(item);
    }
    box.append(P.el("h4", "Relationships"), links.children.length ? links : P.el("p", "No sourced relationship in this view."));
    const facts = P.el("dl", undefined, { class: "c4-facts" });
    for (const [name, value] of Object.entries(node.details)) {
      facts.append(P.el("dt", name.replaceAll("_", " ")));
      const detail = P.el("dd");
      if (Array.isArray(value)) {
        const list = P.el("ul", undefined, { class: "c4-detail-list" });
        for (const item of value) {
          const text = typeof item === "object" ? item.action
            ? `${item.action}: ${item.from_state} → ${item.to_state} · ${item.role}`
            : `${item.name}: ${(item.files || []).join(", ") || "Installed library"}` : String(item);
          list.append(P.el("li", text));
        }
        detail.append(value.length ? list : P.el("span", "None"));
      } else detail.textContent = String(value ?? "Not declared");
      facts.append(detail);
    }
    box.append(P.el("h4", "Declared detail"), facts);
    if (node.support === "fixture_contract") box.append(P.el("p", "Fixture identity only. No authentication, external connector or scheduler is generated.", { class: "c4-warning" }));
    if (node.id === "app/data.json" && report.data_support) box.append(P.el("p", report.data_support.limits.join(" "), { class: "c4-warning" }));
    drawEdges();
  }

  function init(bridge) {
    P = bridge;
    if (!$("c4-panel")) return;
    setup();
    P.hooks.tab.push((which) => { if (which === "c4") refresh(); });
    P.hooks.redraw.push(() => { if (P.tab() === "c4") refresh(); });
    document.addEventListener("playide:built", () => { if (report && asked === key()) freshness(); });
    window.PlayC4 = { open: (next = "context") => { showLevel(next); P.showTab("c4"); }, refresh: () => refresh(true),
      current: () => report && asked === key() ? report : null };
  }
  if (window.PlayIDE) init(window.PlayIDE);
})();
