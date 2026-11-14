---
type: Module
title: application.access
description: 'Who can do what (ADR-0171): the model''s permissions as a role by state matrix, each cell checked by the kernel, and reachability questions such as "can a record reach this state without that role ever acting?".'
resource: repo://src/eija_studio/application/access.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/access.py
  title: application/access.py
  hash_method: ast-api-v1
  sha256: ec552dbaaf7c1540b486ef70985681922800e1235ad0be36d0e23fee4e349d86
notes_baseline: fd4727bb1f98d1cf313a172b35fd8c16e70f5b5592065ed69e35f67049b86b49
---

# application.access

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/access.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Who can do what (ADR-0171): the model's permissions as a role by state matrix, each cell checked by the kernel, and
reachability questions such as "can a record reach this state without that role ever acting?".

The matrix is a projection of the model's transitions; every cell is also tried in the kernel with each of the pack's
fixture actors in that role, on a fresh record in that state, so it says who the kernel actually lets through and why
the others are refused. Comparing two models (the base and a previewed plan) flags the cells that change.

A reachability answer has three outcomes. UNREACHABLE is a proof over the model: no sequence of its transitions
avoids the role, and guards can only refuse more, so no actor can do it. REACHABLE comes with a path the kernel
committed step by step on one record, with fixture actors. NOT_SHOWN means the model has such a path but no fixture
actor could take it in the kernel; other actors might. Nothing persists and no effect leaves the process.
~~~

## Public symbols

* [`Key`](/symbols/application/access/Key.md) (type-alias) - no docstring
* [`access`](/symbols/application/access/access.md) (function) - The matrix for `model`, and, when `base` differs, the permissions it adds, removes and changes compared with `base`.
* [`matrix`](/symbols/application/access/matrix.md) (function) - Every role's actions from every state, each tried in the kernel with the fixture actors in that role.
* [`meeting`](/symbols/application/access/meeting.md) (function) - A record's values that meet every guard over values of these transitions (ADR-0234): {} when they have none, None when…
* [`reach`](/symbols/application/access/reach.md) (function) - Can a record reach `target` with no step taken by role `without` (or at all, when it is None)?

## Internal imports

* [`application/runtime`](/modules/application/runtime.md)
* [`application/simulation`](/modules/application/simulation.md)
* [`domain/data`](/modules/domain/data.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/value_guards`](/modules/domain/value_guards.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.runtime](/modules/application/runtime.md) - Generic execution algorithm; the domain (policy, laws, typed effects) comes from the pack.
* [application.simulation](/modules/application/simulation.md) - Seeded simulation of people using the app built from a model (ADR-0152).
* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.value_guards](/modules/domain/value_guards.md) - Guards over a record's values (issue #93, ADR-0234): which values can decide them, and whether they fit the data model.

## Referenced by

* [application.review](/modules/application/review.md) - Review a model change in PlayIDE instead of a pull request (ADR-0175).
* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [application.access.Key](/symbols/application/access/Key.md) - Type alias `Key` in `application/access`.
* [application.access.access](/symbols/application/access/access.md) - The matrix for `model`, and, when `base` differs, the permissions it adds, removes and changes compared with `base`.
* [application.access.matrix](/symbols/application/access/matrix.md) - Every role's actions from every state, each tried in the kernel with the fixture actors in that role.
* [application.access.meeting](/symbols/application/access/meeting.md) - A record's values that meet every guard over values of these transitions (ADR-0234): {} when they have none, None when no values meet them all.
* [application.access.reach](/symbols/application/access/reach.md) - Can a record reach `target` with no step taken by role `without` (or at all, when it is None)?
<!-- okf:generated:end links -->
