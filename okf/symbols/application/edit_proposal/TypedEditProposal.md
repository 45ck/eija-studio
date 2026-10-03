---
type: Class
title: application.edit_proposal.TypedEditProposal
description: '`class TypedEditProposal(Contract)` in `application/edit_proposal`.'
resource: repo://src/eija_studio/application/edit_proposal.py#TypedEditProposal
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/edit_proposal.py#TypedEditProposal
  title: application/edit_proposal.py
  hash_method: ast-sig-v1
  sha256: 84ab2915c244440149e5758224c50a90fcaed036ad66ccd2a685d8c1bd237b3a
notes_baseline: 52a30c9763238616417148f326feacb66805db731535ae9f6286589a36d4cc6b
---

# application.edit_proposal.TypedEditProposal

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/edit_proposal`](/modules/application/edit_proposal.md) |
| Signature | `class TypedEditProposal(Contract)` |
| Code | `repo://src/eija_studio/application/edit_proposal.py#TypedEditProposal` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `scope` | `Literal['typed-edit-proposal']` | `'typed-edit-proposal'` |
| `provider` | `Literal['offline']` | `'offline'` |
| `model` | `Literal['typed-edit-fixture-v1']` | `'typed-edit-fixture-v1'` |
| `live` | `Literal[False]` | `False` |
| `trust` | `Literal['UNTRUSTED_PROPOSAL']` | `'UNTRUSTED_PROPOSAL'` |
| `request` | `str` | `Field(min_length=1, max_length=6000)` |
| `pack` | `EditProposalPack` |  |
| `preview` | `EditPreview` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.edit_preview.EditPreview](/symbols/application/edit_preview/EditPreview.md) - An uncommitted candidate bound to a captured case revision; no evidence or edit authority.
* [application.edit_proposal.EditProposalPack](/symbols/application/edit_proposal/EditProposalPack.md) - `class EditProposalPack(Contract)` in `application/edit_proposal`.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [application.edit_proposal.propose_edit](/symbols/application/edit_proposal/propose_edit.md) - No persistence or evidence: resolve one request, then use the existing policy-checked projection.
<!-- okf:generated:end links -->
