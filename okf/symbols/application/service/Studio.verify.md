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
  hash_method: ast-v1
  sha256: 1dcdb273a2c0dca8a532cbff1041fb6ec31a65dcbb6e3c2b374c3ed4e6013c5c
description_override: Runs the runtime matrix in a sandbox and stores a sealed receipt; refuses a source that differs from the release fixture.
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
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Verification clears any current decision and never approves. See [verify_runtime](/symbols/application/verifier/verify_runtime.md) and [Evidence Receipt](/language/evidence-receipt.md).

<!-- okf:generated:begin links -->
## Depends on

* [application.compiler.subject_for](/symbols/application/compiler/subject_for.md) - `def subject_for(model: Workflow, layout: dict, identity: dict) -> dict` in `application/compiler` (the source has no docstring).
* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict, sandbox: SandboxFactory) -> dict` in `application/verifier` (the source has no docstring).
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
<!-- okf:generated:end links -->
