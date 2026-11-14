# Inspection: running and checking a design in place (13 November 2026)

A Fagan-style inspection of the parts of PlayIDE that run a design and check it where it is drawn: Simulate and its
replay, the run bar (Run, Pause, Step, Stop, Restart and breakpoints), the Tests tab and failures shown on the
diagram, the Laws tab, the permissions matrix and reachability question, the ripple check, and the game layer that is
meant to follow real checks.

## Scope and method

Code read line by line, against `main` at `fabfb39`:

- `src/eija_studio/resources/web/play-run.js`, `play-tests.js`, `play-laws.js`, `play-access.js`, `play-game.js`
- the Simulate, checks ring and award parts of `src/eija_studio/resources/web/play.js`
- `src/eija_studio/application/simulation.py`, `scenario_run.py`, `access.py`, `ripple.py`, and the routes for them in
  `src/eija_studio/interfaces/play.py`

The checklist:

1. Does the page ever show an answer that differs from what the kernel said?
2. Can a check show green when nothing ran?
3. Can a result made for one model stay on screen after the model changes?
4. Is every game moment and point backed by a real check?
5. Do pause, step, stop and restart happen in the right order, including while a request is still loading?
6. Does a replay show the same steps as the run it replays?

The important defects were then confirmed in Chromium against a library-loan pack that uses the newer kernel
features (`tests/test_play_kernel_features.py::kernel_loan`: initiators, an action from two states, a separation of
duties law, a guard over values and a built reference).

## Defects

| ID | Severity | Where | Defect | Confirmed | Status |
|----|----------|-------|--------|-----------|--------|
| D-01 | Major | `play-run.js` `stopAt`, log list, `status` | The run bar mixes up places in the run log with the run's step numbers. They differ whenever a turn logs nothing, which happens in any model with initiators (ADR-0231): a user who may not start a record has nothing to work on. With seed 1 the log has 496 entries for 500 steps. The run then pauses on the wrong step. The status said "Paused at step 15: breakpoint on Returned", but the panel and the diagram showed step 19, a refused CheckOut. Clicking a step in the log opened a different step. | Browser | Fixed |
| D-02 | Major | `play.js` `simulate` | A simulation that returns after the model on screen has changed was still shown. If the new model had a state the old one did not, painting it threw an error. The panel then said "Simulation refused (ERROR): Cannot read properties of undefined", although the kernel had refused nothing. Its traffic also played on the new diagram. Build & run already guarded against this case. | Browser | Fixed |
| D-03 | Major | `play-laws.js` `showFor` | "Inspect its laws", on a step the kernel refused, looked for laws whose subject is `transition:<id>`. The law proof names subjects `action:<name>` and `state:<name>`, so nothing ever matched. It always said "No law subject explicitly links to this transition", even for Return, which `four-eyes` and `clerk-never-takes-returns` govern. | Browser | Fixed |
| D-04 | Minor | `play-laws.js` `transitionFor`, `cellsOf` | When one action leaves several states (ADR-0232), "Show this run" painted each counterexample step on the first transition with that action, not on the one that leaves the step's state. "Show what it governs" also lit only one of them. | Code | Fixed |
| D-05 | Minor | `application/access.py` `reach` | Reachability ignored who may start a record. "Can a record reach Requested without a Member?" answered Yes for a model where only Members may start one. The kernel refuses anyone else with ROLE_CANNOT_START. The path replay also started its record with no role. | Test | Fixed |
| D-06 | Minor | `play-run.js` `run`, `step`, `buttons` | Run and Step load the run log before starting. If Stop (Shift+F5), Restart or a redraw happened while it loaded, the run started anyway. The Stop button was disabled while the log loaded. Pressing Run twice started two timers, so the run moved at twice the speed. | Browser | Fixed |
| D-07 | Minor | `application/simulation.py` `_attempt`, `_stop` | A slip, where a user tries an action that does not leave the record's state, was counted against the first transition that action labels. Simulate then showed "✗ n" refusals on a transition from another state; MarkOverdue showed ✗ 60 on library loan, all of them slips from other states. A breakpoint on that transition also stopped on these slips. | Browser | Fixed |
| D-08 | Minor | `play.js` `checksNow`, `renderHealth` | "AI steps checked" and "Diagrams agree" showed green when there was no AI plan or no change, so nothing had been checked. A fresh page read "2/5 checks" before anyone had checked anything. | Browser | Fixed |
| D-09 | Minor | `play-tests.js` `run` | When two test runs were in flight, the first to return re-enabled Run while the summary still said "Running every test through the kernel…". A result dropped because the model changed left that summary in place. | Browser | Fixed |
| D-10 | Minor | `application/access.py` `access` | The permissions a plan adds or removes were compared by state, role, action and target only. A plan that redraws CheckOut keeps that key, but it drops the guard `[renewals ≤ 3]`, and the matrix showed no change at all. | Browser | Fixed |
| D-11 | Minor | `play-laws.js` `prove` | Found while testing the D-03 fix under load. Opening the Laws tab and "Inspect its laws" each started a proof. If the tab's proof finished second, it repainted the panel and wiped out what the inspection had just said. | Browser (flaky) | Fixed |

What was clean: scenario runs (`scenario_run.py`) and the Tests tab ignore a result for a model that is no longer on
screen. The laws report does the same. Points come only from looking at AI steps, from catching a refused step, and
from building and simulating an AI change, each checked against the view it was made for. The game layer awards nothing and calls no
server, as `tests/test_play_game.py` already checks. The run bar's breakpoints are checked against the model on the
server.

## Fixes

- D-01: `play-run.js` finds a stop by the step number of the log entry the run is on. The log list and a click on it
  work in places in the log. The status line and the step counter show the run's own step numbers, out of the steps
  asked for.
- D-02: `simulate()` drops a result whose view is no longer on screen. It says so in the status bar instead of
  painting it, and it treats a late refusal the same way.
- D-03 and D-04: the Laws tab links a transition to the laws about its action. It paints a counterexample step on
  the transition that leaves that step's state, and it lights every transition of an action a law governs.
- D-05: `reach` answers UNREACHABLE when the role left out is the only one that may start a record and no signal
  from another workflow starts one (ADR-0242). It answers NOT_SHOWN when no fixture actor holds a starting role.
  Otherwise it replays the path on a record started by a starting role, or, for a workflow that receives a signal, on a
  record started the way delivering the signal starts one, and says so (found in review by Codex).
- D-06: Stop, Restart and a redraw cancel a Run or Step whose log is still loading. A second Run cancels the first.
  Stop is enabled while the log loads.
- D-07: a slip names no transition (`"transition": null` in the run log and Simulate's trace). Its refusals count
  against its state, as `states[s].slips`, and Simulate shows them on the state ("✗ n"). A stop on it names the
  state. The totals still add up: transition refusals plus slips equal the kernel's refusals.
- D-08: a part with nothing to check is marked not applicable. It shows "–" and grey on the ring, it is left out of
  the "n/m checks" count, and it neither passes nor blocks.
- D-09: only the newest test run fills the Tests panel and re-enables Run. A run whose model changed runs again on
  the model shown, or says that it will run when Tests opens.
- D-10: the permissions diff also compares what each permission depends on (assigned only, guards over values). A
  permission kept on other conditions is listed under `changes.changed`, with its conditions before and after, and is
  tagged "changed" in the matrix.
- D-11: the Laws tab runs one proof per model and draft at a time, and every caller waits for that one.

Regression tests are in `tests/test_play_check_in_place.py`. One browser test, opt-in with `EIJA_BROWSER_TESTS=1`,
walks D-01, D-02, D-03, D-06 and D-08 in Chromium, and it fails on `main` before the fix. The Python tests pin D-05, D-07 and D-10, with
negative controls.

## Before and after

Screenshots of each fix in the running app, taken from `main` before it and from this branch after it, on the
library-loan pack with the newer kernel features. They are in `docs/assets/inspection-2026-11-13/`
(`d01-before.png`, `d01-after.png`, and so on).
