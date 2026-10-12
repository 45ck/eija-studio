// Exact draft handoff and owner decisions. The server interprets and checks every step; this surface only
// displays returned case/packet identities and sends a decision when the person deliberately submits it.
"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  let P = null, view = null, context = null, shownCandidate = null, originDraftKey = null, busy = false, message = "", problem = false, packetCurrent = false;
  const short = (hash) => hash ? hash.slice(0, 16) : "not available";
  const closed = () => view && ["APPLIED", "DISCARDED"].includes(view.case.stage);
  const readOnly = () => Boolean(P.reviewing && P.reviewing());
  const candidateCoherent = () => !view || JSON.stringify(shownCandidate) === JSON.stringify(view.case.candidate || view.case.baseline);
  const sameContext = () => !view || context === P.activationDraft().context && candidateCoherent();
  const appConflict = () => view?.packet?.app_build?.conformance?.status === "CONFLICT";
  const appEligible = (packet) => {
    if (!packet.subject?.generated_app) return !view?.case?.app_build && (!packet.app_build || packet.app_build.freshness === "UNBOUND"); // historical workflow-only scope only
    const app = packet.app_build;
    return Boolean(app && app.freshness === "CURRENT" && app.binding?.digest === packet.subject.generated_app
      && app.subject?.digest && app.binding.subject?.digest === app.subject.digest && app.conformance?.status === "PASS");
  };
  const eligible = () => Boolean(packetCurrent && view && view.packet && view.packet.eligible
    && view.packet.core_status === "RELEASE_FIXTURE_MATCH" && Array.isArray(view.packet.blockers)
    && !view.packet.blockers.length && appEligible(view.packet));
  const el = (...args) => P.el(...args);
  const at = () => P.activationDraft();
  const path = (suffix = "") => `/api/cases/${encodeURIComponent(view.case.id)}${suffix}`;
  const MAX_TRANSFER_BYTES = 32768; // Match the HTTP streaming body limit, including all provenance.
  function transferIssue(draft) {
    const bytes = new TextEncoder().encode(JSON.stringify(draft.request)).byteLength;
    return bytes > MAX_TRANSFER_BYTES
      ? `The exact plan is ${bytes.toLocaleString()} bytes; transfer accepts at most ${MAX_TRANSFER_BYTES.toLocaleString()} bytes. The whole draft and authorship are retained. Reduce the accepted change scope before transferring; no text will be truncated.`
      : "";
  }
  const RECOVERY = {
    SOURCE_REVIEW_REQUIRED: "The changed implementation needs legitimate owner source review. Preview and diagram inspection remain available; verification and activation stay blocked.",
    STALE_VERSION: "Another change moved this case. Refresh its evidence and inspect the new revision before deciding again.",
    STALE_BASELINE: "Another case changed the active model. Your case is retained; create a new draft against the current active revision.",
    MODEL_CHANGED: "The active model changed. Your draft is retained. Reopen the current model and inspect the draft before transferring it again.",
    CANDIDATE_IDENTITY_MISMATCH: "The server recomputed a different candidate. Refresh the preview; no different meaning will be silently accepted.",
    PACK_IDENTITY_MISMATCH: "The pack's rules, vocabulary or identity changed. This workflow-only transfer cannot carry that change.",
    PACK_CHANGED: "The pack's rules, vocabulary or identity changed. Open the current active model and inspect a new draft; this workflow-only transfer cannot carry pack changes.",
    CANDIDATE_CHANGED: "The server recomputed a different candidate. Open the current model and re-preview the retained draft; no different meaning will be silently accepted.",
    APPROVAL_REQUIRED: "Approve the exact checked subject first. Activation remains a separate deliberate action.",
    MIXED_DRAFTS: "This case activates workflow edits only. Inspect or reset the listed drafts before checking or deciding; those drafts are retained.",
    BUILD_SUBJECT_CHANGED: "The generated app differs from the one you built. Build the candidate again and inspect its new exact scope before transferring.",
    BUILD_IMPLEMENTATION_MISMATCH: "The installed runtime changed after this app was captured. Build and review the candidate again; the previous approval cannot cover a different runtime.",
    ACTIVE_APP_CHANGED: "Activation was reported, but the active app binding differs or is no longer current. Your draft is retained. Open the current active model and inspect its app identity before continuing.",
    APP_CONFORMANCE_CONFLICT: "This review records both failed and passing generated-app checks. Rerunning does not erase the failure. Diagnose and repair the cause, then build and start a new review case; this case remains in history.",
  };

  function mountAppReview() {
    const section = el("section", undefined, { id: "activation-app", "aria-labelledby": "activation-app-title" });
    const heading = el("h3", "The app covered by this review", { id: "activation-app-title" });
    const summary = el("p", "", { id: "activation-app-summary", class: "activation-app-summary" });
    const checks = el("p", "", { id: "activation-app-check", class: "activation-app-check", role: "status" });
    const scopes = el("dl", undefined, { id: "activation-app-scope", class: "activation-app-scope" });
    const limits = el("ul", undefined, { id: "activation-app-limits", class: "muted small" });
    const recovery = el("p", undefined, { id: "activation-app-recovery", class: "activation-warning" });
    recovery.append(el("span", RECOVERY.APP_CONFORMANCE_CONFLICT + " "),
      el("a", "Open the active model to start a new review", { href: "/play" }));
    const details = el("details", undefined, { class: "activation-app-identities" });
    details.append(el("summary", "Exact app and checker identities"), el("dl", undefined, { id: "activation-app-identities", class: "activation-hashes" }));
    const build = el("button", "Build candidate for review", { id: "activation-build", type: "button", class: "primary" });
    build.addEventListener("click", () => { if (busy || readOnly()) return; $("activation").close(); P.buildForReview(); });
    section.append(heading, summary, checks, scopes, limits, recovery, details, build);
    $("activation-evidence").before(section);
  }

  function appReview(draft) {
    const packet = view && view.packet, app = packet && packet.app_build, subject = app && app.subject;
    const bound = Boolean(packet?.subject?.generated_app), pending = !view;
    $("activation-app-recovery").hidden = !appConflict();
    $("activation-build").hidden = !pending;
    $("activation-build").disabled = busy || readOnly() || !draft.request.expected_candidate_semantic_hash;
    $("activation-app-summary").textContent = pending
      ? draft.request.expected_build_digest ? `Candidate build ${short(draft.request.expected_build_digest)} passed its local checks. Transfer it to capture this exact generated app for review.`
        : "Build the candidate first. The server will capture its generated files and declared contracts when you transfer the change."
      : bound ? `This review names one captured generated app: ${short(subject?.digest)}. Approval covers these exact contracts and files under the reported local runtime.`
        : "This historical case covers its workflow only. No generated app is bound to its approval; create a new built candidate to review an exact app.";
    const state = !packetCurrent && view ? "Refresh required" : app?.freshness || "UNBOUND";
    const conformance = app?.conformance;
    $("activation-app-check").textContent = pending ? "Generated-app review evidence is collected after transfer. Building alone does not approve a change."
      : `App binding: ${state} · generated conformance: ${conformance?.status || "NOT_RUN"}${conformance?.cases != null ? ` · ${conformance.cases} cases` : ""}${conformance?.detail ? ". " + conformance.detail : ""}`;
    $("activation-app-check").dataset.current = String(Boolean(packetCurrent && appEligible(packet || {})));
    const scopes = subject ? [["Workflow", "Exact candidate and action rules"], ["Data contract", subject.data_digest ? "Captured record schema; stored user records are not included" : "No data schema declared"],
      ["Screens", "Captured generated screens"], ["Runtime", "Measured installed implementation and generated code"], ["Generated files", `${subject.payload_paths?.length ?? "Reported"} files in the captured payload`]] : [];
    $("activation-app-scope").replaceChildren(...scopes.flatMap(([name, detail]) => [el("dt", name), el("dd", detail)]));
    const identities = subject ? [["App build", subject.digest], ["Review binding", app.binding?.digest], ["Workflow", subject.model_hash], ["Data schema", subject.data_digest],
      ["Screens", subject.screens_digest], ["Templates", subject.templates_digest], ["Runtime", subject.implementation_digest], ["Generated files", subject.generated_files_hash],
      ["Checker", app.binding?.checker?.id], ["Checker digest", app.binding?.checker?.digest]] : [];
    $("activation-app-identities").replaceChildren(...identities.flatMap(([name, value]) => [el("dt", name), el("dd", value || "Not declared")]));
    $("activation-app-limits").replaceChildren(...(app?.limitations || ["Workflow edits only. Screen, schema, policy and vocabulary edits remain drafts.",
      "Stored records, external services and deployment are outside this local approval."]).map((line) => el("li", line)));
  }

  function sourceStatus(packet) {
    const core = packet?.core_status || (!packet && P.status()?.trusted_fixture ? "RELEASE_FIXTURE_MATCH" : "SOURCE_REVIEW_REQUIRED");
    const source = packet?.identity_source || P.status()?.identity_source;
    const synthetic = typeof source === "string" && (source.includes("synthetic") || source === "pytest-harness");
    $("activation-source").textContent = core === "SOURCE_REVIEW_REQUIRED"
      ? "SOURCE_REVIEW_REQUIRED · source changes need legitimate owner review. Model inspection can continue; trusted verification, approval and activation are blocked."
      : core !== "RELEASE_FIXTURE_MATCH" ? `Source status ${core}. Current source review has not been established; refresh before deciding.`
        : synthetic ? `Synthetic owner test identity (${source}). Legitimate owner source review has not been performed; this fixture exercises the review mechanics only.`
          : "Shipped source fixture matches. Byte identity does not establish correctness or independent owner source review.";
    $("activation-source").className = core === "RELEASE_FIXTURE_MATCH" && !synthetic ? "activation-source" : "activation-warning";
  }

  function status(text, bad = false) {
    message = text; problem = bad;
    $("activation-status").textContent = text;
    $("activation-status").className = bad ? "activation-message bad" : "activation-message";
  }

  function identities(draft) {
    const c = view && view.case, s = c && c.selection, p = view && view.packet, ownerPlan = s && s.kind === "owner_plan";
    const activePack = P.status() && P.status().pack;
    const pack = c ? ownerPlan ? s.pack_id : view.pack && view.pack.id || c.baseline && c.baseline.id : draft.request.pack_id;
    const packDigest = c ? ownerPlan ? s.pack_digest : view.pack && view.pack.digest || activePack && activePack.id === pack && activePack.digest : draft.request.expected_pack_digest;
    const baseline = c ? ownerPlan ? s.baseline_semantic_hash : null : draft.request.expected_baseline_semantic_hash;
    const candidate = p && p.subject ? p.subject.semantic : ownerPlan ? s.candidate_semantic_hash : c ? null : draft.request.expected_candidate_semantic_hash;
    const meaningId = c && (s && s.kind === "pack_meaning" ? s.meaning : c.selected_meaning);
    const meaning = meaningId && view.options && view.options[meaningId];
    const rows = [["Pack", pack], [c && !ownerPlan ? "Current pack digest" : "Pack digest", packDigest],
      ["Baseline", baseline || (c ? `Revision ${c.baseline_version}; semantic hash not reported for this selection` : null)],
      ["Candidate", candidate],
      ["Reviewed subject", p && p.subject_hash]];
    $("activation-hashes").replaceChildren();
    for (const [label, value] of rows) $("activation-hashes").append(el("dt", label), el("dd", value || "not yet available"));
    const baselineLabel = baseline ? short(baseline) : c ? `revision ${c.baseline_version}` : "unknown";
    $("activation-identity").textContent = view
      ? `Case ${c.id.slice(0, 10)} · revision ${c.version} · ${c.stage}${meaningId ? " · " + (meaning && meaning.label || meaningId) : ""} · baseline ${baselineLabel} → candidate ${short(candidate)}`
      : `Active revision ${draft.request.expected_baseline_version ?? "unknown"} · baseline ${short(baseline)} → checked draft ${short(candidate)}`;
  }

  function displayedSteps(draft) {
    if (!view) return draft.request.steps;
    const c = view.case, s = c.selection;
    if (s && s.kind === "owner_plan") return [...s.steps, ...(c.transactions || []).slice(s.steps.length).map((transaction) => ({ transaction, author: "stored" }))];
    return (c.transactions || []).map((transaction) => ({ transaction, author: "stored" }));
  }

  function describeStep(step) {
    const tx = step.transaction, baseline = view?.case?.baseline || P.base();
    const before = (baseline.transitions || []).find((item) => item.id === tx.transition), action = before?.action || tx.transition;
    const descriptions = {
      add_state: () => `Add state ${tx.state}`,
      rename_state: () => `Rename state ${tx.state} → ${tx.to}`,
      remove_state: () => `Remove state ${tx.state}`,
      set_initial: () => `Start new records in ${tx.state}`,
      add_transition: () => `${tx.role} may ${tx.action}: ${tx.from_state} → ${tx.to_state}`,
      retarget_transition: () => `${action}: move the ${tx.end === "source" ? "starting" : "destination"} state to ${tx.state}`,
      remove_transition: () => `Remove action ${action}`,
      set_role: () => `${action}: ${before?.role || "previous role"} → ${tx.role}`,
      set_guards: () => `${action}: require ${tx.guards.join(", ")}`,
      set_effects: () => `${action}: record ${tx.required_effects.length ? tx.required_effects.join(", ") : "no required effects"}`,
    };
    return Object.hasOwn(descriptions, tx.kind) ? descriptions[tx.kind]() : tx.kind.replaceAll("_", " ");
  }

  // Questions and acknowledgement belong to one exact subject. Refreshing that same subject preserves unsent
  // answers; a different subject clears them and closes the disclosure. No answer is inferred from the packet.
  function questions(packet) {
    const root = $("activation-decision"), key = view.case.id + ":" + packet.subject_hash;
    const same = Boolean(packet.subject_hash && root.dataset.subject === key);
    const previous = same ? new Map([...$("activation-questions").querySelectorAll("input")].map((n) => [n.name, n.value])) : new Map();
    if (!same) { root.open = false; $("activation-acknowledge").checked = false; }
    root.dataset.subject = key;
    $("activation-questions").replaceChildren();
    for (const q of packet.questions || []) {
      const label = el("label", q.question), input = el("input", undefined, { name: q.id, type: "text", required: "", maxlength: "2000", autocomplete: "off" });
      input.value = previous.get(q.id) || ""; label.append(input); $("activation-questions").append(label);
    }
    $("activation-subject").textContent = `Your answers concern subject ${short(packet.subject_hash)}. Human understanding remains ${packet.human_understanding || "UNKNOWN"}; these questions do not measure it.`;
    $("activation-limits").replaceChildren(...(packet.limitations || []).map((line) => el("li", line)));
  }

  function render() {
    const draft = at(), coherent = sameContext(), workflowOnly = !draft.reasons.length, sizeIssue = transferIssue(draft), c = view && view.case, packet = view && view.packet;
    const stages = ["Draft", "Exact case", "Checked", "Approved", "Active"];
    const current = !c ? 0 : c.stage === "APPLIED" ? 4 : c.stage === "APPROVED" ? 3 : c.stage === "VERIFIED" ? 2 : 1;
    $("activation-journey").replaceChildren(...stages.map((label, n) => el("li", (n < current ? "✓ " : n === current ? "● " : "○ ") + label,
      { class: n < current ? "done" : n === current ? "current" : "", ...(n === current ? { "aria-current": "step" } : {}) })));
    identities(draft);
    appReview(draft);
    const steps = displayedSteps(draft);
    $("activation-steps").replaceChildren(...steps.map((s, n) => {
      const li = el("li");
      li.append(el("span", s.author === "ai" ? "AI" : s.author === "you" ? "You" : "Stored command", { class: "who " + s.author }),
        el("span", `${n + 1}. ${describeStep(s)}`));
      return li;
    }));
    const reasons = [...draft.reasons];
    if (sizeIssue && !P.about().case_id && !(view && coherent)) reasons.push(sizeIssue);
    if (readOnly()) reasons.unshift("This is a read-only stakeholder view. Open the editable local case to transfer, verify or make an owner decision.");
    if (!coherent && !closed()) reasons.unshift(candidateCoherent()
      ? "The diagram or draft moved since this case was transferred. This case is retained, but its checks and decisions cannot act on the changed draft."
      : "This case has newer behaviour than the diagrams on this page. Open this case again to inspect its current UML before verifying or deciding. Your browser draft is retained.");
    $("activation-drafts").replaceChildren(...[...reasons, ...(draft.notes || [])].map((r) => el("li", r)));
    sourceStatus(packet);
    $("activation-transfer").hidden = Boolean(P.about().case_id) || Boolean(view && coherent && !appConflict());
    $("activation-transfer").textContent = appConflict() ? "Start a new exact-app review case" : view ? "Transfer current draft as a new case" : "Transfer exact accepted steps";
    $("activation-transfer").disabled = busy || readOnly() || !workflowOnly || Boolean(sizeIssue) || !draft.request.expected_candidate_semantic_hash;
    $("activation-diff").disabled = busy || !c && !draft.request.expected_candidate_semantic_hash;
    $("activation-effects").disabled = busy;
    $("activation-case-link").hidden = !view;
    if (view) $("activation-case-link").href = `/play?case=${encodeURIComponent(view.case.id)}`;
    $("activation-evidence").hidden = !packet;
    $("activation-decision").hidden = !packet;
    $("activation-apply-tools").hidden = !view || !["APPROVED", "APPLIED"].includes(c.stage);
    if (packet) {
      $("activation-checks").replaceChildren(...Object.entries(packet.technical_claims || {}).map(([kind, value]) => {
        const li = el("li", undefined, { class: "check-result " + String(value).toLowerCase() });
        li.append(el("span", kind.replaceAll("_", " ")), el("strong", value)); return li;
      }));
      $("activation-blockers").replaceChildren(...(packet.blockers || []).map((code) => el("li", `${code}${RECOVERY[code] ? ": " + RECOVERY[code] : ""}`)));
      questions(packet);
    }
    $("activation-check").disabled = busy || readOnly() || !workflowOnly || !view || closed() || !coherent;
    $("activation-refresh").disabled = busy || !view;
    $("activation-approve").disabled = busy || readOnly() || !workflowOnly || !view || closed() || !coherent || !eligible() || c.stage === "APPROVED";
    $("activation-approve").textContent = packet?.subject?.generated_app ? "Approve this exact app revision" : "Approve this workflow revision";
    $("activation-apply").disabled = busy || readOnly() || !workflowOnly || !view || !coherent || !eligible() || c.stage !== "APPROVED";
    $("activation-apply").textContent = c && c.stage === "APPLIED" ? "✓ Revision activated" : "Activate approved revision";
    $("activation-status").textContent = message;
    $("activation-status").className = problem ? "activation-message bad" : "activation-message";
  }

  async function task(work, pending) {
    if (busy) return;
    busy = true; status(pending); render();
    try { await work(); }
    catch (error) {
      const code = error.code || "OUTCOME_UNKNOWN";
      status(`${code}: ${RECOVERY[code] || error.message}. ${code === "OUTCOME_UNKNOWN" ? "The request may have committed. Refresh the case before repeating a decision." : ""}`, true);
    } finally { busy = false; render(); }
  }

  async function refresh() {
    if (!view) return;
    packetCurrent = false;
    const expected = view.case.id, next = await P.api(path());
    if (!next.case || next.case.id !== expected) throw Object.assign(new Error("The refreshed case did not match the case being reviewed."), { code: "CASE_CONTEXT_CHANGED" });
    view = next;
    packetCurrent = true;
  }

  async function transfer() {
    if (readOnly()) return status("Read-only view: open the editable local case before transferring a plan.", true);
    const draft = at();
    if (draft.reasons.length) return status(draft.reasons.join(" "), true);
    const sizeIssue = transferIssue(draft);
    if (sizeIssue) return status(`PLAN_TRANSFER_TOO_LARGE: ${sizeIssue}`, true);
    await task(async () => {
      const created = await P.api("/api/cases/from-plan", draft.request);
      packetCurrent = false;
      view = { case: created, packet: null };
      context = draft.context; shownCandidate = draft.shownCandidate; originDraftKey = draft.originDraftKey;
      try { sessionStorage.setItem("playide.activation.origin:" + created.id, originDraftKey); } catch { /* origin remains in this page */ }
      await refresh();
      status(`✓ Exact accepted steps and authorship transferred to case ${created.id.slice(0, 10)}. No change is active yet.`);
    }, "Transferring the exact accepted steps and checking the candidate identity…");
  }

  async function command(action, extra = {}) {
    if (readOnly()) throw Object.assign(new Error("Open the editable local case before changing its checks or decision."), { code: "READ_ONLY_VIEW" });
    if (at().reasons.length) throw Object.assign(new Error("Non-workflow drafts remain on this page."), { code: "MIXED_DRAFTS" });
    if (!view || !sameContext() || closed()) throw Object.assign(new Error("The shown case or draft changed. Refresh and inspect the exact revision before continuing."), { code: "CASE_CONTEXT_CHANGED" });
    packetCurrent = false;
    await P.api(path("/" + action), { expected_version: view.case.version, ...extra });
    await refresh();
  }

  async function open() {
    if (!P) return;
    if (view) packetCurrent = false;
    render(); $("activation").showModal();
    if (view) {
      await task(async () => { await refresh(); status("Current case and exact app evidence loaded. Inspect the reported scope before deciding."); }, "Refreshing this case and its exact app evidence…");
      return;
    }
    if (!view && P.about().case_id) {
      const opening = at();
      await task(async () => {
        const expected = P.about().case_id, next = await P.api(`/api/cases/${encodeURIComponent(expected)}`);
        if (!next.case || next.case.id !== expected) throw Object.assign(new Error("The returned case is not the one opened on this page."), { code: "CASE_CONTEXT_CHANGED" });
        view = next; packetCurrent = true;
        context = opening.context; shownCandidate = opening.shownCandidate;
        try { originDraftKey = sessionStorage.getItem("playide.activation.origin:" + view.case.id); } catch { /* storage unavailable */ }
        status("Case and review evidence loaded. Inspection, checks and owner decisions remain separate.");
      }, "Loading the exact case and its evidence…");
    }
  }

  function init(bridge) {
    P = bridge;
    mountAppReview();
    $("activation-open").addEventListener("click", open);
    $("activation-close").addEventListener("click", () => $("activation").close());
    $("activation-transfer").addEventListener("click", transfer);
    $("activation-diff").addEventListener("click", () => { $("activation").close(); P.inspectChange(); });
    $("activation-effects").addEventListener("click", () => { if (busy) return; $("activation").close(); P.showEffects(); });
    $("activation-refresh").addEventListener("click", () => task(async () => { await refresh(); status("Current case and evidence loaded. New subject identities clear old unsent answers."); }, "Refreshing the case and evidence…"));
    $("activation-check").addEventListener("click", () => task(async () => {
      await command("verify"); status("✓ Server verification finished for this exact case; inspect generated-app conformance and runtime evidence separately. Human understanding remains UNKNOWN; nothing was approved.");
    }, "Running the server's bounded runtime verification…"));
    $("activation-form").addEventListener("submit", (event) => {
      event.preventDefault();
      if (readOnly() || at().reasons.length || !eligible() || !sameContext() || !$("activation-form").reportValidity()) return;
      const answers = Object.fromEntries([...$("activation-questions").querySelectorAll("input")].map((n) => [n.name, n.value.trim()]));
      const subject = view.packet.subject_hash, acknowledged = $("activation-acknowledge").checked;
      task(async () => { await command("approve", { subject_hash: subject, answers, acknowledge_unknowns: acknowledged, scope: "local-demo" });
        status("✓ Your exact local revision was approved. Activate remains a separate action."); }, "Recording your explicit decision for this exact subject…");
    });
    $("activation-apply").addEventListener("click", () => {
      if (readOnly() || at().reasons.length || !eligible() || !sameContext() || view.case.stage !== "APPROVED") return;
      const applyingContext = at().context;
      task(async () => {
        await command("apply");
        if (view.case.stage !== "APPLIED") throw new Error("The case did not report a committed activation");
        let stopped = true;
        try { await P.api("/api/play/stop", {}); } catch { stopped = false; }
        const currentDraft = at();
        if (currentDraft.context !== applyingContext || currentDraft.reasons.length) throw Object.assign(new Error("The case was activated. Newer browser edits are retained; open the current active model before building or deciding again."), { code: "ACTIVATED_WITH_NEWER_DRAFT" });
        const active = await P.activated(view, originDraftKey, applyingContext);
        context = at().context;
        const exactApp = view.packet?.subject?.generated_app;
        status(`✓ Revision ${active.baseline_version} is active and every view uses it. ${exactApp ? "The exact reviewed app binding is active; Build & play reopens its captured bundle." : "This historical approval covers the workflow only."}${stopped ? "" : " The previous app could not be stopped; its frame was closed. Stop it before using another runtime."}`);
      }, "Activating the approved revision atomically…");
    });
    for (const event of ["playide:plan", "playide:edit", "playide:tests", "playide:laws", "playide:built"]) document.addEventListener(event, () => { if ($("activation").open) render(); });
    window.PlayActivation = { open };
  }
  if (window.PlayIDE) init(window.PlayIDE);
})();
