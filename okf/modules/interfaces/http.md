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
  sha256: f03683658e7ab8f9880cf910940ee3c4eb1c1c0c104aa9114334a60923043b09
notes_baseline: 92fa6f869b06a5d66bddfec5dae36db2394a6eb5b9d73ceb8e459aacfb507dfe
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
<!-- okf:generated:end links -->
