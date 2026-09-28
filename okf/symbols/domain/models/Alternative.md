---
type: Class
title: domain.models.Alternative
description: '`class Alternative(Contract)` in `domain/models` (the source has no docstring).'
resource: repo://src/eija_studio/domain/models.py#Alternative
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#Alternative
  title: domain/models.py
  hash_method: ast-sig-v1
  sha256: 9f68103c0c7ca19301958b302b9a59e45213350b80de1b8cdf0feb48ba05b294
---

# domain.models.Alternative

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class Alternative(Contract)` |
| Code | `repo://src/eija_studio/domain/models.py#Alternative` |
| Hash | `ast-sig-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `interpretation` | `Interpretation` |  |
| `explanation` | `str` | `Field(min_length=1, max_length=1600)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models` (the source has no docstring).
* [domain.models.Interpretation](/symbols/domain/models/Interpretation.md) - `Interpretation = Literal['recommend_only', 'final_approval', 'confirm_only', 'unsupported']` in `domain/models` (the source has no docstring).

## Referenced by

* [domain.models.Proposal](/symbols/domain/models/Proposal.md) - `class Proposal(Contract)` in `domain/models` (the source has no docstring).
<!-- okf:generated:end links -->
