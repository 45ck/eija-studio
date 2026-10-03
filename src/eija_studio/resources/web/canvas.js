"use strict";
// This renderer owns geometry and selection only. Every semantic verdict comes from the server.
const EijaCanvas = (() => {
  const NS = "http://www.w3.org/2000/svg";
  const width = 190, height = 76, cornerRadius = 12;
  const dragStops = new WeakMap();
  function paintedPort(point, node) {
    // Dagre clips to rectangular boxes. Project only that endpoint onto the
    // painted rounded outline; interior route points remain Dagre's output.
    const x = point.x - node.x, y = point.y - node.y;
    const cx = Math.max(cornerRadius, Math.min(width - cornerRadius, x));
    const cy = Math.max(cornerRadius, Math.min(height - cornerRadius, y));
    const dx = x - cx, dy = y - cy, distance = Math.hypot(dx, dy);
    if (distance <= cornerRadius) return point;
    return {x:node.x + cx + dx * cornerRadius / distance, y:node.y + cy + dy * cornerRadius / distance};
  }
  function edgeLabelSize(transition, labelBoxes) {
    const supplied=labelBoxes?.get(transition.id);
    if(supplied===undefined)return {width:Math.max(70,String(transition.action||"").length*8),height:24};
    if(![supplied?.width,supplied?.height].every(value=>Number.isFinite(value)&&value>0))throw new Error("Display label dimensions must be finite and positive.");
    return {width:supplied.width,height:supplied.height};
  }
  function geometry(model, saved = {}, direction = "LR", labelBoxes) {
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
      {...edgeLabelSize(transition,labelBoxes),labelpos:"c"}, "e" + index));
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
      points[0] = paintedPort(points[0], coords[transition.from_state]);
      points[points.length - 1] = paintedPort(points[points.length - 1], coords[transition.to_state]);
      Object.defineProperty(routes, transition.id, {enumerable:true, value:{points,
        label:{x:edge.x + (a.x + b.x) / 2, y:edge.y + (a.y + b.y) / 2}}});
    });
    return {coords, routes};
  }
  function positions(model, saved = {}) {return geometry(model, saved).coords;}
  function bounds(projected, model, labelBoxes) {
    const points=Object.values(projected.coords).flatMap(p=>[p,{x:p.x+width,y:p.y+height}]);
    for(const transition of model.transitions||[]){const route=projected.routes[transition.id],size=edgeLabelSize(transition,labelBoxes),custom=labelBoxes?.get(transition.id)!==undefined;points.push(...route.points,{x:route.label.x-size.width/2,y:route.label.y-(custom?size.height/2:24)},{x:route.label.x+size.width/2,y:route.label.y+(custom?size.height/2:16)});}
    if(!points.length)return {x:0,y:0,width:320,height:240};
    const x=Math.min(...points.map(p=>p.x))-35,y=Math.min(...points.map(p=>p.y))-35;
    return {x,y,width:Math.max(...points.map(p=>p.x))+35-x,height:Math.max(...points.map(p=>p.y))+55-y};
  }
  function projectLayout(model,saved,direction="AUTO",viewport={width:1000,height:600},labelBoxes) {
    const project=value=>{const result=geometry(model,saved,value,labelBoxes);return {...result,direction:value,bounds:bounds(result,model,labelBoxes)};};
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
  function dragMessage(active, end, origin, node, choice) {
    const subject = `${active.action} ${end}`;
    if (!node) return `Move ${subject} from ${origin}. Drop on a state to preview.`;
    const target = node.dataset.state;
    if (choice?.legal === true) return `Release to preview ${subject}: ${origin} → ${target}.`;
    if (choice?.legal === false) return `Refused ${subject}: ${origin} → ${target}. Release to inspect.`;
    return target === origin ? `${subject} is already ${origin}. No change here.` : `No ${end} change is offered for ${target}.`;
  }
  function beginDrag(root, board, event, options) {
    if (event.button !== 0) return;
    const {end, x, y, active, affordances, onDrop, onNotice, onGestureStatus} = options;
    dragStops.get(root)?.(); event.preventDefault();
    const handle = event.currentTarget, pointer = event.pointerId;
    const available = entries(affordances, active.id, "retarget_" + end);
    const origin = end === "source" ? active.from_state : active.to_state;
    const choiceFor = node => node && available.find(choice => choice.target === "state:" + node.dataset.state);
    const targetAt = e => {
      const node = document.elementFromPoint(e.clientX, e.clientY)?.closest(".model-node");
      return node && board.contains(node) ? node : null;
    };
    const ghost = svg("line", {x1:x, y1:y, x2:x, y2:y, class:"drag-guide"});
    let hovered, finished = false;
    const hover = node => {
      if (node === hovered) return;
      hovered?.classList.remove("drop-hover"); hovered = node;
      hovered?.classList.add("drop-hover");
      onGestureStatus?.(dragMessage(active, end, origin, node, choiceFor(node)));
    };
    const move = e => {
      if (e.pointerId !== pointer) return;
      const matrix = board.getScreenCTM(); if (!matrix) return;
      const point = new DOMPoint(e.clientX, e.clientY).matrixTransform(matrix.inverse());
      ghost.setAttribute("x2", point.x); ghost.setAttribute("y2", point.y);
      hover(targetAt(e));
    };
    const finish = () => {
      if (finished) return; finished = true;
      handle.removeEventListener("pointermove", move); handle.removeEventListener("pointerup", release);
      handle.removeEventListener("pointercancel", cancel); handle.removeEventListener("lostpointercapture", cancel);
      if (handle.hasPointerCapture(pointer)) handle.releasePointerCapture(pointer);
      ghost.remove(); board.classList.remove("drag-active"); handle.classList.remove("drag-active");
      for (const node of board.querySelectorAll(".model-node")) node.classList.remove("drop-legal", "drop-refused", "drop-neutral", "drop-hover");
      if (dragStops.get(root) === finish) dragStops.delete(root);
      onGestureStatus?.(null);
    };
    const cancel = e => {if (e.pointerId !== pointer) return; finish(); onNotice("Gesture cancelled; the model is unchanged.");};
    const release = e => {
      if (e.pointerId !== pointer) return;
      const choice = choiceFor(targetAt(e)); finish();
      if (choice) onDrop(choice); else onNotice("No different state selected; the model is unchanged.");
    };
    handle.setPointerCapture(pointer); board.append(ghost);
    board.classList.add("drag-active"); handle.classList.add("drag-active");
    for (const node of board.querySelectorAll(".model-node")) {
      const choice = choiceFor(node);
      node.classList.add(choice?.legal === true ? "drop-legal" : choice?.legal === false ? "drop-refused" : "drop-neutral");
    }
    handle.addEventListener("pointermove", move); handle.addEventListener("pointerup", release);
    handle.addEventListener("pointercancel", cancel); handle.addEventListener("lostpointercapture", cancel);
    dragStops.set(root, finish); hover(null);
  }
  function render(root, options) {
    const {model, layout, pack, selected, affordances, editable, onSelect, onDrop, onNotice, onGestureStatus} = options;
    dragStops.get(root)?.();
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
      group.append(svg("rect", {x: p.x, y: p.y, width, height, rx: cornerRadius, class: "state-box"}));
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
        handle.append(svg("circle", {cx: x, cy: y, r: 15}), svg("text", {x:x + (end === "source" ? -22 : 22), y:y + 5,
          "text-anchor":end === "source" ? "end" : "start"}, end === "source" ? "Source" : "Target"));
        handle.addEventListener("pointerdown", event => beginDrag(root, board, event,
          {end, x, y, active, affordances, onDrop, onNotice, onGestureStatus})); board.append(handle);
      }
    }
    root.append(board);
  }
  return {render, positions, geometry, projectLayout, entries};
})();
if (typeof module !== "undefined") module.exports = EijaCanvas;
