---
type: Module
title: application.scenario_run
description: Run a pack's scenarios (its test cases) through the kernel, and record new ones (ADR-0177).
resource: repo://src/eija_studio/application/scenario_run.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/scenario_run.py
  title: application/scenario_run.py
  hash_method: ast-api-v1
  sha256: bc7419cba84680f8582bd6ffadd35ab335c7a4ef8141a60fdf287244dcc4866c
notes_baseline: 4a91e5cf6df7efc4aeb7b5ce21a3f6faf4d963cb34efe25ca7be95e1f9bd8c7d
---

# application.scenario_run

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/scenario_run.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Run a pack's scenarios (its test cases) through the kernel, and record new ones (ADR-0177).

Every step is decided by `runtime.execute` on an in-memory session holding the pack's fixture actors, exactly as the
built app's kernel would decide it; nothing here re-encodes a rule. A scenario stops at its first step whose outcome
differs from what it expects, and that step names the diagram elements involved so PlayIDE can show it.

Pure: no IO, no clock, no randomness.
~~~

## Public symbols

* [`CASE`](/symbols/application/scenario_run/CASE.md) (constant) - no docstring
* [`FORMAT`](/symbols/application/scenario_run/FORMAT.md) (constant) - no docstring
* [`record_steps`](/symbols/application/scenario_run/record_steps.md) (function) - What the kernel does for each (actor, action) in turn, written as scenario steps that expect exactly that.
* [`run_scenario`](/symbols/application/scenario_run/run_scenario.md) (function) - Run one scenario; it stops at the first step whose outcome differs from what it expects.
* [`run_scenarios`](/symbols/application/scenario_run/run_scenarios.md) (function) - Every scenario run on `model`; a model the policy refuses runs none of them.

## Internal imports

* [`application/simulation`](/modules/application/simulation.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/policy`](/modules/domain/policy.md)
* [`domain/scenarios`](/modules/domain/scenarios.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.simulation](/modules/application/simulation.md) - Seeded simulation of people using the app built from a model (ADR-0152).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.
* [domain.scenarios](/modules/domain/scenarios.md) - Scenarios: a pack's test cases, written as stories a person can read and the kernel can run (ADR-0177).

## Referenced by

* [application.describe_system](/modules/application/describe_system.md) - Describe your app (ADR-0216): a new system from one description, like starting an app in Lovable or Replit.
* [application.readiness](/modules/application/readiness.md) - What's missing (ADR-0216): one list across every model and view of what is not ready yet, so a system built in chat or on the canvas says what it still lacks i…
* [application.sequence_draft](/modules/application/sequence_draft.md) - Scenarios drafted from the model, for a system that has none yet (ADR-0195).
* [application.sequences](/modules/application/sequences.md) - The pack's scenarios drawn as UML sequence diagrams the kernel checks (ADR-0195).
* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [application.scenario_run.CASE](/symbols/application/scenario_run/CASE.md) - Constant `CASE` in `application/scenario_run`.
* [application.scenario_run.FORMAT](/symbols/application/scenario_run/FORMAT.md) - Constant `FORMAT` in `application/scenario_run`.
* [application.scenario_run.record_steps](/symbols/application/scenario_run/record_steps.md) - What the kernel does for each (actor, action) in turn, written as scenario steps that expect exactly that.
* [application.scenario_run.run_scenario](/symbols/application/scenario_run/run_scenario.md) - Run one scenario; it stops at the first step whose outcome differs from what it expects.
* [application.scenario_run.run_scenarios](/symbols/application/scenario_run/run_scenarios.md) - Every scenario run on `model`; a model the policy refuses runs none of them.
<!-- okf:generated:end links -->
