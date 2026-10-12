---
type: Class
title: domain.navigation.Navigation
description: '`class Navigation(Contract)` in `domain/navigation`.'
resource: repo://src/eija_studio/domain/navigation.py#Navigation
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/navigation.py#Navigation
  title: domain/navigation.py
  hash_method: ast-sig-v1
  sha256: 4174d9c8ec9f6f6d683ed6b5a0fc563149afadbb949dd9a772095d1d99c8a1d2
notes_baseline: 1a2b738d52253f1792621b8ae129d296d4f1ac6a23d4d59e6c416f4b7cb23cb2
---

# domain.navigation.Navigation

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/navigation`](/modules/domain/navigation.md) |
| Signature | `class Navigation(Contract)` |
| Code | `repo://src/eija_studio/domain/navigation.py#Navigation` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `schema_version` | `Literal['eija.navigation.v1']` | `'eija.navigation.v1'` |
| `id` | `str` | `Field(pattern='^[a-z][a-z0-9-]{0,39}$')` |
| `record` | `str \| None` | `Field(default=None, pattern='^[A-Z][A-Za-z0-9]{0,39}$')` |
| `capabilities` | `RecordOperations` | `Field(default_factory=RecordOperations)` |
| `destinations` | `tuple[Destination, ...]` | `Field(min_length=3, max_length=67)` |

## Methods

* [`coherent`](/symbols/domain/navigation/Navigation.coherent.md) - `def coherent(self) -> Navigation`
* [`digest`](/symbols/domain/navigation/Navigation.digest.md) - `def digest(self) -> str`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.navigation.Destination](/symbols/domain/navigation/Destination.md) - `class Destination(Contract)` in `domain/navigation`.
* [domain.navigation.RecordOperations](/symbols/domain/navigation/RecordOperations.md) - `class RecordOperations(Contract)` in `domain/navigation`.

## Referenced by

* [domain.navigation.Navigation.coherent](/symbols/domain/navigation/Navigation.coherent.md) - `def coherent(self) -> Navigation` in `domain/navigation`.
* [domain.navigation.Navigation.digest](/symbols/domain/navigation/Navigation.digest.md) - `def digest(self) -> str` in `domain/navigation`.
* [domain.navigation.navigation_for](/symbols/domain/navigation/navigation_for.md) - Project actual supported panels from one canonical workflow/data/screens snapshot.
<!-- okf:generated:end links -->
