# ADR-0185: Start, open and save your own system in PlayIDE

* Status: accepted for state-machine systems
* Date: 2026-10-08
* Lane: PlayIDE (owner direction, 8 October 2026)

## Context and problem statement

PlayIDE could only show the pack the server was started with (`eija serve --pack …`), and every pack was one that ships with EIJA. The owner wants to use PlayIDE on his own systems. That needs four things it did not have:

* a way to start a new system, from nothing or from a template;
* a place where that system lives, so it can be opened again;
* a list of recent systems, so switching is one click;
* a way to keep the work in progress. Until now a plan or a drawn change was lost when the page was closed.

The kernel still has to check whatever a person creates. A system that the pack check (`parse_pack`) would refuse must never be created, and saving work in progress must not become a back door into the model in force.

## Decision drivers

* A new system is an ordinary pack: no second format and no second interpreter.
* The kernel's own pack check decides whether a new system is valid, as the person types.
* What you type to start a system should look like what the diagram draws.
* Each system keeps its own change cases, history and drafts. A workspace is already bound to one pack's exact digest (`PACK_MISMATCH`), so each system needs its own workspace.
* Saving is not applying. The model in force changes only through the review workbench, as before.
* Stay off the canvas editing (thread "PlayIDE UX, HCI and agentic HCI") and UML import and export (thread "Import and export UML").

## What existing tools do

| Tool | How you start, find and reopen work | What PlayIDE takes from it |
|---|---|---|
| VS Code (MIT) | Welcome page, File > Open Recent, one folder per workspace, a dot on unsaved editors and Ctrl+S. | A recent list in a dialog, a folder per system, Ctrl+S and an "Unsaved changes" mark. |
| draw.io (Apache-2.0) | A "Create new diagram" dialog: blank or one of the templates, then a name. | Blank or a template, chosen in one dialog with a name. |
| Visual Studio | New Project from templates, and a start window listing recent solutions. | Templates are the shipped packs, each with its size. |
| [Copier](https://github.com/copier-org/copier) (MIT) and Cookiecutter (BSD-3-Clause) | Project generators that render a template folder with Jinja and answer questions. | Considered, not adopted: a template here is a pack whose only change is its id and name. Jinja in pack files would make a second way to write a pack, and the questions would not be checked by the kernel. |
| Mermaid and PlantUML state diagrams | Text such as `A --> B : label`. | The idea of a text sketch. PlayIDE's sketch uses the label the diagram already draws, `Action [Role]`, so the role is part of the line. |
| `platformdirs` (MIT) | The per-user data folder for an app. | Not needed: systems go in a visible folder (`~/PlayIDE`) the person can find, back up and put under Git. |

## Considered options

* **A system is a pack folder with its own workspace, in a systems home; the server swaps the open system in place** (chosen).
* **Restart the server for each system.** Simple, but the browser loses its session link and the person has to go back to the terminal.
* **Many systems in one workspace.** The store binds a workspace to one pack digest on purpose, so this would weaken a kernel invariant.
* **Save work in progress straight into `pack.json`.** That would change the model in force without review, and a changed pack digest would no longer open its own workspace.

## Decision outcome

Chosen option.

* **Sketch.** `application/new_system.py` turns a name, a record class and a sketch into `pack.json` and `data.json`. A sketch has one transition per line, `From -> To : Action [Role]`, which is how the state machine labels it. Optional `actions: A, B` and `roles: C` lines declare actions and roles to draw later. Every bad line is named (`line 3: action Fix already labels line 2`). States, actions and roles that differ only in case (`Agent` and `agent`) are refused, because chat matches names ignoring case and one would hide the other. The pack gets one audit effect per action, one active user per role and one revoked user, and the `runtime_matrix` verifier. It gets no laws and no supported meanings, because the person did not write any. The record class gets one attribute, `title`.
* **Template.** A copy of a shipped pack (`library-loan`, `excursion`, `eija-review-slice`) with a new id and name. It keeps the model, rules, laws, data, screens and test cases (`scenarios.json`, ADR-0177). Laws are copied as they are: starting a system never loosens or drops one. What belonged only to the template is dropped: the language terms' `repo://` bindings, and any `hand_encoded` formal model, which becomes `not_run` with the reason.
* **Check.** Both paths end in `parse_pack`, `parse_data`, `parse_screens` and `parse_scenarios`. The dialog checks as you type (`check_only`) and shows the kernel's problems or what will be created. Nothing is written until the documents pass.
* **Where.** `adapters/system_library.py` keeps systems in a systems home (`--systems`, `EIJA_SYSTEMS`, default `~/PlayIDE`): `<home>/<id>/pack.json`, `data.json`, `screens.json`, `scenarios.json`, and the system's own workspace `.eija/`. A system is written into a staging folder, then renamed, and never over an existing one. `recent.json` lists the last 12 systems opened.
* **Open.** `interfaces/play_systems.py` puts the studio behind a `StudioHandle`. Opening a system builds a studio for it with the same provider settings, on its own workspace, stops the running app and swaps the studio in; the page reloads. Only the system the server started with, systems in the home and systems on the recent list can be opened, never an arbitrary path from the page.
* **Save.** The draft is the page's work in progress: the plan's steps as typed transactions with who wrote them, which ones are ticked, and the screens if edited. **Save** or Ctrl+S writes it to `draft.json` in the system's workspace. Each step's shape is checked on save. Opening the system again restores the plan and asks the server to check every step through the policy again, like any plan. If the model in force changed since, PlayIDE says so. The draft is never applied, and the preview banner now says "Nothing is applied to the model".
* **CLI.** `eija new "Support desk" --sketch desk.txt --record Ticket` or `eija new Trips --from excursion` makes the same system and prints the `eija serve` line to open it.
* **Routes.** `GET /api/play/systems`, `POST /api/play/systems/new`, `POST /api/play/systems/open`, `GET` and `POST /api/play/draft`, `POST /api/play/draft/clear`. They exist only when the server is started with systems (`eija serve`); a test app without them hides the controls.

### Consequences

* Good: a person can start a system, build it, simulate it and keep changing it across sessions, and the kernel checks all of it. A new sketched system passes conformance on Build & run.
* Good: each system's cases, history and draft stay with it, and the workspace invariant is unchanged.
* Bad: a system's vocabulary (its actions and roles) is fixed when it is created, because drawn edits can only use declared actions, each on one transition. Declare spare actions in the sketch, or start a new system from the old one. Editing the vocabulary in PlayIDE is follow-up work.
* Bad: a draft holds at most 12 steps, the same cap as a plan preview. The draft does not yet hold a law-file or test-case draft from the Laws and Tests tabs (ADR-0177); those stay downloads.
* Good: Save never writes `pack.json`, so it cannot loosen or remove a law; a law change still goes through review, as ADR-0177 requires.
* Neutral: the server holds one studio per system opened in a session. Each is small; they are released when the server stops.

## Verification

* `tests/test_play_systems.py`: sketch parsing and line-level refusals, id slugs, template copies, `check_only` writing nothing, a created system served and passing Build & run and Simulate, reopening the system the server started with, refusing an unknown path, a draft saved per system and never applied, malformed drafts refused, the page assets, and `eija new`.
* Manual run in Chromium against `eija serve --systems <tmp>`: create from a sketch, plan two steps, Ctrl+S, reload (the plan is restored and re-checked), and switch back from the recent list.
