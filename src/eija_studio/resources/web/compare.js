"use strict";
// Read-only paired projections. The server snapshots remain the only model authority.
const EijaCompare = (() => {
  const NS = "http://www.w3.org/2000/svg", nodeWidth = 190, nodeHeight = 76;
  const transitionFields = [["action", "Action"], ["role", "Role"], ["from_state", "Source state"],
    ["to_state", "Target state"], ["guards", "Guards"], ["required_effects", "Required effects"], ["forbidden_effects", "Forbidden effects"]];
  const statusLabel = {added: "+ Added", removed: "− Removed", changed: "◇ Modified", unchanged: "= Unchanged"};
  let serial = 0;
  const keyOf = item => `${item.kind}:${item.id}`;
  const same = (a, b) => a?.case === b?.case && a?.revision === b?.revision;
  const textValue = value => value === undefined || value === null ? "Not present" :
    Array.isArray(value) ? value.length ? JSON.stringify(value, null, 2) : "[] (none declared)" : String(value);
  function engines() {
    if (typeof EijaReview === "undefined" || typeof EijaCanvas === "undefined") throw new Error("The bundled review and diagram adapters are unavailable.");
    return {review: EijaReview, canvas: EijaCanvas};
  }
  function validate(model) {
    if (!model || !Array.isArray(model.states) || !Array.isArray(model.transitions)) throw new Error("A complete server model is required for comparison.");
    const states = new Set(model.states), ids = new Set();
    if (states.size !== model.states.length) throw new Error("Duplicate state identity in comparison snapshot.");
    for (const t of model.transitions) {
      if (ids.has(t.id)) throw new Error("Duplicate transition identity in comparison snapshot.");
      if (!states.has(t.from_state) || !states.has(t.to_state)) throw new Error("A transition endpoint is absent from its comparison snapshot.");
      ids.add(t.id);
    }
    if (model.initial_state !== undefined && !states.has(model.initial_state)) throw new Error("The initial state is absent from its comparison snapshot.");
  }
  function inventory(before, after) {
    validate(before); validate(after);
    const diff = engines().review.compare(before, after), items = [];
    for (const change of diff.transitions) {
      const changed = new Set(change.changes.map(([key]) => key));
      items.push({...change, kind: "transition", key: `transition:${change.id}`, fields: transitionFields.map(([key, label]) =>
        ({key, label, before: change.before?.[key], after: change.after?.[key], changed: changed.has(key)}))});
    }
    const old = new Set(before.states), next = new Set(after.states);
    for (const id of [...new Set([...old, ...next])].sort()) {
      const status = !old.has(id) ? "added" : !next.has(id) ? "removed" : "unchanged";
      items.push({kind: "state", id, key: `state:${id}`, status, before: old.has(id) ? id : undefined, after: next.has(id) ? id : undefined,
        fields: [{key: "membership", label: "State membership", before: old.has(id) ? "Present" : undefined, after: next.has(id) ? "Present" : undefined, changed: status !== "unchanged"}]});
    }
    items.push({kind: "initial", id: "initial_state", key: "initial:initial_state", status: diff.initialChanged ? "changed" : "unchanged",
      before: before.initial_state, after: after.initial_state,
      fields: [{key: "initial_state", label: "Initial state", before: before.initial_state, after: after.initial_state, changed: diff.initialChanged}]});
    return {items, changes: items.filter(item => item.status !== "unchanged"), diff};
  }
  function project(before, after, options = {}) {
    const changes = inventory(before, after), variants = [], labelBoxes = new Map(), routeIds = {before: new Map(), after: new Map()};
    for (const item of changes.diff.transitions) {
      const a = item.before, b = item.after, shared = a && b && a.from_state === b.from_state && a.to_state === b.to_state;
      const add = (t, sides) => {
        const id = `projection-${variants.length}`, longest = [a?.action || "", b?.action || ""].sort((x, y) => y.length - x.length || x.localeCompare(y))[0];
        variants.push({id, from_state: t.from_state, to_state: t.to_state, action: longest});
        // Reserve the full two-line baseline/stroke envelope; width keeps the existing
        // font estimate, including a longer status caption and both snapshot actions.
        labelBoxes.set(id,{width:Math.max(70,longest.length*8+8,item.status==="unchanged"?0:statusLabel[item.status].length*7+8),height:item.status==="unchanged"?24:48});
        for (const side of sides) routeIds[side].set(item.id, id);
      };
      if (shared) add(a, ["before", "after"]);
      else { if (a) add(a, ["before"]); if (b) add(b, ["after"]); }
    }
    const union = {states: [...new Set([...before.states, ...after.states])].sort(), transitions: variants};
    // Dagre owns positions and routes. This union is disposable display data, never a Workflow update.
    const shared = engines().canvas.projectLayout(union, {}, options.direction || "TB", options.viewport || {width: 500, height: 400}, labelBoxes);
    const status = new Map(changes.items.map(item => [item.key, item.status]));
    const side = (model, name) => ({
      nodes: [...model.states].sort().map(id => ({id, ...shared.coords[id], width: nodeWidth, height: nodeHeight, initial: id === model.initial_state, status: status.get(`state:${id}`)})),
      edges: [...model.transitions].sort((a, b) => a.id.localeCompare(b.id)).map(t => ({...t, status: status.get(`transition:${t.id}`),
        points: shared.routes[routeIds[name].get(t.id)].points.map(p => ({...p})), label: {...shared.routes[routeIds[name].get(t.id)].label}}))
    });
    return {before: side(before, "before"), after: side(after, "after"), bounds: {...shared.bounds}, direction: shared.direction, inventory: changes};
  }
  function restoreState(subject, list, saved) {
    const valid = same(subject, saved?.subject), selected = valid && list.items.find(item => item.kind === saved.selected?.kind && item.id === saved.selected?.id);
    const v = valid && saved.viewport;
    return {subject: {...subject}, selected: selected ? {kind: selected.kind, id: selected.id} : null,
      viewport: v && [v.cx, v.cy, v.scale].every(Number.isFinite) && v.scale >= 0.01 && v.scale <= 2 ? {...v} : null,
      direction: valid && ["TB", "LR"].includes(saved.direction) ? saved.direction : "TB"};
  }
  function bindings(item, terms = []) {
    const refs = new Set(item.kind === "initial" ? [item.before, item.after].filter(Boolean).map(id => `state:${id}`) : [keyOf(item)]);
    return [...new Set(terms.filter(term => (term.refs || []).some(ref => refs.has(ref))).flatMap(term => term.binds || []).filter(ref => typeof ref === "string"))].sort();
  }
  function impactNavigation(reference, before, after) {
    const unavailable = reason => ({reference, label:"No direct destination", scope:"unresolved", target:null, reason});
    const evidence = (section, label) => ({reference, label, scope:"Case-wide evidence; this projection reference is not an individual receipt or verdict.", target:{view:"evidence", section}});
    if (reference === "review-packet") return evidence("overview", "Open case-wide Evidence");
    if (reference === "local-decision") return evidence("decision", "Open local review location");
    if (typeof reference !== "string") return unavailable("Invalid projection reference.");
    const colon = reference.indexOf(":"), kind = reference.slice(0, colon), action = reference.slice(colon + 1);
    if (colon < 1 || !action || !["rule", "runtime", "state-view", "journey", "obligation", "receipt"].includes(kind)) return unavailable("No declared navigation for this projection reference.");
    const matches = [...(before?.transitions || []), ...(after?.transitions || [])].filter(item => item.action === action);
    const ids = [...new Set(matches.map(item => item.id))];
    if (!ids.length) return unavailable("This action is absent from both model snapshots.");
    if (ids.length !== 1) return unavailable("This action names multiple transition identities; no destination was selected.");
    if (["rule", "state-view"].includes(kind)) return {reference, label:"Inspect exact model change", scope:"Baseline and candidate snapshots; no repository binding is inferred.", target:{view:"review", kind:"transition", id:ids[0]}};
    if (["obligation", "receipt"].includes(kind)) return evidence("overview", "Open case-wide Evidence");
    if (!(after?.transitions || []).some(item => item.id === ids[0] && item.action === action)) return unavailable("This action exists only in the baseline; no candidate runtime or journey destination is available.");
    return kind === "runtime" ? {reference, label:"Open Run view", scope:"Candidate preview controls only; navigation does not start or execute a preview.", target:{view:"try", action}} :
      {reference, label:"Open case-wide rules and journeys", scope:"Current candidate projections for the whole case; no source binding or complete behavioral impact is implied.", target:{view:"impact", action}};
  }
  function element(tag, content, cls) {
    const node = document.createElement(tag); if (content !== undefined) node.textContent = String(content); if (cls) node.className = cls; return node;
  }
  function svg(tag, attrs = {}, content) {
    const node = document.createElementNS(NS, tag); for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, String(value));
    if (content !== undefined) node.textContent = content; return node;
  }
  function button(label, callback, action) {
    const node = element("button", label); node.type = "button"; node.onclick = callback; if (action) node.dataset.compareAction = action; return node;
  }
  function itemTitle(item) { return item.kind === "transition" ? `${(item.after || item.before).action} · ${item.id}` : item.kind === "initial" ? "Initial state" : item.id; }
  function fieldTable(fields, preview = false) {
    const table = element("table", undefined, "compare-fields"), head = element("thead"), row = element("tr"), body = element("tbody");
    for (const label of ["Field", preview ? "Captured before" : "Before · baseline", preview ? "Proposed result" : "After · candidate"]) {const th = element("th", label); th.scope = "col"; row.append(th);}
    head.append(row); table.append(head, body);
    for (const field of fields) {
      const tr = element("tr"), th = element("th", field.label); th.scope = "row"; tr.dataset.field = field.key;
      tr.append(th, element("td", textValue(field.before)), element("td", textValue(field.after))); body.append(tr);
    }
    const wrap = element("div", undefined, "compare-table-wrap"); wrap.tabIndex = 0; wrap.setAttribute("role", "region"); wrap.setAttribute("aria-label", "Exact before and after values"); wrap.append(table); return wrap;
  }
  function buildSelectedSummary(s) {
    const preview = s.callbacks.preview, summary = element("section", undefined,
      "compare-selected-fields " + (preview ? "compare-preview-fields" : "compare-change-summary"));
    summary.setAttribute("role", "region");
    summary.setAttribute("aria-label", preview ? "Selected element changes, captured before to proposed result" : "Selected element changes, baseline to candidate");
    if (preview) {s.previewSummary = summary; s.shell.append(summary);}
    else {s.changeSummary = summary; s.visual.append(summary);}
  }
  function render(root, current, callbacks = {}) {
    root.replaceChildren();
    if (!current?.case?.candidate) {root.append(element("p", current ? "Choose an interpretation in Intent to compare its exact model changes." : "Open a change case to compare its baseline and candidate.", "compare-empty")); return {destroy() {}};}
    const c = current.case, subject = {case: c.id, revision: c.version}, shell = element("section", undefined, "paired-compare");
    shell.dataset.case = c.id; shell.dataset.revision = c.version; shell.dataset.compareView = "manual"; root.append(shell);
    let layout;
    const direction = same(subject, callbacks.state?.subject) && ["TB", "LR"].includes(callbacks.state?.direction) ? callbacks.state.direction : "TB";
    try {layout = project(c.baseline, c.candidate, {direction});}
    catch (error) {const notice = element("p", error.message, "compare-empty"); notice.setAttribute("role", "alert"); shell.append(notice); return {destroy() {}};}
    const state = restoreState(subject, layout.inventory, callbacks.state), prefix = `paired-${++serial}`;
    if (!state.selected) {const first = layout.inventory.changes[0] || layout.inventory.items[0]; state.selected = first ? {kind: first.kind, id: first.id} : null;}
    const session = {shell, c, packet: current.packet || {}, subject, state, layout, callbacks, prefix, panes: [], buttons: [], groups: [], stopped: false};
    const getState = () => ({subject: {...subject}, selected: state.selected && {...state.selected}, viewport: state.viewport && {...state.viewport}, direction: state.direction, viewMode: shell.dataset.compareView});
    session.notify = () => callbacks.onStateChange?.(getState());
    session.selected = () => layout.inventory.items.find(item => item.kind === state.selected?.kind && item.id === state.selected?.id);
    session.select = (reference, focus = true) => {
      const item = layout.inventory.items.find(value => value.kind === reference.kind && value.id === reference.id); if (!item) return false;
      state.selected = {kind: item.kind, id: item.id}; updateSelection(session); selectionViewport(session, focus); session.notify();
      callbacks.onSelection?.({...subject, ...state.selected}, item); return true;
    };
    session.visual = element("div", undefined, "compare-visual-workspace");
    buildSelectedSummary(session); shell.append(session.visual);
    buildHeader(session); buildNavigator(session); buildPair(session); buildDetails(session); buildContext(session);
    updateSelection(session);
    initializeViewport(session, callbacks.state);
    const observer = typeof ResizeObserver === "undefined" ? null : new ResizeObserver(() => refreshViewport(session));
    for (const pane of session.panes) observer?.observe(pane.host);
    session.notify(); callbacks.onSelection?.({...subject, ...state.selected}, session.selected());
    return {getState, select: session.select, fit: () => fit(session), focus: () => focusSelection(session),
      setViewport: value => setViewport(session, value), destroy() {session.stopped = true; observer?.disconnect(); session.navigator?.remove();}};
  }
  function buildHeader(s) {
    const header = element("header", undefined, "compare-header"); header.append(element("h2", s.callbacks.preview ? "Captured edit comparison" : `Changes · revision ${s.c.version}`));
    const tools = element("div", undefined, "compare-tools"); tools.setAttribute("aria-label", "Synchronized comparison view"); tools.setAttribute("role", "group");
    tools.append(button(s.callbacks.preview ? "Focus selection" : "Fit selection", () => focusSelection(s), "focus"), button("100%", () => setViewport(s, {...s.state.viewport, scale: 1}), "readable"),
      button("−", () => zoom(s, 1 / 1.2), "zoom-out"), button("+", () => zoom(s, 1.2), "zoom-in"), button("Overview", () => fit(s), "overview"));
    tools.querySelector('[data-compare-action="zoom-out"]').setAttribute("aria-label", "Zoom out both diagrams");
    tools.querySelector('[data-compare-action="zoom-in"]').setAttribute("aria-label", "Zoom in both diagrams");
    s.scale = element("output", "100%"); s.scale.dataset.compareScale = ""; s.scale.setAttribute("aria-label", "Shared diagram scale"); tools.append(s.scale);
    const help = element("details", undefined, "compare-help"); help.append(element("summary", "View help"), element("p", (s.callbacks.preview ? "Read-only captured before and proposed result snapshots share positions and zoom. " : "Read-only baseline and candidate snapshots share positions and zoom. ") + (s.callbacks.preview ? "Focus shows the selected endpoints, route and labels. Home focuses the selection. Focus and Overview may reduce text size. " : "Selections open at 100%; some content may require panning. Fit selection shows the selected endpoints, route and labels, and Home fits the selection. Fit selection and Overview may reduce text size. ") + "Drag empty space or use arrow keys to pan; plus/minus zoom. 100% restores readable scale."));
    help.addEventListener("keydown", event => {if (event.key === "Escape") {help.open = false; help.querySelector("summary").focus(); event.stopPropagation();}});
    s.scaleHint = element("span", "", "compare-scale-hint"); s.scaleHint.setAttribute("role", "status");
    if(s.callbacks.openNavigator)tools.prepend(button("All changes",s.callbacks.openNavigator,"navigator"));
    header.append(tools, help, s.scaleHint); s.visual.append(header);
  }
  function buildNavigator(s) {
    const nav = element("nav", undefined, "compare-navigator"); nav.setAttribute("aria-label", "Model change navigator");
    if (s.callbacks.navigatorRoot) nav.classList.add("compare-navigator-external");
    const label = element("p", `${s.layout.inventory.changes.length} model changes`, "compare-inventory"); nav.append(label);
    const append = (target, item) => {
      const node = button(`${statusLabel[item.status]} · ${itemTitle(item)}`, () => s.select(item)); node.dataset.compareKey = item.key;
      target.append(node); s.buttons.push({node, item});
    };
    const list = element("div", undefined, "compare-change-list"); list.tabIndex = 0; list.setAttribute("role", "region"); list.setAttribute("aria-label", "All changed model elements");
    for (const item of s.layout.inventory.changes) append(list, item);
    if (!s.layout.inventory.changes.length) list.append(element("p", "No model differences in these snapshots.")); nav.append(list);
    const unchanged = s.layout.inventory.items.filter(item => item.status === "unchanged"), details = element("details");
    details.append(element("summary", `${unchanged.length} unchanged items`));
    const extra = element("div", undefined, "compare-change-list"); for (const item of unchanged) append(extra, item); details.append(extra); nav.append(details); (s.callbacks.navigatorRoot || s.visual).append(nav); s.navigator = nav;
    nav.addEventListener("keydown", event => {
      if (!["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key) || event.target.tagName !== "BUTTON") return;
      const available = s.buttons.filter(({node}) => !node.closest("details") || node.closest("details").open), index = available.findIndex(({node}) => node === event.target);
      if (index < 0) return; event.preventDefault(); const next = event.key === "Home" ? 0 : event.key === "End" ? available.length - 1 : (index + (event.key === "ArrowDown" ? 1 : -1) + available.length) % available.length;
      available[next].node.focus(); s.select(available[next].item);
    });
  }
  function buildPair(s) {
    const pair = element("div", undefined, "compare-pair");
    for (const [side, title] of [["before", s.callbacks.preview ? "Captured before" : "Before · baseline"], ["after", s.callbacks.preview ? "Proposed result" : "After · candidate"]]) {
      const pane = element("section", undefined, "compare-pane"); pane.dataset.compareSide = side; pane.setAttribute("aria-label", title);
      const heading = element("h3", title), presence = element("p", "", "compare-presence"), host = element("div", undefined, "compare-graph");
      const board = svg("svg", {class: "compare-svg", role: "group", tabindex: 0, "aria-label": `${title} model diagram. Arrow keys pan both diagrams; plus and minus zoom.`});
      board.append(svg("desc", {}, "A read-only projection of this snapshot. Select states or transitions to inspect exact values. Shared geometry does not establish behavioral conformance."));
      const markerId = `${s.prefix}-${side}-arrow`, defs = svg("defs"), marker = svg("marker", {id: markerId, viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: "auto"});
      marker.append(svg("path", {d: "M0 0 L10 5 L0 10z"})); defs.append(marker); board.append(defs);
      for (const edge of s.layout[side].edges) drawEdge(s, board, edge, markerId);
      for (const node of s.layout[side].nodes) drawNode(s, board, node);
      host.append(board); pane.append(heading, presence, host); pair.append(pane); s.panes.push({side, board, host, presence}); attachPan(s, board);
    }
    s.visual.append(pair);
  }
  function selectable(s, group, item) {
    group.setAttribute("role", "button"); group.setAttribute("tabindex", "0"); group.setAttribute("aria-pressed", "false");
    group.addEventListener("click", () => s.select(item, false));
    group.addEventListener("keydown", event => {if (["Enter", " "].includes(event.key)) {event.preventDefault(); event.stopPropagation(); s.select(item, false);}});
    s.groups.push({node: group, item});
  }
  function drawEdge(s, board, edge, markerId) {
    const item = s.layout.inventory.items.find(value => value.key === `transition:${edge.id}`), path = edge.points.map((p, i) => `${i ? "L" : "M"} ${p.x} ${p.y}`).join(" ");
    const group = svg("g", {class: `compare-edge ${edge.status}`, "data-transition": edge.id, "data-eija-id": `transition:${edge.id}`,
      "data-source": edge.from_state, "data-target": edge.to_state, "data-status": edge.status,
      "aria-label": `${statusLabel[edge.status]}, ${edge.action}, ${edge.role}, ${edge.from_state} to ${edge.to_state}`});
    group.append(svg("path", {d: path, class: "compare-edge-hit"}), svg("path", {d: path, class: "compare-edge-line", "marker-end": `url(#${markerId})`}),
      svg("text", {x: edge.label.x, y: edge.label.y + (edge.status === "unchanged" ? 5 : -8), "text-anchor": "middle", class: "compare-edge-label"}, edge.action));
    if(edge.status !== "unchanged")group.append(svg("text", {x: edge.label.x, y: edge.label.y + 10, "text-anchor": "middle", class: "compare-status-label"}, statusLabel[edge.status]));
    selectable(s, group, item); board.append(group);
  }
  function drawNode(s, board, node) {
    const item = s.layout.inventory.items.find(value => value.key === `state:${node.id}`), group = svg("g", {class: `compare-node ${node.status}`, "data-state": node.id,
      "data-eija-id": `state:${node.id}`, "data-initial": node.initial, "data-status": node.status, "aria-label": `${node.id}, ${statusLabel[node.status]}${node.initial ? ", initial state" : ""}`});
    group.append(svg("rect", {x: node.x, y: node.y, width: node.width, height: node.height, rx: 12, class: "compare-state-box"}),
      svg("text", {x: node.x + 12, y: node.y + 29, class: "compare-state-label"}, node.id));
    const secondary=[node.initial?"● Initial":"",node.status!=="unchanged"?statusLabel[node.status]:""].filter(Boolean).join(" · ");
    if(secondary)group.append(svg("text", {x: node.x + 12, y: node.y + 54, class: `compare-status-label${node.initial ? " compare-initial-label" : ""}`}, secondary));
    const title = svg("title", {}, node.id); group.append(title); selectable(s, group, item); board.append(group);
  }
  function buildDetails(s) {
    s.detail = element("section", undefined, "compare-selection"); s.detail.setAttribute("aria-label", "Selected model element and exact differences");
    s.announcement = element("p", "", "compare-announcement"); s.announcement.setAttribute("role", "status"); s.announcement.setAttribute("aria-live", "polite");
    s.shell.append(s.announcement, s.detail);
  }
  function updateSelection(s) {
    const item = s.selected(); if (!item) return;
    for (const {node, item: value} of [...s.buttons, ...s.groups]) {
      const selected = value.key === item.key || item.kind === "initial" && value.kind === "state" && [item.before, item.after].includes(value.id);
      node.setAttribute("aria-pressed", String(selected)); node.classList.toggle("selected", selected);
    }
    for (const pane of s.panes) pane.presence.textContent = `${itemTitle(item)} · ${item[pane.side] === undefined ? "Not present in this snapshot" : statusLabel[item.status]}`;
    s.detail.replaceChildren(); s.detail.dataset.kind = item.kind; s.detail.dataset.id = item.id;
    s.detail.append(element("h3", `${statusLabel[item.status]} · ${itemTitle(item)}`));
    const changed = item.fields.filter(field => field.changed), unchanged = item.fields.filter(field => !field.changed);
    if (changed.length) s.detail.append(fieldTable(changed, s.callbacks.preview));
    if (unchanged.length) {const details = element("details"); details.open = !changed.length; details.append(element("summary", `${unchanged.length} unchanged fields`), fieldTable(unchanged, s.callbacks.preview)); s.detail.append(details);}
    const summary = s.previewSummary || s.changeSummary;
    if (summary) {
      summary.replaceChildren(); Object.assign(summary.dataset, {kind: item.kind, id: item.id});
      if (s.callbacks.preview) summary.append(element("span", "Selected element’s changes", "compare-preview-scope"));
      else {
        Object.assign(summary.dataset, {case: s.subject.case, revision: String(s.subject.revision)});
        const heading = element("header", undefined, "compare-summary-heading");
        heading.append(element("h3", `${statusLabel[item.status]} · ${itemTitle(item)}`),
          element("span", `Before · baseline → After · candidate · revision ${s.subject.revision}`, "compare-summary-scope"));
        heading.title = `Case ${s.subject.case} · revision ${s.subject.revision}`; summary.append(heading);
      }
      for (const field of changed) {
        const row = element("p"), before = element("span", textValue(field.before)), after = element("span", textValue(field.after));
        row.dataset.field = field.key; before.dataset.compareBefore = ""; after.dataset.compareAfter = "";
        row.append(element("strong", `${field.label}: `), before, element("span", " → "), after); summary.append(row);
      }
      if (!changed.length) summary.append(element("p", "No changed fields for this selected element."));
    }
    if (s.callbacks.preview) {
      s.announcement.textContent = `${statusLabel[item.status]} ${itemTitle(item)} selected. Captured edit comparison for revision ${s.subject.revision}.`; return;
    }
    const related = element("div", undefined, "compare-related"), refs = bindings(item, s.callbacks.terms || []);
    if (!refs.length) related.append(element("p", "Source binding unknown: no declared binding for this selected element."));
    for (const ref of refs) {const open = button(`Open bound source · ${ref}`, () => s.callbacks.openReference?.(ref, {...s.subject, ...s.state.selected})); open.disabled = !s.callbacks.openReference; open.dataset.compareReference = ref; related.append(open);}
    const evidence = button("Inspect evidence for this revision", () => s.callbacks.openEvidence?.({...s.subject, ...s.state.selected}), "evidence"); evidence.disabled = !s.callbacks.openEvidence; related.append(evidence);
    if (item.kind === "transition" && item.after && s.callbacks.inspectTransition) related.append(button("Inspect in model", () => {if (!s.stopped) s.callbacks.inspectTransition(item.id, {...s.subject, ...s.state.selected});}, "inspect-model"));
    s.detail.append(related); s.announcement.textContent = `${statusLabel[item.status]} ${itemTitle(item)} selected. Case revision ${s.subject.revision}.`;
  }
  function buildContext(s) {
    if (s.callbacks.preview) return;
    const context = element("section", undefined, "compare-context"), impact = element("details"), affected = s.packet.impact?.affected || [];
    impact.append(element("summary", `Case-wide known impact · ${affected.length} reported references`), element("p", s.packet.impact?.complete ?
      "Dependency closure is complete only within the declared mapping. This list is case-wide, not a claim about the selected element or complete behavioral impact." :
      "Dependency closure is unavailable or incomplete. This case-wide list is not a selected-element or complete behavioral-impact claim."));
    for (const ref of affected) {
      const navigation = impactNavigation(ref, s.c.baseline, s.c.candidate);
      if (!navigation.target) {const note = element("p", `${ref} · ${navigation.reason}`); note.dataset.compareImpactUnavailable = ref; impact.append(note); continue;}
      const open = button(`${ref} · ${navigation.label}`, () => {if (!s.stopped) s.callbacks.openImpact?.(navigation, {...s.subject, ...s.state.selected});});
      open.disabled = !s.callbacks.openImpact; open.dataset.compareImpact = ref; open.title = navigation.scope; impact.append(open);
    }
    const evidence = element("details"); evidence.append(element("summary", "Revision evidence, blockers and limits"), element("p", s.packet.eligible ? "Technically eligible within the declared scope." : "Technical review is blocked."));
    for (const entry of s.packet.formal_evidence || []) evidence.append(element("p", `${entry.kind} · ${entry.status}`));
    if (!(s.packet.formal_evidence || []).length) evidence.append(element("p", "Checks: NOT_RUN"));
    for (const code of s.packet.blockers || []) evidence.append(element("p", code));
    evidence.append(element("p", "Human comprehension: UNKNOWN. Synthetic checks do not demonstrate reviewer benefit."));
    const transactions = element("details"); transactions.append(element("summary", `${(s.c.transactions || []).length} typed transactions retained by the server`));
    for (const tx of s.c.transactions || []) transactions.append(element("pre", JSON.stringify(tx, null, 2)));
    context.append(impact, evidence, transactions); s.shell.append(context);
  }
  function dimensions(s) {const sizes = s.panes.map(pane => ({width: pane.host.clientWidth, height: pane.host.clientHeight})); return sizes.every(size => size.width > 0 && size.height > 0) ? sizes : null;}
  function setViewport(s, value, mode = "manual") {
    if (![value?.cx, value?.cy, value?.scale].every(Number.isFinite)) return false;
    s.state.viewport = {cx: value.cx, cy: value.cy, scale: Math.max(0.01, Math.min(2, value.scale))};
    s.shell.dataset.compareView = mode; updateViewport(s); s.notify(); return true;
  }
  function updateViewport(s) {
    if (s.stopped || !s.state.viewport) return;
    const {cx, cy, scale} = s.state.viewport, sizes = dimensions(s); if (!sizes) return;
    for (let i = 0; i < s.panes.length; i++) {const size = sizes[i], w = size.width / scale, h = size.height / scale; s.panes[i].board.setAttribute("viewBox", `${cx - w / 2} ${cy - h / 2} ${w} ${h}`);}
    s.scale.value = `${Math.round(scale * 100)}%`; s.scale.textContent = s.scale.value;
    s.scaleHint.textContent = scale < 0.9 ? "Reduced scale · use 100% and pan to read labels." : "Read-only comparison";
  }
  function zoom(s, factor) {if (s.state.viewport) setViewport(s, {...s.state.viewport, scale: s.state.viewport.scale * factor});}
  function fit(s) {
    const sizes = dimensions(s); if (!sizes) {s.shell.dataset.compareView = "overview"; return;}
    setViewport(s, frameBounds(s.layout.bounds, sizes), "overview");
  }
  function selectedNodeIds(item) {
    return new Set(item.kind === "transition" ? [item.before?.from_state, item.before?.to_state, item.after?.from_state, item.after?.to_state] : item.kind === "state" ? [item.id] : [item.before, item.after]);
  }
  function selectionBounds(layout, item, painted = []) {
    const ids = selectedNodeIds(item), boxes = [...painted];
    for (const side of [layout.before, layout.after]) {
      for (const node of side.nodes) if (ids.has(node.id)) boxes.push(node);
      for (const edge of side.edges) if (item.kind === "transition" && edge.id === item.id) {
        for (const point of [...edge.points, edge.label]) boxes.push({...point, width: 0, height: 0});
      }
    }
    if (!boxes.length) return layout.bounds;
    const x = Math.min(...boxes.map(box => box.x)), y = Math.min(...boxes.map(box => box.y));
    return {x, y, width: Math.max(...boxes.map(box => box.x + box.width)) - x, height: Math.max(...boxes.map(box => box.y + box.height)) - y};
  }
  function frameBounds(box, sizes, padding = 20) {
    const scale = Math.min(1, ...sizes.map(size => Math.min(Math.max(1, size.width - padding * 2) / Math.max(1, box.width), Math.max(1, size.height - padding * 2) / Math.max(1, box.height))));
    return {cx: box.x + box.width / 2, cy: box.y + box.height / 2, scale};
  }
  function defaultSelection(s) {focusSelection(s, Boolean(s.callbacks.preview));}
  function selectionViewport(s, focus) {
    if (focus) defaultSelection(s);
    else if (!s.callbacks.preview && ["readable", "focus"].includes(s.shell.dataset.compareView)) s.shell.dataset.compareView = "manual";
  }
  function initializeViewport(s, saved) {
    const pending = saved?.viewport === null && ["focus", "overview", "readable"].includes(saved?.viewMode);
    s.shell.dataset.compareView = same(s.subject, saved?.subject) && (s.state.viewport || pending) ? saved.viewMode || "manual" : "manual";
    refreshViewport(s);
  }
  function refreshViewport(s) {
    if (s.stopped) return;
    const mode = s.shell.dataset.compareView;
    if (mode === "focus") focusSelection(s);
    else if (mode === "overview") fit(s);
    else if (mode === "readable") focusSelection(s, false);
    else if (!s.state.viewport) defaultSelection(s);
    else updateViewport(s);
  }
  function focusSelection(s, fitSelection = true) {
    const item = s.selected(); if (!item) return;
    const mode = fitSelection ? "focus" : "readable";
    const sizes = dimensions(s); if (!sizes) {s.shell.dataset.compareView = mode; return;}
    const ids = selectedNodeIds(item), painted = [];
    for (const group of s.groups) if (group.item.key === item.key || group.item.kind === "state" && ids.has(group.item.id)) {
      try {const box = group.node.getBBox(); if (box.width > 0 || box.height > 0) painted.push(box);} catch {/* Hidden SVG falls back to projection bounds until its resize notification. */}
    }
    const viewport = frameBounds(selectionBounds(s.layout, item, painted), sizes);
    setViewport(s, fitSelection ? viewport : {...viewport, scale: 1}, mode);
  }
  function attachPan(s, board) {
    board.addEventListener("keydown", event => {
      if (event.target !== board || !s.state.viewport) return;
      const delta = {ArrowLeft: [-60, 0], ArrowRight: [60, 0], ArrowUp: [0, -60], ArrowDown: [0, 60]}[event.key];
      if (delta) {event.preventDefault(); const v = s.state.viewport; setViewport(s, {...v, cx: v.cx + delta[0] / v.scale, cy: v.cy + delta[1] / v.scale});}
      else if (["+", "=", "-"].includes(event.key)) {event.preventDefault(); zoom(s, event.key === "-" ? 1 / 1.2 : 1.2);}
      else if (event.key === "Home") {event.preventDefault(); focusSelection(s);}
    });
    board.addEventListener("pointerdown", event => {
      if (event.button !== 0 || event.target.closest("[data-eija-id]") || !s.state.viewport) return;
      event.preventDefault(); board.focus(); board.setPointerCapture(event.pointerId); const start = {x: event.clientX, y: event.clientY, ...s.state.viewport};
      const move = e => setViewport(s, {cx: start.cx - (e.clientX - start.x) / start.scale, cy: start.cy - (e.clientY - start.y) / start.scale, scale: start.scale});
      const end = () => {board.removeEventListener("pointermove", move); board.removeEventListener("pointerup", end); board.removeEventListener("pointercancel", end); if (board.hasPointerCapture(event.pointerId)) board.releasePointerCapture(event.pointerId);};
      board.addEventListener("pointermove", move); board.addEventListener("pointerup", end); board.addEventListener("pointercancel", end);
    });
  }
  return {render, inventory, project, restoreState, bindings, impactNavigation, selectionBounds, frameBounds};
})();
if (typeof module !== "undefined") module.exports = EijaCompare;
