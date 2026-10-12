---
type: Method
title: application.service_views.StudioViews.repository_change_file
description: Read bounded historical text and syntax; live source identity remains separate.
resource: repo://src/eija_studio/application/service_views.py#StudioViews.repository_change_file
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service_views.py#StudioViews.repository_change_file
  title: application/service_views.py
  hash_method: ast-v2
  sha256: 32ac3a079077c166fa82c3496765806cbcdcc5cd9645e1f75b7f163efbdca5b2
notes_baseline: 8477cae28fd9a0e20e3e72171883cc5bf8e63c6a48e8d1f2b17737b1ff37387a
---

# application.service_views.StudioViews.repository_change_file

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service_views`](/modules/application/service_views.md) |
| Class | [`StudioViews`](/symbols/application/service_views/StudioViews.md) |
| Signature | `def repository_change_file(self, base: str, head: str, path: str, reference: str \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service_views.py#StudioViews.repository_change_file` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Read bounded historical text and syntax; live source identity remains separate.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.repository.read_repository_change_file](/symbols/application/repository/read_repository_change_file.md) - Bound the historical selection before dispatch; absence never bypasses validation.
<!-- okf:generated:end links -->
