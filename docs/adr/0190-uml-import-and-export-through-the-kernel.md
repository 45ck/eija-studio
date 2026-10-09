# ADR-0190: UML import and export: XMI, PlantUML, Mermaid and draw.io, with every import judged by the kernel

* Status: accepted for state machines and class models
* Date: 2026-10-08
* Lane: PlayIDE (owner direction, 8 October 2026: "what else, spawn threads")

## Context and problem statement

PlayIDE's users already know UML and already keep UML somewhere else: XMI in Enterprise Architect, Cameo, Papyrus or Visual Paradigm; PlantUML beside the code; Mermaid in a README; draw.io in Confluence. A model that cannot leave PlayIDE, or a team's existing diagrams that cannot come in, makes PlayIDE an island. The owner asked for PlayIDE to fit into the work UML engineers already do.

Two things make interchange harder here than in a drawing tool:

* A PlayIDE model is executable. A file must not be able to choose what an action does (its guards and effects) or slip past a law.
* A UML file can say far more than PlayIDE's closed vocabulary (composite states, value guards, operations, inheritance), and far less (no roles, no effects). Silently dropping the difference would make an import look faithful when it is not.

## Decision drivers

* Export is faithful: every UML element of the model is in the file, and reads back as exactly the same model.
* Import never replaces the model. It goes through the same typed edits and the same kernel checks as a drawn edit or an AI plan.
* Nothing is dropped silently. Every element of an imported file is reported as read, kept or filled in, derived, or not imported, with the reason.
* Open source first ([ADR-0016](0016-oss-first-adapters-not-engines.md)), and evidence from tools other than our own reader.
* Domain and application stay free of vendors and network (`urllib` and `subprocess` are forbidden there).

## Order of the formats

Value to UML engineers against how much a reader can be trusted:

| Order | Format | Why |
|---|---|---|
| 1 | **PlantUML** | The most common text UML in engineering repos and wikis; text round-trips exactly; PlantUML itself can check our reading. |
| 2 | **XMI (UML 2.5.1)** | The real interchange standard: the only way into and out of EA, Cameo, Papyrus, Visual Paradigm, StarUML and Modelio. More work, highest reach. |
| 3 | **Mermaid** | Renders in GitHub and GitLab with no tool at all; Mermaid's own parser can check our reading. |
| 4 | **draw.io** | Where teams sketch. Export is easy; import is the least certain because a drawing says what a shape looks like, not what it is. |

All four ship together because they share one picture of the model and one import path; only the readers and writers differ.

## Considered options

* **One shared UML picture, four thin readers and writers, and import as typed edits judged by the kernel** (chosen).
* **Adopt an EMF stack** ([pyecore](https://github.com/pyecore/pyecore), BSD-3, with an Eclipse UML2 metamodel). It reads Eclipse UML2's own namespace, not the OMG XMI that EA and Cameo write, and adds a metamodel runtime for the few elements PlayIDE has. Reference only.
* **Write the imported file straight into the pack.** Rejected: a file would choose guards and effects and skip the laws. Saving is also the job of the new-system flow ("Start your own system").
* **Render PlantUML through a server** (`plantuml` on PyPI). Needs the network. Rejected for the product; PlantUML runs locally only as a verification tool.

## Decision

* `application/interop/` holds the shared picture (`model.py`), the import mapping (`mapping.py`) and one module per format. Stdlib only: `xml.etree` for XMI and draw.io, `zlib` and `base64` for compressed draw.io pages.
* **Labels.** A transition is written the UML way, `trigger [guard] / effects`: `CheckOut [role = Librarian and assigned] / Audit:LoanCheckedOut, Notification:MemberNotified`. The trigger is the action, the guard names the role and, when the action needs it, an assigned actor.
* **Types.** `text`, `number`, `boolean` and `date` are `String`, `Real`, `Boolean` and `Date`; a choice is an enumeration named after its class and attribute. Required is `[1]`, optional `[0..1]`. A text attribute's maximum length is `{maxLength = n}` (an OCL constraint `name.size() <= n` in XMI). The record class is `«record»` (in XMI, the class whose `classifierBehavior` is the state machine).
* **Export** writes the state machine, the class model and the use case diagram, and lists what no UML file carries (laws, meanings, the effect catalog's kinds and recipients, fixtures). Mermaid has no use case diagram and no notes on attributes, and says so.
* **Import** compares the file's state machine with the model in force and turns the difference into typed semantic transactions (`add_state`, `set_initial`, `add_transition`, `retarget_transition`, `set_role`, `remove_transition`, `remove_state`). The kernel applies each one with the pack's declared guards and effects; a refused edit is reported and the rest are still tried. The result is judged by the protected policy, then the laws. The class model is validated as a `data.json`. Transitions are matched by action, because an action is one transition in a PlayIDE model.
* **What the file cannot say in PlayIDE's vocabulary is reported.** An undeclared action or role, a guard term other than the role and assigned, a composite state, a pseudostate other than the initial one, an orthogonal region, an operation, inheritance, a collection-valued attribute and a class-typed attribute are not imported, each with a reason. A guard or effect list that differs from the pack's declaration is kept as the pack's, and says so. Use case diagrams and final states are derived, so they are listed as derived and not read back.
* **Safety.** XML with a DTD or entities is refused before parsing, and files are capped (2 million characters; XMI and draw.io 8 MB). A compressed draw.io page is inflated with the same 8 MB bound and gets the same DTD refusal, so a small file cannot expand into a large or entity-laden page. A second arrow from the initial pseudostate is reported, never dropped.
* **In PlayIDE**, an Import / Export menu in the title bar exports the model on screen (a previewed plan included) and imports a file into a report. The import's edits become the plan, as the person's own steps, so they are checked, previewed, rippled and reviewed like drawn edits. Nothing is saved. A class model change is shown, and can be downloaded as `data.json`.
* **On the command line**, `eija uml export --format F` and `eija uml import FILE [--out-dir DIR]`. The import exits 0 only when the report is CLEAN.

## Evidence

* `interop_roundtrip` (fast): the committed exports in `verification/interop/generated/` are current, and every pack's export in every format imports back CLEAN, with no edits and the identical class model.
* `interop_mermaid` (full): Mermaid 12.0.0, the bundle PlayIDE already vendors, parses every Mermaid export in Chromium. Its diagram database (states, transitions with labels, classes, members, annotations, associations, notes) must equal PlayIDE's reading. Three negative controls (an unescaped `;` in a label, braces in a member line, a quote in a note) must be caught.
* `interop_plantuml` (full): PlantUML 1.2026.8 (the MIT build, pinned by sha256, run on Java) checks the syntax and writes its own XMI of each export; its states, labelled transitions, classes, stereotypes, attribute lines and associations must equal PlayIDE's reading. Three negative controls must be caught.
* Without Chromium, Java or the jar these report NOT_RUN and skip; they never pass.

## Consequences

* A PlayIDE model can be opened in any UML tool and in GitHub, and an existing diagram can be brought in as a checked plan.
* XMI has no independent checker in this lane yet. A headless Eclipse UML2 or Papyrus import is the planned check; until then XMI is covered by the round trip and by tests with tool-written XMI 2.1 shapes.
* draw.io import reads draw.io's UML palette shapes and the one-cell HTML class box. Other drawings are reported shape by shape.
* A partly read state machine removes nothing (issue #165). A transition renamed to an undeclared action is not read, so removing the old one would offer a plan that breaks the model; the import lists each removal it withheld, and the page says the plan is only what was read.
* An import larger than one plan (12 steps) is shown but cannot be previewed in one go; `eija uml import` gives the whole candidate.
* A new system can start from a UML file (added after the new-system flow of [ADR-0185](0185-start-open-and-save-your-own-system.md) landed). With no model in force to compare with, the file's state machine is written as a sketch, so its actions and roles become the pack's declarations, and its `assigned` guards and `Audit:`/`Notification:` effects are declared per action. The class model becomes `data.json`. The kernel's pack check and protected policy judge the result before it is created, and the form shows the same report as an import. Every shipped pack's export starts a system with the same state machine, guards, effects and class model (`tests/test_uml_new_system.py`).
* Composite states, value guards and the other operators in issue #93 will move from "not imported" to "read" as the kernel gains them; each needs a row in the mapping and a round-trip case.
