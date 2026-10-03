"use strict";
// Isolated DOM controls with the real renderer/Dagre. These do not establish browser paint acceptance.
const {test} = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const web = path.join(__dirname, "../../src/eija_studio/resources/web");
const source = fs.readFileSync(path.join(web, "canvas.js"), "utf8");
const dagre = require(path.join(web, "vendor/dagre.min.js"));

class Element {
  constructor(tag) {
    this.tagName = tag; this.children = []; this.parentNode = null; this.dataset = {};
    this.attrs = {}; this.listeners = new Map(); this.captures = new Set();
    this.classes = new Set(); this.classList = {
      add:(...names) => names.forEach(name => this.classes.add(name)),
      remove:(...names) => names.forEach(name => this.classes.delete(name)),
      contains:name => this.classes.has(name)
    };
  }
  setAttribute(key, value) {
    this.attrs[key] = String(value);
    if (key === "class") this.classes = new Set(String(value).split(/\s+/));
    if (key.startsWith("data-")) this.dataset[key.slice(5).replace(/-([a-z])/g, (_, c) => c.toUpperCase())] = String(value);
  }
  getAttribute(key) {return this.attrs[key] ?? null;}
  append(...nodes) {for (const node of nodes) {node.remove(); node.parentNode = this; this.children.push(node);}}
  replaceChildren(...nodes) {for (const node of this.children) node.parentNode = null; this.children = []; this.append(...nodes);}
  remove() {if (this.parentNode) {this.parentNode.children = this.parentNode.children.filter(node => node !== this); this.parentNode = null;}}
  contains(node) {return node === this || this.children.some(child => child.contains(node));}
  matches(selector) {return selector.startsWith(".") ? this.classes.has(selector.slice(1)) : this.tagName === selector;}
  closest(selector) {return this.matches(selector) ? this : this.parentNode?.closest(selector) || null;}
  querySelectorAll(selector) {return this.children.flatMap(child => [...(child.matches(selector) ? [child] : []), ...child.querySelectorAll(selector)]);}
  querySelector(selector) {return this.querySelectorAll(selector)[0] || null;}
  getBoundingClientRect() {return {width:1000, height:600};}
  getScreenCTM() {return {inverse:() => ({})};}
  addEventListener(type, callback) {if (!this.listeners.has(type)) this.listeners.set(type, new Set()); this.listeners.get(type).add(callback);}
  removeEventListener(type, callback) {this.listeners.get(type)?.delete(callback);}
  dispatch(type, props = {}) {
    const event = {currentTarget:this, pointerId:7, button:0, clientX:240, clientY:180,
      defaultPrevented:false, preventDefault() {this.defaultPrevented = true;}, ...props};
    for (const callback of [...(this.listeners.get(type) || [])]) callback(event);
    return event;
  }
  setPointerCapture(id) {this.captures.add(id);}
  hasPointerCapture(id) {return this.captures.has(id);}
  releasePointerCapture(id) {this.captures.delete(id); this.dispatch("lostpointercapture", {pointerId:id});}
}
function freeze(value) {if (value && typeof value === "object") {Object.values(value).forEach(freeze); Object.freeze(value);} return value;}
const model = freeze({states:["SAVED", "PREVIEW", "VERIFIED", "REFUSED", "UNLISTED"], initial_state:"SAVED",
  transitions:[{id:"TR-VERIFY", action:"Verify", role:"Owner", from_state:"SAVED", to_state:"VERIFIED"}]});
function choice(end, target, legal) {return freeze({element:"transition:TR-VERIFY", kind:"retarget_" + end,
  target:"state:" + target, legal, codes:legal ? [] : ["REFERENCE_AUTHORITY:Approve"],
  transaction:{kind:"retarget_transition", transition:"TR-VERIFY", end, state:target}});}
const legal = choice("source", "PREVIEW", true), refused = choice("source", "REFUSED", false);
const targetChoice = choice("target", "PREVIEW", true);
const affordances = freeze([legal, refused, targetChoice]);

function setup(code = source, includeStatus = true) {
  let hit = null;
  const document = {createElementNS:(_, tag) => new Element(tag), createElement:tag => new Element(tag), elementFromPoint:() => hit};
  const context = {document, dagre, module:{exports:{}}, DOMPoint:class {
    constructor(x, y) {this.x = x; this.y = y;} matrixTransform() {return {x:this.x, y:this.y};}
  }};
  vm.runInNewContext(code, context, {filename:"canvas.js"});
  const canvas = context.module.exports, root = new Element("div");
  const drops = [], notices = [], statuses = [], selections = [];
  const options = {model, layout:{}, pack:"pack", selected:"TR-VERIFY", affordances, editable:true,
    onDrop:entry => drops.push(entry), onNotice:message => notices.push(message), onSelect:id => selections.push(id)};
  if (includeStatus) options.onGestureStatus = message => statuses.push(message);
  canvas.render(root, options);
  const board = root.querySelector(".model-svg");
  const state = name => board.querySelectorAll(".model-node").find(node => node.dataset.state === name);
  const handle = end => board.querySelectorAll(".edit-handle").find(node => node.dataset.end === end);
  const sourceHandle = handle("source");
  const point = (name, type = "pointermove", props = {}, use = sourceHandle) => {
    hit = name instanceof Element ? name : name ? state(name).querySelector("rect") : null;
    return use.dispatch(type, props);
  };
  return {canvas, root, board, options, state, handle, sourceHandle, point, drops, notices, statuses, selections,
    start:(props = {}, end = "source") => handle(end).dispatch("pointerdown", props)};
}
function clean(h) {
  assert.equal(h.board.querySelector(".drag-guide"), null);
  assert.equal(h.board.classList.contains("drag-active"), false);
  for (const node of [...h.board.querySelectorAll(".model-node"), ...h.board.querySelectorAll(".edit-handle")]) {
    for (const cls of ["drag-active", "drop-hover", "drop-legal", "drop-refused", "drop-neutral"]) assert.equal(node.classList.contains(cls), false, cls);
  }
  assert.equal(h.sourceHandle.hasPointerCapture(7), false);
  assert.equal(h.statuses.at(-1), null);
}
function classify(h) {
  h.start();
  assert.equal(h.board.classList.contains("drag-active"), true);
  assert.equal(h.sourceHandle.classList.contains("drag-active"), true);
  assert.equal(h.handle("target").classList.contains("drag-active"), false);
  assert.equal(h.state("PREVIEW").classList.contains("drop-legal"), true);
  assert.equal(h.state("REFUSED").classList.contains("drop-refused"), true);
  for (const name of ["SAVED", "VERIFIED", "UNLISTED"]) {
    assert.equal(h.state(name).classList.contains("drop-neutral"), true);
    assert.equal(h.state(name).classList.contains("drop-refused"), false);
  }
}
test("only explicit server verdicts classify targets; current and unlisted states are neutral", () => classify(setup()));
test("hover emphasizes only the actual target, reports exact source change, and never submits", () => {
  const h = setup(); h.start();
  assert.equal(h.statuses.at(-1), "Move Verify source from SAVED. Drop on a state to preview.");
  h.point("PREVIEW"); assert.equal(h.state("PREVIEW").classList.contains("drop-hover"), true);
  assert.equal(h.statuses.at(-1), "Release to preview Verify source: SAVED → PREVIEW.");
  const count = h.statuses.length; h.point("PREVIEW"); assert.equal(h.statuses.length, count);
  h.point("REFUSED"); assert.equal(h.state("PREVIEW").classList.contains("drop-hover"), false);
  assert.equal(h.statuses.at(-1), "Refused Verify source: SAVED → REFUSED. Release to inspect.");
  h.point("SAVED"); assert.equal(h.statuses.at(-1), "Verify source is already SAVED. No change here.");
  h.point("UNLISTED"); assert.equal(h.statuses.at(-1), "No source change is offered for UNLISTED.");
  h.point(null); assert.equal(h.board.querySelectorAll(".drop-hover").length, 0);
  assert.equal(h.drops.length, 0);
});
for (const [name, expected] of [["PREVIEW", legal], ["REFUSED", refused]]) {
  test(`${name} release forwards the exact server choice once to the existing preview`, () => {
    const h = setup(), before = JSON.stringify({model, affordances}); h.start(); h.point(name);
    assert.equal(h.drops.length, 0); h.point(name, "pointerup");
    assert.equal(h.drops.length, 1); assert.equal(h.drops[0], expected); clean(h);
    h.point(name, "pointerup"); assert.equal(h.drops.length, 1);
    assert.equal(JSON.stringify({model, affordances}), before); assert.deepEqual(h.notices, []);
  });
}
for (const name of ["SAVED", "UNLISTED", null]) {
  test(`release onto ${name} has no offered transaction and remains unchanged`, () => {
    const h = setup(); h.start(); h.point(name, "pointerup"); clean(h);
    assert.equal(h.drops.length, 0); assert.deepEqual(h.notices, ["No different state selected; the model is unchanged."]);
  });
}
test("release resolves the actual target rather than the previous hover", () => {
  const h = setup(); h.start(); h.point("PREVIEW"); h.point("REFUSED", "pointerup");
  assert.deepEqual(h.drops, [refused]); clean(h);
});
for (const event of ["pointercancel", "lostpointercapture"]) {
  test(`${event} restores guidance, removes all gesture listeners and cannot submit later`, () => {
    const h = setup(); h.start(); h.point("PREVIEW"); h.sourceHandle.dispatch(event); clean(h);
    h.point("PREVIEW", "pointerup"); assert.equal(h.drops.length, 0);
    assert.equal(h.statuses.filter(value => value === null).length, 1);
    assert.deepEqual(h.notices, ["Gesture cancelled; the model is unchanged."]);
  });
}
test("rerender cancels an active gesture before removing the old canvas", () => {
  const h = setup(); h.start(); h.point("PREVIEW");
  h.canvas.render(h.root, {...h.options, editable:false}); clean(h);
  assert.equal(h.root.querySelectorAll(".edit-handle").length, 0);
  h.point("PREVIEW", "pointerup"); assert.equal(h.drops.length, 0);
});
test("a foreign pointer cannot move, end, or cancel the initiating gesture", () => {
  const h = setup(); h.start(); const count = h.statuses.length;
  for (const type of ["pointermove", "pointerup", "pointercancel", "lostpointercapture"]) h.point("PREVIEW", type, {pointerId:99});
  assert.equal(h.statuses.length, count); assert.equal(h.drops.length, 0);
  assert.equal(h.sourceHandle.hasPointerCapture(7), true);
  h.point("PREVIEW", "pointerup"); assert.deepEqual(h.drops, [legal]); clean(h);
});
test("a same-labelled target in a different canvas is not an offered drop", () => {
  const h = setup(), other = new Element("g"); other.setAttribute("class", "model-node"); other.setAttribute("data-state", "PREVIEW");
  h.start(); h.point(other); h.point(other, "pointerup");
  assert.equal(h.drops.length, 0); clean(h);
});
test("nonprimary gesture and existing transition keyboard selection do not propose changes", () => {
  const h = setup(); h.start({button:2}); assert.equal(h.board.querySelector(".drag-guide"), null);
  const edge = h.board.querySelector(".model-edge");
  for (const key of ["Enter", " "]) assert.equal(edge.dispatch("keydown", {key}).defaultPrevented, true);
  assert.deepEqual(h.selections, ["TR-VERIFY", "TR-VERIFY"]); assert.equal(h.drops.length, 0); assert.deepEqual(h.statuses, []);
});
test("target handle describes and forwards only the target transaction", () => {
  const h = setup(); h.start({}, "target"); h.point("PREVIEW", "pointermove", {}, h.handle("target"));
  assert.equal(h.statuses.at(-1), "Release to preview Verify target: VERIFIED → PREVIEW.");
  h.point("PREVIEW", "pointerup", {}, h.handle("target")); assert.deepEqual(h.drops, [targetChoice]); clean(h);
});
test("starting a new gesture disposes stale callbacks without cancelling the new gesture", () => {
  const h = setup(); h.start(); h.start({}, "target");
  assert.equal(h.board.querySelectorAll(".drag-guide").length, 1);
  h.point("PREVIEW", "pointerup"); assert.equal(h.drops.length, 0);
  h.point("PREVIEW", "pointerup", {}, h.handle("target")); assert.deepEqual(h.drops, [targetChoice]); clean(h);
});
test("legacy renderer clients can omit the status hook", () => {
  const h = setup(source, false); h.start(); h.point("PREVIEW", "pointerup"); assert.deepEqual(h.drops, [legal]);
});
test("negative control rejects treating absent affordances as kernel refusals", () => {
  const mutant = source.replace('choice?.legal === true ? "drop-legal" : choice?.legal === false ? "drop-refused" : "drop-neutral"', 'choice?.legal === true ? "drop-legal" : "drop-refused"');
  assert.notEqual(mutant, source); assert.throws(() => classify(setup(mutant)), assert.AssertionError);
});
test("negative control catches submitting an edit during hover", () => {
  const mutant = source.replace("hover(targetAt(e));", "hover(targetAt(e)); if (choiceFor(targetAt(e))) onDrop(choiceFor(targetAt(e)));");
  assert.notEqual(mutant, source);
  const h = setup(mutant); h.start(); h.point("PREVIEW");
  assert.throws(() => assert.equal(h.drops.length, 0), assert.AssertionError);
});
