---
type: Module
title: interfaces.play
description: 'PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step the kernel decides (ADR-0152), the screen designer''s check a…'
resource: repo://src/eija_studio/interfaces/play.py
tags:
- module
- interfaces
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/interfaces/play.py
  title: interfaces/play.py
  hash_method: ast-api-v1
  sha256: e150bc1869459fc2f58492a334223bcb08715dadecef3e3ba948f364ca4adfda
notes_baseline: c4060f866e4c2df424110b95af1eac23e446f65f397c53ae1de150dd6072879d
---

# interfaces.play

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | interfaces |
| Code | `repo://src/eija_studio/interfaces/play.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and
Simulate, seeded simulated users whose every step the kernel decides (ADR-0152), the screen designer's check and
build of designed screens (ADR-0154), the component diagram read from the files the app is built from (ADR-0155), the chat's plan mode, whose accepted
steps can be previewed, built and simulated but never saved or applied from here (ADR-0156), and the run bar's seeded
run log with breakpoints and Stop (ADR-0160).

Build & run reuses `eija build` (ADR-0150): the app is generated into the workspace, its kernel conformance tests run,
and only a PASSing app is started, as a separate local process on a free loopback port. One app runs at a time; a new
model's build replaces it and the IDE stops it on exit. The generated app has no access to the workspace database.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`application/components`](/modules/application/components.md)
* [`application/plan`](/modules/application/plan.md)
* [`application/simulation`](/modules/application/simulation.md)
* [`domain/data`](/modules/domain/data.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/policy`](/modules/domain/policy.md)
* [`domain/screens`](/modules/domain/screens.md)
* [`domain/transactions`](/modules/domain/transactions.md)
* [`interfaces/app_build`](/modules/interfaces/app_build.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.components](/modules/application/components.md) - The component diagram of an app built from the model (ADR-0155), extracted from the generated files themselves.
* [application.plan](/modules/application/plan.md) - Plan mode for the PlayIDE chat (ADR-0156): an AI proposes a change as numbered typed steps; the person accepts or rejects each one and sees what the accepted o…
* [application.simulation](/modules/application/simulation.md) - Seeded simulation of people using the app built from a model (ADR-0152).
* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.
* [domain.screens](/modules/domain/screens.md) - Screens: the user interface of a pack's app, designed against its use cases and data model (ADR-0154).
* [domain.transactions](/modules/domain/transactions.md) - Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.
* [interfaces.app_build](/modules/interfaces/app_build.md) - `eija build`: write a runnable app generated from a pack's model, then run its kernel conformance tests (ADR-0150).

## Referenced by

* [interfaces.http](/modules/interfaces/http.md) - Loopback-only local adapter.
<!-- okf:generated:end links -->
