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
  sha256: 8debc816621a69db566aeaa1b810b7baa58af1fb6dfc7a1923270857eb502340
notes_baseline: 567a87f46c4dcae4863cd3aa3761b4597f1289ed099ae0c52d6d841e1d62732b
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
> * `POST /api/play/components` builds the app's files in memory for the shown model and screens (`app_files`, nothing is written) and returns the diagram. The **Components** tab draws it in columns by depth of use, with UML packages for the installed EIJA package and the generated model files. Selecting a component shows its files, line count, what it provides, uses and is used by. After **Build & run**, the conformance suite shows its score and the server shows that it is running.

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
_No generated cross-references._
<!-- okf:generated:end links -->
