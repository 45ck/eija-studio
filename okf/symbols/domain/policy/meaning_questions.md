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
  hash_method: ast-v1
  sha256: 049f5704bdeee8d5c86b5f838bf5f62cb41968435d02f7908ebaebf3e44f2743
description_override: The three critical questions a local owner must answer correctly before a decision is sealed.
---

# domain.policy.meaning_questions

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def meaning_questions(model: Workflow) -> list[dict]` |
| Code | `repo://src/eija_studio/domain/policy.py#meaning_questions` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Authority (Registrar keeps final approval), assignment (an unassigned teacher cannot recommend) and the rejection entry state. Answers are compared with values computed from the model in [Studio.approve](/symbols/application/service/Studio.approve.md). They test attention to consequences; they do not measure human understanding, which stays `UNKNOWN`.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models` (the source has no docstring).

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict, authenticator, active_version: int, scope: str='local-demo') -> dict` in `application/compiler` (the source…
<!-- okf:generated:end links -->
