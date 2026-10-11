---
type: Module
title: application.capabilities
description: Explicit support levels for the workbench; design visibility is not execution.
resource: repo://src/eija_studio/application/capabilities.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/capabilities.py
  title: application/capabilities.py
  hash_method: ast-api-v1
  sha256: 124ac446b5b808831502ba5656005a64b4a16d93559259add1c44ef6bd40ea11
notes_baseline: c1ad7a53aabdf4c934e1549a5366fcbcbca9d1b5c735a6bde832f7d66897b7ea
---

# application.capabilities

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/capabilities.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Explicit support levels for the workbench; design visibility is not execution.
~~~

## Public symbols

* [`capability_map`](/symbols/application/capabilities/capability_map.md) (function) - The supported constructs, bounded to the current model, with no inferred readiness.

## Internal imports

* [`domain/data`](/modules/domain/data.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [interfaces.play_assurance](/modules/interfaces/play_assurance.md) - Read-only assurance review.
* [application.capabilities.capability_map](/symbols/application/capabilities/capability_map.md) - The supported constructs, bounded to the current model, with no inferred readiness.
<!-- okf:generated:end links -->
