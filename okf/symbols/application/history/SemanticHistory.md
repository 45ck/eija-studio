---
type: Class
title: application.history.SemanticHistory
description: Validated replay; models includes the selected meaning followed by each applied owner edit.
resource: repo://src/eija_studio/application/history.py#SemanticHistory
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/history.py#SemanticHistory
  title: application/history.py
  hash_method: ast-sig-v1
  sha256: e575b49d3f6ed0621d92001621afe591ec4e5e20fcbfbb9366264e419b9c211a
notes_baseline: 4354c3e63441e3f6fa6c14660d18da766577f29f66efb4e02867723f9f45f4cc
---

# application.history.SemanticHistory

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/history`](/modules/application/history.md) |
| Signature | `class SemanticHistory` |
| Code | `repo://src/eija_studio/application/history.py#SemanticHistory` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Validated replay; models includes the selected meaning followed by each applied owner edit.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `initial_count` | `int` |  |
| `models` | `tuple[Workflow, ...]` |  |
| `redo_models` | `tuple[Workflow, ...]` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [application.history.replay](/symbols/application/history/replay.md) - Fail closed when stored commands no longer explain the candidate under the exact active pack.
<!-- okf:generated:end links -->
