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
  sha256: 885ec425f5a64c94bafe054e96207298dcce1094e283b69bd8f8e22f39463ece
notes_baseline: 312d1abf153e84fe0d0a5a97d416c87ab45b25b1e22e1c4182d0282c33a248df
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
A typed effect. ``audit`` is written to the audit log, ``notification`` to the outbox for ``recipient``, and
``signal`` to the outbox for the workflow ``recipient`` names, another pack of the system (ADR-0242).
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `id` | `str` | `Field(min_length=1, max_length=80)` |
| `kind` | `Literal['audit', 'notification', 'signal']` |  |
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
