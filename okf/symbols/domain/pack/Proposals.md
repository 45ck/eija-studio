---
type: Class
title: domain.pack.Proposals
description: '`class Proposals(Contract)` in `domain/pack`.'
resource: repo://src/eija_studio/domain/pack.py#Proposals
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#Proposals
  title: domain/pack.py
  hash_method: ast-sig-v1
  sha256: d0eebbad11933b705915c4463f66f0ad631a4a92040eb650b1115e3c3046481d
notes_baseline: b5412685c3594c11824c2993f4cfcd5062c4053b409dea0f51a2aac9a83f094f
---

# domain.pack.Proposals

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `class Proposals(Contract)` |
| Code | `repo://src/eija_studio/domain/pack.py#Proposals` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `summary` | `str` | `Field(min_length=1, max_length=1600)` |
| `rules` | `tuple[ProposalRule, ...]` | `()` |
| `fallback` | `tuple[Alternative, ...]` | `Field(min_length=1, max_length=4)` |
| `unknowns` | `tuple[str, ...]` | `Field(default=(), max_length=10)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Alternative](/symbols/domain/models/Alternative.md) - `class Alternative(Contract)` in `domain/models`.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.pack.ProposalRule](/symbols/domain/pack/ProposalRule.md) - Offline fixture: when the lower-cased request contains every ``all`` word and at least one ``any`` word.

## Referenced by

* [domain.pack.Fixtures](/symbols/domain/pack/Fixtures.md) - `class Fixtures(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
