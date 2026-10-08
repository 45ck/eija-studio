---
type: Architecture Decision Record
title: 'ADR-0152: Simulate seeded users through the kernel and paint where they went'
description: 'The owner asked for PlayIDE to feel like a simulation game for software engineers: build a system, watch it run and find problems fast.'
resource: repo://docs/adr/0152-simulate-seeded-users-through-the-kernel.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0152-simulate-seeded-users-through-the-kernel.md
  title: 0152-simulate-seeded-users-through-the-kernel.md
  hash_method: lf-sha256-v1
  sha256: c454a8c4099123937982ef09e25098f76c89912a45f22fa4a51432e076d4180a
notes_baseline: 86ea3cefccd2434c0edf157e0cb2f5a37ed2aa95eaa4ca45425234f830bfa877
---

# ADR-0152: Simulate seeded users through the kernel and paint where they went

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted for the state-machine slice |
| Date | 2026-10-08 |
| Lane | PlayIDE (owner direction, 8 October 2026) |
| Source | `repo://docs/adr/0152-simulate-seeded-users-through-the-kernel.md` |

## Decision outcome (verbatim)

> Chosen option: a seeded loop through the kernel, in `application/simulation.py`.
>
> * `simulate(pack, model, seed=1, steps=500)` picks a fixture actor at each step. The actor either starts a record or picks a record their role can work on. They usually try an action their role is offered from that record's state. With small fixed chances they try any declared action instead (a slip), or act on an out-of-date version (someone else got there first). Revoked and unassigned actors still try, and the kernel refuses them.
> * `MemorySession` implements the kernel's unit-of-work port in memory. Choices come from SHA-256 of the seed and a draw counter, which, unlike `random.Random`, is promised to give the same sequence on every platform and Python version. Records are named R1, R2 … in creation order, so the report never depends on the kernel's random ids and a seed replays exactly.
> * The report (`eija.simulation.v1`) contains totals, refusal codes, per-transition commits and refusals, per-state "entered" and "here now" counts, effect counts, the first 60 steps in order, and findings. Findings are: transitions that never succeeded, states no record reached, states where records got stuck, and the most-refused transitions. Each finding names a diagram element.
> * `POST /api/play/simulate` takes `{case_id?, model?, seed, steps}`. Like Build & run, it refuses with `MODEL_CHANGED` if the page shows an older model. PlayIDE's **Simulate** button paints the diagram: edge width shows commits, dashed amber edges never succeeded, state fill shows how many records are there now, and labels show counts. It also lists findings (click to select the element) and a run log. **Replay** steps through the log on the diagram, faster when reduced motion is requested.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://tests/test_simulation.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0151: PlayIDE canvas with Build & run of the live app](/adrs/0151-playide-canvas-and-build-and-run.md) - The owner wants EIJA to feel like "UML you can trust to build apps": a visual, mouse-driven IDE (named PlayIDE) where a UML-literate engineer designs a system…

## Referenced by

* [ADR-0160: A run bar with breakpoints, over one seeded run the kernel decides](/adrs/0160-run-bar-with-breakpoints-over-a-seeded-run.md) - The owner asked for "a similar thing to Visual Studio where it has play and stop etc": run the system, pause it, step through it and stop it, from inside PlayI…
* [ADR-0173: PlayIDE's workbench shell, after Visual Studio, VS Code, Cursor and draw.io](/adrs/0173-playide-workbench-shell.md) - After watching the recorded tours, the owner said there was "too much going on in sidebar" and that it "feels weird", and asked to "make playIDE really good, c…
<!-- okf:generated:end links -->
