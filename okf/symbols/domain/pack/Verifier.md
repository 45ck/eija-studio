---
type: Class
title: domain.pack.Verifier
description: An evidence kind that applies to this pack.
resource: repo://src/eija_studio/domain/pack.py#Verifier
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#Verifier
  title: domain/pack.py
  hash_method: ast-sig-v1
  sha256: aa06f2732f58b3bdb5df967934e7730432c93e7f939dfde9053254fb65fbd8d9
notes_baseline: b3786cefdbb2c797327b791e3417e67ae68976cb034c3ab54260154161a15deb
---

# domain.pack.Verifier

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `class Verifier(Contract)` |
| Code | `repo://src/eija_studio/domain/pack.py#Verifier` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
An evidence kind that applies to this pack. ``hand_encoded`` marks a hand-written formal model of the pack;
``not_run`` records that the kind is deliberately not produced for this pack, with the reason.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `str` | `Field(pattern='^[a-z][a-z0-9_]{0,39}$')` |
| `mode` | `Literal['kernel', 'hand_encoded', 'not_run']` |  |
| `reason` | `str` | `Field(default='', max_length=400)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
