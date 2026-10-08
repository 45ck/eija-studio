---
type: Function
title: application.appgen.readme
description: '`def readme(pack: Pack, model: Workflow, cases: int, data: DataModel | None=None) -> str` in `application/appgen`.'
resource: repo://src/eija_studio/application/appgen.py#readme
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#readme
  title: application/appgen.py
  hash_method: ast-v2
  sha256: 0c4a208463a9eef1549636304963c89102d74441b86b4c50e4dfe71c2a813c6c
notes_baseline: 8a445f3213bd48a78095e74ea61cf92aad4f2dc5458246bf888b929e8fc04227
---

# application.appgen.readme

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def readme(pack: Pack, model: Workflow, cases: int, data: DataModel \| None=None) -> str` |
| Code | `repo://src/eija_studio/application/appgen.py#readme` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.appgen.app_limits](/symbols/application/appgen/app_limits.md) - `def app_limits(data: DataModel | None) -> list[str]` in `application/appgen`.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
<!-- okf:generated:end links -->
