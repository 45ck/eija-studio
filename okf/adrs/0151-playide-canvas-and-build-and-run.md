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
  sha256: 71f49b3139c401501992703d147ea3e24c7083333e7badf22c6577dddd2b9ad5
notes_baseline: 27ee781b5a16246c4e47fc3f67e58c46cb3716a2d33799114a1dc406b90d81f3
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
> * `POST /api/play/build` (session token required, like every `/api/` route) builds the active model, or a case's candidate when `case_id` is given, with `build_into` from ADR-0150 into `<workspace>/apps/<model hash>`. It runs the kernel conformance tests and starts `run.py` on a free 127.0.0.1 port only on `PASS`. One app runs at a time: building another model stops the previous one, a `FAIL` stops any running app, and the Studio stops it on exit.
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
<!-- okf:generated:end links -->
