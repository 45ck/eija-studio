---
type: Function
title: application.ripple.check_follow_ons
description: 'The proposer''s follow-on steps, each re-checked on its own on top of the plan: a state-machine step through the policy (`base` with `plan` and the step), a screen step by the design check of `screens` against `candidate…'
resource: repo://src/eija_studio/application/ripple.py#check_follow_ons
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/ripple.py#check_follow_ons
  title: application/ripple.py
  hash_method: ast-v2
  sha256: 3d4bddf69cf9c6767e785e36b841e994e4b1d36ce74e02829dc00cadcdb406a5
notes_baseline: 63e1cd78bdd27ea3b04733498264bf22652a85d320f8b9be2f11f21ed5d86b93
---

# application.ripple.check_follow_ons

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/ripple`](/modules/application/ripple.md) |
| Signature | `def check_follow_ons(document: Any, base: Workflow, plan: list[Any], pack: Pack, candidate: Workflow, screens: Screens, data: DataModel \| None) -> list[dict[str, Any]]` |
| Code | `repo://src/eija_studio/application/ripple.py#check_follow_ons` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The proposer's follow-on steps, each re-checked on its own on top of the plan: a state-machine step through
the policy (`base` with `plan` and the step), a screen step by the design check of `screens` against `candidate`.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.data_steps.parse_step](/symbols/application/data_steps/parse_step.md) - A plan step: a data-model step, or else a kernel transaction (`parse_transaction`).
* [application.data_steps.split](/symbols/application/data_steps/split.md) - The kernel transactions and the data-model steps, each in plan order.
* [application.ripple.MAX_FOLLOW_ONS](/symbols/application/ripple/MAX_FOLLOW_ONS.md) - Constant `MAX_FOLLOW_ONS` in `application/ripple`.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.screens.Screens](/symbols/domain/screens/Screens.md) - `class Screens(Contract)` in `domain/screens`.
<!-- okf:generated:end links -->
