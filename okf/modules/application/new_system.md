---
type: Module
title: application.new_system
description: 'Start a new system (ADR-0185): the pack documents for a system started from a sketch or copied from a template.'
resource: repo://src/eija_studio/application/new_system.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/new_system.py
  title: application/new_system.py
  hash_method: ast-api-v1
  sha256: 5592f7cdf4bfcc47d66a733c2a901dc49e12f01124a9990bbd9e94130731d655
notes_baseline: b379831e1b9788d60750c57d34a594ae4ceffbc0126f0ece1084d3d2df8df42f
---

# application.new_system

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/new_system.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Start a new system (ADR-0185): the pack documents for a system started from a sketch or copied from a template.

A system is a pack: `pack.json`, with `data.json`, `screens.json` and `scenarios.json` beside it when it has them. This module only
writes documents; the kernel's own pack check (`parse_pack`) decides whether they are a system at all, and the
caller saves them. A sketch is one transition per line in the state machine's own label notation,
`From -> To : Action [Role]`, so what you type is what the diagram draws. Nothing here infers laws, effects
beyond one audit entry per action, or meanings the person did not write.
~~~

## Public symbols

* [`FIELD`](/symbols/application/new_system/FIELD.md) (constant) - no docstring
* [`LINE`](/symbols/application/new_system/LINE.md) (constant) - no docstring
* [`LIST`](/symbols/application/new_system/LIST.md) (constant) - no docstring
* [`MAX_LINES`](/symbols/application/new_system/MAX_LINES.md) (constant) - no docstring
* [`NAME`](/symbols/application/new_system/NAME.md) (constant) - no docstring
* [`RECORD`](/symbols/application/new_system/RECORD.md) (constant) - no docstring
* [`SKETCH_HELP`](/symbols/application/new_system/SKETCH_HELP.md) (constant) - no docstring
* [`UNSUPPORTED`](/symbols/application/new_system/UNSUPPORTED.md) (constant) - no docstring
* [`classes`](/symbols/application/new_system/classes.md) (function) - A system's record class and each class's attribute names, for naming data-model steps (ADR-0202); None when the system…
* [`declare`](/symbols/application/new_system/declare.md) (function) - `pack` with every action and role `transactions` name but it does not declare yet, declared exactly as a sketch declare…
* [`new_names`](/symbols/application/new_system/new_names.md) (function) - The actions and roles `transactions` name that `pack` does not declare, in order of first use.
* [`parse_sketch`](/symbols/application/new_system/parse_sketch.md) (function) - The transitions, extra actions and extra roles of a sketch, or `PackError` naming each bad line.
* [`sketch_documents`](/symbols/application/new_system/sketch_documents.md) (function) - `pack.json` and `data.json` for a system started from a sketch, checked by the kernel's pack check.
* [`summary`](/symbols/application/new_system/summary.md) (function) - What the new system has, for the form to say before it is created.
* [`system_id`](/symbols/application/new_system/system_id.md) (function) - A pack id for a new system called `name`, unlike every id in `taken`.
* [`template_documents`](/symbols/application/new_system/template_documents.md) (function) - A copy of a template's documents as a new system: new id and name, the same model, rules, laws, screens and test cases…

## Internal imports

* [`domain/data`](/modules/domain/data.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/scenarios`](/modules/domain/scenarios.md)
* [`domain/screens`](/modules/domain/screens.md)
* [`domain/transactions`](/modules/domain/transactions.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.scenarios](/modules/domain/scenarios.md) - Scenarios: a pack's test cases, written as stories a person can read and the kernel can run (ADR-0177).
* [domain.screens](/modules/domain/screens.md) - Screens: the user interface of a pack's app, designed against its use cases and data model (ADR-0154).
* [domain.transactions](/modules/domain/transactions.md) - Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.

## Referenced by

* [adapters.plan_proposals](/modules/adapters/plan_proposals.md) - Offline plan proposer for the PlayIDE chat (ADR-0156): a bounded phrase grammar and the pack's modelled meanings, never an LLM.
* [application.data_steps](/modules/application/data_steps.md) - Data-model steps in a chat plan (ADR-0202): add an attribute to a class, remove one, or make one required or optional; and the step that changes the kind of ac…
* [application.plan](/modules/application/plan.md) - Plan mode for the PlayIDE chat (ADR-0156): an AI proposes a change as numbered typed steps; the person accepts or rejects each one and sees what the accepted o…
* [interfaces.play_systems](/modules/interfaces/play_systems.md) - PlayIDE's systems (ADR-0185): start a new system from a sketch or a template, open one you made before, and save the work in progress to carry on later.
* [application.new_system.FIELD](/symbols/application/new_system/FIELD.md) - Constant `FIELD` in `application/new_system`.
* [application.new_system.LINE](/symbols/application/new_system/LINE.md) - Constant `LINE` in `application/new_system`.
* [application.new_system.LIST](/symbols/application/new_system/LIST.md) - Constant `LIST` in `application/new_system`.
* [application.new_system.MAX_LINES](/symbols/application/new_system/MAX_LINES.md) - Constant `MAX_LINES` in `application/new_system`.
* [application.new_system.NAME](/symbols/application/new_system/NAME.md) - Constant `NAME` in `application/new_system`.
* [application.new_system.RECORD](/symbols/application/new_system/RECORD.md) - Constant `RECORD` in `application/new_system`.
* [application.new_system.SKETCH_HELP](/symbols/application/new_system/SKETCH_HELP.md) - Constant `SKETCH_HELP` in `application/new_system`.
* [application.new_system.UNSUPPORTED](/symbols/application/new_system/UNSUPPORTED.md) - Constant `UNSUPPORTED` in `application/new_system`.
* [application.new_system.classes](/symbols/application/new_system/classes.md) - A system's record class and each class's attribute names, for naming data-model steps (ADR-0202); None when the system has no class diagram.
* [application.new_system.declare](/symbols/application/new_system/declare.md) - `pack` with every action and role `transactions` name but it does not declare yet, declared exactly as a sketch declares them (ADR-0201): an action gets the ba…
* [application.new_system.new_names](/symbols/application/new_system/new_names.md) - The actions and roles `transactions` name that `pack` does not declare, in order of first use.
* [application.new_system.parse_sketch](/symbols/application/new_system/parse_sketch.md) - The transitions, extra actions and extra roles of a sketch, or `PackError` naming each bad line.
* [application.new_system.sketch_documents](/symbols/application/new_system/sketch_documents.md) - `pack.json` and `data.json` for a system started from a sketch, checked by the kernel's pack check.
* [application.new_system.summary](/symbols/application/new_system/summary.md) - What the new system has, for the form to say before it is created.
* [application.new_system.system_id](/symbols/application/new_system/system_id.md) - A pack id for a new system called `name`, unlike every id in `taken`.
* [application.new_system.template_documents](/symbols/application/new_system/template_documents.md) - A copy of a template's documents as a new system: new id and name, the same model, rules, laws, screens and test cases (`scenarios.json`).
<!-- okf:generated:end links -->
