"use strict";
// Run with node --test tests/web/workbench.test.cjs. No browser or package install.
const {test} = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const crypto = require("node:crypto");
const web = path.join(__dirname, "../../src/eija_studio/resources/web");
globalThis.dagre = require(path.join(web, "vendor/dagre.min.js"));
const canvas = require(path.join(web, "canvas.js"));
const transaction = Object.freeze({kind:"retarget_transition", transition:"TR-MOVE", end:"target", state:"Done"});

test("canvas geometry is deterministic and never changes semantic state or saved layout", () => {
  const model = Object.freeze({states:Object.freeze(["A", "B", "C", "D"])});
  const saved = Object.freeze({B:Object.freeze({x:350,y:120})});
  const before = JSON.stringify({model, saved});
  const first = canvas.positions(model, saved), second = canvas.positions(model, saved);
  assert.deepEqual(first, second);
  assert.equal(new Set(Object.values(first).map(p => `${p.x},${p.y}`)).size, 4);
  assert.equal(JSON.stringify({model,saved}), before);
  assert.equal(first.B.x, 400); assert.equal(first.B.y, 195);
});

test("affordance selection keeps the server verdict and full transaction without recomputing policy", () => {
  const refused = Object.freeze({element:"transition:TR-MOVE", kind:"retarget_target", target:"state:Done", legal:false, codes:["LAW:x"], transaction});
  const allowed = Object.freeze({element:"transition:TR-OTHER", kind:"retarget_target", target:"state:Done", legal:true});
  const found = canvas.entries([refused, allowed], "TR-MOVE", "retarget_target");
  assert.deepEqual(found, [refused]); assert.equal(found[0], refused); assert.equal(found[0].legal, false);
});

function freeze(value) {
  if (value && typeof value === "object") {for (const child of Object.values(value)) freeze(child); Object.freeze(value);}
  return value;
}
const graphFixture = freeze({states:["Open", "Review", "Done", "Unconnected"], transitions:[
  {id:"TR-A", action:"Send", from_state:"Open", to_state:"Review"},
  {id:"TR-B", action:"Return", from_state:"Review", to_state:"Open"},
  {id:"TR-C", action:"Finish", from_state:"Review", to_state:"Done"},
  {id:"TR-D", action:"Retry", from_state:"Review", to_state:"Review"},
  {id:"TR-E", action:"Recheck", from_state:"Open", to_state:"Review"}
]});

test("actual Dagre bundle projects cycles, parallel edges and self-loops without semantic mutation", () => {
  const before = JSON.stringify(graphFixture), first = canvas.geometry(graphFixture), second = canvas.geometry(graphFixture);
  assert.deepEqual(first, second); assert.equal(JSON.stringify(graphFixture), before);
  assert.deepEqual(Object.keys(first.routes).sort(), graphFixture.transitions.map(t => t.id).sort());
  assert.notDeepEqual(first.routes["TR-A"].points, first.routes["TR-E"].points);
  for (const route of Object.values(first.routes)) {
    assert.ok(route.points.length >= 2);
    assert.ok([...route.points, route.label].every(p => Number.isFinite(p.x) && Number.isFinite(p.y)));
  }
  const shuffled = {states:[...graphFixture.states].reverse(), transitions:[...graphFixture.transitions].reverse()};
  assert.deepEqual(canvas.geometry(shuffled), first, "semantic input ordering does not perturb geometry");
});

test("Dagre self-loop endpoints meet the node boundary, including after saved manual placement", () => {
  for (const saved of [{}, {Review:{x:650,y:350}}]) {
    const result = canvas.geometry(graphFixture, saved), node = result.coords.Review, points = result.routes["TR-D"].points;
    for (const point of [points[0], points[points.length - 1]]) {
      const localX = point.x - node.x, localY = point.y - node.y, epsilon = 0.000001;
      assert.ok(localX >= -epsilon && localX <= 190 + epsilon && localY >= -epsilon && localY <= 76 + epsilon);
      assert.ok(Math.min(Math.abs(localX), Math.abs(localX - 190), Math.abs(localY), Math.abs(localY - 76)) < epsilon);
    }
  }
});

test("saved coordinates and dangerous-looking domain labels remain display data only", () => {
  const model = freeze({states:["__proto__", "constructor"],transitions:[{id:"TR-X", action:"<script>", from_state:"__proto__", to_state:"constructor"}]}), saved = freeze({constructor:{x:400,y:250}});
  const before = JSON.stringify({model,saved}), result = canvas.geometry(model,saved);
  assert.ok(Object.hasOwn(result.coords,"__proto__")); assert.equal(result.coords.constructor.x,450); assert.equal(result.coords.constructor.y,325);
  assert.ok(result.routes["TR-X"].points.every(p => Number.isFinite(p.x) && Number.isFinite(p.y)));
  assert.equal(JSON.stringify({model,saved}),before);
});

test("vendored bundle hashes match and layout runs with string code generation forbidden", () => {
  const vendor = path.join(web,"vendor"), record = JSON.parse(fs.readFileSync(path.join(vendor,"dagre.VENDOR.json"),"utf8"));
  for (const [name, expected] of Object.entries(record.files)) {
    const data = fs.readFileSync(path.join(vendor,name)); assert.equal(data.length,expected.bytes);
    assert.equal(crypto.createHash("sha256").update(data).digest("hex"),expected.sha256);
  }
  const bundle = fs.readFileSync(path.join(vendor,"dagre.min.js"),"utf8");
  assert.doesNotMatch(bundle,/\b(?:eval|Function)\s*\(/);
  const blocked = () => {throw new Error("Unexpected network or DOM access");};
  const sandbox = vm.createContext({fetch:blocked, XMLHttpRequest:blocked, document:new Proxy({}, {get:blocked})}, {codeGeneration:{strings:false,wasm:false}});
  vm.runInContext(bundle,sandbox);
  const graph = new sandbox.dagre.graphlib.Graph({multigraph:true}); graph.setGraph({rankdir:"LR"}); graph.setDefaultEdgeLabel(()=>({}));
  graph.setNode("a",{width:190,height:76}); graph.setNode("b",{width:190,height:76}); graph.setEdge("a","b",{}); sandbox.dagre.layout(graph);
  assert.ok(Number.isFinite(graph.node("a").x)); assert.ok(graph.edge("a","b").points.length >= 2);
  assert.equal(sandbox.dagre.version,record.version);
});

test("auto orientation uses the actual Dagre fit and a compact vertical path improves desktop overview", () => {
  const model=freeze({states:["A","B","C","D","E","F","G"],initial_state:"A",transitions:["A","B","C","D","E","F"].map((state,index)=>({id:"T"+index,action:"Advance",from_state:state,to_state:String.fromCharCode(state.charCodeAt(0)+1)}))});
  const viewport={width:1072,height:620},before=JSON.stringify(model),horizontal=canvas.projectLayout(model,{},"LR",viewport),vertical=canvas.projectLayout(model,{},"TB",viewport),automatic=canvas.projectLayout(model,{},"AUTO",viewport);
  const scale=p=>Math.min(viewport.width/p.bounds.width,viewport.height/p.bounds.height);
  assert.ok(scale(vertical)>scale(horizontal));assert.equal(automatic.direction,"TB");assert.deepEqual(automatic,vertical);assert.equal(JSON.stringify(model),before);
  assert.ok(vertical.bounds.height<1000,"compact Dagre ranks avoid excessive vertical whitespace");
});

test("orientation preserves explicit saved coordinates and all routed transition identities", () => {
  const saved=freeze({Review:{x:650,y:350}}),before=JSON.stringify({graphFixture,saved});
  for(const direction of ["LR","TB","AUTO"]){const result=canvas.projectLayout(graphFixture,saved,direction,{width:900,height:500});assert.deepEqual(result.coords.Review,{x:700,y:425});assert.deepEqual(Object.keys(result.routes).sort(),graphFixture.transitions.map(t=>t.id).sort());for(const route of Object.values(result.routes))assert.ok(route.points.every(p=>Number.isFinite(p.x)&&Number.isFinite(p.y)));}
  assert.equal(JSON.stringify({graphFixture,saved}),before);
});

test("Dagre endpoints contact the painted rounded borders in both orientations and after manual placement", () => {
  const excursion=freeze({states:["Draft","Submitted","Approved","Rejected"],transitions:[
    {id:"TR-SUBMIT",action:"Submit",from_state:"Draft",to_state:"Submitted"},
    {id:"TR-APPROVE",action:"Approve",from_state:"Submitted",to_state:"Approved"},
    {id:"TR-REJECT",action:"Reject",from_state:"Submitted",to_state:"Rejected"},
    {id:"TR-REVISE",action:"Revise",from_state:"Rejected",to_state:"Draft"}
  ]});
  for(const model of [excursion,graphFixture])for(const direction of ["LR","TB"])for(const saved of [{},{Submitted:{x:650,y:350},Review:{x:250,y:125}}]){
    const before=JSON.stringify({model,saved}),projection=canvas.geometry(model,saved,direction);
    for(const transition of model.transitions){
      const points=projection.routes[transition.id].points;
      for(const [point,state] of [[points[0],transition.from_state],[points.at(-1),transition.to_state]]){
        const node=projection.coords[state],x=point.x-node.x,y=point.y-node.y;
        assert.ok(x>=-1e-8&&x<=190+1e-8&&y>=-1e-8&&y<=76+1e-8);
        // Independent signed distance to the SVG rounded rectangle (radius 12).
        const qx=Math.abs(x-95)-83,qy=Math.abs(y-38)-26;
        const distance=Math.hypot(Math.max(qx,0),Math.max(qy,0))+Math.min(Math.max(qx,qy),0)-12;
        assert.ok(Math.abs(distance)<1e-8,`${direction} ${transition.id} ${state} endpoint misses painted border by ${distance}`);
      }
    }
    assert.equal(JSON.stringify({model,saved}),before);
  }
});
