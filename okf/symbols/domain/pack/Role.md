---
type: Class
title: domain.pack.Role
description: '`class Role(Contract)` in `domain/pack`.'
resource: repo://src/eija_studio/domain/pack.py#Role
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#Role
  title: domain/pack.py
  hash_method: ast-sig-v1
  sha256: 916ed50a6be5371aaf1417a309fb792a0b62286f1bbfa048955503e7935059cb
notes_baseline: 8c140cd4128dec144bf21705aef32c9ce4f872231cc3d9c1c2fc8cc16be3161a
---

# domain.pack.Role

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `class Role(Contract)` |
| Code | `repo://src/eija_studio/domain/pack.py#Role` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `id` | `str` | `Field(min_length=1, max_length=60)` |
| `description` | `str` | `Field(default='', max_length=400)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
