---
type: Class
title: application.ports.Repository
description: '`class Repository(Protocol)` in `application/ports` (the source has no docstring).'
resource: repo://src/eija_studio/application/ports.py#Repository
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/ports.py#Repository
  title: application/ports.py
  hash_method: ast-sig-v1
  sha256: 19a4b18761ea27770d53e7482ff0204bf6953b9a2c40c8605dd75e14bbf8e6cf
---

# application.ports.Repository

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/ports`](/modules/application/ports.md) |
| Signature | `class Repository(Protocol)` |
| Code | `repo://src/eija_studio/application/ports.py#Repository` |
| Hash | `ast-sig-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `directory` | `Path` |  |

## Protocol members

Structural interface implemented by adapters; not a class to instantiate.

* `def transaction(self) -> ContextManager[UnitOfWork]`
* `def list_cases(self) -> list[dict]`
* `def backup(self, target: Path) -> None`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.ports.UnitOfWork](/symbols/application/ports/UnitOfWork.md) - All mutations on this port commit together or roll back together.

## Referenced by

* [application.ports.SandboxFactory](/symbols/application/ports/SandboxFactory.md) - `SandboxFactory = Callable[[], ContextManager[Repository]]` in `application/ports` (the source has no docstring).
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service` (the source has no docstring).
<!-- okf:generated:end links -->
