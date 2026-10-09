---
type: Class
title: domain.laws.OnlyKindEnters
description: Every transition entering ``state`` is held by a role of one of ``role_kinds``.
resource: repo://src/eija_studio/domain/laws.py#OnlyKindEnters
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#OnlyKindEnters
  title: domain/laws.py
  hash_method: ast-sig-v1
  sha256: eb313aaad6603d9359148cd195c22ec0979eeccdc6fd9dc3f31bcad0b0a5f639
notes_baseline: afb1afcdf4d54620671af756653439e3b552deb13d5bc1f1a50f2912f809ab17
---

# domain.laws.OnlyKindEnters

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `class OnlyKindEnters(_KindLaw)` |
| Code | `repo://src/eija_studio/domain/laws.py#OnlyKindEnters` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Every transition entering ``state`` is held by a role of one of ``role_kinds``.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['only_kind_enters']` |  |
| `state` | `Name` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.Name](/symbols/domain/laws/Name.md) - Type alias `Name` in `domain/laws`.

## Referenced by

* [domain.laws.KIND_LAWS](/symbols/domain/laws/KIND_LAWS.md) - Constant `KIND_LAWS` in `domain/laws`.
* [domain.laws.Law](/symbols/domain/laws/Law.md) - Type alias `Law` in `domain/laws`.
<!-- okf:generated:end links -->
