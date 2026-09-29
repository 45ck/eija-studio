---
type: Class
title: domain.laws.StateFinal
description: No transition leaves ``state``.
resource: repo://src/eija_studio/domain/laws.py#StateFinal
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#StateFinal
  title: domain/laws.py
  hash_method: ast-sig-v1
  sha256: ca00aad1651a2867e953c5a8a76d043868f6c128c1c0022577dc73932c54c28c
notes_baseline: 53ff5fe90cd21768a5dcb45dd2a1d40d1f043e72ad460d2106a4a219603ad7ff
---

# domain.laws.StateFinal

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `class StateFinal(_Law)` |
| Code | `repo://src/eija_studio/domain/laws.py#StateFinal` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
No transition leaves ``state``.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['state_final']` |  |
| `state` | `Name` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.Name](/symbols/domain/laws/Name.md) - Type alias `Name` in `domain/laws`.

## Referenced by

* [domain.laws.Law](/symbols/domain/laws/Law.md) - Type alias `Law` in `domain/laws`.
<!-- okf:generated:end links -->
