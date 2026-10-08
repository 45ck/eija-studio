---
type: Function
title: application.law_proof.with_laws
description: The pack with its law file replaced by `laws` (a draft edited in PlayIDE), checked as the pack loader checks it.
resource: repo://src/eija_studio/application/law_proof.py#with_laws
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/law_proof.py#with_laws
  title: application/law_proof.py
  hash_method: ast-v2
  sha256: 067746be23b790a7cf39c50d151b4d7889bb50058556e2f32ab615d42a69b44d
notes_baseline: 66b5170013f39c5020329cf15fe25d57c9223665cc4c189116f12024f9390f01
---

# application.law_proof.with_laws

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/law_proof`](/modules/application/law_proof.md) |
| Signature | `def with_laws(pack: Pack, laws: list[Any]) -> Pack` |
| Code | `repo://src/eija_studio/application/law_proof.py#with_laws` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The pack with its law file replaced by `laws` (a draft edited in PlayIDE), checked as the pack loader checks it.

Nothing is saved: the draft is proved and shown, and the person decides whether to write it into `pack.json`.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.PackError](/symbols/domain/pack/PackError.md) - A pack that cannot be used.
* [domain.pack.parse_pack](/symbols/domain/pack/parse_pack.md) - Validate a decoded JSON document as a pack.
<!-- okf:generated:end links -->
