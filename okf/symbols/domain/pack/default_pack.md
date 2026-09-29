---
type: Function
title: domain.pack.default_pack
description: The configured pack (cached per location).
resource: repo://src/eija_studio/domain/pack.py#default_pack
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#default_pack
  title: domain/pack.py
  hash_method: ast-v2
  sha256: 9fd31d713eb6cbd5d717877cde3d7b728c173c3e6cf6d0d54fadd0f7055b99a5
notes_baseline: e06d5cc15f22b2189a4185a342d7c77fff145b866b26ee5cd44ff24041d255d4
---

# domain.pack.default_pack

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `def default_pack() -> Pack` |
| Code | `repo://src/eija_studio/domain/pack.py#default_pack` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The configured pack (cached per location).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.default_location](/symbols/domain/pack/default_location.md) - ``$EIJA_PACK`` if set, else the pack named by ``packs/default.json``.

## Referenced by

* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault: Callable[[…` in `application/runtime`.
* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict[str, Any], sandbox: SandboxFactory, pack: Pack | None=None)…` in `application/verifier`.
* [domain.evidence.runtime_shape](/symbols/domain/evidence/runtime_shape.md) - `def runtime_shape(context: Context | None) -> RuntimeShape` in `domain/evidence`.
<!-- okf:generated:end links -->
