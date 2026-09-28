---
type: Function
title: application.compiler.subject_for
description: 'Builds the exact review subject: implementation, policy, environment and harness identity plus semantic and presentation hashes.'
resource: repo://src/eija_studio/application/compiler.py#subject_for
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/compiler.py#subject_for
  title: application/compiler.py
  hash_method: ast-v1
  sha256: b5cb163af79ce92f8d6708ed8e282c7bba327b891bb766852d91574f1d99a0bd
description_override: 'Builds the exact review subject: implementation, policy, environment and harness identity plus semantic and presentation hashes.'
---

# application.compiler.subject_for

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/compiler`](/modules/application/compiler.md) |
| Signature | `def subject_for(model: Workflow, layout: dict, identity: dict) -> dict` |
| Code | `repo://src/eija_studio/application/compiler.py#subject_for` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

The subject hash is what a [Local Decision](/language/local-decision.md) acknowledges; any change to any dimension changes it (acceptance [AC18](/requirements/ac18.md)).

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models` (the source has no docstring).
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models` (the source has no docstring).

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict, authenticator, active_version: int, scope: str='local-demo') -> dict` in `application/compiler` (the source…
* [application.service.Studio.verify](/symbols/application/service/Studio.verify.md) - `def verify(self, case_id: str, expected: int) -> dict` in `application/service` (the source has no docstring).
<!-- okf:generated:end links -->
