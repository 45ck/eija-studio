---
type: Class
title: domain.laws.StateOnlyVia
description: Every transition entering ``state`` performs one of ``actions``.
resource: repo://src/eija_studio/domain/laws.py#StateOnlyVia
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#StateOnlyVia
  title: domain/laws.py
  hash_method: ast-sig-v1
  sha256: a4803ec1de8894b694285497a97ce034c1d6867866f54a00d6c12538970d9ab2
notes_baseline: dfd7b7e280189ac9c34fd3ed72794a7651aa77d300bf8e8d517fbbf3d7a2c71c
---

# domain.laws.StateOnlyVia

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `class StateOnlyVia(_Law)` |
| Code | `repo://src/eija_studio/domain/laws.py#StateOnlyVia` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Every transition entering ``state`` performs one of ``actions``.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['state_only_via']` |  |
| `state` | `Name` |  |
| `actions` | `tuple[Name, ...]` | `Field(min_length=1)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.Name](/symbols/domain/laws/Name.md) - Type alias `Name` in `domain/laws`.

## Referenced by

* [domain.laws.Law](/symbols/domain/laws/Law.md) - Type alias `Law` in `domain/laws`.
<!-- okf:generated:end links -->
