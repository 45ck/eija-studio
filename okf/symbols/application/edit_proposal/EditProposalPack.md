---
type: Class
title: application.edit_proposal.EditProposalPack
description: '`class EditProposalPack(Contract)` in `application/edit_proposal`.'
resource: repo://src/eija_studio/application/edit_proposal.py#EditProposalPack
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/edit_proposal.py#EditProposalPack
  title: application/edit_proposal.py
  hash_method: ast-sig-v1
  sha256: f75beb54aad52405e382bc81b20ac7d4466cedb2cc7bd64bbacc9ceecb37651d
notes_baseline: 09f970b1f7890b18d4934497d6130f5f191e033d9735fee86560963fbf749abe
---

# application.edit_proposal.EditProposalPack

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/edit_proposal`](/modules/application/edit_proposal.md) |
| Signature | `class EditProposalPack(Contract)` |
| Code | `repo://src/eija_studio/application/edit_proposal.py#EditProposalPack` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `id` | `str` |  |
| `digest` | `str` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [application.edit_proposal.TypedEditProposal](/symbols/application/edit_proposal/TypedEditProposal.md) - `class TypedEditProposal(Contract)` in `application/edit_proposal`.
* [application.edit_proposal.propose_edit](/symbols/application/edit_proposal/propose_edit.md) - No persistence or evidence: resolve one request, then use the existing policy-checked projection.
<!-- okf:generated:end links -->
