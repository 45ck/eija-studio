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
  sha256: 4aa2007f166bb031deb17fb966fbf5ca1d7a772ef24cec3ec80853c10572e831
notes_baseline: b9b041401c903897387752aa412b842ed15f97b47cdea0a42b341bfbb2b34093
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
steps can be previewed, built and simulated but never saved or applied from here (ADR-0156), the ripple of a plan
across every diagram with the follow-on edits the proposer suggests, each re-checked (ADR-0158), and the run bar's
seeded run log with breakpoints and Stop (ADR-0160), and how a change looks: the model in force and the change on
one state machine, removed elements kept as ghosts (ADR-0176).

Build & run reuses `eija build` (ADR-0150): the app is generated into the workspace, its kernel conformance tests run,
and only a PASSing app is started, as a separate local process on a free loopback port. One app runs at a time; a new
model's build replaces it and the IDE stops it on exit. The generated app has no access to the workspace database.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`application/components`](/modules/application/components.md)
* [`application/ghost_diff`](/modules/application/ghost_diff.md)
* [`application/law_proof`](/modules/application/law_proof.md)
* [`application/plan`](/modules/application/plan.md)
* [`application/ripple`](/modules/application/ripple.md)
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
* [application.ghost_diff](/modules/application/ghost_diff.md) - How a change looks on the state machine: both models on one canvas, with nothing hidden (ADR-0176).
* [application.law_proof](/modules/application/law_proof.md) - Prove a pack's laws over every run the kernel allows (ADR-0166).
* [application.plan](/modules/application/plan.md) - Plan mode for the PlayIDE chat (ADR-0156): an AI proposes a change as numbered typed steps; the person accepts or rejects each one and sees what the accepted o…
* [application.ripple](/modules/application/ripple.md) - Ripple (ADR-0158): what one change to the state machine does to every other diagram of the same system, and the follow-on edits that would keep them in agreeme…
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
