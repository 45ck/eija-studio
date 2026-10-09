---
type: Module
title: application.data_steps
description: 'Data-model steps in a chat plan (ADR-0202): add an attribute to a class, remove one, or make one required or optional.'
resource: repo://src/eija_studio/application/data_steps.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/data_steps.py
  title: application/data_steps.py
  hash_method: ast-api-v1
  sha256: 41e0c2184b97bb8d66c61e7aefe73a9376c0c76d384f1ddd813a16f23db56e27
notes_baseline: b3409af0eede846fa49a01f19bb2db542516f2662e8b4a74f656152455b4b44d
---

# application.data_steps

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/data_steps.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Data-model steps in a chat plan (ADR-0202): add an attribute to a class, remove one, or make one required or optional.

A system started in PlayIDE has a class diagram (`data.json`, ADR-0153) whose record class is the built app's form.
Building such a system in chat (ADR-0201) also means growing that form, so a plan step may change the data model as
well as the state machine. These steps are not kernel transactions: the data model is not governed by the policy or
the laws, and has its own contract (`domain.data.DataModel`), which checks every result here. A step changes a draft
held in memory (`domain.pack.hold`); nothing is written, and a shipped pack's data model stays its owner's.

A step may also say what kind of actor holds a role (#156, ADR-0210): a person, an AI agent, a timer or an external
system. Kinds change what a law about kinds means, so the step is refused on a system with such a law: a plan cannot
pass a law by renaming who holds a role. On any other system kinds change no rule, only how the role is drawn and run.
~~~

## Public symbols

* [`AddAttribute`](/symbols/application/data_steps/AddAttribute.md) (class) - no docstring
* [`DATA_EDITS`](/symbols/application/data_steps/DATA_EDITS.md) (constant) - no docstring
* [`DATA_STEP_KINDS`](/symbols/application/data_steps/DATA_STEP_KINDS.md) (constant) - no docstring
* [`DataEdit`](/symbols/application/data_steps/DataEdit.md) (type-alias) - no docstring
* [`DataStep`](/symbols/application/data_steps/DataStep.md) (type-alias) - no docstring
* [`FIXED`](/symbols/application/data_steps/FIXED.md) (constant) - no docstring
* [`KIND_NAMES`](/symbols/application/data_steps/KIND_NAMES.md) (constant) - no docstring
* [`RemoveAttribute`](/symbols/application/data_steps/RemoveAttribute.md) (class) - no docstring
* [`SetRequired`](/symbols/application/data_steps/SetRequired.md) (class) - no docstring
* [`SetRoleKind`](/symbols/application/data_steps/SetRoleKind.md) (class) - no docstring
* [`Step`](/symbols/application/data_steps/Step.md) (type-alias) - no docstring
* [`apply_data`](/symbols/application/data_steps/apply_data.md) (function) - `data` with the data-model steps applied in turn, checked by the data model's own contract; `data` when none.
* [`data_changes`](/symbols/application/data_steps/data_changes.md) (function) - What changed on the class diagram, in words: attributes gained and lost, and required ones made optional or back.
* [`describe_data`](/symbols/application/data_steps/describe_data.md) (function) - One line a person can check against the class diagram.
* [`draft_pack`](/symbols/application/data_steps/draft_pack.md) (function) - `pack` as these plan steps would have it, held in memory: on a system the person started (`grows`), the actions and rol…
* [`is_data`](/symbols/application/data_steps/is_data.md) (function) - no docstring
* [`parse_step`](/symbols/application/data_steps/parse_step.md) (function) - A plan step: a data-model step, or else a kernel transaction (`parse_transaction`).
* [`split`](/symbols/application/data_steps/split.md) (function) - The kernel transactions and the data-model steps, each in plan order.
* [`with_kinds`](/symbols/application/data_steps/with_kinds.md) (function) - `pack` with the roles' kinds these steps set, a draft held in memory; `PLAN_KIND_FIXED` on a system with a law about ki…

## Internal imports

* [`application/new_system`](/modules/application/new_system.md)
* [`domain/data`](/modules/domain/data.md)
* [`domain/laws`](/modules/domain/laws.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/transactions`](/modules/domain/transactions.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.new_system](/modules/application/new_system.md) - Start a new system (ADR-0185): the pack documents for a system started from a sketch or copied from a template.
* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.laws](/modules/domain/laws.md) - Typed law DSL of a domain pack: what a workflow may never do, stated as data (WBS 1.1/1.2).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.transactions](/modules/domain/transactions.md) - Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.

## Referenced by

* [application.plan](/modules/application/plan.md) - Plan mode for the PlayIDE chat (ADR-0156): an AI proposes a change as numbered typed steps; the person accepts or rejects each one and sees what the accepted o…
* [application.ripple](/modules/application/ripple.md) - Ripple (ADR-0158): what one change to the state machine does to every other diagram of the same system, and the follow-on edits that would keep them in agreeme…
* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [interfaces.play_systems](/modules/interfaces/play_systems.md) - PlayIDE's systems (ADR-0185): start a new system from a sketch or a template, open one you made before, and save the work in progress to carry on later.
* [application.data_steps.AddAttribute](/symbols/application/data_steps/AddAttribute.md) - `class AddAttribute(Contract)` in `application/data_steps`.
* [application.data_steps.DATA_EDITS](/symbols/application/data_steps/DATA_EDITS.md) - Constant `DATA_EDITS` in `application/data_steps`.
* [application.data_steps.DATA_STEP_KINDS](/symbols/application/data_steps/DATA_STEP_KINDS.md) - Constant `DATA_STEP_KINDS` in `application/data_steps`.
* [application.data_steps.DataEdit](/symbols/application/data_steps/DataEdit.md) - Type alias `DataEdit` in `application/data_steps`.
* [application.data_steps.DataStep](/symbols/application/data_steps/DataStep.md) - Type alias `DataStep` in `application/data_steps`.
* [application.data_steps.FIXED](/symbols/application/data_steps/FIXED.md) - Constant `FIXED` in `application/data_steps`.
* [application.data_steps.KIND_NAMES](/symbols/application/data_steps/KIND_NAMES.md) - Constant `KIND_NAMES` in `application/data_steps`.
* [application.data_steps.RemoveAttribute](/symbols/application/data_steps/RemoveAttribute.md) - `class RemoveAttribute(Contract)` in `application/data_steps`.
* [application.data_steps.SetRequired](/symbols/application/data_steps/SetRequired.md) - `class SetRequired(Contract)` in `application/data_steps`.
* [application.data_steps.SetRoleKind](/symbols/application/data_steps/SetRoleKind.md) - `class SetRoleKind(Contract)` in `application/data_steps`.
* [application.data_steps.Step](/symbols/application/data_steps/Step.md) - Type alias `Step` in `application/data_steps`.
* [application.data_steps.apply_data](/symbols/application/data_steps/apply_data.md) - `data` with the data-model steps applied in turn, checked by the data model's own contract; `data` when none.
* [application.data_steps.data_changes](/symbols/application/data_steps/data_changes.md) - What changed on the class diagram, in words: attributes gained and lost, and required ones made optional or back.
* [application.data_steps.describe_data](/symbols/application/data_steps/describe_data.md) - One line a person can check against the class diagram.
* [application.data_steps.draft_pack](/symbols/application/data_steps/draft_pack.md) - `pack` as these plan steps would have it, held in memory: on a system the person started (`grows`), the actions and roles they name are declared (ADR-0201) and…
* [application.data_steps.is_data](/symbols/application/data_steps/is_data.md) - `def is_data(step: Step) -> bool` in `application/data_steps`.
* [application.data_steps.parse_step](/symbols/application/data_steps/parse_step.md) - A plan step: a data-model step, or else a kernel transaction (`parse_transaction`).
* [application.data_steps.split](/symbols/application/data_steps/split.md) - The kernel transactions and the data-model steps, each in plan order.
* [application.data_steps.with_kinds](/symbols/application/data_steps/with_kinds.md) - `pack` with the roles' kinds these steps set, a draft held in memory; `PLAN_KIND_FIXED` on a system with a law about kinds, and `EDIT_INVALID` for a role the p…
<!-- okf:generated:end links -->
