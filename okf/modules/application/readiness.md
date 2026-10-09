---
type: Module
title: application.readiness
description: 'What''s missing (ADR-0203): one list across every model and view of what is not ready yet, so a system built in chat or on the canvas says what it still lacks instead of the person having to look in each tab.'
resource: repo://src/eija_studio/application/readiness.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/readiness.py
  title: application/readiness.py
  hash_method: ast-api-v1
  sha256: bf30465bf956c43af4ea293ee4ac710d5445eb5b493f206bc160ab04383ea039
notes_baseline: 59ca808b0bdd00420553f0dd38971546a3b0d4afb35682b9f26b4568736bc431
---

# application.readiness

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/readiness.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
What's missing (ADR-0203): one list across every model and view of what is not ready yet, so a system built in
chat or on the canvas says what it still lacks instead of the person having to look in each tab.

Each view gets a row: ready, or the things it is missing, each in words with where to fix it. Nothing here decides
anything new. Every item restates a check the IDE already has: the screens' design check, the scenarios run by the
kernel, the laws proved by the kernel, reachability on the state machine, and who can take what. A view with no law or
no test is "missing", not failing: an empty file proves nothing, and the list says so rather than showing green.
~~~

## Public symbols

* [`VIEWS`](/symbols/application/readiness/VIEWS.md) (constant) - no docstring
* [`missing`](/symbols/application/readiness/missing.md) (function) - Every view's row: what it is missing or what is wrong with it, or nothing when it is ready.

## Internal imports

* [`application/law_proof`](/modules/application/law_proof.md)
* [`application/scenario_run`](/modules/application/scenario_run.md)
* [`domain/data`](/modules/domain/data.md)
* [`domain/laws`](/modules/domain/laws.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/scenarios`](/modules/domain/scenarios.md)
* [`domain/screens`](/modules/domain/screens.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.law_proof](/modules/application/law_proof.md) - Prove a pack's laws over every run the kernel allows (ADR-0166).
* [application.scenario_run](/modules/application/scenario_run.md) - Run a pack's scenarios (its test cases) through the kernel, and record new ones (ADR-0177).
* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.laws](/modules/domain/laws.md) - Typed law DSL of a domain pack: what a workflow may never do, stated as data (WBS 1.1/1.2).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.scenarios](/modules/domain/scenarios.md) - Scenarios: a pack's test cases, written as stories a person can read and the kernel can run (ADR-0177).
* [domain.screens](/modules/domain/screens.md) - Screens: the user interface of a pack's app, designed against its use cases and data model (ADR-0154).

## Referenced by

* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [application.readiness.VIEWS](/symbols/application/readiness/VIEWS.md) - Constant `VIEWS` in `application/readiness`.
* [application.readiness.missing](/symbols/application/readiness/missing.md) - Every view's row: what it is missing or what is wrong with it, or nothing when it is ready.
<!-- okf:generated:end links -->
