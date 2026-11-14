# Inspection: running and checking a design in place, second pass (14 November 2026)

The second Fagan-style pass over the parts of PlayIDE that run a design and check it where it is drawn: Simulate and
its replay, the run bar, the checks ring, the Tests, Laws and Permissions tabs, reachability, the ripple check and the
game layer. The first pass ([2026-11-13](2026-11-13-INSPECTION-CHECK-IN-PLACE.md), D-01 to D-11) read the code against
one pack. This one goes where that did not:

- every sector pack, with the page's answers compared to the kernel's on `main` after #257, #258 and #261;
- late and overlapping answers treated as one class of defect, with one rule for all of them;
- design: what the checks ring and the game layer claim, and who owns the diagram when two features paint it.

## Method

1. A kernel sweep over all eleven packs (`simulate`, `run_log`, `access`, `reach` for every state and role,
   `prove_laws`, `run_scenarios`), looking for answers that contradict each other: a transition Simulate commits that
   the matrix says no one may take, a state Simulate enters that reach calls not shown, a stop with no log entry.
2. A browser sweep over all eleven packs in Chromium: open the page, Simulate, open Laws, Tests and Permissions, run to
   the first refusal, and compare every number and verdict on screen with the kernel's report for the same seed.
3. A survey of every request the run, check and lens modules make, asking of each: is the answer shown only for the
   question still on screen?
4. Line-by-line reading of the checks ring and the game layer against question 4 of the first pass's checklist: is
   every moment backed by a real check?

## Defects

| ID | Severity | Where | Defect | Confirmed | Status |
|----|----------|-------|--------|-----------|--------|
| E-01 | Major | `application/access.py` `_try`, `_replay` | The permissions matrix tried each cell on a fresh record that had not waited and linked no object. A step with a time event (ADR-0237) or one that moves a linked object (ADR-0241) was refused for every actor (TIMER_NOT_DUE, LINKED_OBJECT_REFUSED), though Simulate commits it. ai-ops showed OpenWindow, ConfirmHealthy and AutoRollback as no one's; refund-desk showed EscalateStale as no one's. Reachability then said "Not shown" for Rolling, InProduction, RolledBack and WithSupervisor, states Simulate enters. | Browser, all packs | Fixed |
| E-02 | Minor | `play-game.js` `countUp` | Simulate's counts count up. The first frame's time can come before the start the count-up read, so the eased fraction went below zero, and the summary read "-22 attempts by simulated users on -8 records: -9 went through, -13 refused by the kernel". Seen on all eleven packs. | Browser, all packs | Fixed |
| E-03 | Minor | `play.js` `checksNow`, `play-run.js` `stop` | Stop and Restart on the run bar clear the diagram. That also emptied the "Simulated" check, which then said "Not simulated since the last change" with no change made. | Browser | Fixed |
| E-04 | Minor | `application/simulation.py` `_stop`, `play-run.js` `stopText` | A stop on a slip (an action that does not leave the record's state) said "the kernel refused an action from Lodged", hiding which action. | Browser, 6 packs | Fixed |
| E-05 | Minor | `play.js` `simulate`, `play-run.js` | Simulate and the run bar paint the same diagram. Pressing Simulate during a run showed Simulate's totals in the panel ("183 went through") while the run kept repainting the diagram with its own partial counts ("Returned, 1 in"). Run after Simulate did the same the other way round. | Browser | Fixed |
| E-06 | Minor | `play-game.js` `checks` | Undoing an AI plan nobody had looked at made the "AI steps checked" part not applicable, which the game layer read as passing: it popped "✓ AI steps checked". | Browser | Fixed |
| E-07 | Minor | `play-access.js` reachability | Answers were shown in the order they arrived. Ask "Returned without a Librarian?", then "OnLoan at all?": the first answer, landing late, showed "No … without Librarian" under the second question. | Browser | Fixed |
| E-08 | Minor | `play-tests.js` `tryStep`, `play-sequence.js` `tried`, `play-missing.js` `update` | An answer written into the test draft after the model changed: the Tests recorder, the Sequences tab's add, re-record and new scenario, and "Update the tests" recorded what the kernel did on a model no longer on show. A second add during the first could also overwrite it. | Code | Fixed |
| E-09 | Minor | `play-run.js` `load`, `play.js` `loadComponents` | Run logs were not ordered: toggling breakpoints quickly could leave an older log, without the newest breakpoint, in place. The components report could be cached for a view other than the one it was asked about. | Code | Fixed |

What was clean, on every pack: Simulate's totals and each state's label match `simulate()`; each law's verdict on the
Laws tab matches `prove_laws`; the Tests summary matches `run_scenarios`; the run bar's first stop matches `run_log`;
the matrix's ✓ and ✗ counts match `access()` (after E-01). No page errors on any pack.

Looked at and kept: when an undo removes a gap the start flow listed, the game layer says it went away. The gap is gone
from the model on show, so that note is backed by the check.

## One rule for every answer

The first pass fixed this class four times, each its own way (D-02, D-06, D-09, D-11), and this pass found three more
(E-07 to E-09). The fix is one rule, in one place: `ticket(channel, also)` in `play.js`, on the bridge as
`P.ticket`. A caller takes a ticket before it asks; the answer is shown only while the ticket is current, meaning it
is the newest on its channel and the view it was asked about (model, plan, screens, and whatever `also` reads, such as
the test draft or the breakpoints) is still on show.

Simulate, Build & run, the components report, the run log, Permissions, reachability, the Tests recorder, the
Sequences tab and "Update the tests" use it. `tests/test_play_answers_follow_view.py` reads every request in the run,
check and lens modules and fails on one that neither takes a ticket nor is listed with the guard it has instead (the
chat plan, the plan preview, the ripple, the screens report, the effects view, start-up, Stop, the law proof, the test
run, the roles cache and the start flow's gap list, each with its reason).

## Fixes

- E-01: a cell's fresh record is made ready the way Simulate's records are: values that meet its guards (as before),
  its time event waited out, and each object it moves linked in a state that event moves from. The reach replay links
  each object in its initial state and waits before each timed step. A cell names its time event (`after`) and the
  moves it makes (`moves`), the matrix tags them, and the permissions diff counts them as conditions, so a plan that
  changes a time event is listed as changed. The kernel is untouched: on a record that has not waited it still refuses.
- E-02: the count-up's fraction is clamped at zero.
- E-03: the "Simulated" check follows what was simulated for the view on show, not what is painted.
- E-04: an exception stop carries the refused entry's `action` (additive in `eija.run.v1`).
- E-05: the diagram shows one run at a time. A Simulate result shown ends a run on the run bar ("Ended the run: the
  diagram shows Simulate's run"); Run or Step hides a Simulate result first.
- E-06: a part that becomes not applicable is no moment, and never counts as having passed.
- E-07 to E-09: the ticket rule above. A recorded step or scenario whose model or draft changed meanwhile is not
  written; the page says so (STALE_ANSWER) and asks to try again. A superseded run log waits for the newest one.

Regression tests are in `tests/test_play_check_in_place_second.py` (with negative controls; the Python tests fail
against `main`) and `tests/test_play_answers_follow_view.py`. One browser test, opt-in with `EIJA_BROWSER_TESTS=1`,
walks E-02, E-03, E-05, E-06 and E-07 in Chromium, and it fails on `main`.

## Before and after

Screenshots from the running app, `main` at `41369a2` before and this branch after, in
`docs/assets/inspection-2026-11-14/` (`e01-before.png`, `e01-after.png`, and so on). E-01 uses the ai-ops pack, E-04
building-permit, the rest library-loan. E-02 lasts one animation frame, and E-08 and E-09 need a slow server at the
right moment, so those three are pinned by tests rather than pictures.
