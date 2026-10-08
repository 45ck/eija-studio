# ADR-0160: A run bar with breakpoints, over one seeded run the kernel decides

* Status: accepted
* Date: 2026-10-08
* Lane: PlayIDE (owner direction, 8 October 2026)

## Context and problem statement

The owner asked for "a similar thing to Visual Studio where it has play and stop etc": run the system, pause it, step through it and stop it, from inside PlayIDE. [ADR-0152](0152-simulate-seeded-users-through-the-kernel.md) already runs seeded simulated users through the kernel, but it only reports the totals and replays the first 60 steps. An engineer debugging a model wants what a debugger gives them: run until something interesting happens, look at the state of every record at that moment, and step on one try at a time.

## Decision drivers

* The kernel decides every step. The page must not interpret the model to move a record, or it becomes a second interpreter.
* A pause must show the run exactly as it was at that step, and the same run must come back after a reload or on someone else's machine.
* The controls and shortcuts should be the ones engineers already know from Visual Studio and VS Code.
* Breakpoints belong on UML elements, the thing the engineer is looking at, not on lines of generated code.

## Considered options

* A stateless run log: the server runs the whole seeded run through the kernel, returns every step and the steps where the breakpoints stop it, and the page moves through it (chosen).
* A server-side debug session that holds a live `MemorySession` and advances it one request at a time.
* Debug Adapter Protocol (DAP, MIT) end to end, with a debug adapter for the kernel and a DAP client in the page.
* Stepping the model in the browser, as bpmn-js-token-simulation (MIT) does for BPMN.

## Decision outcome

Chosen option: the stateless run log, because a seeded run is deterministic. Running it again from step 1 gives the same steps, so a log that the page moves through is the same as stepping a live session, with no server state to leak, expire or race.

* `application/simulation.py` gains `run_log(pack, model, seed, steps, breakpoints, break_on_refusal)`. It runs the same loop as `simulate` and returns `eija.run.v1`: every step in order (each now names its `transition`), each record's final state, and `stops`.
* A breakpoint is a diagram element. `state:<name>` stops when a record enters that state (it is created there or a transition commits into it). `transition:<id>` stops whenever someone tries that transition, whatever the kernel answers. "Break when the kernel refuses" stops at every refused attempt, like breaking on thrown exceptions. Stop reasons use DAP's words: `breakpoint`, and `exception` for a refusal with its code. Breakpoints never change the run. An element the model does not have is refused (`UNKNOWN_BREAKPOINT`), and at most 64 may be set (`TOO_MANY_BREAKPOINTS`).
* `POST /api/play/run` takes the Simulate request plus `breakpoints` and `break_on_refusal`. Like Build & run and Simulate, it refuses a model the page no longer shows (`MODEL_CHANGED`) and runs a previewed plan through the policy first. `POST /api/play/stop` stops the built app if one is running.
* The run bar in PlayIDE's header has Run/Continue (F5), Pause (F6), Step (F10), Stop (Shift+F5) and Restart (Ctrl+Shift+F5), a speed (slow, normal, fast, or straight to the next stop) and a status line. With reduced motion requested, Run goes straight to the next stop.
* While a run is on, the state machine fills in as it goes: busier transitions are thicker, states darken with the records in them now, and the current step is marked in amber (red when the kernel refused it), as a debugger marks the current line. A transition not yet taken is drawn plainly: mid-run it is not a finding.
* The Run panel shows the current step (who, which record, what they tried and the kernel's answer, and its effects), every record's state at that step (click one to select its state), the breakpoints, and the steps so far. F9 or the inspector's "Add breakpoint" sets a breakpoint on the selected state or transition; it shows as a red dot on the diagram, and clicking the dot removes it.
* Stop ends the run, restores the diagram and stops the running app. Previewing a plan or going back to the model starts the run again, keeping the breakpoints that still exist.
* The run bar lives in `resources/web/play-run.js`, which uses a small bridge (`window.PlayIDE`) that `play.js` exposes. It holds no rules: it moves a position through the server's log.

### Consequences

* Good: every step on screen is the kernel's answer for that step. `tests/test_simulation.py` checks that the log is the run Simulate counts and that stops fall exactly where the elements are reached.
* Good: no session state on the server. A paused run survives anything but a model change, and a reload reproduces it.
* Bad: the whole run (500 steps by default) is computed before the first step is shown. At about 0.1 s for 500 steps that is not noticeable; very long or timed runs would need streaming.
* Bad: the run is of simulated users, not of the built app's real HTTP traffic. Stop does stop that app, but stepping a person's clicks in the built app is not covered.
* Bad: breakpoints and the run position live in the page; they are not saved.
* Revisit when: runs need to react to the person while paused (for example "set this record's state and continue"), which needs a live session; or when the app's own requests should be stepped, which fits a DAP adapter.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| Debug Adapter Protocol (Microsoft, MIT specification) | Vocabulary adopted (continue, pause, next, restart, stop; stop reasons `breakpoint` and `exception`). A full adapter and client would need a JSON-RPC session and a DAP client in the page, for a run that is already deterministic | Write a DAP adapter over `run_log` if PlayIDE runs are to be driven from VS Code |
| VS Code debug toolbar and Visual Studio debug toolbar | Interaction pattern and shortcuts adopted (F5, F6, F10, Shift+F5, Ctrl+Shift+F5, F9, red breakpoint dots, a highlighted current step). VS Code's codicons (CC BY 4.0) were not vendored; the five icons are plain inline SVG shapes | Vendor codicons if more debug icons are needed |
| bpmn-js-token-simulation (MIT) | Pattern only, as in ADR-0152: it steps the model in the browser, which would be a second interpreter | — |
| maxGraph `CellOverlay` (Apache-2.0, already vendored) | Adopted for the breakpoint dots | — |
