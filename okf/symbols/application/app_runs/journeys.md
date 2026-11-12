---
type: Function
title: application.app_runs.journeys
description: 'For each transition, a record started through the app and walked to it: the shortest run from the initial state whose last step is that transition, each step taken by the first fixture actor the kernel allows, and the k…'
resource: repo://src/eija_studio/application/app_runs.py#journeys
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/app_runs.py#journeys
  title: application/app_runs.py
  hash_method: ast-v2
  sha256: 34e4749c7a693d5951de89abf3f115914ba7aacd8dc15fd52d79210631a332c1
notes_baseline: 7183e463b803680da01fdb3b17af1b02ba0b3f2745ecf1ad516ab2a534fe6492
---

# application.app_runs.journeys

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/app_runs`](/modules/application/app_runs.md) |
| Signature | `def journeys(pack: Pack, model: Workflow, valid: dict[str, Any]) -> list[dict[str, Any]]` |
| Code | `repo://src/eija_studio/application/app_runs.py#journeys` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
For each transition, a record started through the app and walked to it: the shortest run from the initial state
whose last step is that transition, each step taken by the first fixture actor the kernel allows, and the kernel's
answer for each step on one record that remembers its values and who acted. A transition no run reaches is left
out (the law proof reports what is unreachable). Unlike `oracle_cases`, nothing is seeded: the record is the
app's own, created with valid values.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
<!-- okf:generated:end links -->
