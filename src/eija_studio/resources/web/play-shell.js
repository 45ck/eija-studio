// PlayIDE shell (ADR-0173): the workbench around the diagrams, after Visual Studio, VS Code, Cursor and draw.io.
// Left, the model outline over the inspector (Solution Explorer over Properties). Centre, the diagram tabs with the
// UML palette beside the canvas (draw.io). Right, the chat on its own (Cursor's agent panel). Below the diagrams, one
// panel whose tabs are the run, the simulation and the running app (VS Code's panel); it opens on whichever has just
// started. Along the foot, a status bar. Layout only: it decides nothing, and every id stays where the page's
// scripts look for it. Each region can be hidden (Ctrl+B, Ctrl+Alt+P, Ctrl+Alt+C) and the choice is kept in this browser.
// Ctrl+J and Ctrl+L, VS Code's and Cursor's keys, belong to the browser (Downloads, the address bar), so they are not used.
"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  const KEY = "playide.shell.v1";
  const REVIEW = new URLSearchParams(location.search).get("view") === "review";
  const DOCK = [["debug", "Run"], ["sim", "Simulation"], ["run", "Running app"]];
  const LIMITS = { leftWidth: [200, 480], chatWidth: [300, 640], dockHeight: [140, 640] };
  const state = { left: true, chat: true, dock: true, leftWidth: 272, chatWidth: 380, dockHeight: 280, active: null };

  function load() {
    try {
      const kept = JSON.parse(localStorage.getItem(KEY) || "{}");
      for (const k of Object.keys(state)) if (typeof kept[k] === typeof state[k] && k !== "active") state[k] = kept[k];
    } catch { /* storage blocked: the defaults stand */ }
  }

  function save() {
    try { localStorage.setItem(KEY, JSON.stringify({ ...state, active: null })); } catch { /* not kept; still works */ }
  }

  const shown = () => DOCK.filter(([id]) => $(id) && !$(id).hidden).map(([id]) => id);

  // A region opened or closed: the diagram on show is fitted to its new size, once, as a resize of the window would.
  let layoutWas = "";
  function refit() {
    const now = ["left", "chat", "dock"].map((k) => document.body.dataset[k]).join();
    if (now === layoutWas) return;
    const first = !layoutWas;
    layoutWas = now;
    const P = window.PlayIDE;
    if (!first && P && P.fit && P.tab && ["states", "classes", "usecases", "components"].includes(P.tab())) requestAnimationFrame(() => P.fit());
  }

  // The side columns give way before the diagram does: the centre keeps at least CENTRE pixels, the chat narrows first.
  const CENTRE = 520;
  function fitted() {
    let left = state.leftWidth, chat = state.chatWidth;
    const room = window.innerWidth - CENTRE - (state.left ? left : 0);
    if (state.chat && chat > room) chat = Math.max(LIMITS.chatWidth[0], room);
    const over = window.innerWidth - CENTRE - (state.chat ? chat : 0);
    if (state.left && left > over) left = Math.max(LIMITS.leftWidth[0], over);
    return [left, chat];
  }

  // The size a region is drawn at, which can be less than the size kept when the window is narrow; a drag or a key
  // starts from what the person sees.
  function rendered(key) {
    const [left, chat] = fitted();
    return { leftWidth: left, chatWidth: chat }[key] ?? state[key];
  }

  function apply() {
    const body = document.body, available = shown();
    if (!available.includes(state.active)) state.active = available[available.length - 1] || null;
    body.dataset.left = state.left ? "open" : "closed";
    body.dataset.chat = state.chat && !REVIEW ? "open" : "closed";
    body.dataset.dock = state.dock && available.length ? "open" : "closed";
    const [left, chat] = fitted();
    for (const [k, v] of [["--left-w", left], ["--chat-w", chat], ["--dock-h", state.dockHeight]]) {
      document.documentElement.style.setProperty(k, v + "px");
    }
    for (const [id] of DOCK) {
      const tab = $("dock-tab-" + id);
      tab.hidden = !available.includes(id);
      tab.setAttribute("aria-selected", String(id === state.active));
      tab.tabIndex = id === state.active ? 0 : -1;
      $(id).classList.toggle("dock-active", id === state.active);
    }
    $("toggle-dock").disabled = !available.length;
    for (const [id, on] of [["toggle-left", state.left], ["toggle-dock", body.dataset.dock === "open"], ["toggle-chat", body.dataset.chat === "open"]]) {
      $(id).setAttribute("aria-pressed", String(on));
    }
    refit();
    save();
  }

  function reveal(id) { state.active = id; state.dock = true; apply(); }

  // ---- The bottom panel ------------------------------------------------------------------------------------------
  function dock() {
    const tabs = $("dock-tabs");
    for (const [id, name] of DOCK) {
      const tab = Object.assign(document.createElement("button"), { id: "dock-tab-" + id, type: "button", textContent: name, hidden: true });
      tab.setAttribute("role", "tab");
      tab.setAttribute("aria-controls", id);
      tab.addEventListener("click", () => reveal(id));
      tabs.append(tab);
      $(id).setAttribute("role", "tabpanel");
      $(id).setAttribute("aria-labelledby", tab.id);
      // A section the page has just shown (a run, a simulation, the running app) comes to the front, as VS Code
      // reveals the panel that has new output.
      new MutationObserver(() => { if (!$(id).hidden) reveal(id); else apply(); })
        .observe($(id), { attributes: true, attributeFilter: ["hidden"] });
    }
    tabs.addEventListener("keydown", (event) => {
      const ids = shown(), at = ids.indexOf(state.active);
      const next = { ArrowRight: at + 1, ArrowLeft: at - 1, Home: 0, End: ids.length - 1 }[event.key];
      if (next === undefined || !ids.length) return;
      event.preventDefault();
      reveal(ids[(next + ids.length) % ids.length]);
      $("dock-tab-" + state.active).focus();
    });
    $("dock-close").addEventListener("click", () => { state.dock = false; apply(); });
  }

  // ---- Splitters ---------------------------------------------------------------------------------------------------
  function splitter(id, key, axis, sign) {
    const bar = $(id), [min, max] = LIMITS[key];
    const set = (v) => { state[key] = Math.round(Math.min(max, Math.max(min, v))); apply(); bar.setAttribute("aria-valuenow", String(state[key])); };
    bar.setAttribute("aria-valuemin", String(min));
    bar.setAttribute("aria-valuemax", String(max));
    bar.setAttribute("aria-valuenow", String(state[key]));
    bar.addEventListener("pointerdown", (event) => {
      event.preventDefault();
      bar.setPointerCapture(event.pointerId);
      const start = axis === "x" ? event.clientX : event.clientY, from = rendered(key);
      const move = (e) => set(from + sign * ((axis === "x" ? e.clientX : e.clientY) - start));
      const up = () => { bar.removeEventListener("pointermove", move); bar.removeEventListener("pointerup", up); document.body.classList.remove("resizing"); };
      document.body.classList.add("resizing");
      bar.addEventListener("pointermove", move);
      bar.addEventListener("pointerup", up);
    });
    bar.addEventListener("keydown", (event) => {
      const step = event.shiftKey ? 60 : 20;
      const delta = { ArrowLeft: -step, ArrowUp: -step, ArrowRight: step, ArrowDown: step }[event.key];
      if (delta === undefined) return;
      event.preventDefault();
      set(rendered(key) + sign * delta);
    });
  }

  // ---- The checks popover ------------------------------------------------------------------------------------------
  function checksPopover() {
    const close = () => { if (!$("checks").hidden) $("health").click(); };
    document.addEventListener("keydown", (event) => { if (event.key === "Escape" && !$("checks").hidden) { close(); $("health").focus(); } });
    document.addEventListener("pointerdown", (event) => {
      if (!$("checks").hidden && !event.target.closest("#checks, #health")) close();
    });
  }

  // ---- The status bar ----------------------------------------------------------------------------------------------
  function mirror(from, to, text = (node) => node.textContent) {
    const copy = () => { $(to).textContent = text($(from)); };
    new MutationObserver(copy).observe($(from), { childList: true, characterData: true, subtree: true, attributes: true });
    copy();
  }

  function statusBar() {
    mirror("model-name", "status-model");
    const banner = $("plan-banner");
    const plan = () => { $("status-plan").hidden = banner.hidden; };
    new MutationObserver(plan).observe(banner, { attributes: true, attributeFilter: ["hidden"] });
    plan();
    document.addEventListener("playide:select", (event) => {
      const id = event.detail || "";
      $("status-selection").textContent = id ? id.replace(":", " ") : "";
    });
  }

  // ---- Diagram tabs that do not fit ---------------------------------------------------------------------------------
  // As in VS Code: the strip scrolls (the wheel scrolls it sideways), the chosen tab is scrolled into view, an edge that
  // hides tabs fades, and a "More tabs" button lists every tab, the hidden ones marked, whenever any is out of view.
  function tabOverflow() {
    const strip = document.querySelector(".stage-tools .tabs");
    if (!strip) return;
    const more = Object.assign(document.createElement("button"), { id: "tabs-more", type: "button", textContent: "»", hidden: true,
      title: "More tabs" });
    more.setAttribute("aria-label", "More tabs");
    more.setAttribute("aria-haspopup", "menu");
    more.setAttribute("aria-expanded", "false");
    const menu = Object.assign(document.createElement("div"), { id: "tabs-menu", className: "tabs-menu", hidden: true });
    menu.setAttribute("role", "menu");
    menu.setAttribute("aria-label", "Diagram tabs");
    strip.after(more, menu);
    const tabs = () => [...strip.querySelectorAll('[role="tab"]')].filter((t) => !t.hidden);
    const outOfView = (t) => t.offsetLeft < strip.scrollLeft - 1 || t.offsetLeft + t.offsetWidth > strip.scrollLeft + strip.clientWidth + 1;
    const update = () => {
      const over = strip.scrollWidth > strip.clientWidth + 1;
      more.hidden = !over;
      strip.classList.toggle("fade-start", over && strip.scrollLeft > 1);
      strip.classList.toggle("fade-end", over && strip.scrollLeft + strip.clientWidth < strip.scrollWidth - 1);
      if (!over) close();
    };
    const close = () => { menu.hidden = true; more.setAttribute("aria-expanded", "false"); };
    const open = () => {
      menu.replaceChildren(...tabs().map((t) => {
        const item = Object.assign(document.createElement("button"), { type: "button", textContent: t.firstChild ? t.firstChild.textContent : t.textContent });
        item.setAttribute("role", "menuitemradio");
        item.setAttribute("aria-checked", t.getAttribute("aria-selected") || "false");
        if (outOfView(t)) item.classList.add("hidden-tab");
        item.addEventListener("click", () => { close(); t.click(); t.focus(); });
        return item;
      }));
      menu.hidden = false;
      more.setAttribute("aria-expanded", "true");
      (menu.querySelector('[aria-checked="true"]') || menu.firstChild).focus();
    };
    more.addEventListener("click", () => (menu.hidden ? open() : close()));
    menu.addEventListener("keydown", (event) => {
      const items = [...menu.children], at = items.indexOf(document.activeElement);
      const next = { ArrowDown: at + 1, ArrowUp: at - 1, Home: 0, End: items.length - 1 }[event.key];
      if (event.key === "Escape") { event.preventDefault(); close(); more.focus(); }
      else if (next !== undefined) { event.preventDefault(); items[(next + items.length) % items.length].focus(); }
    });
    document.addEventListener("pointerdown", (event) => { if (!menu.hidden && !event.target.closest("#tabs-menu, #tabs-more")) close(); });
    strip.addEventListener("wheel", (event) => {
      if (Math.abs(event.deltaY) <= Math.abs(event.deltaX) || strip.scrollWidth <= strip.clientWidth) return;
      event.preventDefault();
      strip.scrollLeft += event.deltaY;
    }, { passive: false });
    strip.addEventListener("scroll", update);
    new ResizeObserver(update).observe(strip);
    new MutationObserver((changes) => {
      const chosen = changes.find((c) => c.attributeName === "aria-selected" && c.target.getAttribute("aria-selected") === "true");
      if (chosen && outOfView(chosen.target)) chosen.target.scrollIntoView({ block: "nearest", inline: "nearest" });
      update();
    }).observe(strip, { attributes: true, attributeFilter: ["aria-selected", "hidden"], childList: true, subtree: true, characterData: true });
    update();
  }

  // ---- Toggles and keys --------------------------------------------------------------------------------------------
  function toggles() {
    const flip = (key) => () => { state[key] = !state[key]; apply(); };
    $("toggle-left").addEventListener("click", flip("left"));
    $("toggle-dock").addEventListener("click", flip("dock"));
    $("toggle-chat").addEventListener("click", () => {
      state.chat = !state.chat;
      apply();
      if (state.chat) $("chat-input").focus();
    });
    if (REVIEW) $("toggle-chat").hidden = true;
    document.addEventListener("keydown", (event) => {
      if (!(event.ctrlKey || event.metaKey) || event.shiftKey) return;
      const keys = event.altKey ? { KeyP: "toggle-dock", KeyC: "toggle-chat" } : { KeyB: "toggle-left" };
      const id = keys[event.code];
      if (!id || $(id).hidden) return;
      event.preventDefault();
      if (!$(id).disabled) $(id).click();
    });
  }

  function start() {
    load();
    dock();
    splitter("split-left", "leftWidth", "x", 1);
    splitter("split-chat", "chatWidth", "x", -1);
    splitter("split-dock", "dockHeight", "y", -1);
    checksPopover();
    statusBar();
    toggles();
    tabOverflow();
    window.addEventListener("resize", apply);
    apply();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
