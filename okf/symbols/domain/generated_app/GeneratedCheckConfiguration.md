---
type: Class
title: domain.generated_app.GeneratedCheckConfiguration
description: '`class GeneratedCheckConfiguration(Contract)` in `domain/generated_app`.'
resource: repo://src/eija_studio/domain/generated_app.py#GeneratedCheckConfiguration
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/generated_app.py#GeneratedCheckConfiguration
  title: domain/generated_app.py
  hash_method: ast-sig-v1
  sha256: e474e039e651fe606687e9b8a5dacffb2b81c2866e7a3a40796fba043238d668
notes_baseline: 6f1397bdf8856bac67b7bf2d4365eb81c44e3a0e2afcfd6deb8acd54279e161b
---

# domain.generated_app.GeneratedCheckConfiguration

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/generated_app`](/modules/domain/generated_app.md) |
| Signature | `class GeneratedCheckConfiguration(Contract)` |
| Code | `repo://src/eija_studio/domain/generated_app.py#GeneratedCheckConfiguration` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `runner` | `Literal['python-unittest-discover']` |  |
| `arguments` | `tuple[str, ...]` |  |
| `timeout_seconds` | `int` | `Field(gt=0, strict=True)` |
| `python_version` | `str` |  |
| `platform` | `str` |  |
| `environment_digest` | `Digest` |  |
| `runner_environment_digest` | `Digest` |  |
| `isolation` | `Literal['isolated-python-fresh-bytecode-v1']` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.generated_app.Digest](/symbols/domain/generated_app/Digest.md) - Type alias `Digest` in `domain/generated_app`.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [domain.generated_app.GeneratedAppBinding](/symbols/domain/generated_app/GeneratedAppBinding.md) - `class GeneratedAppBinding(Contract)` in `domain/generated_app`.
<!-- okf:generated:end links -->
