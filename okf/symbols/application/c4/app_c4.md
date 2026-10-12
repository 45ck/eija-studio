---
type: Function
title: application.c4.app_c4
description: Current generated-source architecture, plus explicit fixture and data-design limits.
resource: repo://src/eija_studio/application/c4.py#app_c4
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/c4.py#app_c4
  title: application/c4.py
  hash_method: ast-v2
  sha256: 1cdc736d7805d716c02a52298a0075898259ad93c17bfa49f915eb47e7803200
notes_baseline: e242e78a0071278eb51f134703098b4cbe35eed8645ab28ef4d2521073251cb2
---

# application.c4.app_c4

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/c4`](/modules/application/c4.md) |
| Signature | `def app_c4(files: dict[str, str], *, kernel_version: str='unknown') -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/c4.py#app_c4` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Current generated-source architecture, plus explicit fixture and data-design limits.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.build_subject.checked_build_subject](/symbols/application/build_subject/checked_build_subject.md) - Check archived identity, optionally binding it to the installed runtime and prior snapshot.
* [application.build_subject.snapshot_contracts](/symbols/application/build_subject/snapshot_contracts.md) - Parse the very contracts the generated application will load.
* [application.c4.FORMAT](/symbols/application/c4/FORMAT.md) - Constant `FORMAT` in `application/c4`.
* [application.c4.LIMITS](/symbols/application/c4/LIMITS.md) - Constant `LIMITS` in `application/c4`.
* [application.class_build.class_build](/symbols/application/class_build/class_build.md) - Which classes and associations the built app stores and checks, and what to consider about the rest.
* [application.components.app_components](/symbols/application/components/app_components.md) - Components, interfaces and dependencies of a generated app, read from its files (`app_files` output).
* [application.deployment.app_deployment](/symbols/application/deployment/app_deployment.md) - Where a generated app runs (`app_files` output), with `kernel` the installed eija_studio version it imports.
<!-- okf:generated:end links -->
