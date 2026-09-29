---
type: Class
title: domain.pack.Term
description: '`class Term(Contract)` in `domain/pack`.'
resource: repo://src/eija_studio/domain/pack.py#Term
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#Term
  title: domain/pack.py
  hash_method: ast-sig-v1
  sha256: 61b7370e5d655c60de7a149cc603e5fa081736ead24e61eb2e5f4d1ee35c1b6f
notes_baseline: 4ec277707e2874fffb9df6f4dff6a607c8b5ccb97516442f3621abcc6dd73a79
---

# domain.pack.Term

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `class Term(Contract)` |
| Code | `repo://src/eija_studio/domain/pack.py#Term` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `id` | `str` | `Field(pattern='^[a-z][a-z0-9-]{0,63}$')` |
| `label` | `str` | `Field(min_length=1, max_length=120)` |
| `definition` | `str` | `Field(default='', max_length=2000)` |
| `binds` | `tuple[str, ...]` | `()` |
| `refs` | `tuple[str, ...]` | `()` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [domain.pack.Language](/symbols/domain/pack/Language.md) - `class Language(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
