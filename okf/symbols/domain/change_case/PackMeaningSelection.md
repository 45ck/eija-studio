---
type: Class
title: domain.change_case.PackMeaningSelection
description: '`class PackMeaningSelection(Contract)` in `domain/change_case`.'
resource: repo://src/eija_studio/domain/change_case.py#PackMeaningSelection
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/change_case.py#PackMeaningSelection
  title: domain/change_case.py
  hash_method: ast-sig-v1
  sha256: 906e6fd5e5dcb76d7620df0a83d3bd09073fd03a44a0507df81b2aff5773c5c2
notes_baseline: 7fa9712d8c16c7636ef907d63664c9f7e93a279efef0ca6488548302fae3f894
---

# domain.change_case.PackMeaningSelection

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/change_case`](/modules/domain/change_case.md) |
| Signature | `class PackMeaningSelection(Contract)` |
| Code | `repo://src/eija_studio/domain/change_case.py#PackMeaningSelection` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['pack_meaning']` |  |
| `meaning` | `str` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [application.service.Studio.select](/symbols/application/service/Studio.select.md) - `def select(self, case_id: str, expected: int, interpretation: str, principal: Principal) -> dict[str, Any]` in `application/service`.
* [domain.change_case.Selection](/symbols/domain/change_case/Selection.md) - Type alias `Selection` in `domain/change_case`.
<!-- okf:generated:end links -->
