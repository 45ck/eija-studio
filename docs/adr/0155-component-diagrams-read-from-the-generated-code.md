# ADR-0155: Component diagrams read from the generated code

* Status: accepted
* Date: 2026-10-08
* Lane: PlayIDE (owner direction, 8 October 2026)

## Context and problem statement

The owner's roadmap asks for component diagrams after use cases and screens. A component diagram that someone draws by hand is a claim about the code that nothing checks, so it drifts. PlayIDE's promise is "UML you can trust": each diagram must be the model itself, or be read from what the model produced.

## Decision drivers

* No hand-drawn structure. Every component and dependency must come from the files that are actually built.
* No second source: not a description file kept next to the templates, and not a model of the app's architecture.
* The diagram must change when the generated code changes, and must not show a dependency the code does not have.
* Pure and deterministic, so it can be computed for any model without running anything.

## Considered options

* Read the component diagram from the generated files with `ast` and regular expressions (chosen).
* Hand-write a `components.json` next to the templates. Rejected: nothing would check it against the code.
* pydeps or import-linter's graph (both BSD-2-Clause). They draw Python import graphs of installed packages. They cannot see the browser page's routes, the files a module reads, or the generated app before it is written to disk. They also produce Graphviz, not UML component notation.
* code2flow or pyan (MIT, GPL-2.0). Call graphs, not components. pyan is GPL, so it is reference only.

## Decision outcome

Chosen option: `application/components.py`, `app_components(files)`.

* Components are the generated Python modules (stereotyped «component», «executable» for `run.py`, «test» for the conformance suite). The browser page, `app/web` with `index.html`, `app.js` and `app.css`, is «browser». The EIJA modules the app imports are «kernel». `sqlite3` is «database» and `http.server` is «framework». Generated JSON documents are «artifact».
* Each dependency is evidence in the code:
  * an import statement, labelled with the imported names, with relative imports resolved;
  * a route the page calls that the server serves (`/api/...` in both files);
  * a module that reads a generated file by its quoted name;
  * the server serving the page.
* A provider's interface is the set of names its users import. It is drawn as a lollipop (ball) beside the provider, and each user has a dashed «use» dependency to it. File reads are «read» and serving is «serve».
* Routes the page calls that the server does not serve are listed as `unserved_routes`. Utility imports that are not drawn (json, re, pathlib, ...) are listed as `not_drawn`, so the omission is visible.
* `POST /api/play/components` builds the app's files in memory for the shown model and screens (`app_files`, nothing is written) and returns the diagram. The **Components** tab draws it in columns by depth of use, with UML packages for the installed EIJA package and the generated model files. Selecting a component shows its files, line count, what it provides, uses and is used by. After **Build & run**, the conformance suite shows its score and the server shows that it is running.

### Consequences

* Good: the diagram cannot drift from the code. Tests add and remove an import and a route, and the diagram follows.
* Good: it shows the claim at the heart of the built app: the service asks `execute`, `initialise` and `check_actor` in the EIJA kernel for every decision, so there is no second interpreter.
* Bad: it shows the generated app, whose structure is the same for every model; only the files read, the data model and the screens vary. Component diagrams of the user's own system come later, from repository intake.
* Bad: the layout is a simple column layout, not an optimised one; dense diagrams cross lines.
* Revisit when: component diagrams of connected repositories are wanted (reuse the extraction over captured files), or when models can declare components of their own.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| pydeps | Imports of installed packages only; no browser routes or file reads; Graphviz output, not UML | Use for whole-repository import graphs |
| import-linter graph | Same scope as pydeps; it is already used for layer contracts | — |
| pyan, code2flow | Call graphs, not components; pyan is GPL-2.0 (reference only) | — |
| Python `ast` | Adopted (standard library) | — |
| maxGraph `ellipse`, `cylinder` and `swimlane` shapes | Adopted for interfaces, the database and packages | — |
