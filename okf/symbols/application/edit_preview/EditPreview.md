---
type: Class
title: application.edit_preview.EditPreview
description: An uncommitted candidate bound to a captured case revision; no evidence or edit authority.
resource: repo://src/eija_studio/application/edit_preview.py#EditPreview
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/edit_preview.py#EditPreview
  title: application/edit_preview.py
  hash_method: ast-sig-v1
  sha256: acb0f0ae1b817b55e8245f44888d11516ae65f00c27d6b577859e5d186057678
notes_baseline: bc0832b2095944633974385aab60165681d4e65d572bbe315a04723447ec1134
---

# application.edit_preview.EditPreview

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/edit_preview`](/modules/application/edit_preview.md) |
| Signature | `class EditPreview(Contract)` |
| Code | `repo://src/eija_studio/application/edit_preview.py#EditPreview` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
An uncommitted candidate bound to a captured case revision; no evidence or edit authority.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `legal` | `bool` |  |
| `codes` | `list[str]` |  |
| `refs` | `list[str]` |  |
| `case_id` | `str` |  |
| `version` | `int` |  |
| `stage` | `str` |  |
| `semantic_hash` | `str` |  |
| `transaction` | `Transaction` |  |
| `current` | `Workflow` |  |
| `candidate` | `Workflow \| None` |  |
| `candidate_semantic_hash` | `str \| None` |  |
| `applied` | `Literal[False]` | `False` |
| `persisted` | `Literal[False]` | `False` |
| `scope` | `Literal['semantic-edit-preview']` | `'semantic-edit-preview'` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.

## Referenced by

* [application.edit_preview.preview_edit](/symbols/application/edit_preview/preview_edit.md) - The candidate edit would produce from this snapshot, or its refusal without a guessed model.
<!-- okf:generated:end links -->
