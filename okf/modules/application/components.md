---
type: Module
title: application.components
description: The component diagram of an app built from the model (ADR-0155), extracted from the generated files themselves.
resource: repo://src/eija_studio/application/components.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/components.py
  title: application/components.py
  hash_method: ast-api-v1
  sha256: 5db5d7010f5dde2e6e96440fa3be55b63bdd2f1822cb1094718c4c1755c58431
notes_baseline: 575213b9f3cfe4e45f9dc4697173e0d5ae3d9f01ffb20bb0a817c3a3d64f8e1d
---

# application.components

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/components.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
The component diagram of an app built from the model (ADR-0155), extracted from the generated files themselves.

Nothing here is a description someone wrote: components are the generated modules, the EIJA modules they import and the
infrastructure they use; each dependency is an import statement, a page request to a route the server serves, or a
module reading a generated file by name. Each provider's interface is the set of names its users import from it. So
the diagram changes when the generated code changes, and cannot claim a dependency the code does not have.

Pure: parses text with `ast` and regular expressions, never imports or runs the generated code.
~~~

## Public symbols

* [`FORMAT`](/symbols/application/components/FORMAT.md) (constant) - no docstring
* [`INFRASTRUCTURE`](/symbols/application/components/INFRASTRUCTURE.md) (constant) - no docstring
* [`PAGE`](/symbols/application/components/PAGE.md) (constant) - no docstring
* [`ROUTE`](/symbols/application/components/ROUTE.md) (constant) - no docstring
* [`app_components`](/symbols/application/components/app_components.md) (function) - Components, interfaces and dependencies of a generated app, read from its files (`app_files` output).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [application.components.FORMAT](/symbols/application/components/FORMAT.md) - Constant `FORMAT` in `application/components`.
* [application.components.INFRASTRUCTURE](/symbols/application/components/INFRASTRUCTURE.md) - Constant `INFRASTRUCTURE` in `application/components`.
* [application.components.PAGE](/symbols/application/components/PAGE.md) - Constant `PAGE` in `application/components`.
* [application.components.ROUTE](/symbols/application/components/ROUTE.md) - Constant `ROUTE` in `application/components`.
* [application.components.app_components](/symbols/application/components/app_components.md) - Components, interfaces and dependencies of a generated app, read from its files (`app_files` output).
<!-- okf:generated:end links -->
