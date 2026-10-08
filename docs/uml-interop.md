# UML import and export

PlayIDE reads and writes the UML formats engineers already use, so a model can go into Enterprise Architect, a README or a draw.io page, and an existing diagram can come in as a change you check. The design is [ADR-0190](adr/0190-uml-import-and-export-through-the-kernel.md).

| Format | Export | Import | Opens in |
|---|---|---|---|
| XMI (UML 2.5.1) | state machine, class model, use cases | state machine, class model | Enterprise Architect, Cameo/MagicDraw, Papyrus, Visual Paradigm, StarUML, Modelio |
| PlantUML (`.puml`) | state machine, class model, use cases | state machine, class model | PlantUML, IDE plugins, wikis |
| Mermaid (`.md`) | state machine, class model | state machine, class model | GitHub, GitLab, most Markdown viewers |
| draw.io (`.drawio`) | state machine, class model, use cases (one page each) | state machine, class model | diagrams.net, Confluence, the VS Code extension |

Every pack's exports are committed in [`verification/interop/generated/`](https://github.com/45ck/eija-studio/tree/main/verification/interop/generated), so you can open one without installing anything.

## In PlayIDE

**Import / Export** in the title bar, or Ctrl+K and type "export" or "import".

- **Export** downloads the model on screen. While a plan is previewed, that is the model with the plan. A status line lists what no UML file carries.
- **Import a UML file** shows a report. Its verdict is one of:
  - **Clean:** everything was read and the kernel accepts the result.
  - **Partial:** something could not be imported; each item is listed with where it was and why.
  - **Refused:** the policy or the laws reject the model as it stands, with the codes.

  **Preview as a plan** turns the state machine's differences into the plan, as your own steps. From there everything works as for drawn edits: tick or untick steps, preview, see the ripple and the Changes view, Build & run, Simulate and Review. Nothing is saved. A class model change is shown and can be downloaded as `data.json`.

## On the command line

```console
eija uml export --format xmi --pack packs/library-loan --out loan.xmi
eija uml import edited.puml --pack packs/library-loan --out-dir candidate/
eija laws --pack packs/library-loan --workflow candidate/workflow.json
```

`uml import` prints the JSON report and exits 0 only when it is CLEAN. `--out-dir` writes the candidate `workflow.json` and `data.json`, which the other commands accept. Neither command changes the pack.

## How PlayIDE writes UML

- A transition label is `trigger [guard] / effects`: `CheckOut [role = Librarian and assigned] / Audit:LoanCheckedOut, Notification:MemberNotified`. The trigger is the action, the guard names the role, and `assigned` appears when the action needs an assigned actor.
- Attribute types are `String`, `Real`, `Boolean`, `Date`, or an enumeration for a choice (named after its class and attribute, such as `LoanFormat`). `[1]` is required and `[0..1]` optional. A text attribute carries `{maxLength = n}`.
- The class whose instances move through the state machine is `«record»`. In XMI it owns the state machine as its classifier behaviour.
- Associations keep their kind (composition, aggregation or plain), both multiplicities and the target's role name.
- Final states are drawn after every state no transition leaves, and the use case diagram has one actor per role and one use case per action.

## What an import does

The file never replaces the model. The state machine is compared with the model in force, and the difference becomes the same typed edits a drawn change uses: add a state, set the initial state, add a transition, move an end, change the role, remove a transition or a state. Transitions are matched by action. The kernel applies each edit with the pack's own guards and effects, so a file cannot choose them, and then judges the result with the policy and the laws.

These are reported, never guessed:

| In the file | What happens |
|---|---|
| an action the pack does not declare | not imported: declare its guards and effects in the pack first |
| a role the pack does not declare, or no role | not imported (an action already in the model keeps its role) |
| guards or effects that differ from the pack's declaration | the pack's are kept, and the report says so |
| a guard term other than the role and `assigned` (such as `fine > 0`) | not imported; value guards are planned (issue #93) |
| composite states, choice, fork, join or history pseudostates, orthogonal regions | not imported; composite states are planned (issue #93) |
| operations, inheritance, interfaces, collection-valued or class-typed attributes | not imported: they are not in the data vocabulary |
| `Integer`, `DateTime` | read as `Real` and `Date`, and listed |
| a text attribute without a maximum length | 200, and listed |
| use case diagrams and final states | derived, so redrawn from the imported model |

XML with a DTD or entities is refused before it is parsed, and so is a compressed draw.io page that holds one. A compressed page may inflate to at most 8 MB.

## How it is checked

- `nox -s interop_roundtrip`: every pack's export, in every format, imports back clean, with no edits and the identical class model, and the committed exports are current.
- `nox -s interop_mermaid`: Mermaid's own parser, the bundle PlayIDE already ships, reads every Mermaid export in Chromium and must agree with PlayIDE's reader, and three deliberately broken exports must be caught. Set `EIJA_CHROMIUM` to a Chromium if Chrome is not installed.
- `nox -s interop_plantuml`: PlantUML itself (the pinned MIT build, on Java) checks the syntax and must read every PlantUML export as PlayIDE does, and three deliberately broken exports must be caught. Download the jar first:

  ```console
  curl -o .tmp/tools/plantuml-mit-1.2026.8.jar https://repo1.maven.org/maven2/net/sourceforge/plantuml/plantuml-mit/1.2026.8/plantuml-mit-1.2026.8.jar
  ```

Without Chromium, Java or the jar these two report NOT_RUN. XMI has no independent checker yet; a headless Eclipse UML2 or Papyrus import is the planned one.

## Limits

- An import that needs more than 12 edits cannot be previewed as one plan. `eija uml import` gives the whole candidate.
- draw.io import reads draw.io's UML palette shapes and the one-cell class box. Other shapes are listed one by one as not imported.
- Creating a new system from an imported file belongs to the new-system flow.
