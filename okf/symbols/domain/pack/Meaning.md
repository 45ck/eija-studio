---
type: Class
title: domain.pack.Meaning
description: One interpretation of a request.
resource: repo://src/eija_studio/domain/pack.py#Meaning
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#Meaning
  title: domain/pack.py
  hash_method: ast-sig-v1
  sha256: d9b9d4109ad36201fef4bc9ea1267cd1be80560c4fbc41362688192e105fb8c3
notes_baseline: f5aacf7fda95eb28be215c2874ee3c0e1750fd5064b783e6ac8d9f43e854e72d
---

# domain.pack.Meaning

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `class Meaning(Contract)` |
| Code | `repo://src/eija_studio/domain/pack.py#Meaning` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
One interpretation of a request. A supported meaning's transactions produce the candidate; an unsupported
one's transactions (if any) describe what it WOULD do, for explanation only, never as a candidate.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `id` | `str` | `Field(pattern=MEANING_ID)` |
| `label` | `str` | `Field(min_length=1, max_length=200)` |
| `supported` | `bool` |  |
| `consequences` | `tuple[str, ...]` | `Field(min_length=1)` |
| `transactions` | `tuple[dict[str, Any], ...]` | `()` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.models.MEANING_ID](/symbols/domain/models/MEANING_ID.md) - Constant `MEANING_ID` in `domain/models`.

## Referenced by

* [Meaning Selection](/language/meaning-selection.md) - A local owner's explicit choice of one canonical supported interpretation.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.Pack.meaning](/symbols/domain/pack/Pack.meaning.md) - `def meaning(self, meaning_id: str) -> Meaning | None` in `domain/pack`.
<!-- okf:generated:end links -->
