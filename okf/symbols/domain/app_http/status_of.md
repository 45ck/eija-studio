---
type: Function
title: domain.app_http.status_of
description: The status a refusal with this code is answered with; a code missing from the table is a conflict.
resource: repo://src/eija_studio/domain/app_http.py#status_of
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/app_http.py#status_of
  title: domain/app_http.py
  hash_method: ast-v2
  sha256: b17488e6a51ba191529a5a266fd98ad4a2b5b6bc5a3cbd1e28a1b954f50f84fb
notes_baseline: 337ad5ee666a6158fc4cd03c5318321718bdbec367465692fdb76d2f1a78ff5c
---

# domain.app_http.status_of

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/app_http`](/modules/domain/app_http.md) |
| Signature | `def status_of(code: str) -> int` |
| Code | `repo://src/eija_studio/domain/app_http.py#status_of` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The status a refusal with this code is answered with; a code missing from the table is a conflict.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.app_http.STATUS](/symbols/domain/app_http/STATUS.md) - Constant `STATUS` in `domain/app_http`.
<!-- okf:generated:end links -->
