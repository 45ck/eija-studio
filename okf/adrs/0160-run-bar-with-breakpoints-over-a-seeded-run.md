---
type: Architecture Decision Record
title: 'ADR-0160: A run bar with breakpoints, over one seeded run the kernel decides'
description: 'The owner asked for "a similar thing to Visual Studio where it has play and stop etc": run the system, pause it, step through it and stop it, from inside PlayIDE.'
resource: repo://docs/adr/0160-run-bar-with-breakpoints-over-a-seeded-run.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0160-run-bar-with-breakpoints-over-a-seeded-run.md
  title: 0160-run-bar-with-breakpoints-over-a-seeded-run.md
  hash_method: lf-sha256-v1
  sha256: 6c61e889b6689102c78938ec77b659b780ea53a4374e8480f5fbe1b673a351eb
notes_baseline: 336399ac2e949e93a20aa6de1eb451be19badb2614ddba7374fe89a6889227fb
---

# ADR-0160: A run bar with breakpoints, over one seeded run the kernel decides

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-08 |
| Lane | PlayIDE (owner direction, 8 October 2026) |
| Source | `repo://docs/adr/0160-run-bar-with-breakpoints-over-a-seeded-run.md` |

## Decision outcome (verbatim)

> Chosen option: the stateless run log, because a seeded run is deterministic. Running it again from step 1 gives the same steps, so a log that the page moves through is the same as stepping a live session, with no server state to leak, expire or race.
>
> * `application/simulation.py` gains `run_log(pack, model, seed, steps, breakpoints, break_on_refusal)`. It runs the same loop as `simulate` and returns `eija.run.v1`: every step in order (each now names its `transition`), each record's final state, and `stops`.
> * A breakpoint is a diagram element. `state:<name>` stops when a record enters that state (it is created there or a transition commits into it). `transition:<id>` stops whenever someone tries that transition, whatever the kernel answers. "Break when the kernel refuses" stops at every refused attempt, like breaking on thrown exceptions. Stop reasons use DAP's words: `breakpoint`, and `exception` for a refusal with its code. Breakpoints never change the run. An element the model does not have is refused (`UNKNOWN_BREAKPOINT`), and at most 64 may be set (`TOO_MANY_BREAKPOINTS`).
> * `POST /api/play/run` takes the Simulate request plus `breakpoints` and `break_on_refusal`. Like Build & run and Simulate, it refuses a model the page no longer shows (`MODEL_CHANGED`) and runs a previewed plan through the policy first. `POST /api/play/stop` stops the built app if one is running.
> * The run bar in PlayIDE's header has Run/Continue (F5), Pause (F6), Step (F10), Stop (Shift+F5) and Restart (Ctrl+Shift+F5), a speed (slow, normal, fast, or straight to the next stop) and a status line. With reduced motion requested, Run goes straight to the next stop.
> * While a run is on, the state machine fills in as it goes: busier transitions are thicker, states darken with the records in them now, and the current step is marked in amber (red when the kernel refused it), as a debugger marks the current line. A transition not yet taken is drawn plainly: mid-run it is not a finding.
> * The Run panel shows the current step (who, which record, what they tried and the kernel's answer, and its effects), every record's state at that step (click one to select its state), the breakpoints, and the steps so far. F9 or the inspector's "Add breakpoint" sets a breakpoint on the selected state or transition; it shows as a red dot on the diagram, and clicking the dot removes it.
> * Stop ends the run, restores the diagram and stops the running app. Previewing a plan or going back to the model starts the run again, keeping the breakpoints that still exist.
> * The run bar lives in `resources/web/play-run.js`, which uses a small bridge (`window.PlayIDE`) that `play.js` exposes. It holds no rules: it moves a position through the server's log.

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

* [ADR-0152: Simulate seeded users through the kernel and paint where they went](/adrs/0152-simulate-seeded-users-through-the-kernel.md) - The owner asked for PlayIDE to feel like a simulation game for software engineers: build a system, watch it run and find problems fast.

## Referenced by

* [ADR-0170: PlayIDE asks about the selection, completes exact names, has a command palette and keyboard plan review](/adrs/0170-playide-assist-ask-complete-palette-review.md) - PlayIDE's chat proposes typed steps (ADR-0156) and rewards checking them (ADR-0157).
* [ADR-0173: PlayIDE's workbench shell, after Visual Studio, VS Code, Cursor and draw.io](/adrs/0173-playide-workbench-shell.md) - After watching the recorded tours, the owner said there was "too much going on in sidebar" and that it "feels weird", and asked to "make playIDE really good, c…
<!-- okf:generated:end links -->
