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
| D-06 | Minor | `play-run.js` `run`, `step` | Run and Step load the run log before starting. If Stop or Restart was pressed, or the model was redrawn, while it loaded, the run started anyway. Pressing Run twice started two timers, so the run moved at twice the speed. | Browser | Fixed |
| D-07 | Minor | `application/simulation.py` `_attempt` | A slip, where a user tries an action that does not leave the record's state, is counted against the first transition that action labels. Simulate then shows "✗ n" refusals, and the finding "refused n times, mostly INVALID_TRANSITION", on a transition from another state. A breakpoint on that transition also stops on slips made from other states. The game layer already draws these slips on the state, not the transition. | Code | Logged |
| D-08 | Observation | `play.js` `checksNow` | "AI steps checked" and "Diagrams agree" show green when there is no AI plan or no change, so nothing was checked. Together with the screens check, which runs by itself, three of the five parts are green before anyone checks anything. | Code | Logged |
| D-09 | Minor | `play-tests.js` `run` | When a test run's result is dropped because the model changed, the summary keeps saying "Running every test through the kernel…" until the tab is shown again. With two runs in flight, the first one to finish enables the Run button while the other is still running. | Code | Logged |
| D-10 | Minor | `application/access.py` `access` | The permissions a plan adds or removes are compared by state, role, action and target. A plan that only adds or drops an `actor_assigned` guard, or a guard over values, shows no change. | Code | Logged |

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

Regression tests are in `tests/test_play_check_in_place.py`. One browser test, opt-in with `EIJA_BROWSER_TESTS=1`,
walks D-01, D-02, D-03 and D-06 in Chromium, and it fails on `main` before the fix. The Python tests pin D-05, with a
negative control.

D-07 to D-10 are left for follow-up. D-07 and D-10 change report formats (`eija.simulation.v1`, `eija.access.v1`)
that other views read. D-08 is a product choice about what counts as checked.
