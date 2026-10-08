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
  sha256: ce7859ef5fe0aca0e90eb8f33875dc7580d9b52b9e867d50c710ae8699beb57d
notes_baseline: aedff84cf449f2b5393bf978fc322c6e3222a6bfc5fddb992c24768316974bbe
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
<!-- okf:generated:end links -->
