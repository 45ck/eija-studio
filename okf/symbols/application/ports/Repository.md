---
type: Class
title: application.ports.Repository
description: '`class Repository(Protocol)` in `application/ports`.'
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
  sha256: 0f905eb7198e6f9a1b3377c40c0f05cc67ba473b73ac8851edb415eef3837833
notes_baseline: 8ab858c61846c3208882d322d85d8ecfd8cb088c56f232ce9d8abb5b6637a4f3
---

# application.ports.Repository

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/ports`](/modules/application/ports.md) |
| Signature | `class Repository(Protocol)` |
| Code | `repo://src/eija_studio/application/ports.py#Repository` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `directory` | `Path` |  |

## Protocol members

Structural interface implemented by adapters; not a class to instantiate.

* `def transaction(self) -> ContextManager[UnitOfWork]`
* `def list_cases(self) -> list[dict[str, Any]]`
* `def backup(self, target: Path) -> None`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.ports.UnitOfWork](/symbols/application/ports/UnitOfWork.md) - All mutations on this port commit together or roll back together.

## Referenced by

* [application.ports.SandboxFactory](/symbols/application/ports/SandboxFactory.md) - Type alias `SandboxFactory` in `application/ports`.
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service`.
<!-- okf:generated:end links -->
