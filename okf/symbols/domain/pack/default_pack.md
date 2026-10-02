---
type: Function
title: domain.pack.default_pack
description: The configured pack, reread on every call and validated from a content-keyed cache.
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
  sha256: e6fdda20d9b55846a346d12253ec8502316463d2b04378368ce139dbbecddf69
notes_baseline: df305f6c4e3da4d4354c5f7c839e9847af708101e13708419c298ccb34307f4d
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
The configured pack, reread on every call and validated from a content-keyed cache.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.default_location](/symbols/domain/pack/default_location.md) - ``$EIJA_PACK`` if set, else the pack named by ``packs/default.json``.
* [domain.pack.load_pack](/symbols/domain/pack/load_pack.md) - Read current file contents and retain an immutable, digest-addressed pack snapshot.

## Referenced by

* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault: Callable[[…` in `application/runtime`.
* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict[str, Any], sandbox: SandboxFactory, pack: Pack | None=None)…` in `application/verifier`.
* [domain.evidence.runtime_shape](/symbols/domain/evidence/runtime_shape.md) - `def runtime_shape(context: Context | None) -> RuntimeShape` in `domain/evidence`.
<!-- okf:generated:end links -->
