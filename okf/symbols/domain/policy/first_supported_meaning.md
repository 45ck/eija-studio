---
type: Function
title: domain.policy.first_supported_meaning
description: The id of the pack's first supported meaning (the demo candidate's meaning).
resource: repo://src/eija_studio/domain/policy.py#first_supported_meaning
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#first_supported_meaning
  title: domain/policy.py
  hash_method: ast-v2
  sha256: c0ab30c7e4a79af4e9d4691c3e60dd1f903bd100a2739648d81e36842b8ec6a7
notes_baseline: f25e9b30a479dcdad71810382b26dc672fdf532255278f9e3e82421a5f1ff379
---

# domain.policy.first_supported_meaning

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def first_supported_meaning(pack: Pack \| None=None) -> str` |
| Code | `repo://src/eija_studio/domain/policy.py#first_supported_meaning` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The id of the pack's first supported meaning (the demo candidate's meaning).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [domain.policy.apply_transaction](/symbols/domain/policy/apply_transaction.md) - Apply one transaction (policy-checked).
* [domain.policy.demo_candidate](/symbols/domain/policy/demo_candidate.md) - The pack's baseline with its first supported meaning applied.
<!-- okf:generated:end links -->
