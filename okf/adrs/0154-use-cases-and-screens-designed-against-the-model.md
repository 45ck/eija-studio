---
type: Architecture Decision Record
title: 'ADR-0154: Use case diagrams, and screens designed against the model'
description: PlayIDE shows the workflow as a state machine (ADR-0151) and the data as a class diagram (ADR-0153).
resource: repo://docs/adr/0154-use-cases-and-screens-designed-against-the-model.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0154-use-cases-and-screens-designed-against-the-model.md
  title: 0154-use-cases-and-screens-designed-against-the-model.md
  hash_method: lf-sha256-v1
  sha256: 96fd161d3f4ea8caf2862cef9bbf2e22fc73ba1e46f8d0d7e20056f4bd2283cf
notes_baseline: b9f21b9d179a3080a39071550e430373fd39c62af4a5aaac6728e6161e8d9649
---

# ADR-0154: Use case diagrams, and screens designed against the model

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-08 |
| Lane | PlayIDE (owner direction, 8 October 2026) |
| Source | `repo://docs/adr/0154-use-cases-and-screens-designed-against-the-model.md` |

## Decision outcome (verbatim)

> Chosen option: `domain/screens.py` and a **Screens** tab.
>
> * `use_cases(model)` is creating a record, then each distinct workflow action in transition-id order. Creating a record is the screen with no `use_case` (null), so no workflow action, even one named `create`, can collide with it. The **Use cases** tab draws them in UML: a system boundary named after the pack, a use case ellipse per action plus "Create <record>", an actor per role, and an association from each role to the use cases it may perform. Use cases are grouped by role and each actor sits beside its group, so no association crosses a use case. Double-click a use case to design its screen.
> * `Screens` (`eija.screens.v1`) holds one `Screen` per use case: a title, the record attributes it shows (in order, each with an optional label) and its button label. `default_screens` gives every use case a screen when the pack has no `screens.json`: the create screen asks for every record attribute, an action shows the required ones. Authored screens are completed with a default screen for each use case they leave out, so a model with a new action still has a screen for it. `parse_screens` refuses malformed screens (`SCREENS_INVALID`) and another pack's (`SCREENS_PACK_MISMATCH`).
> * `check_screens` returns design problems with stable codes: `SCREEN_UNKNOWN_USE_CASE`, `SCREEN_DUPLICATE_USE_CASE`, `SCREEN_UNKNOWN_ATTRIBUTE`, `SCREEN_MISSING_CREATE`, `SCREEN_MISSING_USE_CASE`, and `SCREEN_MISSING_REQUIRED` when the create screen leaves out a required attribute, so nobody could create a record. `generate` refuses screens with any problem (`SCREENS_BLOCKED`).
> * `eija build` writes `app/screens.json`. The oracle records the screens digest and the conformance suite checks that the app was built with those screens and that they pass the design check; a screens file swapped after the build fails conformance. The generated page takes the create form's attributes, order, labels, title and button from the create screen. Choosing an action opens that action's screen: its title, the record values it shows in its order and under its labels, and its button, which runs the action. The server still checks every value with `check_values`, and the kernel still decides every action.
> * PlayIDE: `POST /api/play/screens` returns the screens (the request's, else the pack's, else the defaults), the use cases and the design problems. The **Screens** tab lists every use case with a ✓ or ⚠ (a use case without a screen can be given one, and a screen for a use case the model no longer has can be removed), shows the selected screen as a card, and offers the record's attributes as a palette. Drag an attribute onto the screen (or press Add), drag rows to reorder them (or use ↑), rename labels, title and button, or remove a row. Each edit reruns the design check. **Build & run** sends the edited screens, and the built app is keyed by model hash, data model digest and screens digest. **Download screens.json** saves the design to put beside `pack.json`.
> * The library-loan pack has an authored `screens.json`; the other packs use the defaults.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0151: PlayIDE canvas with Build & run of the live app](/adrs/0151-playide-canvas-and-build-and-run.md) - The owner wants EIJA to feel like "UML you can trust to build apps": a visual, mouse-driven IDE (named PlayIDE) where a UML-literate engineer designs a system…
* [ADR-0153: Data models as UML class diagrams, checked in the built app](/adrs/0153-data-models-as-uml-class-diagrams.md) - Until now, records in a built app (ADR-0150) carried only a title, because the model had no data.

## Referenced by

* [ADR-0215: See and run the app as each role](/adrs/0215-see-and-run-the-app-as-each-role.md) - PlayIDE already models the human side of a system: roles and fixture actors in the pack, a use case diagram (ADR-0154), one screen per use case, and a Permissi…
<!-- okf:generated:end links -->
