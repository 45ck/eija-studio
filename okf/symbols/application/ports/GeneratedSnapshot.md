---
type: Type Alias
title: application.ports.GeneratedSnapshot
description: Type alias `GeneratedSnapshot` in `application/ports`.
resource: repo://src/eija_studio/application/ports.py#GeneratedSnapshot
tags:
- symbol
- application
- type-alias
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/ports.py#GeneratedSnapshot
  title: application/ports.py
  hash_method: ast-v2
  sha256: 295a6562c8d6485e923d9ac5aa2c38b170517c4a419edb53496ff2ee87ed8bea
notes_baseline: 08c3468b0a4b9bfa5cffaca4ff259d3fe35717ba204e13c28f9b50d6243630d6
---

# application.ports.GeneratedSnapshot

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | type-alias |
| Module | [`application/ports`](/modules/application/ports.md) |
| Signature | `GeneratedSnapshot = Callable[[Pack, Workflow, dict[str, str], dict[str, Any], dict[str, Any]], tuple[dict[str, str], dict[str, Any], GeneratedAppBinding]]` |
| Code | `repo://src/eija_studio/application/ports.py#GeneratedSnapshot` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.generated_app.GeneratedAppBinding](/symbols/domain/generated_app/GeneratedAppBinding.md) - `class GeneratedAppBinding(Contract)` in `domain/generated_app`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
