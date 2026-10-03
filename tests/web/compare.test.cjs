"use strict";
// Isolated projection/oracle checks. They do not establish browser or human acceptance.
// Staged runs set EIJA_WEB_ROOT, EIJA_CANVAS_MODULE and EIJA_COMPARE_MODULE to the reviewed files.
const {test} = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");
const web = process.env.EIJA_WEB_ROOT || path.join(__dirname, "../../src/eija_studio/resources/web");
globalThis.dagre = require(path.join(web, "vendor/dagre.min.js"));
globalThis.EijaCanvas = require(process.env.EIJA_CANVAS_MODULE || path.join(web, "canvas.js"));
globalThis.EijaReview = require(path.join(web, "review.js"));
const compare = require(process.env.EIJA_COMPARE_MODULE || path.join(web, "compare.js"));

function freeze(value) {
  if (value && typeof value === "object") {
    Object.values(value).forEach(freeze);
    Object.freeze(value);
  }
  return value;
}
const copy = value => JSON.parse(JSON.stringify(value));
const sorted = values => [...values].sort();
function transition(id, from, to, extra = {}) {
  return {id, from_state:from, to_state:to, action:id, role:"Owner", guards:[],
    required_effects:[], forbidden_effects:[], ...extra};
}

const before = freeze({
  states:["Draft", "Review", "Done", "Old", "Unused"], initial_state:"Draft",
  transitions:[
    transition("T-KEEP", "Draft", "Review", {action:"Submit"}),
    transition("T-PARALLEL", "Draft", "Review", {action:"Resubmit"}),
    transition("T-LOOP", "Review", "Review", {action:"Recheck"}),
    transition("T-RETARGET", "Review", "Done", {action:"Finish"}),
    transition("T-CHANGE", "Review", "Done", {action:"Recommend", guards:["active", "assigned"],
      required_effects:["audit"], forbidden_effects:["publish"]}),
    transition("T-REMOVE", "Old", "Draft", {action:"Restore"})
  ]
});
const after = freeze({
  states:["Draft", "Review", "Done", "New", "Spare"], initial_state:"Draft",
  transitions:[
    transition("T-KEEP", "Draft", "Review", {action:"Submit"}),
    transition("T-PARALLEL", "Draft", "Review", {action:"Resubmit"}),
    transition("T-LOOP", "Review", "Review", {action:"Recheck"}),
    transition("T-RETARGET", "Review", "New", {action:"Finish"}),
    transition("T-CHANGE", "Review", "Done", {action:"Recommend", role:"Agent", guards:["active"],
      required_effects:["audit", "notify"], forbidden_effects:["publish", "payment"]}),
    transition("T-ADD", "New", "Done", {action:"Complete"})
  ]
});
const expectedChanges = freeze({
  "transition:T-RETARGET":"changed", "transition:T-CHANGE":"changed",
  "transition:T-REMOVE":"removed", "transition:T-ADD":"added",
  "state:Old":"removed", "state:Unused":"removed", "state:New":"added", "state:Spare":"added"
});
const initialBefore = freeze({states:["A", "B", "Removed"], initial_state:"A", transitions:[]});
const initialAfter = freeze({states:["A", "B", "Added"], initial_state:"B", transitions:[]});
const initialChanges = freeze({"state:Removed":"removed", "state:Added":"added", "initial:initial_state":"changed"});

function assertMembers(actual, expected, label) {
  assert.equal(new Set(actual).size, actual.length, `${label}: duplicate identity`);
  assert.deepEqual(sorted(actual), sorted(expected), `${label}: exact membership`);
}
function assertChanges(inventory, expected) {
  assertMembers(inventory.changes.map(item => item.key), Object.keys(expected), "change inventory");
  for (const item of inventory.changes) assert.equal(item.status, expected[item.key], `${item.key}: status`);
}
function assertField(item, key, oldValue, newValue, changed = true) {
  const field = item.fields.find(value => value.key === key);
  assert.ok(field, `${item.key}: missing ${key} field`);
  assert.deepEqual(field.before, oldValue, `${item.key}: old ${key}`);
  assert.deepEqual(field.after, newValue, `${item.key}: new ${key}`);
  assert.equal(field.changed, changed, `${item.key}: ${key} change flag`);
}
function assertPaintedContact(point, node, label) {
  const x = point.x - node.x, y = point.y - node.y;
  const qx = Math.abs(x - 95) - 83, qy = Math.abs(y - 38) - 26;
  // Independent signed distance to the expected 190 x 76, radius-12 painted rectangle.
  const distance = Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) + Math.min(Math.max(qx, qy), 0) - 12;
  assert.ok(Math.abs(distance) < 1e-7, `${label}: endpoint misses expected painted border by ${distance}`);
}
function assertSide(side, model, statuses = {}) {
  assertMembers(side.nodes.map(node => node.id), model.states, "state membership");
  assertMembers(side.edges.map(edge => edge.id), model.transitions.map(edge => edge.id), "transition membership");
  const nodes = new Map(side.nodes.map(node => [node.id, node]));
  for (const node of side.nodes) {
    assert.ok(Number.isFinite(node.x) && Number.isFinite(node.y), `${node.id}: finite coordinates`);
    assert.equal(node.width, 190); assert.equal(node.height, 76);
    assert.equal(node.initial, node.id === model.initial_state, `${node.id}: initial marker`);
    if (statuses[`state:${node.id}`]) assert.equal(node.status, statuses[`state:${node.id}`]);
  }
  for (const expected of model.transitions) {
    const edge = side.edges.find(value => value.id === expected.id);
    for (const key of ["from_state", "to_state", "action", "role"]) {
      assert.equal(edge[key], expected[key], `${edge.id}: ${key} belongs to this side`);
    }
    if (statuses[`transition:${edge.id}`]) assert.equal(edge.status, statuses[`transition:${edge.id}`]);
    assert.ok(edge.points.length >= 2, `${edge.id}: routed points`);
    assert.ok([...edge.points, edge.label].every(point => Number.isFinite(point.x) && Number.isFinite(point.y)));
    assertPaintedContact(edge.points[0], nodes.get(expected.from_state), `${edge.id} source`);
    assertPaintedContact(edge.points.at(-1), nodes.get(expected.to_state), `${edge.id} target`);
  }
}
function projection(direction = "TB", oldModel = before, newModel = after) {
  return compare.project(oldModel, newModel, {direction, viewport:{width:620, height:540}});
}
function geometryOnly(result) {
  const canonical = side => ({
    nodes:[...side.nodes].sort((a, b) => a.id.localeCompare(b.id)),
    edges:[...side.edges].sort((a, b) => a.id.localeCompare(b.id))
  });
  return {before:canonical(result.before), after:canonical(result.after), direction:result.direction, bounds:result.bounds};
}

test("inventory exposes every added, removed and modified element with exact old and new semantics", () => {
  const inventory = compare.inventory(before, after);
  assertChanges(inventory, expectedChanges);
  const item = inventory.items.find(value => value.key === "transition:T-CHANGE");
  assert.equal(item.kind, "transition"); assert.equal(item.id, "T-CHANGE");
  assertField(item, "role", "Owner", "Agent");
  assertField(item, "guards", ["active", "assigned"], ["active"]);
  assertField(item, "required_effects", ["audit"], ["audit", "notify"]);
  assertField(item, "forbidden_effects", ["publish"], ["publish", "payment"]);
  assertField(item, "action", "Recommend", "Recommend", false);
  assertField(inventory.items.find(value => value.key === "transition:T-RETARGET"), "to_state", "Done", "New");
  for (const id of ["T-KEEP", "T-PARALLEL", "T-LOOP"]) {
    assert.equal(inventory.items.find(value => value.key === `transition:${id}`).status, "unchanged");
  }
});

test("initial-only and isolated-state differences survive without any transition changes", () => {
  const onlyBefore = freeze({states:["A", "B"], initial_state:"A", transitions:[]});
  const onlyAfter = freeze({states:["A", "B"], initial_state:"B", transitions:[]});
  assertChanges(compare.inventory(onlyBefore, onlyAfter), {"initial:initial_state":"changed"});
  const onlyProjection = projection("TB", onlyBefore, onlyAfter);
  assertSide(onlyProjection.before, onlyBefore); assertSide(onlyProjection.after, onlyAfter);
  const inventory = compare.inventory(initialBefore, initialAfter);
  assertChanges(inventory, initialChanges);
  const initial = inventory.items.find(item => item.key === "initial:initial_state");
  assert.equal(initial.kind, "initial"); assert.equal(initial.id, "initial_state");
  assert.equal(initial.before, "A"); assert.equal(initial.after, "B");
  const result = projection("TB", initialBefore, initialAfter);
  assertSide(result.before, initialBefore, initialChanges);
  assertSide(result.after, initialAfter, initialChanges);
  assert.equal(result.before.nodes.find(node => node.id === "A").initial, true);
  assert.equal(result.after.nodes.find(node => node.id === "B").initial, true);
});

test("paired LR and TB projections share coordinates and unchanged routes while preserving side membership", () => {
  for (const direction of ["LR", "TB"]) {
    const result = projection(direction);
    assert.equal(result.direction, direction);
    assertSide(result.before, before, expectedChanges);
    assertSide(result.after, after, expectedChanges);
    for (const id of ["Draft", "Review", "Done"]) {
      const oldNode = result.before.nodes.find(node => node.id === id);
      const newNode = result.after.nodes.find(node => node.id === id);
      assert.deepEqual([oldNode.x, oldNode.y], [newNode.x, newNode.y]);
    }
    for (const id of ["T-KEEP", "T-PARALLEL", "T-LOOP"]) {
      const oldEdge = result.before.edges.find(edge => edge.id === id);
      const newEdge = result.after.edges.find(edge => edge.id === id);
      assert.deepEqual(oldEdge.points, newEdge.points, `${id}: unchanged route`);
      assert.deepEqual(oldEdge.label, newEdge.label, `${id}: unchanged label anchor`);
    }
    const edges = result.before.edges;
    assert.notDeepEqual(edges.find(edge => edge.id === "T-KEEP").points,
      edges.find(edge => edge.id === "T-PARALLEL").points, "parallel transitions remain distinct");
    const box = result.bounds;
    assert.ok([box.x, box.y, box.width, box.height].every(Number.isFinite));
    for (const side of [result.before, result.after]) for (const node of side.nodes) {
      assert.ok(node.x >= box.x && node.y >= box.y && node.x + node.width <= box.x + box.width &&
        node.y + node.height <= box.y + box.height, `${node.id}: common bounds include both sides`);
    }
  }
});

test("an independently checked endpoint oracle rejects a lying path even when its semantic labels stay correct", () => {
  for (const direction of ["LR", "TB"]) {
    const result = projection(direction);
    assertSide(result.after, after, expectedChanges);
    const altered = copy(result.after), wrongNode = altered.nodes.find(node => node.id === "Done");
    const edge = altered.edges.find(value => value.id === "T-RETARGET");
    edge.points[edge.points.length - 1] = {x:wrongNode.x + 190, y:wrongNode.y + 38};
    assert.equal(edge.to_state, "New", "the negative control leaves declared identity unchanged");
    assert.throws(() => assertSide(altered, after, expectedChanges), /expected painted border/);
  }
});

test("membership and marker oracles reject missing additions, removals and an omitted initial marker", () => {
  const result = projection();
  assertSide(result.before, before, expectedChanges); assertSide(result.after, after, expectedChanges);
  for (const [name, model, collection, id] of [
    ["after", after, "nodes", "Spare"], ["before", before, "nodes", "Unused"],
    ["after", after, "edges", "T-ADD"], ["before", before, "edges", "T-REMOVE"]
  ]) {
    const altered = copy(result[name]);
    altered[collection] = altered[collection].filter(item => item.id !== id);
    assert.throws(() => assertSide(altered, model, expectedChanges), /exact membership/);
  }
  const initial = projection("TB", initialBefore, initialAfter);
  assertSide(initial.after, initialAfter, initialChanges);
  const altered = copy(initial.after);
  altered.nodes.find(node => node.id === "B").initial = false;
  assert.throws(() => assertSide(altered, initialAfter, initialChanges), /initial marker/);
});

test("change and field oracles reject omitted modifications, effects and initial-state changes", () => {
  const inventory = compare.inventory(before, after);
  assertChanges(inventory, expectedChanges);
  const missingChange = copy(inventory);
  missingChange.changes = missingChange.changes.filter(item => item.key !== "transition:T-CHANGE");
  assert.throws(() => assertChanges(missingChange, expectedChanges), /exact membership/);
  const changed = inventory.items.find(item => item.key === "transition:T-CHANGE");
  assertField(changed, "role", "Owner", "Agent");
  const concealedRole = copy(changed);
  concealedRole.fields.find(field => field.key === "role").changed = false;
  assert.throws(() => assertField(concealedRole, "role", "Owner", "Agent"), /role change flag/);
  assertField(changed, "required_effects", ["audit"], ["audit", "notify"]);
  const missingEffect = copy(changed);
  missingEffect.fields = missingEffect.fields.filter(field => field.key !== "required_effects");
  assert.throws(() => assertField(missingEffect, "required_effects", ["audit"], ["audit", "notify"]), /missing required_effects/);
  const initial = compare.inventory(initialBefore, initialAfter);
  assertChanges(initial, initialChanges);
  const missingInitial = copy(initial);
  missingInitial.changes = missingInitial.changes.filter(item => item.kind !== "initial");
  assert.throws(() => assertChanges(missingInitial, initialChanges), /exact membership/);
});

test("projection is deterministic under input reordering and does not mutate frozen source models", () => {
  const original = JSON.stringify({before, after});
  const shuffled = model => freeze({...model, states:[...model.states].reverse(), transitions:[...model.transitions].reverse()});
  for (const direction of ["LR", "TB", "AUTO"]) {
    assert.deepEqual(geometryOnly(projection(direction, shuffled(before), shuffled(after))),
      geometryOnly(projection(direction)), `${direction}: input order does not move semantic geometry`);
  }
  compare.inventory(before, after);
  assert.equal(JSON.stringify({before, after}), original);
  const reorderedSets = freeze({...before, transitions:before.transitions.map(item => ({...item,
    guards:[...item.guards].reverse(), required_effects:[...item.required_effects].reverse(),
    forbidden_effects:[...item.forbidden_effects].reverse()}))});
  assert.equal(compare.inventory(before, reorderedSets).changes.length, 0, "set order is not a semantic edit");
});

test("prototype-looking state and transition IDs remain literal identities in inventory and geometry", () => {
  const model = freeze({states:["__proto__", "constructor", "<script>"], initial_state:"__proto__", transitions:[
    transition("__proto__", "__proto__", "constructor", {action:"<img src=x>", role:"<script>"}),
    transition("constructor", "constructor", "<script>")
  ]});
  const original = JSON.stringify(model), inventory = compare.inventory(model, model);
  assert.equal(inventory.changes.length, 0);
  assert.ok(inventory.items.some(item => item.key === "state:__proto__"));
  assert.ok(inventory.items.some(item => item.key === "transition:constructor"));
  const result = projection("LR", model, model);
  assertSide(result.before, model); assertSide(result.after, model);
  assert.equal(result.after.edges.find(edge => edge.id === "__proto__").action, "<img src=x>");
  assert.equal(JSON.stringify(model), original);
});

test("bindings match exact typed references and initial changes include both states without guessing source links", () => {
  const item = compare.inventory(before, after).items.find(value => value.key === "transition:T-CHANGE");
  const hostile = "repo://<script>#symbol";
  const terms = freeze([
    {refs:["transition:T-CHANGE"], binds:["repo://src/runtime.py#recommend", hostile]},
    {refs:["transition:T-CHANGE-extra"], binds:["repo://wrong-prefix"]},
    {refs:["state:T-CHANGE"], binds:["repo://wrong-kind"]},
    {refs:["transition:T-KEEP"], binds:["repo://unrelated"]}
  ]);
  assert.deepEqual(sorted(compare.bindings(item, terms)), sorted(["repo://src/runtime.py#recommend", hostile]));
  const initial = compare.inventory(initialBefore, initialAfter).items.find(value => value.kind === "initial");
  assert.deepEqual(sorted(compare.bindings(initial, freeze([
    {refs:["state:A"], binds:["repo://old-start"]}, {refs:["state:B"], binds:["repo://new-start"]},
    {refs:["state:B-extra"], binds:["repo://wrong-prefix"]}, {refs:["transition:A"], binds:["repo://wrong-kind"]}
  ]))), ["repo://new-start", "repo://old-start"]);
  assert.deepEqual(compare.bindings(item, []), []);
});

test("restored selection and viewport belong to the exact case revision and missing selections are discarded", () => {
  const inventory = compare.inventory(before, after), subject = freeze({case:"case-a", revision:7});
  const saved = freeze({subject, selected:{kind:"transition", id:"T-CHANGE"},
    viewport:{cx:123, cy:456, scale:1.25}, direction:"LR"});
  const original = JSON.stringify(saved), restored = compare.restoreState(subject, inventory, saved);
  assert.deepEqual(restored, saved);
  for (const mismatch of [{case:"case-b", revision:7}, {case:"case-a", revision:8}]) {
    assert.deepEqual(compare.restoreState(mismatch, inventory, saved),
      {subject:mismatch, selected:null, viewport:null, direction:"TB"});
  }
  const missing = compare.restoreState(subject, inventory, {...saved, selected:{kind:"transition", id:"NO-LONGER-PRESENT"}});
  assert.equal(missing.selected, null, "a stale selection must not follow an unrelated element");
  assert.deepEqual(compare.restoreState(subject, inventory, null),
    {subject, selected:null, viewport:null, direction:"TB"});
  assert.equal(JSON.stringify(saved), original);
});

function assertFramed(boxes, viewport, sizes, padding = 19.999) {
  for (const size of sizes) for (const box of boxes) {
    const left = (box.x - viewport.cx) * viewport.scale + size.width / 2;
    const top = (box.y - viewport.cy) * viewport.scale + size.height / 2;
    assert.ok(left >= padding && top >= padding, "selected content begins inside each pane");
    assert.ok(left + box.width * viewport.scale <= size.width - padding, "selected content ends inside pane width");
    assert.ok(top + box.height * viewport.scale <= size.height - padding, "selected content ends inside pane height");
  }
}
test("focus framing includes each side's selected endpoints, route and measured label bounds", () => {
  const result = freeze(projection()), item = result.inventory.items.find(value => value.key === "transition:T-RETARGET");
  // Browser getBBox supplies text/paint bounds; this deliberately exceeds the routed node bounds.
  const measured = freeze([{x: -120, y: 12, width: 500, height: 31}]);
  const source = JSON.stringify(result), box = compare.selectionBounds(result, item, measured);
  const selected = [];
  for (const [side, model] of [[result.before, before], [result.after, after]]) {
    const t = model.transitions.find(value => value.id === "T-RETARGET");
    selected.push(...side.nodes.filter(node => [t.from_state, t.to_state].includes(node.id)));
    selected.push(...side.edges.find(edge => edge.id === t.id).points.map(point => ({...point, width: 0, height: 0})));
  }
  for (const sizes of [[{width: 640, height: 480}, {width: 635, height: 480}], [{width: 420, height: 255}, {width: 410, height: 245}]]) {
    const view = compare.frameBounds(box, sizes);assert.ok(view.scale > 0 && view.scale <= 1);
    assertFramed([...selected, ...measured], view, sizes);
  }
  assert.equal(JSON.stringify(result), source);
});
test("focus framing shows added and removed state and initial-state selections without phantom endpoints", () => {
  const result = freeze(projection("TB", initialBefore, initialAfter));
  for (const key of ["state:Removed", "state:Added", "initial:initial_state"]) {
    const item = result.inventory.items.find(value => value.key === key), box = compare.selectionBounds(result, item);
    const ids = item.kind === "initial" ? ["A", "B"] : [item.id];
    const nodes = [...result.before.nodes, ...result.after.nodes].filter(node => ids.includes(node.id));
    assertFramed(nodes, compare.frameBounds(box, [{width: 450, height: 280}]), [{width: 450, height: 280}]);
  }
});
test("the clipping oracle rejects the original forced 100 percent focus on a tall selection", () => {
  const box = freeze({x: 100, y: 90, width: 260, height: 610}), sizes = freeze([{width: 480, height: 310}]);
  const fixed = compare.frameBounds(box, sizes);assertFramed([box], fixed, sizes);assert.ok(fixed.scale < 0.5);
  assert.throws(() => assertFramed([box], {...fixed, scale: 1}, sizes), /selected content/);
});
test("fitting never enlarges small content and handles tiny panes without a false 100 percent label", () => {
  const small = freeze({x: 20, y: 40, width: 190, height: 76});
  assert.equal(compare.frameBounds(small, [{width: 800, height: 600}]).scale, 1);
  const tiny = compare.frameBounds(small, [{width: 32, height: 20}]);
  assert.ok(Number.isFinite(tiny.scale) && tiny.scale > 0 && tiny.scale < 0.1);
});
test("actual viewport handlers defer hidden hosts instead of publishing invented dimensions", () => {
  const fs = require("node:fs"), vm = require("node:vm");
  const source = fs.readFileSync(process.env.EIJA_COMPARE_MODULE || path.join(web, "compare.js"), "utf8");
  const start = source.indexOf("  function dimensions(s)"), end = source.indexOf("  return {render, inventory");
  assert.ok(start >= 0 && end > start);const handlers = {};vm.createContext(handlers);vm.runInContext(source.slice(start, end), handlers);
  const layout = projection(), item = layout.inventory.items.find(value => value.key === "transition:T-RETARGET");
  const host = {clientWidth: 0, clientHeight: 0}, board = {setAttribute:()=>{throw Error("A hidden SVG must not publish a fallback viewBox");}};
  const s = {state:{viewport:null},panes:[{host,board}],shell:{dataset:{}},layout,selected:()=>item,groups:[],scale:{},scaleHint:{},notify:()=>{}};
  handlers.focusSelection(s);assert.equal(s.state.viewport,null);assert.equal(s.shell.dataset.compareView,"focus");
  handlers.fit(s);assert.equal(s.state.viewport,null);assert.equal(s.shell.dataset.compareView,"overview");
  host.clientWidth=430;host.clientHeight=275;const boxes=[];board.setAttribute=(name,value)=>boxes.push({name,value});
  handlers.focusSelection(s);assert.equal(s.shell.dataset.compareView,"focus");assert.equal(boxes[0].name,"viewBox");
  assertFramed([compare.selectionBounds(layout,item)],s.state.viewport,[{width:430,height:275}]);
});

test("declared impact families navigate to exact model changes or explicitly case-wide views", () => {
  const expected = {
    "rule:Recommend": {view:"review", kind:"transition", id:"T-CHANGE"},
    "state-view:Recommend": {view:"review", kind:"transition", id:"T-CHANGE"},
    "runtime:Recommend": {view:"try", action:"Recommend"},
    "journey:Recommend": {view:"impact", action:"Recommend"},
    "obligation:Recommend": {view:"evidence", section:"overview"},
    "receipt:Recommend": {view:"evidence", section:"overview"},
    "review-packet": {view:"evidence", section:"overview"},
    "local-decision": {view:"evidence", section:"decision"}
  };
  const original = JSON.stringify({before, after});
  for (const [reference, target] of Object.entries(expected)) {
    const route = compare.impactNavigation(reference, before, after);
    assert.deepEqual(route.target, target, reference);
    assert.equal(route.reference, reference);
    assert.ok(route.label.length > 0 && route.scope.length > 0);
    assert.ok(!JSON.stringify(route).includes("repo://"), "projection navigation invents no source link");
    if (target.view === "evidence") assert.match(route.scope, /Case-wide.*not an individual receipt or verdict/);
  }
  assert.equal(JSON.stringify({before, after}), original);
});

test("removed actions keep exact comparison and case evidence, with no candidate runtime or journey link", () => {
  assert.deepEqual(compare.impactNavigation("rule:Restore", before, after).target,
    {view:"review", kind:"transition", id:"T-REMOVE"});
  assert.deepEqual(compare.impactNavigation("receipt:Restore", before, after).target,
    {view:"evidence", section:"overview"});
  for (const kind of ["runtime", "journey"]) {
    const route = compare.impactNavigation(`${kind}:Restore`, before, after);
    assert.equal(route.target, null); assert.match(route.reason, /only in the baseline/);
  }
});

test("unknown and ambiguous impact references never choose a destination by prefix or first match", () => {
  for (const reference of ["repo://src/runtime.py", "receipt:Recommend-extra", "rule:", "unknown:Recommend", "review-packet:extra", "local-decision:extra", null]) {
    assert.equal(compare.impactNavigation(reference, before, after).target, null, String(reference));
  }
  const ambiguous = freeze({...after, transitions:[...after.transitions,
    transition("T-SECOND", "Draft", "Done", {action:"Recommend"})]});
  for (const kind of ["rule", "runtime", "state-view", "journey", "obligation", "receipt"]) {
    const route = compare.impactNavigation(`${kind}:Recommend`, before, ambiguous);
    assert.equal(route.target, null); assert.match(route.reason, /multiple transition identities/);
  }
  const renamedIdentity = freeze({...after, transitions:after.transitions.map(item =>
    item.id === "T-CHANGE" ? {...item, id:"T-RENAMED"} : item)});
  assert.equal(compare.impactNavigation("rule:Recommend", before, renamedIdentity).target, null);
});

test("literal action and transition identities remain exact, including prototype-looking values", () => {
  const model = freeze({transitions:[transition("__proto__", "A", "B", {action:"constructor"})]});
  assert.deepEqual(compare.impactNavigation("rule:constructor", model, model).target,
    {view:"review", kind:"transition", id:"__proto__"});
  assert.equal(compare.impactNavigation("rule:Constructor", model, model).target, null);
});

test("actual impact renderer exposes supported destinations and explanatory nonlinks with exact context", () => {
  const fs = require("node:fs"), vm = require("node:vm");
  const source = fs.readFileSync(process.env.EIJA_COMPARE_MODULE || path.join(web, "compare.js"), "utf8");
  const begin = source.indexOf("  function buildContext(s) {"), end = source.indexOf("  function dimensions(s)", begin);
  assert.ok(begin >= 0 && end > begin);
  const element = (tag, content) => ({tag, textContent:content, children:[], dataset:{}, append(...nodes){this.children.push(...nodes);}});
  const button = (label, onclick) => ({...element("button", label), onclick});
  const buildContext = vm.runInNewContext("(" + source.slice(begin, end).trim() + ")", {element, button, impactNavigation:compare.impactNavigation});
  const routes = [], s = {shell:element("section"), c:{baseline:before, candidate:after, transactions:[]},
    packet:{impact:{complete:true, affected:["rule:Recommend", "receipt:Recommend", "runtime:Restore", "unknown:Recommend"]}},
    callbacks:{openImpact:(...args)=>routes.push(args), openReference:()=>{throw Error("Projection references must not use generic source navigation");}},
    subject:{case:"case-current", revision:8}, state:{selected:{kind:"state", id:"New"}}, stopped:false};
  buildContext(s);
  const impact = s.shell.children[0].children[0], controls = impact.children.filter(node => node.tag === "button");
  assert.deepEqual(controls.map(node => node.dataset.compareImpact), ["rule:Recommend", "receipt:Recommend"]);
  assert.equal(impact.children.filter(node => node.dataset?.compareImpactUnavailable).length, 2);
  controls[0].onclick();
  assert.deepEqual(routes[0][0].target, {view:"review", kind:"transition", id:"T-CHANGE"});
  assert.deepEqual(JSON.parse(JSON.stringify(routes[0][1])), {case:"case-current", revision:8, kind:"state", id:"New"});
  controls[1].onclick(); assert.match(routes[1][0].scope, /Case-wide/);
  s.stopped = true; controls[0].onclick(); assert.equal(routes.length, 2, "destroyed render cannot navigate");
});

test("actual selected-change inspector sends exact context only for current candidate transitions", () => {
  const fs = require("node:fs"), vm = require("node:vm");
  const source = fs.readFileSync(process.env.EIJA_COMPARE_MODULE || path.join(web, "compare.js"), "utf8");
  const begin = source.indexOf("  function updateSelection(s) {"), end = source.indexOf("  function buildContext(s)", begin);
  assert.ok(begin >= 0 && end > begin);
  const element = (tag, content) => ({tag, textContent:content, children:[], dataset:{}, append(...nodes){this.children.push(...nodes);}, replaceChildren(){this.children=[];}});
  const button = (label, onclick, action) => ({...element("button", label), onclick, dataset:{compareAction:action}});
  const updateSelection = vm.runInNewContext("(" + source.slice(begin, end).trim() + ")", {
    element, button, bindings:()=>[], fieldTable:()=>element("table"), itemTitle:item=>item.id,
    statusLabel:{changed:"Modified", removed:"Removed", unchanged:"Unchanged"}
  });
  const calls = [], item = {kind:"transition", id:"T-CHANGE", key:"transition:T-CHANGE", status:"changed", fields:[], before:{}, after:{}};
  const s = {selected:()=>item, buttons:[], groups:[], panes:[], detail:element("section"), announcement:element("p"),
    callbacks:{inspectTransition:(...args)=>calls.push(args)}, subject:{case:"case-current", revision:8},
    state:{selected:{kind:"transition", id:"T-CHANGE"}}, stopped:false};
  const descendants = node => [node, ...node.children.flatMap(descendants)];
  updateSelection(s);
  const inspect = descendants(s.detail).find(node => node.dataset.compareAction === "inspect-model");
  assert.equal(inspect.textContent, "Inspect in model"); inspect.onclick();
  assert.deepEqual(JSON.parse(JSON.stringify(calls)), [["T-CHANGE", {case:"case-current", revision:8, kind:"transition", id:"T-CHANGE"}]]);
  s.stopped = true; inspect.onclick(); assert.equal(calls.length, 1);
  delete item.after; item.status = "removed"; updateSelection(s);
  assert.ok(!descendants(s.detail).some(node => node.dataset.compareAction === "inspect-model"), "removed transition has no current-model control");
});

test("prospective comparison labels both server snapshots without reusing current evidence or source navigation", () => {
  const fs = require("node:fs"), vm = require("node:vm");
  const source = fs.readFileSync(process.env.EIJA_COMPARE_MODULE || path.join(web, "compare.js"), "utf8");
  const element = (tag, content) => ({tag, textContent:content, children:[], dataset:{},
    append(...nodes){this.children.push(...nodes);},replaceChildren(){this.children=[];},setAttribute(){}});
  const descendants = node => [node,...node.children.flatMap(descendants)];
  const handlers = {element,textValue:value=>String(value),itemTitle:item=>item.id,statusLabel:{changed:"Modified"},
    bindings:()=>{throw Error("Captured comparison must not inherit live source bindings");}};
  vm.createContext(handlers);
  for(const [start,end] of [["  function fieldTable(","  function render("],["  function updateSelection(","  function dimensions("]]) {
    vm.runInContext(source.slice(source.indexOf(start),source.indexOf(end)),handlers);
  }
  const fields = [{key:"role",label:"Role",before:"Owner",after:"Agent",changed:true}];
  const item={kind:"transition",id:"T-CHANGE",status:"changed",fields,before:{},after:{}};
  const s={selected:()=>item,buttons:[],groups:[],panes:[],detail:element("section"),announcement:element("p"),shell:element("section"),
    callbacks:{preview:true,openEvidence:()=>{throw Error("No evidence inherited by captured comparison");}},subject:{case:"A",revision:7},state:{selected:{kind:"transition",id:item.id}}};
  handlers.updateSelection(s);handlers.buildContext(s);
  const texts=descendants(s.detail).map(node=>node.textContent).filter(Boolean);
  assert.ok(texts.includes("Captured before"));assert.ok(texts.includes("Proposed result"));
  assert.ok(texts.includes("Owner")&&texts.includes("Agent"));assert.equal(s.shell.children.length,0);
  assert.match(s.announcement.textContent,/Captured edit comparison for revision 7/);
  const ordinary=descendants(handlers.fieldTable(fields)).map(node=>node.textContent);
  assert.ok(ordinary.includes("Before · baseline")&&ordinary.includes("After · candidate"),"normal review keeps its existing subject captions");
});

function previewSummaryHarness(preview = true, alter = text => text) {
  const fs = require("node:fs"), vm = require("node:vm");
  const source = alter(fs.readFileSync(process.env.EIJA_COMPARE_MODULE || path.join(web, "compare.js"), "utf8"));
  const element = (tag, value, className) => ({tag, className, ownText:value === undefined ? "" : String(value), children:[], dataset:{}, attributes:{},
    get textContent(){return this.ownText + this.children.map(node => node.textContent).join("");},
    set textContent(value){this.ownText = String(value);this.children=[];},
    append(...nodes){this.children.push(...nodes);},replaceChildren(...nodes){this.ownText="";this.children=[...nodes];},
    setAttribute(name,value){this.attributes[name]=String(value);}});
  const calls = [];
  const button = (label, onclick, action) => ({...element("button", label), onclick, dataset:action ? {compareAction:action} : {}});
  const handlers = {element, button, bindings:compare.bindings, statusLabel:{changed:"Modified",added:"Added",removed:"Removed",unchanged:"Unchanged"}};
  vm.createContext(handlers);
  for(const [start,end] of [["  const textValue =", "  function engines()"], ["  function itemTitle(", "  function render("], ["  function updateSelection(", "  function buildContext("]]) {
    vm.runInContext(source.slice(source.indexOf(start),source.indexOf(end)),handlers);
  }
  let item;
  const visual=element("div",undefined,"compare-visual-workspace");
  const s={selected:()=>item,buttons:[],groups:[],panes:[],detail:element("section"),announcement:element("p"),shell:element("section"),visual,
    callbacks:{preview,terms:[],openReference:(...args)=>calls.push(["source",...args]),openEvidence:(...args)=>calls.push(["evidence",...args]),inspectTransition:(...args)=>calls.push(["model",...args])},
    subject:{case:"A",revision:7},state:{selected:null}};
  handlers.buildSelectedSummary(s);
  // Execute the real summary builder; a separate browser oracle must establish painted fit.
  const summaryAt=source.indexOf("buildSelectedSummary(session);"), pairAt=source.indexOf("buildPair(session);");
  assert.ok(summaryAt>=0 && summaryAt<pairAt);
  s.shell.append(visual);
  return {s,visual,calls,get summary(){return s.previewSummary||s.changeSummary;},select(value){item=value;s.state.selected={kind:item.kind,id:item.id};handlers.updateSelection(s);},
    row(key){return this.summary?.children.find(node=>node.dataset.field===key);},
    pair(key){const row=this.row(key);return row && [row.children.find(node=>Object.hasOwn(node.dataset,"compareBefore")).textContent,row.children.find(node=>Object.hasOwn(node.dataset,"compareAfter")).textContent];}};
}

test("preview summary exposes exact selected role and endpoint deltas before the diagram workspace", () => {
  const base={states:["A","B","C"],initial_state:"A",transitions:[transition("T","A","B")]};
  for(const [field,label,value] of [["role","Role","Agent"],["from_state","Source state","C"],["to_state","Target state","C"]]) {
    const next={...base,transitions:[{...base.transitions[0],[field]:value}]}, original=JSON.stringify({base,next});
    const h=previewSummaryHarness();h.select(compare.inventory(base,next).items.find(item=>item.key==="transition:T"));
    assert.equal(h.s.shell.children[0],h.s.previewSummary);assert.equal(h.s.shell.children[1],h.visual);
    assert.deepEqual(h.pair(field),[base.transitions[0][field],value]);assert.equal(h.row(field).textContent,`${label}: ${base.transitions[0][field]} → ${value}`);
    assert.deepEqual({...h.s.previewSummary.dataset},{kind:"transition",id:"T"});
    assert.match(h.s.previewSummary.textContent,/Selected element’s changes/);assert.equal(JSON.stringify({base,next}),original);
  }
  const ordinary=previewSummaryHarness(false);assert.equal(ordinary.s.previewSummary,undefined);
  assert.deepEqual(ordinary.s.shell.children,[ordinary.visual]);assert.equal(ordinary.visual.children[0],ordinary.s.changeSummary);
});

test("preview summary preserves multiple array values and distinguishes absent sides, empty arrays and initial changes", () => {
  const h=previewSummaryHarness();h.select(compare.inventory(before,after).items.find(item=>item.key==="transition:T-CHANGE"));
  assert.deepEqual(h.pair("role"),["Owner","Agent"]);
  assert.deepEqual(h.pair("guards"),[JSON.stringify(["active","assigned"],null,2),JSON.stringify(["active"],null,2)]);
  assert.deepEqual(h.pair("required_effects"),[JSON.stringify(["audit"],null,2),JSON.stringify(["audit","notify"],null,2)]);
  assert.deepEqual(h.pair("forbidden_effects"),[JSON.stringify(["publish"],null,2),JSON.stringify(["publish","payment"],null,2)]);
  h.select(compare.inventory(before,after).items.find(item=>item.key==="transition:T-ADD"));assert.deepEqual(h.pair("guards"),["Not present","[] (none declared)"]);
  h.select(compare.inventory(before,after).items.find(item=>item.key==="transition:T-REMOVE"));assert.deepEqual(h.pair("guards"),["[] (none declared)","Not present"]);
  const initial=compare.inventory(initialBefore,initialAfter);
  for(const [key,expected] of [["state:Added",["Not present","Present"]],["state:Removed",["Present","Not present"]]]) {
    h.select(initial.items.find(item=>item.key===key));assert.deepEqual(h.pair("membership"),expected);
  }
  h.select(initial.items.find(item=>item.kind==="initial"));assert.deepEqual(h.pair("initial_state"),["A","B"]);
});

test("selection changes replace the summary truthfully without resetting viewport or interpreting display strings", () => {
  const model={states:["A","B"],initial_state:"A",transitions:[transition("T","A","B")]};
  const changed={...model,transitions:[{...model.transitions[0],role:'<img src=x onerror="execute()">'}]}, inventory=compare.inventory(model,changed);
  const h=previewSummaryHarness(),viewport=Object.freeze({cx:125,cy:100,scale:0.85});h.s.state.viewport=viewport;
  h.select(inventory.items.find(item=>item.kind==="transition"));assert.deepEqual(h.pair("role"),["Owner",changed.transitions[0].role]);
  assert.equal(h.row("role").children.filter(node=>node.tag==="img").length,0);
  h.select(inventory.items.find(item=>item.kind==="state"));assert.equal(h.row("role"),undefined);assert.match(h.s.previewSummary.textContent,/No changed fields for this selected element/);
  assert.equal(h.s.state.viewport,viewport);assert.equal(h.s.state.viewport.scale,0.85);
});

test("summary value oracle rejects omitted and reversed role consequences", () => {
  const item=compare.inventory(before,after).items.find(item=>item.key==="transition:T-CHANGE");
  const omitted=previewSummaryHarness(true,source=>source.replace("for (const field of changed) {",'for (const field of changed.filter(value=>value.key!=="role")) {'));
  omitted.select(item);assert.throws(()=>assert.deepEqual(omitted.pair("role"),["Owner","Agent"]),assert.AssertionError);
  const reversed=previewSummaryHarness(true,source=>source.replace('before = element("span", textValue(field.before)), after = element("span", textValue(field.after))','before = element("span", textValue(field.after)), after = element("span", textValue(field.before))'));
  reversed.select(item);assert.deepEqual(reversed.pair("role"),["Agent","Owner"]);assert.throws(()=>assert.deepEqual(reversed.pair("role"),["Owner","Agent"]),assert.AssertionError);
});

test("ordinary summary presents exact role, source and guard deltas above graphs with current selected subject", () => {
  const base=freeze({states:["A","B","C"],initial_state:"A",transitions:[transition("T","A","B",{action:"Verify",guards:["active","assigned"]})]});
  for(const [field,value,expected] of [["role","Agent",["Owner","Agent"]],["from_state","C",["A","C"]],
    ["guards",["active"],[JSON.stringify(["active","assigned"],null,2),JSON.stringify(["active"],null,2)]]]) {
    const candidate=freeze({...base,transitions:[{...base.transitions[0],[field]:value}]}), original=JSON.stringify({base,candidate});
    const h=previewSummaryHarness(false);h.select(compare.inventory(base,candidate).items.find(item=>item.key==="transition:T"));
    assert.equal(h.visual.children[0],h.summary);assert.equal(h.s.shell.children[0],h.visual);
    assert.deepEqual({...h.summary.dataset},{kind:"transition",id:"T",case:"A",revision:"7"});
    assert.deepEqual(h.summary.children.filter(node=>node.dataset.field).map(node=>node.dataset.field),[field]);
    assert.deepEqual(h.pair(field),expected);assert.match(h.summary.textContent,/Modified · Verify · T/);
    assert.match(h.summary.textContent,/Before · baseline → After · candidate · revision 7/);
    assert.doesNotMatch(h.summary.textContent,/Proposed result|Captured before/);
    assert.equal(JSON.stringify({base,candidate}),original);assert.deepEqual(h.calls,[],"rendering cannot navigate or execute");
  }
});

test("ordinary summary retains complete arrays, missing sides and initial identity while replacing old selection", () => {
  const h=previewSummaryHarness(false),inventory=compare.inventory(before,after),viewport=Object.freeze({cx:100,cy:200,scale:0.75});h.s.state.viewport=viewport;
  h.select(inventory.items.find(item=>item.key==="transition:T-CHANGE"));
  assert.deepEqual(h.pair("guards"),[JSON.stringify(["active","assigned"],null,2),JSON.stringify(["active"],null,2)]);
  assert.deepEqual(h.pair("required_effects"),[JSON.stringify(["audit"],null,2),JSON.stringify(["audit","notify"],null,2)]);
  assert.deepEqual(h.pair("forbidden_effects"),[JSON.stringify(["publish"],null,2),JSON.stringify(["publish","payment"],null,2)]);
  h.select(inventory.items.find(item=>item.key==="transition:T-ADD"));assert.deepEqual(h.pair("guards"),["Not present","[] (none declared)"]);
  h.select(inventory.items.find(item=>item.key==="transition:T-REMOVE"));assert.deepEqual(h.pair("guards"),["[] (none declared)","Not present"]);
  const initial=compare.inventory(initialBefore,initialAfter);
  for(const [key,expected] of [["state:Added",["Not present","Present"]],["state:Removed",["Present","Not present"]]]) {
    h.select(initial.items.find(item=>item.key===key));assert.deepEqual(h.pair("membership"),expected);assert.equal(h.row("role"),undefined);
  }
  h.select(initial.items.find(item=>item.kind==="initial"));assert.deepEqual(h.pair("initial_state"),["A","B"]);
  h.select(inventory.items.find(item=>item.key==="transition:T-KEEP"));
  assert.equal(h.summary.dataset.id,"T-KEEP");assert.equal(h.summary.children.filter(node=>node.dataset.field).length,0);
  assert.match(h.summary.textContent,/No changed fields for this selected element/);assert.equal(h.s.state.viewport,viewport);
});

test("ordinary summary leaves declared source and exact revision navigation intact without inventing a binding", () => {
  const h=previewSummaryHarness(false),item=compare.inventory(before,after).items.find(item=>item.key==="transition:T-CHANGE");
  const ref="repo://src/runtime.py#recommend";
  h.s.callbacks.terms=[{refs:["transition:T-CHANGE"],binds:[ref]}];h.select(item);
  const all=node=>[node,...node.children.flatMap(all)],controls=all(h.s.detail);
  assert.deepEqual(h.calls,[]);controls.find(node=>node.dataset.compareReference===ref).onclick();
  controls.find(node=>node.dataset.compareAction==="evidence").onclick();controls.find(node=>node.dataset.compareAction==="inspect-model").onclick();
  const subject={case:"A",revision:7,kind:"transition",id:"T-CHANGE"};
  assert.deepEqual(JSON.parse(JSON.stringify(h.calls)),[["source",ref,subject],["evidence",subject],["model","T-CHANGE",subject]]);
  h.s.callbacks.terms=[];h.select(item);assert.equal(all(h.s.detail).filter(node=>node.dataset.compareReference).length,0);
  assert.match(h.s.detail.textContent,/Source binding unknown: no declared binding/);
});

test("ordinary summary oracle rejects omitted, reversed and retained stale field values", () => {
  const inventory=compare.inventory(before,after),item=inventory.items.find(item=>item.key==="transition:T-CHANGE");
  const omitted=previewSummaryHarness(false,source=>source.replace("for (const field of changed) {",'for (const field of changed.filter(value=>value.key!=="role")) {'));
  omitted.select(item);assert.throws(()=>assert.deepEqual(omitted.pair("role"),["Owner","Agent"]),assert.AssertionError);
  const reversed=previewSummaryHarness(false,source=>source.replace('before = element("span", textValue(field.before)), after = element("span", textValue(field.after))','before = element("span", textValue(field.after)), after = element("span", textValue(field.before))'));
  reversed.select(item);assert.throws(()=>assert.deepEqual(reversed.pair("role"),["Owner","Agent"]),assert.AssertionError);
  const stale=previewSummaryHarness(false,source=>source.replace("summary.replaceChildren(); Object.assign", "Object.assign"));
  stale.select(item);stale.select(inventory.items.find(value=>value.key==="transition:T-KEEP"));
  assert.throws(()=>assert.equal(stale.summary.children.filter(node=>node.dataset.field).length,0),assert.AssertionError);
});

test("ordinary summary preserves distinct literal whitespace values", () => {
  const base={states:["A","B"],initial_state:"A",transitions:[transition("T","A","B",{role:"Team  Lead"})]};
  const candidate={...base,transitions:[{...base.transitions[0],role:"Team Lead"}]};
  const h=previewSummaryHarness(false);h.select(compare.inventory(base,candidate).items.find(item=>item.key==="transition:T"));
  assert.deepEqual(h.pair("role"),["Team  Lead","Team Lead"]);
});


function viewportSession({preview = false, width = 420, height = 240} = {}) {
  const source = require("node:fs").readFileSync(process.env.EIJA_COMPARE_MODULE || path.join(web, "compare.js"), "utf8");
  const start = source.indexOf("  function dimensions(s)"), end = source.indexOf("  return {render, inventory");
  const handlers = {same:(a,b)=>Boolean(a&&b&&a.case===b.case&&a.revision===b.revision)};
  require("node:vm").createContext(handlers);require("node:vm").runInContext(source.slice(start,end),handlers);
  const layout=projection(), item=layout.inventory.items.find(value=>value.key==="transition:T-RETARGET");
  const host={clientWidth:width,clientHeight:height}, attributes={};
  const s={subject:{case:"A",revision:2},callbacks:{preview},state:{viewport:null},
    shell:{dataset:{}},layout,selected:()=>item,groups:[],scale:{},scaleHint:{},notify:()=>{},
    panes:[{host,board:{setAttribute:(key,value)=>{attributes[key]=value;}}}]};
  return {handlers,s,host,attributes,item};
}

test("ordinary initial and new selection center at natural scale; explicit fit keeps containment", () => {
  const {handlers,s,item}=viewportSession();
  handlers.initializeViewport(s);const box=compare.selectionBounds(s.layout,item);
  const readable=()=>{assert.equal(s.state.viewport.scale,1);assert.equal(s.scale.textContent,"100%");};
  readable();assert.equal(s.shell.dataset.compareView,"readable");
  assert.equal(s.state.viewport.cx,box.x+box.width/2);assert.equal(s.state.viewport.cy,box.y+box.height/2);
  handlers.focusSelection(s);assert.ok(s.state.viewport.scale<1);
  assertFramed([box],s.state.viewport,[{width:420,height:240}]);
  assert.throws(readable,/Expected values/); // Existing fit behavior must fail the distinct default-readability oracle.
  handlers.defaultSelection(s);readable();
});

test("preview default still fits and hidden ordinary entry defers its readable viewport", () => {
  const preview=viewportSession({preview:true});preview.handlers.initializeViewport(preview.s);
  assert.equal(preview.s.shell.dataset.compareView,"focus");
  assertFramed([compare.selectionBounds(preview.s.layout,preview.item)],preview.s.state.viewport,[{width:420,height:240}]);
  const hidden=viewportSession({width:0,height:0});hidden.handlers.initializeViewport(hidden.s);
  assert.equal(hidden.s.state.viewport,null);assert.deepEqual(hidden.attributes,{});
  assert.equal(hidden.s.shell.dataset.compareView,"readable");
  hidden.host.clientWidth=320;hidden.host.clientHeight=220;hidden.handlers.refreshViewport(hidden.s);
  assert.equal(hidden.s.state.viewport.scale,1);assert.ok(hidden.attributes.viewBox);
});

test("manual zoom and pan survive resize and matching-subject rerender", () => {
  const first=viewportSession();first.handlers.initializeViewport(first.s);
  first.handlers.setViewport(first.s,{cx:321,cy:654,scale:0.73});
  first.host.clientWidth=300;first.host.clientHeight=180;first.handlers.refreshViewport(first.s);
  const expected=JSON.stringify({cx:321,cy:654,scale:0.73});
  assert.equal(JSON.stringify(first.s.state.viewport),expected);assert.equal(first.s.shell.dataset.compareView,"manual");
  const next=viewportSession();next.s.state.viewport={...first.s.state.viewport};
  next.handlers.initializeViewport(next.s,{subject:{...first.s.subject},viewMode:"manual"});
  assert.equal(JSON.stringify(next.s.state.viewport),expected);assert.equal(next.s.shell.dataset.compareView,"manual");
});

test("explicit overview and fit survive resize and matching-subject rerender", () => {
  for(const mode of ["overview","focus"]){
    const first=viewportSession();first.handlers.initializeViewport(first.s);
    if(mode==="overview")first.handlers.fit(first.s);else first.handlers.focusSelection(first.s);
    first.host.clientWidth=300;first.host.clientHeight=180;first.handlers.refreshViewport(first.s);
    const box=mode==="overview"?first.s.layout.bounds:compare.selectionBounds(first.s.layout,first.item);
    assert.equal(first.s.shell.dataset.compareView,mode);assertFramed([box],first.s.state.viewport,[{width:300,height:180}]);
    const next=viewportSession();next.s.state.viewport={...first.s.state.viewport};
    next.handlers.initializeViewport(next.s,{subject:{...first.s.subject},viewMode:mode});
    assert.equal(next.s.shell.dataset.compareView,mode);assertFramed([box],next.s.state.viewport,[{width:420,height:240}]);
  }
});

test("old case or revision presentation cannot turn a fresh ordinary view into automatic fit", () => {
  for(const subject of [{case:"B",revision:2},{case:"A",revision:1}]){
    const fresh=viewportSession();fresh.handlers.initializeViewport(fresh.s,{subject,viewMode:"overview"});
    assert.equal(fresh.s.state.viewport.scale,1);assert.equal(fresh.s.shell.dataset.compareView,"readable");
  }
});

test("ordinary graph selection keeps its view even when its summary triggers resize", () => {
  for(const mode of ["readable","focus"]){
    const {handlers,s,host}=viewportSession();handlers.initializeViewport(s);
    if(mode==="focus")handlers.focusSelection(s);
    const previous=JSON.stringify(s.state.viewport);
    const selected=s.layout.inventory.items.find(item=>item.key==="state:Draft");assert.ok(selected);
    s.selected=()=>selected;
    handlers.selectionViewport(s,false);host.clientHeight=120;handlers.refreshViewport(s);
    assert.equal(JSON.stringify(s.state.viewport),previous);assert.equal(s.shell.dataset.compareView,"manual");
  }
  const preview=viewportSession({preview:true});preview.handlers.initializeViewport(preview.s);
  preview.handlers.selectionViewport(preview.s,false);assert.equal(preview.s.shell.dataset.compareView,"focus");
});

test("rejected saved coordinates default to readable after the hidden host becomes visible", () => {
  for(const viewport of [{cx:"invalid",cy:100,scale:0.5},{cx:200,cy:100,scale:0}]){
    const {handlers,s,host}=viewportSession({width:0,height:0});
    const saved={subject:{...s.subject},selected:{kind:"transition",id:"T-RETARGET"},viewMode:"overview",viewport};
    s.state=compare.restoreState(s.subject,s.layout.inventory,saved);assert.equal(s.state.viewport,null);
    handlers.initializeViewport(s,saved);assert.equal(s.state.viewport,null);assert.equal(s.shell.dataset.compareView,"readable");
    host.clientWidth=320;host.clientHeight=200;handlers.refreshViewport(s);
    assert.equal(s.state.viewport.scale,1);assert.equal(s.shell.dataset.compareView,"readable");
  }
});

test("hidden explicit fit and overview remain pending through a same-subject rerender", () => {
  for(const mode of ["focus","overview"]){
    const first=viewportSession({width:0,height:0});
    if(mode==="overview")first.handlers.fit(first.s);else first.handlers.focusSelection(first.s);
    const saved={subject:{...first.s.subject},viewport:first.s.state.viewport,viewMode:first.s.shell.dataset.compareView};
    const next=viewportSession({width:0,height:0});next.s.state=compare.restoreState(next.s.subject,next.s.layout.inventory,saved);
    next.handlers.initializeViewport(next.s,saved);assert.equal(next.s.state.viewport,null);assert.equal(next.s.shell.dataset.compareView,mode);
    next.host.clientWidth=320;next.host.clientHeight=200;next.handlers.refreshViewport(next.s);
    const box=mode==="overview"?next.s.layout.bounds:compare.selectionBounds(next.s.layout,next.item);
    assertFramed([box],next.s.state.viewport,[{width:320,height:200}]);assert.equal(next.s.shell.dataset.compareView,mode);
  }
});

function graphLabelHarness(alter = source => source) {
  const fs = require("node:fs"), vm = require("node:vm");
  const source = alter(fs.readFileSync(process.env.EIJA_COMPARE_MODULE || path.join(web, "compare.js"), "utf8"));
  const svg = (tag, attrs = {}, text) => ({tag, attrs:{...attrs}, textContent:text, children:[], listeners:{},
    append(...nodes){this.children.push(...nodes);}, setAttribute(key,value){this.attrs[key]=String(value);},
    addEventListener(name,callback){this.listeners[name]=callback;}});
  const begin=source.indexOf("  function selectable("), end=source.indexOf("  function buildDetails(",begin);
  assert.ok(begin>=0 && end>begin);
  const handlers={svg};vm.createContext(handlers);
  const labels=source.slice(source.indexOf("  const statusLabel ="),source.indexOf("  let serial ="));
  vm.runInContext(labels+source.slice(begin,end),handlers);
  const calls=[], s={layout:compare.project(before,after),groups:[],select:(...args)=>calls.push(args)};
  const draw=(kind,value)=>{const board=svg("svg");handlers[kind](s,board,value,"arrow");return board.children[0];};
  return {s,calls,edge:value=>draw("drawEdge",value),node:value=>draw("drawNode",value)};
}

function assertLabelHierarchy(h) {
  const edge=h.s.layout.before.edges.find(item=>item.id==="T-KEEP"), painted=h.edge(edge);
  assert.equal(painted.children.find(node=>node.attrs.class==="compare-edge-label").textContent,"Submit");
  assert.equal(painted.children.filter(node=>node.attrs.class==="compare-status-label").length,0,"unchanged edge has no redundant visible status");
  assert.equal(painted.attrs["data-status"],"unchanged");assert.match(painted.attrs["aria-label"],/= Unchanged, Submit, Owner, Draft to Review/);
  assert.equal(painted.attrs["data-eija-id"],"transition:T-KEEP");
  const initial=h.node(h.s.layout.before.nodes.find(item=>item.id==="Draft"));
  const marker=initial.children.find(node=>String(node.attrs.class).includes("compare-initial-label"));
  assert.equal(marker?.textContent,"● Initial","unchanged initial state must retain its visible start marker");
  assert.match(initial.attrs["aria-label"],/Unchanged, initial state/);
  const ordinary=h.node(h.s.layout.before.nodes.find(item=>item.id==="Review"));
  assert.ok(!ordinary.children.some(node=>String(node.attrs.class).includes("compare-status-label")));
  assert.equal(ordinary.children.find(node=>node.attrs.class==="compare-state-label").textContent,"Review");
  for(const [side,id,label] of [["after","T-CHANGE","◇ Modified"],["after","T-ADD","+ Added"],["before","T-REMOVE","− Removed"]]) {
    const value=h.s.layout[side].edges.find(item=>item.id===id), group=h.edge(value);
    assert.equal(group.children.find(node=>node.attrs.class==="compare-status-label")?.textContent,label,"changed membership and fields keep a visible status");
    assert.equal(group.children.find(node=>node.attrs.class==="compare-edge-label").textContent,value.action);
  }
  for(const [side,id,label] of [["after","New","+ Added"],["before","Old","− Removed"]]) {
    const group=h.node(h.s.layout[side].nodes.find(item=>item.id===id));
    assert.equal(group.children.find(node=>node.attrs.class==="compare-status-label")?.textContent,label);
  }
  const nextInitial=h.node({...h.s.layout.after.nodes.find(item=>item.id==="New"),initial:true});
  assert.equal(nextInitial.children.find(node=>String(node.attrs.class).includes("compare-initial-label"))?.textContent,"● Initial · + Added");
  return painted;
}

test("actual painted hierarchy retains names, changes, initial markers and accessible unchanged classification", () => {
  const h=graphLabelHarness(), group=assertLabelHierarchy(h), original=JSON.stringify(h.s.layout);
  group.listeners.click();let prevented=0,stopped=0;
  for(const key of ["Enter"," "])group.listeners.keydown({key,preventDefault:()=>prevented++,stopPropagation:()=>stopped++});
  group.listeners.keydown({key:"ArrowRight"});
  assert.equal(h.calls.length,3);assert.equal(prevented,2);assert.equal(stopped,2);
  assert.ok(h.calls.every(([item,frame])=>item.key==="transition:T-KEEP" && frame===false));
  assert.equal(JSON.stringify(h.s.layout),original,"selection must not rewrite either projection");
});

test("label hierarchy oracle detects missing Initial and changed markers", () => {
  for(const [from,to] of [["node.initial?\"● Initial\":\"\"","\"\""],["if(edge.status !== \"unchanged\")group.append","if(false)group.append"]]) {
    const h=graphLabelHarness(source=>{assert.ok(source.includes(from),"mutant must modify a real renderer path");return source.replace(from,to);});
    assert.throws(()=>assertLabelHierarchy(h),assert.AssertionError);
  }
});

function captureLabelReservations(operation) {
  const actualLayout=globalThis.dagre.layout, actualProjection=globalThis.EijaCanvas.projectLayout;
  const graphLabels=[], requests=[];
  globalThis.dagre.layout=graph=>{graphLabels.push(graph.edges().map(edge=>({...graph.edge(edge)})));return actualLayout(graph);};
  globalThis.EijaCanvas.projectLayout=(model,saved,direction,viewport,boxes)=>{
    requests.push({model:copy(model),boxes:boxes && new Map([...boxes].map(([id,box])=>[id,{...box}]))});
    return actualProjection(model,saved,direction,viewport,boxes);
  };
  try{return {value:operation(),graphLabels,requests};}
  finally{globalThis.dagre.layout=actualLayout;globalThis.EijaCanvas.projectLayout=actualProjection;}
}

test("Dagre reserves both snapshot actions and the full changed-label block in the shared union", () => {
  const longAction="VerifySavedWithLongExactActionName";
  const a=freeze({states:["A","B","C"],initial_state:"A",transitions:[
    transition("changed","A","B",{action:longAction}),transition("parallel","A","B",{action:"VerifySaved"})]});
  const b=freeze({...a,transitions:[{...a.transitions[0],action:"V",to_state:"C"},a.transitions[1],transition("added","A","B",{action:"X"})]});
  const original=JSON.stringify({a,b});
  for(const [first,last] of [[a,b],[b,a]])for(const direction of ["LR","TB"]) {
    const captured=captureLabelReservations(()=>compare.project(first,last,{direction}));
    const {model,boxes}=captured.requests[0];assert.equal(boxes.size,4,"retargeted before and after retain separate union edges");
    const longer=model.transitions.filter(item=>item.action===longAction);assert.equal(longer.length,2);
    for(const item of longer) {
      assert.ok(boxes.get(item.id).width>=longAction.length*8+8,"both route variants must reserve the longer snapshot label");
      assert.ok(boxes.get(item.id).height>=48,"two painted baselines and text stroke require more than the legacy 24px slot");
    }
    const unchanged=model.transitions.find(item=>item.action==="VerifySaved");assert.equal(boxes.get(unchanged.id).height,24);
    const addedOrRemoved=model.transitions.find(item=>item.action==="X");assert.ok(boxes.get(addedOrRemoved.id).height>=48);
    const caption=first===a?"+ Added":"− Removed";
    assert.ok(boxes.get(addedOrRemoved.id).width>=caption.length*7+8,"short action still reserves its longer visible status caption");
    assert.deepEqual(captured.graphLabels[0].map(({width,height})=>({width,height})),[...boxes.values()],"actual Dagre receives the union label boxes");
    assertSide(captured.value.before,first);assertSide(captured.value.after,last);
    for(const node of captured.value.before.nodes) {
      const match=captured.value.after.nodes.find(item=>item.id===node.id);
      if(match)assert.deepEqual([node.x,node.y],[match.x,match.y]);
    }
  }
  assert.equal(JSON.stringify({a,b}),original);
});

test("optional display metrics preserve legacy defaults and reject invalid sizes before Dagre runs", () => {
  const model=freeze({states:["A","B"],initial_state:"A",transitions:[transition("T","A","B",{action:"Long exact action"})]});
  for(const direction of ["LR","TB"]) {
    const baseline=globalThis.EijaCanvas.projectLayout(model,{},direction);
    assert.deepEqual(globalThis.EijaCanvas.projectLayout(model,{},direction,undefined,new Map()),baseline);
    const defaults=captureLabelReservations(()=>globalThis.EijaCanvas.projectLayout(model,{},direction));
    assert.deepEqual(defaults.graphLabels[0].map(({width,height})=>({width,height})),[{width:136,height:24}]);
    const boxes=new Map([["T",Object.freeze({width:640,height:120})]]), original=JSON.stringify([...boxes]);
    const capture=captureLabelReservations(()=>globalThis.EijaCanvas.projectLayout(model,{},direction,undefined,boxes));
    assert.deepEqual(capture.graphLabels[0].map(({width,height})=>({width,height})),[{width:640,height:120}]);
    const {bounds,routes}=capture.value,{x,y}=routes.T.label;
    assert.ok(bounds.x<=x-320 && bounds.y<=y-60 && bounds.x+bounds.width>=x+320 && bounds.y+bounds.height>=y+60,"Fit bounds contain the supplied label rectangle");
    assert.equal(JSON.stringify([...boxes]),original);
  }
  for(const bad of [0,-1,NaN,Infinity,"48",null,undefined])for(const key of ["width","height"]) {
    const size={width:80,height:48,[key]:bad};let calls=0, actual=globalThis.dagre.layout;
    globalThis.dagre.layout=graph=>{calls++;return actual(graph);};
    try{assert.throws(()=>globalThis.EijaCanvas.geometry(model,{},"TB",new Map([["T",size]])),/finite and positive/);assert.equal(calls,0);}
    finally{globalThis.dagre.layout=actual;}
  }
});
