---
type: Class
title: domain.laws.ForbiddenEffects
description: No transition requires any of ``effects`` and every transition declares them forbidden.
resource: repo://src/eija_studio/domain/laws.py#ForbiddenEffects
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#ForbiddenEffects
  title: domain/laws.py
  hash_method: ast-sig-v1
  sha256: db4ad48e43db5f33d6dc42c7ea5944271cc2be96f227f3c762d43f4e962e5eed
notes_baseline: 245ec89ff8a2138f29e888d7ca27d19b467e214cdae8da59b9ff397b94a9cab7
---

# domain.laws.ForbiddenEffects

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `class ForbiddenEffects(_Law)` |
| Code | `repo://src/eija_studio/domain/laws.py#ForbiddenEffects` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
No transition requires any of ``effects`` and every transition declares them forbidden.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['forbidden_effects']` |  |
| `effects` | `tuple[Name, ...]` | `Field(min_length=1)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.Name](/symbols/domain/laws/Name.md) - Type alias `Name` in `domain/laws`.

## Referenced by

* [domain.laws.Law](/symbols/domain/laws/Law.md) - Type alias `Law` in `domain/laws`.
<!-- okf:generated:end links -->
