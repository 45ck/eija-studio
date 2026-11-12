---
type: Function
title: domain.linked.combinations
description: Every combination of states of the objects `transition` moves, one dict per combination; `[{}]` when it moves none.
resource: repo://src/eija_studio/domain/linked.py#combinations
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/linked.py#combinations
  title: domain/linked.py
  hash_method: ast-v2
  sha256: 86230f2be3b3af198434a86066b5167333e755e071fe1a59c6d0aa6259956b1d
notes_baseline: 64abb5988307109b8aa1c94655d64d1c7d44cf9352a90075c6ff0f6eda354d0d
---

# domain.linked.combinations

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/linked`](/modules/domain/linked.md) |
| Signature | `def combinations(model: Workflow, transition: Transition \| None) -> list[dict[str, str]]` |
| Code | `repo://src/eija_studio/domain/linked.py#combinations` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every combination of states of the objects `transition` moves, one dict per combination; `[{}]` when it moves
none. A lifecycle has at most 8 states and a transition moves at most 2 objects, so this is at most 64.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [application.appgen.linked_cases](/symbols/application/appgen/linked_cases.md) - For each transition that moves linked objects, an actor who may take it tries it with the objects in every state of their lifecycles, and the kernel's answer,…
* [domain.linked.admitting](/symbols/domain/linked/admitting.md) - The first combination of states (as `combinations` orders them) from which `transition` can move every object it names; `{}` when it moves none, None when no c…
<!-- okf:generated:end links -->
