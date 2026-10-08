# ADR-0154: Use case diagrams, and screens designed against the model

* Status: accepted
* Date: 2026-10-08
* Lane: PlayIDE (owner direction, 8 October 2026)

## Context and problem statement

PlayIDE shows the workflow as a state machine ([ADR-0151](0151-playide-canvas-and-build-and-run.md)) and the data as a class diagram ([ADR-0153](0153-data-models-as-uml-class-diagrams.md)). The owner's roadmap asks next for use cases and a UI designer: engineers who know UML expect a use case diagram, and they want to design the app's screens in the IDE, then test them in place. A free-form page builder would let a screen promise what the model does not allow, or leave out what the model needs.

## Decision drivers

* One source per fact. Use cases are not a new model: each one is an action of the workflow, plus starting a record. Screens bind to use cases and to the record class's attributes by name.
* Screens decide how the app looks, never what it may do. Who may act, when and with what effect stays with the kernel.
* Design, then test in place: the design check runs as you edit, and Build & run builds the app with the designed screens.
* No app is built from a screen that cannot be used.
* Pack digests stay unchanged; a pack without screens behaves as before.

## Considered options

* An optional `screens.json` per pack (`eija.screens.v1`), one screen per use case, with a design check and a native HTML5 drag-and-drop designer (chosen).
* GrapesJS (BSD-3-Clause) as the designer. Rejected: its output is free HTML and CSS bound to nothing in the model, it needs inline styles that the strict CSP refuses, and it is far heavier than the problem.
* JSON Forms (MIT) UI schemas. Close in shape (a layout of controls bound to properties), but it needs JSON Schema and a React, Angular or Vue renderer, and a UI schema has no notion of use cases.
* Craft.js (MIT). A React page editor; the same objections as GrapesJS without the CSP issue.

## Decision outcome

Chosen option: `domain/screens.py` and a **Screens** tab.

* `use_cases(model)` is `create`, then each distinct workflow action in transition-id order. The **Use cases** tab draws them in UML: a system boundary named after the pack, a use case ellipse per action plus "Create <record>", an actor per role, and an association from each role to the use cases it may perform. Use cases are grouped by role and each actor sits beside its group, so no association crosses a use case. Double-click a use case to design its screen.
* `Screens` (`eija.screens.v1`) holds one `Screen` per use case: a title, the record attributes it shows (in order, each with an optional label) and its button label. `default_screens` gives every use case a screen when the pack has no `screens.json`: `create` asks for every record attribute, an action shows the required ones. `parse_screens` refuses malformed screens (`SCREENS_INVALID`) and another pack's (`SCREENS_PACK_MISMATCH`).
* `check_screens` returns design problems with stable codes: `SCREEN_UNKNOWN_USE_CASE`, `SCREEN_DUPLICATE_USE_CASE`, `SCREEN_UNKNOWN_ATTRIBUTE`, `SCREEN_MISSING_CREATE`, and `SCREEN_MISSING_REQUIRED` when the create screen leaves out a required attribute, so nobody could create a record. `generate` refuses screens with any problem (`SCREENS_BLOCKED`).
* `eija build` writes `app/screens.json`. The oracle records the screens digest and the conformance suite checks that the app was built with those screens and that they pass the design check; a screens file swapped after the build fails conformance. The generated page takes the create form's attributes, order, labels, title and button from the create screen, and each action button's label from its screen. The server still checks every value with `check_values`, and the kernel still decides every action.
* PlayIDE: `POST /api/play/screens` returns the screens (the request's, else the pack's, else the defaults), the use cases and the design problems. The **Screens** tab lists the use cases with a ✓ or ⚠, shows the selected screen as a card, and offers the record's attributes as a palette. Drag an attribute onto the screen (or press Add), drag rows to reorder them (or use ↑), rename labels, title and button, or remove a row. Each edit reruns the design check. **Build & run** sends the edited screens, and the built app is keyed by model hash, data model digest and screens digest. **Download screens.json** saves the design to put beside `pack.json`.
* The library-loan pack has an authored `screens.json`; the other packs use the defaults.

### Consequences

* Good: a screen can only show what the record has, and the create screen cannot forget what the data model requires.
* Good: the design is tested in place: one click builds and runs the app with it, and the kernel conformance score covers it.
* Bad: the designer does not write `screens.json` into the pack; the engineer downloads it and commits it. Saving through typed transactions comes with the drag-and-drop palettes.
* Bad: a screen holds fields, a title and a button. There is no free layout, no styling, and no screens beyond one per use case.
* Revisit when: screens need layout (columns, sections), or exporting to JSON Forms UI schemas is wanted for interchange.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| GrapesJS | Free HTML/CSS bound to nothing in the model; inline styles conflict with the strict CSP; heavy | — |
| JSON Forms UI schema | Needs JSON Schema and a framework renderer; no use cases | Export `Screens` to a JSON Forms UI schema |
| Craft.js | React page editor bound to nothing in the model | — |
| HTML5 drag and drop | Adopted (native, no dependency) | — |
| maxGraph `actor` and `ellipse` shapes | Adopted for the use case diagram | — |
