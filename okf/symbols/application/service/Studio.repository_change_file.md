---
type: Method
title: application.service.Studio.repository_change_file
description: Read bounded historical text and syntax; live source identity remains separate.
resource: repo://src/eija_studio/application/service.py#Studio.repository_change_file
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.repository_change_file
  title: application/service.py
  hash_method: ast-v2
  sha256: 32ac3a079077c166fa82c3496765806cbcdcc5cd9645e1f75b7f163efbdca5b2
notes_baseline: 3ebd532bacf7a1255b922677b12469c09cccbe1200f6be5d91566038415de61a
---

# application.service.Studio.repository_change_file

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def repository_change_file(self, base: str, head: str, path: str, reference: str \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.repository_change_file` |
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
