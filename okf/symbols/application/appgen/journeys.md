---
type: Function
title: application.appgen.journeys
description: 'For each transition, a record started through the app and walked to it: the shortest run from the initial state whose last step is that transition, each step taken by the first fixture actor the kernel allows, and the k…'
resource: repo://src/eija_studio/application/appgen.py#journeys
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#journeys
  title: application/appgen.py
  hash_method: ast-v2
  sha256: b6c4e34b5ad88d57031fef2c085dc3e01049a930f71fc04c5012d4e8f63d92be
notes_baseline: f3cdf8a33b49ee5edf0890b4f367f2c6611081802942951c208848f16bf2678f
---

# application.appgen.journeys

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def journeys(pack: Pack, model: Workflow, data: DataModel \| None) -> list[dict[str, Any]]` |
| Code | `repo://src/eija_studio/application/appgen.py#journeys` |
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

* [application.appgen.valid_values](/symbols/application/appgen/valid_values.md) - A valid record: a sample of each attribute, and each reference naming the first `stock` object of its class.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
<!-- okf:generated:end links -->
