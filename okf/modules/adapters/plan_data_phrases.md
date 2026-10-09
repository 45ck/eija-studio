---
type: Module
title: adapters.plan_data_phrases
description: 'The data-model and role-kind phrases of the offline plan proposer (ADR-0202, #156): add a field to a class, remove one, make one required or optional, and say what kind of actor holds a role.'
resource: repo://src/eija_studio/adapters/plan_data_phrases.py
tags:
- module
- adapters
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/adapters/plan_data_phrases.py
  title: adapters/plan_data_phrases.py
  hash_method: ast-api-v1
  sha256: faf7cdca60b07a8873d1a7a8ce58a65f8f2bf70a43bd12b45b97ea25df00fa37
notes_baseline: 3bc99d6b90319187107f583f2c2d75024e654e2b6a8e5baf677cb8a8a07171c6
---

# adapters.plan_data_phrases

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | adapters |
| Code | `repo://src/eija_studio/adapters/plan_data_phrases.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
The data-model and role-kind phrases of the offline plan proposer (ADR-0202, #156): add a field to a class, remove
one, make one required or optional, and say what kind of actor holds a role. They apply only to a system the person
started; on a shipped pack the class diagram and the roles are the owner's. Like every phrase, what they read is an
untrusted proposal that the application re-checks.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`application/new_system`](/modules/application/new_system.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.new_system](/modules/application/new_system.md) - Start a new system (ADR-0185): the pack documents for a system started from a sketch or copied from a template.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [adapters.plan_proposals](/modules/adapters/plan_proposals.md) - Offline plan proposer for the PlayIDE chat (ADR-0156): a bounded phrase grammar and the pack's modelled meanings, never an LLM.
<!-- okf:generated:end links -->
