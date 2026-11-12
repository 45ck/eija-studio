---
type: Function
title: application.ghost_diff.ghost_diff
description: The union of two state machines, each element with its status, and the ordered list of changes.
resource: repo://src/eija_studio/application/ghost_diff.py#ghost_diff
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/ghost_diff.py#ghost_diff
  title: application/ghost_diff.py
  hash_method: ast-v2
  sha256: c04f0c407400600b86f1bbd29eb575f92488233ff2abef880194988564e10045
notes_baseline: a4bc4c9cec4f1479115cbbbd93a6fe37dc48c2fcfc0e3c1208cf98076df9d7ba
---

# application.ghost_diff.ghost_diff

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/ghost_diff`](/modules/application/ghost_diff.md) |
| Signature | `def ghost_diff(before: Workflow, after: Workflow) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/ghost_diff.py#ghost_diff` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The union of two state machines, each element with its status, and the ordered list of changes.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.ghost_diff.FORMAT](/symbols/application/ghost_diff/FORMAT.md) - Constant `FORMAT` in `application/ghost_diff`.
* [domain.impact.keyed](/symbols/domain/impact/keyed.md) - Both models' transitions keyed for comparison.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [application.sequences.check_sequences](/symbols/application/sequences/check_sequences.md) - Every scenario drawn as a sequence and checked by the kernel on `model`; with `base` (the model in force) also on it, for the change.
<!-- okf:generated:end links -->
