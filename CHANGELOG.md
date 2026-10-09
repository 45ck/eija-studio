# Change log

## Unreleased

### 9 October 2026: sequence diagrams that read well

- The Sequences tab is legible at laptop and recording size: lifeline names wrap onto two lines, labels are larger, steps are numbered as in the Tests tab, the record shows an activation bar for each call, and effects are UML lost messages instead of a column each. It never scales below 80%.
- When scenarios fail, a panel above the diagram names each one, the failing step and why, with **Show the step** and **Expect what the model does now**.
- A system with no scenarios yet (one started from a sketch) gets scenarios drafted from the model, so the tab is never empty. See [ADR-0195](docs/adr/0195-sequence-diagrams-the-kernel-checks.md).

### 9 October 2026: PlayIDE keeps the diagram readable with Simulate open, and a drawn transition can name a new action

- Opening Simulate no longer shrinks the state machine until its labels are about 7 pixels high (#139). When the canvas is short, fitting stops at a readable size and starts at the top left, where the initial state is, and the rest is a drag away. The **Fit** button still fits the whole diagram, however small. Before, Library loan went to about half size at 1280 by 800 with the panel open.
- On a system you started yourself, a transition drawn on the canvas can name a new action or role: type it, and the editor says "New action: the step declares" it. Before, the editor offered only actions the model already had, so a new action needed the chat ([ADR-0201](docs/adr/0201-build-a-new-system-in-chat-round-after-round.md)). Template and sample models still offer only their own actions.

### 9 October 2026: PlayIDE polish, round 8 (tabs and screen fields on a laptop)

- A diagram tab is never shown cut off at the edge of the tab strip. At 1280 pixels the strip ended on "Use" or "Scre", which reads as another tab; a tab the edge would cut now leaves a gap, and More tabs (») still lists every tab (#141).
- On the Screens tab, a field shows its whole label ("Member card", not "Member c"), and its type and whether it is required sit on the line beneath, taking two lines at most rather than four (#140).

### 9 October 2026: AI agents, timers and external systems in the model

- A role can now be held by a person (the default), an AI agent, a timer or an external system. The use case diagram draws a person as a stick figure and the others as «agent», «timer» and «system» actor boxes ([ADR-0210](docs/adr/0210-actors-that-are-not-people.md)).
- Three new laws are about the kind of actor rather than one role: only a person takes an action, only a person moves a record into a state, and a person acted on every record before it reached a state. They hold for agent roles added later, and a role nobody declared never counts as a person. The policy, the law proof and the generated SMT check judge them.
- A new example pack, **Refund desk**: an AI agent triages and proposes refunds, a timer escalates, the payment system confirms or fails a payout, and only a supervisor on shift approves. Ask the chat to `allow SupportAgent to ApproveRefund` and the plan is refused, naming the three laws.
- **Simulate** reports what the people, agents, timers and external systems each tried and what the kernel answered. How to model them: [Model AI agents, timers and external systems](docs/modelling-agents.md).

### 9 October 2026: PlayIDE polish, round 7 (readable on a laptop)

- The state machine is laid out top to bottom when that draws it clearly larger, as on a laptop with the side bar and the chat open. Before, Library loan was shrunk to a third of its size in one long row, with 5-pixel labels; at 1280 pixels it is now drawn at full size. The direction is chosen once, when the diagram is first drawn, so an edit or a preview never turns it. The Changes view follows the same direction.
- On a 1280-pixel laptop screen, an edit no longer scrolls the whole page sideways. "Unsaved changes" in the title bar had made the page 42 pixels wider than the window; the title bar now gives way inside the window instead.
- A state dragged near the edge of the state machine stays where you let go. maxGraph used to slide the view to show all of it, so it settled a few pixels away from the pointer.

### 9 October 2026: PlayIDE puts shapes where you put them

- A state you place on the state machine now lands exactly where you click or drop it, at any zoom. A dashed outline shows where before you commit, and a transition shows a line from the state it leaves to the pointer. Nothing else on the diagram moves when the plan redraws, and a state you drag stays where you let go. Before, every step laid the diagram out again, and the plan banner pushed it down. Shapes dragged on the class, use case and component diagrams stay put too, and pressing on a class's attribute row takes hold of the class. **Tidy** (beside Fit, and in Ctrl+K) lays the diagrams out again. On the Screens tab, a line shows where a dragged field will go. See the amendment to [ADR-0174](docs/adr/0174-add-without-dragging-and-edit-inline.md).

### 9 October 2026: PlayIDE polish, round 6 (the Import / Export menu)

- The Import / Export menu wraps its longer lines again. Since round 3 kept the title bar's buttons on one line, the menu inherited that, and the XMI line ("Enterprise Architect, Cameo, …, StarUML") ran past the menu's edge into the chat panel.

### 9 October 2026: PlayIDE polish, round 5 (the command palette)

- Ctrl+K now reaches Undo, Redo, Save the work on this system, and Open another system or start a new one. Before, those were only on the title bar. In the review view (`/play?view=review`) the palette offers none of the commands that change the model.

### 9 October 2026: PlayIDE polish, round 4 (your own systems)

- On a system you started in PlayIDE, the chat's example is a typed step the chat reads ("add state Archived after Escalated"). Before, it offered the system's demo request, which a new system does not model, so sending the example as shown was refused. `/api/status` says whether the demo request passes as it stands (`demo_modelled`); only an offline proposer is asked, so a live one is never called on page load.
- The Laws tab on a system with no laws says so, instead of "Every law in force holds… ." with a stray full stop.
- The Laws and Tests tabs name the system's own files (`~/PlayIDE/support-desk/pack.json`), not `packs/support-desk/…`, which does not exist. Shipped packs still read `packs/library-loan/…`.

### 8 October 2026: sequence diagrams

- PlayIDE has a **Sequences** tab: the pack's scenarios (the Tests tab's `scenarios.json`) drawn in UML sequence notation (lifelines, calls, refusal replies, state invariants, effects as asynchronous messages, and a `neg` fragment around each step that must be refused), each step run through the kernel. A step the model can't do is flagged with the kernel's reason. Edit in the tab (the same draft the Tests tab shows), export as Mermaid or PlantUML, or download `scenarios.json`. A plan's ripple lists the scenarios it breaks. New route `POST /api/play/sequences`. See [ADR-0195](docs/adr/0195-sequence-diagrams-the-kernel-checks.md).

### 9 October 2026: your own systems, two fixes

- The Systems dialog opens again after you close it. Before, a second open did nothing until the page was reloaded.
- A sketch whose roles differ only in punctuation (`A_B` and `A__B`) now gets one user per role instead of being refused for duplicate user ids.
- A sketch whose states, actions or roles differ only in case (`Agent` and `agent`) is refused with a line saying so: chat matches names ignoring case, so one of them could never be named there.

### 8 October 2026: PlayIDE polish, round 3

- The Tests tab's **Run all** is no longer cut off at the right edge on a laptop screen: when the header's text and buttons do not fit side by side, the buttons go under the text, on the Laws tab too.
- Starting or pausing a run no longer shifts **Simulate** and **Build & run** to the right: the run status has a fixed width, with the full text in its tooltip, and the Run button keeps room for "Continue".
- Simulation findings say "refused once" and "refused 12 times", not "time(s)".
- The review view's title bar keeps **Import / Export** and **Review workbench** on one line, and the layout toggles side by side, beside the read-only badge.

### 8 October 2026: your own systems in PlayIDE

- PlayIDE is no longer limited to the shipped packs. **Systems** in the title bar opens a dialog: **Open** lists recent systems and the ones in your systems home, and **New system** starts one from a sketch or from a template. A sketch is the state machine typed as the diagram labels it, one `From -> To : Action [Role]` per line, and the kernel's pack check runs as you type. **Save** (Ctrl+S) keeps your plan and edited screens as a draft on that system; reopening it restores them and checks every step again. Nothing is applied to the model. Systems live in `~/PlayIDE` (`--systems` or `EIJA_SYSTEMS` to change it), each with its own workspace. `eija new` does the same from the command line. See [ADR-0185](docs/adr/0185-start-open-and-save-your-own-system.md).

### 8 October 2026: PlayIDE polish

- A plan the policy refuses now says which laws it would break, in the pack's own words ("Only a librarian checks a loan out."), with the policy codes after them.
- On the Permissions tab, "Can a record reach this state at all?" shows Yes as a good answer and No as a bad one. The red Yes is kept for "without this role" questions, where it means the role can be bypassed.
- With nothing to review, the Review tab's message spans the tab instead of sitting beside an empty column, and it points to the review workbench rather than a URL parameter.
- The screen designer fits a laptop screen with the side bar and the chat open: the record attributes move under the screen instead of squeezing it until its fields spilled over them.
- Step counts read "1 step" rather than "1 step(s)", and PlayIDE has a tab icon (the page had asked for a missing favicon).
- The status bar names the selection as the outline does ("transition CheckOut", not its id), and the inspector labels a transition's states "Path".

### 8 October 2026: PlayIDE adds without dragging

- Adding to the state machine no longer needs a drag (ADR-0174). Pick State, Transition or Initial in the palette and click the diagram, as in draw.io and Visio; a transition is two clicks, the state it leaves and the state it goes to. Double-click empty space for a new state, a state to rename it, or a transition to change who may take it. A small editor opens where you click: Enter adds the step to the plan, Escape drops it, and nothing is modal. Dragging still works and drops into the same editor; Enter on a palette item still opens the full form. The tour and ripple demos place their state this way.

### 8 October 2026: PlayIDE end-to-end fixes

Found by using every PlayIDE feature together on the workbench shell, as a UML-literate engineer would:

- The chat's example request now works when sent as it stands. On the model in force it is the pack's demo request (for example "Let teachers sign off excursions."), which becomes the change the pack models. Before, the example on Library loan reused an action that already had a transition and was refused. The chat's plan proposer now reads the pack's proposal rules the way the review workbench's offline provider does, so "loans" and "excursions" match the rules' "loan" and "excursion".
- When a run pauses, the Run panel keeps who tried what and the kernel's answer in view. The step log and the simulation log scroll on their own instead of scrolling the whole panel.
- Roles in the outline are buttons that open the Permissions tab, like the other outline entries. The outline grows to fit before the inspector takes the rest.
- The plan banner hides "Review the change" while the Review tab is open, and the Laws tab's "Prove again" button no longer wraps.
- The Run and Simulation panels use their width as intended: when paused, records and breakpoints sit beside the steps so far, and the simulation's "Worth a look" sits beside its run log. A more specific panel rule had kept them in one column.
- Plan steps name a transition by its action, as the diagram does ("Let Member take CheckOut", not "TR-CHECKOUT").
- Choosing a class in the outline clears a stale selection on the state machine, and the other way round.

### 8 October 2026: PlayIDE tabs that do not fit

- When the diagram tabs do not fit, the strip scrolls, the edge that hides tabs fades, and a **More tabs** button lists every tab, as in VS Code. Buttons beside the strip no longer cover a tab label. Hiding the left side no longer pushes the diagrams into its empty column.

### 8 October 2026: PlayIDE's workbench shell

- PlayIDE is laid out like Visual Studio, VS Code, Cursor and draw.io (ADR-0173). The model outline sits above the inspector on the left, the diagrams are editor tabs, and the UML palette is a column beside the canvas. The chat is alone on the right. Run, Simulation and Running app share a resizable panel under the diagrams that opens on whatever has just run. The checks list is a popover from the ring, a status bar runs along the bottom, and the title bar has a command center (Ctrl+K). Ctrl+B, Ctrl+Alt+P and Ctrl+Alt+C hide the side bar, the panel and the chat, and the layout is remembered in the browser.

### 8 October 2026: the review view

- `/play?view=review` is a read-only view of PlayIDE for someone who reviews the model: the same UML diagrams, Permissions, Simulate, the run bar and the running app, with the drawing palette, the chat and every edit tool out of view. Approval stays owner-only in the review workbench. See [ADR-0172](docs/adr/0172-review-view-for-reading-the-model.md).

### 8 October 2026: who can do what

- PlayIDE has a **Permissions** tab: a role by state matrix of who may take which action, each cell tried in the kernel with the pack's fixture actors (who is let through, and why the others are refused). Ask "can a record reach Overdue without a Clerk?" and get a proof (No), a path the kernel committed (Yes) or Not shown. On a previewed plan the same question is asked again and the permissions the plan adds or removes are flagged. See [ADR-0171](docs/adr/0171-permissions-matrix-and-reachability-questions.md).

### 8 October 2026: ripple across the diagrams

- A change to PlayIDE's state machine now shows its effect on every other diagram: the class diagram (the record's state enumeration), use cases, screens, components and the number of conformance cases. Each tab gets a badge, and the affected elements are marked. For each warning or problem, such as an unreachable state or a screen stranded by a removed action, the AI proposes a follow-on edit, and the server checks it again before you can add it. The checks ring has a fifth part, "Diagrams agree". New route `POST /api/play/ripple`. See [ADR-0158](docs/adr/0158-ripple-across-diagrams-with-checked-follow-ons.md).
- New recorded demo `playide_ripple` (PASS, 2:07), see [the write-up](docs/demos/2026-10-08-PLAYIDE-RIPPLE.md). The PlayIDE tour was re-recorded with the five-part ring (PASS, 2:40).

### 8 October 2026: PlayIDE assist (UI, HCI and agentic HCI)

- PlayIDE's chat says who does what (the AI proposes, you check, the owner approves), offers the requests it can read as buttons, about the selected state or transition with its name filled in, and completes exact model names as you type. Ctrl+K (⌘K) opens a palette of every command and element, and an AI plan can be reviewed from the keyboard (J/K, S, Space, P). The reasoning is in [PlayIDE: UML, HCI and agentic HCI](docs/hci/design/playide-ahci.md). See [ADR-0170](docs/adr/0170-playide-assist-ask-complete-palette-review.md).

### 8 October 2026: PlayIDE tour recording

- New scripted demo `playide_tour`, recorded (PASS, 2:38): diagrams, screens, Build & run, components, Simulate, drawing with the palette, and checking an offline AI proposal. See [the write-up](docs/demos/2026-10-08-PLAYIDE-TOUR.md).

### 8 October 2026: drawing and the checks ring

- PlayIDE's state machine has a drag-and-drop UML palette (State, Transition, Initial), and selected elements can be renamed, moved, given another role or removed. Drawn changes join the plan as your steps and are previewed through the same server check as the AI's. A checks ring in the header shows four real checks on the model being shown, and points reward checking AI steps, never making changes. See [ADR-0157](docs/adr/0157-drawn-edits-and-checks-ring.md).

### 8 October 2026: chat plan mode

- PlayIDE has a chat in plan mode. It proposes a change as numbered typed steps; you accept or reject each, and preview the result on every diagram, with Build & run and Simulate on the candidate. The policy checks the accepted steps like an owner's edit, and nothing is saved from the chat. The default proposer is an offline phrase reader (`offline-plan-fixture-v1`), not an AI. See [ADR-0156](docs/adr/0156-chat-plan-mode-proposes-typed-steps.md).

### 8 October 2026: component diagrams

- PlayIDE has a **Components** tab: the UML component diagram of the app the model builds, read from its generated files. Components are the app's modules, the EIJA kernel modules they import, SQLite, the browser page and the generated files. Every dependency is an import, a route or a file read in the code, and each interface lists the names its users import. After Build & run, the conformance score and the running server show on the diagram. See [ADR-0155](docs/adr/0155-component-diagrams-read-from-the-generated-code.md).

### 8 October 2026: use cases and the screen designer

- PlayIDE has a **Use cases** tab that draws the workflow as a UML use case diagram: actors per role, a use case per action plus creating a record, inside the system boundary. Double-click a use case to design its screen.
- The **Screens** tab designs one screen per use case against the record class: drag attributes onto it, reorder them, rename labels, title and button. A design check (`check_screens`) runs on every edit, and no app is built from screens it rejects, for example a create screen that leaves out a required attribute. **Build & run** builds the app with the designed screens, and its form and buttons follow them. Packs can keep screens in `screens.json` beside `pack.json`; library-loan has one. See [ADR-0154](docs/adr/0154-use-cases-and-screens-designed-against-the-model.md).

### 8 October 2026: class diagrams for data

- Packs can have a data model, `data.json` beside `pack.json`, with classes, typed attributes, associations and a «record» class. PlayIDE shows it as a UML class diagram. Built apps get a form from the record class, and every value is checked by `check_values` on the server. The conformance oracle gains data cases, and two new broken apps are caught. The excursion and library-loan packs have data models; pack digests are unchanged. See [ADR-0153](docs/adr/0153-data-models-as-uml-class-diagrams.md).

### 8 October 2026: PlayIDE Simulate

- PlayIDE's **Simulate** runs 500 seeded actions by the pack's fixture actors through the kernel and paints the result on the diagram: commits as line width, never-used transitions dashed, records per state as fill. It lists findings (never succeeded, never reached, stuck, most refused) and a run log you can replay. The same seed replays exactly. See [ADR-0152](docs/adr/0152-simulate-seeded-users-through-the-kernel.md).

### 8 October 2026: PlayIDE canvas and Build & run

- New PlayIDE page at `/play` (its private link is printed by `eija serve`). It draws the model as a UML state machine on maxGraph 0.25.0 (Apache-2.0, vendored), with an outline and inspector. **Build & run** builds the app with `eija build`, shows the kernel conformance score and starts the app beside the diagram only if it passes. See [PlayIDE](docs/playide.md) and [ADR-0151](docs/adr/0151-playide-canvas-and-build-and-run.md).

### 8 October 2026: build an app from the model

- New `eija build --pack P --out DIR`. It writes a runnable app (web page, API and SQLite database) from the workflow model, plus `tests/oracle.json` with the kernel's answer for every state, action, actor and version. It runs the app's conformance tests and records the result in `BUILD.json`, and exits 2 if they fail. All three packs pass: excursion 240 cases, library-loan and eija-review-slice 360 each. The app stores records in SQLite and calls the kernel for every decision, so there is no second interpreter. Five broken apps (storage and built-in model mutants) are each caught, and the `appgen` nox session builds all three packs. See [Build an app from the model](docs/build-an-app.md) and [ADR-0150](docs/adr/0150-build-apps-from-the-model-with-a-kernel-oracle.md).

### 8 October 2026: the source-connected IDE on main (#78)

- The IDE from `integrate/all` (#29) and #76 is merged onto `main`. Run it with `eija serve --pack packs/eija-review-slice --repo . --open`. The lane PRs it contained (#12, #14, #16, #22, #23, #24, #25) are recorded as merged. See the [IDE-on-main record](docs/engineering/2026-10-08-IDE-ON-MAIN.md).
- Canvas drag handles sit on the line's ends and no longer cover the selected transition's label. Inspector Change buttons sit beside their selects.
- Linux gate fixes: the vocabulary gate skips gitignored `*.egg-info`, and npm shim paths are separator-normalised.
- New demo scenario `ide_walkthrough`, recorded PARTIAL, with the [walkthrough record](docs/demos/2026-10-08-IDE-WALKTHROUGH.md). The demo harness can connect a repository and pick a pack, and keeps captions visible over modal dialogs.
- Still open: HCI budget re-derivation ([#79](https://github.com/45ck/eija-studio/issues/79)) and owner source review and restamp ([#80](https://github.com/45ck/eija-studio/issues/80)). Until #80 is done, verify returns `SOURCE_REVIEW_REQUIRED`, and approve and apply are blocked by source review (`GATE_BLOCKED`).

Summary of the open-source foundation since 0.2.0. Nothing here changes kernel behaviour except where stated.

### Added

- Apache-2.0 licence, NOTICE, [ADR](docs/adr/README.md) index in MADR format (ADR-0015 to ADR-0020), OSS-first register ([docs/oss/REGISTER.md](docs/oss/REGISTER.md)), lane conventions in `AGENTS.md`, and nox gate sessions loaded as plugins from `quality/sessions/` (PR #2).
- Durable and ephemeral SQLite profiles, an application-owned `SandboxFactory` port, and a fast Windows test suite (PR #1). This is a kernel change: it means the source no longer matches the owner-stamped release fixture, so `eija doctor` reports `release_fixture_matches: false` and verify/apply return `SOURCE_REVIEW_REQUIRED` until the maintainer re-stamps.
- Front-door documentation (oss lane): README rewrite with a before/after state diagram generated from `domain.policy`, `docs/getting-started.md` (the previous README's install, provider and verification detail), CONTRIBUTING, CODE_OF_CONDUCT (Contributor Covenant 2.1), SECURITY, CITATION.cff, issue and pull-request templates, `docs/ROADMAP.md`, lane hub pages, a banner, ADR-0043.
- MkDocs Material configuration (`mkdocs.yml`, extra `docs`), and nox sessions `docs_links`, `readme_diagram`, `community_files` (fast and full), `docs` and `pr_status` (release; both `NOT_RUN` when their prerequisite is absent). `community_files` is skipped, never green, when PyYAML is missing. No deployment: hosted CI is unavailable.

### Changed

- The README is now the project's front door. Installation, OpenRouter, Codex, first-demonstration, compiler and operations detail moved to `docs/getting-started.md` without removal.

### Not added

Everything not on `main` in the [roadmap](docs/ROADMAP.md): formal V&V beyond the Bend laws (TLA+, Z3), property and mutation testing, metrics, HCI instrumentation, MCP server, knowledge base. Providers, visual, agents, HCI, metrics, Z3 and OKF work exists on open pull requests and is not part of this entry; the quality gates (lint, typing, architecture, complexity, coverage, dependencies), the demo harness and the Bend laws are already on `main`. See the [roadmap](docs/ROADMAP.md).

## 0.2.0 — 2026-09-27

First runnable unified local implementation, following the v0.1 consolidation specification.

Added browser Studio, CLI/semantic compiler, typed domain contracts, explicit semantic transactions, SQLite unit of work, current-authority checks before replay, transactional audit/outbox, subject-bound local evidence and review/apply, derived rule/state/journey views, fixed-point mapped impact, source-fixture checks, offline/OpenRouter/Codex proposal adapters, mock provider tests, regression/crash/concurrency tests, HTTP/browser-component/wheel smoke tests, source contracts, engineering review and agent handoff.

Additional review hardened receipt coverage (empty/missing/duplicated cells, false boolean types, invalid subject/state), provider accounting-envelope rejection and Codex output decoding. An early test mutated an already-true value to true; that test assertion was corrected to actually mutate the value, then the complete suite was rerun. Historical intermediate reports are not presented as current release evidence.

Not added: arbitrary-repository compiler, independent formal proofs, live credential-tested providers, institutional SSO, production effects, multi-tenant isolation, drag-and-drop diagram canvas, MCP server, independent hidden evaluation or measured human benefit. Ordinary browser-network testing was blocked by the environment; separate real TCP and Chromium component tests passed.
