---
type: Function
title: domain.evidence.receipt_status
description: One receipt's applicability by its OWN declared claim and kind; an unauthentic receipt is FAIL.
resource: repo://src/eija_studio/domain/evidence.py#receipt_status
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/evidence.py#receipt_status
  title: domain/evidence.py
  hash_method: ast-v2
  sha256: 5d1a69f85076ea56052e145041fe8076bd4760335e15117b9d0d4817e5b3d79b
notes_baseline: 779622b2e574bdb2b7ada85bca3643e9912adf452a78f437b9ad7e6af51e4a67
---

# domain.evidence.receipt_status

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/evidence`](/modules/domain/evidence.md) |
| Signature | `def receipt_status(receipt: dict[str, Any], subject: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool], context: Context \| None=None) -> str` |
| Code | `repo://src/eija_studio/domain/evidence.py#receipt_status` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
One receipt's applicability by its OWN declared claim and kind; an unauthentic receipt is FAIL.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.evidence.assess_receipt](/symbols/domain/evidence/assess_receipt.md) - `def assess_receipt(receipt: dict[str, Any], subject: dict[str, Any], claim: str, kind: str, context: Context…` in `domain/evidence`.
* [domain.formal.Context](/symbols/domain/formal/Context.md) - What the kernel itself knows about the CURRENT subject, beyond the technical dimensions.

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
<!-- okf:generated:end links -->
