---
type: Module
title: application.history
description: Semantic history is a projection of typed commands, replayed by the existing policy interpreter.
resource: repo://src/eija_studio/application/history.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/history.py
  title: application/history.py
  hash_method: ast-api-v1
  sha256: 0f6bed7632e4920f95e9a13c954685db8a9682722d258ea2277270ebbdb1a8a0
notes_baseline: a81fe5f11c6268c6acd086576df8b260735df5dc983b345f681587580de9cad9
---

# application.history

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/history.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Semantic history is a projection of typed commands, replayed by the existing policy interpreter.

The selected meaning is one protected atomic batch. Owner edits and undone edits are individual
commands. These reconstructed models are not historical verification receipts or case snapshots.
~~~

## Public symbols

* [`SemanticHistory`](/symbols/application/history/SemanticHistory.md) (class) - Validated replay; models includes the selected meaning followed by each applied owner edit.
* [`command_event`](/symbols/application/history/command_event.md) (function) - Append-only command provenance; decision and receipt payloads remain in their existing audit.
* [`history_view`](/symbols/application/history/history_view.md) (function) - Read-only models for navigation plus actual command audit entries; no invented legacy timestamps.
* [`replay`](/symbols/application/history/replay.md) (function) - Fail closed when stored commands no longer explain the candidate under the exact active pack.

## Internal imports

* [`domain/change_case`](/modules/domain/change_case.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/policy`](/modules/domain/policy.md)
* [`domain/transactions`](/modules/domain/transactions.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.change_case](/modules/domain/change_case.md) - Module `domain/change_case` (no module docstring).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.
* [domain.transactions](/modules/domain/transactions.md) - Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.

## Referenced by

* [application.edit_preview](/modules/application/edit_preview.md) - Read-only edit projection over one captured case, using the same interpreter as owner edits.
* [application.edit_proposal](/modules/application/edit_proposal.md) - A read-only offline proposal over one captured candidate; owner edits keep their existing boundary.
* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [application.history.SemanticHistory](/symbols/application/history/SemanticHistory.md) - Validated replay; models includes the selected meaning followed by each applied owner edit.
* [application.history.command_event](/symbols/application/history/command_event.md) - Append-only command provenance; decision and receipt payloads remain in their existing audit.
* [application.history.history_view](/symbols/application/history/history_view.md) - Read-only models for navigation plus actual command audit entries; no invented legacy timestamps.
* [application.history.replay](/symbols/application/history/replay.md) - Fail closed when stored commands no longer explain the candidate under the exact active pack.
<!-- okf:generated:end links -->
