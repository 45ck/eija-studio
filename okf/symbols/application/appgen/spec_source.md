---
type: Function
title: application.appgen.spec_source
description: '`def spec_source(pack: Pack, model: Workflow) -> str` in `application/appgen`.'
resource: repo://src/eija_studio/application/appgen.py#spec_source
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#spec_source
  title: application/appgen.py
  hash_method: ast-v2
  sha256: 4bd1cc58d775aaf245da9a3974cf12955a697cd7f5a79a9a176ecca66551ef05
notes_baseline: 4cf86f0ed040723751bbafcd92833df7f2fdde1721e1893db1e825fe75793989
---

# application.appgen.spec_source

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def spec_source(pack: Pack, model: Workflow) -> str` |
| Code | `repo://src/eija_studio/application/appgen.py#spec_source` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
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
