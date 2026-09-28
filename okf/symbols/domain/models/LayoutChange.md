---
type: Class
title: domain.models.LayoutChange
description: '`class LayoutChange(Contract)` in `domain/models` (the source has no docstring).'
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
  sha256: 3d5f9c0eb4e730f07838ce087f37dc476dfb3e55eda3eff1ae975527d64f8cb0
---

# domain.models.LayoutChange

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class LayoutChange(Contract)` |
| Code | `repo://src/eija_studio/domain/models.py#LayoutChange` |
| Hash | `ast-sig-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `node` | `str` | `Field(min_length=1, max_length=60)` |
| `x` | `int` | `Field(ge=0, le=2000)` |
| `y` | `int` | `Field(ge=0, le=2000)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models` (the source has no docstring).

## Referenced by

* [Authoring](/contexts/authoring.md) - Owns Requested intent, alternatives, explicit selection, candidate and edits
* [application.service.Studio.layout](/symbols/application/service/Studio.layout.md) - `def layout(self, case_id: str, expected: int, change: LayoutChange, principal: Principal) -> dict` in `application/service` (the source has no docstring).
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service` (the source has no docstring).
<!-- okf:generated:end links -->
