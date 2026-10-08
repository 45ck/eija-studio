---
type: Constant
title: application.repository.COMMIT_OID_PATTERN
description: Constant `COMMIT_OID_PATTERN` in `application/repository`.
resource: repo://src/eija_studio/application/repository.py#COMMIT_OID_PATTERN
tags:
- symbol
- application
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/repository.py#COMMIT_OID_PATTERN
  title: application/repository.py
  hash_method: ast-v2
  sha256: e0cc9dcaf65bc6f101af5acfba016164a392dff74083e26d070ef89688289b0e
notes_baseline: 31823cee8e4048f024d0a8f57761bb022ede17fc2b3add1e4784e27bf34550e2
---

# application.repository.COMMIT_OID_PATTERN

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`application/repository`](/modules/application/repository.md) |
| Signature | `COMMIT_OID_PATTERN = '^(?:[0-9a-f]{40}\|[0-9a-f]{64})$'` |
| Code | `repo://src/eija_studio/application/repository.py#COMMIT_OID_PATTERN` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.repository.validate_change_revisions](/symbols/application/repository/validate_change_revisions.md) - Validate full object IDs before calling any configured repository port.
<!-- okf:generated:end links -->
