// Actual generated-app observations. This layer projects confirmed HTTP outcomes onto the existing model;
// it never interprets policy, changes meaning, submits actions, or treats model simulation as app execution.
"use strict";
const PlayLiveProtocol = (() => {
  const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  const HASH = /^[0-9a-f]{64}$/;
  const fields = new Set(["type", "nonce", "kind", "modelHash", "subjectHash", "recordId", "version", "operationId", "action", "from", "to", "actorId", "effects", "code"]);
  const short = (value) => typeof value === "string" && value.length > 0 && value.length <= 160;
  const subjectHash = (value) => value && value.format === "eija.build-subject.v1" && typeof value.digest === "string" && HASH.test(value.digest) ? value.digest : null;

  function vocabulary(value) {
    if (!value || typeof value !== "object" || Array.isArray(value) || Object.keys(value).some((key) => !["actors", "actions"].includes(key))
      || !Array.isArray(value.actors) || value.actors.length > 256 || !Array.isArray(value.actions) || value.actions.length > 256) return null;
    if (!value.actions.every((action) => short(action) && action.length <= 60) || new Set(value.actions).size !== value.actions.length) return null;
    if (!value.actors.every((actor) => actor && typeof actor === "object" && !Array.isArray(actor)
      && Object.keys(actor).length === 2 && Object.keys(actor).every((key) => ["id", "role"].includes(key))
      && short(actor.id) && actor.id.length <= 80 && short(actor.role) && actor.role.length <= 60)
      || new Set(value.actors.map((actor) => actor.id)).size !== value.actors.length) return null;
    return Object.freeze({ actors: Object.freeze(value.actors.map((actor) => Object.freeze({ id: actor.id, role: actor.role }))),
      actions: Object.freeze([...value.actions]) });
  }

  function validate(event, context) {
    if (!context || event.source !== context.source || event.origin !== context.origin) return null;
    const value = event.data;
    if (!value || typeof value !== "object" || Array.isArray(value) || Object.keys(value).some((key) => !fields.has(key))) return null;
    if (value.type !== "playide.runtime.v1" || typeof value.nonce !== "string" || !UUID.test(value.nonce) || value.nonce !== context.nonce) return null;
    if (typeof value.modelHash !== "string" || !HASH.test(value.modelHash) || value.modelHash !== context.modelHash) return null;
    if (typeof value.subjectHash !== "string" || !HASH.test(value.subjectHash) || value.subjectHash !== context.subjectHash) return null;
    if (!["committed", "refused"].includes(value.kind) || typeof value.operationId !== "string" || !UUID.test(value.operationId) || context.operations.has(value.operationId)) return null;
    if (typeof value.recordId !== "string" || !/^[0-9a-f]{32}$/.test(value.recordId) || ![value.action, value.from, value.to, value.actorId].every(short)) return null;
    if ([value.action, value.from, value.to].some((value) => value.length > 60) || value.actorId.length > 80) return null;
    if (!Number.isSafeInteger(value.version) || value.version < 0) return null;
    if (!Array.isArray(value.effects) || value.effects.length > 64 || !value.effects.every((value) => short(value) && value.length <= 80)) return null;
    const model = context.model, actor = context.actors.find((candidate) => candidate.id === value.actorId);
    if (!actor || !context.actions.includes(value.action) || !model.states.includes(value.from) || !model.states.includes(value.to)) return null;
    let transition = null, observedGap = false;
    if (value.kind === "committed") {
      if (value.code !== undefined || value.version < 1) return null;
      const last = context.versions.get(value.recordId);
      if (last !== undefined && value.version <= last) return null;
      observedGap = value.version > (last === undefined ? 1 : last + 1);
      // This matches identity and geometry, not guards or authority: the actual runtime already decided the action.
      const matches = model.transitions.filter((item) => item.action === value.action && item.from_state === value.from && item.to_state === value.to && item.role === actor.role);
      if (matches.length !== 1) return null;
      transition = matches[0].id;
    } else {
      // A refusal confirms only the failed attempt. Its state/version describe the submitted baseline,
      // not current database state after a possible concurrent update. It never paints a transition.
      if (value.from !== value.to || value.effects.length || typeof value.code !== "string" || !/^[A-Z][A-Z0-9_.]{0,79}$/.test(value.code)) return null;
    }
    return Object.freeze({ ...value, effects: Object.freeze([...value.effects]), transition, observedGap });
  }
  return Object.freeze({ validate, vocabulary, subjectHash, uuid: (value) => typeof value === "string" && UUID.test(value) });
})();
if (typeof module !== "undefined" && module.exports) module.exports = PlayLiveProtocol;

if (typeof window !== "undefined" && typeof document !== "undefined") (() => {
  const $ = (id) => document.getElementById(id), MAX_STEPS = 128, MAX_RECORDS = 256, MAX_OPERATIONS = 512;
  const NS = "http://www.w3.org/2000/svg";
  let P = null, binding = null, entries = [], cursor = -1, paused = false, replaying = false, replayTimer = 0, animation = 0, painted = [], emphasized = [];
  let versions = new Map(), operations = new Set(), ignored = 0, capacity = "";
  const frame = () => $("run-frame"), reduced = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

  function currentBuild() {
    const built = P && P.runningBuild && P.runningBuild();
    if (!built || !built.url || !built.model || $("run").hidden) return null;
    const vocabulary = PlayLiveProtocol.vocabulary(built.vocabulary);
    const subjectHash = PlayLiveProtocol.subjectHash(built.subject);
    if (!vocabulary || !subjectHash || built.subject.model_hash !== built.model) return null;
    try {
      const actual = new URL(frame().src), expected = new URL(built.url);
      actual.hash = ""; expected.hash = "";
      if (actual.href !== expected.href || actual.protocol !== "http:" || actual.hostname !== "127.0.0.1") return null;
      return { ...built, subjectHash, origin: actual.origin, url: actual.href, vocabulary, vocabularyKey: JSON.stringify(vocabulary) };
    } catch { return null; }
  }

  function fresh() {
    const built = currentBuild();
    return Boolean(binding && built && binding.key === built.key && binding.modelHash === built.model && binding.subjectHash === built.subjectHash
      && binding.url === built.url && binding.vocabularyKey === built.vocabularyKey);
  }

  function clearPaint() {
    animation += 1;
    for (const node of painted) node.remove();
    painted = [];
    for (const node of emphasized) node.classList.remove("live-edge");
    emphasized = [];
    for (const node of document.querySelectorAll(".live-arrival")) node.classList.remove("live-arrival");
  }

  function stopReplay() { clearTimeout(replayTimer); replayTimer = 0; replaying = false; }

  function connect(force = false) {
    const built = currentBuild();
    if (!built) { render(); return; }
    if (!binding || force || binding.url !== built.url || binding.modelHash !== built.model || binding.subjectHash !== built.subjectHash
      || binding.key !== built.key || binding.vocabularyKey !== built.vocabularyKey) {
      stopReplay(); clearPaint();
      binding = { url: built.url, origin: built.origin, source: frame().contentWindow, modelHash: built.model, subjectHash: built.subjectHash, key: built.key,
        vocabulary: built.vocabulary, vocabularyKey: built.vocabularyKey, nonce: crypto.randomUUID() };
      entries = []; cursor = -1; paused = false; versions = new Map(); operations = new Set(); ignored = 0; capacity = "";
    }
    binding.source.postMessage({ type: "playide.runtime.connect.v1", modelHash: binding.modelHash, subjectHash: binding.subjectHash, nonce: binding.nonce }, binding.origin);
    render();
  }

  function receive(event) {
    const built = currentBuild();
    if (!built || event.source !== frame().contentWindow || event.origin !== built.origin) return;
    if (event.data && event.data.type === "playide.runtime.ready.v1") {
      if (!Array.isArray(event.data) && Object.keys(event.data).length === 3
        && event.data.modelHash === built.model && event.data.subjectHash === built.subjectHash) connect();
      return;
    }
    if (!fresh() || capacity) return;
    const entry = PlayLiveProtocol.validate(event, { ...binding, model: P.model(), ...binding.vocabulary, versions, operations });
    if (!entry) { ignored += 1; return; }
    if (operations.size >= MAX_OPERATIONS || (!versions.has(entry.recordId) && versions.size >= MAX_RECORDS)) {
      capacity = operations.size >= MAX_OPERATIONS ? "operations" : "records";
      stopReplay(); clearPaint(); paused = true; render(); return;
    }
    operations.add(entry.operationId);
    if (entry.kind === "committed") versions.set(entry.recordId, entry.version);
    entries.push(entry);
    if (entries.length > MAX_STEPS) { entries.shift(); cursor = Math.max(0, cursor - 1); }
    if (!paused) { cursor = entries.length - 1; show(entry, true); }
    if (operations.size >= MAX_OPERATIONS) { capacity = "operations"; paused = true; stopReplay(); }
    render();
  }

  function shape(tag, attributes) {
    const node = document.createElementNS(NS, tag);
    for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, String(value));
    node.setAttribute("class", "live-traffic");
    return node;
  }

  function pathOf(id) {
    const graph = P.graph(), cell = graph && graph.getDataModel().getCell(id), view = cell && graph.getView().getState(cell);
    const node = view && view.shape && view.shape.node;
    if (!node) return null;
    let chosen = null, length = 0;
    for (const path of node.querySelectorAll("path,polyline")) {
      const size = path.getTotalLength ? path.getTotalLength() : 0;
      if (size > length) { length = size; chosen = path; }
    }
    if (!chosen || length < 4) return null;
    const points = [];
    for (let i = 0; i <= 40; i += 1) { const point = chosen.getPointAtLength(length * i / 40); points.push([point.x, point.y]); }
    return points;
  }

  function show(entry, moving) {
    clearPaint();
    if (!entry || !fresh() || P.tab() !== "states" || entry.kind !== "committed") return;
    if (P.follow) P.follow(["state:" + entry.from, "transition:" + entry.transition, "state:" + entry.to]);
    const graph = P.graph(), pane = graph && graph.getView().getOverlayPane(), points = pathOf("transition:" + entry.transition);
    if (!pane || !points) return;
    // Emphasize the rendered edge itself, beneath its existing label, rather than covering labels with a new path.
    const edge = graph.getView().getState(graph.getDataModel().getCell("transition:" + entry.transition));
    if (edge && edge.shape && edge.shape.node) { edge.shape.node.classList.add("live-edge"); emphasized.push(edge.shape.node); }
    const arrive = () => {
      // A canvas resize can replace maxGraph CellState/shape objects while the token moves. Resolve the current
      // destination at completion instead of putting an arrival mark on a detached shape from before the reflow.
      if (!fresh() || P.tab() !== "states") return;
      if (P.follow) P.follow(["state:" + entry.to]);
      const current = P.graph(), cell = current && current.getDataModel().getCell("state:" + entry.to);
      const state = cell && current.getView().getState(cell), node = state && state.shape && state.shape.node;
      if (node && node.isConnected) node.classList.add("live-arrival");
    };
    if (!moving || reduced()) { arrive(); return; }
    const dot = shape("circle", { r: 7, fill: "var(--accent)", stroke: "var(--panel)", "stroke-width": 2.5 });
    pane.append(dot); painted.push(dot);
    const generation = animation, begin = performance.now(), duration = 700;
    const tick = (now) => {
      if (generation !== animation || !fresh()) return;
      // Labels and edge coordinates may move when the outcome row changes the canvas height. Follow the path
      // actually drawn now rather than animating geometry captured before that responsive reflow.
      const current = P.graph(), track = pathOf("transition:" + entry.transition);
      if (!current || !track) { clearPaint(); return; }
      const labels = Object.values(current.getDataModel().cells).map((cell) => cell.isEdge && cell.isEdge() ? current.getView().getState(cell) : null)
        .map((view) => view && view.text && view.text.boundingBox).filter(Boolean);
      // A frame timestamp can precede the observation's performance.now() within that frame.
      // Clamp both ends so the first token position cannot index before the rendered path.
      const fraction = Math.max(0, Math.min(1, (now - begin) / duration)), along = (1 - (1 - fraction) ** 3) * (track.length - 1);
      const index = Math.min(track.length - 2, Math.floor(along)), blend = along - index;
      const x = track[index][0] + (track[index + 1][0] - track[index][0]) * blend, y = track[index][1] + (track[index + 1][1] - track[index][1]) * blend;
      dot.setAttribute("cx", String(x)); dot.setAttribute("cy", String(y));
      dot.setAttribute("opacity", labels.some((box) => x >= box.x - 5 && x <= box.x + box.width + 5 && y >= box.y - 5 && y <= box.y + box.height + 5) ? ".12" : "1");
      if (fraction < 1) requestAnimationFrame(tick); else { dot.remove(); arrive(); }
    };
    requestAnimationFrame(tick);
  }

  function row(name, value) { const term = P.el("dt", name), description = P.el("dd", value); $("live-inspector").append(term, description); }

  function render() {
    const section = $("live-trace");
    section.hidden = !binding && !entries.length;
    if (section.hidden) return;
    const available = fresh(), entry = entries[cursor];
    $("live-status").textContent = !available ? "Earlier build · rebuild to follow the model on screen"
      : replaying ? "Replaying recorded outcomes · app unchanged"
      : capacity ? "Recording paused · capacity reached"
      : paused ? `Inspecting recorded actions${cursor < entries.length - 1 ? ` · ${entries.length - 1 - cursor} newer` : ""}` : "Following actual app actions";
    $("live-recording").hidden = !capacity;
    $("live-recording").textContent = capacity ? "Later outcomes are not observed. Start a new recording to clear this history and reconnect to the current app." : "";
    $("live-reconnect").hidden = !capacity;
    $("live-reconnect").disabled = !available || (!entries.length && !capacity);
    $("live-pause").textContent = paused ? "Follow latest" : "Pause trace";
    $("live-pause").setAttribute("aria-pressed", String(paused));
    $("live-pause").disabled = !entries.length || !available || Boolean(capacity);
    $("live-replay").disabled = !entries.length || !available;
    $("live-previous").disabled = cursor <= 0;
    $("live-next").disabled = cursor >= entries.length - 1;
    $("live-show").disabled = !entry || !available;
    $("live-current").className = "live-current" + (entry && entry.kind === "refused" ? " refused" : "");
    $("live-action").textContent = entry ? entry.action : "Take an action in the local app";
    $("live-outcome").textContent = !entry ? "Only confirmed outcomes appear here." : entry.kind === "committed" ? `${entry.from} → ${entry.to}` : `Refused attempt: ${entry.code} · no commit reported`;
    $("live-meta").textContent = entry ? `${entry.actorId} · ${entry.kind === "refused" ? "attempted " : ""}version ${entry.version}` : "Fixture actors · real local database";
    $("live-inspector").replaceChildren();
    if (entry) {
      row("Record", entry.recordId); row("Actor", entry.actorId); row("Action", entry.action);
      row(entry.kind === "committed" ? "From" : "Attempted from", entry.from);
      row(entry.kind === "committed" ? "Committed to" : "Outcome", entry.kind === "committed" ? entry.to : "Refused; current state was not reported");
      row(entry.kind === "committed" ? "Confirmed version" : "Attempted version", String(entry.version));
      row("Effects", entry.effects.join(", ") || "None reported"); row("Operation", entry.operationId);
      row("Build subject", entry.subjectHash);
      row("Coverage", entry.observedGap ? "Some earlier record versions were not observed" : "Recorded outcomes; not a complete runtime history");
      if (capacity) row("Recording", "Capacity reached; later outcomes are not observed");
    }
    // Keep existing buttons so an arriving action cannot take focus away from someone inspecting the history.
    const history = $("live-steps"), retained = new Set(entries.map((entry) => entry.operationId));
    for (const button of Array.from(history.children)) if (!retained.has(button.dataset.operation)) button.remove();
    entries.forEach((item, index) => {
      let button = Array.from(history.children).find((button) => button.dataset.operation === item.operationId);
      if (!button) {
        button = P.el("button", "", { type: "button", class: item.kind });
        button.dataset.operation = item.operationId;
        button.addEventListener("click", () => inspect(entries.findIndex((entry) => entry.operationId === item.operationId)));
        history.append(button);
      }
      button.textContent = `${index + 1} · ${item.action}`;
      button.setAttribute("aria-current", String(index === cursor));
      button.title = `${item.kind === "committed" ? "Committed" : "Refused attempt"}: ${item.action}, ${item.actorId}, version ${item.version}`;
    });
  }

  function inspect(index) { stopReplay(); paused = true; cursor = Math.max(0, Math.min(entries.length - 1, index)); show(entries[cursor], false); render(); }

  function replay() {
    stopReplay(); paused = true; replaying = true;
    const sequence = entries.map((entry) => entry.operationId), key = binding.key;
    let index = 0;
    const next = () => {
      cursor = entries.findIndex((entry) => entry.operationId === sequence[index]);
      if (!fresh() || binding.key !== key || cursor < 0) { stopReplay(); render(); return; }
      show(entries[cursor], true); render();
      if (index < sequence.length - 1) replayTimer = setTimeout(() => { index += 1; next(); }, reduced() ? 400 : 950);
      else replayTimer = setTimeout(() => { stopReplay(); render(); }, reduced() ? 400 : 950);
    };
    next();
  }

  function init() {
    if (P || !window.PlayIDE || !$("live-trace")) return;
    P = window.PlayIDE;
    frame().addEventListener("load", () => connect(true));
    new MutationObserver(() => { if (!currentBuild()) { stopReplay(); clearPaint(); } render(); }).observe(frame(), { attributes: true, attributeFilter: ["src"] });
    window.addEventListener("message", receive);
    $("live-pause").addEventListener("click", () => { if (capacity || !fresh()) return; stopReplay(); paused = !paused; if (!paused) { cursor = entries.length - 1; show(entries[cursor], true); } render(); });
    $("live-previous").addEventListener("click", () => inspect(cursor - 1));
    $("live-next").addEventListener("click", () => inspect(cursor + 1));
    $("live-replay").addEventListener("click", replay);
    $("live-reconnect").addEventListener("click", () => { if (fresh()) connect(true); });
    $("live-show").addEventListener("click", () => { const entry = entries[cursor]; if (!entry || !fresh()) return; P.showTab("states"); P.select(entry.transition ? "transition:" + entry.transition : "state:" + entry.from, true); show(entry, false); });
    for (const name of ["playide:checks", "playide:edit", "playide:plan", "playide:activated"]) document.addEventListener(name, () => { if (!fresh()) { stopReplay(); clearPaint(); } render(); });
    P.hooks.redraw.push(() => { clearPaint(); if (fresh()) show(entries[cursor], false); });
    P.hooks.tab.push((tab) => { clearPaint(); if (tab === "states" && fresh()) show(entries[cursor], false); });
    window.PlayLive = Object.freeze({ snapshot: () => ({ modelHash: binding && binding.modelHash, subjectHash: binding && binding.subjectHash, fresh: fresh(), paused, replaying, cursor, ignored, capacity,
      entries: entries.map((entry) => ({ ...entry, effects: [...entry.effects] })) }) });
    connect();
  }
  document.addEventListener("playide:ready", init);
  if (document.body && document.body.dataset.ready === "true") init();
})();
