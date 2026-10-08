// PlayIDE assist (ADR-0170): how a person and the AI share the work. The page asks the AI about what is selected,
// completes exact model names while typing, opens every command from one palette, and lets a person review an AI
// plan from the keyboard. Nothing here interprets a request or decides a step: it only writes text into the chat box
// and presses the page's own controls, so every request still goes through the server's proposer and policy.
"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  const HOLE = /‹[^›]+›/; // a blank the person still has to fill, written ‹state›, ‹role›, ‹action› or ‹new name›
  const isMac = /Mac|iPhone|iPad/.test(navigator.platform);
  const MOD = isMac ? "⌘" : "Ctrl+";
  const REVIEW = new URLSearchParams(location.search).get("view") === "review"; // the read-only review view (ADR-0172)

  function el(tag, text, attrs = {}) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
    return node;
  }

  const view = () => window.PlayIDE; // the view play.js exposes; the assist layer only reads base(), pack() and selected()
  const usable = (node) => node && !node.hidden && !node.disabled && !node.closest("[hidden]");

  // ---- Who does what --------------------------------------------------------------------------------------------
  // The delegation fence, always visible beside the chat: the AI proposes, the person checks and tries, and only the
  // owner approves and applies, in the review workbench.
  function authority() {
    const strip = el("p", undefined, { class: "authority", id: "authority" });
    for (const [who, what] of [["AI", "proposes steps"], ["You", "check, preview and try them"], ["Owner", "approves and applies in the review workbench"]]) {
      const part = el("span");
      part.append(el("strong", who), " " + what);
      strip.append(part);
    }
    document.querySelector(".chat .run-head").after(strip);
  }

  // ---- Ask about the selection ----------------------------------------------------------------------------------
  // Phrases the offline proposer reads (ADR-0156). A selected state or transition fills its own name in; the blanks
  // left are for the person. Pressing a phrase while the box has text adds it as the next clause ("then").
  const PHRASES = {
    none: [
      ["Add a state", "add state ‹new state› after ‹state›"],
      ["Rename a state", "rename ‹state› to ‹new name›"],
      ["Add a transition", "add ‹action› from ‹state› to ‹state› for ‹role›"],
      ["Change who may", "allow ‹role› to ‹action›"],
      ["Move an end", "move ‹action› target to ‹state›"],
    ],
    state: (s) => [
      ["Add a state after", `add state ‹new state› after ${s}`],
      ["Rename", `rename ${s} to ‹new name›`],
      ["Add a transition from here", `add ‹action› from ${s} to ‹state› for ‹role›`],
      ["Start records here", `start in ${s}`],
      ["Remove", `remove state ${s}`],
    ],
    transition: (t) => [
      ["Change who may", `allow ‹role› to ${t.action}`],
      ["Move its target", `move ${t.action} target to ‹state›`],
      ["Move its source", `move ${t.action} source to ‹state›`],
      ["Remove", `remove ${t.action}`],
    ],
  };

  function suggestions(id) {
    const box = $("chat-suggest"), model = view() && view().base();
    if (!box || !model) return;
    let title = "Try", phrases = PHRASES.none;
    if (id && id.startsWith("state:") && model.states.includes(id.slice(6))) {
      title = `About ${id.slice(6)}`;
      phrases = PHRASES.state(id.slice(6));
    } else if (id && id.startsWith("transition:")) {
      const t = model.transitions.find((x) => x.id === id.slice(11));
      if (t) { title = `About ${t.action}`; phrases = PHRASES.transition(t); }
    }
    const row = el("div", undefined, { class: "suggest-row" });
    for (const [name, phrase] of phrases) {
      const b = el("button", name, { type: "button", title: phrase, "data-phrase": phrase });
      b.addEventListener("click", () => insertPhrase(phrase));
      row.append(b);
    }
    box.replaceChildren(el("span", title, { class: "suggest-title" }), row);
  }

  function insertPhrase(phrase) {
    const input = $("chat-input"), text = input.value.trim();
    input.value = text ? `${text} then ${phrase}` : phrase;
    input.focus();
    if (!nextHole(input, text.length)) input.setSelectionRange(input.value.length, input.value.length);
    complete();
  }

  // Select the next blank at or after `from`, like a snippet's tab stop.
  function nextHole(input, from = 0) {
    let match = HOLE.exec(input.value.slice(from)), start = match ? from + match.index : 0;
    if (!match) {
      match = HOLE.exec(input.value);
      if (!match) return false;
      start = match.index;
    }
    input.setSelectionRange(start, start + match[0].length);
    return true;
  }

  // ---- Exact names while typing ---------------------------------------------------------------------------------
  // The proposer wants exact model names. The box offers them: the kind follows a selected blank (‹state› offers
  // states), otherwise any state, action or role that starts with the word being typed. A combobox list (WAI-ARIA APG).
  let options = [], active = -1, span = null;
  let slot = null; // the blank being filled: its kind still applies after its marker has been typed over

  function names() {
    const v = view(), model = v && v.base(), pack = v && v.pack();
    if (!model || !pack) return [];
    // States this request adds itself are offered too, since a later clause may use them.
    const planned = [...$("chat-input").value.matchAll(/\b(?:add state|rename [\w-]+ to) ([A-Za-z][\w-]*)/gi)].map((m) => m[1]).filter((n) => !model.states.includes(n));
    return [...model.states.map((n) => [n, "state"]), ...[...new Set(planned)].map((n) => [n, "new state"]),...pack.actions.map((n) => [n, "action"]), ...pack.roles.map((n) => [n, "role"])];
  }

  function complete() {
    const input = $("chat-input"), { selectionStart: a, selectionEnd: b, value } = input;
    const hole = value.slice(a, b);
    let kind = null, prefix = "";
    if (HOLE.test(hole) && HOLE.exec(hole)[0] === hole) {
      kind = /role/.test(hole) ? "role" : /action/.test(hole) ? "action" : /new/.test(hole) ? null : "state";
      span = [a, b];
      slot = { kind, start: a };
      if (!kind) return close(); // a new name is the person's to choose
    } else {
      const word = /[A-Za-z][\w-]*$/.exec(value.slice(0, a));
      if (!word || a !== b) return close();
      prefix = word[0];
      span = [a - prefix.length, a];
      if (slot && slot.start === span[0]) kind = slot.kind;
      else slot = null;
      if (slot && !kind) return close();
    }
    const lower = prefix.toLowerCase();
    options = names().filter(([n, k]) => (!kind || k === kind || (kind === "state" && k === "new state")) && n.toLowerCase().startsWith(lower) && n !== prefix).slice(0, 8);
    if (!options.length) return close();
    active = 0;
    render();
  }

  function render() {
    const list = $("chat-complete"), input = $("chat-input");
    list.replaceChildren(...options.map(([n, k], i) => {
      const li = el("li", undefined, { role: "option", id: `complete-${i}`, "aria-selected": String(i === active) });
      li.append(el("span", n), el("span", k, { class: "kind-tag" }));
      li.addEventListener("mousedown", (event) => { event.preventDefault(); accept(i); });
      return li;
    }));
    list.hidden = false;
    input.setAttribute("aria-expanded", "true");
    input.setAttribute("aria-activedescendant", `complete-${active}`);
  }

  function close() {
    options = [];
    active = -1;
    $("chat-complete").hidden = true;
    $("chat-input").setAttribute("aria-expanded", "false");
    $("chat-input").removeAttribute("aria-activedescendant");
  }

  function accept(i) {
    const input = $("chat-input"), [a, b] = span, name = options[i][0];
    slot = null;
    input.value = input.value.slice(0, a) + name + input.value.slice(b);
    input.focus();
    close();
    if (!nextHole(input, a + name.length)) input.setSelectionRange(a + name.length, a + name.length);
    else complete();
  }

  function composerKeys(event) {
    const input = event.target;
    if (!$("chat-complete").hidden && options.length) {
      if (event.key === "ArrowDown" || event.key === "ArrowUp") {
        event.preventDefault();
        active = (active + (event.key === "ArrowDown" ? 1 : options.length - 1)) % options.length;
        return render();
      }
      if ((event.key === "Enter" && !event.ctrlKey && !event.metaKey) || event.key === "Tab") { event.preventDefault(); return accept(active); }
      if (event.key === "Escape") { event.preventDefault(); return close(); }
    }
    if (event.key === "Tab" && !event.shiftKey && HOLE.test(input.value)) { event.preventDefault(); nextHole(input, input.selectionEnd); complete(); return; }
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      if (!$("chat-send").disabled) $("chat-form").requestSubmit(); // the same rule as the button: one plan request at a time
    }
  }

  // A request with an unfilled blank would only be refused; say which blank instead of sending it.
  function guardSubmit(event) {
    if (event.target.id !== "chat-form") return;
    const input = $("chat-input"), hole = HOLE.exec(input.value);
    close();
    if (!hole) { $("chat-hint").textContent = ""; return; }
    event.preventDefault();
    event.stopImmediatePropagation();
    $("chat-hint").textContent = `Fill in ${hole[0]} first.`;
    input.focus();
    nextHole(input);
    complete();
  }

  function composer() {
    const form = $("chat-form"), input = $("chat-input");
    const box = el("div", undefined, { id: "chat-suggest", class: "suggest", role: "group", "aria-label": "Phrases the planner reads" });
    const list = el("ul", undefined, { id: "chat-complete", class: "complete", role: "listbox", "aria-label": "Model names" });
    list.hidden = true;
    form.before(box);
    form.append(list);
    form.after(el("p", "", { id: "chat-hint", class: "muted small chat-hint", role: "status", "aria-live": "polite" }));
    form.classList.add("with-complete");
    input.setAttribute("role", "combobox");
    input.setAttribute("aria-autocomplete", "list");
    input.setAttribute("aria-controls", "chat-complete");
    input.setAttribute("aria-expanded", "false");
    input.placeholder = `Ask for a change… (${MOD}Enter to send)`;
    input.addEventListener("keydown", composerKeys);
    input.addEventListener("input", complete);
    input.addEventListener("click", complete);
    input.addEventListener("blur", () => setTimeout(close, 120));
    document.addEventListener("submit", guardSubmit, true);
    suggestions("");
  }

  // ---- Reviewing an AI plan from the keyboard ---------------------------------------------------------------------
  // Single-key shortcuts act only while focus is inside the plan being reviewed (WCAG 2.1.4). Space is the
  // checkbox's own toggle; nothing here ticks a step on the person's behalf.
  const livePlan = () => [...document.querySelectorAll("#chat-log .plan")].reverse().find((p) => p.querySelector("input:not(:disabled)"));

  function reviewKeys(event) {
    if (event.ctrlKey || event.metaKey || event.altKey) return;
    const card = event.target.closest && event.target.closest(".plan");
    if (!card || card !== livePlan()) return;
    const steps = [...card.querySelectorAll(".plan-steps > li")];
    const at = steps.findIndex((li) => li.contains(event.target));
    const key = event.key.toLowerCase();
    if (key === "j" || key === "arrowdown" || key === "k" || key === "arrowup") {
      event.preventDefault();
      const to = Math.max(0, Math.min(steps.length - 1, at + (key === "j" || key === "arrowdown" ? 1 : -1)));
      steps[to].querySelector("input").focus();
    } else if ((key === "s" || key === "enter") && at >= 0) {
      event.preventDefault();
      steps[at].querySelector(".show").click();
    } else if (key === "p") {
      const preview = card.querySelector(".plan-tools .primary");
      if (usable(preview)) { event.preventDefault(); preview.click(); }
    }
  }

  function markPlans(records) {
    for (const record of records) {
      for (const node of record.addedNodes) {
        const card = node.querySelector && node.querySelector(".plan");
        if (!card || card.querySelector(".review-keys")) continue;
        for (const box of card.querySelectorAll(".plan-steps input")) box.setAttribute("aria-keyshortcuts", "J K Space S P");
        card.querySelector(".plan-steps").after(el("p", "Review keys: J/K move · Space accept or reject · S show on the diagram · P preview on or off", { class: "muted small review-keys" }));
      }
    }
  }

  function reviewPlan() {
    const card = livePlan();
    if (card) card.querySelector(".plan-steps input").focus();
  }

  // ---- The review view ----------------------------------------------------------------------------------------------
  // ?view=review: the same UML diagrams, Permissions, Simulate, the run bar and Build & run, with every editing tool out
  // of view, for someone who reviews the model rather than changes it. It is a view, not a permission: edits in PlayIDE
  // are never saved anyway, and approving or applying a change stays with the owner in the review workbench.
  const viewUrl = (review) => {
    const query = new URLSearchParams(location.search);
    if (review) query.set("view", "review"); else query.delete("view");
    return location.pathname + (query.toString() ? "?" + query : "");
  };

  function reviewView() {
    if (!REVIEW) return;
    document.body.dataset.view = "review";
    $("screen-card").inert = true; // read the screens, change nothing
    const badge = el("span", undefined, { id: "review-badge", class: "view-badge", role: "note",
      title: "Read, simulate and check. Nothing here can change the model; the owner approves in the review workbench." });
    const leave = el("a", "Edit", { href: viewUrl(false), class: "quiet", title: "Leave the review view" });
    badge.append(el("strong", "Review view"), " read only ", leave);
    (document.querySelector(".bar .brand") || document.body).after(badge);
    // The state machine's hint talks about drawing; say what this view is for instead.
    const hint = $("canvas-help"), reword = () => {
      if (hint.textContent.startsWith("Drag from the palette")) hint.textContent = "Select an element to inspect it. Simulate and the run bar show how records move; Permissions shows who can do what.";
    };
    new MutationObserver(reword).observe(hint, { childList: true });
    reword();
    // Delete on the canvas would add a removal to a plan; there is no plan in this view.
    document.addEventListener("keydown", (event) => {
      if ((event.key === "Delete" || event.key === "Backspace") && event.target.closest && event.target.closest(".canvas")) event.stopImmediatePropagation();
    }, true);
  }

  // ---- One palette for every command and every element -------------------------------------------------------------
  // Ctrl+K (⌘K). Commands press the page's own buttons, so the palette can do nothing a click could not.
  function commands() {
    const press = (id) => () => $(id).click();
    const items = [
      ["Ask the AI for a change", "chat-input", () => $("chat-input").focus()],
      ["Review the AI plan", null, reviewPlan, () => Boolean(livePlan())],
      ["Preview the plan on the diagram", null, () => livePlan().querySelector(".plan-tools .primary").click(),
        () => { const p = livePlan(), b = p && p.querySelector(".plan-tools .primary"); return usable(b) && /Preview/.test(b.textContent); }],
      ["Back to the model", "plan-back", press("plan-back")],
      ["Build & run", "build", press("build")],
      ["Simulate", "simulate", press("simulate")],
      ["Run the simulation (F5)", "run-play", press("run-play")],
      ["Pause (F6)", "run-pause", press("run-pause")],
      ["Step (F10)", "run-step", press("run-step")],
      ["Stop (Shift+F5)", "run-stop", press("run-stop")],
      ["Restart (Ctrl+Shift+F5)", "run-restart", press("run-restart")],
      ["Show the state machine", "tab-states", press("tab-states")],
      ["Show the class diagram", "tab-classes", press("tab-classes")],
      ["Show the use cases", "tab-usecases", press("tab-usecases")],
      ["Show the screens", "tab-screens", press("tab-screens")],
      ["Show the components", "tab-components", press("tab-components")],
      ["Show who can do what (permissions)", "tab-access", press("tab-access")],
      ["Show the laws", "tab-laws", press("tab-laws")],
      ["Show or hide the model and inspector (Ctrl+B)", "toggle-left", press("toggle-left")],
      ["Show or hide the run panel (Ctrl+Alt+P)", "toggle-dock", press("toggle-dock")],
      ["Show or hide the chat (Ctrl+Alt+C)", "toggle-chat", press("toggle-chat")],
      ["Fit the diagram", "fit", press("fit")],
      ["Show the checks", "health", press("health"), () => $("checks") && $("checks").hidden],
      ["Open the review workbench", null, () => { location.href = "/"; }],
      ...[["xmi", "XMI"], ["plantuml", "PlantUML"], ["mermaid", "Mermaid"], ["drawio", "draw.io"]].map(([f, name]) => // ADR-0190
        [`Export the model as ${name}`, null, () => $(`uml-export-${f}`).click(), () => Boolean($(`uml-export-${f}`))]),
      ["Import a UML file (XMI, PlantUML, Mermaid, draw.io)", null, () => $("uml-import").click(), () => Boolean($("uml-import"))],
    ];
    items.push(REVIEW ? ["Leave the review view (edit)", null, () => { location.href = viewUrl(false); }]
      : ["Open the review view (read-only)", null, () => { location.href = viewUrl(true); }]);
    return items.filter(([, id, , when]) => (!id || usable($(id))) && (!when || when()))
      .filter(([label]) => !REVIEW || !/AI|plan/.test(label))
      .map(([label, , run]) => ({ label, group: "Command", run }));
  }

  function elements() {
    const kinds = { state: "State", transition: "Transition", class: "Class" };
    return [...document.querySelectorAll(".outline button[data-id]")].flatMap((b) => {
      const kind = kinds[b.dataset.id.split(":")[0]], go = () => b.click();
      const items = [{ label: b.textContent, group: kind, run: go }];
      if (kind !== "Class" && !REVIEW) items.push({ label: `Ask the AI about ${b.textContent.replace(/ \(initial\)$/, "")}`, group: "Ask", run: () => { go(); $("chat-input").focus(); } });
      return items;
    });
  }

  let paletteItems = [], paletteActive = 0, paletteShown = [];

  function palette() {
    const dialog = el("dialog", undefined, { id: "palette-dialog", class: "palette-dialog", "aria-label": "Commands" });
    const input = el("input", undefined, { id: "palette-input", type: "text", role: "combobox", "aria-autocomplete": "list", "aria-controls": "palette-list",
      "aria-expanded": "true", autocomplete: "off", placeholder: "Type a command, a state or a transition…", "aria-label": "Command or element" });
    const list = el("ul", undefined, { id: "palette-list", role: "listbox", "aria-label": "Results" });
    const keys = el("p", `${MOD}K commands · J/K and Space review an AI plan · Tab fills the next blank · ${MOD}Enter sends`, { class: "muted small palette-keys" });
    dialog.append(input, list, keys);
    document.body.append(dialog);
    input.addEventListener("input", () => filter(input.value));
    input.addEventListener("keydown", (event) => {
      if (event.key === "ArrowDown" || event.key === "ArrowUp") {
        event.preventDefault();
        paletteActive = (paletteActive + (event.key === "ArrowDown" ? 1 : paletteShown.length - 1)) % Math.max(1, paletteShown.length);
        drawList();
      } else if (event.key === "Enter") {
        event.preventDefault();
        run(paletteActive);
      }
    });
    dialog.addEventListener("click", (event) => { if (event.target === dialog) dialog.close(); });
    const opener = el("button", undefined, { id: "palette-open", type: "button", class: "quiet palette-open command-center", title: "Commands: every command and element",
      "aria-label": "Commands", "aria-keyshortcuts": isMac ? "Meta+K" : "Control+K" });
    opener.append(el("span", "Search commands, diagrams and elements"), el("kbd", `${MOD}K`)); // the title bar's command center (ADR-0173)
    opener.addEventListener("click", openPalette);
    (document.querySelector(".bar .brand") || document.body).after(opener);
    document.addEventListener("keydown", (event) => {
      if ((event.ctrlKey || event.metaKey) && !event.altKey && event.key.toLowerCase() === "k") { event.preventDefault(); openPalette(); }
    });
  }

  function openPalette() {
    const dialog = $("palette-dialog");
    if (dialog.open) return;
    paletteItems = [...commands(), ...elements()];
    $("palette-input").value = "";
    filter("");
    dialog.showModal();
    $("palette-input").focus();
  }

  function filter(query) {
    const words = query.toLowerCase().split(/\s+/).filter(Boolean);
    paletteShown = paletteItems.filter((item) => words.every((w) => `${item.group} ${item.label}`.toLowerCase().includes(w))).slice(0, 40);
    paletteActive = 0;
    drawList();
  }

  function drawList() {
    const list = $("palette-list");
    list.replaceChildren(...paletteShown.map((item, i) => {
      const li = el("li", undefined, { role: "option", id: `palette-${i}`, "aria-selected": String(i === paletteActive) });
      li.append(el("span", item.label), el("span", item.group, { class: "kind-tag" }));
      li.addEventListener("click", () => run(i));
      return li;
    }));
    if (!paletteShown.length) list.append(el("li", "Nothing matches.", { class: "muted empty" }));
    $("palette-input").setAttribute("aria-activedescendant", paletteShown.length ? `palette-${paletteActive}` : "");
    const current = $(`palette-${paletteActive}`);
    if (current) current.scrollIntoView({ block: "nearest" });
  }

  function run(i) {
    const item = paletteShown[i];
    if (!item) return;
    $("palette-dialog").close();
    item.run();
  }

  function start() {
    if (!view() || document.body.dataset.ready !== "true" || document.body.dataset.assist) return;
    document.body.dataset.assist = "ready";
    reviewView();
    authority();
    composer();
    palette();
    $("chat-log").addEventListener("keydown", reviewKeys);
    new MutationObserver(markPlans).observe($("chat-log"), { childList: true });
    document.addEventListener("playide:select", (event) => suggestions(event.detail));
  }

  document.addEventListener("playide:ready", start);
  start(); // in case the model loaded before this script ran
})();
