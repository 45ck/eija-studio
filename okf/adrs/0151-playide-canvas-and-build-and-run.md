---
type: Architecture Decision Record
title: 'ADR-0151: PlayIDE canvas with Build & run of the live app'
description: 'The owner wants EIJA to feel like "UML you can trust to build apps": a visual, mouse-driven IDE (named PlayIDE) where a UML-literate engineer designs a system and immediately runs and tests it in place.'
resource: repo://docs/adr/0151-playide-canvas-and-build-and-run.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0151-playide-canvas-and-build-and-run.md
  title: 0151-playide-canvas-and-build-and-run.md
  hash_method: lf-sha256-v1
  sha256: fc678aa9f733a5e74f974341d2cdaa6a18d22c796355c8f08735f457fc795949
notes_baseline: 1aa57618e85b2ace1907397b91f63570fd4e0b0bc9606d21120218e9ddc573e7
---

# ADR-0151: PlayIDE canvas with Build & run of the live app

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted for the state-machine slice |
| Date | 2026-10-08 |
| Lane | PlayIDE (owner direction, 8 October 2026) |
| Source | `repo://docs/adr/0151-playide-canvas-and-build-and-run.md` |

## Decision outcome (verbatim)

> Chosen option: maxGraph for the canvas, and Build & run as a separate local process.
>
> * `GET /play` serves `play.html`: an outline (states, transitions, roles), a maxGraph canvas in UML state-machine notation (initial pseudostate, rounded states, transitions labelled `action [role]`) and an inspector. Pan, zoom, fit and dragging states work. Arrangement is not saved yet.
> * `POST /api/play/build` (session token required, like every `/api/` route) builds the active model, or a case's candidate when `case_id` is given, with `build_into` from ADR-0150 into `<workspace>/apps/<model hash>`. The page sends the model it shows, and a request whose model is no longer the one that would be built is refused with `MODEL_CHANGED`, so the app beside the diagram is always the diagram's. It runs the kernel conformance tests and starts `run.py` on a free 127.0.0.1 port only on `PASS`. One app runs at a time: building another model stops the previous one, a `FAIL` stops any running app, and the Studio stops it on exit.
> * Only `/play` gets `frame-src 'self' http://127.0.0.1:*` so it can frame the app; every other page keeps `frame-src 'self'`. The generated app allows framing only by loopback origins.
> * maxGraph 0.25.0 is vendored unmodified as an esbuild IIFE (`resources/web/vendor/maxgraph.min.js`, licence and npm integrity in `maxgraph.VENDOR.json`), served from the existing exact vendor allowlist.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0150: Build runnable apps from the model, checked against the kernel as oracle](/adrs/0150-build-apps-from-the-model-with-a-kernel-oracle.md) - The owner's goal, stated on 8 October 2026, is "UML you can trust to build apps".

## Referenced by

* [ADR-0152: Simulate seeded users through the kernel and paint where they went](/adrs/0152-simulate-seeded-users-through-the-kernel.md) - The owner asked for PlayIDE to feel like a simulation game for software engineers: build a system, watch it run and find problems fast.
* [ADR-0154: Use case diagrams, and screens designed against the model](/adrs/0154-use-cases-and-screens-designed-against-the-model.md) - PlayIDE shows the workflow as a state machine (ADR-0151) and the data as a class diagram (ADR-0153).
* [ADR-0173: PlayIDE's workbench shell, after Visual Studio, VS Code, Cursor and draw.io](/adrs/0173-playide-workbench-shell.md) - After watching the recorded tours, the owner said there was "too much going on in sidebar" and that it "feels weird", and asked to "make playIDE really good, c…
<!-- okf:generated:end links -->
