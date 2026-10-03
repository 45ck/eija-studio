---
type: Function
title: application.edit_proposal.propose_edit
description: 'No persistence or evidence: resolve one request, then use the existing policy-checked projection.'
resource: repo://src/eija_studio/application/edit_proposal.py#propose_edit
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/edit_proposal.py#propose_edit
  title: application/edit_proposal.py
  hash_method: ast-v2
  sha256: 62c32a0b5319ef59a7d86ab63d827cb42fe48f545a817296fa8ee0afbebc6126
notes_baseline: d243a2c34976968a07a771409b76eb554f8e345f11c3f56878be8f73454a6604
verified:
- by: process:codex-packaging-integration
  at: '2026-10-03T03:27:08Z'
  notes_sha256: 9e4cf9d68aa586af1cc26f25d4891403b5967337b8488e21bab41019ba87df6b
  sources_sha256: d243a2c34976968a07a771409b76eb554f8e345f11c3f56878be8f73454a6604
---

# application.edit_proposal.propose_edit

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/edit_proposal`](/modules/application/edit_proposal.md) |
| Signature | `def propose_edit(case: ChangeCase, request: str, pack: Pack, proposer: EditProposer \| None) -> TypedEditProposal` |
| Code | `repo://src/eija_studio/application/edit_proposal.py#propose_edit` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
No persistence or evidence: resolve one request, then use the existing policy-checked projection.
~~~
<!-- okf:generated:end facts -->

## Notes

This application helper owns the missing-proposer refusal as well as request,
editable-case and semantic-history checks. It validates the untrusted result against
captured typed choices and delegates policy/candidate projection to `preview_edit`.
It neither persists state nor checks a later database revision; the Studio use case
owns capture and its final version recheck.

<!-- okf:generated:begin links -->
## Depends on

* [application.edit_preview.preview_edit](/symbols/application/edit_preview/preview_edit.md) - The candidate edit would produce from this snapshot, or its refusal without a guessed model.
* [application.edit_proposal.EditProposalPack](/symbols/application/edit_proposal/EditProposalPack.md) - `class EditProposalPack(Contract)` in `application/edit_proposal`.
* [application.edit_proposal.TypedEditProposal](/symbols/application/edit_proposal/TypedEditProposal.md) - `class TypedEditProposal(Contract)` in `application/edit_proposal`.
* [application.history.replay](/symbols/application/history/replay.md) - Fail closed when stored commands no longer explain the candidate under the exact active pack.
* [application.ports.EditProposer](/symbols/application/ports/EditProposer.md) - Offline request resolution only; returns an untrusted transaction and performs no IO or persistence.
* [domain.affordance.affordances](/symbols/domain/affordance/affordances.md) - Every single-step retarget and role change of ``model``, each with its dry-run verdict.
* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.transactions.parse_transaction](/symbols/domain/transactions/parse_transaction.md) - Validate one transaction document; a malformed one is ``EDIT_INVALID``, never a crash.

## Referenced by

* [application.service.Studio.propose_edit](/symbols/application/service/Studio.propose_edit.md) - Read-only offline proposal; capture and recheck the case revision without granting owner authority.
<!-- okf:generated:end links -->
