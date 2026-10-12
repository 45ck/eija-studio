---
type: Class
title: domain.generated_app.GeneratedAppActivation
description: '`class GeneratedAppActivation(Contract)` in `domain/generated_app`.'
resource: repo://src/eija_studio/domain/generated_app.py#GeneratedAppActivation
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/generated_app.py#GeneratedAppActivation
  title: domain/generated_app.py
  hash_method: ast-sig-v1
  sha256: 2c26a16ea08d8d965309ebc8b7006f1ca9e16f3f7043824a40672975931da714
notes_baseline: e0d50fa6b6980e29c63cdfc736dbc1cc75e45ae71f9ad6b237cc55e56b98e79c
---

# domain.generated_app.GeneratedAppActivation

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/generated_app`](/modules/domain/generated_app.md) |
| Signature | `class GeneratedAppActivation(Contract)` |
| Code | `repo://src/eija_studio/domain/generated_app.py#GeneratedAppActivation` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `format` | `Literal['eija.generated-app-activation.v1']` |  |
| `case_id` | `str` |  |
| `baseline_version` | `int` | `Field(ge=1, strict=True)` |
| `binding` | `GeneratedAppBinding` |  |
| `subject_hash` | `Digest` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.generated_app.Digest](/symbols/domain/generated_app/Digest.md) - Type alias `Digest` in `domain/generated_app`.
* [domain.generated_app.GeneratedAppBinding](/symbols/domain/generated_app/GeneratedAppBinding.md) - `class GeneratedAppBinding(Contract)` in `domain/generated_app`.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [application.service_views.StudioViews.active_app_build](/symbols/application/service_views/StudioViews.active_app_build.md) - Read the atomically associated case and remeasure its exact approved generated application.
<!-- okf:generated:end links -->
