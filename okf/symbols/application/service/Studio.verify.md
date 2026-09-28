---
type: Method
title: application.service.Studio.verify
description: Runs the runtime matrix in a sandbox and stores a sealed receipt; refuses a source that differs from the release fixture.
resource: repo://src/eija_studio/application/service.py#Studio.verify
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.verify
  title: application/service.py
  hash_method: ast-v2
  sha256: ee1f0955b4ae434667ae13a4369c23b4a24e96bbae4a5a1979dedb76d6f38728
description_override: Runs the runtime matrix in a sandbox and stores a sealed receipt; refuses a source that differs from the release fixture.
notes_baseline: cb447b283609e7331c899eaed3407cebf36e002697082810e06650c5e036b38f
---

# application.service.Studio.verify

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def verify(self, case_id: str, expected: int) -> dict` |
| Code | `repo://src/eija_studio/application/service.py#Studio.verify` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Verification clears any current decision and never approves. See [verify_runtime](/symbols/application/verifier/verify_runtime.md) and [Evidence Receipt](/language/evidence-receipt.md).

<!-- okf:generated:begin links -->
## Depends on

* [application.compiler.subject_for](/symbols/application/compiler/subject_for.md) - `def subject_for(model: Workflow, layout: dict, identity: dict) -> dict` in `application/compiler`.
* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict, sandbox: SandboxFactory) -> dict` in `application/verifier`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
<!-- okf:generated:end links -->
