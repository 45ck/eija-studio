---
type: Function
title: application.data_steps.apply_data
description: '`data` with the data-model steps applied in turn, checked by the data model''s own contract; `data` when none.'
resource: repo://src/eija_studio/application/data_steps.py#apply_data
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/data_steps.py#apply_data
  title: application/data_steps.py
  hash_method: ast-v2
  sha256: 926667c356a9a79c22bf3b3d69dc5c029fe5a25471ece4dd46233c59ef7e982b
notes_baseline: 68f327be1122d4f503c1c775fb67f98bc8ffb169989d5fff0dda9ad021752aaf
---

# application.data_steps.apply_data

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/data_steps`](/modules/application/data_steps.md) |
| Signature | `def apply_data(data: DataModel \| None, steps: Sequence[DataEdit]) -> DataModel \| None` |
| Code | `repo://src/eija_studio/application/data_steps.py#apply_data` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
`data` with the data-model steps applied in turn, checked by the data model's own contract; `data` when none.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.data_steps.DataEdit](/symbols/application/data_steps/DataEdit.md) - Type alias `DataEdit` in `application/data_steps`.
* [application.data_steps.SetRoleKind](/symbols/application/data_steps/SetRoleKind.md) - `class SetRoleKind(Contract)` in `application/data_steps`.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.data.parse_data](/symbols/domain/data/parse_data.md) - `def parse_data(document: Any, pack_id: str) -> DataModel` in `domain/data`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.

## Referenced by

* [application.data_steps.draft_pack](/symbols/application/data_steps/draft_pack.md) - `pack` as these plan steps would have it, held in memory: on a system the person started (`grows`), the actions and roles they name are declared (ADR-0201) and…
<!-- okf:generated:end links -->
