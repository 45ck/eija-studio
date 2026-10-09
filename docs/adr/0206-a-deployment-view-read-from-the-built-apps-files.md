# ADR-0206: A deployment view read from the built app's files

* Status: accepted
* Date: 2026-10-09
* Lane: PlayIDE software architecture views (issue #143; follows ADR-0155 and ADR-0203)

## Context and problem statement

PlayIDE had no deployment view. The Components tab showed the app's modules (ADR-0155) and the System lens showed the workflows (ADR-0203), but neither showed where a built workflow runs: which process, which address and port, which database file, or which EIJA package version. An architect's review needs that view. It also needs to state plainly that two workflows sharing `Member` keep two copies of it in two databases.

## Decision drivers

* Nothing hand-written. The deployment must change when the generated files change, as the component diagram does.
* UML notation: nodes drawn as boxes in three dimensions, with «device», «executionEnvironment» and «artifact».
* No new route and no second build. The view is read from the same generated files as the component diagram.

## Considered options

* **Read the deployment from `run.py`, `app/server.py` and the page, next to the component diagram (chosen).**
* **Describe the deployment in the pack.** Rejected. It would be a second source that could disagree with the code (ADR-0093).
* **Show the live process only after Build & run.** Rejected as the only view. The design is reviewable before anything runs. After a build, the live address and verdict are added to the same diagram.

## Decision outcome

Chosen option. `application.deployment.app_deployment(files, kernel)` is pure. It parses `run.py` with `ast` for each option's default and the environment variable that sets it (`--port`, `PORT`, `--data`). It reads the bind address from `app/server.py`, and the routes the page calls and the server serves from `app/web/app.js`. The `sqlite3` connection comes from the import. `POST /api/play/components` returns the report as `deployment`.

The Components tab gains a third lens, **Deployment** (`play-deployment.js`):

* A «device» named *This computer* holds two «executionEnvironment» nodes, *Web browser* and *Python process*. The browser deploys the web page. The process deploys `run.py`, the generated package, the model files and the installed `eija_studio` package.
* The database file is an «artifact» on the device.
* An HTTP communication path is labelled with the routes, and a «use» dependency is labelled `sqlite3`.
* After Build & run, the process shows the running address and the conformance verdict, under the Components tab's evidence rule.
* The other workflows of the system (ADR-0203) are drawn as processes of their own, each with its own database file and nothing between them.

The UML node shape adapts draw.io's `cube` path (Apache-2.0) as a maxGraph `CylinderShape` subclass. maxGraph core ships no node shape.

### Consequences

* Good: the deployment is reviewable before anything runs, and it is always the one the files declare.
* Good: run-time isolation between workflows is visible, which is the honest state until cross-workflow messages exist (#93).
* Bad: this is the local deployment `run.py` declares. A container or cloud deployment is not modelled. It would need a deployment descriptor generated from the model, which is a separate decision.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| maxGraph 0.25 (vendored, Apache-2.0) | Has no UML node shape | A 15-line `CylinderShape` subclass with draw.io's `cube` path (Apache-2.0) |
| C4 deployment diagrams, Structurizr DSL, PlantUML deployment (patterns only) | Each is a hand-written second model of the deployment | Export to Structurizr DSL is the interchange path |
