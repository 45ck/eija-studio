---
type: Class
title: domain.laws.RoleNeverHolds
description: No transition performing ``action`` is held by ``role``.
resource: repo://src/eija_studio/domain/laws.py#RoleNeverHolds
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#RoleNeverHolds
  title: domain/laws.py
  hash_method: ast-sig-v1
  sha256: b1f48ddc8f9c7c51f152d5209de486d2bebc4cbca791dc538bcef6eb37689e38
notes_baseline: d3d7301d6ca39cd2527958d2278b2a29ec37528f49a90737b8165dcba9e28337
---

# domain.laws.RoleNeverHolds

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `class RoleNeverHolds(_Law)` |
| Code | `repo://src/eija_studio/domain/laws.py#RoleNeverHolds` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
No transition performing ``action`` is held by ``role``.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['role_never_holds']` |  |
| `action` | `Name` |  |
| `role` | `Name` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.Name](/symbols/domain/laws/Name.md) - Type alias `Name` in `domain/laws`.

## Referenced by

* [domain.laws.Law](/symbols/domain/laws/Law.md) - Type alias `Law` in `domain/laws`.
<!-- okf:generated:end links -->
