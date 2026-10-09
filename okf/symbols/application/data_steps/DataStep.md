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
  sha256: 9678bd96a5c48f3502669594d42b4df30cd13c89130e0e6b798bbc764dac385b
notes_baseline: e805a6dd2f9b08ba1d9ab6696f064af29d9672a2678b1cc8b79e1f4bcda68e55
---

# application.data_steps.DataStep

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | type-alias |
| Module | [`application/data_steps`](/modules/application/data_steps.md) |
| Signature | `DataStep = Annotated[Union[AddAttribute, RemoveAttribute, SetRequired, SetRoleKind], Field(discriminator='kind')]` |
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
* [application.data_steps.SetRoleKind](/symbols/application/data_steps/SetRoleKind.md) - Make the actor holding `role` a person, an AI agent, a timer or an external system (ADR-0210).
<!-- okf:generated:end links -->
