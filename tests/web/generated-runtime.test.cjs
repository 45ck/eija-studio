"use strict";
// Actual generated sender/orchestration with isolated HTTP/window doubles, not observed browser evidence.
const {test} = require("node:test"), assert = require("node:assert/strict");
const fs = require("node:fs"), path = require("node:path"), vm = require("node:vm");
const source = fs.readFileSync(path.join(__dirname, "../../src/eija_studio/resources/appgen/web/app.js.tmpl"), "utf8");
const hash = "a".repeat(64), id = "b".repeat(32), nonce = "5fac2043-63c6-4e1a-866e-ddcd15e0a700";
const subjectHash = "d".repeat(64), subject = {format:"eija.build-subject.v1",digest:subjectHash,model_hash:hash};
const operationId = "e242d916-73ec-4442-afbb-baf285ff75d8";
const origin = "http://127.0.0.1:8000";
const clone = value => JSON.parse(JSON.stringify(value));

function fragment(begin, end) {
  const first = source.indexOf(begin), last = source.indexOf(end, first);
  assert.ok(first >= 0 && last > first, `Missing actual source section ${begin}`);
  return source.slice(first, last);
}

function harness({standalone = false, ancestor = origin, referrer = ""} = {}) {
  const messages = [], requests = [], listeners = {}, outcomes = [];
  const parent = {postMessage:(message, targetOrigin) => messages.push({message:clone(message), targetOrigin})};
  const window = {parent, addEventListener:(name, callback) => {listeners[name] = callback;}};
  if (standalone) window.parent = window;
  const context = {window, URL, location:{ancestorOrigins:ancestor ? [ancestor] : []},
    document:{referrer, getElementById:() => ({focus(){}})}, crypto:{randomUUID:() => operationId},
    setWriting:busy => vm.runInContext(`state.writing=${busy}`, context),
    refreshSafely:async () => true, say:(text, kind) => outcomes.push({text, kind}), refusal:error => error.code,
    fetch:async (url, options = {}) => {
      requests.push({url, options});
      return context.response;
    }};
  vm.createContext(context);
  vm.runInContext(source.slice(0, source.indexOf("// Layout only:")), context);
  vm.runInContext(fragment("async function api(", "function refusal("), context);
  vm.runInContext(fragment("async function act(", "async function start("), context);
  vm.runInContext(`state.app={model_hash:${JSON.stringify(hash)},subject:${JSON.stringify(subject)}};state.actor="customer-a";state.selected=${JSON.stringify(id)};state.fresh=true;`, context);
  const record = {id, model_hash:hash, version:0, state:"Requested", current_model:true,
    title:"PRIVATE TITLE", fields:{secret:"PRIVATE FIELD"}};
  const receipt = {duplicate:false, committed:true, record:{...record, state:"Withdrawn", version:1},
    effects:["Audit:RequestWithdrawn"]};
  context.response = {ok:true, status:200, json:async () => receipt};
  return {context, messages, requests, record, receipt, outcomes,
    read:expression => vm.runInContext(expression, context),
    connect:(data = {}, overrides = {}) => listeners.message({source:parent, origin,
      data:{type:"playide.runtime.connect.v1", modelHash:hash, subjectHash, nonce, ...data}, ...overrides}),
    attempt:() => context.runtimeAttempt("Withdraw", record, operationId),
    act:() => context.act("Withdraw", record)};
}

test("whole generated template is valid JavaScript", () => {new vm.Script(source);});

test("handshake requires exact immediate parent, origin, model, build subject and bounded nonce", () => {
  const h = harness();
  h.context.runtimeReady();
  assert.deepEqual(h.messages, [{message:{type:"playide.runtime.ready.v1", modelHash:hash, subjectHash}, targetOrigin:origin}]);
  h.messages.length = 0;
  for (const [data, overrides] of [[{}, {source:{}}], [{}, {origin:"https://other.example"}],
    [{modelHash:"c".repeat(64)}, {}], [{subjectHash:"c".repeat(64)}, {}], [{subjectHash:undefined}, {}],
    [{nonce:"bad"}, {}], [{type:"other"}, {}], [{authority:"owner"}, {}]]) {
    h.connect(data, overrides);
    assert.equal(h.attempt(), null);
  }
  h.connect();
  assert.ok(h.attempt());
});

test("standalone, opaque or missing parent origins remain silent", async () => {
  for (const options of [{standalone:true}, {ancestor:"null"}, {ancestor:""}]) {
    const h = harness(options);
    h.context.runtimeReady();h.connect();
    await h.act();
    assert.equal(h.messages.length, 0);
    assert.equal(h.requests.length, 1); // no parent dependency for ordinary app writes
  }
});

test("legacy, unknown or mismatched build subjects leave ordinary app actions available without tracing", async () => {
  for (const expression of ["delete state.app.subject", 'state.app.subject.format="eija.build-subject.v2"',
    'state.app.subject.digest="short"', 'state.app.subject.model_hash="e".repeat(64)']) {
    const h = harness();h.read(expression);h.context.runtimeReady();h.connect();await h.act();
    assert.equal(h.messages.length,0);assert.equal(h.requests.length,1);
  }
});

test("no-referrer uses ancestor origin; supported fallback never broadcasts", () => {
  for (const options of [{referrer:""}, {ancestor:"", referrer:origin + "/private/path?token=never-send"}]) {
    const h = harness(options);h.context.runtimeReady();
    assert.equal(h.messages[0].targetOrigin, origin);
    assert.equal(JSON.stringify(h.messages).includes("private"), false);
  }
});

test("actual HTTP receipt publishes one minimal confirmed movement after completion", async () => {
  const h = harness();h.connect();
  let release, entered;
  const responsePending = new Promise(resolve => {entered = resolve;});
  h.context.response.json = () => new Promise(resolve => {release = resolve;entered();});
  const pending = h.act();
  await responsePending;
  assert.equal(h.messages.length, 0); // neither click nor pending POST is execution evidence
  release(h.receipt);await pending;
  assert.equal(h.requests.length, 1);
  assert.equal(JSON.parse(h.requests[0].options.body).operation_id, operationId);
  assert.deepEqual(h.messages, [{targetOrigin:origin, message:{type:"playide.runtime.v1", nonce,
    modelHash:hash, subjectHash, recordId:id, operationId, action:"Withdraw", from:"Requested", to:"Withdrawn",
    actorId:"customer-a", version:1, kind:"committed", effects:["Audit:RequestWithdrawn"]}}]);
  assert.equal(JSON.stringify(h.messages).includes("PRIVATE"), false);
});

test("coded HTTP refusal reports attempted baseline and no committed movement", async () => {
  const h = harness();h.connect();
  h.context.response = {ok:false, status:409, json:async () => ({code:"STALE_VERSION", message:"Instance changed"})};
  await h.act();
  assert.deepEqual(h.messages[0], {targetOrigin:origin, message:{type:"playide.runtime.v1", nonce,
    modelHash:hash, subjectHash, recordId:id, operationId, action:"Withdraw", from:"Requested", to:"Requested",
    actorId:"customer-a", version:0, kind:"refused", effects:[], code:"STALE_VERSION"}});
});

test("duplicate, malformed or mismatched success cannot produce a runtime movement", async () => {
  const variants = [
    value => ({...value, duplicate:true, committed:false}), value => ({...value, committed:false}),
    value => ({...value, record:{...value.record, id:"d".repeat(32)}}),
    value => ({...value, record:{...value.record, model_hash:"d".repeat(64)}}),
    value => ({...value, record:{...value.record, current_model:false}}),
    value => ({...value, record:{...value.record, version:4}}),
    value => ({...value, effects:"Audit:RequestWithdrawn"}),
    value => ({...value, effects:["x".repeat(81)]})
  ];
  for (const change of variants) {
    const h = harness();h.connect();
    h.context.response.json = async () => change(h.receipt);
    await h.act();
    assert.equal(h.messages.length, 0);
  }
});

test("network, uncoded, malformed or 5xx failures are unconfirmed rather than domain refusals", async () => {
  for (const [status, body] of [[500, {code:"STALE_VERSION"}], [409, {}], [409, {code:"unsafe error text"}]]) {
    const h = harness();h.connect();
    h.context.response = {ok:false, status, json:async () => body};
    await h.act();assert.equal(h.messages.length, 0);
  }
  const h = harness();h.connect();h.context.fetch = async () => {throw new Error("Network failed");};
  await h.act();assert.equal(h.messages.length, 0);
});

test("delayed responses cannot target a new model, view, actor, record or handshake", async () => {
  const changes = [h => h.read("state.read++"), h => h.read('state.app.model_hash="c".repeat(64)'),
    h => h.read('state.app.subject.digest="c".repeat(64)'),
    h => h.read('state.actor="another-actor"'), h => h.read('state.selected="d".repeat(32)'),
    h => h.connect({nonce:"26a2d59e-f2fd-4c09-a395-c9a7a32b5d37"})];
  for (const change of changes) {
    const h = harness();h.connect();let release, entered;
    const responsePending = new Promise(resolve => {entered = resolve;});
    h.context.response.json = () => new Promise(resolve => {release = resolve;entered();});
    const pending = h.act();await responsePending;
    change(h);release(h.receipt);await pending;
    assert.equal(h.messages.length, 0);
  }
});

test("repeated same handshake keeps an in-flight request bound; stale-read/write guards remain", async () => {
  const h = harness();h.connect();const attempt = h.attempt();h.connect();
  h.context.runtimeOutcome(attempt, h.receipt);
  assert.equal(h.messages.length, 1);
  for (const guard of ["state.fresh=false", "state.fresh=true;state.writing=true"]) {
    h.read(guard);await h.act();assert.equal(h.requests.length, 0);
  }
});
