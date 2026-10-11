"use strict";
// Actual activation controller, with an explicit fake API. These component observations do not grant owner
// authority, stamp implementation bytes, or replace the separate browser/server and service boundary checks.
const { test } = require("node:test"), assert = require("node:assert/strict");
const fs = require("node:fs"), path = require("node:path"), vm = require("node:vm");
const source = fs.readFileSync(path.join(__dirname, "../../src/eija_studio/resources/web/play-activation.js"), "utf8");
const playSource = fs.readFileSync(path.join(__dirname, "../../src/eija_studio/resources/web/play.js"), "utf8");
const clone = (x) => JSON.parse(JSON.stringify(x));
const tick = () => new Promise((resolve) => setImmediate(resolve));
function fixture() {
  const nodes = new Map(), calls = [], storage = new Map(), docEvents = new Map();
  class Element {
    constructor(tag = "div", text, attrs = {}) { this.tagName = tag.toUpperCase(); this.textContent = text || ""; this.dataset = {}; this.children = []; this.events = new Map(); this.value = ""; this.checked = false; this.hidden = false; this.open = false; for (const [key, value] of Object.entries(attrs)) this.setAttribute(key, value); }
    setAttribute(key, value) { this[key] = value; }
    append(...children) { this.children.push(...children); }
    replaceChildren(...children) { this.children = children; }
    querySelectorAll(selector) { assert.equal(selector, "input"); return this.children.flatMap((child) => child instanceof Element ? [...(child.tagName === "INPUT" ? [child] : []), ...child.querySelectorAll(selector)] : []); }
    addEventListener(name, handler) { this.events.set(name, handler); }
    showModal() { this.open = true; }
    close() { this.open = false; }
    reportValidity() { return true; }
    async fire(event) { const result = this.events.get(event)?.({ preventDefault() {} }); await result; await tick(); await tick(); }
  }
  const get = (id) => { if (!nodes.has(id)) nodes.set(id, new Element()); return nodes.get(id); };
  let draft = { reasons: [], notes: [], context: "draft-A", originDraftKey: "origin-A", request: { request: "Archive the workflow", pack_id: "demo", expected_pack_digest: "a".repeat(64), expected_baseline_version: 2, expected_baseline_semantic_hash: "b".repeat(64), expected_candidate_semantic_hash: "c".repeat(64), steps: [
    { transaction: { kind: "add_state", state: "Archived" }, author: "you", round: 2, request: "My drawn change" },
    { transaction: { kind: "retarget_transition", transition: "FINISH", end: "target", state: "Archived" }, author: "ai", round: 3, request: "Move finish" },
  ] } };
  draft.shownCandidate = { id: "demo", states: ["Open", "Archived"], initial_state: "Open", transitions: [{ id: "FINISH", action: "Finish", from_state: "Open", to_state: "Archived", role: "Moderator" }] };
  let server = { case: { id: "case-A", version: 0, stage: "PREVIEW", candidate: clone(draft.shownCandidate), selection: { kind: "owner_plan", pack_id: "demo", pack_digest: "a".repeat(64), baseline_semantic_hash: "b".repeat(64), candidate_semantic_hash: "c".repeat(64), steps: clone(draft.request.steps) } },
    packet: { subject_hash: "subject-A", subject: { semantic: "c".repeat(64) }, eligible: false, blockers: ["RUNTIME_EVIDENCE_UNKNOWN"], core_status: "RELEASE_FIXTURE_MATCH", technical_claims: { schema_policy: "PASS", runtime_matrix: "UNKNOWN", bounded_reachability: "NOT_RUN" }, human_understanding: "UNKNOWN", questions: [{ id: "authority", question: "Who may finish?", expected: "Moderator" }], limitations: ["Synthetic fixture actors; no real SSO"] } };
  let failVerification = false, caseId = null, activated = 0, held, readOnly = false;
  const P = { el: (tag, text, attrs) => new Element(tag, text, attrs), reviewing: () => readOnly, activationDraft: () => clone(draft), base: () => ({ transitions: [{ id: "FINISH", action: "Finish" }] }), about: () => ({ case_id: caseId }), status: () => ({ trusted_fixture: true, pack: { id: "demo", digest: "a".repeat(64) }, baseline_semantic_hash: "new-active-baseline" }), inspectChange: () => calls.push(["inspect"]), showEffects: () => calls.push(["effects"]),
    activated: async () => { activated++; draft.context = "active-C"; return { baseline_version: 3 }; },
    api: async (route, body) => {
      calls.push([route, clone(body || null)]);
      if (held && (route.endsWith("/verify") || route.endsWith("/apply"))) await held;
      if (route === "/api/cases/from-plan") return clone(server.case);
      if (route === "/api/cases/case-A") return clone(server);
      if (route === "/api/play/stop") return { stopped: true };
      const verb = route.split("/").at(-1);
      if (verb === "verify" && failVerification) throw Object.assign(Error("Owner source review required"), { code: "SOURCE_REVIEW_REQUIRED" });
      if (verb === "verify") { server.case.version++; server.case.stage = "VERIFIED"; server.packet.eligible = true; server.packet.blockers = []; server.packet.technical_claims.runtime_matrix = "PASS"; }
      if (verb === "approve") { server.case.version++; server.case.stage = "APPROVED"; }
      if (verb === "apply") { server.case.version++; server.case.stage = "APPLIED"; }
      return clone(server.case);
    } };
  const sandbox = { TextEncoder, window: { PlayIDE: P }, document: { getElementById: get, addEventListener: (name, handler) => docEvents.set(name, handler) }, sessionStorage: { setItem: (k, v) => storage.set(k, v), getItem: (k) => storage.get(k) } };
  vm.runInNewContext(source, sandbox);
  return { get, calls, P, async open() { await sandbox.window.PlayActivation.open(); }, transfer: () => get("activation-transfer").fire("click"),
    fields: () => get("activation-questions").querySelectorAll("input"), server: () => server, mutateDraft: (fn) => fn(draft), setVerificationFailure: () => { failVerification = true; server.packet.core_status = "SOURCE_REVIEW_REQUIRED"; server.packet.blockers.push("SOURCE_REVIEW_REQUIRED"); },
    emit: (name) => docEvents.get(name)?.(), setCase: () => { caseId = "case-A"; }, setReadOnly: () => { readOnly = true; }, activated: () => activated,
    hold: () => { let release; held = new Promise((resolve) => { release = resolve; }); return release; } };
}
const decisions = (h) => h.calls.filter(([route]) => /\/(approve|apply)$/.test(route));
test("exact accepted steps, authorship and revision identities reach the server without a second proposal", async () => {
  const h = fixture(); await h.open(); await h.transfer();
  const body = h.calls.find(([route]) => route.endsWith("from-plan"))[1];
  assert.deepEqual(body.steps.map((step) => [step.author, step.round, step.request]), [["you", 2, "My drawn change"], ["ai", 3, "Move finish"]]);
  assert.equal(body.expected_baseline_version, 2); assert.equal(body.expected_candidate_semantic_hash, "c".repeat(64));
  assert.equal(h.fields()[0].value, ""); assert.equal(h.get("activation-acknowledge").checked, false); assert.deepEqual(decisions(h), []);
});
test("verification alone never opens owner review, fills answers, acknowledges or activates", async () => {
  const h = fixture(); await h.open(); await h.transfer(); await h.get("activation-check").fire("click");
  assert.equal(h.get("activation-decision").open, false); assert.equal(h.fields()[0].value, ""); assert.equal(h.get("activation-acknowledge").checked, false);
  assert.deepEqual(decisions(h), []); assert.equal(h.activated(), 0); assert.match(h.get("activation-status").textContent, /Human understanding remains UNKNOWN/);
});
test("source refusal remains visible and disables approval and activation", async () => {
  const h = fixture(); h.setVerificationFailure(); await h.open(); await h.transfer(); await h.get("activation-check").fire("click");
  assert.match(h.get("activation-status").textContent, /SOURCE_REVIEW_REQUIRED/); assert.match(h.get("activation-source").textContent, /SOURCE_REVIEW_REQUIRED/);
  assert.equal(h.get("activation-approve").disabled, true); assert.equal(h.get("activation-apply").disabled, true); assert.deepEqual(decisions(h), []);
});
test("mixed draft refusal preserves edits and never creates a workflow case", async () => {
  const h = fixture(); h.mutateDraft((draft) => { draft.reasons = ["Law changes remain a draft", "Screen changes remain a draft"]; }); await h.open(); await h.transfer();
  assert.equal(h.get("activation-transfer").disabled, true); assert.equal(h.calls.length, 0); assert.deepEqual(decisions(h), []);
});

test("existing cases cannot check or decide while mixed drafts predate opening their review", async () => {
  for (const stage of ["PREVIEW", "VERIFIED", "APPROVED"]) {
    const h = fixture(); h.setCase(); h.server().case.stage = stage; h.server().packet.eligible = true; h.server().packet.blockers = [];
    h.mutateDraft((draft) => { draft.reasons = ["Screen changes remain a draft", "Scenario changes remain a draft", "Law editor contains an untried change"]; });
    const retained = h.P.activationDraft(); await h.open();
    assert.equal(h.get("activation-check").disabled, true, stage); assert.equal(h.get("activation-approve").disabled, true, stage); assert.equal(h.get("activation-apply").disabled, true, stage);
    await h.get("activation-check").fire("click"); h.fields()[0].value = "Moderator"; h.get("activation-acknowledge").checked = true;
    await h.get("activation-form").fire("submit"); await h.get("activation-apply").fire("click");
    assert.equal(h.calls.every(([, body]) => body === null), true, stage); assert.equal(h.activated(), 0, stage);
    assert.match(h.get("activation-status").textContent, /MIXED_DRAFTS/, stage); assert.deepEqual(h.P.activationDraft(), retained, stage);
  }
});

test("oversized UTF-8 provenance is retained intact and a smaller accepted scope can transfer", async () => {
  const h = fixture(); h.mutateDraft((draft) => { for (const step of draft.request.steps) step.request = "界".repeat(6000); });
  const retained = h.P.activationDraft();
  assert.equal(JSON.stringify(retained.request).length < 32768, true); assert.equal(new TextEncoder().encode(JSON.stringify(retained.request)).byteLength > 32768, true);
  await h.open(); assert.equal(h.get("activation-transfer").disabled, true); await h.transfer();
  assert.equal(h.calls.length, 0); assert.match(h.get("activation-status").textContent, /PLAN_TRANSFER_TOO_LARGE/); assert.deepEqual(h.P.activationDraft(), retained);
  h.mutateDraft((draft) => { draft.request.steps.pop(); }); h.emit("playide:plan");
  assert.equal(h.get("activation-transfer").disabled, false); await h.transfer();
  const sent = h.calls.find(([route]) => route.endsWith("from-plan"))[1];
  assert.deepEqual(sent.steps, [retained.request.steps[0]]); assert.equal(sent.steps[0].request.length, 6000);
});

test("named selections show their stored baseline revision and commands without invented authorship", async () => {
  const h = fixture(); h.setCase(); const c = h.server().case;
  c.selection = { kind: "pack_meaning", meaning: "archive" }; c.selected_meaning = "archive"; c.baseline_version = 1; c.baseline = { id: "demo" };
  c.transactions = [{ kind: "add_state", state: "From stored meaning" }]; h.server().pack = { id: "demo" }; h.server().options = { archive: { label: "Archive completed work" } };
  await h.open(); const hashes = h.get("activation-hashes").children.map((node) => node.textContent);
  assert.equal(hashes.includes("demo"), true); assert.equal(hashes.includes("Current pack digest"), true);
  assert.equal(hashes.includes("Revision 1; semantic hash not reported for this selection"), true); assert.equal(hashes.includes("new-active-baseline"), false);
  assert.match(h.get("activation-identity").textContent, /Archive completed work/);
  const steps = h.get("activation-steps").children; assert.equal(steps.length, 1); assert.equal(steps[0].children[0].textContent, "Stored command"); assert.match(steps[0].children[1].textContent, /From stored meaning/);
});

test("later case commands remain visible alongside immutable imported plan provenance", async () => {
  const h = fixture(); h.setCase(); const c = h.server().case;
  c.transactions = [...c.selection.steps.map((step) => step.transaction), { kind: "rename_state", state: "Archived", to: "Closed" }]; await h.open();
  const steps = h.get("activation-steps").children; assert.equal(steps.length, 3); assert.deepEqual(steps.map((step) => step.children[0].textContent), ["You", "AI", "Stored command"]);
  assert.match(steps[2].children[1].textContent, /Archived → Closed/);
});
test("a changed diagram cannot verify, approve or activate the old case", async () => {
  const h = fixture(); await h.open(); await h.transfer(); h.mutateDraft((draft) => { draft.context = "draft-B"; }); h.emit("playide:edit");
  assert.equal(h.get("activation-check").disabled, true); await h.get("activation-check").fire("click");
  assert.match(h.get("activation-status").textContent, /CASE_CONTEXT_CHANGED/); assert.equal(h.calls.some(([route]) => route.endsWith("/verify")), false); assert.deepEqual(decisions(h), []);
});
test("refresh preserves same-subject unsent answers and clears a new subject", async () => {
  const h = fixture(); await h.open(); await h.transfer(); h.fields()[0].value = "unsent owner draft"; h.get("activation-acknowledge").checked = true; h.get("activation-decision").open = true;
  await h.get("activation-refresh").fire("click"); assert.equal(h.fields()[0].value, "unsent owner draft"); assert.equal(h.get("activation-decision").open, true);
  h.server().packet.subject_hash = "subject-B"; await h.get("activation-refresh").fire("click"); assert.equal(h.fields()[0].value, ""); assert.equal(h.get("activation-acknowledge").checked, false); assert.equal(h.get("activation-decision").open, false);
});
test("only deliberate form submission and the separate activate click send owner decisions", async () => {
  const h = fixture(); await h.open(); await h.transfer(); await h.get("activation-check").fire("click");
  h.fields()[0].value = "Moderator"; h.get("activation-acknowledge").checked = true; await h.get("activation-form").fire("submit");
  assert.equal(decisions(h).length, 1); assert.equal(decisions(h)[0][1].subject_hash, "subject-A"); assert.deepEqual(decisions(h)[0][1].answers, { authority: "Moderator" }); assert.equal(h.activated(), 0);
  await h.get("activation-apply").fire("click"); assert.equal(decisions(h).length, 2); assert.equal(h.activated(), 1); assert.equal(h.get("activation-apply").disabled, true);
});
test("pending verification cannot duplicate a request or turn into an owner decision", async () => {
  const h = fixture(); await h.open(); await h.transfer(); const release = h.hold();
  const pending = h.get("activation-check").fire("click"); await tick(); await h.get("activation-check").fire("click");
  assert.equal(h.calls.filter(([route]) => route.endsWith("/verify")).length, 1); assert.deepEqual(decisions(h), []); release(); await pending;
});
test("a read-only stakeholder view can inspect evidence but cannot mutate the case", async () => {
  const h = fixture(); h.setReadOnly(); h.setCase(); await h.open(); await h.transfer(); await h.get("activation-check").fire("click"); await h.get("activation-form").fire("submit");
  assert.equal(h.get("activation-check").disabled, true); assert.equal(h.get("activation-approve").disabled, true);
  assert.equal(h.calls.every(([, body]) => body === null), true); assert.deepEqual(decisions(h), []);
});
test("refreshed evidence for newer behaviour cannot approve the UML still displayed", async () => {
  const h = fixture(); await h.open(); await h.transfer(); await h.get("activation-check").fire("click");
  h.server().case.candidate.transitions[0].role = "Member"; h.server().packet.subject.semantic = "d".repeat(64); h.server().packet.subject_hash = "subject-D";
  await h.get("activation-refresh").fire("click"); assert.equal(h.get("activation-approve").disabled, true); assert.equal(h.get("activation-check").disabled, true);
  await h.get("activation-form").fire("submit"); assert.deepEqual(decisions(h), []); assert.match(h.get("activation-drafts").children[0].textContent, /newer behaviour/);
});
test("activation preserves a newer browser draft created while the committed request waits", async () => {
  const h = fixture(); await h.open(); await h.transfer(); await h.get("activation-check").fire("click"); h.fields()[0].value = "Moderator"; h.get("activation-acknowledge").checked = true; await h.get("activation-form").fire("submit");
  const release = h.hold(), pending = h.get("activation-apply").fire("click"); await tick(); h.mutateDraft((draft) => { draft.context = "newer-unsent-draft"; }); release(); await pending;
  assert.equal(h.server().case.stage, "APPLIED"); assert.equal(h.activated(), 0); assert.match(h.get("activation-status").textContent, /ACTIVATED_WITH_NEWER_DRAFT/);
});

test("activation retains raw editor drafts arriving without a serialized context change", async () => {
  const h = fixture(); await h.open(); await h.transfer(); await h.get("activation-check").fire("click"); h.fields()[0].value = "Moderator"; h.get("activation-acknowledge").checked = true; await h.get("activation-form").fire("submit");
  const originalContext = h.P.activationDraft().context, release = h.hold(), pending = h.get("activation-apply").fire("click"); await tick();
  h.mutateDraft((draft) => { draft.reasons = ["The law editor contains an untried change"]; }); release(); await pending;
  assert.equal(h.server().case.stage, "APPLIED"); assert.equal(h.P.activationDraft().context, originalContext); assert.equal(h.activated(), 0);
  assert.deepEqual(h.P.activationDraft().reasons, ["The law editor contains an untried change"]); assert.match(h.get("activation-status").textContent, /ACTIVATED_WITH_NEWER_DRAFT/);
});

// Execute the actual bridge functions in isolation. This avoids constructing a second refresh algorithm or
// booting the entire graph editor; DOM/network dependencies remain explicit component fixtures.
function bridgeFunction(name, next, globals) {
  const start = playSource.search(new RegExp(`  (?:async )?function ${name}\\(`));
  const end = playSource.indexOf(next, start); assert.ok(start >= 0 && end > start);
  return vm.runInNewContext("(" + playSource.slice(start, end).trim() + "\n)", globals);
}

test("pending law reports and unkept test recorders are part of the actual activation draft guard", () => {
  const nodes = new Map(), get = (id) => { if (!nodes.has(id)) nodes.set(id, { hidden: true, value: "" }); return nodes.get(id); };
  const globals = { $: get, caseId: "case-A", plan: null, screensEdited: false, baseModel: { id: "demo" }, packInfo: { id: "demo" }, activeStatus: { pack: { digest: "a".repeat(64) } }, draftKey: () => "case-A", draft: () => ({}), window: { PlayLaws: { draft: () => null, report: () => null }, PlayTests: { draft: () => null } } };
  const read = bridgeFunction("activationDraft", "  // A committed activation", globals);
  get("laws-editor").hidden = false; get("laws-source").value = "untried draft while initial report waits";
  assert.equal(read().reasons.some((reason) => /authoritative report/.test(reason)), true);
  get("laws-editor").hidden = true; get("tests-recorder").hidden = false;
  assert.equal(read().reasons.some((reason) => /recorder is open/.test(reason)), true);
  get("tests-recorder").hidden = true; assert.equal(read().reasons.length, 0);
});

test("active refresh retains edits arriving during screen loading before any draft retirement", async () => {
  let release, retired = 0; const pendingScreens = new Promise((resolve) => { release = resolve; }), calls = [];
  const draft = { context: "draft-A", reasons: [] }, status = { baseline_semantic_hash: "c".repeat(64), baseline_version: 3, baseline: { id: "demo" }, pack: { digest: "a".repeat(64) } };
  const globals = { activationDraft: () => draft, retire: () => { retired++; }, api: async (route, body) => {
    calls.push([route, body]); if (route === "/api/status") return clone(status);
    if (route === "/api/play/data") return { data: {} }; if (route === "/api/play/roles") return { roles: [] };
    if (route === "/api/play/screens") { await pendingScreens; return { screens: {}, problems: [], accessibility: {}, use_cases: [] }; }
    throw Error("Unexpected route " + route);
  } };
  const activate = bridgeFunction("activated", "  function renderSourceStatus", globals);
  const pending = activate({ packet: { subject: { semantic: status.baseline_semantic_hash } } }, "origin-A", "draft-A"); await tick();
  draft.context = "new-screen-draft"; draft.reasons = ["Screen changes remain a draft"]; release();
  await assert.rejects(pending, (error) => error.code === "ACTIVATED_WITH_NEWER_DRAFT"); assert.equal(retired, 0); assert.equal(draft.context, "new-screen-draft");
  assert.deepEqual(clone(calls.find(([route]) => route === "/api/play/screens")[1]), { case_id: null, model: status.baseline, plan: null, screens: null });
});

test("a pending screen response cannot replace a newer design or an activated model", async () => {
  for (const change of ["design", "model"]) {
    let release; const held = new Promise((resolve) => { release = resolve; }), original = { screens: [{ title: "original" }] };
    const globals = { screens: original, key: "view-A", viewKey() { return globals.key; }, about: () => ({ plan: null }), renderHealth: () => { throw Error("stale response rendered"); }, api: async () => { await held; return { screens: { screens: [{ title: "old response" }] } }; } };
    const load = bridgeFunction("loadScreens", "  function changed", globals), pending = load(null); await tick();
    if (change === "design") globals.screens = { screens: [{ title: "new draft" }] }; else globals.key = "active-C";
    const retained = globals.screens; release(); await pending; assert.strictEqual(globals.screens, retained, change);
  }
});

test("effects across system rejects results arriving for an earlier candidate", async () => {
  const nodes = new Map(), get = (id) => { if (!nodes.has(id)) nodes.set(id, { children: [], replaceChildren(...children) { this.children = children; } }); return nodes.get(id); };
  let release; const held = new Promise((resolve) => { release = resolve; });
  const globals = { $: get, effectsSeq: 0, key: "candidate-A", effectsKey: () => globals.key, plan: null, screensEdited: false, window: {}, about: () => ({ case_id: "case-A", plan: null }), showTab: () => {},
    api: async () => { await held; return {}; }, effectsDiagrams: () => { throw Error("stale diagram result rendered"); }, effectsRequirements: () => { throw Error("stale requirement result rendered"); } };
  const show = bridgeFunction("showEffects", '  $("review-effects-open")', globals), pending = show(); await tick();
  globals.key = "candidate-B"; release(); await pending;
  assert.equal(get("review-effects-content").children.length, 0); assert.match(get("review-effects-status").textContent, /subject changed/);
});

function effectsFixture() {
  const el = (tag, text, attrs = {}) => ({ tag, ...attrs, textContent: text || "", children: [], events: new Map(),
    get firstChild() { return this.children[0]; }, append(...items) { this.children.push(...items); }, replaceChildren(...items) { this.children = items; },
    addEventListener(name, handler) { this.events.set(name, handler); }, setAttribute(name, value) { this[name] = value; }, scrollIntoView() {} });
  const saved = [], preferences = { layout: "connected", emphasized: ["states", "system"] };
  const globals = { el, effectsPreferences: preferences, saveEffectsPreferences: () => saved.push(clone(preferences)), RIPPLE: { states: "State machine", system: "System" }, MARK: {}, showRipple: () => {} };
  const render = bridgeFunction("effectsDiagrams", "  function effectsRequirements", globals), box = el("div");
  const all = (node = box) => [node, ...node.children.flatMap((child) => all(child))];
  return { box, render, all, preferences, saved };
}

test("returned empty effects remain distinct from an unbound view", () => {
  const h = effectsFixture(); h.render(h.box, { before_model: "before-A", model: "candidate-A", diagrams: { states: [] } });
  assert.equal(h.all().some((node) => /before-A → candidate candidate-A/.test(node.textContent)), true);
  const states = h.all().find((node) => node.id === "effects-detail-states"), system = h.all().find((node) => node.id === "effects-detail-system");
  assert.match(states.children[0].textContent, /No effect returned/); assert.match(states.children[1].children[0].textContent, /No effect returned within/);
  assert.match(system.children[0].textContent, /UNKNOWN/); assert.match(system.children[1].children[0].textContent, /not bound/);
});

test("effects preferences change presentation while retaining unknown views and compared report", () => {
  const h = effectsFixture(), report = { before_model: "before-A", model: "candidate-A", diagrams: { states: [{ change: "warning", text: "Check Renew coverage" }] } }, original = clone(report);
  h.render(h.box, report); assert.equal(h.all().filter((node) => node["data-effects-view"]).length, 2);
  assert.equal(h.all().some((node) => node.textContent === "Warning · 1 returned effect(s)"), true);
  const system = h.all().find((node) => node["data-effects-lens"] === "system"); system.checked = false; system.events.get("change")();
  assert.deepEqual(clone(h.preferences.emphasized), ["states"]); assert.equal(h.all().filter((node) => node["data-effects-view"]).length, 2);
  assert.equal(h.all().some((node) => node.textContent === "UNKNOWN"), true);
  h.all().find((node) => node.id === "effects-layout-grouped").events.get("click")();
  assert.equal(h.preferences.layout, "grouped"); assert.equal(h.all().find((node) => node.id === "effects-layout-grouped")["aria-pressed"], "true");
  assert.equal(h.all().find((node) => node.id === "effects-detail-states").open, true); assert.equal(h.all().some((node) => /not causal or runtime edges/.test(node.textContent)), true);
  assert.deepEqual(report, original); assert.deepEqual(h.saved.at(-1), { layout: "grouped", emphasized: ["states"] });
});

test("effects never combine matching candidates compared against different baselines", async () => {
  const nodes = new Map(), get = (id) => { if (!nodes.has(id)) nodes.set(id, { children: [], replaceChildren(...items) { this.children = items; }, append(...items) { this.children.push(...items); }, scrollIntoView() {} }); return nodes.get(id); };
  const globals = { $: get, effectsSeq: 0, effectsKey: () => "subject-A", plan: null, screensEdited: false, window: {}, about: () => ({ case_id: "case-A", plan: null }), showTab: () => {}, el: (tag, text) => ({ textContent: text }),
    api: async (route) => route.endsWith("ripple") ? { model: "candidate-A", before_model: "baseline-A" } : { traceability: { subject: { model_hash: "candidate-A", baseline_model_hash: "baseline-B" } } },
    effectsDiagrams: () => {}, effectsRequirements: () => { throw Error("mismatched comparisons combined"); } };
  await bridgeFunction("showEffects", '  $("review-effects-open")', globals)();
  assert.equal(get("review-effects-content").children.some((node) => /different or unreported baselines/.test(node.textContent)), true);
});
