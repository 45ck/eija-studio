---
type: Module
title: interfaces.play_systems
description: 'PlayIDE''s systems (ADR-0185): start a new system from a sketch or a template, open one you made before, and save the work in progress to carry on later.'
resource: repo://src/eija_studio/interfaces/play_systems.py
tags:
- module
- interfaces
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/interfaces/play_systems.py
  title: interfaces/play_systems.py
  hash_method: ast-api-v1
  sha256: 620920428406c5f9418bec920636d5ad9138bca84b85e5d9b11247eface72587
notes_baseline: 8e9e10b556e8b249599f86e805fefcd246a7ff4ad68246a44f002fd082476ad6
---

# interfaces.play_systems

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | interfaces |
| Code | `repo://src/eija_studio/interfaces/play_systems.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
PlayIDE's systems (ADR-0185): start a new system from a sketch or a template, open one you made before, and save
the work in progress to carry on later.

The server serves one system at a time. Opening another builds a studio for it, on its own workspace, and swaps it
in behind every route; the page then reloads. A system is created only from documents the kernel's pack check
accepts. The draft is the page's work in progress (its plan steps and edited screens), kept in the system's
workspace; it is never the model in force, and on reopening every step is checked by the policy again, like any plan.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`application/data_steps`](/modules/application/data_steps.md)
* [`application/describe_system`](/modules/application/describe_system.md)
* [`application/new_system`](/modules/application/new_system.md)
* [`application/plan`](/modules/application/plan.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/scenarios`](/modules/domain/scenarios.md)
* [`domain/screens`](/modules/domain/screens.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.data_steps](/modules/application/data_steps.md) - Data-model steps in a chat plan (ADR-0202): add an attribute to a class, remove one, or make one required or optional.
* [application.describe_system](/modules/application/describe_system.md) - Describe your app (ADR-0216): a new system from one description, like starting an app in Lovable or Replit.
* [application.new_system](/modules/application/new_system.md) - Start a new system (ADR-0185): the pack documents for a system started from a sketch or copied from a template.
* [application.plan](/modules/application/plan.md) - Plan mode for the PlayIDE chat (ADR-0156): an AI proposes a change as numbered typed steps; the person accepts or rejects each one and sees what the accepted o…
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.scenarios](/modules/domain/scenarios.md) - Scenarios: a pack's test cases, written as stories a person can read and the kernel can run (ADR-0177).
* [domain.screens](/modules/domain/screens.md) - Screens: the user interface of a pack's app, designed against its use cases and data model (ADR-0154).

## Referenced by

* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
* [interfaces.http](/modules/interfaces/http.md) - Loopback-only local adapter.
<!-- okf:generated:end links -->
