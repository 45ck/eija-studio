---
type: Module
title: interfaces.http
description: Loopback-only local adapter.
resource: repo://src/eija_studio/interfaces/http.py
tags:
- module
- interfaces
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/interfaces/http.py
  title: interfaces/http.py
  hash_method: ast-api-v1
  sha256: 967486ca515575de5948bb5d275c4c219a8837c14db8d8901db28bfe76310854
notes_baseline: f8347f0c60a1322a771f8ec8aaf940a09e422f4c8f9c5193a8a9f8873704b9fe
---

# interfaces.http

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | interfaces |
| Code | `repo://src/eija_studio/interfaces/http.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Loopback-only local adapter. No public hosting, CORS, remote provider proxy or raw file endpoint.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`application/diagram_catalog`](/modules/application/diagram_catalog.md)
* [`application/edit_preview`](/modules/application/edit_preview.md)
* [`application/edit_proposal`](/modules/application/edit_proposal.md)
* [`application/repository`](/modules/application/repository.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/transactions`](/modules/domain/transactions.md)
* [`interfaces/play`](/modules/interfaces/play.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.diagram_catalog](/modules/application/diagram_catalog.md) - Named diagram views over a baseline and an optional candidate Workflow.
* [application.edit_preview](/modules/application/edit_preview.md) - Read-only edit projection over one captured case, using the same interpreter as owner edits.
* [application.edit_proposal](/modules/application/edit_proposal.md) - A read-only offline proposal over one captured candidate; owner edits keep their existing boundary.
* [application.repository](/modules/application/repository.md) - Read-only repository evidence port; this does not grant project execution or approval.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.transactions](/modules/domain/transactions.md) - Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.
* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, and Build & run of the model as a live app beside it (ADR-0151).
<!-- okf:generated:end links -->
