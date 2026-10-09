---
type: Type Alias
title: domain.laws.RoleKind
description: Type alias `RoleKind` in `domain/laws`.
resource: repo://src/eija_studio/domain/laws.py#RoleKind
tags:
- symbol
- domain
- type-alias
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#RoleKind
  title: domain/laws.py
  hash_method: ast-v2
  sha256: 9d3c44dda5e57bb471e07a4b6635fab8f3ab7dbca2a8c908026c16faf52a6ccf
notes_baseline: a8ccb461576ccfcd840d09f6a8b1169e2626959cc1edbf770d6721eac706f5ab
---

# domain.laws.RoleKind

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | type-alias |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `RoleKind = Literal['human', 'agent', 'timer', 'system']` |
| Code | `repo://src/eija_studio/domain/laws.py#RoleKind` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.data_steps.SetRoleKind](/symbols/application/data_steps/SetRoleKind.md) - Make the actor holding `role` a person, an AI agent, a timer or an external system (ADR-0210).
* [domain.pack.Role](/symbols/domain/pack/Role.md) - A role and the kind of actor that holds it (ADR-0210): a person by default, or an AI agent, a timer or an external system.
<!-- okf:generated:end links -->
