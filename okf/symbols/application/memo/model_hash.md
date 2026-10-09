---
type: Function
title: application.memo.model_hash
description: '`model.semantic_hash`, computed once per model object.'
resource: repo://src/eija_studio/application/memo.py#model_hash
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/memo.py#model_hash
  title: application/memo.py
  hash_method: ast-v2
  sha256: 16bbfb29af8db85079acc7cade8b0d78517eeb7d9fe119e8c17af13d7b9b0915
notes_baseline: cf914a5c09d95158dfb4f675337f4e30f7299c35a2cb2e237dfd4d4f6dfd5542
---

# application.memo.model_hash

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/memo`](/modules/application/memo.md) |
| Signature | `def model_hash(model: Workflow) -> str` |
| Code | `repo://src/eija_studio/application/memo.py#model_hash` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
`model.semantic_hash`, computed once per model object.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault: Callable[[…` in `application/runtime`.
* [application.runtime.initialise](/symbols/application/runtime/initialise.md) - `def initialise(session: UnitOfWork, case_id: str, model: Workflow, *, state: str | None=None, pack: Pack | No…` in `application/runtime`.
<!-- okf:generated:end links -->
