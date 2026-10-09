// PlayIDE roles (ADR-0215): the human side of the model as one view. Each role is an actor: choosing one (on the use
// case diagram, in the outline or on the Permissions tab) says what it may do, which screens it sees and which fixture
// actors play it, and runs the built app as one of them. On the Screens tab, "See the app as" dims the screens a role
// never sees. What a role may do is the kernel's answer (`/api/play/access`, ADR-0171), never a reading of the page;
// starting a record is open to any active actor, because the model does not say who may.
"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  let P = null, lens = "", access = null, accessKey = "", loading = null, lastList = null, lastCard = null;

  // ---- The kernel's answer, per role --------------------------------------------------------------------------------
  async function permissions() {
    const key = P.viewKey();
    if (access && accessKey === key) return access;
    if (!loading || loading.key !== key) {
      const promise = P.api("/api/play/access", P.about()).then((result) => {
        if (P.viewKey() === key) { access = result; accessKey = key; }
        return result;
      });
      loading = { key, promise };
    }
    return loading.promise;
  }

  const current = () => (access && accessKey === P.viewKey() ? access : null);

  // A role's use cases: each action the kernel lets some fixture actor of that role take, with the states it leaves
  // from and which of the role's actors were let through. Use cases the role holds in the model but no actor could
  // take still count: the role holds them, and its actors' refusals say why.
  function useCasesOf(result, role) {
    const byAction = new Map();
    for (const state of result.states) {
      for (const c of (result.cells[state] || {})[role] || []) {
        const u = byAction.get(c.action) || { action: c.action, steps: [], assignedOnly: false, actors: new Map() };
        u.steps.push({ from: state, to: c.to, transition: c.transition });
        u.assignedOnly = u.assignedOnly || c.assigned_only;
        for (const a of c.actors) if (!u.actors.has(a.actor) || !a.refused) u.actors.set(a.actor, a.refused || "");
        byAction.set(c.action, u);
      }
    }
    return [...byAction.values()];
  }

  function roleOfAction(action) {
    const t = P.model().transitions.find((x) => x.action === action);
    return t ? t.role : "";
  }

  const actorsOf = (role) => ((P.pack() && P.pack().actors) || []).filter((a) => a.role === role);
  const titleOf = (action) => {
    const s = P.screens() && P.screens().screens.find((x) => x.use_case === action);
    return s ? s.title : action === null ? "Create" : action;
  };
  const article = (word) => (/^[AEIOU]/i.test(word) ? "An " : "A ") + word;
  const a = (word) => (/^[AEIOU]/i.test(word) ? "an " : "a ") + word;

  // ---- Run the app as one actor -------------------------------------------------------------------------------------
  function runButton(actor, primary) {
    const label = `▶ Run as ${actor.id}` + (actor.active ? "" : " (inactive)");
    const b = P.el("button", label, { type: "button", class: primary ? "primary run-as" : "quiet run-as", "data-actor": actor.id,
      title: actor.active ? `Build and run the app acting as ${actor.id}` : `${actor.id} is inactive: the kernel refuses every step it tries` });
    b.addEventListener("click", () => P.runAs(actor.id));
    return b;
  }

  function runTools(role) {
    const box = P.el("div", undefined, { class: "run-as-tools" });
    const actors = actorsOf(role);
    if (!actors.length) {
      box.append(P.el("span", `No fixture actor has the role ${role}, so the built app cannot act as one.`, { class: "muted small" }));
      return box;
    }
    const first = actors.find((a) => a.active) || actors[0];
    box.append(runButton(first, true), ...actors.filter((a) => a !== first).map((a) => runButton(a, false)));
    return box;
  }

  // Who holds the role, as a choice: changing it adds a step to the plan, which the server checks against the laws about
  // kinds of actor (only a person approves, ...), like any drawn edit. Nothing is saved (ADR-0210, #156).
  function kindPicker(role, kind) {
    const label = P.el("label", "Held by ", { class: "role-kind" }), select = P.el("select", undefined, { "aria-label": `Who holds ${role}` });
    for (const [k, words] of Object.entries(P.kinds)) {
      const option = P.el("option", words + (k === kind && k !== P.inForce(role) ? " (in the plan)" : ""), { value: k });
      option.selected = k === kind;
      select.append(option);
    }
    select.addEventListener("change", () => P.setKind(role, select.value));
    label.append(select);
    return label;
  }

  // ---- The inspector for an actor -----------------------------------------------------------------------------------
  async function inspectRole(id, box) {
    if (!id.startsWith("role:")) return;
    const role = id.slice(5), notes = (P.pack() && P.pack().role_notes) || {};
    const kind = P.roleKind ? P.roleKind(role) : "human"; // a person, an AI agent, a timer or an external system (ADR-0210)
    if (P.setKind && P.kinds && !P.reviewing()) box.append(kindPicker(role, kind));
    else if (kind !== "human" && P.kinds) box.append(P.el("p", `«${P.kinds[kind]}»`, { class: "role-kind" }));
    if (notes[role]) box.append(P.el("p", notes[role], { class: "muted" }));
    const body = P.el("div", undefined, { class: "role-inspect", "aria-live": "polite" });
    body.append(P.el("p", "Asking the kernel…", { class: "muted small" }));
    box.append(body);
    let result;
    try { result = await permissions(); } catch (error) {
      body.replaceChildren(P.el("p", `${error.code || "ERROR"}: ${error.message}`, { class: "refusal" }));
      return;
    }
    if (P.selected() !== id) return; // another selection replaced this one while the kernel answered
    const cases = useCasesOf(result, role);
    const list = P.el("ul", undefined, { class: "role-cases", "aria-label": `Use cases of ${role}` });
    for (const u of cases) {
      const li = P.el("li");
      const b = P.el("button", u.action, { type: "button", class: "quiet", title: "Show it on the state machine" });
      b.addEventListener("click", () => P.select("transition:" + u.steps[0].transition, true));
      li.append(b, P.el("span", ` ${u.steps.map((s) => `${s.from} → ${s.to}`).join(", ")}${u.assignedOnly ? " · assigned only" : ""}`, { class: "muted small" }));
      list.append(li);
    }
    if (!cases.length) list.append(P.el("li", `${role} may take no step of the workflow: only start a record.`, { class: "muted" }));
    const actors = P.el("ul", undefined, { class: "role-actors", "aria-label": `Fixture actors with the role ${role}` });
    for (const a of actorsOf(role)) {
      const flags = [a.active ? "active" : "inactive", a.assigned ? "assigned" : ""].filter(Boolean).join(", ");
      actors.append(P.el("li", `${a.id} (${flags})`, { class: a.active ? "" : "no" }));
    }
    const tools = P.el("div", undefined, { class: "inspector-tools" });
    const see = P.el("button", "See their screens", { type: "button" });
    see.addEventListener("click", () => { lens = role; P.showTab("screens"); renderLens(); });
    const who = P.el("button", "Who can do what", { type: "button", class: "quiet" });
    who.addEventListener("click", () => P.showTab("access"));
    tools.append(see, who);
    body.replaceChildren(P.el("h4", "May"), list, P.el("p", "Any active actor may start a record.", { class: "muted small" }),
      P.el("h4", "Played by"), actors, tools, runTools(role));
  }

  // ---- "See the app as" on the Screens tab --------------------------------------------------------------------------
  function theirs(result, role) {
    return new Set(useCasesOf(result, role).map((u) => u.action));
  }

  function renderLens() {
    const bar = $("role-lens"), strip = $("role-app");
    if (!bar || !P.screens()) return;
    const result = current();
    if (!result) { permissions().then(renderLens, () => {}); return; }
    if (lens && !result.roles.includes(lens)) lens = "";
    bar.replaceChildren(P.el("span", "See the app as", { class: "lens-label" }));
    for (const role of ["", ...result.roles]) {
      const b = P.el("button", role || "Everyone", { type: "button", class: "lens-role", "aria-pressed": String(role === lens), "data-role": role });
      b.addEventListener("click", () => { lens = role; renderLens(); });
      bar.append(b);
    }
    strip.replaceChildren();
    strip.hidden = !lens;
    if (lens) {
      const mine = theirs(result, lens), cases = [null, ...useCasesOf(result, lens).map((u) => u.action)];
      const all = [null, ...new Set(P.model().transitions.map((t) => t.action))];
      const never = all.filter((a) => a !== null && !mine.has(a));
      const head = P.el("p", undefined, { class: "role-app-head" });
      head.append(P.el("strong", `${article(lens)} sees ${cases.length} of ${all.length} screens.`),
        " Starting a record is open to any active actor; the rest are what the kernel lets the role do.");
      const flow = P.el("ol", undefined, { class: "role-flow", "aria-label": `Screens ${lens} sees` });
      for (const action of cases) {
        const b = P.el("button", titleOf(action), { type: "button", title: action === null ? "Starts a record" : action });
        b.addEventListener("click", () => P.openScreen(action));
        const li = P.el("li");
        li.append(b);
        flow.append(li);
      }
      strip.append(head, flow);
      if (never.length) strip.append(P.el("p", `Never sees: ${never.map((a) => `${titleOf(a)} (${roleOfAction(a)})`).join(", ")}.`, { class: "muted small role-never" }));
      strip.append(runTools(lens));
    }
    decorate();
  }

  // Dim the screens the chosen role never sees, and say on the card who sees the one open.
  function decorate(event) {
    if (event && event.list) lastList = event;
    const result = current(), mine = result && lens ? theirs(result, lens) : null;
    if (lastList && lastList.list.isConnected) {
      [...lastList.list.children].forEach((li, i) => {
        const name = lastList.names[i], hide = mine !== null && name !== null && !mine.has(name);
        li.classList.toggle("not-theirs", hide);
        const b = li.querySelector("button");
        if (b) b.title = hide ? `${article(lens)} never sees this screen` : "";
      });
    }
    const card = $("screen-card");
    const old = card && card.querySelector(".role-note");
    if (old) old.remove();
    if (!card || !mine || !card.querySelector(".screen-title")) return;
    const open = event && "useCase" in event ? event.useCase : (lastCard || {}).useCase;
    let text;
    if (open === null) text = `${article(lens)} sees this screen: any active actor may start a record.`;
    else if (mine.has(open)) text = `${article(lens)} sees this screen.`;
    else text = `${article(lens)} never sees this screen: only ${roleOfAction(open) ? a(roleOfAction(open)) : "another role"} may take ${open}.`;
    card.prepend(P.el("p", text, { class: "role-note " + (open === null || mine.has(open) ? "ok" : "warn") }));
  }

  function onScreens(event) {
    if (event.card) lastCard = event;
    decorate(event);
  }

  function init() {
    if (P || !window.PlayIDE || !window.PlayIDE.tab) return;
    P = window.PlayIDE;
    P.hooks.inspect.push(inspectRole);
    P.hooks.screens.push(onScreens);
    P.hooks.tab.push((which) => { if (which === "screens") renderLens(); });
    P.hooks.redraw.push(() => { if (P.tab() === "screens") renderLens(); }); // a plan previewed or left changes who may do what
  }

  init();
  document.addEventListener("playide:ready", init);
})();
