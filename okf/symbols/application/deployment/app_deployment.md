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
  sha256: cbadbbc655e3db8e885db677fbf2a6e827bd16f9b1f8267df043f51d7dc991e1
notes_baseline: f0e8fa99d754f36debd594385ffc6fea3bf23f9b956950d2f969a636b5f72c27
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
