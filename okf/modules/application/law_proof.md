---
type: Module
title: application.law_proof
description: Prove a pack's laws over every run the kernel allows (ADR-0166).
resource: repo://src/eija_studio/application/law_proof.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/law_proof.py
  title: application/law_proof.py
  hash_method: ast-api-v1
  sha256: 280326154b79700f0adb19ab2c717a16e34c85b74572ee60c5381c360d597af4
notes_baseline: 491127e2ed9019eb75b30070012849d2177980dd0eb5060a6662c1b536a497dc
---

# application.law_proof

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/law_proof.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Prove a pack's laws over every run the kernel allows (ADR-0166).

The laws in `pack.json` (`domain/laws.py`) are the layer above the UML: what the model must never do, whatever is
drawn. The policy already judges them on the transition table. This module asks the stronger, runtime question for
any pack: is there ANY run, by ANY actor, from a new record, in which the kernel commits a step that breaks a law?

It explores the kernel's reachable configurations exhaustively. The kernel decides every step (`runtime.execute`
on an in-memory session); the laws are judged by `laws.evaluate_run` itself, so nothing here re-encodes either.

* Actors: every class the kernel can tell apart. `check_actor` reads only `active`, `role` and `assigned`, so one
  actor per role and per combination of the two flags, plus one actor holding a role the pack does not declare,
  stands for every possible actor.
* Configurations: the record's state plus the set of path-law waypoints (`path_requires.via`) it has passed and of
  the `path_requires_kind` laws whose kind of actor has already taken a step (ADR-0210). Every other law kind is
  judged per step, so this product is complete for the current law kinds; `LAW_HANDLING` names
  how each kind is judged and a test fails if a new kind is not classified.
* `can_reach_end` is about the runs a record could still take, not one run: it is judged on the steps the kernel
  committed during the search, so a record is stuck only where the kernel itself leaves no way to an end (ADR-0221).
* Each configuration is reached first by a shortest run, so a counterexample is the shortest run that breaks the law.
* A law about a state that is never reached, or an action that never commits, holds vacuously; that is reported.

Pure: no IO, no clock, no randomness. The same pack and model always give the same report.
~~~

## Public symbols

* [`FORMAT`](/symbols/application/law_proof/FORMAT.md) (constant) - no docstring
* [`LAW_HANDLING`](/symbols/application/law_proof/LAW_HANDLING.md) (constant) - no docstring
* [`LIMITS`](/symbols/application/law_proof/LIMITS.md) (constant) - no docstring
* [`MAX_CONFIGURATIONS`](/symbols/application/law_proof/MAX_CONFIGURATIONS.md) (constant) - no docstring
* [`OUTSIDER`](/symbols/application/law_proof/OUTSIDER.md) (constant) - no docstring
* [`Passed`](/symbols/application/law_proof/Passed.md) (type-alias) - no docstring
* [`actor_classes`](/symbols/application/law_proof/actor_classes.md) (function) - One actor per role (declared or used) and per combination of `active` and `assigned`, and an outsider.
* [`compare_laws`](/symbols/application/law_proof/compare_laws.md) (function) - Which laws a draft adds, removes or changes.
* [`prove_laws`](/symbols/application/law_proof/prove_laws.md) (function) - Every law of the pack, judged on `model` (the pack's own by default), with the evidence for each verdict.
* [`with_laws`](/symbols/application/law_proof/with_laws.md) (function) - The pack with its law file replaced by `laws` (a draft edited in PlayIDE), checked as the pack loader checks it.

## Internal imports

* [`application/memo`](/modules/application/memo.md)
* [`application/simulation`](/modules/application/simulation.md)
* [`domain/laws`](/modules/domain/laws.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/policy`](/modules/domain/policy.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.memo](/modules/application/memo.md) - Ask the kernel the same question of the same frozen model once (ADR-0199).
* [application.simulation](/modules/application/simulation.md) - Seeded simulation of people using the app built from a model (ADR-0152).
* [domain.laws](/modules/domain/laws.md) - Typed law DSL of a domain pack: what a workflow may never do, stated as data (WBS 1.1/1.2).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.

## Referenced by

* [application.readiness](/modules/application/readiness.md) - What's missing (ADR-0216): one list across every model and view of what is not ready yet, so a system built in chat or on the canvas says what it still lacks i…
* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [application.law_proof.FORMAT](/symbols/application/law_proof/FORMAT.md) - Constant `FORMAT` in `application/law_proof`.
* [application.law_proof.LAW_HANDLING](/symbols/application/law_proof/LAW_HANDLING.md) - Constant `LAW_HANDLING` in `application/law_proof`.
* [application.law_proof.LIMITS](/symbols/application/law_proof/LIMITS.md) - Constant `LIMITS` in `application/law_proof`.
* [application.law_proof.MAX_CONFIGURATIONS](/symbols/application/law_proof/MAX_CONFIGURATIONS.md) - Constant `MAX_CONFIGURATIONS` in `application/law_proof`.
* [application.law_proof.OUTSIDER](/symbols/application/law_proof/OUTSIDER.md) - Constant `OUTSIDER` in `application/law_proof`.
* [application.law_proof.Passed](/symbols/application/law_proof/Passed.md) - Type alias `Passed` in `application/law_proof`.
* [application.law_proof.actor_classes](/symbols/application/law_proof/actor_classes.md) - One actor per role (declared or used) and per combination of `active` and `assigned`, and an outsider.
* [application.law_proof.compare_laws](/symbols/application/law_proof/compare_laws.md) - Which laws a draft adds, removes or changes.
* [application.law_proof.prove_laws](/symbols/application/law_proof/prove_laws.md) - Every law of the pack, judged on `model` (the pack's own by default), with the evidence for each verdict.
* [application.law_proof.with_laws](/symbols/application/law_proof/with_laws.md) - The pack with its law file replaced by `laws` (a draft edited in PlayIDE), checked as the pack loader checks it.
<!-- okf:generated:end links -->
