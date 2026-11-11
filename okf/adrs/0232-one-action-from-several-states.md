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
  sha256: 816c45e9b3947c074a9dcd7745a7e87391be5257aa17286f2ae87614bc0c4627
notes_baseline: 1781a0d8bf12fe3fe71ddabea630601f406db4d940d476da5ae1baa6f5a89c08
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

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://verification/scope.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
