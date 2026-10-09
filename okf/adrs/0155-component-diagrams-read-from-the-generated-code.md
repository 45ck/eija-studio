---
type: Architecture Decision Record
title: 'ADR-0155: Component diagrams read from the generated code'
description: The owner's roadmap asks for component diagrams after use cases and screens.
resource: repo://docs/adr/0155-component-diagrams-read-from-the-generated-code.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0155-component-diagrams-read-from-the-generated-code.md
  title: 0155-component-diagrams-read-from-the-generated-code.md
  hash_method: lf-sha256-v1
  sha256: 594e277269aeb2675c7b259987a10970fba77bbe000862d425a3a6ff377a96ba
notes_baseline: 7b8699ea230bb4fb7eb99e33f9ada5f200882895641465ab87bc02b554db4fb7
---

# ADR-0155: Component diagrams read from the generated code

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-08 |
| Lane | PlayIDE (owner direction, 8 October 2026) |
| Source | `repo://docs/adr/0155-component-diagrams-read-from-the-generated-code.md` |

## Decision outcome (verbatim)

> Chosen option: `application/components.py`, `app_components(files)`.
>
> * Components are the generated Python modules (stereotyped «component», «executable» for `run.py`, «test» for the conformance suite). The browser page, `app/web` with `index.html`, `app.js` and `app.css`, is «browser». The EIJA modules the app imports are «kernel». `sqlite3` is «database» and `http.server` is «framework». Generated JSON documents are «artifact».
> * Each dependency is evidence in the code:
>   * an import statement, labelled with the imported names, with relative imports resolved;
>   * a route the page calls that the server serves (`/api/...` in both files);
>   * a module that reads a generated file by its quoted name;
>   * the server serving the page.
> * A provider's interface is the set of names its users import. It is drawn as a lollipop (ball) beside the provider, and each user has a dashed «use» dependency to it. File reads are «read» and serving is «serve».
> * Routes the page calls that the server does not serve are listed as `unserved_routes`. Utility imports that are not drawn (json, re, pathlib, ...) are listed as `not_drawn`, so the omission is visible.
> * `POST /api/play/components` builds the app's files in memory for the shown model and screens (`app_files`, nothing is written) and returns the diagram. The **Components** tab draws it in columns by depth of use, with UML packages for the installed EIJA package and the generated model files. Selecting a component shows its files, line count, what it provides, uses and is used by. After **Build & run**, the conformance suite shows its score and the server shows that it is running, but only while the diagram is of the same model and screens digest the build was made from; any screen edit clears that evidence. File reads and serving are dependencies, not provided interfaces. A package's members share one column, so each package is one box.

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
## Referenced by

* [ADR-0158: A change ripples across every diagram, and the AI's follow-on edits are re-checked](/adrs/0158-ripple-across-diagrams-with-checked-follow-ons.md) - PlayIDE draws five diagrams of one system: the state machine, the class diagram, the use cases, the screens and the components of the built app.
* [ADR-0203: A system landscape of the workflows that share classes](/adrs/0203-system-landscape-of-workflows-that-share-classes.md) - PlayIDE edits one workflow at a time: one state machine moving one record class, with its class diagram, use cases, screens and laws.
* [ADR-0206: A deployment view read from the built app's files](/adrs/0206-a-deployment-view-read-from-the-built-apps-files.md) - PlayIDE had no deployment view.
<!-- okf:generated:end links -->
