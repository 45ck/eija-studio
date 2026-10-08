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
  sha256: 0339beb6ced8f249e1c2150a7c6e90b23d7a9db762f53e80604a1d7670d82fb6
notes_baseline: d3294d17b7874be0b0f3be8a1f7c4aedc0a365b5d5d6153a29b769f09705349f
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
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [application.sequences.check_sequences](/symbols/application/sequences/check_sequences.md) - Every sequence checked by the kernel on `model`; with `base` (the model in force) also on it, for the change.
<!-- okf:generated:end links -->
