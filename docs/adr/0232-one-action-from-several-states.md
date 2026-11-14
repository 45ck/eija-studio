# ADR-0232: One action from several states

* Status: accepted
* Date: 2026-11-11
* Lane: kernel / generated apps / interop / PlayIDE

## Context and problem statement

Issue #148: `Workflow.coherent` refused a second transition with the same action, so each action labelled exactly one transition. UML state machines let one trigger leave several states (`Cancel` from `Requested`, `Scheduled` and `Booked`). Engineers who draw it that way were refused. The workaround was a differently named action per state (`WithdrawAfterVetting`, `WithdrawAfterBooking`), and every one of those added a use case, a screen and law entries.

## Decision drivers

* Existing models keep their meaning, bytes and hashes.
* Authority, laws, screens and use cases are keyed by action today. Keep them that way, so one action still means one rule.
* The runtime still checks authority before state, so refusal codes keep their order.
* Formal encodings that model one rule per action must not silently encode only one of an action's transitions.

## Considered options

* An action labels several transitions that are alike apart from id and source state (chosen).
* An action labels several transitions with any target, role, guards or effects. This is more general, but authority would depend on the record's state, which reorders refusals. Every law, screen and use case would then need a per-source variant.
* Keep one transition per action and add a "sources" list field. That is a schema change to every model and to every tool that reads one.

## Decision outcome

`Workflow.coherent` allows several transitions with the same action, under three conditions:
* Each leaves a different state.
* All of them share target, role, guards, required effects and forbidden effects.
* `(from_state, action)` is unique.

New helpers:
* `Workflow.transition_for(action, state)` gives the transition leaving `state`. If the action does not leave that state, it gives any one of its transitions, which is enough for an authority check.
* `Workflow.sources(action)` lists the states the action leaves.

Changes by area:
* **Runtime**: `execute` takes the transition leaving the record's state. Authority is checked first, as before, and an action that does not leave that state is `STATE_DENIED`.
* **Edits**: `set_role`, `set_guards`, `set_effects` and retargeting the target end change every transition the action labels, so they stay alike. Moving a source changes only that one transition.
* **Diffs**: review, impact, the ghost diff and the diagram diff key transitions by action while an action labels at most one transition, so all existing outputs are unchanged. Once an action labels several in either model, its transitions are keyed by action and source state (`Return from Overdue`). The use case diagram keeps one use case per action.
* **Sketches and UML import**:
  * A sketch or a new system started from UML may repeat a trigger from another state when it goes to the same state, by the same role, with the same guard and effects. Anything else is refused and named.
  * Importing into an existing model matches each arrow of such an action to the transition leaving its source. It adds or removes transitions as needed.
* **Generated apps**: the oracle lists each action once. The app already asks the kernel, so it needed no change.
* **Formal tools**: the TLA+, SMT and BMC encodings still model one transition per action. `verification/scope.py` refuses any other workflow with `OutsideFormalScope`. The Bend generator is unchanged, because its proof is bound to the generator's bytes. It is only run on the fixed excursion models, which keep one transition per action.

### Consequences

* Good: a UML engineer can draw one `Cancel` from several states. The use case diagram, screens and laws stay one per action.
* Good: no existing model, hash, receipt or output changes. The tests cover:
  * the runtime;
  * edits;
  * diffs;
  * sketches;
  * UML import in every format;
  * a built app passing conformance;
  * the simulation;
  * the formal scope guard.
* Bad: an action cannot have a different target or role per source. A model that needs that still uses two actions.
* Bad: the formal proofs do not cover a workflow that uses this. Such a workflow is refused there and reported, not proved.
* Bad: kernel change, so it needs owner source review (#80).
* Revisit when: a pack needs per-source targets, or the formal encodings gain a set of sources per action.

## Amendment, 12 November 2026: chat and the outline name the source

In PlayIDE, chat plan mode refused every phrase about such an action ("The model has no single transition or action
Return"), and the outline listed `Return [Librarian]` twice. Now:

* "allow ‹role› to Return" and "move Return target to ‹state›" change what the action's transitions share, so any one
  stands for all of them and the kernel's edit changes every one.
* "remove Return" removes every transition the action labels; "remove Return from Overdue" removes the one leaving
  Overdue. "move Return from Overdue source to ‹state›" moves one source; without "from" it names the sources to choose
  from. The phrases offered for a selected transition say "from ‹state›" when its action leaves several states.
* The outline (and so the status bar) reads `Return [Librarian] from OnLoan` and `Return [Librarian] from Overdue`.

## Amendment, 13 November 2026: another source keeps what the action shares

Re-inspection of the merged PRs (`docs/quality/inspection-2026-11-13-merged-prs.md`, M1) found that time events
(ADR-0237), value guards (ADR-0234) and steps on linked objects (ADR-0241) broke this decision for the actions that
carry them: an added source was declared from the pack's catalog, which has none of them, so the edit was refused as
incoherent. `add_transition` for an action the model already has now copies everything its transitions share (guards,
effects, value guards, time event, linked steps) and takes only its id and source from the request. A different target
or role is refused with `EDIT_INVALID`, naming the action's target and role.
