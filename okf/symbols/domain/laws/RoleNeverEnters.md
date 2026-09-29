---
type: Class
title: domain.laws.RoleNeverEnters
description: No transition held by ``role`` enters ``state``.
resource: repo://src/eija_studio/domain/laws.py#RoleNeverEnters
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#RoleNeverEnters
  title: domain/laws.py
  hash_method: ast-sig-v1
  sha256: 56a342c459f416ed7e4afc217954646ec807e1f695cd1d5a54587379efa1e9cb
notes_baseline: b3349314fa0322d46c731df943dd384364d0116923747fc47d529c7a0b1556ca
---

# domain.laws.RoleNeverEnters

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `class RoleNeverEnters(_Law)` |
| Code | `repo://src/eija_studio/domain/laws.py#RoleNeverEnters` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
No transition held by ``role`` enters ``state``.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['role_never_enters']` |  |
| `role` | `Name` |  |
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
