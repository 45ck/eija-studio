---
type: Module
title: application.app_runs
description: 'The app oracle''s runs that start from a record the app itself creates (ADR-0243): who may start one and where it starts, a run from a new record to each transition, the actions offered in each state, and the rule table…'
resource: repo://src/eija_studio/application/app_runs.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/app_runs.py
  title: application/app_runs.py
  hash_method: ast-api-v1
  sha256: dadc5ac8d2d41e57a2b8717c918b603fb6f5526486e6c065479415b8f6a4f341
notes_baseline: 23ad0ffb576e970c0c9998264d1895873794bd9aec1ddf62a3f80592a0f2dd75
---

# application.app_runs

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/app_runs.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
The app oracle's runs that start from a record the app itself creates (ADR-0243): who may start one and where it
starts, a run from a new record to each transition, the actions offered in each state, and the rule table shown.
Each answer is the kernel's, asked through `OracleSession`.
~~~

## Public symbols

* [`create_cases`](/symbols/application/app_runs/create_cases.md) (function) - Every fixture actor, and one unknown actor, starting a record with valid values: the state and version it starts in, or…
* [`journeys`](/symbols/application/app_runs/journeys.md) (function) - For each transition, a record started through the app and walked to it: the shortest run from the initial state whose l…
* [`options_cases`](/symbols/application/app_runs/options_cases.md) (function) - What the app offers each fixture actor (and one unknown actor) on a record in each state that holds valid values: every…
* [`rules`](/symbols/application/app_runs/rules.md) (function) - The rule table the app shows: each action once, every state it leaves, where it leads and who takes it.

## Internal imports

* [`application/oracle_session`](/modules/application/oracle_session.md)
* [`application/runtime`](/modules/application/runtime.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.oracle_session](/modules/application/oracle_session.md) - The in-memory session the app oracle asks the kernel through (ADR-0150): one record, nothing persists.
* [application.runtime](/modules/application/runtime.md) - Generic execution algorithm; the domain (policy, laws, typed effects) comes from the pack.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [application.appgen](/modules/application/appgen.md) - App generation: a reviewed workflow model becomes a runnable app and its conformance oracle (ADR-0150).
* [application.app_runs.create_cases](/symbols/application/app_runs/create_cases.md) - Every fixture actor, and one unknown actor, starting a record with valid values: the state and version it starts in, or the refusal.
* [application.app_runs.journeys](/symbols/application/app_runs/journeys.md) - For each transition, a record started through the app and walked to it: the shortest run from the initial state whose last step is that transition, each step t…
* [application.app_runs.options_cases](/symbols/application/app_runs/options_cases.md) - What the app offers each fixture actor (and one unknown actor) on a record in each state that holds valid values: every action leaving that state, and whether…
* [application.app_runs.rules](/symbols/application/app_runs/rules.md) - The rule table the app shows: each action once, every state it leaves, where it leads and who takes it.
<!-- okf:generated:end links -->
