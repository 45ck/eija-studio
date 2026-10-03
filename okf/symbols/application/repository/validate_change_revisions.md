---
type: Function
title: application.repository.validate_change_revisions
description: Validate full object IDs before calling any configured repository port.
resource: repo://src/eija_studio/application/repository.py#validate_change_revisions
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/repository.py#validate_change_revisions
  title: application/repository.py
  hash_method: ast-v2
  sha256: e0b81421aa4bc3b564c3ae8377b7e0c83d8f55746ea08359cf21b49826384885
notes_baseline: 399921f2c2887898e1a63df807802353110272eff98e996adde287830fab823f
---

# application.repository.validate_change_revisions

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/repository`](/modules/application/repository.md) |
| Signature | `def validate_change_revisions(base: str, head: str) -> None` |
| Code | `repo://src/eija_studio/application/repository.py#validate_change_revisions` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Validate full object IDs before calling any configured repository port.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.repository.COMMIT_OID_PATTERN](/symbols/application/repository/COMMIT_OID_PATTERN.md) - Constant `COMMIT_OID_PATTERN` in `application/repository`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.

## Referenced by

* [application.repository.compare_repository_changes](/symbols/application/repository/compare_repository_changes.md) - Validate an immutable comparison request before dispatch to its read-only port.
* [application.repository.read_repository_change_file](/symbols/application/repository/read_repository_change_file.md) - Bound the historical selection before dispatch; absence never bypasses validation.
<!-- okf:generated:end links -->
