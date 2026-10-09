---
type: Type Alias
title: application.data_steps.DataStep
description: Type alias `DataStep` in `application/data_steps`.
resource: repo://src/eija_studio/application/data_steps.py#DataStep
tags:
- symbol
- application
- type-alias
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/data_steps.py#DataStep
  title: application/data_steps.py
  hash_method: ast-v2
  sha256: 0f3998e29cfa15305a6b695c716f5debfe5a42f665556f3ff8acd2fe9cce8676
notes_baseline: 30d56e1c9fabe8ac8d6d32476c9285b3f0d776eaca04687564865b33df5af0b7
---

# application.data_steps.DataStep

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | type-alias |
| Module | [`application/data_steps`](/modules/application/data_steps.md) |
| Signature | `DataStep = Annotated[Union[AddAttribute, RemoveAttribute, SetRequired], Field(discriminator='kind')]` |
| Code | `repo://src/eija_studio/application/data_steps.py#DataStep` |
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
<!-- okf:generated:end links -->
