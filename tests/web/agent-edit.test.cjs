"use strict";
// Controller contract checks with actual module and controlled read-only service/owner-preview boundaries.
const {test} = require("node:test"), assert = require("node:assert/strict"), fs = require("node:fs"), path = require("node:path"), vm = require("node:vm");
const source = fs.readFileSync(process.env.EIJA_AGENT_EDIT_MODULE || path.join(__dirname, "../../src/eija_studio/resources/web/agent-edit.js"), "utf8");
const clone = value => JSON.parse(JSON.stringify(value));
const deferred = () => { let resolve, reject; const promise = new Promise((yes, no) => { resolve = yes; reject = no; }); return {promise, resolve, reject}; };
const tx = {kind: "retarget_transition", transition: "TR-VERIFY", end: "source", state: "SAVED"};
const request = "Move Verify source to SAVED";
function model(from = "PREVIEW") { return {id: "workflow", states: ["PREVIEW", "SAVED", "VERIFIED"], initial_state: "PREVIEW", transitions: [{id: "TR-VERIFY", action: "Verify", role: "Owner", from_state: from, to_state: "VERIFIED", guards: ["authorized"], required_effects: ["Audit"], forbidden_effects: []}]}; }
function context() { return {caseId: "case-A", version: 7, stage: "PREVIEW", semanticHash: "before", model: model(), packId: "demo", packDigest: "pack-hash", editable: true, selectedTransition: "TR-VERIFY"}; }
function proposal() { return {scope: "typed-edit-proposal", provider: "offline", model: "typed-edit-fixture-v1", live: false, trust: "UNTRUSTED_PROPOSAL", request, pack: {id: "demo", digest: "pack-hash"}, preview: {scope: "semantic-edit-preview", applied: false, persisted: false, legal: true, codes: [], refs: [], case_id: "case-A", version: 7, stage: "PREVIEW", semantic_hash: "before", current: model(), transaction: clone(tx), candidate: model("SAVED"), candidate_semantic_hash: "after"}}; }
const acknowledgement = () => ({caseId: "case-A", previousVersion: 7, version: 8, semanticHash: "after", transaction: clone(tx)});
class Element {
  constructor(document, tag) { this.ownerDocument = document; this.tag = tag; this.children = []; this.attributes = {}; this.dataset = {}; this.value = ""; this.hidden = false; this.disabled = false; this.open = false; this.ownText = ""; }
  set textContent(value) { this.ownText = String(value); this.children = []; }
  get textContent() { return this.ownText + this.children.map(child => child.textContent).join(" "); }
  set innerHTML(_) { throw Error("Unsafe HTML rendering is not permitted"); }
  append(...items) { items.forEach(item => {item.parentElement = this;}); this.children.push(...items); }
  replaceChildren(...items) { this.children = []; this.ownText = ""; this.append(...items); }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  getClientRects() { for (let item = this; item; item = item.parentElement) if (item.hidden) return []; return [{}]; }
  focus() { if (!this.disabled && this.getClientRects().length) this.ownerDocument.activeElement = this; }
}
function harness() {
  const document = {createElement: tag => new Element(document, tag)}, root = new Element(document, "section"), queued = [], proposals = [], previews = [], routes = [];
  const tab = new Element(document, "section"); document.body = new Element(document, "body"); document.body.append(tab); tab.append(root); document.activeElement = document.body;
  let current = context();
  const sandbox = {document, module: {exports: {}}}; vm.createContext(sandbox); vm.runInContext(source, sandbox);
  const controller = sandbox.module.exports.mount(root, {
    getContext: () => current,
    propose: (text, captured) => { proposals.push({request: text, context: clone(captured)}); assert.ok(queued.length, "unexpected proposal request"); return queued.shift()(); },
    previewChoice: (choice, onCommitted) => { previews.push({choice: clone(choice), onCommitted}); },
    navigate: (kind, transaction) => routes.push({kind, transaction: clone(transaction)})
  });
  const descendants = node => [node, ...node.children.flatMap(descendants)];
  const get = id => descendants(root).find(node => node.id === id);
  return {controller, root, tab, document, get, proposals, previews, routes, queued,
    context: () => current, setContext: value => { current = value; },
    type: (value = request) => { get("agent-edit-request").value = value; get("agent-edit-request").oninput(); },
    submit: () => get("agent-edit-form").onsubmit({preventDefault() {}}),
    preview: () => get("agent-edit-preview").onclick(),
    respond: (value = proposal()) => queued.push(() => Promise.resolve(clone(value))),
    state: () => get("agent-edit-status").dataset.status,
    saved: () => { current = {...current, version: 8, stage: "DRAFT", semanticHash: "after", model: model("SAVED")}; controller.update(); }
  };
}
async function ready(h, value = proposal()) { h.type(); h.respond(value); assert.equal(await h.submit(), true); }

test("natural request produces one explicit offline proposal and no automatic preview or mutation", async () => {
  const h = harness(), original = clone(h.context()); await ready(h);
  assert.equal(h.get("agent-edit-request").placeholder, "Move <action> source to <state> — use exact model names");
  assert.equal(h.proposals.length, 1); assert.deepEqual(h.proposals[0], {request, context: original});
  assert.equal(h.previews.length, 0); assert.deepEqual(h.context(), original); assert.deepEqual(h.routes, []);
  assert.equal(h.state(), "proposed"); assert.equal(h.get("agent-edit-summary").textContent, "Verify · source: PREVIEW → SAVED");
  assert.match(h.root.textContent, /Offline fixture.*synthetic, untrusted proposal.*source stays read only/);
  assert.match(h.get("agent-edit-status").textContent, /only your Apply edit saves/);
  assert.deepEqual(JSON.parse(h.get("agent-edit-json").textContent), proposal());
  assert.equal(h.get("agent-edit-details").open, false); assert.equal(h.get("agent-edit-actions").hidden, true);
});

test("explicit preview delegates exact transaction; close and re-review never claim a saved edit", async () => {
  const h = harness(); await ready(h); await h.preview(); await h.preview();
  assert.equal(h.previews.length, 2); assert.deepEqual(h.previews.map(item => item.choice), [{transaction: tx}, {transaction: tx}]);
  assert.equal(h.state(), "proposed"); assert.equal(h.get("agent-edit-actions").hidden, true);
  assert.doesNotMatch(h.get("agent-edit-status").textContent, /Candidate edit saved/);
});

test("only exact persisted acknowledgement plus authoritative reload enables model Changes and rules links", async () => {
  const h = harness(); await ready(h); await h.preview(); h.saved();
  assert.equal(h.state(), "stale", "reload alone is not an acknowledgement");
  assert.equal(h.previews[0].onCommitted(acknowledgement()), true);
  assert.equal(h.state(), "applied"); assert.match(h.get("agent-edit-status").textContent, /Candidate edit saved · revision 8.*Baseline unchanged/);
  assert.equal(h.get("agent-edit-preview").hidden, true); assert.equal(h.get("agent-edit-actions").hidden, false);
  for (const kind of ["model", "changes", "rules"]) h.get("agent-edit-" + kind).onclick();
  assert.deepEqual(h.routes, ["model", "changes", "rules"].map(kind => ({kind, transaction: tx})));
  assert.equal(h.proposals.length, 1); assert.equal(h.previews.length, 1);
});

test("mismatched acknowledgements and unrefreshed or different candidates cannot appear applied", async () => {
  const mutations = [a => {a.caseId = "case-B";}, a => {a.previousVersion = 6;}, a => {a.version = 9;}, a => {a.semanticHash = "wrong";}, a => {a.transaction.state = "PREVIEW";}];
  for (const mutate of mutations) {
    const h = harness(); await ready(h); await h.preview(); h.saved(); const value = acknowledgement(); mutate(value);
    assert.equal(h.previews[0].onCommitted(value), false); assert.notEqual(h.state(), "applied");
    h.get("agent-edit-model").onclick(); assert.deepEqual(h.routes, []);
  }
  for (const setup of [() => {}, h => {h.saved(); h.context().model = model();}, h => {h.saved(); h.context().semanticHash = "wrong";}, h => {h.saved(); h.context().packDigest = "new-pack";}]) {
    const h = harness(); await ready(h); await h.preview(); setup(h);
    assert.equal(h.previews[0].onCommitted(acknowledgement()), false); assert.notEqual(h.state(), "applied");
  }
});

test("unsupported request failure preserves typed draft, enables deliberate retry and never opens preview", async () => {
  const h = harness(); h.type("Make an arbitrary application");
  h.queued.push(() => Promise.reject(Object.assign(Error("Unsupported request"), {code: "EDIT_PROPOSAL_UNSUPPORTED"})));
  assert.equal(await h.submit(), false); assert.equal(h.state(), "failed");
  assert.equal(h.get("agent-edit-request").value, "Make an arbitrary application"); assert.equal(h.get("agent-edit-propose").disabled, false);
  assert.match(h.get("agent-edit-status").textContent, /EDIT_PROPOSAL_UNSUPPORTED.*No edit was submitted/);
  assert.equal(h.previews.length, 0); await ready(h); assert.equal(h.state(), "proposed");
});

test("an intended illegal edit retains kernel refusal and can only open the existing refusal preview", async () => {
  const h = harness(), value = proposal();
  Object.assign(value.preview, {legal: false, candidate: null, candidate_semantic_hash: null, codes: ["PROTECTED_AUTHORITY"], refs: ["law:owner-only"]});
  await ready(h, value); assert.equal(h.state(), "refused");
  assert.match(h.get("agent-edit-status").textContent, /PROTECTED_AUTHORITY.*No edit was submitted/);
  assert.equal(h.get("agent-edit-preview").textContent, "Inspect refusal"); await h.preview(); h.saved();
  assert.equal(h.previews[0].onCommitted(acknowledgement()), false); assert.notEqual(h.state(), "applied");
  assert.deepEqual(JSON.parse(h.get("agent-edit-json").textContent).preview.refs, ["law:owner-only"]);
});

test("proposal must bind the full request provider pack and captured candidate identity", async () => {
  const mutations = [r => {r.scope = "other";}, r => {r.provider = "live";}, r => {r.model = "other";}, r => {r.live = true;}, r => {r.trust = "TRUSTED";}, r => {r.request = "another request";}, r => {r.pack.id = "other";}, r => {r.pack.digest = "other";}, r => {r.preview.case_id = "case-B";}, r => {r.preview.version = 8;}, r => {r.preview.stage = "APPROVED";}, r => {r.preview.semantic_hash = "other";}, r => {r.preview.current = model("SAVED");}];
  for (const mutate of mutations) { const h = harness(), value = proposal(); mutate(value); h.type(); h.respond(value); assert.equal(await h.submit(), false); assert.equal(h.state(), "failed"); assert.equal(h.get("agent-edit-result").hidden, true); await h.preview(); assert.equal(h.previews.length, 0); }
});

test("malformed or authority-claiming preview cannot enable a preview action", async () => {
  const mutations = [r => {r.preview.scope = "other";}, r => {r.preview.applied = true;}, r => {r.preview.persisted = true;}, r => {r.preview.legal = "yes";}, r => {r.preview.codes = [7];}, r => {r.preview.refs = null;}, r => {r.preview.transaction = {kind: "apply"};}, r => {r.preview.transaction.transition = "missing";}, r => {r.preview.candidate = null;}, r => {r.preview.candidate_semantic_hash = "";}, r => {r.preview.legal = false;}];
  for (const mutate of mutations) { const h = harness(), value = proposal(); mutate(value); h.type(); h.respond(value); assert.equal(await h.submit(), false); assert.equal(h.state(), "failed"); await h.preview(); assert.equal(h.previews.length, 0); }
});

test("duplicate pending submits are local single flight and the captured request cannot mutate", async () => {
  const h = harness(), pending = deferred(); h.type(); h.queued.push(() => pending.promise); const run = h.submit();
  assert.equal(h.state(), "requesting"); assert.equal(h.get("agent-edit-propose").disabled, true); assert.equal(h.get("agent-edit-request").disabled, true);
  await h.submit(); assert.equal(h.proposals.length, 1);
  h.context().selectedTransition = "another-selection"; pending.resolve(proposal()); await run;
  assert.equal(h.state(), "proposed"); assert.equal(h.proposals[0].context.selectedTransition, "TR-VERIFY");
});

test("case switches reject late responses even after returning to the original case", async () => {
  for (const failure of [false, true]) {
    const h = harness(), pending = deferred(); h.type(); h.queued.push(() => pending.promise); const old = h.submit();
    h.setContext({...context(), caseId: "case-B"}); h.controller.update(); assert.equal(h.get("agent-edit-request").value, "");
    h.setContext(context()); h.controller.update(); await ready(h); const visible = h.get("agent-edit-json").textContent;
    if (failure) pending.reject(Error("old failure")); else pending.resolve(proposal()); await old;
    assert.equal(h.state(), "proposed"); assert.equal(h.get("agent-edit-json").textContent, visible); assert.equal(h.previews.length, 0);
  }
});

test("revision semantic model stage pack and read-only changes invalidate a pending or ready proposal", async () => {
  const mutations = [c => {c.version++;}, c => {c.semanticHash = "changed";}, c => {c.model = model("SAVED");}, c => {c.stage = "APPROVED";}, c => {c.packDigest = "changed";}, c => {c.editable = false;}];
  for (const mutate of mutations) for (const pendingCheck of [false, true]) {
    const h = harness(); let run, pending;
    if (pendingCheck) {h.type(); pending = deferred(); h.queued.push(() => pending.promise); run = h.submit();} else await ready(h);
    mutate(h.context()); h.controller.update(); if (pending) {pending.resolve(proposal()); await run;}
    assert.equal(h.state(), "stale"); assert.equal(h.get("agent-edit-request").value, request); await h.preview(); assert.equal(h.previews.length, 0);
  }
});

test("read-only view retains draft; no candidate hides panel and cannot issue a request", async () => {
  const h = harness(); h.type(); h.context().editable = false; h.controller.update(); await h.submit();
  assert.equal(h.get("agent-edit-request").value, request); assert.match(h.get("agent-edit-status").textContent, /read only.*retained/); assert.equal(h.proposals.length, 0);
  h.context().editable = true; h.controller.update(); assert.equal(h.get("agent-edit-propose").disabled, false);
  h.setContext(null); h.controller.update(); assert.equal(h.root.hidden, true); await h.submit(); assert.equal(h.proposals.length, 0);
});

test("editing request or advancing after a saved edit disables old applicability and navigation", async () => {
  const h = harness(); await ready(h); await h.preview(); const old = h.previews[0]; h.type("Allow Agent to Save"); h.saved();
  assert.equal(old.onCommitted(acknowledgement()), false); assert.notEqual(h.state(), "applied");
  const next = harness(); await ready(next); await next.preview(); next.saved(); next.previews[0].onCommitted(acknowledgement());
  next.context().version++; next.controller.update(); assert.equal(next.state(), "stale"); next.get("agent-edit-model").onclick(); assert.deepEqual(next.routes, []);
});

test("role summary is model-derived and provider text is never inserted as HTML", async () => {
  const h = harness(), value = proposal(); value.preview.transaction = {kind: "set_role", transition: "TR-VERIFY", role: "Agent"}; value.preview.candidate.transitions[0].role = "Agent";
  await ready(h, value); assert.equal(h.get("agent-edit-summary").textContent, "Verify · role: Owner → Agent");
  const bad = harness(); bad.type(); bad.queued.push(() => Promise.reject(Error("<img src=x onerror=alert(1)>"))); await bad.submit();
  assert.match(bad.get("agent-edit-status").textContent, /<img/); assert.equal(bad.get("agent-edit-status").children.length, 0);
});

test("destroy invalidates pending proposal callbacks and clears the mounted surface", async () => {
  const h = harness(), pending = deferred(); h.type(); h.queued.push(() => pending.promise); const run = h.submit();
  h.controller.destroy(); pending.resolve(proposal()); await run; assert.equal(h.root.children.length, 0); assert.equal(h.previews.length, 0);
});

test("confirmed saved edit focuses its visible result without adding a normal tab stop", async () => {
  const h = harness(); await ready(h); await h.preview(); h.saved(); h.document.body.focus();
  assert.equal(h.previews[0].onCommitted(acknowledgement()), true);
  assert.equal(h.document.activeElement?.id, "agent-edit-status");
  assert.equal(h.get("agent-edit-status").tabIndex, -1);
  assert.match(h.document.activeElement.textContent, /Candidate edit saved/);
  h.get("agent-edit-model").focus(); h.controller.update(); assert.equal(h.document.activeElement, h.get("agent-edit-model"), "ordinary renders preserve the chosen next action");
});

test("a saved callback does not steal focus when Intent is hidden", async () => {
  const h = harness(); await ready(h); await h.preview(); h.saved(); h.tab.hidden = true;
  const other = new Element(h.document, "button"); h.document.body.append(other); other.focus();
  assert.equal(h.previews[0].onCommitted(acknowledgement()), true);
  assert.equal(h.state(), "applied"); assert.equal(h.document.activeElement, other);
});

test("stale acknowledgements and failed proposals never take success focus", async () => {
  const h = harness(); await ready(h); await h.preview(); h.saved(); h.document.body.focus();
  const stale = acknowledgement(); stale.version++;
  assert.equal(h.previews[0].onCommitted(stale), false); assert.equal(h.document.activeElement, h.document.body);
  const failed = harness(); failed.type(); failed.document.body.focus(); failed.queued.push(() => Promise.reject(Error("Unavailable"))); await failed.submit();
  assert.equal(failed.state(), "failed"); assert.equal(failed.document.activeElement, failed.document.body);
});
