---
type: Module
title: application.edit_proposal
description: A read-only offline proposal over one captured candidate; owner edits keep their existing boundary.
resource: repo://src/eija_studio/application/edit_proposal.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/edit_proposal.py
  title: application/edit_proposal.py
  hash_method: ast-api-v1
  sha256: 98c94d3d8e005c6a90d63843c11d67e72b6b0180f8387072e76714b26151b533
notes_baseline: 877abf7c1c7e9ec101da6f6c0ca982ce6d753ffa0244917b220c377c30bded34
---

# application.edit_proposal

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/edit_proposal.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
A read-only offline proposal over one captured candidate; owner edits keep their existing boundary.
~~~

## Public symbols

* [`EditProposalPack`](/symbols/application/edit_proposal/EditProposalPack.md) (class) - no docstring
* [`TypedEditProposal`](/symbols/application/edit_proposal/TypedEditProposal.md) (class) - no docstring
* [`propose_edit`](/symbols/application/edit_proposal/propose_edit.md) (function) - No persistence or evidence: resolve one request, then use the existing policy-checked projection.

## Internal imports

* [`application/edit_preview`](/modules/application/edit_preview.md)
* [`application/history`](/modules/application/history.md)
* [`application/ports`](/modules/application/ports.md)
* [`domain/affordance`](/modules/domain/affordance.md)
* [`domain/change_case`](/modules/domain/change_case.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/transactions`](/modules/domain/transactions.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.edit_preview](/modules/application/edit_preview.md) - Read-only edit projection over one captured case, using the same interpreter as owner edits.
* [application.history](/modules/application/history.md) - Semantic history is a projection of typed commands, replayed by the existing policy interpreter.
* [application.ports](/modules/application/ports.md) - Application-owned ports.
* [domain.affordance](/modules/domain/affordance.md) - Affordance map (WBS 1.3): which single edits the kernel would accept, and why the others are refused.
* [domain.change_case](/modules/domain/change_case.md) - Module `domain/change_case` (no module docstring).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.transactions](/modules/domain/transactions.md) - Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.

## Referenced by

* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [interfaces.http](/modules/interfaces/http.md) - Loopback-only local adapter.
* [application.edit_proposal.EditProposalPack](/symbols/application/edit_proposal/EditProposalPack.md) - `class EditProposalPack(Contract)` in `application/edit_proposal`.
* [application.edit_proposal.TypedEditProposal](/symbols/application/edit_proposal/TypedEditProposal.md) - `class TypedEditProposal(Contract)` in `application/edit_proposal`.
* [application.edit_proposal.propose_edit](/symbols/application/edit_proposal/propose_edit.md) - No persistence or evidence: resolve one request, then use the existing policy-checked projection.
<!-- okf:generated:end links -->
