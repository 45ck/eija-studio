---
type: Function
title: application.deployment.app_deployment
description: Where a generated app runs (`app_files` output), with `kernel` the installed eija_studio version it imports.
resource: repo://src/eija_studio/application/deployment.py#app_deployment
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/deployment.py#app_deployment
  title: application/deployment.py
  hash_method: ast-v2
  sha256: a6c7771e3b3e84bbd17ae61951d09dbe6ddeb058430a75d04963bb939e8971c8
notes_baseline: 80ecd1a74162af650f1e3dda82dfa7fa3f33ae163e379c2f5dca770168e2a53b
---

# application.deployment.app_deployment

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/deployment`](/modules/application/deployment.md) |
| Signature | `def app_deployment(files: dict[str, str], kernel: str) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/deployment.py#app_deployment` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Where a generated app runs (`app_files` output), with `kernel` the installed eija_studio version it imports.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.deployment.FORMAT](/symbols/application/deployment/FORMAT.md) - Constant `FORMAT` in `application/deployment`.
<!-- okf:generated:end links -->
