---
type: Class
title: domain.pack.Fixtures
description: '`class Fixtures(Contract)` in `domain/pack`.'
resource: repo://src/eija_studio/domain/pack.py#Fixtures
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#Fixtures
  title: domain/pack.py
  hash_method: ast-sig-v1
  sha256: 946f4ce9fd083d3b921719420e8c7eda3c424668eb13bc7b16021a9649f9d285
notes_baseline: 4f06de5a6cf963f84d4ae206d30e5b9e8181ac161d6cbff9cfff996709f22e01
---

# domain.pack.Fixtures

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `class Fixtures(Contract)` |
| Code | `repo://src/eija_studio/domain/pack.py#Fixtures` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `actors` | `tuple[Actor, ...]` | `Field(min_length=1)` |
| `proposals` | `Proposals` |  |
| `demo_request` | `str` | `Field(min_length=1, max_length=6000)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.pack.Actor](/symbols/domain/pack/Actor.md) - `class Actor(Contract)` in `domain/pack`.
* [domain.pack.Proposals](/symbols/domain/pack/Proposals.md) - `class Proposals(Contract)` in `domain/pack`.

## Referenced by

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
