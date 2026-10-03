"use strict";
// Read-only presentation tests using a tiny DOM recorder, not a browser/human validation claim.
const {test} = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");
const source = require(path.join(__dirname, "../../src/eija_studio/resources/web/source.js"));
class Node {
  constructor(tag) {this.tag = tag; this.children = []; this.dataset = {}; this.events = {}; this.textContent = "";}
  setAttribute(key, value) {this[key] = String(value);}
  append(...items) {this.children.push(...items);}
  replaceChildren(...items) {this.children = items;}
  addEventListener(event, handler) {this.events[event] = handler;}
}
global.document = {createElement: tag => new Node(tag)};
const flatten = root => [root, ...root.children.flatMap(flatten)];
const text = root => flatten(root).map(node => node.textContent).join("\n");
function expand(root) {for (const node of flatten(root)) if (node.tag === "details") {node.open = true; node.events.toggle();}}
function snapshot(extra = {}) {
  return {status:"connected", root:"C:/sample", read_only:true, pack:{id:"sample",digest:"pack-digest"},
    source_hash:"source-digest", graph_hash:"graph-digest", file_hashes:{"src/sample.py":"file-digest"},
    git:{head:"abc123", branch:"main", dirty:true, untracked:"not inspected", worktrees:[{path:"C:/sample",branch:"main",head:"abc123"}], worktree_limit:64},
    coverage:{tracked_files:5,captured_files:3,excluded:{private_filename:2},semantic_complete:false,limitations:["No target execution"]},
    bindings:[{term:"operation",target:"repo://src/sample.py#Operation",resolved:false,digest:null}],
    gaps:[{path:"other.ts",reason:"No behavior extraction"}],
    lint:{verdict:"NOT_RUN",findings:[],verdicts:{"WV-005":"NOT_RUN"},not_run:[{rule:"WV-005",reason:"No accepted binding baseline"}]}, ...extra};
}

test("unavailable connection object is not presented as connected or clean", () => {
  const root = new Node("div");
  source.render(root, {status:"unavailable",root:"C:/missing",reason:"Git metadata unavailable",lint:{verdict:"NOT_RUN",findings:[]}});
  const output = text(root);
  assert.match(output, /Repository unavailable/); assert.match(output, /Git metadata unavailable/);
  assert.match(output, /Source-link checks did not run/); assert.match(output, /NOT_RUN/);
  assert.doesNotMatch(output, /Repository snapshot available|Tracked working tree|Clean/);
  assert.equal(source.state({status:"unavailable"}).connected, false);
});

test("unconfigured repository keeps declared-model use available and does not invent source results", () => {
  const root = new Node("div"); source.render(root, null);
  assert.match(text(root), /Repository not configured/); assert.match(text(root), /declared domain pack/);
  assert.doesNotMatch(text(root), /Resolved|PASS|Repository snapshot available/);
});

test("rendering keeps reported failures, unresolved bindings and hostile source text literal", () => {
  const hostile = '<img src=x onerror="run()">';
  const data = snapshot({lint:{verdict:"FAIL",findings:[{rule:"WV-001",message_id:"link-endpoint-missing",uri:hostile,args:{endpoint:hostile}}],not_run:[]}});
  const before = JSON.stringify(data), root = new Node("div"); source.render(root, data);
  assert.match(text(root), /Lint verdict: FAIL/); assert.match(text(root), /Unresolved/); assert.match(text(root), /Dirty/);
  assert.ok(text(root).includes(hostile)); assert.ok(!flatten(root).some(node => ["img", "script", "iframe"].includes(node.tag)));
  assert.equal(JSON.stringify(data), before);
  assert.ok(!text(root).includes("file-digest"), "file inventory stays collapsed until requested");
  expand(root); assert.ok(text(root).includes("file-digest")); assert.match(text(root), /No behavior extraction/);
});

test("implementation syntax remains separate from the declared journey and unrun conformance", () => {
  const ref = "repo://src/service.py#Review.approve", expression = "principal.require('approve')";
  const facts = {extraction:{status:"PARTIAL",method:"python_ast",executes_target:false,limitations:["No reachability proof"]},
    declared_model:{pack_id:"review",status:"DECLARED_REFERENCE_JOURNEY",scope:"Bounded simulation"},
    conformance:{status:"NOT_RUN",reason:"Implementation equivalence is unproved"},sources:[],gaps:[],
    symbols:[{ref,status:"EXTRACTED",line:10,end_line:20,facts:[{kind:"principal_require_call",line:11,value:expression},{kind:"stage_write_syntax",line:15,value:"'APPROVED'"}]}]};
  const data = snapshot({observed_facts:facts}), before = JSON.stringify(data), root = new Node("div"); source.render(root, data);
  assert.match(text(root), /Conformance: NOT_RUN/); assert.match(text(root), /DECLARED_REFERENCE_JOURNEY/);
  assert.ok(!text(root).includes(expression)); expand(root);
  assert.ok(text(root).includes(expression)); assert.ok(text(root).includes(ref)); assert.ok(text(root).includes("'APPROVED'"));
  assert.match(text(root), /not a proved state transition/); assert.match(text(root), /does not prove that every path enforces authority/);
  assert.equal(JSON.stringify(data), before);
});

test("every repository table exposes a labelled keyboard-focusable scroll region", () => {
  const root=new Node("div");source.render(root,snapshot());expand(root);
  const wrappers=flatten(root).filter(node=>node.className==="source-table-wrap");assert.ok(wrappers.length>3);
  for(const wrapper of wrappers){assert.equal(wrapper.tabIndex,0);assert.equal(wrapper.role,"region");assert.ok(wrapper["aria-label"].length>8);}
});
