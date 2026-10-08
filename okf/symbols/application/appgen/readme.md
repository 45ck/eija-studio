---
type: Function
title: application.appgen.readme
description: '`def readme(pack: Pack, model: Workflow, cases: int) -> str` in `application/appgen`.'
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
  sha256: 66f92c7273356c704dacbe15a184441c3f69de070e4fcb761554cee91fa45cc7
notes_baseline: 91ed4d06b953bc6bc47e737ad6b89d8c783ce66aca4f9f17ef75a8e1f8574ac5
---

# application.appgen.readme

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def readme(pack: Pack, model: Workflow, cases: int) -> str` |
| Code | `repo://src/eija_studio/application/appgen.py#readme` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.appgen.LIMITS](/symbols/application/appgen/LIMITS.md) - Constant `LIMITS` in `application/appgen`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
<!-- okf:generated:end links -->
