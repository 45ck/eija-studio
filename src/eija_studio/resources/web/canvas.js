"use strict";
// This renderer owns geometry and selection only. Every semantic verdict comes from the server.
const EijaCanvas = (() => {
  const NS = "http://www.w3.org/2000/svg";
  const width = 190, height = 76;
  function geometry(model, saved = {}, direction = "LR") {
    const engine = globalThis.dagre;
    if (!engine?.graphlib?.Graph || !engine.layout) throw new Error("The bundled Dagre layout engine is unavailable. Use the transition editor while the local asset is restored.");
    // A fresh disposable projection, never the server's Workflow or layout objects.
    // Opaque internal IDs also keep arbitrary domain labels out of Graphlib's object keys.
    const graph = new engine.graphlib.Graph({multigraph:true});
    graph.setGraph({rankdir:direction, nodesep:44, ranksep:direction === "TB" ? 32 : 64, edgesep:24, marginx:50, marginy:75});
    graph.setDefaultEdgeLabel(() => ({}));
    const states = [...model.states].sort(), ids = new Map(states.map((state, index) => [state, "n" + index]));
    for (const state of states) graph.setNode(ids.get(state), {width, height});
    const transitions = [...(model.transitions || [])].sort((a, b) => a.id < b.id ? -1 : a.id > b.id ? 1 : 0);
    transitions.forEach((transition, index) => graph.setEdge(ids.get(transition.from_state), ids.get(transition.to_state),
      {width:Math.max(70, String(transition.action || "").length * 8), height:24, labelpos:"c"}, "e" + index));
    engine.layout(graph);
    const coords = {}, offsets = new Map();
    for (const state of states) {
      const node = graph.node(ids.get(state)), stored = saved[state];
      const automatic = {x:node.x - width / 2, y:node.y - height / 2};
      const position = stored && Number.isFinite(stored.x) && Number.isFinite(stored.y)
        ? {x:stored.x + 50, y:stored.y + 75} : automatic;
      Object.defineProperty(coords, state, {value:position, enumerable:true});
      offsets.set(state, {x:position.x - automatic.x, y:position.y - automatic.y});
    }
    const routes = {};
    transitions.forEach((transition, index) => {
      const edge = graph.edge({v:ids.get(transition.from_state), w:ids.get(transition.to_state), name:"e" + index});
      const a = offsets.get(transition.from_state), b = offsets.get(transition.to_state);
      // Retain Dagre's routed points. Saved manual placements shift those points;
      // they never become semantic edits or a second routing algorithm.
      const points = edge.points.map((point, i) => {
        const weight = i / Math.max(1, edge.points.length - 1);
        return {x:point.x + a.x * (1 - weight) + b.x * weight, y:point.y + a.y * (1 - weight) + b.y * weight};
      });
      Object.defineProperty(routes, transition.id, {enumerable:true, value:{points,
        label:{x:edge.x + (a.x + b.x) / 2, y:edge.y + (a.y + b.y) / 2}}});
    });
    return {coords, routes};
  }
  function positions(model, saved = {}) {return geometry(model, saved).coords;}
  function bounds(projected, model) {
    const points=Object.values(projected.coords).flatMap(p=>[p,{x:p.x+width,y:p.y+height}]);
    for(const transition of model.transitions||[]){const route=projected.routes[transition.id],half=Math.max(70,String(transition.action||"").length*8)/2;points.push(...route.points,{x:route.label.x-half,y:route.label.y-24},{x:route.label.x+half,y:route.label.y+16});}
    if(!points.length)return {x:0,y:0,width:320,height:240};
    const x=Math.min(...points.map(p=>p.x))-35,y=Math.min(...points.map(p=>p.y))-35;
    return {x,y,width:Math.max(...points.map(p=>p.x))+35-x,height:Math.max(...points.map(p=>p.y))+55-y};
  }
  function projectLayout(model,saved,direction="AUTO",viewport={width:1000,height:600}) {
    const project=value=>{const result=geometry(model,saved,value);return {...result,direction:value,bounds:bounds(result,model)};};
    if(direction==="LR"||direction==="TB")return project(direction);
    const horizontal=project("LR"),vertical=project("TB");
    const scale=p=>Math.min(viewport.width/p.bounds.width,viewport.height/p.bounds.height);
    return scale(vertical)>scale(horizontal)?vertical:horizontal;
  }
  function entries(affordances, transition, kind) {
    return (affordances || []).filter(a => a.element === "transition:" + transition && a.kind === kind);
  }
  function svg(tag, attrs = {}, text) {
    const node = document.createElementNS(NS, tag);
    for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, String(value));
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function activate(node, callback) {
    node.addEventListener("click", callback);
    node.addEventListener("keydown", event => {
      if (["Enter", " "].includes(event.key)) { event.preventDefault(); callback(); }
    });
  }
  function render(root, options) {
    const {model, layout, pack, selected, affordances, editable, onSelect, onDrop, onNotice} = options;
    root.replaceChildren();
    if (!model) return;
    let projection;
    const rect=root.getBoundingClientRect(),space=rect.width&&rect.height?rect:root.closest(".editor-stack")?.getBoundingClientRect();
    try {projection = projectLayout(model, layout, options.direction, {width:space?.width||1000,height:space?.height||600});} catch (error) {
      const message = document.createElement("p"); message.textContent = error.message; message.setAttribute("role", "status"); root.append(message); return;
    }
    const {coords, routes, bounds:box} = projection;
    const {x:minX,y:minY,width:viewWidth,height:viewHeight}=box;
    const board = svg("svg", {viewBox: `${minX} ${minY} ${viewWidth} ${viewHeight}`, role: "group", "aria-label": "Executable workflow state diagram", class: "model-svg"});
    board.dataset.initialX = coords[model.initial_state]?.x ?? 50;
    board.dataset.initialY = coords[model.initial_state]?.y ?? 75;
    board.dataset.direction = projection.direction;
    const focus=model.transitions.find(t=>t.id===selected),focusState=focus?.from_state||model.initial_state;
    board.dataset.focusX=coords[focusState]?.x??50;board.dataset.focusY=coords[focusState]?.y??75;
    const desc = svg("desc", {}, "Select a transition, then drag its Source or Target handle onto a state. The transition editor provides the same operation with a keyboard. Changes are checked by the server.");
    board.append(desc);
    const defs = svg("defs"), marker = svg("marker", {id: "model-arrow", viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: "auto-start-reverse"});
    marker.append(svg("path", {d: "M 0 0 L 10 5 L 0 10 z", class: "arrow-head"}));
    defs.append(marker); board.append(defs);
    for (const transition of model.transitions) {
      const route = routes[transition.id];
      const path = route.points.map((point, index) => `${index ? "L" : "M"} ${point.x} ${point.y}`).join(" ");
      const group = svg("g", {class: "model-edge" + (transition.id === selected ? " selected" : ""), role: "button", tabindex: 0,
        "aria-label": `${transition.action}, ${transition.role}, ${transition.from_state} to ${transition.to_state}. Select transition.`,
        "aria-pressed": transition.id === selected, "data-eija-id": `${pack}.transition.${transition.id}`});
      group.append(svg("path", {d: path, class: "edge-hit"}), svg("path", {d: path, class: "edge-line", "marker-end": "url(#model-arrow)"}));
      const label = svg("text", {x: route.label.x, y: route.label.y - 8, class: "edge-label", "text-anchor": "middle"}, transition.action);
      group.append(label); activate(group, () => onSelect(transition.id)); board.append(group);
    }
    for (const state of model.states) {
      const p = coords[state], initial = model.initial_state === state;
      const group = svg("g", {class: "model-node", "data-state": state, "data-eija-id": `${pack}.state.${state}`});
      group.append(svg("rect", {x: p.x, y: p.y, width, height, rx: 12, class: "state-box"}));
      group.append(svg("text", {x: p.x + 15, y: p.y + 29, class: "state-label"}, state));
      group.append(svg("text", {x: p.x + 15, y: p.y + 53, class: "state-meta"}, initial ? "Initial state" : `${model.transitions.filter(t => t.from_state === state).length} outgoing transitions`));
      board.append(group);
    }
    const active = model.transitions.find(t => t.id === selected);
    if (active && editable) {
      for (const end of ["source", "target"]) {
        const p = coords[end === "source" ? active.from_state : active.to_state];
        const x = p.x + (end === "source" ? 35 : width - 35), y = p.y + height;
        const handle = svg("g", {class: "edit-handle", "data-end": end, "aria-hidden": "true"});
        handle.append(svg("circle", {cx: x, cy: y, r: 15}), svg("text", {x, y: y + 32, "text-anchor": "middle"}, end === "source" ? "Source" : "Target"));
        handle.addEventListener("pointerdown", event => beginDrag(event, end, x, y)); board.append(handle);
      }
    }
    function beginDrag(event, end, x, y) {
      if (event.button !== 0 || !active) return;
      event.preventDefault();
      const handle = event.currentTarget;
      handle.setPointerCapture(event.pointerId);
      const ghost = svg("line", {x1: x, y1: y, x2: x, y2: y, class: "drag-guide"});
      board.append(ghost);
      const available = entries(affordances, active.id, "retarget_" + end);
      for (const node of board.querySelectorAll(".model-node")) {
        const choice = available.find(a => a.target === "state:" + node.dataset.state);
        node.classList.add(choice?.legal ? "drop-legal" : "drop-refused");
      }
      const move = e => {
        const matrix = board.getScreenCTM();
        if (!matrix) return;
        const point = new DOMPoint(e.clientX, e.clientY).matrixTransform(matrix.inverse());
        ghost.setAttribute("x2", point.x); ghost.setAttribute("y2", point.y);
      };
      const finish = e => {
        handle.removeEventListener("pointermove", move); handle.removeEventListener("pointerup", release); handle.removeEventListener("pointercancel", cancel);
        if (handle.hasPointerCapture(e.pointerId)) handle.releasePointerCapture(e.pointerId);
        ghost.remove();
        for (const node of board.querySelectorAll(".model-node")) node.classList.remove("drop-legal", "drop-refused");
      };
      const cancel = e => { finish(e); onNotice("Gesture cancelled; the model is unchanged."); };
      const release = e => {
        const node = document.elementFromPoint(e.clientX, e.clientY)?.closest(".model-node");
        const choice = node && available.find(a => a.target === "state:" + node.dataset.state);
        finish(e); handle.removeEventListener("pointerup", release);
        if (choice) onDrop(choice);
        else onNotice("No different state selected; the model is unchanged.");
      };
      handle.addEventListener("pointermove", move); handle.addEventListener("pointerup", release, {once: true}); handle.addEventListener("pointercancel", cancel, {once: true});
    }
    root.append(board);
  }
  return {render, positions, geometry, projectLayout, entries};
})();
if (typeof module !== "undefined") module.exports = EijaCanvas;
