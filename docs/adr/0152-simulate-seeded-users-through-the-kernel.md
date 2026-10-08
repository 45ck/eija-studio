# ADR-0152: Simulate seeded users through the kernel and paint where they went

* Status: accepted for the state-machine slice
* Date: 2026-10-08
* Lane: PlayIDE (owner direction, 8 October 2026)

## Context and problem statement

The owner asked for PlayIDE to feel like a simulation game for software engineers: build a system, watch it run and find problems fast. [ADR-0151](0151-playide-canvas-and-build-and-run.md) shows the model and runs the app built from it, but one person clicking through an app finds problems slowly. Engineers need to see, on the diagram itself, where many users succeed, where they are refused and where records pile up.

## Decision drivers

* Every simulated step must be the kernel's own decision, so a simulation can never disagree with the built app.
* Runs must replay exactly from a seed, so a finding can be shown to someone else.
* The output is synthetic and must say so. It is not a measurement of people.
* The page paints counts and selects elements. It holds no rules.

## Considered options

* A seeded loop in the application layer that calls `runtime.initialise` and `runtime.execute` against an in-memory unit of work (chosen).
* SimPy (MIT) discrete-event simulation.
* Hypothesis (MPL-2.0) stateful testing, already a test dependency.
* Animating tokens in the browser from the model alone, as bpmn-js-token-simulation (MIT) does.

## Decision outcome

Chosen option: a seeded loop through the kernel, in `application/simulation.py`.

* `simulate(pack, model, seed=1, steps=500)` picks a fixture actor at each step. The actor either starts a record or picks a record their role can work on. They usually try an action their role is offered from that record's state. With small fixed chances they try any declared action instead (a slip), or act on an out-of-date version (someone else got there first). Revoked and unassigned actors still try, and the kernel refuses them.
* `MemorySession` implements the kernel's unit-of-work port in memory. Choices come from SHA-256 of the seed and a draw counter, which, unlike `random.Random`, is promised to give the same sequence on every platform and Python version. Records are named R1, R2 … in creation order, so the report never depends on the kernel's random ids and a seed replays exactly.
* The report (`eija.simulation.v1`) contains totals, refusal codes, per-transition commits and refusals, per-state "entered" and "here now" counts, effect counts, the first 60 steps in order, and findings. Findings are: transitions that never succeeded, states no record reached, states where records got stuck, and the most-refused transitions. Each finding names a diagram element.
* `POST /api/play/simulate` takes `{case_id?, model?, seed, steps}`. Like Build & run, it refuses with `MODEL_CHANGED` if the page shows an older model. PlayIDE's **Simulate** button paints the diagram: edge width shows commits, dashed amber edges never succeeded, state fill shows how many records are there now, and labels show counts. It also lists findings (click to select the element) and a run log. **Replay** steps through the log on the diagram, faster when reduced motion is requested.

### Consequences

* Good: the diagram shows where the system works and where people are blocked, and every number is the kernel's answer. `tests/test_simulation.py` replays a trace against a fresh kernel session and requires the same outcome at every step.
* Good: a run is reproducible from its seed and model hash.
* Bad: the users are uniform-random fixture actors, not a model of real behaviour or load. The limits field and the page say so.
* Bad: there is no notion of time, so "overdue" and similar timing paths are reached only through their explicit actions.
* Revisit when: behaviour profiles per role, time or load are wanted. SimPy fits a timed model, and recorded real usage would replace the random choice.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| SimPy | Its value is simulated time and resource queues; the model has neither yet, and a seeded step loop is a few lines | Adopt when timed or load simulation is added |
| Hypothesis stateful testing | Built to find and shrink failing examples in tests, not to report a reproducible usage picture to a person; it is a test-only dependency | Keep for property tests of the kernel |
| bpmn-js-token-simulation | Pattern adopted (tokens moving over the diagram), code not: it interprets BPMN in the browser, which would be a second interpreter | — |
