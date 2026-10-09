---
type: Function
title: application.data_steps.describe_data
description: One line a person can check against the class diagram, or the use case diagram for a role's kind.
resource: repo://src/eija_studio/application/data_steps.py#describe_data
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/data_steps.py#describe_data
  title: application/data_steps.py
  hash_method: ast-v2
  sha256: 5849381248b861574c85d3f2d6e814f46c84c2488a3ff0501c214391b3420e27
notes_baseline: 799aa101db361de0d15c2a16ca732011056b9250cfff8c0529481f7867780912
---

# application.data_steps.describe_data

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/data_steps`](/modules/application/data_steps.md) |
| Signature | `def describe_data(step: DataEdit \| SetRoleKind) -> str` |
| Code | `repo://src/eija_studio/application/data_steps.py#describe_data` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
One line a person can check against the class diagram, or the use case diagram for a role's kind.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.data_steps.ACTOR_WORDS](/symbols/application/data_steps/ACTOR_WORDS.md) - Constant `ACTOR_WORDS` in `application/data_steps`.
* [application.data_steps.AddAttribute](/symbols/application/data_steps/AddAttribute.md) - `class AddAttribute(Contract)` in `application/data_steps`.
* [application.data_steps.DataEdit](/symbols/application/data_steps/DataEdit.md) - Type alias `DataEdit` in `application/data_steps`.
* [application.data_steps.RemoveAttribute](/symbols/application/data_steps/RemoveAttribute.md) - `class RemoveAttribute(Contract)` in `application/data_steps`.
* [application.data_steps.SetRoleKind](/symbols/application/data_steps/SetRoleKind.md) - Make the actor holding `role` a person, an AI agent, a timer or an external system (ADR-0210).

## Referenced by

* [application.plan.describe](/symbols/application/plan/describe.md) - One line a person can check against the diagram.
<!-- okf:generated:end links -->
