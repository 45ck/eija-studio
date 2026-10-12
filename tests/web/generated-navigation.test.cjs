"use strict";
// Actual generated controller, isolated DOM/HTTP doubles. Browser checks observe
// its React navigation and real service separately; these are binding controls.
const {test} = require("node:test"), assert = require("node:assert/strict");
const fs = require("node:fs"), path = require("node:path"), vm = require("node:vm");
const source = fs.readFileSync(path.join(__dirname, "../../src/eija_studio/resources/appgen/react-source/controller.js"), "utf8");

function harness() {
  const focused = [], messages = [], writes = [];
  const context = {window: {parent: null, addEventListener() {}}, URL, URLSearchParams,
    location: {hash: "", ancestorOrigins: []}, document: {referrer: "", activeElement: {isConnected: true, focus: () => focused.push("opener")},
      getElementById: id => ({focus: () => focused.push(id)}), querySelector: () => ({focus: () => focused.push("confirm")})},
    requestAnimationFrame: callback => callback(), fetch: async (...args) => {writes.push(args); throw new Error("unexpected HTTP");},
    crypto: {randomUUID: () => "e242d916-73ec-4442-afbb-baf285ff75d8"}};
  context.window.parent = context.window;
  vm.createContext(context); vm.runInContext(source, context);
  const destination = {id: "action:ship", kind: "action", use_case: "Ship", record_required: true, focus: "action-screen"};
  const record = {id: "b".repeat(32), state: "Ready", version: 7};
  context.navigationModel = {schema_version: "eija.navigation.v1", destinations: [destination]};
  context.detail = {record, options: [{action: "Ship", allowed: true, to: "Shipped"}]};
  vm.runInContext("state.app={navigation:navigationModel};state.detail=detail;state.selected=detail.record.id;state.fresh=true;", context);
  return {context, focused, messages, writes, destination, record,
    read: expression => JSON.parse(vm.runInContext(`JSON.stringify(${expression})`, context))};
}

test("navigation uses declared destinations and focuses an existing panel without HTTP or losing selection", () => {
  const h = harness(), selected = h.read("state.selected");
  h.context.navigate({id: "custom-records", kind: "records", focus: "records-title", record_required: false});
  assert.deepEqual(h.focused, ["records-title"]);
  assert.equal(h.read("state.navigationSelected"), "custom-records");
  assert.equal(h.read("state.selected"), selected);
  assert.equal(h.writes.length, 0);
});

test("record destinations cannot open without a selected observed record", () => {
  const h = harness(); vm.runInContext("state.detail=null", h.context);
  h.context.navigate(h.destination);
  assert.equal(h.read("state.action"), null); assert.deepEqual(h.focused, []); assert.equal(h.writes.length, 0);
});

test("missing navigation binding and refused service options cannot open an action", () => {
  for (const broken of ["state.app.navigation.destinations=[]", "state.detail.options[0].allowed=false",
    'state.app.navigation.schema_version="unknown-version"']) {
    const h = harness(); vm.runInContext(broken, h.context);
    h.context.navigate(h.destination);
    assert.equal(h.read("state.action"), null); assert.deepEqual(h.focused, []); assert.equal(h.writes.length, 0);
  }
});

test("checked action navigation opens confirmation from the observed service option and performs no write", () => {
  const h = harness(); h.context.navigate(h.destination);
  assert.equal(h.read("state.action.option.action"), "Ship");
  assert.equal(h.read("state.action.record.version"), 7);
  assert.equal(h.read("state.navigationSelected"), "action:ship");
  assert.deepEqual(h.focused, ["confirm"]); assert.equal(h.writes.length, 0);
  h.context.closeAction(); assert.equal(h.read("state.action"), null); assert.equal(h.focused.at(-1), "opener");
});

test("a typed attribute named title stays distinct from the record display title", () => {
  const h = harness();
  h.context.updateRecordTitle("Friday multiplayer lobby");
  h.context.updateRecordField("title", "Friends only");
  assert.equal(h.read("state.form.title"), "Friday multiplayer lobby");
  assert.equal(h.read("state.form.fields.title"), "Friends only");
  h.context.updateRecordTitle("Saturday multiplayer lobby");
  assert.equal(h.read("state.form.fields.title"), "Friends only");
  assert.equal(h.writes.length, 0);
});
