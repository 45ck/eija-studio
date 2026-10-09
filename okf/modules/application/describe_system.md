---
type: Module
title: application.describe_system
description: 'Describe your app (ADR-0216): a new system from one description, like starting an app in Lovable or Replit.'
resource: repo://src/eija_studio/application/describe_system.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/describe_system.py
  title: application/describe_system.py
  hash_method: ast-api-v1
  sha256: f5e565888a102c0d6f155cb2e18a9aa08c1b7a010bb71761fe62ac783320e57d
notes_baseline: 424dbb33fa92dbb4b8518519eadc27e2eb18588e72ff3c1d2da42bd559c52310
---

# application.describe_system

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/describe_system.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Describe your app (ADR-0216): a new system from one description, like starting an app in Lovable or Replit.

A describer (an application port; offline here) reads the description as an app shape: a record class, a state
machine in the sketch's label notation, roles and the record's fields. Nothing it says is trusted. The documents are
built exactly as a sketch's are (`new_system.sketch_documents`, ADR-0185), the fields are added to the record class
and checked by the data model's own contract, and test cases are recorded by running the kernel: the path to each end
state and one refusal, each step written as what the kernel did (`scenario_run.record_steps`). Laws are not
generated: a law is protected policy, so the person writes it (the Laws tab), and "What's missing" says none is set.
Every other view (use cases, screens, sequences, components, permissions) is derived from these documents as for any
system.
~~~

## Public symbols

* [`MAX_DESCRIPTION`](/symbols/application/describe_system/MAX_DESCRIPTION.md) (constant) - no docstring
* [`describe_documents`](/symbols/application/describe_system/describe_documents.md) (function) - The documents of a new system described in `text`, checked by the kernel, and what the describer read.
* [`described_summary`](/symbols/application/describe_system/described_summary.md) (function) - What a described system has in every view, for the form to say before it is created.
* [`tests_for`](/symbols/application/describe_system/tests_for.md) (function) - Test cases for a new system, recorded by the kernel: the way to each end state, and the first step taken by a role that…

## Internal imports

* [`application/new_system`](/modules/application/new_system.md)
* [`application/ports`](/modules/application/ports.md)
* [`application/scenario_run`](/modules/application/scenario_run.md)
* [`domain/data`](/modules/domain/data.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.new_system](/modules/application/new_system.md) - Start a new system (ADR-0185): the pack documents for a system started from a sketch or copied from a template.
* [application.ports](/modules/application/ports.md) - Application-owned ports.
* [application.scenario_run](/modules/application/scenario_run.md) - Run a pack's scenarios (its test cases) through the kernel, and record new ones (ADR-0177).
* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [interfaces.play_systems](/modules/interfaces/play_systems.md) - PlayIDE's systems (ADR-0185): start a new system from a sketch or a template, open one you made before, and save the work in progress to carry on later.
* [application.describe_system.MAX_DESCRIPTION](/symbols/application/describe_system/MAX_DESCRIPTION.md) - Constant `MAX_DESCRIPTION` in `application/describe_system`.
* [application.describe_system.describe_documents](/symbols/application/describe_system/describe_documents.md) - The documents of a new system described in `text`, checked by the kernel, and what the describer read.
* [application.describe_system.described_summary](/symbols/application/describe_system/described_summary.md) - What a described system has in every view, for the form to say before it is created.
* [application.describe_system.tests_for](/symbols/application/describe_system/tests_for.md) - Test cases for a new system, recorded by the kernel: the way to each end state, and the first step taken by a role that may not take it.
<!-- okf:generated:end links -->
