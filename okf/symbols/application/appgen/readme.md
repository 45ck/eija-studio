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
  sha256: d4e6f92fba6d039f2638600c8c36f387a20e23461c1a2bbd906b87a550426966
notes_baseline: 5468057891eeb96feaf725b0ae1c277ca3bc1f71bb5f4b263b41f4f0e44ca2e9
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
