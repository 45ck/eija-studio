---
type: Class
title: domain.models.Alternative
description: '`class Alternative(Contract)` in `domain/models`.'
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
notes_baseline: a5b965fcb6c13e2ad972106df8f2f5f07364bf9a68765bded68d879798464768
---

# domain.models.Alternative

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class Alternative(Contract)` |
| Code | `repo://src/eija_studio/domain/models.py#Alternative` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

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

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.models.Interpretation](/symbols/domain/models/Interpretation.md) - Type alias `Interpretation` in `domain/models`.

## Referenced by

* [domain.models.Proposal](/symbols/domain/models/Proposal.md) - `class Proposal(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
