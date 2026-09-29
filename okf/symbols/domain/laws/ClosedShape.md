---
type: Class
title: domain.laws.ClosedShape
description: The workflow has exactly these states and actions and this initial state.
resource: repo://src/eija_studio/domain/laws.py#ClosedShape
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#ClosedShape
  title: domain/laws.py
  hash_method: ast-sig-v1
  sha256: 0f144f4faf0b3189ba47012a0dc340ad09676725bfcad36c77af6c801489e287
notes_baseline: 7ae92f17d547527206793340ebc4c55e94a2b8cbce43ddf497b1246773530f51
---

# domain.laws.ClosedShape

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `class ClosedShape(_Law)` |
| Code | `repo://src/eija_studio/domain/laws.py#ClosedShape` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
The workflow has exactly these states and actions and this initial state.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['closed_shape']` |  |
| `states` | `tuple[Name, ...]` | `Field(min_length=1)` |
| `actions` | `tuple[Name, ...]` | `Field(min_length=1)` |
| `initial_state` | `Name` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.Name](/symbols/domain/laws/Name.md) - Type alias `Name` in `domain/laws`.

## Referenced by

* [domain.laws.Law](/symbols/domain/laws/Law.md) - Type alias `Law` in `domain/laws`.
<!-- okf:generated:end links -->
