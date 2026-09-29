---
type: Class
title: domain.laws.ActionSourceIn
description: Every transition performing ``action`` starts in one of ``states``.
resource: repo://src/eija_studio/domain/laws.py#ActionSourceIn
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#ActionSourceIn
  title: domain/laws.py
  hash_method: ast-sig-v1
  sha256: e057b5f2b0b3874cc8a90665c98877057751a49e6a0d78cfd3546ac77cbdacc8
notes_baseline: 0030472ffa5389bea83dcf1afc286c5a9a6b3a33da0edd7ce214135259642339
---

# domain.laws.ActionSourceIn

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `class ActionSourceIn(_Law)` |
| Code | `repo://src/eija_studio/domain/laws.py#ActionSourceIn` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Every transition performing ``action`` starts in one of ``states``.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['action_source_in']` |  |
| `action` | `Name` |  |
| `states` | `tuple[Name, ...]` | `Field(min_length=1)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.Name](/symbols/domain/laws/Name.md) - Type alias `Name` in `domain/laws`.

## Referenced by

* [domain.laws.Law](/symbols/domain/laws/Law.md) - Type alias `Law` in `domain/laws`.
<!-- okf:generated:end links -->
