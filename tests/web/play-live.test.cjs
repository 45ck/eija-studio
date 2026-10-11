"use strict";
// Actual receiver with isolated DOM/window/model doubles. These checks are not observed browser evidence.
const {test} = require("node:test"), assert = require("node:assert/strict");
const fs = require("node:fs"), path = require("node:path"), vm = require("node:vm");
const sourceCode = fs.readFileSync(path.join(__dirname, "../../src/eija_studio/resources/web/play-live.js"), "utf8");
const protocol = require("../../src/eija_studio/resources/web/play-live.js");
const c4Subject = require("../../src/eija_studio/resources/web/play-c4.js");
const hash = "a".repeat(64), id = "b".repeat(32), nonce = "11111111-1111-4111-8111-111111111111";
const subjectHash = "d".repeat(64), subject = {format:"eija.build-subject.v1",digest:subjectHash,model_hash:hash};
const operationId = "22222222-2222-4222-8222-222222222222", origin = "http://127.0.0.1:43210";
const clone = value => JSON.parse(JSON.stringify(value));
const model = Object.freeze({states:Object.freeze(["Open", "Done"]), transitions:Object.freeze([
  Object.freeze({id:"TR-GO", action:"Go", from_state:"Open", to_state:"Done", role:"Host"})])});
const actors = [{id:"host", role:"Host"}, {id:"member", role:"Member"}];
const vocabulary = {actors, actions:["Go"]};
const envelope = {type:"playide.runtime.v1", nonce, kind:"committed", modelHash:hash, subjectHash, recordId:id,
  version:1, operationId, action:"Go", from:"Open", to:"Done", actorId:"host", effects:["Audit:Done"]};
const context = () => ({source:{}, origin, nonce, modelHash:hash, subjectHash, model, actors, actions:["Go"], versions:new Map(), operations:new Set()});
const event = (context, patch = {}) => ({source:context.source, origin, data:{...envelope, ...patch}});

test("whole actual receiver is valid JavaScript", () => {new vm.Script(sourceCode);});

test("confirmed observation matches one displayed transition without modifying meaning or record tracking", () => {
  const c = context(), before = JSON.stringify(model), entry = protocol.validate(event(c), c);
  assert.equal(entry.transition, "TR-GO"); assert.equal(entry.observedGap, false);
  assert.ok(Object.isFrozen(entry)); assert.ok(Object.isFrozen(entry.effects));
  assert.equal(JSON.stringify(model), before); assert.equal(c.versions.size, 0); assert.equal(c.operations.size, 0);
});

test("source, origin, connection nonce and full current model and build identities are all required", () => {
  const c = context();
  for (const patch of [{source:{}}, {origin:"https://attacker.invalid"}, {origin:"null"}]) {
    assert.equal(protocol.validate({...event(c), ...patch}, c), null);
  }
  for (const patch of [{nonce:operationId}, {nonce:"bad"}, {modelHash:"c".repeat(64)}, {modelHash:hash.slice(0,12)},
    {subjectHash:undefined}, {subjectHash:"c".repeat(64)}, {subjectHash:subjectHash.slice(0,12)},
    {modelHash:{toString:null,valueOf:null}}, {subjectHash:{toString:null,valueOf:null}}]) {
    assert.equal(protocol.validate(event(c, patch), c), null);
  }
});

test("typed bounded schema rejects pending, hostile, missing and privileged-looking message fields", () => {
  const c = context();
  const patches = [{kind:"pending"}, {recordId:"not-a-record"}, {recordId:{toString:() => id}},
    {version:-1}, {version:1.1}, {version:NaN}, {version:Number.MAX_SAFE_INTEGER+1},
    {operationId:"invalid"}, {actorId:"unknown"}, {actorId:"x".repeat(81)}, {action:"x".repeat(61)},
    {action:"Unknown"}, {from:"Missing"}, {to:"Missing"}, {effects:["x".repeat(81)]},
    {effects:Array(65).fill("audit")}, {effects:"audit"}, {approve:true}, {build:true},
    {code:"ROLE_DENIED"}, {type:"playide.runtime.connect.v1"}];
  for (const patch of patches) assert.equal(protocol.validate(event(c, patch), c), null, JSON.stringify(patch));
  for (const data of [null, [], {}, "message"]) assert.equal(protocol.validate({...event(c), data}, c), null);
});

test("commits require matching actor role, direction and one unambiguous current transition", () => {
  const c = context();
  for (const patch of [{actorId:"member"}, {from:"Done"}, {to:"Open"}]) assert.equal(protocol.validate(event(c, patch), c), null);
  assert.equal(protocol.validate(event(c), {...c, model:{...model, transitions:[]}}), null);
  assert.equal(protocol.validate(event(c), {...c, model:{...model, transitions:[...model.transitions, {...model.transitions[0], id:"ALSO"}]}}), null);
});

test("duplicate operations and nonmonotonic versions cannot create another committed observation", () => {
  const c = context();
  assert.equal(protocol.validate(event(c), {...c, operations:new Set([operationId])}), null);
  for (const last of [1,2]) assert.equal(protocol.validate(event(c), {...c, versions:new Map([[id,last]])}), null);
  assert.equal(protocol.validate(event(c, {version:4}), {...c, versions:new Map([[id,2]])}).observedGap, true);
  assert.equal(protocol.validate(event(c, {version:3}), {...c, versions:new Map([[id,2]])}).observedGap, false);
});

test("refusal confirms an attempt, accepts older attempted baseline and never maps movement", () => {
  const c = {...context(), versions:new Map([[id,2]])};
  const refused = {...envelope, kind:"refused", version:0, to:"Open", effects:[], code:"STALE_VERSION"};
  const result = protocol.validate({...event(c), data:refused}, c);
  assert.equal(result.transition, null); assert.equal(result.version, 0); assert.equal(result.observedGap, false);
  for (const patch of [{to:"Done"}, {effects:["audit"]}, {code:undefined}, {code:"<script>"}]) {
    assert.equal(protocol.validate({...event(c), data:{...refused, ...patch}}, c), null);
  }
});

class Element {
  constructor(tag = "div") {
    this.tag = tag; this.children = []; this.dataset = {}; this.attributes = {}; this.listeners = {}; this.hidden = false; this.textContent = ""; this.isConnected = true;
    const classes = new Set();this.classList = {add:name => classes.add(name),remove:name => classes.delete(name),contains:name => classes.has(name)};
  }
  append(...nodes) {for (const node of nodes) {node.parent = this; this.children.push(node);}}
  replaceChildren(...nodes) {this.children = []; this.append(...nodes);}
  remove() {if (this.parent) this.parent.children = this.parent.children.filter(node => node !== this);}
  setAttribute(name,value) {this.attributes[name] = String(value);}
  addEventListener(name,callback) {this.listeners[name] = callback;}
}

function receiver({displayed = model, buildVocabulary = vocabulary, renderedGraph = null, motion = false} = {}) {
  const nodes = new Map(), get = id => {if (!nodes.has(id)) nodes.set(id,new Element()); return nodes.get(id);};
  const listeners = {}, documentListeners = {}, sent = [], timers = new Map(), frames = [], privileged = [], hooks = {redraw:[],tab:[]};
  let built = {url:origin + "/", model:hash, subject, key:"reviewed-view", vocabulary:buildVocabulary}, count = 0;
  const frameSource = {postMessage:(data,target) => sent.push({data:clone(data),target})};
  const frame = get("run-frame"); frame.src = built.url; frame.contentWindow = frameSource;
  const document = {body:{dataset:{ready:"true"}}, getElementById:get, querySelectorAll:() => [],
    createElementNS:(_namespace,tag) => new Element(tag),
    addEventListener:(name,callback) => {documentListeners[name] = callback;}};
  const P = {runningBuild:() => built, model:() => displayed, pack:() => {throw new Error("Base pack must not supply draft trace vocabulary");}, hooks,
    graph:() => renderedGraph, tab:() => "states", follow:() => {},
    el:(tag,text,attributes = {}) => {const node = new Element(tag); node.textContent = text; for (const [key,value] of Object.entries(attributes)) node.setAttribute(key,value); return node;},
    api:() => privileged.push("api"), commit:() => privileged.push("commit"), restore:() => privileged.push("restore"),
    showTab:() => {}, select:() => {}};
  const window = {PlayIDE:P, addEventListener:(name,callback) => {listeners[name] = callback;}};
  const sandbox = {window,document,URL,matchMedia:() => ({matches:!motion}),MutationObserver:class {observe() {}},
    requestAnimationFrame:callback => frames.push(callback),performance:{now:() => 0},
    crypto:{randomUUID:() => `${String(++count).padStart(8,"0")}-1111-4111-8111-111111111111`},
    setTimeout:callback => {const key = ++count; timers.set(key,callback); return key;}, clearTimeout:key => timers.delete(key)};
  vm.createContext(sandbox); vm.runInContext(sourceCode,sandbox);
  const snapshot = () => clone(window.PlayLive.snapshot());
  const send = (patch = {}, overrides = {}) => listeners.message({source:frameSource,origin,
    data:{...envelope,nonce:sent.at(-1).data.nonce,...patch},...overrides});
  return {get,frame,frameSource,sent,snapshot,send,privileged,documentListeners,hooks,
    setBuild:value => {built = value;}, load:() => frame.listeners.load(),
    nextTimer:() => {const [key,callback] = timers.entries().next().value; timers.delete(key);callback();},
    animationFrame:time => frames.shift()(time)};
}

function drawnGraph() {
  const destination = new Element("g"), edgeNode = new Element("g"), pane = new Element("g");
  let offset = 0;
  edgeNode.querySelectorAll = () => [{getTotalLength:() => 100,getPointAtLength:length => ({x:length+offset,y:40})}];
  const edge = {id:"transition:TR-GO",isEdge:() => true}, state = {id:"state:Done",isEdge:() => false};
  const cells = {[edge.id]:edge,[state.id]:state}, shapes = {[edge.id]:{shape:{node:edgeNode}},[state.id]:{shape:{node:destination}}};
  const view = {getState:cell => shapes[cell.id],getOverlayPane:() => pane};
  const graph = {getDataModel:() => ({getCell:id => cells[id],cells}),getView:() => view};
  return {graph,pane,edgeNode,destination,movePath:value => {offset=value;},replaceDestination:() => {
    destination.isConnected = false;const current = new Element("g");shapes[state.id] = {shape:{node:current}};return current;
  }};
}

test("arrival resolves the current destination shape after a canvas reflow during real-outcome animation", () => {
  const drawing = drawnGraph(),h = receiver({renderedGraph:drawing.graph,motion:true}); h.send();
  assert.equal(drawing.pane.children.length,1);assert.equal(drawing.edgeNode.classList.contains("live-edge"),true);
  const current = drawing.replaceDestination();h.animationFrame(800);
  assert.equal(current.classList.contains("live-arrival"),true);
  assert.equal(drawing.destination.classList.contains("live-arrival"),false);
  assert.equal(drawing.pane.children.length,0);assert.deepEqual(h.privileged,[]);
});

test("moving token follows the current rendered edge when responsive reflow changes its coordinates", () => {
  const drawing = drawnGraph(),h = receiver({renderedGraph:drawing.graph,motion:true});h.send();
  drawing.movePath(40);h.animationFrame(350);
  assert.equal(Number(drawing.pane.children[0].attributes.cx),127.5);
  h.animationFrame(800);assert.equal(drawing.destination.classList.contains("live-arrival"),true);
  assert.deepEqual(h.privileged,[]);
});

test("a frame timestamp earlier than the observation starts at the edge origin and still arrives", () => {
  const drawing = drawnGraph(),h = receiver({renderedGraph:drawing.graph,motion:true});h.send();
  // requestAnimationFrame supplies the start time of the frame, which can precede performance.now()
  // captured by an observation callback later in that same frame.
  h.animationFrame(-2);
  assert.equal(Number(drawing.pane.children[0].attributes.cx),0);
  assert.equal(Number(drawing.pane.children[0].attributes.cy),40);
  h.animationFrame(800);
  assert.equal(drawing.destination.classList.contains("live-arrival"),true);
  assert.equal(drawing.pane.children.length,0);assert.deepEqual(h.privileged,[]);
});

test("redraw restores the selected confirmed outcome even while following instead of dropping its arrival marker", () => {
  const drawing = drawnGraph(),h = receiver({renderedGraph:drawing.graph});h.send();
  const current = drawing.replaceDestination();h.hooks.redraw[0]();
  assert.equal(h.snapshot().paused,false);assert.equal(current.classList.contains("live-arrival"),true);
  assert.equal(h.snapshot().entries.length,1);assert.deepEqual(h.privileged,[]);
});

test("receiver uses current exact frame URL and fresh checked model; messages confer no authority", () => {
  const h = receiver();
  assert.equal(h.sent[0].target, origin); assert.equal(h.sent[0].data.modelHash, hash); assert.equal(h.sent[0].data.subjectHash, subjectHash);
  for (const overrides of [{source:{}}, {origin:"https://attacker.invalid"}, {origin:"null"}]) h.send({},overrides);
  h.send({recordId:"wrong"}); h.send({approve:true}); h.send({modelHash:"c".repeat(64)});
  assert.equal(h.snapshot().entries.length, 0); assert.deepEqual(h.privileged, []);
  h.frame.src = origin + "/unexpected"; h.send(); assert.equal(h.snapshot().entries.length, 0);
  h.frame.src = origin + "/"; h.send(); assert.equal(h.snapshot().entries.length, 1);
  h.send(); assert.equal(h.snapshot().entries.length, 1); assert.deepEqual(h.privileged, []);
});

test("pause retains history buttons and inspection; recorded replay cannot submit an HTTP or model write", () => {
  const h = receiver(); h.send();
  const firstButton = h.get("live-steps").children[0];
  h.get("live-pause").listeners.click();
  h.send({operationId:"33333333-3333-4333-8333-333333333333",version:2});
  assert.equal(h.snapshot().cursor, 0); assert.equal(h.get("live-steps").children[0], firstButton);
  assert.match(h.get("live-status").textContent,/1 newer/);
  h.get("live-replay").listeners.click(); assert.match(h.get("live-status").textContent,/Replaying recorded outcomes/);
  h.nextTimer(); h.nextTimer();
  assert.equal(h.snapshot().cursor, 1); assert.equal(h.snapshot().replaying, false);
  assert.deepEqual(h.privileged, []);
});

test("model edits and stopped builds retain labelled earlier observations; rebuild replaces the connection", () => {
  const h = receiver(); h.send(); const oldNonce = h.sent[0].data.nonce;
  h.setBuild(null); h.documentListeners["playide:edit"](); h.send({version:2});
  assert.equal(h.snapshot().fresh, false); assert.equal(h.snapshot().entries.length, 1);
  assert.match(h.get("live-status").textContent,/Earlier build/); assert.equal(h.get("live-replay").disabled,true);
  h.setBuild({url:origin + "/",model:hash,subject,key:"new-view",vocabulary}); h.load();
  assert.notEqual(h.sent.at(-1).data.nonce,oldNonce); assert.equal(h.snapshot().entries.length,0);
  h.send({nonce:oldNonce}); assert.equal(h.snapshot().entries.length,0);
  h.send(); assert.equal(h.snapshot().entries.length,1); assert.deepEqual(h.privileged,[]);
});

test("same workflow with different build contents cannot keep old trace evidence current", () => {
  const h = receiver(); h.send(); const oldNonce = h.sent[0].data.nonce;
  const replacement = {...subject,digest:"e".repeat(64)};
  h.setBuild({url:origin + "/",model:hash,subject:replacement,key:"reviewed-view",vocabulary});
  h.documentListeners["playide:edit"]();
  assert.equal(h.snapshot().fresh,false); assert.match(h.get("live-status").textContent,/Earlier build/);
  h.send({version:2,operationId:numberedOperation(2)}); assert.equal(h.snapshot().entries.length,1);
  h.load(); assert.notEqual(h.sent.at(-1).data.nonce,oldNonce);
  assert.equal(h.sent.at(-1).data.subjectHash,replacement.digest);assert.equal(h.snapshot().entries.length,0);
  h.send(); assert.equal(h.snapshot().entries.length,0);
  h.send({subjectHash:replacement.digest});assert.equal(h.snapshot().entries.length,1);
  assert.deepEqual(h.privileged,[]);
});

test("missing, unknown or internally mismatched build subjects cannot connect a trace", () => {
  for (const candidate of [undefined, {...subject,format:"eija.build-subject.v2"}, {...subject,digest:"short"},
    {...subject,model_hash:"e".repeat(64)}]) {
    const h = receiver();const connected = h.sent.length;
    h.setBuild({url:origin + "/",model:hash,subject:candidate,key:"reviewed-view",vocabulary});h.load();
    assert.equal(h.snapshot().fresh,false);assert.equal(h.sent.length,connected);
  }
});

test("C4 match requires the exact versioned build subject, not a matching workflow alone", () => {
  const running = {model:hash,subject};
  assert.equal(c4Subject.matches(subject,running),true);
  for (const candidate of [null,{model:hash},{model:hash,subject:{...subject,digest:"e".repeat(64)}},
    {model:hash,subject:{...subject,format:"eija.build-subject.v2"}},
    {model:hash,subject:{...subject,model_hash:"e".repeat(64)}},{model:"e".repeat(64),subject}]) {
    assert.equal(c4Subject.matches(subject,candidate),false);
  }
  assert.equal(c4Subject.matches({...subject,digest:"short"},{model:hash,subject:{...subject,digest:"short"}}),false);
});

test("trace vocabulary is typed, bounded, unique, copied and immutable", () => {
  const original = clone(vocabulary), bound = protocol.vocabulary(original);
  assert.ok(Object.isFrozen(bound)); assert.ok(Object.isFrozen(bound.actors)); assert.ok(Object.isFrozen(bound.actors[0]));
  original.actors[0].role = "Changed"; original.actions[0] = "Changed";
  assert.equal(bound.actors[0].role,"Host"); assert.equal(bound.actions[0],"Go");
  for (const value of [null, {}, {actors,actions:"Go"}, {actors,actions:["Go","Go"]},
    {actors:[...actors,actors[0]],actions:["Go"]}, {actors:[{id:"x",role:"Host",active:true}],actions:["Go"]},
    {actors:[{id:"x",role:"x".repeat(61)}],actions:["Go"]}, {actors,actions:["x".repeat(61)]},
    {actors,actions:["Go"],approve:true}, {actors:Array(257).fill(actors[0]),actions:["Go"]}]) {
    assert.equal(protocol.vocabulary(value),null);
  }
});

test("owned draft action and actor use the exact server build vocabulary without borrowing base pack meaning", () => {
  const displayed = {states:["Open","Done"],transitions:[{id:"TR-RELEASE",action:"Release",from_state:"Open",to_state:"Done",role:"GameMaster"}]};
  const h = receiver({displayed,buildVocabulary:{actors:[{id:"game-master-1",role:"GameMaster"}],actions:["Release"]}});
  h.send({action:"Release",actorId:"game-master-1"});
  assert.equal(h.snapshot().entries[0].transition,"TR-RELEASE");
  h.send({action:"Release",actorId:"host",version:2,operationId:"33333333-3333-4333-8333-333333333333"});
  assert.equal(h.snapshot().entries.length,1);
  h.setBuild({url:origin + "/",model:hash,subject,key:"reviewed-view",vocabulary:{actors:[{id:"game-master-1",role:"OtherRole"}],actions:["Release"]}});
  h.send({action:"Release",actorId:"game-master-1",version:2,operationId:"44444444-4444-4444-8444-444444444444"});
  assert.equal(h.snapshot().fresh,false); assert.equal(h.snapshot().entries.length,1);
  assert.deepEqual(h.privileged,[]);
  const missing = receiver({buildVocabulary:null}); assert.equal(missing.sent.length,0);assert.equal(missing.snapshot().fresh,false);
});

const numberedOperation = value => `${value.toString(16).padStart(8,"0")}-2222-4222-8222-222222222222`;
const loop = {states:["Open"],transitions:[{id:"TR-GO",action:"Go",from_state:"Open",to_state:"Open",role:"Host"}]};

test("operation capacity is persistently visible, separates ignored messages and reconnects with a fresh nonce", () => {
  const h = receiver({displayed:loop});
  h.send({to:"Open",recordId:"bad"}); assert.equal(h.snapshot().ignored,1); assert.equal(h.snapshot().capacity,"");
  for (let index=1;index<=512;index+=1) h.send({to:"Open",version:index,operationId:numberedOperation(index)});
  assert.equal(h.snapshot().entries.length,128); assert.equal(h.snapshot().entries.at(-1).version,512);
  assert.equal(h.snapshot().capacity,"operations"); assert.equal(h.snapshot().ignored,1);
  assert.match(h.get("live-status").textContent,/Recording paused/);
  assert.equal(h.get("live-recording").hidden,false);assert.match(h.get("live-recording").textContent,/Later outcomes are not observed/);
  h.send({to:"Open",version:513,operationId:numberedOperation(513)});
  assert.equal(h.snapshot().entries.at(-1).version,512); assert.equal(h.snapshot().ignored,1);
  h.send({}, {data:{type:"playide.runtime.ready.v1",modelHash:hash,subjectHash}});
  assert.equal(h.snapshot().capacity,"operations"); assert.equal(h.snapshot().entries.length,128);
  h.get("live-replay").listeners.click(); assert.equal(h.get("live-recording").hidden,false);
  const oldNonce = h.sent.at(-1).data.nonce;
  h.get("live-reconnect").listeners.click();
  assert.notEqual(h.sent.at(-1).data.nonce,oldNonce); assert.equal(h.snapshot().capacity,"");
  assert.equal(h.snapshot().entries.length,0);assert.equal(h.get("live-recording").hidden,true);
  h.send({to:"Open",version:514,operationId:numberedOperation(514),nonce:oldNonce});assert.equal(h.snapshot().entries.length,0);
  h.send({to:"Open",version:514,operationId:numberedOperation(514)}); assert.equal(h.snapshot().entries.length,1);
  assert.deepEqual(h.privileged,[]);
});

test("record capacity reports a gap when a new record cannot be tracked without allocating unbounded state", () => {
  const h = receiver();
  for (let index=1;index<=256;index+=1) h.send({recordId:index.toString(16).padStart(32,"0"),operationId:numberedOperation(index)});
  assert.equal(h.snapshot().capacity,"");
  h.send({recordId:(257).toString(16).padStart(32,"0"),operationId:numberedOperation(257)});
  assert.equal(h.snapshot().capacity,"records"); assert.equal(h.snapshot().entries.length,128);
  assert.equal(h.snapshot().ignored,0); assert.match(h.get("live-recording").textContent,/Later outcomes are not observed/);
  const last = h.snapshot().entries.at(-1).operationId;
  h.send({recordId:(256).toString(16).padStart(32,"0"),version:2,operationId:numberedOperation(258)});
  assert.equal(h.snapshot().entries.at(-1).operationId,last);assert.equal(h.snapshot().ignored,0);
  assert.deepEqual(h.privileged,[]);
});
