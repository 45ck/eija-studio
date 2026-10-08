---
type: Function
title: application.law_proof.actor_classes
description: One actor per role (declared or used) and per combination of `active` and `assigned`, and an outsider.
resource: repo://src/eija_studio/application/law_proof.py#actor_classes
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/law_proof.py#actor_classes
  title: application/law_proof.py
  hash_method: ast-v2
  sha256: 4121f85ec5ff312ff19f55cb0d98c851d06d5cb20f32d1486121d4192ce9ebdd
notes_baseline: 3b0690728e59b0bb51487d46c6cc918896e9d0f66c413ecdbf8cd0a6d7bb2185
---

# application.law_proof.actor_classes

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/law_proof`](/modules/application/law_proof.md) |
| Signature | `def actor_classes(pack: Pack, model: Workflow) -> list[dict[str, Any]]` |
| Code | `repo://src/eija_studio/application/law_proof.py#actor_classes` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
One actor per role (declared or used) and per combination of `active` and `assigned`, and an outsider.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.law_proof.OUTSIDER](/symbols/application/law_proof/OUTSIDER.md) - Constant `OUTSIDER` in `application/law_proof`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
