---
type: Function
title: application.generated_app.validate_review_payload
description: The selected payload and installed implementation must satisfy the same build-subject contract.
resource: repo://src/eija_studio/application/generated_app.py#validate_review_payload
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/generated_app.py#validate_review_payload
  title: application/generated_app.py
  hash_method: ast-v2
  sha256: 11ba77663492f47a23488418b8bd97fdc6b2b8a8516dfdea1202e19a142544c3
notes_baseline: 6582e339d3b898b971d4e2484909fe57d75530cc8b829e9b4db391dcbe6731e9
---

# application.generated_app.validate_review_payload

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/generated_app`](/modules/application/generated_app.md) |
| Signature | `def validate_review_payload(files: dict[str, str], implementation: str, binding: GeneratedAppBinding) -> None` |
| Code | `repo://src/eija_studio/application/generated_app.py#validate_review_payload` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The selected payload and installed implementation must satisfy the same build-subject contract.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.build_subject.checked_build_subject](/symbols/application/build_subject/checked_build_subject.md) - Check archived identity, optionally binding it to the installed runtime and prior snapshot.
* [domain.generated_app.GeneratedAppBinding](/symbols/domain/generated_app/GeneratedAppBinding.md) - `class GeneratedAppBinding(Contract)` in `domain/generated_app`.
<!-- okf:generated:end links -->
