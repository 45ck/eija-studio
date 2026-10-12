---
type: Function
title: domain.generated_app.generated_receipt_status
description: Compute a scoped process observation, never trust its submitted status field.
resource: repo://src/eija_studio/domain/generated_app.py#generated_receipt_status
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/generated_app.py#generated_receipt_status
  title: domain/generated_app.py
  hash_method: ast-v2
  sha256: 15d8c009b6b9430fd14436fe6dfb241fa6086ed257dfe59d41359c8dcde413f2
notes_baseline: 1f55effbbec876382575d43e7a66cb59c1d368a975bef4f902d8242480c6409e
---

# domain.generated_app.generated_receipt_status

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/generated_app`](/modules/domain/generated_app.md) |
| Signature | `def generated_receipt_status(receipt: dict[str, Any], binding: GeneratedAppBinding, authentic: bool) -> str` |
| Code | `repo://src/eija_studio/domain/generated_app.py#generated_receipt_status` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Compute a scoped process observation, never trust its submitted status field.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.generated_app.GeneratedAppBinding](/symbols/domain/generated_app/GeneratedAppBinding.md) - `class GeneratedAppBinding(Contract)` in `domain/generated_app`.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.

## Referenced by

* [application.generated_app.app_build_view](/symbols/application/generated_app/app_build_view.md) - Keep workflow evidence separate from generated application execution evidence.
<!-- okf:generated:end links -->
