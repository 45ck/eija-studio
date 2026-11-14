---
type: Architecture Decision Record
title: 'ADR-0246: The kernel refuses undeclared roles, judges path laws alike, and fails value guards closed'
description: A Fagan inspection of the kernel (inspection record) read the policy, the model contracts, the law judges, the value guards, the edit vocabulary, the impact ripple and the runtime against their ADRs.
resource: repo://docs/adr/0246-kernel-inspection-fixes.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0246-kernel-inspection-fixes.md
  title: 0246-kernel-inspection-fixes.md
  hash_method: lf-sha256-v1
  sha256: 0f807d52dc19cb8b0085fe19387490cc219ead992b478f2ec0f0e8e2bc742f0d
notes_baseline: 1899155485c8ea6a0161ad8060607c414d63adc6e4e1b51595f29f53132792a2
---

# ADR-0246: The kernel refuses undeclared roles, judges path laws alike, and fails value guards closed

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-13 |
| Lane | kernel (Fagan inspection of the kernel) |
| Source | `repo://docs/adr/0246-kernel-inspection-fixes.md` |

## Decision outcome (verbatim)

> * **K1**: `policy.declared_codes` adds `UNDECLARED_ROLE:<transition id>` for each transition held by an undeclared role.
>   The transition id is pattern-checked; a role is free text, and the policy codes are drawn into diagram notes, where a
>   hostile role name could inject markup (`tests/test_diagrams.py` caught that with the role in the code).
> * **K2**: the table judge of `path_requires` asks whether some step enters the state from a state a record reaches
>   without the waypoint, as `path_requires_kind` already does. A new record has taken no step. Unchanged for any state
>   other than the initial one.
> * **K3, K4**: `ValueGuard.holds` orders text against a date only when the text is a real date, and a value that is not a
>   bool, a number or a string is no kind a guard compares. Both fail closed (`VALUE_GUARD_DENIED` at runtime).
> * **K5**: `add_transition` gives a new source of an existing action that action's value guards, time event and linked
>   steps, so its transitions stay alike. #257 landed the same fix (`transactions._another_source`) while this was open;
>   its code is kept and the K5 tests here cover it.
> * **K6**: `value_guards.points` keeps `1` apart from `True` and `0` apart from `False`.
> * **K7**: `model_impact` adds `model_changes` (only when non-empty) naming `initial_state`, `initiators`, `receives` or
>   `objects`. A start change roots a `record-start` node rippling to the review packet; a lifecycle change marks the
>   actions that move that object as changed.
> * **K8**: each initiator and each linked-object state is a 1 to 60 character name, as every other role and state is.
>
> The composite-tree helpers moved from `models.py` to `domain/state_tree.py` unchanged, to keep `models.py` above the
> maintainability floor (MI-01) after the additions.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://tests/test_diagrams.py`
* `repo://tests/test_kernel_inspection.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0231: Who may start a record](/adrs/0231-who-may-start-a-record.md) - Issue #142: a workflow said who may take each transition, but not who may start a record.
* [ADR-0232: One action from several states](/adrs/0232-one-action-from-several-states.md) - Issue #148: `Workflow.coherent` refused a second transition with the same action, so each action labelled exactly one transition.

## Referenced by

* [ADR-0250: Who starts a record is checked like who acts, and a law never protects a state that is gone](/adrs/0250-kernel-second-inspection.md) - The first inspection of the kernel (ADR-0246) read each kernel function against its own ADR.
<!-- okf:generated:end links -->
