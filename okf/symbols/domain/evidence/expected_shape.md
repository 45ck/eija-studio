---
type: Function
title: domain.evidence.expected_shape
description: 'The runtime matrix a receipt must cover under ``pack``: exactly ``model``''s states when it is known.'
resource: repo://src/eija_studio/domain/evidence.py#expected_shape
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/evidence.py#expected_shape
  title: domain/evidence.py
  hash_method: ast-v2
  sha256: 5ad92476b63a39b2ffa025fe3ea8bad6b58de2a0e6579d7f78cbea0995d8d49b
notes_baseline: 5230e11cb9d7d97ff91368c7f44e184f607e60bbfd47bbae00c165e58859b44c
---

# domain.evidence.expected_shape

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/evidence`](/modules/domain/evidence.md) |
| Signature | `def expected_shape(pack: Pack, model: Workflow \| None=None) -> RuntimeShape` |
| Code | `repo://src/eija_studio/domain/evidence.py#expected_shape` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The runtime matrix a receipt must cover under ``pack``: exactly ``model``'s states when it is known.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.formal.RuntimeShape](/symbols/domain/formal/RuntimeShape.md) - What a runtime-matrix receipt for the current subject must cover: the pack's fixture actors and declared actions, and one of the allowed state sets (exactly th…
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.state_sets](/symbols/domain/pack/state_sets.md) - The state sets a workflow of this pack can have: the baseline's, and the baseline's after each supported meaning (states its transactions add or remove).

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
* [domain.evidence.runtime_shape](/symbols/domain/evidence/runtime_shape.md) - `def runtime_shape(context: Context | None) -> RuntimeShape` in `domain/evidence`.
<!-- okf:generated:end links -->
