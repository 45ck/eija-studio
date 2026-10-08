---
type: Class
title: domain.pack.PackInfo
description: '`class PackInfo(Contract)` in `domain/pack`.'
resource: repo://src/eija_studio/domain/pack.py#PackInfo
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#PackInfo
  title: domain/pack.py
  hash_method: ast-sig-v1
  sha256: b00632ec0da3e50a9ff64499d5357e9694435e03374ec83d0226ebeaba068560
notes_baseline: a8f7dcf73a091dd01984f17d5592a9e7c3d048d96477811cddc0b8de828c33c9
---

# domain.pack.PackInfo

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `class PackInfo(Contract)` |
| Code | `repo://src/eija_studio/domain/pack.py#PackInfo` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `id` | `str` | `Field(pattern=PACK_ID)` |
| `name` | `str` | `Field(min_length=1, max_length=120)` |
| `version` | `str` | `Field(pattern='^\\d+\\.\\d+\\.\\d+$')` |
| `description` | `str` | `Field(default='', max_length=2000)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.pack.PACK_ID](/symbols/domain/pack/PACK_ID.md) - Constant `PACK_ID` in `domain/pack`.

## Referenced by

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
