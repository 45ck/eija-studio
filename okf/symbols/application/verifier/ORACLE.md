---
type: Constant
title: application.verifier.ORACLE
description: Hand-authored expected role, source and target state per action, separate from the runtime's guard evaluator.
resource: repo://src/eija_studio/application/verifier.py#ORACLE
tags:
- symbol
- application
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/verifier.py#ORACLE
  title: application/verifier.py
  hash_method: ast-v1
  sha256: 1e6160d2919dc79e1220c7a202e052a4b6ae45dde80c90c630b830ed2aa084ed
description_override: Hand-authored expected role, source and target state per action, separate from the runtime's guard evaluator.
---

# application.verifier.ORACLE

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`application/verifier`](/modules/application/verifier.md) |
| Signature | `ORACLE = {'Submit': ('Teacher', 'Draft', 'Submitted'), 'Recommend': ('Teacher', 'Submitted', 'Recommended'), 'Approve': ('Registrar', 'Recommended', 'Approved'…` |
| Code | `repo://src/eija_studio/application/verifier.py#ORACLE` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Shares authorship with the implementation, so agreement is evidence of consistency with the written policy, not of independence.

<!-- okf:generated:begin links -->
## Referenced by

* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict, sandbox: SandboxFactory) -> dict` in `application/verifier` (the source has no docstring).
<!-- okf:generated:end links -->
