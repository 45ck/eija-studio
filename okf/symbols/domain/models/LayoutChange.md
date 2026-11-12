---
type: Class
title: domain.models.LayoutChange
description: '`class LayoutChange(Contract)` in `domain/models`.'
resource: repo://src/eija_studio/domain/models.py#LayoutChange
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#LayoutChange
  title: domain/models.py
  hash_method: ast-sig-v1
  sha256: b6c6929032fad43585c16f7890882b0df18b5609422484ccf32c62426ee6f946
notes_baseline: 7409df5370ad0926a2473349b017d9e7789f9f741d644df25ab350f42fd2e318
---

# domain.models.LayoutChange

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class LayoutChange(Contract)` |
| Code | `repo://src/eija_studio/domain/models.py#LayoutChange` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `node` | `str` | `Field(min_length=1, max_length=60)` |
| `x` | `JsonInt` | `Field(ge=0, le=2000)` |
| `y` | `JsonInt` | `Field(ge=0, le=2000)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.models.JsonInt](/symbols/domain/models/JsonInt.md) - Type alias `JsonInt` in `domain/models`.

## Referenced by

* [Authoring](/contexts/authoring.md) - Owns Requested intent, alternatives, explicit selection, candidate and edits
* [application.diagrams.CONTRACTS](/symbols/application/diagrams/CONTRACTS.md) - Constant `CONTRACTS` in `application/diagrams`.
* [application.service.Studio.layout](/symbols/application/service/Studio.layout.md) - `def layout(self, case_id: str, expected: int, change: LayoutChange, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio(StudioViews)` in `application/service`.
<!-- okf:generated:end links -->
