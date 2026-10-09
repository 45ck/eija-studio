// PlayIDE systems (ADR-0185): start a new system from a sketch or a template, open one made before, and save the
// work in progress to carry on later. Like VS Code's Open Recent and draw.io's new-diagram templates. The page holds
// no rules: the server checks a sketch with the kernel's own pack check before anything is created, and a reopened
// draft's steps are checked by the policy again like any plan. Saving never applies anything to the model in force.
(() => {
  const $ = (id) => document.getElementById(id);
  const query = new URLSearchParams(location.search);
  const EXAMPLE = "Open -> Triaged : Triage [Agent]\nTriaged -> Resolved : Resolve [Agent]\nTriaged -> Escalated : Escalate [Agent]\nEscalated -> Resolved : Fix [Engineer]";
  let P = null, listing = null, leaving = false, notice = "", saved = "", savedAt = 0, checkTimer = 0, checkSeq = 0, choice = "blank";
  let umlFile = { name: "", text: "" }; // "From a UML file" (ADR-0190): the file chosen, read in the page and checked by the server
  const canSave = () => !query.get("case") && query.get("view") !== "review";

  const when = (seconds) => new Date(seconds * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  const short = (path) => path.replace(/^.*?([^/\\]+[/\\][^/\\]+)$/, "…/$1");

  function setSaveState() {
    const button = $("system-save"), state = $("system-saved");
    if (!button || !P || !canSave()) return;
    const now = JSON.stringify(P.draft()), dirty = now !== saved;
    button.disabled = !dirty;
    if (dirty) notice = ""; // a reopening note lasts until the next change
    state.textContent = dirty ? "Unsaved changes" : notice || (savedAt ? `Saved ${when(savedAt)}` : "");
    state.dataset.dirty = String(dirty);
  }

  async function save() {
    if (!canSave() || !P) return;
    const draft = P.draft();
    try {
      const result = await P.api("/api/play/draft", draft);
      saved = JSON.stringify(draft);
      savedAt = result.saved;
    } catch (error) {
      $("system-saved").textContent = `Not saved (${error.code || "ERROR"}): ${error.message}`;
      return;
    }
    setSaveState();
  }

  async function reopen() {
    const { draft, moved } = await P.api("/api/play/draft");
    if (!draft || ((!draft.steps || !draft.steps.length) && !draft.screens)) { saved = JSON.stringify(P.draft()); return; }
    const result = await P.restoreDraft(draft);
    saved = JSON.stringify(P.draft());
    savedAt = draft.saved;
    const parts = [];
    if (draft.steps.length) parts.push(`${draft.steps.length} step${draft.steps.length === 1 ? "" : "s"}`);
    if (draft.screens) parts.push("your screens");
    const verdict = !result ? "" : result.legal ? " The policy allows them again." : " The policy now refuses them; see the plan.";
    const since = moved ? " The model in force has changed since." : "";
    notice = `Reopened ${parts.join(" and ")} saved ${when(draft.saved)}.${since}${verdict}`;
  }

  // The dialog: Open (recent and the systems home) and New system (a sketch, or a copy of a template).
  function item(entry, note) {
    const li = P.el("li"), button = P.el("button", undefined, { type: "button", class: "system-item", title: entry.pack });
    button.append(P.el("strong", entry.name), P.el("span", note || short(entry.pack), { class: "muted small" }));
    button.addEventListener("click", () => open(entry.pack));
    li.append(button);
    return li;
  }

  function renderOpen() {
    const box = $("systems-open-pane");
    box.replaceChildren();
    box.append(P.el("p", "", { class: "muted small", id: "systems-current" }));
    $("systems-current").append("Open now: ", P.el("strong", listing.current.name), ` (${short(listing.current.pack)})`);
    const lists = [["Recent", listing.recent, (e) => e.opened ? `opened ${new Date(e.opened * 1000).toLocaleString()}` : null],
      [`In ${short(listing.home)}`, listing.systems, null]];
    for (const [title, entries, note] of lists) {
      box.append(P.el("h3", title));
      const ul = P.el("ul", undefined, { class: "system-list" });
      for (const entry of entries) ul.append(item(entry, note && note(entry)));
      if (!entries.length) ul.append(P.el("li", title === "Recent" ? "Nothing else opened yet." : "No other systems yet. Start one under New system.", { class: "muted small" }));
      box.append(ul);
    }
    if (canSave()) {
      const clear = P.el("button", "Clear saved work on this system", { type: "button", class: "quiet small", id: "systems-clear" });
      clear.addEventListener("click", async () => { await P.api("/api/play/draft/clear", {}); saved = ""; savedAt = 0; setSaveState(); clear.textContent = "Saved work cleared"; clear.disabled = true; });
      box.append(clear);
    }
  }

  function renderNew() {
    const list = $("systems-templates");
    list.replaceChildren();
    const options = [{ id: "blank", name: "Blank, from a sketch", description: "Type the state machine as the diagram labels it; the kernel checks it as you type." },
      { id: "uml", name: "From a UML file", description: "XMI, PlantUML, Mermaid or draw.io. Its state machine and class model are checked by the kernel, and what it cannot import is listed." },
      ...listing.templates];
    for (const t of options) {
      const label = P.el("label", undefined, { class: "template" }), radio = P.el("input", undefined, { type: "radio", name: "system-template", value: t.id });
      radio.checked = t.id === choice;
      radio.addEventListener("change", () => { choice = t.id; showChoice(); check(); });
      const text = P.el("span");
      text.append(P.el("strong", t.name), P.el("span", t.states === undefined ? t.description : `${t.states} states, ${t.transitions} transitions, ${t.roles} roles. ${t.description}`, { class: "muted small" }));
      label.append(radio, text);
      list.append(label);
    }
    list.firstChild.after($("systems-sketch-box")); // the sketch sits under its own option
    list.children[2].after(umlBox()); // and the file under "From a UML file"
    $("systems-sketch-help").textContent = listing.sketch_help + ". Optional: actions: A, B and roles: C, for ones you will draw later.";
    showChoice();
  }

  function showChoice() {
    $("systems-sketch-box").hidden = choice !== "blank";
    $("systems-uml-box").hidden = choice !== "uml";
  }

  function umlBox() {
    let box = $("systems-uml-box");
    if (box) return box;
    box = P.el("div", undefined, { id: "systems-uml-box", class: "systems-uml-box" });
    const input = P.el("input", undefined, { id: "systems-uml-file", type: "file", "aria-label": "UML file",
      accept: ".xmi,.uml,.xml,.puml,.plantuml,.pu,.iuml,.wsd,.mmd,.mermaid,.md,.drawio,.dio" });
    input.addEventListener("change", async () => {
      const file = input.files[0];
      umlFile = file && file.size <= 2_000_000 ? { name: file.name, text: await file.text() } : { name: file ? file.name : "", text: "" };
      if (file && !$("systems-name").value.trim()) $("systems-name").value = file.name.replace(/\.[^.]+$/, "").replace(/[-_]+/g, " ").replace(/^./, (c) => c.toUpperCase());
      check();
    });
    box.append(input, P.el("p", "Nothing is created until you choose Create and open. The file is not kept.", { class: "muted small" }));
    return box;
  }

  // What the server read from a UML file: the same report as Import / Export, so nothing is dropped unseen.
  function importReport(report) {
    const box = P.el("div", undefined, { class: "systems-import", id: "systems-import" });
    const counts = [["read", report.mapped], ["kept or filled in", report.defaulted], ["not imported", report.unmapped]]
      .map(([what, list]) => `${list.length} ${what}`).join(", ");
    box.append(P.el("p", `Read as ${report.from}: ${counts}.`));
    const lists = window.PlayInterop ? [window.PlayInterop.entries("Not imported", report.unmapped, true),
      window.PlayInterop.entries("Kept or filled in by PlayIDE", report.defaulted, false)] : [];
    for (const list of lists) if (list) box.append(list);
    return box;
  }

  const body = (checkOnly) => ({ name: $("systems-name").value.trim() || "My system", template: choice,
    record: $("systems-record").value.trim() || "Record", sketch: $("systems-sketch").value, check_only: checkOnly,
    ...(choice === "uml" ? { uml: umlFile.text, filename: umlFile.name } : {}) });

  function check() {
    clearTimeout(checkTimer);
    checkTimer = setTimeout(async () => {
      const seq = (checkSeq += 1), verdict = $("systems-check");
      let result;
      try {
        result = await P.api("/api/play/systems/new", body(true));
      } catch (error) {
        result = { problems: [`${error.code || "ERROR"}: ${error.message}`] };
      }
      if (seq !== checkSeq) return;
      verdict.replaceChildren();
      $("systems-create").disabled = result.problems.length > 0;
      verdict.className = "systems-check " + (result.problems.length ? "bad" : "ok");
      if (result.problems.length) {
        verdict.append(P.el("p", "The kernel's pack check refuses this:"));
        const ul = P.el("ul");
        for (const p of result.problems.slice(0, 8)) ul.append(P.el("li", p));
        verdict.append(ul);
        return;
      }
      const s = result.system;
      verdict.append(P.el("p", `Checked: ${s.states.length} states (starts in ${s.initial}), ${s.transitions} transitions, roles ${s.roles.join(", ")}${s.record ? `, record class ${s.record}` : ""}. It will be saved as ${s.id}.`));
      if (result.import) verdict.append(importReport(result.import));
    }, 250);
  }

  const unsaved = () => canSave() && $("system-save") && !$("system-save").disabled;
  const leave = () => { leaving = true; location.reload(); }; // the server now serves the other system; the hash keeps the session

  async function create(event) {
    event.preventDefault();
    if (unsaved() && !confirm("You have unsaved changes on this system. Start the new one anyway?")) return;
    const button = $("systems-create");
    button.disabled = true;
    try {
      const result = await P.api("/api/play/systems/new", body(false));
      if (!result.created) { check(); return; }
      leave();
    } catch (error) {
      $("systems-check").textContent = `${error.code || "ERROR"}: ${error.message}`;
      button.disabled = false;
    }
  }

  async function open(pack) {
    if (unsaved() && !confirm("You have unsaved changes on this system. Open the other one anyway?")) return;
    try {
      await P.api("/api/play/systems/open", { pack });
      leave();
    } catch (error) {
      alert(`Could not open it (${error.code || "ERROR"}): ${error.message}`);
    }
  }

  async function showDialog(pane, start) {
    if (start) choice = start;
    listing = await P.api("/api/play/systems");
    renderOpen();
    renderNew();
    showPane(pane);
    $("systems-dialog").showModal();
    if (pane === "new") { $("systems-name").focus(); check(); }
  }

  function showPane(pane) {
    for (const key of ["open", "new"]) {
      $(`systems-tab-${key}`).setAttribute("aria-selected", String(key === pane));
      $(`systems-${key}-pane`).hidden = key !== pane;
    }
  }

  async function init(ide) {
    if (P) return;
    P = ide;
    try {
      listing = await P.api("/api/play/systems");
    } catch {
      return; // this server does not offer systems (for example a test app): the controls stay hidden
    }
    $("system-controls").hidden = false;
    $("system-menu").addEventListener("click", () => showDialog("open"));
    $("systems-close").addEventListener("click", () => $("systems-dialog").close());
    $("systems-tab-open").addEventListener("click", () => showPane("open"));
    $("systems-tab-new").addEventListener("click", () => { showPane("new"); $("systems-name").focus(); check(); });
    $("systems-sketch").value = EXAMPLE;
    for (const id of ["systems-name", "systems-record", "systems-sketch"]) $(id).addEventListener("input", check);
    $("systems-form").addEventListener("submit", create);
    if (!canSave()) { $("system-save").hidden = true; return; }
    $("system-save").addEventListener("click", save);
    document.addEventListener("keydown", (event) => {
      if ((event.ctrlKey || event.metaKey) && !event.altKey && event.key.toLowerCase() === "s") { event.preventDefault(); save(); }
    });
    await reopen();
    setSaveState();
    setInterval(setSaveState, 800);
    window.addEventListener("beforeunload", (event) => { if (!leaving && unsaved()) event.preventDefault(); });
  }

  // Commands for the palette and the demos.
  window.PlaySystems = { open: () => showDialog("open"), new: (start) => showDialog("new", start), save };
  document.addEventListener("playide:ready", () => init(window.PlayIDE));
  if (document.body && document.body.dataset.ready === "true" && window.PlayIDE) init(window.PlayIDE);
})();
