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
  sha256: 438675367e95fa91f60dd3d98b60a7b9e78f0760a2b84c08c370c8549b71a7eb
description_override: The three critical questions a local owner must answer correctly before a decision is sealed.
notes_baseline: 9e7f24f52a5f9f8c5271b0e92c75faee7fab6c894a322689c743d803fa5109c2
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: e3922bd5e5107b8ef013a6dfc2d615dcc926e58e63e39302dc77ac131bf7c2ab
  sources_sha256: 2f18d658e9ce1c11e6d87ec5caebb432d523c91ee50aafbfaf53b6aaaca37d5a
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: fd6c2a26ed180a873ae4e5f23579e0f02dd676c83443f404418dd507c6d2712e
  sources_sha256: 9e7f24f52a5f9f8c5271b0e92c75faee7fab6c894a322689c743d803fa5109c2
---

# domain.policy.meaning_questions

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def meaning_questions(model: Workflow, pack: Pack \| None=None) -> list[dict[str, Any]]` |
| Code | `repo://src/eija_studio/domain/policy.py#meaning_questions` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The pack's meaning-check questions, with expected answers read from the model where the pack says so.
~~~
<!-- okf:generated:end facts -->

## Notes

The pack's journey questions (for the excursion pack: authority, assignment and the rejection entry state), with expected answers literal or read from a transition field of the model. Answers are compared in [Studio.approve](/symbols/application/service/Studio.approve.md). They test attention to consequences; they do not measure human understanding, which stays `UNKNOWN`.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
<!-- okf:generated:end links -->
