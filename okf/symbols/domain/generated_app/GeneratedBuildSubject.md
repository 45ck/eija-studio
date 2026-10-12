---
type: Class
title: domain.generated_app.GeneratedBuildSubject
description: '`class GeneratedBuildSubject(Contract)` in `domain/generated_app`.'
resource: repo://src/eija_studio/domain/generated_app.py#GeneratedBuildSubject
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/generated_app.py#GeneratedBuildSubject
  title: domain/generated_app.py
  hash_method: ast-sig-v1
  sha256: f12be6b70358ddfc95877d5fdf874f7e60ab3f23ea9366d6e0f38d6c4cd664cc
notes_baseline: 570483eec2315a8847221355cc3119ca8706bf1534c0a993c867dd101444178d
---

# domain.generated_app.GeneratedBuildSubject

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/generated_app`](/modules/domain/generated_app.md) |
| Signature | `class GeneratedBuildSubject(Contract)` |
| Code | `repo://src/eija_studio/domain/generated_app.py#GeneratedBuildSubject` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `format` | `Literal['eija.build-subject.v1']` |  |
| `model_hash` | `Digest` |  |
| `workflow_digest` | `Digest` |  |
| `pack_digest` | `Digest` |  |
| `data_digest` | `Digest \| None` |  |
| `screens_digest` | `Digest` |  |
| `templates_digest` | `Digest` |  |
| `template_paths` | `tuple[str, ...]` |  |
| `implementation_digest` | `Digest` |  |
| `payload_paths` | `tuple[str, ...]` |  |
| `generated_files_hash` | `Digest` |  |
| `digest` | `Digest` |  |

## Methods

* [`consistent_digest`](/symbols/domain/generated_app/GeneratedBuildSubject.consistent_digest.md) - `def consistent_digest(self) -> Self`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.generated_app.Digest](/symbols/domain/generated_app/Digest.md) - Type alias `Digest` in `domain/generated_app`.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [domain.generated_app.GeneratedAppBinding](/symbols/domain/generated_app/GeneratedAppBinding.md) - `class GeneratedAppBinding(Contract)` in `domain/generated_app`.
* [domain.generated_app.GeneratedBuildSubject.consistent_digest](/symbols/domain/generated_app/GeneratedBuildSubject.consistent_digest.md) - `def consistent_digest(self) -> Self` in `domain/generated_app`.
<!-- okf:generated:end links -->
