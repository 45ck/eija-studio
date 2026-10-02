---
type: Module
title: application.edit_preview
description: Read-only edit projection over one captured case, using the same interpreter as owner edits.
resource: repo://src/eija_studio/application/edit_preview.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/edit_preview.py
  title: application/edit_preview.py
  hash_method: ast-api-v1
  sha256: 6920398a22f4a75613c85c8db23478c44f85e251efddfcfa091e786469568621
notes_baseline: e77b87d0a5b9ca2e42f7301f657b607c82fad06f92d871e261c3671c53a8ae4a
---

# application.edit_preview

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/edit_preview.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Read-only edit projection over one captured case, using the same interpreter as owner edits.
~~~

## Public symbols

* [`EditPreview`](/symbols/application/edit_preview/EditPreview.md) (class) - An uncommitted candidate bound to a captured case revision; no evidence or edit authority.
* [`preview_edit`](/symbols/application/edit_preview/preview_edit.md) (function) - The candidate edit would produce from this snapshot, or its refusal without a guessed model.

## Internal imports

* [`application/history`](/modules/application/history.md)
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

* [application.history](/modules/application/history.md) - Semantic history is a projection of typed commands, replayed by the existing policy interpreter.
* [domain.change_case](/modules/domain/change_case.md) - Module `domain/change_case` (no module docstring).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.
* [domain.transactions](/modules/domain/transactions.md) - Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.

## Referenced by

* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [interfaces.http](/modules/interfaces/http.md) - Loopback-only local adapter.
* [application.edit_preview.EditPreview](/symbols/application/edit_preview/EditPreview.md) - An uncommitted candidate bound to a captured case revision; no evidence or edit authority.
* [application.edit_preview.preview_edit](/symbols/application/edit_preview/preview_edit.md) - The candidate edit would produce from this snapshot, or its refusal without a guessed model.
<!-- okf:generated:end links -->
