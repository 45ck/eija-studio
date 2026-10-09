// PlayIDE Changes (ADR-0176): how a UML change looks. The server returns the union of the model in force and the
// change shown (a change case's candidate and any accepted plan steps), each element with its status; this file only
// draws it. One layout serves every lens, so nothing jumps when you flip between them:
//   Changes  both models at once: added in green, changed in amber, a moved arrow in amber with its old route as a
//            dashed ghost, removed elements kept as faded, struck-through ghosts. Unchanged elements fade back.
//   Before   the model in force: what the change adds is hidden, what it removes is drawn as it is today.
//   After    the change: what it removes is hidden.
//   Onion    a slider between Before and After, like an image diff's onion skin.
// [ and ] step through the changes like hunks in a code review. Nothing here saves, approves or applies anything.
// The renderer is also exposed as window.PlayDiff.mount(box, ghost, options) for other views of a change.
"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  const STATE = { width: 150, height: 54 }, INITIAL = 22;
  const INK = "#1b2130", LINE = "#4a5568";
  const LOOK = {
    same: { fill: "#eef2ff", stroke: "#5b74d6", text: INK, mark: "" },
    added: { fill: "#e5f5ec", stroke: "#17734a", text: "#17734a", mark: "+ " },
    changed: { fill: "#fdf4e3", stroke: "#c27c0e", text: "#8a5a08", mark: "~ " },
    moved: { fill: "#fdf4e3", stroke: "#c27c0e", text: "#8a5a08", mark: "↷ " },
    removed: { fill: "#fbe9e9", stroke: "#a12f2f", text: "#a12f2f", mark: "− " },
    was: { fill: "#fdf4e3", stroke: "#c27c0e", text: "#8a5a08", mark: "was " },
  };
  const FONT = { fontFamily: "system-ui, sans-serif" };
  const STRIKE = 8, BOLD = 1; // maxGraph font style bits
  const side = (status) => (status === "added" || status === "moved" ? "after" : status === "removed" || status === "was" ? "before" : "both");

  function el(tag, text, attrs = {}) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
    return node;
  }

  // ---- The renderer --------------------------------------------------------------------------------------------
  function layout(ghost, direction = "LR") {
    const g = new dagre.graphlib.Graph({ multigraph: true });
    g.setGraph(direction === "TB" ? { rankdir: "TB", nodesep: 70, ranksep: 90, edgesep: 30, marginx: 30, marginy: 30 }
      : { rankdir: "LR", nodesep: 60, ranksep: 120, edgesep: 30, marginx: 30, marginy: 30 }); // LR as the state machine tab
    g.setDefaultEdgeLabel(() => ({}));
    g.setNode("__initial", { width: INITIAL, height: INITIAL });
    for (const s of ghost.states) g.setNode(s.name, { ...STATE });
    g.setEdge("__initial", ghost.initial.after, {}, "start");
    if (ghost.initial.before !== ghost.initial.after) g.setEdge("__initial", ghost.initial.before, {}, "was-start");
    for (const t of ghost.transitions) g.setEdge(t.from_state, t.to_state, { width: 130, height: 20 }, t.key);
    dagre.layout(g);
    const at = (id) => { const n = g.node(id); return [n.x - n.width / 2, n.y - n.height / 2]; };
    const bends = (t) => g.edge(t.from_state, t.to_state, t.key).points.slice(1, -1);
    return { at, bends };
  }

  // Draw the union once; the lenses only change styles, never positions.
  function mount(box, ghost, options = {}) {
    const { Graph, InternalEvent, Point } = maxgraph;
    box.replaceChildren();
    InternalEvent.disableContextMenu(box);
    const graph = new Graph(box);
    for (const off of ["setConnectable", "setCellsEditable", "setCellsDisconnectable", "setDropEnabled", "setCellsMovable", "setCellsResizable"]) graph[off](false);
    graph.setPanning(true);
    graph.setTooltips(true);
    const place = layout(ghost, options.direction), knockOn = new Set(options.knockOn || []), parent = graph.getDefaultParent(), cells = {}, items = {};
    graph.batchUpdate(() => {
      const initial = graph.insertVertex({ parent, id: "initial", position: place.at("__initial"), size: [INITIAL, INITIAL],
        style: { shape: "ellipse", fillColor: INK, strokeColor: INK } });
      for (const s of ghost.states) {
        cells[s.name] = graph.insertVertex({ parent, id: "state:" + s.name, value: LOOK[s.status].mark + s.name, position: place.at(s.name),
          size: [STATE.width, STATE.height], style: { ...FONT, rounded: true, arcSize: 22, fontSize: 14 } });
        // A state the change affects without editing it (a knock-on the caller names) is drawn as changed.
        const status = s.status === "same" && knockOn.has(s.name) ? "changed" : s.status;
        items[cells[s.name].id] = { status, touched: s.touched || status !== s.status, kind: "state", data: s, text: s.name };
      }
      const moved = ghost.initial.before !== ghost.initial.after;
      const start = graph.insertEdge({ parent, id: "initial-edge", source: initial, target: cells[ghost.initial.after],
        style: { endArrow: "open", endSize: 8, edgeStyle: "orthogonalEdgeStyle", rounded: true } });
      items[start.id] = { status: moved ? "moved" : "same", touched: moved, kind: "start" };
      if (moved) {
        const was = graph.insertEdge({ parent, id: "was:initial-edge", source: initial, target: cells[ghost.initial.before],
          style: { endArrow: "open", endSize: 8, edgeStyle: "orthogonalEdgeStyle", rounded: true } });
        items[was.id] = { status: "was", touched: true, kind: "start" };
      }
      for (const t of ghost.transitions) {
        const edge = graph.insertEdge({ parent, id: t.key, value: `${LOOK[t.status].mark}${t.action} [${t.role}]`, source: cells[t.from_state],
          target: cells[t.to_state], style: { ...FONT, fontSize: 12, endArrow: "open", endSize: 9, curved: true, labelBackgroundColor: "#fbfcfe" } });
        edge.geometry.points = place.bends(t).map((p) => new Point(p.x, p.y));
        items[t.key] = { status: t.status, touched: t.status !== "same", kind: "transition", data: t, text: `${t.action} [${t.role}]` };
      }
    });
    graph.getTooltipForCell = (cell) => { // a node, not a string: maxGraph puts string tooltips into innerHTML
      const text = tooltip(items[cell && cell.id]);
      return text ? el("div", text, { class: "diff-tip" }) : "";
    };
    const view = { graph, ghost, lens: "changes", onion: 0.5, focus: true };

    // How one element looks in a lens. `share` is how present it is: 1 drawn, 0 hidden, in between for the onion.
    function share(status) {
      const where = side(status);
      if (where === "both") return 1;
      if (view.lens === "changes") return 1;
      const t = view.lens === "before" ? 0 : view.lens === "after" ? 1 : view.onion;
      return where === "after" ? t : 1 - t;
    }

    function styleOf(item) {
      const look = LOOK[item.status], diff = view.lens === "changes";
      const shown = diff ? look : LOOK.same; // before, after and onion draw the model plainly, as it is on that side
      const ghostly = diff && (item.status === "removed" || item.status === "was");
      const quiet = diff && view.focus && item.status === "same" && !item.touched;
      const opacity = Math.round(100 * share(item.status) * (ghostly ? 0.55 : quiet ? 0.35 : 1));
      const visible = opacity > 0;
      if (item.kind === "state") {
        return { fillColor: shown.fill, strokeColor: shown.stroke, fontColor: shown.text, strokeWidth: diff && item.status !== "same" ? 2.5 : 1.5,
          dashed: ghostly, dashPattern: "6 4", fontStyle: BOLD | (ghostly ? STRIKE : 0), opacity, textOpacity: opacity, visible };
      }
      const colour = diff && item.status !== "same" ? look.stroke : item.kind === "start" ? INK : LINE;
      return { strokeColor: colour, fontColor: diff && item.status !== "same" ? look.text : INK, strokeWidth: diff && item.status !== "same" ? 2.6 : 1.3,
        dashed: ghostly, dashPattern: "7 5", fontStyle: ghostly ? STRIKE : 0, opacity, textOpacity: opacity, visible };
    }

    function paint() {
      const model = graph.getDataModel();
      graph.batchUpdate(() => {
        for (const [id, item] of Object.entries(items)) {
          const cell = model.getCell(id);
          const { visible, ...style } = styleOf(item);
          model.setStyle(cell, { ...cell.style, ...style });
          if (item.text) model.setValue(cell, (view.lens === "changes" ? LOOK[item.status].mark : "") + item.text); // marks only where both sides show
          model.setVisible(cell, visible);
        }
      });
    }

    function fit() {
      const plugin = graph.getPlugin("fit");
      plugin.maxFitScale = 1.3;
      plugin.fitCenter({ margin: 24 });
    }

    function show(change) {
      const ids = [change.ref, change.was].filter(Boolean);
      const found = ids.map((id) => graph.getDataModel().getCell(id)).filter(Boolean);
      if (view.lens !== "changes" && found.some((c) => !c.visible)) setLens("changes");
      graph.setSelectionCells(found);
      if (found[0]) graph.scrollCellToVisible(found[0], false);
      if (options.onShow) options.onShow(change, found);
    }

    function setLens(lens, onion) {
      view.lens = lens;
      if (onion !== undefined) view.onion = onion;
      paint();
      if (options.onLens) options.onLens(view.lens, view.onion);
    }

    graph.getSelectionModel().addListener(InternalEvent.CHANGE, () => {
      const cell = graph.getSelectionCell();
      if (options.onSelect) options.onSelect(cell ? items[cell.id] : null, cell ? cell.id : "");
    });
    paint();
    fit();
    return Object.assign(view, { paint, fit, show, setLens, setFocus: (on) => { view.focus = on; paint(); },
      destroy: () => graph.destroy(), item: (id) => items[id] });
  }

  function tooltip(item) {
    if (!item) return "";
    const what = { same: "Unchanged", added: "Added by the change", removed: "Removed by the change (ghost)", changed: "Changed",
      moved: "Moved by the change", was: "Where it went before the change (ghost)" }[item.status];
    if (item.kind !== "transition") return what;
    const t = item.data, lines = [`${what}: ${t.action}, ${t.from_state} → ${t.to_state}, by ${t.role}`];
    if (t.was) lines.push(`Was ${t.was.from_state} → ${t.was.to_state}`);
    for (const f of t.fields || []) lines.push(`${f.field}: ${[].concat(f.before).join(", ") || "none"} → ${[].concat(f.after).join(", ") || "none"}`);
    return lines.join("\n");
  }

  // The same marks and colours for the other diagrams (class and use case), which draw the union themselves: `part` is
  // box (a use case), actor, line (an association) or text (an enumeration literal). Unchanged parts fade back.
  function look(status, part) {
    const l = LOOK[status], ghostly = status === "removed", quiet = status === "same";
    if (part === "text") return quiet ? { textOpacity: 50 } : { fontColor: l.text, fontStyle: BOLD | (ghostly ? STRIKE : 0), textOpacity: ghostly ? 70 : 100 };
    const opacity = quiet ? 40 : ghostly ? 55 : 100;
    const base = { strokeColor: quiet ? undefined : l.stroke, strokeWidth: quiet ? undefined : 2.5, dashed: ghostly, dashPattern: "6 4", opacity, textOpacity: opacity };
    if (part === "line") return base;
    const text = quiet ? {} : { fontColor: l.text, fontStyle: BOLD | (ghostly ? STRIKE : 0) };
    return part === "actor" ? { ...base, ...text } : { ...base, ...text, fillColor: quiet ? undefined : l.fill };
  }
  const markOf = (status) => LOOK[status].mark;

  window.PlayDiff = { mount, layout, look, mark: markOf };

  // ---- The Changes view, on the state machine tab ---------------------------------------------------------------
  // A toggle beside Fit, shown while there is a change, swaps the editable canvas for the change drawn as above.-
  const ide = () => window.PlayIDE;
  let view = null, ghost = null, at = -1, seq = 0, open = false;

  function request() {
    const about = ide().about(), planned = ide().planned();
    return { case_id: about.case_id, model: ide().base(), plan: planned && planned.length ? planned : null };
  }

  async function refresh() {
    const mine = (seq += 1);
    let result;
    try {
      result = await ide().api("/api/play/diff", request());
    } catch (error) {
      result = { error };
    }
    if (mine !== seq) return; // a newer plan asked again
    ghost = result.error ? null : result;
    if (open && ghost && !ghost.changes.length) toggle(false); // nothing left to show
    badge(result);
    if (!open) return;
    const tab = ide().tab();
    if (tab === "states") render(result);
    else if (DRAWN.includes(tab)) ide().showTab(tab);
  }

  function badge(result) {
    const button = $("show-changes"), b = button.querySelector(".badge");
    const n = result && !result.error ? result.changes.length : 0;
    b.textContent = String(n);
    button.hidden = !n && !open;
    button.title = n ? "Show the change on the diagram (removed parts as ghosts):\n" + result.changes.map((c) => `${LOOK[c.change].mark.trim()} ${c.text}`).join("\n")
      : "No change to show";
  }

  // One calm row: what changed, in a sentence, and stepping. Lenses, the onion skin and Fade unchanged wait behind Compare.
  function toolbar(counts) {
    const bar = el("div", undefined, { class: "diff-tools", role: "toolbar", "aria-label": "The change" });
    bar.append(summary(counts));
    const nav = el("div", undefined, { class: "diff-nav" });
    const prev = el("button", "‹", { type: "button", class: "quiet", "aria-label": "Previous change", title: "Previous change ([)", "aria-keyshortcuts": "[" });
    const next = el("button", "›", { type: "button", class: "quiet", "aria-label": "Next change", title: "Next change (])", "aria-keyshortcuts": "]" });
    prev.addEventListener("click", () => step(-1));
    next.addEventListener("click", () => step(1));
    nav.append(prev, el("span", "", { id: "diff-pos", class: "small", role: "status", "aria-live": "polite" }), next);
    const compare = el("button", "Compare", { type: "button", id: "diff-compare", class: "quiet", "aria-pressed": "false", "aria-controls": "diff-compare-tools",
      title: "Before, after, and a slider between them" });
    const tools = compareTools();
    compare.addEventListener("click", () => {
      const on = tools.hidden;
      tools.hidden = !on;
      compare.setAttribute("aria-pressed", String(on));
      if (!on) view.setLens("changes");
    });
    bar.append(nav, compare);
    return [bar, tools];
  }

  function compareTools() {
    const bar = el("div", undefined, { class: "diff-tools diff-compare", id: "diff-compare-tools", role: "toolbar", "aria-label": "Compare before and after", hidden: "" });
    const group = el("div", undefined, { class: "lens", role: "radiogroup", "aria-label": "Lens" });
    for (const [lens, text, title] of [["before", "Before", "The model in force"], ["changes", "Changes", "Both, with removed elements as ghosts"],
      ["after", "After", "The model with the change"]]) {
      const b = el("button", text, { type: "button", role: "radio", "data-lens": lens, title, "aria-checked": "false" });
      b.addEventListener("click", () => view.setLens(lens, lens === "before" ? 0 : lens === "after" ? 1 : view.onion));
      group.append(b);
    }
    const onion = el("input", undefined, { type: "range", min: "0", max: "100", value: "50", id: "diff-onion", "aria-label": "Onion skin: fade from before to after" });
    onion.addEventListener("input", () => view.setLens("onion", onion.value / 100));
    const onionLabel = el("label", undefined, { class: "onion", for: "diff-onion", title: "Fade between the model in force and the change" });
    onionLabel.append(el("span", "Before", { class: "small" }), onion, el("span", "After", { class: "small" }));
    const focus = el("label", undefined, { class: "small focus-toggle", title: "Fade what the change does not touch" });
    const box = el("input", undefined, { type: "checkbox", id: "diff-focus" });
    box.checked = true;
    box.addEventListener("change", () => view.setFocus(box.checked));
    focus.append(box, " Fade unchanged");
    bar.append(group, onionLabel, focus);
    return bar;
  }

  // "4 changes: 2 added, 1 moved, 1 removed", each count in its colour: the legend and the count in one line.
  function summary(counts) {
    const total = Object.values(counts).reduce((a, b) => a + b, 0);
    const box = el("p", undefined, { class: "diff-summary" });
    box.append(el("strong", `${total} change${total === 1 ? "" : "s"}`));
    const parts = [["added", "added"], ["changed", "changed"], ["moved", "moved"], ["removed", "removed"]].filter(([s]) => counts[s]);
    parts.forEach(([status, text], i) => box.append(i ? ", " : ": ", el("span", `${counts[status]} ${text}`, { class: "key " + status })));
    return box;
  }

  // The list lives in the inspector: one place to read the change. The open change shows its before and after under it.
  function changeList(changes) {
    const list = el("ol", undefined, { class: "diff-list", "aria-label": "Changes" });
    changes.forEach((c, i) => {
      const b = el("button", undefined, { type: "button", class: "diff-item " + c.change, "data-n": String(c.n) });
      b.append(el("span", LOOK[c.change].mark.trim(), { class: "mark", "aria-hidden": "true" }), el("span", c.text));
      b.addEventListener("click", () => go(i));
      const li = el("li");
      li.append(b);
      list.append(li);
    });
    list.addEventListener("keydown", keys);
    return list;
  }

  function render(result) {
    const host = $("diff-view");
    if (view) { view.destroy(); view = null; }
    host.replaceChildren();
    if (!result) { host.append(el("p", "Working out the change…", { class: "muted empty" })); return; }
    if (result.error) { host.append(el("p", `${result.error.code || "ERROR"}: ${result.error.message}`, { class: "muted empty" })); return; }
    if (!result.changes.length) {
      host.append(el("p", "No change to show. Ask the chat for a plan, draw on the state machine, or open a change case: its difference from the model in force appears here.", { class: "muted empty" }));
      return;
    }
    const canvas = el("div", undefined, { class: "canvas diff-canvas", tabindex: "0", "aria-label": "The change on the state machine" });
    host.append(...toolbar(result.counts), canvas);
    $("inspector").replaceChildren(el("h3", "Changes"), changeList(result.changes),
      el("p", "Read-only: the change is not saved, approved or applied here.", { class: "muted small" }));
    view = mount(canvas, result, {
      onLens: (lens, onion) => {
        for (const b of host.querySelectorAll(".lens button")) b.setAttribute("aria-checked", String(b.dataset.lens === lens));
        $("diff-onion").value = String(Math.round(onion * 100));
        host.dataset.lens = lens;
      },
      onShow: (change) => detail(change),
      onSelect: (item, id) => { const i = result.changes.findIndex((c) => c.ref === id || c.was === id); if (i >= 0 && i !== at) { mark(i); detail(result.changes[i]); } },
    });
    view.setLens("changes");
    at = -1;
    $("diff-pos").textContent = "";
    canvas.addEventListener("keydown", keys);
  }

  function mark(i) {
    at = i;
    for (const b of document.querySelectorAll(".diff-item")) b.setAttribute("aria-current", String(+b.dataset.n === ghost.changes[i].n));
    if ($("diff-pos")) $("diff-pos").textContent = `Change ${i + 1} of ${ghost.changes.length}`;
  }

  function go(i) {
    if (!ghost || !ghost.changes.length) return;
    mark((i + ghost.changes.length) % ghost.changes.length);
    if (view) view.show(ghost.changes[at]); // the state machine
    else { showOn(ide().tab(), ghost.changes[at]); detail(ghost.changes[at]); }
  }

  // Where a change shows on the class and use case diagrams: a state is a literal of the record's enumeration, and an
  // action is a use case.
  function cellsOn(tab, change) {
    const refs = [change.ref, change.was].filter(Boolean);
    if (tab === "classes") return refs.filter((r) => r.startsWith("state:")).map((r) => "literal:" + r.slice(6));
    if (tab === "usecases") return refs.filter((r) => r.startsWith("t:") || r.startsWith("was:")).map((r) => "uc:" + r.slice(r.indexOf(":") + 1));
    if (tab === "sequences" && window.PlaySequence) return window.PlaySequence.cellsFor(refs.filter((r) => r.startsWith("t:")).map((r) => r.slice(2)));
    return [];
  }

  function showOn(tab, change) {
    const g = ide().diagram(tab);
    if (!g) return;
    const found = cellsOn(tab, change).map((id) => g.getDataModel().getCell(id)).filter(Boolean);
    const pick = found.map((c) => (c.id.startsWith("literal:") ? c.parent : c)); // a literal is not selectable; its enumeration is
    g.setSelectionCells(pick);
    if (pick[0]) g.scrollCellToVisible(pick[0], false);
  }

  const step = (by) => go(at < 0 ? (by > 0 ? 0 : -1) : at + by);

  // What one change is, opened under its line in the list: each changed field before and after, when it has any.
  function detail(change) {
    for (const old of document.querySelectorAll(".diff-detail")) old.remove();
    const t = ghost.transitions.find((x) => x.key === change.ref);
    if (!t || !((t.fields && t.fields.length) || t.was)) return;
    const table = el("table", undefined, { class: "diff-fields diff-detail" });
    const head = el("tr");
    head.append(el("th", ""), el("th", "Before"), el("th", "After"));
    table.append(head);
    const rowOf = (name, before, after) => {
      const tr = el("tr");
      tr.append(el("th", name), el("td", before, { class: "before" }), el("td", after, { class: "after" }));
      table.append(tr);
    };
    if (t.was) rowOf("route", `${t.was.from_state} → ${t.was.to_state}`, `${t.from_state} → ${t.to_state}`);
    for (const f of t.fields || []) rowOf(f.field, [].concat(f.before).join(", ") || "none", [].concat(f.after).join(", ") || "none");
    const li = document.querySelector(`.diff-item[data-n="${change.n}"]`);
    if (li) li.parentElement.append(table);
  }

  // [ and ] step through the changes; b, c and a pick a lens. Single keys act only while focus is in the Changes tab.
  function keys(event) {
    if (event.ctrlKey || event.metaKey || event.altKey || /^(INPUT|TEXTAREA|SELECT)$/.test(event.target.tagName) && event.target.type !== "checkbox") return;
    const lens = { b: "before", c: "changes", a: "after" }[event.key.toLowerCase()];
    if (event.key === "]" || event.key === "[") { event.preventDefault(); step(event.key === "]" ? 1 : -1); }
    else if (lens) { event.preventDefault(); view.setLens(lens, lens === "before" ? 0 : lens === "after" ? 1 : view.onion); }
  }

  const DRAWN = ["states", "classes", "usecases", "sequences"]; // the diagrams that draw a change; the others are left as they are
  const HELP = {
    states: "Green is added, amber changed or moved, and faded dashes are what the change removes. [ and ] step through the changes.",
    classes: "The record's states are its enumeration's literals: green is added, struck through is what the change removes.",
    usecases: "Green is added, amber changed, and faded dashes are what the change removes: use cases, actors and who takes which.",
    sequences: "Messages whose action the change adds are green, changes amber, removes dashed red; a message the kernel now refuses says what it was before.",
  };

  // Changes is a mode across the diagrams: it stays on while you flip tabs, and each diagram shows the same change.
  function apply(tab) {
    const states = tab === "states", on = open && states;
    $("diff-view").hidden = !on;
    $("canvas").hidden = on || !states;
    $("draw-palette").hidden = on || !states;
    ide().setChanges(open && ghost && DRAWN.includes(tab) ? ghost : null);
    if (on) render(ghost);
    else if (view) { view.destroy(); view = null; }
    if (open && DRAWN.includes(tab)) {
      $("canvas-help").textContent = HELP[tab];
      if (!states) list();
    }
  }

  // The change list in the inspector, for diagrams other than the state machine (whose view puts it there itself).
  function list() {
    if (!ghost || !ghost.changes.length) return;
    $("inspector").replaceChildren(el("h3", "Changes"), changeList(ghost.changes),
      el("p", "Read-only: the change is not saved, approved or applied here.", { class: "muted small" }));
    at = -1;
  }

  function toggle(on) {
    open = on;
    $("show-changes").setAttribute("aria-pressed", String(on));
    const tab = ide().tab();
    if (on && !DRAWN.includes(tab)) { ide().showTab("states"); return; } // showTab calls apply through the tab hook
    if (DRAWN.includes(tab) && tab !== "states") ide().showTab(tab); // redraw that diagram with or without the change
    else apply(tab);
    if (!on) $("inspector").replaceChildren(el("p", "Select a state or transition.", { class: "muted" }));
    if (on && !ghost) refresh();
    badge(ghost);
  }

  function setup() {
    const button = el("button", "Changes", { id: "show-changes", type: "button", class: "quiet show-changes", "aria-pressed": "false", "aria-controls": "diff-view", hidden: "" });
    button.append(el("span", "0", { class: "badge" }));
    $("fit").before(button);
    button.addEventListener("click", () => toggle(!open));
    ide().hooks.tab.push((which) => apply(which));
    ide().hooks.changeSelect.push((id) => {
      if (!ghost) return;
      const i = ghost.changes.findIndex((c) => cellsOn(ide().tab(), c).includes(id));
      if (i >= 0 && i !== at) { mark(i); detail(ghost.changes[i]); }
    });
    ide().hooks.diffGraph = () => (open && view ? view.graph : null);
    document.addEventListener("playide:plan", () => { ghost = null; refresh(); });
    refresh();
  }

  if (document.body.dataset.ready === "true") setup();
  else document.addEventListener("playide:ready", setup, { once: true });
})();
