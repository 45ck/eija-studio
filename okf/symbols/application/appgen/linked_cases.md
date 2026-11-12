---
type: Function
title: application.appgen.linked_cases
description: For each transition that moves linked objects, an actor who may take it tries it with the objects in every state of their lifecycles, and the kernel's answer, with the objects' states after a commit (ADR-0241).
resource: repo://src/eija_studio/application/appgen.py#linked_cases
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#linked_cases
  title: application/appgen.py
  hash_method: ast-v2
  sha256: 7bda389b50dba6089b01f5dc939e7baa1bed4e278475eb7e2205c9722f917812
notes_baseline: eb95f20fd5bafdb3e868b4a71622daaa3ac59ab173dd6564ad18da1ebaf235a9
---

# application.appgen.linked_cases

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def linked_cases(pack: Pack, model: Workflow) -> list[dict[str, object]]` |
| Code | `repo://src/eija_studio/application/appgen.py#linked_cases` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
For each transition that moves linked objects, an actor who may take it tries it with the objects in every
state of their lifecycles, and the kernel's answer, with the objects' states after a commit (ADR-0241). Empty for a
model without linked objects, so every other oracle keeps its exact bytes.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.linked.combinations](/symbols/domain/linked/combinations.md) - Every combination of states of the objects `transition` moves, one dict per combination; `[{}]` when it moves none.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
