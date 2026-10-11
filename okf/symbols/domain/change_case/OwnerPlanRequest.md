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
  sha256: ea3d66f7efd8d5c935b21df662f91b5ca57df15716f2fbea03fc569190667252
notes_baseline: a0ff9aad2b3826ab19da1c6621044865e62711806ce3da827bd89c8e05e162f0
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
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.change_case.OwnerPlanStep](/symbols/domain/change_case/OwnerPlanStep.md) - Reported proposal provenance, never a capability or an owner decision.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [application.service.Studio.from_plan](/symbols/application/service/Studio.from_plan.md) - Select an exact owner-reviewed command batch; previews and provenance never grant authority.
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service`.
<!-- okf:generated:end links -->
