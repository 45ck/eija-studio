---
type: Class
title: domain.pack.Verifier
description: An evidence kind that applies to this pack (``kind`` is the evidence kind's name).
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
  sha256: e8e6dea32928196522694f05c16452f4756e45291bb44cba72523c1909e44710
notes_baseline: 5e6810219542169d1d4fa6ca6d4c248f699530f4e3029cd8dcf898b384552b07
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
An evidence kind that applies to this pack (``kind`` is the evidence kind's name). ``hand_encoded`` marks a
hand-written formal model of the pack; ``generated`` a model generated from the pack's laws; ``not_run`` records
that the kind is deliberately not produced for this pack, with the reason. Only ``kernel`` and ``hand_encoded``
kinds read the checkout's committed formal reports; every other kind is NOT_RUN in the review packet, with the reason.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `str` | `Field(pattern='^[a-z][a-z0-9_]{0,39}$')` |
| `mode` | `Literal['kernel', 'hand_encoded', 'generated', 'not_run']` |  |
| `reason` | `str` | `Field(default='', max_length=400)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.Pack.verifier](/symbols/domain/pack/Pack.verifier.md) - `def verifier(self, kind: str) -> Verifier | None` in `domain/pack`.
<!-- okf:generated:end links -->
