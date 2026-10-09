// PlayIDE permissions (ADR-0171): who can do what, from each state, as a role by state matrix whose every cell the
// kernel has tried with the pack's fixture actors, and reachability questions ("can a record reach this state without
// that role?") answered on the server. While a plan is previewed, the permissions it adds or removes are flagged.
// The page only draws what the server returns.
"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  let P = null, seq = 0, asked = false, question = { target: "", without: "" }; // asked: re-ask on every redraw

  const VERDICTS = {
    UNREACHABLE: ["No", "ok"],
    REACHABLE: ["Yes", "bad"],
    NOT_SHOWN: ["Not shown", "warn"],
  };

  async function render() {
    if (!P || P.tab() !== "access") return;
    const mine = ++seq, panel = $("access-panel");
    try {
      const result = await P.api("/api/play/access", P.about());
      if (mine !== seq) return; // a newer render (another preview) is on its way
      panel.replaceChildren(ask(result), changes(result), table(result), P.el("p", result.limits.join(" "), { class: "muted small" }));
    } catch (error) {
      if (mine === seq) panel.replaceChildren(P.el("p", `${error.code || "ERROR"}: ${error.message}`, { class: "refusal" }));
    }
  }

  // ---- The question -----------------------------------------------------------------------------------------------
  function select(options, value, label) {
    const node = P.el("select", undefined, { "aria-label": label });
    for (const [v, text] of options) node.append(Object.assign(P.el("option", text), { value: v, selected: v === value }));
    return node;
  }

  function ask(result) {
    const form = P.el("form", undefined, { class: "reach", "aria-label": "Reachability question" });
    if (!result.states.includes(question.target)) question.target = result.states[result.states.length - 1];
    const target = select(result.states.map((s) => [s, s]), question.target, "State");
    const without = select([["", "at all"], ...result.roles.map((r) => [r, `without a ${r}`])], question.without, "Without role");
    const answer = P.el("div", undefined, { id: "reach-answer", class: "reach-answer", role: "status", "aria-live": "polite" });
    form.append(P.el("span", "Can a record reach"), target, without, P.el("span", "?"),
      P.el("button", "Ask the kernel", { type: "submit", class: "primary" }), answer);
    const run = async (event) => {
      if (event) { event.preventDefault(); asked = true; }
      question = { target: target.value, without: without.value };
      answer.replaceChildren(P.el("span", "Checking…", { class: "muted" }));
      try {
        showAnswer(answer, await P.api("/api/play/reach", { ...P.about(), target: question.target, without: question.without || null }));
      } catch (error) {
        answer.replaceChildren(P.el("p", `${error.code || "ERROR"}: ${error.message}`, { class: "refusal" }));
      }
    };
    form.addEventListener("submit", run);
    if (asked) run();
    return form;
  }

  function showAnswer(box, r) {
    let [word, tone] = VERDICTS[r.verdict];
    // Reaching a state without a role is the worrying answer; reaching it at all is the expected one, and a state no
    // run reaches is the problem.
    if (!question.without && r.verdict !== "NOT_SHOWN") tone = r.verdict === "REACHABLE" ? "ok" : "bad";
    const head = P.el("p", undefined, { class: "verdict " + tone });
    head.append(P.el("strong", word), ` ${r.why}`);
    box.replaceChildren(head);
    if (!r.path.length) return;
    const path = P.el("ol", undefined, { class: "reach-path", "aria-label": "Path the kernel committed" });
    for (const step of r.path) {
      const b = P.el("button", `${step.action}: ${step.from} → ${step.to}`, { type: "button", title: `Taken by ${step.actor} (${step.role}); show it on the state machine` });
      b.addEventListener("click", () => P.select("transition:" + step.transition, true));
      const li = P.el("li");
      li.append(b, P.el("span", ` by ${step.actor}`, { class: "muted small" }));
      path.append(li);
    }
    box.append(path);
  }

  // ---- What a previewed plan changes --------------------------------------------------------------------------------
  function changes(result) {
    const { added, removed } = result.changes;
    const box = P.el("div", undefined, { class: "access-changes" });
    if (!added.length && !removed.length) return box;
    box.append(P.el("h3", "This plan changes who can do what"));
    const list = P.el("ul");
    for (const [rows, sign, tone] of [[added, "+", "added"], [removed, "−", "removed"]]) {
      for (const c of rows) list.append(P.el("li", `${sign} ${c.role} may ${c.action} from ${c.state} (to ${c.to})`, { class: tone }));
    }
    box.append(list);
    return box;
  }

  // ---- The matrix ---------------------------------------------------------------------------------------------------
  function table(result) {
    const removed = result.changes.removed, added = new Set(result.changes.added.map((c) => `${c.state}|${c.role}|${c.action}|${c.to}`));
    const grid = P.el("table", undefined, { class: "access-grid" });
    grid.append(P.el("caption", "Rows are states, columns are roles. Each entry is an action that role may take from that state."));
    const head = P.el("tr");
    head.append(P.el("th", "From state", { scope: "col" }), ...result.roles.map((r) => {
      // A role heads its column; choosing it shows the actor's screens and runs the app as one (play-roles.js, ADR-0215).
      // A role held by an AI agent, a timer or an external system says so, in its colours on the use case diagram.
      const th = P.el("th", undefined, { scope: "col" }), b = P.el("button", r, { type: "button", class: "role-head", title: `What ${r} may do and sees` });
      b.addEventListener("click", () => P.select("role:" + r, false));
      th.append(b);
      const kind = P.roleKind(r);
      if (kind !== "human") th.append(P.el("span", P.kinds[kind], { class: `actor-kind ${kind}` }));
      return th;
    }));
    grid.append(head);
    for (const state of result.states) {
      const tr = P.el("tr");
      const th = P.el("th", state + (state === result.initial ? " (initial)" : ""), { scope: "row" });
      tr.append(th);
      for (const role of result.roles) {
        const td = P.el("td");
        for (const c of result.cells[state][role] || []) td.append(entry(c, added.has(`${state}|${role}|${c.action}|${c.to}`)));
        for (const c of removed.filter((x) => x.state === state && x.role === role)) {
          td.append(P.el("div", `${c.action} → ${c.to}`, { class: "perm removed", title: "Removed by this plan" }));
        }
        if (!td.childNodes.length) td.append(P.el("span", "—", { class: "muted", "aria-label": "nothing" }));
        tr.append(td);
      }
      grid.append(tr);
    }
    return grid;
  }

  function entry(c, isNew) {
    const box = P.el("div", undefined, { class: "perm" + (isNew ? " added" : "") });
    const name = P.el("button", `${c.action} → ${c.to}`, { type: "button", class: "perm-name", title: "Show it on the state machine" });
    name.addEventListener("click", () => P.select("transition:" + c.transition, true));
    box.append(name);
    if (c.assigned_only) box.append(P.el("span", "assigned only", { class: "tag" }));
    if (isNew) box.append(P.el("span", "new", { class: "tag new" }));
    const who = P.el("ul", undefined, { class: "who-can", "aria-label": "Fixture actors the kernel tried" });
    for (const a of c.actors) {
      who.append(P.el("li", a.refused ? `✗ ${a.actor} (${a.refused})` : `✓ ${a.actor}`, { class: a.refused ? "no" : "yes" }));
    }
    if (!c.actors.length) who.append(P.el("li", "No fixture actor has this role", { class: "no" }));
    box.append(who);
    return box;
  }

  function init() {
    if (P || !window.PlayIDE || !window.PlayIDE.tab) return;
    P = window.PlayIDE;
    P.hooks.tab.push((which) => { if (which === "access") render(); });
    P.hooks.redraw.push(render); // a preview entered or left: the matrix follows the model on show
  }

  init();
  document.addEventListener("playide:ready", init);
})();
