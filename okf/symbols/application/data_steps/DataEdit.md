---
type: Type Alias
title: application.data_steps.DataEdit
description: Type alias `DataEdit` in `application/data_steps`.
resource: repo://src/eija_studio/application/data_steps.py#DataEdit
tags:
- symbol
- application
- type-alias
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/data_steps.py#DataEdit
  title: application/data_steps.py
  hash_method: ast-v2
  sha256: c216a638bf2b575088d73a64fdf8ff9b4e796e01f945ab7922ec3fc89f78d2ec
notes_baseline: 18d06a91edc44891b6208253e128b62582651ee67004ab0e3da725d822973123
---

# application.data_steps.DataEdit

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | type-alias |
| Module | [`application/data_steps`](/modules/application/data_steps.md) |
| Signature | `DataEdit = AddAttribute \| RemoveAttribute \| SetRequired \| SetRoleKind` |
| Code | `repo://src/eija_studio/application/data_steps.py#DataEdit` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.data_steps.AddAttribute](/symbols/application/data_steps/AddAttribute.md) - `class AddAttribute(Contract)` in `application/data_steps`.
* [application.data_steps.RemoveAttribute](/symbols/application/data_steps/RemoveAttribute.md) - `class RemoveAttribute(Contract)` in `application/data_steps`.
* [application.data_steps.SetRequired](/symbols/application/data_steps/SetRequired.md) - `class SetRequired(Contract)` in `application/data_steps`.
* [application.data_steps.SetRoleKind](/symbols/application/data_steps/SetRoleKind.md) - `class SetRoleKind(Contract)` in `application/data_steps`.

## Referenced by

* [application.data_steps.Step](/symbols/application/data_steps/Step.md) - Type alias `Step` in `application/data_steps`.
* [application.data_steps.apply_data](/symbols/application/data_steps/apply_data.md) - `data` with the data-model steps applied in turn, checked by the data model's own contract; `data` when none.
* [application.data_steps.describe_data](/symbols/application/data_steps/describe_data.md) - One line a person can check against the class diagram.
* [application.data_steps.split](/symbols/application/data_steps/split.md) - The kernel transactions and the data-model steps, each in plan order.
* [application.data_steps.with_kinds](/symbols/application/data_steps/with_kinds.md) - `pack` with the roles' kinds these steps set, a draft held in memory; `PLAN_KIND_FIXED` on a system with a law about kinds, and `EDIT_INVALID` for a role the p…
<!-- okf:generated:end links -->
