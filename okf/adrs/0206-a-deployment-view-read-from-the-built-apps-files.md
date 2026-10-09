---
type: Architecture Decision Record
title: 'ADR-0206: A deployment view read from the built app''s files'
description: PlayIDE had no deployment view.
resource: repo://docs/adr/0206-a-deployment-view-read-from-the-built-apps-files.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0206-a-deployment-view-read-from-the-built-apps-files.md
  title: 0206-a-deployment-view-read-from-the-built-apps-files.md
  hash_method: lf-sha256-v1
  sha256: 94be33fcab1316bdd178239fe06988d08cb6b81c0f223698967ca04f64ca8eca
notes_baseline: 5bb0e715bf88cb7bc16cb0e13deef1b08aaf7e10dfcf25ae3f613b33bd92f851
---

# ADR-0206: A deployment view read from the built app's files

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-09 |
| Lane | PlayIDE software architecture views (issue #143; follows ADR-0155 and ADR-0203) |
| Source | `repo://docs/adr/0206-a-deployment-view-read-from-the-built-apps-files.md` |

## Decision outcome (verbatim)

> Chosen option. `application.deployment.app_deployment(files, kernel)` is pure. It parses `run.py` with `ast` for each option's default and the environment variable that sets it (`--port`, `PORT`, `--data`). It reads the bind address from `app/server.py`, and the routes the page calls and the server serves from `app/web/app.js`. The `sqlite3` connection comes from the import. `POST /api/play/components` returns the report as `deployment`.
>
> The Components tab gains a third lens, **Deployment** (`play-deployment.js`):
>
> * A «device» named *This computer* holds two «executionEnvironment» nodes, *Web browser* and *Python process*. The browser deploys the web page. The process deploys `run.py`, the generated package, the model files and the installed `eija_studio` package.
> * The database file is an «artifact» on the device.
> * An HTTP communication path is labelled with the routes, and a «use» dependency is labelled `sqlite3`.
> * After Build & run, the process shows the running address and the conformance verdict, under the Components tab's evidence rule.
> * The other workflows of the system (ADR-0203) are drawn as processes of their own, each with its own database file and nothing between them.
>
> The UML node shape adapts draw.io's `cube` path (Apache-2.0) as a maxGraph `CylinderShape` subclass. maxGraph core ships no node shape.

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
## Related decisions

* [ADR-0093: Consistency and synchronisation between views: one source per fact, one-way generation, keyed merge](/adrs/0093-weave-consistency-sync.md) - EIJA keeps many views of one system: code, workflow model, diagrams, OKF pages, term registry, UI sidecar, requirements, links, ledger, exports.
* [ADR-0155: Component diagrams read from the generated code](/adrs/0155-component-diagrams-read-from-the-generated-code.md) - The owner's roadmap asks for component diagrams after use cases and screens.
* [ADR-0203: A system landscape of the workflows that share classes](/adrs/0203-system-landscape-of-workflows-that-share-classes.md) - PlayIDE edits one workflow at a time: one state machine moving one record class, with its class diagram, use cases, screens and laws.
<!-- okf:generated:end links -->
