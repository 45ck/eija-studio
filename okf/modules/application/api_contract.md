---
type: Module
title: application.api_contract
description: 'The API contract of an app built from a workflow (ADR-0207): an OpenAPI 3.1 document of what the generated server serves, written from the model, the pack and the data model rather than by hand.'
resource: repo://src/eija_studio/application/api_contract.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/api_contract.py
  title: application/api_contract.py
  hash_method: ast-api-v1
  sha256: 231027563d2e3c4a8c900bceca8aea2abe3cab50cd62a6688f4e2c0118019343
notes_baseline: 368bfccd0458aaf18cf9c794b8d64528fdd20425254822ce1d6ac8aa869cfd88
---

# application.api_contract

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/api_contract.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
The API contract of an app built from a workflow (ADR-0207): an OpenAPI 3.1 document of what the generated server
serves, written from the model, the pack and the data model rather than by hand.

The paths and status codes are those of the generated server (ADR-0150). Request bodies come from the same sources the
server checks against: the record fields from the record class (the schema says what `check_values` accepts), the
actions from the model's transitions and the actors from the pack's fixture directory. The kernel's refusal codes are
the documented error responses, grouped by the status the server sends them with: both read one table,
`eija_studio.domain.app_http` (ADR-0254). The drift check is in the tests: every route the generated server serves is in
the document, and every path in the document is served.

Pure: reads the pack, its model and its data model only.
~~~

## Public symbols

* [`FORMAT`](/symbols/application/api_contract/FORMAT.md) (constant) - no docstring
* [`ONCE`](/symbols/application/api_contract/ONCE.md) (constant) - no docstring
* [`api_contract`](/symbols/application/api_contract/api_contract.md) (function) - The OpenAPI 3.1 document of the app this pack, model and data model build.

## Internal imports

* [`domain/app_http`](/modules/domain/app_http.md)
* [`domain/data`](/modules/domain/data.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.app_http](/modules/domain/app_http.md) - The HTTP status a generated app answers each refusal code with (ADR-0254).
* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [application.api_contract.FORMAT](/symbols/application/api_contract/FORMAT.md) - Constant `FORMAT` in `application/api_contract`.
* [application.api_contract.ONCE](/symbols/application/api_contract/ONCE.md) - Constant `ONCE` in `application/api_contract`.
* [application.api_contract.api_contract](/symbols/application/api_contract/api_contract.md) - The OpenAPI 3.1 document of the app this pack, model and data model build.
<!-- okf:generated:end links -->
