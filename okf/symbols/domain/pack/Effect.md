---
type: Class
title: domain.pack.Effect
description: A typed effect.
resource: repo://src/eija_studio/domain/pack.py#Effect
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#Effect
  title: domain/pack.py
  hash_method: ast-sig-v1
  sha256: 2ec5f889acc94b38d0ab51c3bc4acd014d8a80e9c9620c47d55612814d4f375f
notes_baseline: 82fc2396e4dc9d3a909df18abca01036ee7c86a621727880b68af311a7306f47
---

# domain.pack.Effect

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `class Effect(Contract)` |
| Code | `repo://src/eija_studio/domain/pack.py#Effect` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
A typed effect. ``audit`` is written to the audit log, ``notification`` to the outbox for ``recipient``.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `id` | `str` | `Field(min_length=1, max_length=80)` |
| `kind` | `Literal['audit', 'notification']` |  |
| `recipient` | `str \| None` | `Field(default=None, max_length=60)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [Effect Intent](/language/effect-intent.md) - A transactionally queued synthetic notification or audit append.
* [domain.pack.Effects](/symbols/domain/pack/Effects.md) - `class Effects(Contract)` in `domain/pack`.
* [domain.pack.Pack.effect](/symbols/domain/pack/Pack.effect.md) - `def effect(self, effect_id: str) -> Effect | None` in `domain/pack`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
