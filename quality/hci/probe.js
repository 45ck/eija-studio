/* In-page measurement probe, installed as a Playwright init script (CDP, so it is not subject to
 * the Studio's `script-src 'self'` Content-Security-Policy, which is left intact).
 *
 * It only OBSERVES: it never clicks, types or mutates the page. All numbers are raw facts about the
 * rendered DOM; the laws are applied in Python (quality/hci/analysis.py).
 */
(() => {
  "use strict";
  if (window.__hci) return;
  const H = (window.__hci = { interactions: [], lastMutation: 0, mutations: 0 });
  const now = () => performance.now();

  // --- Doherty: click -> DOM-update latency ------------------------------------------------
  new MutationObserver(() => {
    const t = now();
    H.lastMutation = t;
    H.mutations += 1;
    const open = H.interactions[H.interactions.length - 1];
    if (open && open.muts.length < 400) open.muts.push(t);
  }).observe(document, { subtree: true, childList: true, attributes: true, characterData: true });

  const describe = (el) => {
    if (!el || !el.tagName) return "";
    return el.tagName.toLowerCase() + (el.id ? "#" + el.id : "");
  };
  // `click` in the capture phase fires for mouse clicks and for Enter/Space activation (detail 0).
  document.addEventListener(
    "click",
    (e) => {
      H.interactions.push({ t0: now(), target: describe(e.target), kind: e.detail === 0 ? "keyboard" : "pointer", muts: [] });
    },
    true
  );

  H.waitQuiet = (quietMs, timeoutMs) =>
    new Promise((resolve) => {
      const started = now();
      const tick = () => {
        const busy = document.body.hasAttribute("aria-busy");
        const quiet = now() - H.lastMutation >= quietMs;
        if (!busy && quiet && now() - started >= quietMs) return resolve({ ok: true, waited: now() - started });
        if (now() - started > timeoutMs) return resolve({ ok: false, waited: now() - started });
        setTimeout(tick, 10);
      };
      tick();
    });

  H.lastInteraction = () => {
    const i = H.interactions[H.interactions.length - 1];
    if (!i) return null;
    return {
      target: i.target,
      kind: i.kind,
      first_feedback_ms: i.muts.length ? i.muts[0] - i.t0 : null,
      settled_ms: i.muts.length ? i.muts[i.muts.length - 1] - i.t0 : null,
      mutation_batches: i.muts.length,
    };
  };

  // --- geometry ------------------------------------------------------------------------------
  const INTERACTIVE = 'a[href],button,input:not([type="hidden"]),select,textarea,summary,[role="button"],[tabindex]:not([tabindex="-1"])';
  const rectOf = (el) => {
    const r = el.getBoundingClientRect();
    return { x: r.left, y: r.top, w: r.width, h: r.height };
  };
  const layoutShown = (el) => {
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) return false;
    const s = getComputedStyle(el);
    return s.visibility !== "hidden" && s.display !== "none" && parseFloat(s.opacity) !== 0;
  };
  // A nonempty layout box can be completely outside an independently scrolling pane.
  // Intersect its ancestors' overflow clips before calling it visible. Document viewport
  // clipping remains a separate scope decision so the page/viewport distinction survives.
  const visibleBounds = (el) => {
    const raw = el.getBoundingClientRect();
    let left = raw.left, right = raw.right, top = raw.top, bottom = raw.bottom;
    for (let parent = el.parentElement; parent && parent !== document.body && parent !== document.documentElement; parent = parent.parentElement) {
      const style = getComputedStyle(parent);
      const clipX = /^(auto|scroll|hidden|clip)$/.test(style.overflowX);
      const clipY = /^(auto|scroll|hidden|clip)$/.test(style.overflowY);
      if (!clipX && !clipY) continue;
      const box = parent.getBoundingClientRect();
      const sx = parent.offsetWidth ? box.width / parent.offsetWidth : 1;
      const sy = parent.offsetHeight ? box.height / parent.offsetHeight : 1;
      const x = box.left + parent.clientLeft * sx, y = box.top + parent.clientTop * sy;
      if (clipX) { left = Math.max(left, x); right = Math.min(right, x + parent.clientWidth * sx); }
      if (clipY) { top = Math.max(top, y); bottom = Math.min(bottom, y + parent.clientHeight * sy); }
      if (right <= left || bottom <= top) return null;
    }
    return {left, right, top, bottom, width: right - left, height: bottom - top};
  };
  const shown = (el) => layoutShown(el) && visibleBounds(el) !== null;
  const onCanvas = (r) => r.bottom + window.scrollY > 0 && r.right + window.scrollX > 0; // excludes the off-screen skip link
  const inViewport = (r) => r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < innerWidth;
  const labelOf = (el) => {
    if (!el.labels || !el.labels.length) return null;
    return el.labels[0];
  };
  const nameOf = (el) => {
    const aria = el.getAttribute("aria-label");
    if (aria) return aria.trim();
    const label = labelOf(el);
    if (label && label.textContent.trim()) return label.textContent.trim().replace(/\s+/g, " ").slice(0, 60);
    const text = (el.innerText || el.value || el.getAttribute("placeholder") || "").trim().replace(/\s+/g, " ");
    return (text || el.id || el.tagName.toLowerCase()).slice(0, 60);
  };
  // A checkbox/radio/field and its <label> are one pointer target: the label activates the control.
  const effectiveBox = (el) => {
    const own = rectOf(el);
    const label = labelOf(el);
    if (label && shown(label) && (el.type === "checkbox" || el.type === "radio")) {
      const l = rectOf(label);
      if (l.w * l.h > own.w * own.h) return { box: l, viaLabel: true };
    }
    return { box: own, viaLabel: false };
  };
  const selectorOf = (el) => {
    if (el.id) return "#" + el.id;
    const parts = [];
    let node = el;
    while (node && node.nodeType === 1 && parts.length < 4) {
      let part = node.tagName.toLowerCase();
      if (node.id) { parts.unshift("#" + node.id); break; }
      const parent = node.parentElement;
      if (parent) {
        const same = [...parent.children].filter((c) => c.tagName === node.tagName);
        if (same.length > 1) part += ":nth-of-type(" + (same.indexOf(node) + 1) + ")";
      }
      parts.unshift(part);
      node = parent;
    }
    return parts.join(" > ");
  };

  H.targetOf = (el) => {
    const eff = effectiveBox(el);
    return {
      tag: el.tagName.toLowerCase(),
      name: nameOf(el),
      selector: selectorOf(el),
      raw: rectOf(el),
      effective: eff.box,
      via_label: eff.viaLabel,
      disabled: !!el.disabled,
    };
  };
  // Would a real pointer at (x, y) land on `el` (or on the label that activates it)?
  H.hitOk = (el, x, y) => {
    const hit = document.elementFromPoint(x, y);
    if (!hit) return false;
    const label = labelOf(el);
    return el === hit || el.contains(hit) || (!!label && (label === hit || label.contains(hit)));
  };

  // Every visible pointer target on the current view, in page coordinates (for WCAG 2.5.8).
  H.controls = () =>
    [...document.querySelectorAll(INTERACTIVE)]
      .filter((el) => shown(el) && onCanvas(visibleBounds(el)))
      .map((el) => {
        const eff = effectiveBox(el);
        const r = eff.box;
        return {
          selector: selectorOf(el),
          tag: el.tagName.toLowerCase(),
          name: nameOf(el),
          x: r.x + scrollX, y: r.y + scrollY, w: r.w, h: r.h,
          raw_w: rectOf(el).w, raw_h: rectOf(el).h,
          via_label: eff.viaLabel,
          disabled: !!el.disabled,
          in_viewport: inViewport(visibleBounds(el)),
        };
      });

  // --- Hick-Hyman: alternatives at a decision point -------------------------------------------
  H.choices = (selectors) => {
    const seen = new Set();
    for (const s of selectors) for (const el of document.querySelectorAll(s)) {
      if (el.tagName === "OPTION") { if (!el.disabled && shown(el.parentElement)) seen.add(el); continue; }
      if (shown(el) && !el.disabled) seen.add(el);
    }
    return seen.size;
  };
  H.screenChoices = () =>
    [...document.querySelectorAll(INTERACTIVE)].filter((el) => {
      if (!shown(el) || el.disabled) return false;
      const r = visibleBounds(el);
      return onCanvas(r) && inViewport(r);
    }).length;

  // --- Working memory proxy -------------------------------------------------------------------
  // HEURISTIC, not a measurement of any person's memory. controls = each visible control (including disabled)
  // (a decision/operation to keep in mind; a checkbox and its label are one). content_groups =
  // static text/heading atoms grouped by shared parent element (proximity in the DOM). Miller
  // (1956) 7+-2 and Cowan (2001) ~4 concern chunks a person holds, not pixels on screen.
  const SKIP_TAGS = new Set(["SCRIPT", "STYLE", "OPTION", "NOSCRIPT", "HEAD", "TEMPLATE"]);
  const countChunks = (scope, clipped) => {
    const visibleHere = (el) => {
      if (!layoutShown(el)) return false;
      const r = clipped ? visibleBounds(el) : el.getBoundingClientRect();
      if (!r) return false;
      if (!onCanvas(r)) return false;
      return scope === "page" ? true : inViewport(r);
    };
    let controls = 0;
    const groups = new Set();
    let atoms = 0;
    const isControl = (el) => el.matches(INTERACTIVE);
    for (const el of document.body.querySelectorAll("*")) {
      if (SKIP_TAGS.has(el.tagName)) continue;
      if (el.closest("option,script,style")) continue;
      const controlAncestor = el.parentElement && el.parentElement.closest(INTERACTIVE);
      if (controlAncestor) continue; // text inside a button/summary belongs to that control
      if (isControl(el)) {
        if (!visibleHere(el)) continue;
        controls += 1; atoms += 1;
        continue;
      }
      if (el.tagName === "LABEL" && el.control) continue; // paired with its control
      const own = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim().length > 0);
      if (!own || !visibleHere(el)) continue;
      atoms += 1;
      const parent = el.parentElement || el;
      groups.add(parent);
    }
    return { controls, content_groups: groups.size, atoms, chunks: controls + groups.size };
  };
  H.chunks = (scope) => {
    const visible = countChunks(scope, true), raw = countChunks(scope, false);
    const excluded_clipped = Object.fromEntries(Object.keys(raw).map(key => [key, raw[key] - visible[key]]));
    return {...visible, raw, excluded_clipped};
  };

  // --- keyboard -------------------------------------------------------------------------------
  H.tabbableCount = () =>
    [...document.querySelectorAll(INTERACTIVE)].filter((el) => shown(el) && !el.disabled && el.tabIndex >= 0 && onCanvas(visibleBounds(el))).length;
  H.focus = () => {
    const el = document.activeElement;
    if (!el || el === document.body || el === document.documentElement) return { tag: "body", id: "", name: "", visible_ring: false, rect: null, lost: true };
    const s = getComputedStyle(el);
    const outline = s.outlineStyle !== "none" && parseFloat(s.outlineWidth) > 0;
    const shadow = s.boxShadow && s.boxShadow !== "none";
    const r = el.getBoundingClientRect();
    return {
      tag: el.tagName.toLowerCase(), id: el.id || "", name: nameOf(el), selector: selectorOf(el),
      visible_ring: !!(outline || shadow), outline_width: parseFloat(s.outlineWidth) || 0,
      focus_visible: el.matches(":focus-visible"),
      rect: { x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height },
      in_viewport: inViewport(r), lost: false,
    };
  };
  // Supplementary non-axe check: state shown only by a CSS class (WCAG 1.3.1 / 4.1.2 need a programmatic state).
  H.visualStateOnly = () =>
    [...document.querySelectorAll(INTERACTIVE)]
      .filter((el) => shown(el) && /(^|\s)(active|selected)(\s|$)/.test(el.className) &&
        !["aria-current", "aria-selected", "aria-pressed", "aria-checked", "aria-expanded"].some((a) => el.hasAttribute(a)))
      .map((el) => selectorOf(el) + " (" + nameOf(el) + ")");
  H.geometry = () => ({ scrollX, scrollY, innerWidth, innerHeight, scrollWidth: document.documentElement.scrollWidth, scrollHeight: document.documentElement.scrollHeight });
  H.text = (selector) => { const el = document.querySelector(selector); return el ? el.textContent.trim() : null; };
  H.isVisible = (selector) => { const el = document.querySelector(selector); return !!el && shown(el); };
  H.isEnabled = (selector) => { const el = document.querySelector(selector); return !!el && !el.disabled; };
})();
