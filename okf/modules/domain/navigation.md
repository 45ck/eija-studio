---
type: Module
title: domain.navigation
description: The generated app's bounded navigation, derived from its existing contracts.
resource: repo://src/eija_studio/domain/navigation.py
tags:
- module
- domain
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/navigation.py
  title: domain/navigation.py
  hash_method: ast-api-v1
  sha256: 366891a9f1b3d3d602bfc211f95a36277996e923ca986963703a05f754682bf6
notes_baseline: 97b3de6c25e7af7c91529e04be1968507b43b86cf3f7859f617069b962861169
---

# domain.navigation

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | domain |
| Code | `repo://src/eija_studio/domain/navigation.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
The generated app's bounded navigation, derived from its existing contracts.

Destinations name actual React panels and existing use cases. They grant no
authority, introduce no HTTP routes and do not imply record update/delete support.
~~~

## Public symbols

* [`Destination`](/symbols/domain/navigation/Destination.md) (class) - no docstring
* [`Navigation`](/symbols/domain/navigation/Navigation.md) (class) - no docstring
* [`RecordOperations`](/symbols/domain/navigation/RecordOperations.md) (class) - no docstring
* [`navigation_for`](/symbols/domain/navigation/navigation_for.md) (function) - Project actual supported panels from one canonical workflow/data/screens snapshot.

## Internal imports

* [`domain/data`](/modules/domain/data.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/screens`](/modules/domain/screens.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.screens](/modules/domain/screens.md) - Screens: the user interface of a pack's app, designed against its use cases and data model (ADR-0154).

## Referenced by

* [application.appgen](/modules/application/appgen.md) - App generation: a reviewed workflow model becomes a runnable app and its conformance oracle (ADR-0150).
* [application.presentation](/modules/application/presentation.md) - A bounded presentation/navigation lens over one exact generated snapshot.
* [domain.navigation.Destination.coherent](/symbols/domain/navigation/Destination.coherent.md) - `def coherent(self) -> Destination` in `domain/navigation`.
* [domain.navigation.Destination](/symbols/domain/navigation/Destination.md) - `class Destination(Contract)` in `domain/navigation`.
* [domain.navigation.Navigation.coherent](/symbols/domain/navigation/Navigation.coherent.md) - `def coherent(self) -> Navigation` in `domain/navigation`.
* [domain.navigation.Navigation.digest](/symbols/domain/navigation/Navigation.digest.md) - `def digest(self) -> str` in `domain/navigation`.
* [domain.navigation.Navigation](/symbols/domain/navigation/Navigation.md) - `class Navigation(Contract)` in `domain/navigation`.
* [domain.navigation.RecordOperations](/symbols/domain/navigation/RecordOperations.md) - `class RecordOperations(Contract)` in `domain/navigation`.
* [domain.navigation.navigation_for](/symbols/domain/navigation/navigation_for.md) - Project actual supported panels from one canonical workflow/data/screens snapshot.
<!-- okf:generated:end links -->
