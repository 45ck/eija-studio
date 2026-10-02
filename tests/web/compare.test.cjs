"use strict";
// Isolated projection/oracle checks. They do not establish browser or human acceptance.
// Staged runs set EIJA_WEB_ROOT and EIJA_COMPARE_MODULE to the reviewed source files.
const {test} = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");
const web = process.env.EIJA_WEB_ROOT || path.join(__dirname, "../../src/eija_studio/resources/web");
globalThis.dagre = require(path.join(web, "vendor/dagre.min.js"));
globalThis.EijaCanvas = require(path.join(web, "canvas.js"));
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
