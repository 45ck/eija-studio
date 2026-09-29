---
type: Function
title: domain.policy.what_if
description: What an UNSUPPORTED meaning would do to ``model`` (structure only, never a candidate), or None when it declares no transactions or they do not even apply structurally.
resource: repo://src/eija_studio/domain/policy.py#what_if
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#what_if
  title: domain/policy.py
  hash_method: ast-v2
  sha256: 4430fb2e8d7a7c799ea27d08ad3ee254a63bf6a9a931711928362c3d17b2b1c3
notes_baseline: d7ac9b7b93bf1deedc9afd3dd1b464f3c449c37434eebb26a3bd16e8e5f4b253
---

# domain.policy.what_if

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def what_if(model: Workflow, meaning_id: str, pack: Pack \| None=None) -> Workflow \| None` |
| Code | `repo://src/eija_studio/domain/policy.py#what_if` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
What an UNSUPPORTED meaning would do to ``model`` (structure only, never a candidate), or None when it
declares no transactions or they do not even apply structurally.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.policy.apply_structural_all](/symbols/domain/policy/apply_structural_all.md) - ``model`` with every transaction applied in order; structure only, no policy (what-if and meaning previews).

## Referenced by

* [application.formal.what_if_model](/symbols/application/formal/what_if_model.md) - The workflow an unsupported interpretation would produce, or None (supported, unknown, or no transactions).
<!-- okf:generated:end links -->
