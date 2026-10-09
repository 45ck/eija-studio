---
type: Class
title: application.data_steps.SetRoleKind
description: '`class SetRoleKind(Contract)` in `application/data_steps`.'
resource: repo://src/eija_studio/application/data_steps.py#SetRoleKind
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/data_steps.py#SetRoleKind
  title: application/data_steps.py
  hash_method: ast-sig-v1
  sha256: 0ed231971d953c20f59254e68f6e072484e664e92ad00ed781e13bd78bce0b5b
notes_baseline: dd4d38bbebc5b514dfdd0b628e1899cfac3bc57faa6aeb80955647fcf6b75ca4
---

# application.data_steps.SetRoleKind

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/data_steps`](/modules/application/data_steps.md) |
| Signature | `class SetRoleKind(Contract)` |
| Code | `repo://src/eija_studio/application/data_steps.py#SetRoleKind` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['set_role_kind']` |  |
| `role` | `str` | `Field(pattern=NAME)` |
| `role_kind` | `RoleKind` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.NAME](/symbols/domain/data/NAME.md) - Constant `NAME` in `domain/data`.
* [domain.laws.RoleKind](/symbols/domain/laws/RoleKind.md) - Type alias `RoleKind` in `domain/laws`.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [application.data_steps.DATA_EDITS](/symbols/application/data_steps/DATA_EDITS.md) - Constant `DATA_EDITS` in `application/data_steps`.
* [application.data_steps.DataEdit](/symbols/application/data_steps/DataEdit.md) - Type alias `DataEdit` in `application/data_steps`.
* [application.data_steps.DataStep](/symbols/application/data_steps/DataStep.md) - Type alias `DataStep` in `application/data_steps`.
* [application.data_steps.apply_data](/symbols/application/data_steps/apply_data.md) - `data` with the data-model steps applied in turn, checked by the data model's own contract; `data` when none.
* [application.data_steps.describe_data](/symbols/application/data_steps/describe_data.md) - One line a person can check against the class diagram.
* [application.data_steps.with_kinds](/symbols/application/data_steps/with_kinds.md) - `pack` with the roles' kinds these steps set, a draft held in memory; `PLAN_KIND_FIXED` on a system with a law about kinds, and `EDIT_INVALID` for a role the p…
<!-- okf:generated:end links -->
