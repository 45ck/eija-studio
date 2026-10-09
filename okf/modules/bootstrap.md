---
type: Module
title: bootstrap
description: 'The only composition root: wires application ports to concrete adapters.'
resource: repo://src/eija_studio/bootstrap.py
tags:
- module
- root
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/bootstrap.py
  title: bootstrap.py
  hash_method: ast-api-v1
  sha256: 529fded9fd77de98155f8c9bf6bd7248e5b052c76b3baa25fe17f8d4a95ebdb8
notes_baseline: 8a9685cbfba5e1c9aaf12731818ccdea6515594b59cb72248308d45c3e258212
---

# bootstrap

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | root |
| Code | `repo://src/eija_studio/bootstrap.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
The only composition root: wires application ports to concrete adapters.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`adapters/edit_proposals`](/modules/adapters/edit_proposals.md)
* [`adapters/identity`](/modules/adapters/identity.md)
* [`adapters/plan_proposals`](/modules/adapters/plan_proposals.md)
* [`adapters/receipts`](/modules/adapters/receipts.md)
* [`adapters/repository`](/modules/adapters/repository.md)
* [`adapters/repository_analysis`](/modules/adapters/repository_analysis.md)
* [`adapters/repository_changes`](/modules/adapters/repository_changes.md)
* [`adapters/self_facts`](/modules/adapters/self_facts.md)
* [`adapters/sqlite_store`](/modules/adapters/sqlite_store.md)
* [`adapters/system_describer`](/modules/adapters/system_describer.md)
* [`adapters/system_library`](/modules/adapters/system_library.md)
* [`application/service`](/modules/application/service.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [adapters.edit_proposals](/modules/adapters/edit_proposals.md) - Bounded offline request fixture: exact model names and complete phrases, never an LLM.
* [adapters.identity](/modules/adapters/identity.md) - Measured release identity, not a proof of correctness or author authenticity.
* [adapters.plan_proposals](/modules/adapters/plan_proposals.md) - Offline plan proposer for the PlayIDE chat (ADR-0156): a bounded phrase grammar and the pack's modelled meanings, never an LLM.
* [adapters.receipts](/modules/adapters/receipts.md) - Local integrity seal.
* [adapters.repository](/modules/adapters/repository.md) - Repository analysis and bounded source navigation over captured checkout bytes.
* [adapters.repository_analysis](/modules/adapters/repository_analysis.md) - Captured-byte syntax and partial impact adapted to existing Weave primitives.
* [adapters.repository_changes](/modules/adapters/repository_changes.md) - Read-only, bounded comparison of two local Git commits.
* [adapters.self_facts](/modules/adapters/self_facts.md) - Syntactic facts about EIJA's own review implementation, never a conformance proof.
* [adapters.sqlite_store](/modules/adapters/sqlite_store.md) - Durable local unit of work.
* [adapters.system_describer](/modules/adapters/system_describer.md) - Offline system describer for PlayIDE's "Describe your app" start (ADR-0203): a fixed library of app shapes and a small reader for the fields and roles a descri…
* [adapters.system_library](/modules/adapters/system_library.md) - Where a person's own systems live on disk (ADR-0185): one folder per system under a systems home, the recent list, and the saved draft of the work in progress.
* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
<!-- okf:generated:end links -->
