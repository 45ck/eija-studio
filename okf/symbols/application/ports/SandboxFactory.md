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
  hash_method: ast-v2
  sha256: 346f2bae4ba49c05fc0a1ab153ed9a6bd4861f727e5d3114dbc284e58b8e923b
description_override: Opens a disposable verification store that keeps unit-of-work atomicity and is deleted on exit.
notes_baseline: 3ddf1eba22456ac9c68e5160dab729930bd0385c44213aacc1ac677398c37710
---

# application.ports.SandboxFactory

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | type-alias |
| Module | [`application/ports`](/modules/application/ports.md) |
| Signature | `SandboxFactory = Callable[[], ContextManager[Repository]]` |
| Code | `repo://src/eija_studio/application/ports.py#SandboxFactory` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Owned by the application so [verify_runtime](/symbols/application/verifier/verify_runtime.md) never depends on how a sandbox is built. It need not be durable; receipts state that.

<!-- okf:generated:begin links -->
## Depends on

* [application.ports.Repository](/symbols/application/ports/Repository.md) - `class Repository(Protocol)` in `application/ports`.

## Referenced by

* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service`.
* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict[str, Any], sandbox: SandboxFactory) -> dict[str, Any]` in `application/verifier`.
<!-- okf:generated:end links -->
