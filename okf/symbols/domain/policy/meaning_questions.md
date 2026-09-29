---
type: Function
title: domain.policy.meaning_questions
description: The three critical questions a local owner must answer correctly before a decision is sealed.
resource: repo://src/eija_studio/domain/policy.py#meaning_questions
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#meaning_questions
  title: domain/policy.py
  hash_method: ast-v2
  sha256: f572a456387fe360c0583269cb7b67fb193b51d7aedde39235904d7518e3168d
description_override: The three critical questions a local owner must answer correctly before a decision is sealed.
notes_baseline: 2758810cf1fa8438c38d7f1c311b4324c4d79afcd1161816f4a664a3205bdd29
---

# domain.policy.meaning_questions

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def meaning_questions(model: Workflow) -> list[dict[str, Any]]` |
| Code | `repo://src/eija_studio/domain/policy.py#meaning_questions` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Authority (Registrar keeps final approval), assignment (an unassigned teacher cannot recommend) and the rejection entry state. Answers are compared with values computed from the model in [Studio.approve](/symbols/application/service/Studio.approve.md). They test attention to consequences; they do not measure human understanding, which stays `UNKNOWN`.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
<!-- okf:generated:end links -->
