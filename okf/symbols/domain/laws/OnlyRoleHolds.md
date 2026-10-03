---
type: Class
title: domain.laws.OnlyRoleHolds
description: Every transition performing ``action`` is held by ``role``.
resource: repo://src/eija_studio/domain/laws.py#OnlyRoleHolds
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#OnlyRoleHolds
  title: domain/laws.py
  hash_method: ast-sig-v1
  sha256: 9eda29e05075f59ef1dc7b4a2f908264c33479e0fc2af8cf29b921c8a8e19e8d
notes_baseline: 4728d680c2e3a83c7aa8457310e09ff6f5a44d4d8a8b627dbb0c006de6b22799
---

# domain.laws.OnlyRoleHolds

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `class OnlyRoleHolds(_Law)` |
| Code | `repo://src/eija_studio/domain/laws.py#OnlyRoleHolds` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Every transition performing ``action`` is held by ``role``.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['only_role_holds']` |  |
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
