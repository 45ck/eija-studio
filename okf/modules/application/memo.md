---
type: Module
title: application.memo
description: Ask the kernel the same question of the same frozen model once (ADR-0191).
resource: repo://src/eija_studio/application/memo.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/memo.py
  title: application/memo.py
  hash_method: ast-api-v1
  sha256: 7cc2ffb30f9dcccbbb9d02560f1468335cb75007a94ce198a1bed779b91cb6bd
notes_baseline: 3a144f7f792a3d2d6fe909045406e3d18fc84f14adbb6e3d1402077fce429508
---

# application.memo

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/memo.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Ask the kernel the same question of the same frozen model once (ADR-0191).

Building an app's oracle or proving a pack's laws runs `runtime.execute` tens of thousands of times on one unchanged
model, and every run checked the whole model against the policy and hashed it again: over 95 % of the time at the
kernel's limits. A `Workflow` and a `Pack` are frozen after validation, so the same objects always get the same
answer. The answers are kept by the objects' identity, and the memo holds the objects themselves, so an id is never
reused for another object while its entry exists. A copy or an edit is a new object and is asked afresh. The domain's
own functions are unchanged; a refusal still comes from `ensure_policy` itself.
~~~

## Public symbols

* [`IdentityMemo`](/symbols/application/memo/IdentityMemo.md) (class) - A small, bounded memo for pure functions of frozen contracts, keyed by the identity of the arguments.
* [`ensure_conforms`](/symbols/application/memo/ensure_conforms.md) (function) - `ensure(model, pack)` (the policy check): a pair it let through is remembered; any other is refused by it again, so the…
* [`model_hash`](/symbols/application/memo/model_hash.md) (function) - `model.semantic_hash`, computed once per model object.

## Internal imports

* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [application.appgen](/modules/application/appgen.md) - App generation: a reviewed workflow model becomes a runnable app and its conformance oracle (ADR-0150).
* [application.law_proof](/modules/application/law_proof.md) - Prove a pack's laws over every run the kernel allows (ADR-0166).
* [application.runtime](/modules/application/runtime.md) - Generic execution algorithm; the domain (policy, laws, typed effects) comes from the pack.
* [application.memo.IdentityMemo.get](/symbols/application/memo/IdentityMemo.get.md) - `def get(self, args: tuple[Any, ...], compute: Callable[[], _T]) -> _T` in `application/memo`.
* [application.memo.IdentityMemo](/symbols/application/memo/IdentityMemo.md) - A small, bounded memo for pure functions of frozen contracts, keyed by the identity of the arguments.
* [application.memo.ensure_conforms](/symbols/application/memo/ensure_conforms.md) - `ensure(model, pack)` (the policy check): a pair it let through is remembered; any other is refused by it again, so the error is always the check's own.
* [application.memo.model_hash](/symbols/application/memo/model_hash.md) - `model.semantic_hash`, computed once per model object.
<!-- okf:generated:end links -->
