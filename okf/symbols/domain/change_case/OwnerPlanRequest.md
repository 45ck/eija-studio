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
  sha256: 958c6d5921e0097183d777337aa043df3277b4ce9d61bed12f2b06946a1edddc
notes_baseline: 8203cdb7678e2718fcd79a34309d9594127e73acfb25047a3635468c6fc1c35d
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
| `expected_baseline_version` | `int` | `Field(ge=0, strict=True)` |
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

## Referenced by

* [application.service.Studio.from_plan](/symbols/application/service/Studio.from_plan.md) - Select an exact owner-reviewed command batch; previews and provenance never grant authority.
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio(StudioViews)` in `application/service`.
<!-- okf:generated:end links -->
