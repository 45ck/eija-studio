---
type: Function
title: application.repository.compare_repository_changes
description: Validate an immutable comparison request before dispatch to its read-only port.
resource: repo://src/eija_studio/application/repository.py#compare_repository_changes
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/repository.py#compare_repository_changes
  title: application/repository.py
  hash_method: ast-v2
  sha256: 875b1147cfcb74a7655df556c787b68cb141de95132b2f57cf48bb14d2e14b12
notes_baseline: b2c02fb366c551ad8c827b9c3adea9bc8b58481a8ce0ec166cad846a9a5a312b
---

# application.repository.compare_repository_changes

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/repository`](/modules/application/repository.md) |
| Signature | `def compare_repository_changes(source: RepositoryChangeSource \| None, base: str, head: str) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/repository.py#compare_repository_changes` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Validate an immutable comparison request before dispatch to its read-only port.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.repository.RepositoryChangeSource](/symbols/application/repository/RepositoryChangeSource.md) - Immutable, read-only facts for an explicit pair in one configured repository.
* [application.repository.unconfigured_repository_changes](/symbols/application/repository/unconfigured_repository_changes.md) - No comparison connection is not a successful empty code change.
* [application.repository.validate_change_revisions](/symbols/application/repository/validate_change_revisions.md) - Validate full object IDs before calling any configured repository port.

## Referenced by

* [application.service.Studio.repository_change](/symbols/application/service/Studio.repository_change.md) - Compare immutable source revisions; this grants no model or repository write authority.
<!-- okf:generated:end links -->
