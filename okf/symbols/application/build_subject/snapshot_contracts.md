---
type: Function
title: application.build_subject.snapshot_contracts
description: Parse the very contracts the generated application will load.
resource: repo://src/eija_studio/application/build_subject.py#snapshot_contracts
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/build_subject.py#snapshot_contracts
  title: application/build_subject.py
  hash_method: ast-v2
  sha256: a8d8f19fd36ac3c090790c8a67ffd5d595dd052e35e0d14cc5c77bede7368379
notes_baseline: 82274203036225871b6273c28d815cc937cdf01dfbf6cb20409f5552d92a52a3
---

# application.build_subject.snapshot_contracts

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/build_subject`](/modules/application/build_subject.md) |
| Signature | `def snapshot_contracts(files: dict[str, str]) -> tuple[Pack, Workflow, DataModel \| None, Screens]` |
| Code | `repo://src/eija_studio/application/build_subject.py#snapshot_contracts` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Parse the very contracts the generated application will load.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.screens.Screens](/symbols/domain/screens/Screens.md) - `class Screens(Contract)` in `domain/screens`.

## Referenced by

* [application.build_subject.build_subject](/symbols/application/build_subject/build_subject.md) - Bind model, contracts, template bytes and measured implementation to one payload.
* [application.c4.app_c4](/symbols/application/c4/app_c4.md) - Current generated-source architecture, plus explicit fixture and data-design limits.
<!-- okf:generated:end links -->
