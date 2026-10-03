---
type: Class
title: domain.pack.Effects
description: '`class Effects(Contract)` in `domain/pack`.'
resource: repo://src/eija_studio/domain/pack.py#Effects
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#Effects
  title: domain/pack.py
  hash_method: ast-sig-v1
  sha256: f2d575eff3284a2ebedd5cd705e1cb9a1782e3be68f38f737fc6834d8fd4e7a1
notes_baseline: b4ff220970a2d022c3bb7bf194b638c66e4e0067dedc5236510a33886da28481
---

# domain.pack.Effects

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `class Effects(Contract)` |
| Code | `repo://src/eija_studio/domain/pack.py#Effects` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `catalog` | `tuple[Effect, ...]` | `()` |
| `forbidden` | `tuple[str, ...]` | `()` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.pack.Effect](/symbols/domain/pack/Effect.md) - A typed effect.

## Referenced by

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
