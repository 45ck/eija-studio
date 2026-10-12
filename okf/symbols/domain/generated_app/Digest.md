---
type: Type Alias
title: domain.generated_app.Digest
description: Type alias `Digest` in `domain/generated_app`.
resource: repo://src/eija_studio/domain/generated_app.py#Digest
tags:
- symbol
- domain
- type-alias
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/generated_app.py#Digest
  title: domain/generated_app.py
  hash_method: ast-v2
  sha256: 3adbbe093f6d27a775cd627beadde538e0b020f286124fdca617d94df7701ead
notes_baseline: 6255f4dae9fa23597946eaa05f99183a5849616e2430496e0af8d44d5e8b8ed0
---

# domain.generated_app.Digest

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | type-alias |
| Module | [`domain/generated_app`](/modules/domain/generated_app.md) |
| Signature | `Digest = Annotated[str, Field(pattern='^[a-f0-9]{64}$')]` |
| Code | `repo://src/eija_studio/domain/generated_app.py#Digest` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.generated_app.GeneratedAppActivation](/symbols/domain/generated_app/GeneratedAppActivation.md) - `class GeneratedAppActivation(Contract)` in `domain/generated_app`.
* [domain.generated_app.GeneratedAppBinding](/symbols/domain/generated_app/GeneratedAppBinding.md) - `class GeneratedAppBinding(Contract)` in `domain/generated_app`.
* [domain.generated_app.GeneratedBuildSubject](/symbols/domain/generated_app/GeneratedBuildSubject.md) - `class GeneratedBuildSubject(Contract)` in `domain/generated_app`.
* [domain.generated_app.GeneratedCheckConfiguration](/symbols/domain/generated_app/GeneratedCheckConfiguration.md) - `class GeneratedCheckConfiguration(Contract)` in `domain/generated_app`.
* [domain.generated_app.GeneratedChecker](/symbols/domain/generated_app/GeneratedChecker.md) - `class GeneratedChecker(Contract)` in `domain/generated_app`.
<!-- okf:generated:end links -->
