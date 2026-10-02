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
  sha256: 3332ae2a788b96027e679cab6f8882ce79c8885a57aca3bfd3c899188c5c2f64
notes_baseline: abb7ce434545d8fa87b7400af7feb0e62b4fcfa7e1a2790459db0be210808ff7
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
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/transactions`](/modules/domain/transactions.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.diagram_catalog](/modules/application/diagram_catalog.md) - Named diagram views over a baseline and an optional candidate Workflow.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.transactions](/modules/domain/transactions.md) - Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.
<!-- okf:generated:end links -->
