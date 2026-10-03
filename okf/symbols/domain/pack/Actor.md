---
type: Class
title: domain.pack.Actor
description: '`class Actor(Contract)` in `domain/pack`.'
resource: repo://src/eija_studio/domain/pack.py#Actor
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#Actor
  title: domain/pack.py
  hash_method: ast-sig-v1
  sha256: a0d9fa887fb95efef13aa9547c7744ebdcf29165f8e12fb5bd60d0c8f1a09239
notes_baseline: 119741ef2a2a239a69efc31c42f8e56c03995b158bf218bf31aabb771503e2e9
---

# domain.pack.Actor

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `class Actor(Contract)` |
| Code | `repo://src/eija_studio/domain/pack.py#Actor` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `id` | `str` | `Field(min_length=1, max_length=80)` |
| `role` | `str` | `Field(min_length=1, max_length=60)` |
| `active` | `bool` |  |
| `assigned` | `bool` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [domain.pack.Fixtures](/symbols/domain/pack/Fixtures.md) - `class Fixtures(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
