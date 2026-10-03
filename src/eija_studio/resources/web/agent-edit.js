/* Offline proposals are untrusted. Only the existing owner preview may submit an edit. */
const EijaAgentEdit = (() => {
  "use strict";
  const clone = value => JSON.parse(JSON.stringify(value));
  const same = (left, right) => JSON.stringify(left) === JSON.stringify(right);
  const strings = value => Array.isArray(value) && value.every(item => typeof item === "string");
  function identity(left, right) {
    return !!left && !!right && left.caseId === right.caseId && left.version === right.version &&
      left.stage === right.stage && left.semanticHash === right.semanticHash &&
      left.packId === right.packId && left.packDigest === right.packDigest && same(left.model, right.model);
  }
  function validate(response, captured, request) {
    const check = response?.preview, tx = check?.transaction;
    if (!response || response.scope !== "typed-edit-proposal" || response.provider !== "offline" ||
        response.model !== "typed-edit-fixture-v1" || response.live !== false || response.trust !== "UNTRUSTED_PROPOSAL" ||
        response.request !== request || response.pack?.id !== captured.packId || response.pack?.digest !== captured.packDigest ||
        check?.scope !== "semantic-edit-preview" || check.applied !== false || check.persisted !== false ||
        typeof check.legal !== "boolean" || !strings(check.codes) || !strings(check.refs) ||
        check.case_id !== captured.caseId || check.version !== captured.version || check.stage !== captured.stage ||
        check.semantic_hash !== captured.semanticHash || !same(check.current, captured.model)) {
      throw new Error("Proposal did not identify this exact request and candidate. Request it again.");
    }
    const transition = captured.model.transitions?.find(item => item.id === tx?.transition);
    const role = tx?.kind === "set_role" && typeof tx.role === "string" && tx.role.length > 0;
    const endpoint = tx?.kind === "retarget_transition" && ["source", "target"].includes(tx.end) &&
      typeof tx.state === "string" && tx.state.length > 0;
    if (!transition || (!role && !endpoint) ||
        (check.legal && (!check.candidate || typeof check.candidate_semantic_hash !== "string" || !check.candidate_semantic_hash)) ||
        (!check.legal && (check.candidate !== null || check.candidate_semantic_hash !== null))) {
      throw new Error("Proposal contains no supported, identified transition edit. Nothing was submitted.");
    }
    return response;
  }
  function describe(response) {
    const {transaction: tx, current} = response.preview;
    const transition = current.transitions.find(item => item.id === tx.transition);
    const field = tx.kind === "set_role" ? "role" : tx.end;
    const before = field === "role" ? transition.role : transition[field === "source" ? "from_state" : "to_state"];
    const after = field === "role" ? tx.role : tx.state;
    return `${transition.action} · ${field}: ${before} → ${after}`;
  }
  function mount(root, {getContext, propose, previewChoice, navigate}) {
    const doc = root.ownerDocument || document;
    function node(tag, text, id, className) {
      const value = doc.createElement(tag);
      if (text !== undefined) value.textContent = text;
      if (id) value.id = id;
      if (className) value.className = className;
      return value;
    }
    const heading = node("h2", "Agent edit proposal");
    const scope = node("p", "Offline fixture · synthetic, untrusted proposal · model only; source stays read only.", null, "muted");
    const form = node("form", undefined, "agent-edit-form", "agent-edit-form");
    const label = node("label", "What should the agent change?"); label.htmlFor = "agent-edit-request";
    const input = node("textarea", undefined, "agent-edit-request"); input.rows = 2; input.maxLength = 6000;
    input.placeholder = "Move <action> source to <state> — use exact model names";
    const submit = node("button", "Propose edit", "agent-edit-propose"); submit.type = "submit";
    const status = node("p", undefined, "agent-edit-status"); status.tabIndex = -1; status.setAttribute("role", "status"); status.setAttribute("aria-live", "polite");
    const result = node("div", undefined, "agent-edit-result", "agent-edit-result");
    const summary = node("strong", undefined, "agent-edit-summary");
    const preview = node("button", "Preview proposed edit", "agent-edit-preview", "secondary"); preview.type = "button";
    const links = node("div", undefined, "agent-edit-actions", "agent-edit-actions");
    const navButtons = [["model", "Open changed transition"], ["changes", "Review UML changes"], ["rules", "Inspect affected rules"]].map(([kind, text]) => {
      const button = node("button", text, "agent-edit-" + kind, "secondary"); button.type = "button";
      button.onclick = () => route(kind); links.append(button); return button;
    });
    const details = node("details", undefined, "agent-edit-details");
    const exact = node("pre", undefined, "agent-edit-json"); exact.tabIndex = 0;
    details.append(node("summary", "Exact proposal and captured identity"), exact);
    form.append(label, input, submit); result.append(summary, preview, links, details);
    root.replaceChildren(heading, scope, form, status, result);
    let caseId = null, attempt = null, sequence = 0, destroyed = false;
    const context = () => getContext();
    const current = item => !destroyed && !!item && attempt === item && item.sequence === sequence;
    const applicable = item => current(item) && context()?.editable === true && identity(item.context, context());
    const savedCurrent = item => {
      const now = context(), saved = item?.saved;
      return current(item) && !!saved && now?.caseId === saved.caseId && now.version === saved.version &&
        now.semanticHash === saved.semanticHash && now.packId === item.context.packId && now.packDigest === item.context.packDigest &&
        same(now.model, item.response.preview.candidate);
    };
    function paint() {
      if (destroyed) return;
      const now = context(), phase = attempt?.phase || "idle", busy = phase === "requesting" || phase === "opening";
      root.hidden = !now;
      input.disabled = !now?.editable || busy;
      submit.disabled = !now?.editable || busy || !input.value?.trim();
      form.setAttribute("aria-busy", String(busy));
      status.dataset.status = phase;
      status.textContent = attempt?.message || (now?.editable ? "Describe one transition edit." : "Working candidate is read only. Your request is retained.");
      result.hidden = !attempt?.response;
      summary.textContent = attempt?.response ? describe(attempt.response) : "";
      exact.textContent = attempt?.response ? JSON.stringify(attempt.response, null, 2) : "";
      preview.hidden = !attempt?.response || phase === "applied";
      preview.disabled = !attempt?.response || !applicable(attempt) || !["proposed", "refused"].includes(phase);
      preview.textContent = attempt?.response?.preview.legal === false ? "Inspect refusal" : "Preview proposed edit";
      links.hidden = phase !== "applied";
      navButtons.forEach(button => { button.disabled = !savedCurrent(attempt); });
    }
    function update() {
      if (destroyed) return;
      const now = context();
      if ((now?.caseId || null) !== caseId) {
        caseId = now?.caseId || null; ++sequence; attempt = null; input.value = ""; details.open = false;
      } else if (attempt && !["failed", "stale"].includes(attempt.phase)) {
        const valid = attempt.phase === "applied" ? savedCurrent(attempt) : applicable(attempt);
        if (!valid) {
          attempt.cancelled = attempt.phase === "requesting";
          attempt.phase = "stale"; attempt.message = "Candidate or editing context changed. Request a new proposal before editing.";
        }
      }
      paint();
    }
    async function request(event) {
      event?.preventDefault();
      update();
      const now = context(), text = input.value.trim();
      if (!now?.editable || !text || ["requesting", "opening"].includes(attempt?.phase)) return false;
      const item = {sequence: ++sequence, context: clone(now), request: text, phase: "requesting", message: "Requesting one offline edit proposal…"};
      attempt = item; details.open = false; paint();
      try {
        const response = await propose(text, clone(item.context));
        if (!current(item) || item.cancelled) return false;
        if (!applicable(item)) { update(); return false; }
        item.response = clone(validate(response, item.context, text));
        item.phase = response.preview.legal ? "proposed" : "refused";
        item.message = response.preview.legal ? "Kernel checked this proposal. Preview the change; only your Apply edit saves it." :
          `Kernel refused this proposal: ${response.preview.codes.join("; ")}. No edit was submitted.`;
        paint(); return true;
      } catch (error) {
        if (!current(item) || item.cancelled) return false;
        if (!applicable(item)) { update(); return false; }
        item.phase = "failed"; item.message = `${error.code ? error.code + ": " : ""}${error.message || "Proposal request failed"} No edit was submitted.`;
        paint(); return false;
      }
    }
    function committed(item, value) {
      if (!current(item) || !item.previewOpened || !item.response.preview.legal ||
          value?.caseId !== item.context.caseId || value.previousVersion !== item.context.version || value.version !== item.context.version + 1 ||
          value.semanticHash !== item.response.preview.candidate_semantic_hash || !same(value.transaction, item.response.preview.transaction)) return false;
      item.saved = clone(value);
      if (!savedCurrent(item)) { item.saved = null; update(); return false; }
      item.phase = "applied"; item.message = `Candidate edit saved · revision ${value.version}. Baseline unchanged; evidence needs review.`;
      paint();
      if (status.getClientRects().length) status.focus();
      return true;
    }
    async function openPreview() {
      update();
      const item = attempt;
      if (!item?.response || !applicable(item) || !["proposed", "refused"].includes(item.phase)) return false;
      item.previewOpened = true;
      const previousPhase = item.phase; item.phase = "opening"; paint();
      try {
        await previewChoice({transaction: clone(item.response.preview.transaction)}, value => committed(item, value));
      } catch (error) {
        if (current(item) && item.phase === "opening") {
          item.phase = "failed"; item.message = `Could not open the edit preview: ${error.message || "request failed"}. Check the workspace status.`;
        }
      } finally {
        if (current(item) && item.phase === "opening") item.phase = previousPhase;
        update();
      }
      return current(item);
    }
    function route(kind) {
      update();
      if (!savedCurrent(attempt) || attempt.phase !== "applied") return false;
      navigate(kind, clone(attempt.response.preview.transaction)); return true;
    }
    input.oninput = () => { ++sequence; attempt = null; details.open = false; paint(); };
    form.onsubmit = request; preview.onclick = openPreview;
    update();
    return {update, destroy() { destroyed = true; ++sequence; attempt = null; root.replaceChildren(); }};
  }
  return {mount};
})();
if (typeof module !== "undefined") module.exports = EijaAgentEdit;
