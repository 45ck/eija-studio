// What's missing (ADR-0203): one list across every model and view of what the system shown still lacks, so whether
// you built it in chat, on the canvas or both, it says what is not ready yet. The server works it out from checks the
// IDE already runs (the screens' design check, the tests and laws run by the kernel, reachability, who takes what);
// the page only shows it. It reads the plan's accepted steps when the policy allows them, previewed or not, since
// that is the system being built. Each item opens the view where it is fixed.
(() => {
  const $ = (id) => document.getElementById(id);
  let P = null, timer = 0, seq = 0, last = null;

  function refresh() {
    clearTimeout(timer);
    timer = setTimeout(load, 300);
  }

  async function load() {
    const mine = (seq += 1);
    let result;
    try {
      const steps = P.steps().map((x) => x.transaction); // the work in progress, previewed or not: what it still lacks
      result = await P.api("/api/play/ready", { ...P.about(), plan: steps.length ? steps : null });
    } catch (error) {
      if (mine === seq) $("missing-list").replaceChildren(P.el("li", `${error.code || "ERROR"}: ${error.message}`, { class: "muted small" }));
      return;
    }
    if (mine !== seq) return;
    last = result;
    render(result);
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
        for (const item of view.items) {
          const row = P.el("li", undefined, { class: item.kind });
          row.append(P.el("span", item.text), P.el("span", item.fix, { class: "muted small fix" }));
          items.append(row);
        }
        li.append(items);
      }
      return li;
    }));
  }

  function init() {
    if (P || !$("missing")) return;
    P = window.PlayIDE;
    document.addEventListener("playide:plan", refresh);
    P.hooks.redraw.push(refresh);
    refresh();
  }

  window.PlayMissing = { refresh, last: () => last };
  document.addEventListener("playide:ready", init);
  if (document.body && document.body.dataset.ready === "true" && window.PlayIDE) init();
})();
