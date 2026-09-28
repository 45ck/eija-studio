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
  hash_method: ast-v2
  sha256: 74f7dd06322a42198c7c78d812c77c3296f08449549ff4247df513a4c0df3068
description_override: 'Builds the exact review subject: implementation, policy, environment and harness identity plus semantic and presentation hashes.'
notes_baseline: 17dd0240f2faff1218d76025bf6f7d3f864379d7a998b060869afbccd2366813
---

# application.compiler.subject_for

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/compiler`](/modules/application/compiler.md) |
| Signature | `def subject_for(model: Workflow, layout: dict, identity: dict) -> dict` |
| Code | `repo://src/eija_studio/application/compiler.py#subject_for` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

The subject hash is what a [Local Decision](/language/local-decision.md) acknowledges; any change to any dimension changes it (acceptance [AC18](/requirements/ac18.md)).

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict, authenticator, active_version: int, scope: str='local-demo…` in `application/compiler`.
* [application.service.Studio.verify](/symbols/application/service/Studio.verify.md) - `def verify(self, case_id: str, expected: int) -> dict` in `application/service`.
<!-- okf:generated:end links -->
