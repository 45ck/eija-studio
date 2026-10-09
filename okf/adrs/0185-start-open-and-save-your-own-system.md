---
type: Architecture Decision Record
title: 'ADR-0185: Start, open and save your own system in PlayIDE'
description: PlayIDE could only show the pack the server was started with (`eija serve --pack …`), and every pack was one that ships with EIJA.
resource: repo://docs/adr/0185-start-open-and-save-your-own-system.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0185-start-open-and-save-your-own-system.md
  title: 0185-start-open-and-save-your-own-system.md
  hash_method: lf-sha256-v1
  sha256: aa19ae545bf1a8e5df7a70bc282d76feb0656d13efbaa5c18f2cc3112c3a2adf
notes_baseline: fef892ad61a147f586465173b13573e90dc61a1e4e7f44005536f6fe49064365
---

# ADR-0185: Start, open and save your own system in PlayIDE

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted for state-machine systems |
| Date | 2026-10-08 |
| Lane | PlayIDE (owner direction, 8 October 2026) |
| Source | `repo://docs/adr/0185-start-open-and-save-your-own-system.md` |

## Decision outcome (verbatim)

> Chosen option.
>
> * **Sketch.** `application/new_system.py` turns a name, a record class and a sketch into `pack.json` and `data.json`. A sketch has one transition per line, `From -> To : Action [Role]`, which is how the state machine labels it. Optional `actions: A, B` and `roles: C` lines declare actions and roles to draw later. Every bad line is named (`line 3: action Fix already labels line 2`). States, actions and roles that differ only in case (`Agent` and `agent`) are refused, because chat matches names ignoring case and one would hide the other. The pack gets one audit effect per action, one active user per role and one revoked user, and the `runtime_matrix` verifier. It gets no laws and no supported meanings, because the person did not write any. The record class gets one attribute, `title`.
> * **Template.** A copy of a shipped pack (`library-loan`, `excursion`, `eija-review-slice`) with a new id and name. It keeps the model, rules, laws, data, screens and test cases (`scenarios.json`, ADR-0177). Laws are copied as they are: starting a system never loosens or drops one. What belonged only to the template is dropped: the language terms' `repo://` bindings, and any `hand_encoded` formal model, which becomes `not_run` with the reason.
> * **Check.** Both paths end in `parse_pack`, `parse_data`, `parse_screens` and `parse_scenarios`. The dialog checks as you type (`check_only`) and shows the kernel's problems or what will be created. Nothing is written until the documents pass.
> * **Where.** `adapters/system_library.py` keeps systems in a systems home (`--systems`, `EIJA_SYSTEMS`, default `~/PlayIDE`): `<home>/<id>/pack.json`, `data.json`, `screens.json`, `scenarios.json`, and the system's own workspace `.eija/`. A system is written into a staging folder, then renamed, and never over an existing one. `recent.json` lists the last 12 systems opened.
> * **Open.** `interfaces/play_systems.py` puts the studio behind a `StudioHandle`. Opening a system builds a studio for it with the same provider settings, on its own workspace, stops the running app and swaps the studio in; the page reloads. Only the system the server started with, systems in the home and systems on the recent list can be opened, never an arbitrary path from the page.
> * **Save.** The draft is the page's work in progress: the plan's steps as typed transactions with who wrote them, which ones are ticked, and the screens if edited. **Save** or Ctrl+S writes it to `draft.json` in the system's workspace. Each step's shape is checked on save. Opening the system again restores the plan and asks the server to check every step through the policy again, like any plan. If the model in force changed since, PlayIDE says so. The draft is never applied, and the preview banner now says "Nothing is applied to the model".
> * **CLI.** `eija new "Support desk" --sketch desk.txt --record Ticket` or `eija new Trips --from excursion` makes the same system and prints the `eija serve` line to open it.
> * **Routes.** `GET /api/play/systems`, `POST /api/play/systems/new`, `POST /api/play/systems/open`, `GET` and `POST /api/play/draft`, `POST /api/play/draft/clear`. They exist only when the server is started with systems (`eija serve`); a test app without them hides the controls.

## Sections

* Context and problem statement
* Decision drivers
* What existing tools do
* Considered options
* Decision outcome
* Verification

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://tests/test_play_systems.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0177: The law file and the test cases are files PlayIDE opens, edits as drafts and runs](/adrs/0177-law-files-and-test-cases-in-playide.md) - The owner asked where the formal law files and the test cases are.

## Referenced by

* [ADR-0190: UML import and export: XMI, PlantUML, Mermaid and draw.io, with every import judged by the kernel](/adrs/0190-uml-import-and-export-through-the-kernel.md) - PlayIDE's users already know UML and already keep UML somewhere else: XMI in Enterprise Architect, Cameo, Papyrus or Visual Paradigm; PlantUML beside the code;…
* [ADR-0198: Undo, redo and autosave of the edited document in PlayIDE](/adrs/0198-undo-redo-and-autosave-of-the-edited-document.md) - PlayIDE is meant to be more robust than the UML tools engineers already use, and every one of those has undo.
* [ADR-0201: Build a new system in chat, round after round](/adrs/0201-build-a-new-system-in-chat-round-after-round.md) - The showcase changes a pack that already exists (Library loan).
* [ADR-0202: Grow the class diagram in chat](/adrs/0202-grow-the-class-diagram-in-chat.md) - ADR-0201 let a system started from a sketch grow its state machine round after round in chat.
* [ADR-0203: Describe your app, and what's missing](/adrs/0203-describe-your-app-and-whats-missing.md) - Until now a new system started from three sketch lines, a template or a UML file (ADR-0185, ADR-0190), and then grew in chat (ADR-0201, ADR-0202).
<!-- okf:generated:end links -->
