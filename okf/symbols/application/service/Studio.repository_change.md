---
type: Method
title: application.service.Studio.repository_change
description: Compare immutable source revisions; this grants no model or repository write authority.
resource: repo://src/eija_studio/application/service.py#Studio.repository_change
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.repository_change
  title: application/service.py
  hash_method: ast-v2
  sha256: c0638113e74a2ea64934abe0831008a9bacb5b13ea8d5eafb92566ba671ff01c
notes_baseline: fcf16d1601aa0a3fe376ed8a95368f70c5d62cc640353236ee4d54c2a53f2f02
---

# application.service.Studio.repository_change

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def repository_change(self, base: str, head: str) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.repository_change` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Compare immutable source revisions; this grants no model or repository write authority.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.repository.compare_repository_changes](/symbols/application/repository/compare_repository_changes.md) - Validate an immutable comparison request before dispatch to its read-only port.
<!-- okf:generated:end links -->
