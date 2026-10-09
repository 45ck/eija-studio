---
type: Function
title: domain.data.parse_data
description: '`def parse_data(document: Any, pack_id: str) -> DataModel` in `domain/data`.'
resource: repo://src/eija_studio/domain/data.py#parse_data
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/data.py#parse_data
  title: domain/data.py
  hash_method: ast-v2
  sha256: ac79d1965cf789d5b5e7dd6cb29289bb1bcf1a53ee6ee15e86cbed87a63ec363
notes_baseline: 81461cea342e12b402cd315f53e2482d48ca1feed2d59c4c25034d4801a7ba33
---

# domain.data.parse_data

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/data`](/modules/domain/data.md) |
| Signature | `def parse_data(document: Any, pack_id: str) -> DataModel` |
| Code | `repo://src/eija_studio/domain/data.py#parse_data` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.

## Referenced by

* [application.data_steps.apply_data](/symbols/application/data_steps/apply_data.md) - `data` with the data-model steps applied in turn, checked by the data model's own contract; `data` when none.
* [application.new_system.checked_documents](/symbols/application/new_system/checked_documents.md) - The documents, if the kernel's checks accept them; `PackError` with every problem otherwise.
* [domain.data.load_data](/symbols/domain/data/load_data.md) - The pack's data model, or None when the pack has no `data.json`.
<!-- okf:generated:end links -->
