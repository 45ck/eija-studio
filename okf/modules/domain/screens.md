---
type: Module
title: domain.screens
description: 'Screens: the user interface of a pack''s app, designed against its use cases and data model (ADR-0154).'
resource: repo://src/eija_studio/domain/screens.py
tags:
- module
- domain
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/screens.py
  title: domain/screens.py
  hash_method: ast-api-v1
  sha256: 0edcb505de6874646dce6d1500dc52312aecba338ef72c74b0e60e09010a4970
notes_baseline: a28f5ac34e371621ceca7580ad068200ba640abca24df2ed2053a76597795921
---

# domain.screens

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | domain |
| Code | `repo://src/eija_studio/domain/screens.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Screens: the user interface of a pack's app, designed against its use cases and data model (ADR-0154).

A screen belongs to one use case: creating a record (`use_case` null, so no workflow action, whatever its name, can
collide with it) or an action of the workflow. It lists the record
attributes it shows, in order and with their labels, and names its button. Screens decide how the app looks, never
what it may do: who may act, when and with what effect stays with the kernel. They live in an optional
`screens.json` beside the pack's `pack.json` with their own digest; a pack without one gets `default_screens`.
Authored screens are completed with a default screen for each use case they leave out, so a new action always has
one. `check_screens` is the design check PlayIDE runs as you edit, and an app is never built from screens it rejects.
~~~

## Public symbols

* [`CREATE`](/symbols/domain/screens/CREATE.md) (constant) - no docstring
* [`SCREENS_FILE`](/symbols/domain/screens/SCREENS_FILE.md) (constant) - no docstring
* [`Screen`](/symbols/domain/screens/Screen.md) (class) - no docstring
* [`ScreenField`](/symbols/domain/screens/ScreenField.md) (class) - no docstring
* [`Screens`](/symbols/domain/screens/Screens.md) (class) - no docstring
* [`check_screens`](/symbols/domain/screens/check_screens.md) (function) - Design problems, each with a stable code and the use case it is about.
* [`default_screen`](/symbols/domain/screens/default_screen.md) (function) - The screen a use case gets when nobody designed one: `create` asks for every record attribute; an action shows the requ…
* [`default_screens`](/symbols/domain/screens/default_screens.md) (function) - One default screen per use case.
* [`load_screens`](/symbols/domain/screens/load_screens.md) (function) - The pack's screens, or None when the pack has no `screens.json`.
* [`parse_screens`](/symbols/domain/screens/parse_screens.md) (function) - no docstring
* [`require_buildable`](/symbols/domain/screens/require_buildable.md) (function) - no docstring
* [`screens_for`](/symbols/domain/screens/screens_for.md) (function) - The screens beside this pack's `pack.json`, each use case they leave out given its default screen; or the defaults.
* [`use_cases`](/symbols/domain/screens/use_cases.md) (function) - Creating a record (None), then each distinct action in transition-id order: the ellipses of the use case diagram.

## Internal imports

* [`domain/data`](/modules/domain/data.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [application.appgen](/modules/application/appgen.md) - App generation: a reviewed workflow model becomes a runnable app and its conformance oracle (ADR-0150).
* [application.new_system](/modules/application/new_system.md) - Start a new system (ADR-0185): the pack documents for a system started from a sketch or copied from a template.
* [application.ripple](/modules/application/ripple.md) - Ripple (ADR-0158): what one change to the state machine does to every other diagram of the same system, and the follow-on edits that would keep them in agreeme…
* [interfaces.app_build](/modules/interfaces/app_build.md) - `eija build`: write a runnable app generated from a pack's model, then run its kernel conformance tests (ADR-0150).
* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [interfaces.play_systems](/modules/interfaces/play_systems.md) - PlayIDE's systems (ADR-0185): start a new system from a sketch or a template, open one you made before, and save the work in progress to carry on later.
* [domain.screens.CREATE](/symbols/domain/screens/CREATE.md) - Constant `CREATE` in `domain/screens`.
* [domain.screens.SCREENS_FILE](/symbols/domain/screens/SCREENS_FILE.md) - Constant `SCREENS_FILE` in `domain/screens`.
* [domain.screens.Screen](/symbols/domain/screens/Screen.md) - `class Screen(Contract)` in `domain/screens`.
* [domain.screens.Screen.unique](/symbols/domain/screens/Screen.unique.md) - `def unique(self) -> Screen` in `domain/screens`.
* [domain.screens.ScreenField](/symbols/domain/screens/ScreenField.md) - `class ScreenField(Contract)` in `domain/screens`.
* [domain.screens.Screens.digest](/symbols/domain/screens/Screens.digest.md) - `def digest(self) -> str` in `domain/screens`.
* [domain.screens.Screens](/symbols/domain/screens/Screens.md) - `class Screens(Contract)` in `domain/screens`.
* [domain.screens.Screens.screen](/symbols/domain/screens/Screens.screen.md) - `def screen(self, use_case: str | None) -> Screen | None` in `domain/screens`.
* [domain.screens.check_screens](/symbols/domain/screens/check_screens.md) - Design problems, each with a stable code and the use case it is about.
* [domain.screens.default_screen](/symbols/domain/screens/default_screen.md) - The screen a use case gets when nobody designed one: `create` asks for every record attribute; an action shows the required ones.
* [domain.screens.default_screens](/symbols/domain/screens/default_screens.md) - One default screen per use case.
* [domain.screens.load_screens](/symbols/domain/screens/load_screens.md) - The pack's screens, or None when the pack has no `screens.json`.
* [domain.screens.parse_screens](/symbols/domain/screens/parse_screens.md) - `def parse_screens(document: Any, pack_id: str) -> Screens` in `domain/screens`.
* [domain.screens.require_buildable](/symbols/domain/screens/require_buildable.md) - `def require_buildable(screens: Screens, model: Workflow, data: DataModel | None) -> None` in `domain/screens`.
* [domain.screens.screens_for](/symbols/domain/screens/screens_for.md) - The screens beside this pack's `pack.json`, each use case they leave out given its default screen; or the defaults.
* [domain.screens.use_cases](/symbols/domain/screens/use_cases.md) - Creating a record (None), then each distinct action in transition-id order: the ellipses of the use case diagram.
<!-- okf:generated:end links -->
