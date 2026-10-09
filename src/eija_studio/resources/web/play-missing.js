// What's missing (ADR-0216): one list across every model and view of what the system shown still lacks, so whether
// you built it in chat, on the canvas or both, it says what is not ready yet. The server works it out from checks the
// IDE already runs (the screens' design check, the tests and laws run by the kernel, reachability, who takes what);
// the page only shows it. It reads the plan's accepted steps when the policy allows them, previewed or not, since
// that is the system being built, and the Tests tab's draft. Each item opens the view where it is fixed; a stale or
// missing test has a one-click fix, "Update the tests", which records them again on the model shown into the Tests
// tab's draft (kept by Save, never written to scenarios.json by itself). Each time the list is worked out the page hears
// `playide:missing` with every gap's stable id, so another part of the page can tell when one clears.
(() => {
  const $ = (id) => document.getElementById(id);
  let P = null, timer = 0, seq = 0, last = null, updated = null;
  const tests = () => (window.PlayTests ? window.PlayTests.draft() : null);
  const asked = () => {
    const steps = P.steps().map((x) => x.transaction); // the work in progress, previewed or not: what it still lacks
    const screens = P.editedScreens ? P.editedScreens() : null; // the designer's edits, which its own check reads too
    return { ...P.about(), plan: steps.length ? steps : null, screens, ...(tests() ? { scenarios: tests() } : {}) };
  };

  function refresh() {
    clearTimeout(timer);
    timer = setTimeout(load, 300);
  }

  async function load() {
    const mine = (seq += 1);
    let result;
    try {
      result = await P.api("/api/play/ready", asked());
    } catch (error) {
      if (mine === seq) $("missing-list").replaceChildren(P.el("li", `${error.code || "ERROR"}: ${error.message}`, { class: "muted small" }));
      return;
    }
    if (mine !== seq) return;
    last = result;
    render(result);
    const items = result.views.flatMap((view) => view.items.map((item) => ({ id: item.id, text: item.text, view: view.view })));
    document.dispatchEvent(new CustomEvent("playide:missing", { detail: { key: P.viewKey ? P.viewKey() : "", items } }));
  }

  // "Update the tests": the kernel records them again on the model shown; the result is the Tests tab's draft.
  async function update(button) {
    button.disabled = true;
    try {
      const result = await P.api("/api/play/tests/update", asked());
      updated = result.changes;
      window.PlayTests.edit(result.document);
      if (P.commit) P.commit("update the tests"); // undoable, and kept in this browser like any edit
    } catch (error) {
      updated = [{ change: "not updated", title: error.message }];
      refresh();
    } finally {
      button.disabled = false;
    }
  }

  function updateNote() {
    if (!updated) return null;
    const words = updated.length ? updated.map((c) => `${c.title} ${c.change}`).join("; ") : "nothing to change";
    return P.el("p", `Tests updated: ${words}. Not saved yet: Save keeps them, Reset in Tests drops them.`, { class: "missing-updated small" });
  }

  function render(result) {
    const box = $("missing"), list = $("missing-list");
    box.dataset.count = String(result.count);
    $("missing-count").textContent = result.count ? `${result.count} to do · ${result.ready} of ${result.of} views ready` : `All ${result.of} views ready`;
    list.replaceChildren(...result.views.map((view) => {
      const li = P.el("li", undefined, { class: "missing-view " + (view.ready ? "ready" : "todo"), "data-view": view.view });
      const head = P.el("button", undefined, { type: "button", class: "missing-head", title: `Open ${view.label}` });
      head.append(P.el("span", view.ready ? "✓" : "○", { class: "mark" }), P.el("span", view.label), P.el("span", view.ready ? "ready" : String(view.items.length), { class: "missing-n" }));
      head.addEventListener("click", () => P.showTab(view.view));
      li.append(head);
      if (view.items.length) {
        const items = P.el("ul", undefined, { class: "missing-items" });
        if (view.items.some((item) => item.action === "update-tests") && window.PlayTests) {
          const fix = P.el("button", "Update the tests", { type: "button", class: "missing-fix", id: "missing-update-tests",
            title: "Record the tests again on the model shown: stale ones re-recorded or dropped, new paths added. A draft you keep with Save." });
          fix.addEventListener("click", () => update(fix));
          li.append(fix);
        }
        for (const item of view.items) {
          const row = P.el("li", undefined, { class: item.kind });
          row.append(P.el("span", item.text), P.el("span", item.fix, { class: "muted small fix" }));
          items.append(row);
        }
        li.append(items);
      }
      return li;
    }));
    const note = updateNote();
    if (note) { const li = P.el("li", undefined, { class: "missing-note" }); li.append(note); list.append(li); }
  }

  function init() {
    if (P || !$("missing")) return;
    P = window.PlayIDE;
    document.addEventListener("playide:plan", refresh);
    document.addEventListener("playide:tests", refresh); // the Tests tab's draft changed
    document.addEventListener("playide:edit", refresh); // a screen, canvas or other edit to the document
    P.hooks.redraw.push(refresh);
    refresh();
  }

  window.PlayMissing = { refresh, last: () => last };
  document.addEventListener("playide:ready", init);
  if (document.body && document.body.dataset.ready === "true" && window.PlayIDE) init();
})();
