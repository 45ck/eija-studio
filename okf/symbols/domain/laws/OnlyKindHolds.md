---
type: Class
title: domain.laws.OnlyKindHolds
description: Every transition performing ``action`` is held by a role of one of ``role_kinds`` (e.g.
resource: repo://src/eija_studio/domain/laws.py#OnlyKindHolds
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#OnlyKindHolds
  title: domain/laws.py
  hash_method: ast-sig-v1
  sha256: 39736bd8b24ebe712009f45e1411c88486509c495efc5666a3a7f91c00a77be3
notes_baseline: 04234fc9cd632732275db39c3e620294b69427b9a3e93768fc8e77c4d256a098
---

# domain.laws.OnlyKindHolds

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `class OnlyKindHolds(_KindLaw)` |
| Code | `repo://src/eija_studio/domain/laws.py#OnlyKindHolds` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Every transition performing ``action`` is held by a role of one of ``role_kinds`` (e.g. only a human approves).
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['only_kind_holds']` |  |
| `action` | `Name` |  |
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
