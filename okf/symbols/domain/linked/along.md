---
type: Function
title: domain.linked.along
description: 'For each state a record can reach, the states its linked objects are in when only this record moves them, from every object in its initial state: the first such combination found breadth-first.'
resource: repo://src/eija_studio/domain/linked.py#along
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/linked.py#along
  title: domain/linked.py
  hash_method: ast-v2
  sha256: 8de13e1629fc4feeb3db6cfe20844441ebffc31219ed8a0e9ceab921670c08e7
notes_baseline: d569585d488a0f98479449d85eae1e0a897246cc5b39d8efe0889657358bc56a
---

# domain.linked.along

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/linked`](/modules/domain/linked.md) |
| Signature | `def along(model: Workflow) -> dict[str, dict[str, str]]` |
| Code | `repo://src/eija_studio/domain/linked.py#along` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
For each state a record can reach, the states its linked objects are in when only this record moves them, from
every object in its initial state: the first such combination found breadth-first. Empty without linked objects.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
<!-- okf:generated:end links -->
