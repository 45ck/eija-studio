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
  sha256: 3e55b425575fc22402eb5ac6efc99dc91f1e549b4b732a9b468220acc8cd3c67
notes_baseline: 366a638528a60f84c8dd90ac17c9d10308179c0abf16155906ab75e712855a1f
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

* [application.ripple.MAX_FOLLOW_ONS](/symbols/application/ripple/MAX_FOLLOW_ONS.md) - Constant `MAX_FOLLOW_ONS` in `application/ripple`.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.screens.Screens](/symbols/domain/screens/Screens.md) - `class Screens(Contract)` in `domain/screens`.
* [domain.transactions.parse_transaction](/symbols/domain/transactions/parse_transaction.md) - Validate one transaction document; a malformed one is ``EDIT_INVALID``, never a crash.
<!-- okf:generated:end links -->
