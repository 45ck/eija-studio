---
type: Module
title: adapters.edit_proposals
description: 'Bounded offline request fixture: exact model names and complete phrases, never an LLM.'
resource: repo://src/eija_studio/adapters/edit_proposals.py
tags:
- module
- adapters
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/adapters/edit_proposals.py
  title: adapters/edit_proposals.py
  hash_method: ast-api-v1
  sha256: 18d3bf7dfe19d7228b89c57a2fd13fe29ca0ae8a3d19ac799af7c348de5b9be9
notes_baseline: f4e660e456a1ffaf5e9fa54d4a8624dee592df27c8fb1ce9ac3e4c3a8b1b9464
---

# adapters.edit_proposals

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | adapters |
| Code | `repo://src/eija_studio/adapters/edit_proposals.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Bounded offline request fixture: exact model names and complete phrases, never an LLM.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`domain/models`](/modules/domain/models.md)
* [`domain/transactions`](/modules/domain/transactions.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.transactions](/modules/domain/transactions.md) - Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.

## Referenced by

* [bootstrap](/modules/bootstrap.md) - The only composition root: wires application ports to concrete adapters.
<!-- okf:generated:end links -->
