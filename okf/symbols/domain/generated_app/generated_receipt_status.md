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
  sha256: b3954f31fb0db19d9d569ad273c8537c2be8af28f443e82b44dc21ceda8fd290
notes_baseline: af69213102e49915b03c8c621e63b24e4b7bcd1ca3ff0d828e103ad9ded684db
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
