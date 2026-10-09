# ADR-0208: Moments for real checks, and the run as traffic on the diagram

* Status: accepted
* Date: 2026-10-09
* Lane: PlayIDE (owner direction, 9 October 2026: PlayIDE should be "fun/gamified" while doing everything it needs to; the product vision is "City Skylines for software engineers")

## Context and problem statement

ADR-0157 gave PlayIDE a checks ring and points that reward checking, never producing. The rules were right but the feel was flat. The ring is 26 pixels wide. When a check passed, the ring changed colour without any feedback. Reaching every check on a view, the result the ring exists for, looked the same as reaching three. A step the policy caught gave the same small status-bar toast as looking at a step. A change that made the last build stale emptied two parts of the ring, and nothing said what to run again. Simulate painted its final counts at once, and the run bar changed edge colours. Neither looked like a system running.

The positioning research ("PlayIDE vs the field", from "How teams work with AI today" on) found that rewards plus instant feedback doubled how often people caught a confidently wrong AI. Its condition is that the reward goes to checking and understanding the AI's proposal, not to producing more output.

## Decision drivers

* No moment without a real result. Every animation follows an event the page sends after a server result (a check, a kernel step, a points award ADR-0157 already makes).
* No new points and no new rules. The layer awards nothing and decides nothing; it cannot make a check pass.
* Professional: no confetti, mascots or sounds. Motion is short, quiet and in the product's existing colours.
* Reduced motion turns every animation off; the information stays (notes, the next check, the ready state).
* Stay off the shared hot spots: one new module and stylesheet, and a few events from `play.js` and `play-run.js`.

## What existing tools do

| Tool | Feedback pattern | What PlayIDE takes from it |
|---|---|---|
| Cities: Skylines (proprietary game) | Traffic on the roads shows the simulation is alive; problems glow where they are | The run's real steps travel the transitions; a refusal stops on its edge with a cross |
| bpmn-js-token-simulation (MIT) | Tokens move along BPMN flows | The pattern only. It interprets BPMN in the browser, a second interpreter; here every dot is a step the kernel already decided |
| GitHub Actions, CI dashboards | A stale check is marked and re-runnable | A change that makes the build or simulation stale makes that button glow until it is run again |
| Duolingo, Octalysis framework (patterns) | Instant feedback, a clear next objective | The checks panel names the next check and has its button; nothing streak-like or loss-averse |
| canvas-confetti (ISC), anime.js (MIT), Lottie (MIT) | Celebration and animation libraries | Not adopted: confetti reads as unearned, and the motion here is a handful of CSS keyframes and one `getPointAtLength` loop |

## Considered options

* **A listening layer (`play-game.js`) over events play.js sends after real results** (chosen).
* **Animate inside `play.js`.** Rejected: `play.js` is the busiest file in the repository and several threads edit it at once.
* **New points for building, simulating or reaching every check on the model in force.** Rejected: it rewards running the buttons, not checking the AI. ADR-0157's points stand unchanged.
* **An animation library.** Rejected: the motion needed is a few keyframes, and a vendored dependency would be larger than the module.

## Decision outcome

Chosen option. `play.js` sends `playide:checks` (each check with a stable id: `ai`, `screens`, `conformance`, `ripple`, `simulated`), `playide:earn` (with a `caught` kind for a step the policy caught), `playide:simulated` and, during Replay, `playide:step`. The run bar sends `playide:step` for each single step forward; a jump straight to the next stop draws no traffic for the steps it skips. `play-game.js` listens:

* **A check passes.** Its ring part pops, and a note rises under the ring: "✓ Conformance. PASS: 373 cases checked against the kernel".
* **Every check passes on the view.** The ring turns green with one pulse, and the note says "Every check passes on this model" (or "on this change"). This happens once for each view, and never on page load.
* **A change makes a build or simulation stale.** The ring flashes amber, and the note says "Changed since the last build and simulation: run them again". **Build & run** and **Simulate** glow until they are run. A button glows only for a check that passed earlier in this page, so a fresh page does not nag.
* **The next check.** The checks panel opens with "Next:" and names the first failing check, with the page's own button where there is one ("Build & run", "Simulate", "Open Screens"). Once every check passes, it says "Ready."
* **Caught it.** When unticking an AI step turns a refused plan into one the policy allows (+3, ADR-0157), the note is larger and amber with a shield, and the plan's card pulses.
* **Traffic.** For each step the kernel decided in the run bar or in Replay, a dot travels along the drawn transition, green when the step went through and blue when a record is created. A refused step stops halfway with a red cross. A try from a state the transition does not leave flashes that state in red. After Simulate, the run's first 120 steps go by in about four seconds as overlapping traffic, and the summary counts count up. The traffic stops if the simulation is cleared or the view changes, so a dot is never drawn on a model it was not run on. These are the real log, sped up.

### Round 2: actors that are not people, the system, and what a new system still needs

* **Who acted.** A dot's shape shows the kind of actor that took the step (ADR-0210): a circle for a person, a diamond for an AI agent, a square for a timer or an external system. Its colour is still the kernel's answer. When a run includes actors that are not people, the Simulation panel shows a key under the summary.
* **The guardrail held.** When the kernel refused AI agents in a simulation, a violet note gives the count and the most common refusal code, from the run's own per-kind counts ("The kernel stopped AI agents 71 times in this run, mostly ACTOR_REVOKED").
* **The system agrees.** The System lens (ADR-0203) sends `playide:landscape` with its count of class-diagram disagreements each time it is drawn. When that count goes down for the same system, a note says how many were resolved and how many are left. When it reaches none, the ring pulses and a note says "The system's class diagrams agree now".
* **What's missing.** The greenfield start flow owns its list of what a new system still needs. It sends `playide:missing` (`key`, and `items`, each with a stable `id` and its `text`) every time the list is recomputed, and each item comes from a real check. When an item goes away under the same key, a note ticks it off. When the list empties, the ready moment says "Nothing missing: ready to build". While the list has items, the checks panel's "Next" names the first of them. There is no second list.
* A refusal from a state the transition does not leave is a small cross on the state's corner, not a ring around the whole state, so a run with many refusals does not cover the diagram.

### Consequences

* Good: what was checked, what is stale and what to run next can be seen without opening the panel. The biggest feedback goes to catching an AI step.
* Good: the run looks like a system running, and every dot is a kernel decision from the server's log.
* Good: one module and one stylesheet. Without them the page works exactly as before.
* Bad: the traffic draws only on the state machine tab, and only while it is showing. The other diagrams keep their counts.
* Bad: a note for points repeats the status bar's toast. Both are polite live regions, so a screen reader may read an award twice.
* Revisit when: a plan can be saved (issue #89), so that a view's readiness could be kept with it; or people find the traffic distracting, in which case it could become a setting.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| bpmn-js-token-simulation (MIT) | Interprets BPMN in the browser: a second interpreter, and BPMN only | Pattern adopted: tokens along the drawn flow |
| canvas-confetti (ISC), anime.js (MIT), Lottie (MIT) | Not needed for a few keyframes; confetti is the wrong register | Web Animations or CSS keyframes (browser standard) |
| SVG `getTotalLength`/`getPointAtLength` (browser standard) | Adopted | — |
| maxGraph overlay pane (Apache-2.0, already vendored) | Adopted: the dots are drawn in maxGraph's own overlay layer, on the drawn edge path | — |
