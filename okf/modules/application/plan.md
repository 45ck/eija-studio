---
type: Module
title: application.plan
description: 'Plan mode for the PlayIDE chat (ADR-0156): an AI proposes a change as numbered typed steps; the person accepts or rejects each one and sees what the accepted ones would do.'
resource: repo://src/eija_studio/application/plan.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/plan.py
  title: application/plan.py
  hash_method: ast-api-v1
  sha256: 36dd0d9c4ad4ce7cf17d27fe1176c956e8d7283f472fcb6cc2549ae831fd7a28
notes_baseline: 97e696ddd808e5f677413132502fa8cf7e298bb636aed01a3ec6e502531f552f
---

# application.plan

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/plan.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Plan mode for the PlayIDE chat (ADR-0156): an AI proposes a change as numbered typed steps; the person accepts or
rejects each one and sees what the accepted ones would do. Nothing here persists or applies anything.

The proposer's plan is untrusted. Every step is re-parsed into the typed transaction vocabulary, each accepted prefix
is checked for structure step by step (so a step that needs a rejected one says so), and the accepted steps are
applied as one change through the policy (`apply_transactions`), exactly as an owner's edit would be. A plan cannot
choose meaning, approve or apply: making a change real still goes through the change case.
~~~

## Public symbols

* [`MAX_DRAFT_STEPS`](/symbols/application/plan/MAX_DRAFT_STEPS.md) (constant) - no docstring
* [`MAX_REQUEST`](/symbols/application/plan/MAX_REQUEST.md) (constant) - no docstring
* [`MAX_STEPS`](/symbols/application/plan/MAX_STEPS.md) (constant) - no docstring
* [`describe`](/symbols/application/plan/describe.md) (function) - One line a person can check against the diagram.
* [`example_passes`](/symbols/application/plan/example_passes.md) (function) - Whether `request`, sent to the chat as it stands, becomes a plan the policy allows on `model`.
* [`preview_plan`](/symbols/application/plan/preview_plan.md) (function) - What the accepted steps would make of `model`.
* [`propose_plan`](/symbols/application/plan/propose_plan.md) (function) - Ask the proposer for a plan, re-check it, and preview it with every step accepted.

## Internal imports

* [`application/data_steps`](/modules/application/data_steps.md)
* [`application/diagrams`](/modules/application/diagrams.md)
* [`application/new_system`](/modules/application/new_system.md)
* [`application/ports`](/modules/application/ports.md)
* [`domain/data`](/modules/domain/data.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/policy`](/modules/domain/policy.md)
* [`domain/transactions`](/modules/domain/transactions.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.data_steps](/modules/application/data_steps.md) - Data-model steps in a chat plan (ADR-0202): add an attribute to a class, remove one, or make one required or optional.
* [application.diagrams](/modules/application/diagrams.md) - Diagram models derived from the executable Workflow (ADR-0019, ADR-0023).
* [application.new_system](/modules/application/new_system.md) - Start a new system (ADR-0185): the pack documents for a system started from a sketch or copied from a template.
* [application.ports](/modules/application/ports.md) - Application-owned ports.
* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.
* [domain.transactions](/modules/domain/transactions.md) - Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.

## Referenced by

* [application.ripple](/modules/application/ripple.md) - Ripple (ADR-0158): what one change to the state machine does to every other diagram of the same system, and the follow-on edits that would keep them in agreeme…
* [interfaces.http](/modules/interfaces/http.md) - Loopback-only local adapter.
* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [interfaces.play_interop](/modules/interfaces/play_interop.md) - PlayIDE routes for UML interchange (ADR-0190): export the model on screen, and read a UML file as a report.
* [interfaces.play_systems](/modules/interfaces/play_systems.md) - PlayIDE's systems (ADR-0185): start a new system from a sketch or a template, open one you made before, and save the work in progress to carry on later.
* [application.plan.MAX_DRAFT_STEPS](/symbols/application/plan/MAX_DRAFT_STEPS.md) - Constant `MAX_DRAFT_STEPS` in `application/plan`.
* [application.plan.MAX_REQUEST](/symbols/application/plan/MAX_REQUEST.md) - Constant `MAX_REQUEST` in `application/plan`.
* [application.plan.MAX_STEPS](/symbols/application/plan/MAX_STEPS.md) - Constant `MAX_STEPS` in `application/plan`.
* [application.plan.describe](/symbols/application/plan/describe.md) - One line a person can check against the diagram.
* [application.plan.example_passes](/symbols/application/plan/example_passes.md) - Whether `request`, sent to the chat as it stands, becomes a plan the policy allows on `model`.
* [application.plan.preview_plan](/symbols/application/plan/preview_plan.md) - What the accepted steps would make of `model`.
* [application.plan.propose_plan](/symbols/application/plan/propose_plan.md) - Ask the proposer for a plan, re-check it, and preview it with every step accepted.
<!-- okf:generated:end links -->
