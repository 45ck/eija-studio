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
  sha256: 8ef28ec119bf6ebdbef82c321871ccca4170d721762946127d07ee8e424c5b73
notes_baseline: cff7ed2008be76e7e52f8f949188d8805e4ba3e6858294cae0098eea8082d7ab
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
| `transactions` | `tuple[Transaction, ...]` | `()` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.models.MEANING_ID](/symbols/domain/models/MEANING_ID.md) - Constant `MEANING_ID` in `domain/models`.
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.

## Referenced by

* [Meaning Selection](/language/meaning-selection.md) - A local owner's explicit choice of one canonical supported interpretation.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.Pack.meaning](/symbols/domain/pack/Pack.meaning.md) - `def meaning(self, meaning_id: str) -> Meaning | None` in `domain/pack`.
<!-- okf:generated:end links -->
