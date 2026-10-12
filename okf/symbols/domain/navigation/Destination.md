---
type: Class
title: domain.navigation.Destination
description: '`class Destination(Contract)` in `domain/navigation`.'
resource: repo://src/eija_studio/domain/navigation.py#Destination
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/navigation.py#Destination
  title: domain/navigation.py
  hash_method: ast-sig-v1
  sha256: 08392193f4c2aa63e3c28ae8cdf960ab954085084c6300105244aaf6bf35b921
notes_baseline: 00c9268197157e431b7588549dde62a08491ba4bd3f105bba3ad41b5a12a8f43
---

# domain.navigation.Destination

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/navigation`](/modules/domain/navigation.md) |
| Signature | `class Destination(Contract)` |
| Code | `repo://src/eija_studio/domain/navigation.py#Destination` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `id` | `str` | `Field(min_length=1, max_length=80)` |
| `kind` | `Literal['records', 'create', 'detail', 'action']` |  |
| `parent` | `str \| None` | `Field(default=None, min_length=1, max_length=80)` |
| `title` | `str` | `Field(min_length=1, max_length=60)` |
| `panel` | `Literal['records', 'create', 'detail', 'action-screen']` |  |
| `focus` | `Literal['records-title', 'title', 'detail-title', 'action-screen']` |  |
| `record_required` | `bool` | `False` |
| `use_case` | `str \| None` | `Field(default=None, min_length=1, max_length=60)` |
| `transition_ref` | `str \| None` | `Field(default=None, pattern='^transition:[A-Z][A-Z0-9_-]{0,63}$')` |

## Methods

* [`coherent`](/symbols/domain/navigation/Destination.coherent.md) - `def coherent(self) -> Destination`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [domain.navigation.Destination.coherent](/symbols/domain/navigation/Destination.coherent.md) - `def coherent(self) -> Destination` in `domain/navigation`.
* [domain.navigation.Navigation](/symbols/domain/navigation/Navigation.md) - `class Navigation(Contract)` in `domain/navigation`.
* [domain.navigation.navigation_for](/symbols/domain/navigation/navigation_for.md) - Project actual supported panels from one canonical workflow/data/screens snapshot.
<!-- okf:generated:end links -->
