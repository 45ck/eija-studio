---
type: Function
title: domain.linked.admitting
description: The first combination of states (as `combinations` orders them) from which `transition` can move every object it names; `{}` when it moves none, None when no combination can.
resource: repo://src/eija_studio/domain/linked.py#admitting
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/linked.py#admitting
  title: domain/linked.py
  hash_method: ast-v2
  sha256: a9335949a1b9d66b1a624535e789e413dae61ea801afb9c80d4754ac6b016279
notes_baseline: 037771c8c43659d88866db5d887f22ac6720cc1527863a7c09109db190028a3a
---

# domain.linked.admitting

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/linked`](/modules/domain/linked.md) |
| Signature | `def admitting(model: Workflow, transition: Transition \| None) -> dict[str, str] \| None` |
| Code | `repo://src/eija_studio/domain/linked.py#admitting` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The first combination of states (as `combinations` orders them) from which `transition` can move every object it
names; `{}` when it moves none, None when no combination can.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.linked.combinations](/symbols/domain/linked/combinations.md) - Every combination of states of the objects `transition` moves, one dict per combination; `[{}]` when it moves none.
* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
