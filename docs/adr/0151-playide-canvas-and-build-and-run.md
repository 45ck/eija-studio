# ADR-0151: PlayIDE canvas with Build & run of the live app

* Status: accepted for the state-machine slice
* Date: 2026-10-08
* Lane: PlayIDE (owner direction, 8 October 2026)

## Context and problem statement

The owner wants EIJA to feel like "UML you can trust to build apps": a visual, mouse-driven IDE (named PlayIDE) where a UML-literate engineer designs a system and immediately runs and tests it in place. [ADR-0150](0150-build-apps-from-the-model-with-a-kernel-oracle.md) made `eija build` turn the workflow model into an app checked against the kernel. Nothing in the IDE yet drew the model in UML notation or let the user run what they drew.

## Decision drivers

* Proper UML notation on a professional diagram engine, not a hand-written canvas.
* Reuse open-source engines; write only adapters ([ADR-0016](0016-oss-first-adapters-not-engines.md)).
* The page draws only what the server returns. Every rule stays in the Python kernel; the browser is not a second interpreter.
* An app that fails its kernel conformance is never started, and an older app is never left running as if it were the current model's.
* The Studio's strict page CSP (no `unsafe-inline`, no `unsafe-eval`) stays in force.

## Considered options

* maxGraph (draw.io's engine, Apache-2.0) for the canvas, laid out by the bundled Dagre (chosen).
* tldraw (needs a paid licence key for production use), React Flow (MIT, but brings React and has no UML shapes), JointJS (core MPL-2.0; UML shapes and editing tools in the paid JointJS+), GoJS (commercial), bpmn-js (licence requires its watermark; BPMN, not UML).
* Extending the existing Dagre/SVG canvas (`canvas.js`): no shape library, ports or palette to grow into the drag-and-drop editor.
* Running the built app inside the Studio process instead of a separate process.

## Decision outcome

Chosen option: maxGraph for the canvas, and Build & run as a separate local process.

* `GET /play` serves `play.html`: an outline (states, transitions, roles), a maxGraph canvas in UML state-machine notation (initial pseudostate, rounded states, transitions labelled `action [role]`) and an inspector. Pan, zoom, fit and dragging states work. Arrangement is not saved yet.
* `POST /api/play/build` (session token required, like every `/api/` route) builds the active model, or a case's candidate when `case_id` is given, with `build_into` from ADR-0150 into `<workspace>/apps/<model hash>`. It runs the kernel conformance tests and starts `run.py` on a free 127.0.0.1 port only on `PASS`. One app runs at a time: building another model stops the previous one, a `FAIL` stops any running app, and the Studio stops it on exit.
* Only `/play` gets `frame-src 'self' http://127.0.0.1:*` so it can frame the app; every other page keeps `frame-src 'self'`. The generated app allows framing only by loopback origins.
* maxGraph 0.25.0 is vendored unmodified as an esbuild IIFE (`resources/web/vendor/maxgraph.min.js`, licence and npm integrity in `maxgraph.VENDOR.json`), served from the existing exact vendor allowlist.

### Consequences

* Good: a user sees the model as a UML state machine and, with one click, a live app built from it beside the diagram, with a score that is the real conformance count.
* Good: the app process has no access to the Studio's database or token; it reads only its own build directory.
* Bad: the canvas is read-only for the model. Typed edits from the canvas, palettes and other UML diagram kinds are later steps.
* Bad: maxGraph is pre-1.0, so its API may change; the version is pinned and the adapter is one file.
* Revisit when: the canvas starts editing the model (it must emit the existing typed transactions), or when more than one app needs to run at once.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| maxGraph | Adopted as the diagram engine | Upgrade the pinned bundle; the adapter is `play.js` |
| Dagre (already vendored) | Adopted for automatic layout; maxGraph's own layouts do not route a state machine as cleanly | ELK (elkjs, EPL-2.0) if larger diagrams need it |
| tldraw, JointJS+, GoJS, bpmn-js | Licence keys, paid tiers or required watermarks | — |
| Process managers (supervisor, honcho) | One child process with start, health and stop needs no daemon | Use one if several apps must run at once |
