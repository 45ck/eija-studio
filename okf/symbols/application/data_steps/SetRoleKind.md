---
type: Class
title: application.data_steps.SetRoleKind
description: Make the actor holding `role` a person, an AI agent, a timer or an external system (ADR-0210).
resource: repo://src/eija_studio/application/data_steps.py#SetRoleKind
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/data_steps.py#SetRoleKind
  title: application/data_steps.py
  hash_method: ast-sig-v1
  sha256: 3760abd7c8d6f65e3f4b6cd393c3a864b554db38d57f3a77845922251ef8b86c
notes_baseline: bd0e200f6cecc4fb12cf283eaee7814c555cc2c08b970177b84fa7d1c3e3a1a8
---

# application.data_steps.SetRoleKind

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/data_steps`](/modules/application/data_steps.md) |
| Signature | `class SetRoleKind(Contract)` |
| Code | `repo://src/eija_studio/application/data_steps.py#SetRoleKind` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Make the actor holding `role` a person, an AI agent, a timer or an external system (ADR-0210). Not a kernel
transaction and not a data-model step: it changes a draft of the pack's roles, which is protected policy input
(the kind laws count roles by kind), so the policy judges the plan with the draft's kinds, and nothing is written.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['set_role_kind']` |  |
| `role` | `str` | `Field(pattern=NAME)` |
| `to` | `RoleKind` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.NAME](/symbols/domain/data/NAME.md) - Constant `NAME` in `domain/data`.
* [domain.laws.RoleKind](/symbols/domain/laws/RoleKind.md) - Type alias `RoleKind` in `domain/laws`.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [application.data_steps.DataStep](/symbols/application/data_steps/DataStep.md) - Type alias `DataStep` in `application/data_steps`.
* [application.data_steps.Step](/symbols/application/data_steps/Step.md) - Type alias `Step` in `application/data_steps`.
* [application.data_steps.describe_data](/symbols/application/data_steps/describe_data.md) - One line a person can check against the class diagram, or the use case diagram for a role's kind.
* [application.data_steps.kind_steps](/symbols/application/data_steps/kind_steps.md) - The role-kind steps, in plan order.
* [application.data_steps.set_kinds](/symbols/application/data_steps/set_kinds.md) - `pack` with each role-kind step applied in turn: a draft held in memory, checked as any pack is, so the kind laws are bound to the new kinds.
* [application.data_steps.split](/symbols/application/data_steps/split.md) - The kernel transactions and the data-model steps, each in plan order (role-kind steps are in neither).
* [application.plan.describe](/symbols/application/plan/describe.md) - One line a person can check against the diagram.
<!-- okf:generated:end links -->
