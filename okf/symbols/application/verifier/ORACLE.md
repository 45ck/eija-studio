---
type: Constant
title: application.verifier.ORACLE
description: Hand-authored expected role, source and target state per action, separate from the runtime's guard evaluator.
resource: repo://src/eija_studio/application/verifier.py#ORACLE
tags:
- symbol
- application
- constant
status: deprecated
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/verifier.py#ORACLE
  title: application/verifier.py
  hash_method: ast-v2
  sha256: ef38996d38b07b9177d8a14fa27c8ab48521867edd30757711f1e68c841bafc3
description_override: Hand-authored expected role, source and target state per action, separate from the runtime's guard evaluator.
notes_baseline: d5f8ab79b8e21e7d5bc10c545dd38a93ecc83432801b38b74c483905915c96be
---

# application.verifier.ORACLE

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`application/verifier`](/modules/application/verifier.md) |
| Signature | `ORACLE = {'Submit': ('Teacher', 'Draft', 'Submitted'), 'Recommend': ('Teacher', 'Submitted', 'Recommended'), 'Approve': ('Registrar', 'Recommended', 'Approved'…` |
| Code | `repo://src/eija_studio/application/verifier.py#ORACLE` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Shares authorship with the implementation, so agreement is evidence of consistency with the written policy, not of independence.

<!-- okf:generated:begin links -->
## Referenced by

* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict[str, Any], sandbox: SandboxFactory) -> dict[str, Any]` in `application/verifier`.
<!-- okf:generated:end links -->
