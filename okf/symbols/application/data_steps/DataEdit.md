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
  sha256: 9f3e22ee85b7e1ca724d90c0a01f317a589ce3e7d34bdd8c4324059f42504115
notes_baseline: 8de557e56e0ab66ab2ff4d402998b6f89c69abfe15cd273ff5f488d74553d288
---

# application.data_steps.DataEdit

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | type-alias |
| Module | [`application/data_steps`](/modules/application/data_steps.md) |
| Signature | `DataEdit = AddAttribute \| RemoveAttribute \| SetRequired` |
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

## Referenced by

* [application.data_steps.Step](/symbols/application/data_steps/Step.md) - Type alias `Step` in `application/data_steps`.
* [application.data_steps.apply_data](/symbols/application/data_steps/apply_data.md) - `data` with the data-model steps applied in turn, checked by the data model's own contract; `data` when none.
* [application.data_steps.describe_data](/symbols/application/data_steps/describe_data.md) - One line a person can check against the class diagram, or the use case diagram for a role's kind.
* [application.data_steps.split](/symbols/application/data_steps/split.md) - The kernel transactions and the data-model steps, each in plan order (role-kind steps are in neither).
<!-- okf:generated:end links -->
