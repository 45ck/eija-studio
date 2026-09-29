---
type: Class
title: domain.laws.ActionRequiresGuard
description: Every transition performing ``action`` carries at least ``guards``.
resource: repo://src/eija_studio/domain/laws.py#ActionRequiresGuard
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#ActionRequiresGuard
  title: domain/laws.py
  hash_method: ast-sig-v1
  sha256: 135417920ed873c0232ca1a1c1accefc526bbcee125d243ee246a194a511dbb6
notes_baseline: 061fb29dc9b3be19e98e59461f350c5ddade6fa56ad36b10c449b3b6e62c1365
---

# domain.laws.ActionRequiresGuard

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `class ActionRequiresGuard(_Law)` |
| Code | `repo://src/eija_studio/domain/laws.py#ActionRequiresGuard` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Every transition performing ``action`` carries at least ``guards``.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['action_requires_guard']` |  |
| `action` | `Name` |  |
| `guards` | `tuple[Guard, ...]` | `Field(min_length=1)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.Name](/symbols/domain/laws/Name.md) - Type alias `Name` in `domain/laws`.
* [domain.models.Guard](/symbols/domain/models/Guard.md) - Type alias `Guard` in `domain/models`.

## Referenced by

* [domain.laws.Law](/symbols/domain/laws/Law.md) - Type alias `Law` in `domain/laws`.
<!-- okf:generated:end links -->
