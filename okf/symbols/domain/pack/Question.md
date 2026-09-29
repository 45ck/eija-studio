---
type: Class
title: domain.pack.Question
description: A meaning-check question for the owner.
resource: repo://src/eija_studio/domain/pack.py#Question
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#Question
  title: domain/pack.py
  hash_method: ast-sig-v1
  sha256: 1ed35d11b6631469986d9ed939a49e0342becf5be32a6373f901b30b26c07335
notes_baseline: 3bf2aafcfd398c4dd1714b8c04af3720673a2d04fa4c61062fc4fff97f38d29f
---

# domain.pack.Question

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `class Question(Contract)` |
| Code | `repo://src/eija_studio/domain/pack.py#Question` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
A meaning-check question for the owner. The expected answer is literal, or read from a transition field.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `id` | `str` | `Field(pattern='^[a-z][a-z0-9_]{0,39}$')` |
| `question` | `str` | `Field(min_length=1, max_length=400)` |
| `expected` | `str \| None` | `Field(default=None, max_length=120)` |
| `expected_from` | `tuple[str, Literal['from_state', 'to_state', 'role']] \| None` | `None` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [domain.pack.Journey](/symbols/domain/pack/Journey.md) - `class Journey(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
