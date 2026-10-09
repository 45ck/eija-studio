---
type: Module
title: application.deployment
description: The deployment diagram of an app built from the model (ADR-0206), read from the generated files themselves.
resource: repo://src/eija_studio/application/deployment.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/deployment.py
  title: application/deployment.py
  hash_method: ast-api-v1
  sha256: 6769f05a9ac3351ba533f63fc98e632171d250cdc86907143f5409177fb064f4
notes_baseline: 7dd50468c5302d6dab22d2a025e31b303be1547e65fc155956dd672581c962de
---

# application.deployment

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/deployment.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
The deployment diagram of an app built from the model (ADR-0206), read from the generated files themselves.

As with the component diagram (ADR-0155), nothing here is a description someone wrote. The nodes are where the
generated files run: the browser that loads the page, the Python process that `run.py` starts, and the SQLite database
file that process opens, all on one computer. The address, port and database path are the defaults `run.py` and
`app/server.py` declare, with the option and environment variable that change them. Each communication path is an
HTTP route the page calls and the server serves, or the `sqlite3` connection; each artifact is a group of generated
files, plus the installed EIJA package the app imports.

Pure: parses text with `ast` and regular expressions, never imports or runs the generated code.
~~~

## Public symbols

* [`FORMAT`](/symbols/application/deployment/FORMAT.md) (constant) - no docstring
* [`HOST`](/symbols/application/deployment/HOST.md) (constant) - no docstring
* [`PAGE`](/symbols/application/deployment/PAGE.md) (constant) - no docstring
* [`ROUTE`](/symbols/application/deployment/ROUTE.md) (constant) - no docstring
* [`app_deployment`](/symbols/application/deployment/app_deployment.md) (function) - Where a generated app runs (`app_files` output), with `kernel` the installed eija_studio version it imports.
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [application.deployment.FORMAT](/symbols/application/deployment/FORMAT.md) - Constant `FORMAT` in `application/deployment`.
* [application.deployment.HOST](/symbols/application/deployment/HOST.md) - Constant `HOST` in `application/deployment`.
* [application.deployment.PAGE](/symbols/application/deployment/PAGE.md) - Constant `PAGE` in `application/deployment`.
* [application.deployment.ROUTE](/symbols/application/deployment/ROUTE.md) - Constant `ROUTE` in `application/deployment`.
* [application.deployment.app_deployment](/symbols/application/deployment/app_deployment.md) - Where a generated app runs (`app_files` output), with `kernel` the installed eija_studio version it imports.
<!-- okf:generated:end links -->
