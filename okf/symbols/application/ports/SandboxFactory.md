---
type: Type Alias
title: application.ports.SandboxFactory
description: Opens a disposable verification store that keeps unit-of-work atomicity and is deleted on exit.
resource: repo://src/eija_studio/application/ports.py#SandboxFactory
tags:
- symbol
- application
- type-alias
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/ports.py#SandboxFactory
  title: application/ports.py
  hash_method: ast-v1
  sha256: efd92e3e06baadda81c02bc2893ccc2896ad95a7d539c87c97a2ec784d6a2fca
description_override: Opens a disposable verification store that keeps unit-of-work atomicity and is deleted on exit.
---

# application.ports.SandboxFactory

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | type-alias |
| Module | [`application/ports`](/modules/application/ports.md) |
| Signature | `SandboxFactory = Callable[[], ContextManager[Repository]]` |
| Code | `repo://src/eija_studio/application/ports.py#SandboxFactory` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Owned by the application so [verify_runtime](/symbols/application/verifier/verify_runtime.md) never depends on how a sandbox is built. It need not be durable; receipts state that.

<!-- okf:generated:begin links -->
## Depends on

* [application.ports.Repository](/symbols/application/ports/Repository.md) - `class Repository(Protocol)` in `application/ports` (the source has no docstring).

## Referenced by

* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service` (the source has no docstring).
* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict, sandbox: SandboxFactory) -> dict` in `application/verifier` (the source has no docstring).
<!-- okf:generated:end links -->
