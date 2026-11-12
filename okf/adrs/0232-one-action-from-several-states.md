---
type: Architecture Decision Record
title: 'ADR-0232: One action from several states'
description: 'Issue #148: `Workflow.coherent` refused a second transition with the same action, so each action labelled exactly one transition.'
resource: repo://docs/adr/0232-one-action-from-several-states.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0232-one-action-from-several-states.md
  title: 0232-one-action-from-several-states.md
  hash_method: lf-sha256-v1
  sha256: fb2e94d7e4d8cdd7b8eafe0926f7b9a2532d5791b0f6571bac7e3e596419ba99
notes_baseline: f78a24662ce943c2fa8018cff1b81db2cebf14b68de4b1d512afe6d3f4d7fbdc
---

# ADR-0232: One action from several states

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-11 |
| Lane | kernel / generated apps / interop / PlayIDE |
| Source | `repo://docs/adr/0232-one-action-from-several-states.md` |

## Decision outcome (verbatim)

> `Workflow.coherent` allows several transitions with the same action, under three conditions:
> * Each leaves a different state.
> * All of them share target, role, guards, required effects and forbidden effects.
> * `(from_state, action)` is unique.
>
> New helpers:
> * `Workflow.transition_for(action, state)` gives the transition leaving `state`. If the action does not leave that state, it gives any one of its transitions, which is enough for an authority check.
> * `Workflow.sources(action)` lists the states the action leaves.
>
> Changes by area:
> * **Runtime**: `execute` takes the transition leaving the record's state. Authority is checked first, as before, and an action that does not leave that state is `STATE_DENIED`.
> * **Edits**: `set_role`, `set_guards`, `set_effects` and retargeting the target end change every transition the action labels, so they stay alike. Moving a source changes only that one transition.
> * **Diffs**: review, impact, the ghost diff and the diagram diff key transitions by action while an action labels at most one transition, so all existing outputs are unchanged. Once an action labels several in either model, its transitions are keyed by action and source state (`Return from Overdue`). The use case diagram keeps one use case per action.
> * **Sketches and UML import**:
>   * A sketch or a new system started from UML may repeat a trigger from another state when it goes to the same state, by the same role, with the same guard and effects. Anything else is refused and named.
>   * Importing into an existing model matches each arrow of such an action to the transition leaving its source. It adds or removes transitions as needed.
> * **Generated apps**: the oracle lists each action once. The app already asks the kernel, so it needed no change.
> * **Formal tools**: the TLA+, SMT and BMC encodings still model one transition per action. `verification/scope.py` refuses any other workflow with `OutsideFormalScope`. The Bend generator is unchanged, because its proof is bound to the generator's bytes. It is only run on the fixed excursion models, which keep one transition per action.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* Amendment, 12 November 2026: chat and the outline name the source

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://verification/scope.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [ADR-0234: Guards over record values](/adrs/0234-guards-over-record-values.md) - Issue #93, item 1.
* [ADR-0237: Time events on transitions](/adrs/0237-time-events.md) - Issue #93, item 2.
* [ADR-0239: Verify value-guard representatives by property and mutation, and fix what that found](/adrs/0239-value-guard-representatives-verified.md) - ADR-0231 to ADR-0235 added initiators, one action from several states, separation of duties, guards over record values and built associations.
* [ADR-0240: Composite states](/adrs/0240-composite-states.md) - Issue #93, item 3.
* [ADR-0241: Actions on linked objects](/adrs/0241-actions-on-linked-objects.md) - Issue #93, item 4.
* [ADR-0242: Conformance that catches a divergent app by behaviour](/adrs/0242-conformance-that-catches-divergence.md) - The pitch for `eija build` (ADR-0150) is that the generated app's conformance tests prove the app matches its model.
<!-- okf:generated:end links -->
