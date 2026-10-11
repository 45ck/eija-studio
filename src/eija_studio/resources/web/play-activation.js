// Exact draft handoff and owner decisions. The server interprets and checks every step; this surface only
// displays returned case/packet identities and sends a decision when the person deliberately submits it.
"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  let P = null, view = null, context = null, shownCandidate = null, originDraftKey = null, busy = false, message = "", problem = false;
  const short = (hash) => hash ? hash.slice(0, 16) : "not available";
  const closed = () => view && ["APPLIED", "DISCARDED"].includes(view.case.stage);
  const readOnly = () => Boolean(P.reviewing && P.reviewing());
  const candidateCoherent = () => !view || JSON.stringify(shownCandidate) === JSON.stringify(view.case.candidate || view.case.baseline);
  const sameContext = () => !view || context === P.activationDraft().context && candidateCoherent();
  const eligible = () => Boolean(view && view.packet && view.packet.eligible && Array.isArray(view.packet.blockers) && !view.packet.blockers.length);
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
  };

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
    const steps = displayedSteps(draft);
    $("activation-steps").replaceChildren(...steps.map((s, n) => {
      const li = el("li"), drawn = P.base().transitions.find((t) => t.id === s.transaction.transition);
      const name = s.transaction.kind.replaceAll("_", " "), subject = s.transaction.state || s.transaction.action || (drawn && drawn.action) || s.transaction.transition || "";
      li.append(el("span", s.author === "ai" ? "AI" : s.author === "you" ? "You" : "Stored command", { class: "who " + s.author }),
        el("span", `${n + 1}. ${name}${subject ? ": " + subject : ""}${s.transaction.to ? " → " + s.transaction.to : ""}`));
      return li;
    }));
    const reasons = [...draft.reasons];
    if (sizeIssue && !P.about().case_id && !(view && coherent)) reasons.push(sizeIssue);
    if (readOnly()) reasons.unshift("This is a read-only stakeholder view. Open the editable local case to transfer, verify or make an owner decision.");
    if (!coherent && !closed()) reasons.unshift(candidateCoherent()
      ? "The diagram or draft moved since this case was transferred. This case is retained, but its checks and decisions cannot act on the changed draft."
      : "This case has newer behaviour than the diagrams on this page. Open this case again to inspect its current UML before verifying or deciding. Your browser draft is retained.");
    $("activation-drafts").replaceChildren(...[...reasons, ...(draft.notes || [])].map((r) => el("li", r)));
    const core = packet && packet.core_status || (P.status() && P.status().trusted_fixture ? "RELEASE_FIXTURE_MATCH" : "SOURCE_REVIEW_REQUIRED");
    $("activation-source").textContent = core === "SOURCE_REVIEW_REQUIRED" ? "SOURCE_REVIEW_REQUIRED · source changes need legitimate owner review. Model inspection can continue; trusted verification, approval and activation are blocked."
      : "Source matches the reviewed release fixture. Byte identity does not prove correctness.";
    $("activation-source").className = core === "SOURCE_REVIEW_REQUIRED" ? "activation-warning" : "activation-source";
    $("activation-transfer").hidden = Boolean(P.about().case_id) || Boolean(view && coherent);
    $("activation-transfer").textContent = view ? "Transfer current draft as a new case" : "Transfer exact accepted steps";
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
    view = await P.api(path());
  }

  async function transfer() {
    if (readOnly()) return status("Read-only view: open the editable local case before transferring a plan.", true);
    const draft = at();
    if (draft.reasons.length) return status(draft.reasons.join(" "), true);
    const sizeIssue = transferIssue(draft);
    if (sizeIssue) return status(`PLAN_TRANSFER_TOO_LARGE: ${sizeIssue}`, true);
    await task(async () => {
      const created = await P.api("/api/cases/from-plan", draft.request);
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
    await P.api(path("/" + action), { expected_version: view.case.version, ...extra });
    await refresh();
  }

  async function open() {
    if (!P) return;
    render(); $("activation").showModal();
    if (!view && P.about().case_id) {
      const opening = at();
      await task(async () => {
        view = await P.api(`/api/cases/${encodeURIComponent(P.about().case_id)}`);
        context = opening.context; shownCandidate = opening.shownCandidate;
        try { originDraftKey = sessionStorage.getItem("playide.activation.origin:" + view.case.id); } catch { /* storage unavailable */ }
        status("Case and review evidence loaded. Inspection, checks and owner decisions remain separate.");
      }, "Loading the exact case and its evidence…");
    }
  }

  function init(bridge) {
    P = bridge;
    $("activation-open").addEventListener("click", open);
    $("activation-close").addEventListener("click", () => $("activation").close());
    $("activation-transfer").addEventListener("click", transfer);
    $("activation-diff").addEventListener("click", () => { $("activation").close(); P.inspectChange(); });
    $("activation-effects").addEventListener("click", () => { if (busy) return; $("activation").close(); P.showEffects(); });
    $("activation-refresh").addEventListener("click", () => task(async () => { await refresh(); status("Current case and evidence loaded. New subject identities clear old unsent answers."); }, "Refreshing the case and evidence…"));
    $("activation-check").addEventListener("click", () => task(async () => {
      await command("verify"); status("✓ Bounded runtime verification finished for this case. Human understanding remains UNKNOWN; nothing was approved.");
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
        status(`✓ Revision ${active.baseline_version} is active and every view uses it. Build & run starts from the active model.${stopped ? "" : " The previous app could not be stopped; its frame was closed. Stop it before using another runtime."}`);
      }, "Activating the approved revision atomically…");
    });
    for (const event of ["playide:plan", "playide:edit", "playide:tests", "playide:laws"]) document.addEventListener(event, () => { if ($("activation").open) render(); });
    window.PlayActivation = { open };
  }
  if (window.PlayIDE) init(window.PlayIDE);
})();
