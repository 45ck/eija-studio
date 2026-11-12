---
type: Class
title: domain.change_case.OwnerPlanRequest
description: Exact accepted workflow commands and the identities of their reviewed preview.
resource: repo://src/eija_studio/domain/change_case.py#OwnerPlanRequest
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/change_case.py#OwnerPlanRequest
  title: domain/change_case.py
  hash_method: ast-sig-v1
  sha256: 86b7b1f7a0dfb6b1d9ea58db52a9f45bbb40a0eede0b09af83e328be44de90a4
notes_baseline: b23f8bacbac8fb98f4b25e3b8c260be7623e62b9c61d33c6b75df7fe82460869
---

# domain.change_case.OwnerPlanRequest

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/change_case`](/modules/domain/change_case.md) |
| Signature | `class OwnerPlanRequest(Contract)` |
| Code | `repo://src/eija_studio/domain/change_case.py#OwnerPlanRequest` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Exact accepted workflow commands and the identities of their reviewed preview.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `request` | `str` | `Field(min_length=1, max_length=6000)` |
| `pack_id` | `str` | `Field(min_length=1, max_length=40)` |
| `expected_pack_digest` | `str` | `Field(pattern='^[a-f0-9]{64}$')` |
| `expected_baseline_version` | `JsonInt` | `Field(ge=0)` |
| `expected_baseline_semantic_hash` | `str` | `Field(pattern='^[a-f0-9]{64}$')` |
| `expected_candidate_semantic_hash` | `str` | `Field(pattern='^[a-f0-9]{64}$')` |
| `steps` | `tuple[OwnerPlanStep, ...]` | `Field(min_length=1, max_length=64)` |
| `expected_build_digest` | `str \| None` | `Field(default=None, pattern='^[a-f0-9]{64}$')` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.change_case.OwnerPlanStep](/symbols/domain/change_case/OwnerPlanStep.md) - Reported proposal provenance, never a capability or an owner decision.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.models.JsonInt](/symbols/domain/models/JsonInt.md) - Type alias `JsonInt` in `domain/models`.

## Referenced by

* [application.service.Studio.from_plan](/symbols/application/service/Studio.from_plan.md) - Select an exact owner-reviewed command batch; previews and provenance never grant authority.
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio(StudioViews)` in `application/service`.
<!-- okf:generated:end links -->
