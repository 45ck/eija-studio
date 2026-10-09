---
type: Module
title: application.class_build
description: 'What the built app does with each part of the class diagram (#145, ADR-0205): the record class is built and checked; the other classes and the associations are drawn but not built.'
resource: repo://src/eija_studio/application/class_build.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/class_build.py
  title: application/class_build.py
  hash_method: ast-api-v1
  sha256: d01fe218e32025a4a46a046fae950994c7bd18a71cc73b1fa463259e65ffc9d1
notes_baseline: d2c708423b05bb8623c78cbd761fa2441dc97e650d11384cf5af5cd5e7b97783
---

# application.class_build

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/class_build.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
What the built app does with each part of the class diagram (#145, ADR-0205): the record class is built and checked;
the other classes and the associations are drawn but not built. The diagram says which is which, so nobody reads an
association as a rule the app enforces.

The built app (ADR-0150, ADR-0153) stores records of the record class only and checks their attribute values. It never
stores another class, never looks one up and never checks a multiplicity. A record attribute that names an associated
class (`memberCard` beside `borrower: Member`) is the usual hand-written stand-in for the association: the app checks the
text, not that such a member exists.

Pure: reads the data model only.
~~~

## Public symbols

* [`FORMAT`](/symbols/application/class_build/FORMAT.md) (constant) - no docstring
* [`class_build`](/symbols/application/class_build/class_build.md) (function) - Which classes and associations the built app stores and checks, and what to consider about the rest.

## Internal imports

* [`domain/data`](/modules/domain/data.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.

## Referenced by

* [application.plan](/modules/application/plan.md) - Plan mode for the PlayIDE chat (ADR-0156): an AI proposes a change as numbered typed steps; the person accepts or rejects each one and sees what the accepted o…
* [application.ripple](/modules/application/ripple.md) - Ripple (ADR-0158): what one change to the state machine does to every other diagram of the same system, and the follow-on edits that would keep them in agreeme…
* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [application.class_build.FORMAT](/symbols/application/class_build/FORMAT.md) - Constant `FORMAT` in `application/class_build`.
* [application.class_build.class_build](/symbols/application/class_build/class_build.md) - Which classes and associations the built app stores and checks, and what to consider about the rest.
<!-- okf:generated:end links -->
