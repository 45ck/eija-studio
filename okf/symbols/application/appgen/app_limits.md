---
type: Function
title: application.appgen.app_limits
description: '`def app_limits(data: DataModel | None) -> list[str]` in `application/appgen`.'
resource: repo://src/eija_studio/application/appgen.py#app_limits
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#app_limits
  title: application/appgen.py
  hash_method: ast-v2
  sha256: 37e7090147b70fb3edb9e6120ebf41cd42877057817658b6000613a3cdca695e
notes_baseline: 22582f076b1b950ee3d7c0191fdbc99e25548d326da035f89f2f56c9892860ca
---

# application.appgen.app_limits

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def app_limits(data: DataModel \| None) -> list[str]` |
| Code | `repo://src/eija_studio/application/appgen.py#app_limits` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.appgen.LIMITS](/symbols/application/appgen/LIMITS.md) - Constant `LIMITS` in `application/appgen`.
* [application.appgen.NO_DATA](/symbols/application/appgen/NO_DATA.md) - Constant `NO_DATA` in `application/appgen`.
* [application.appgen.WITH_DATA](/symbols/application/appgen/WITH_DATA.md) - Constant `WITH_DATA` in `application/appgen`.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.

## Referenced by

* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
* [application.appgen.readme](/symbols/application/appgen/readme.md) - `def readme(pack: Pack, model: Workflow, cases: int, data: DataModel | None=None) -> str` in `application/appgen`.
<!-- okf:generated:end links -->
