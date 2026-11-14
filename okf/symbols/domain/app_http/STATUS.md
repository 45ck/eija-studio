---
type: Constant
title: domain.app_http.STATUS
description: Constant `STATUS` in `domain/app_http`.
resource: repo://src/eija_studio/domain/app_http.py#STATUS
tags:
- symbol
- domain
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/app_http.py#STATUS
  title: domain/app_http.py
  hash_method: ast-v2
  sha256: d217d1e2a0afce3c43ce45641af6fd167b0bd1e903f8091dae58bcd2a10e2582
notes_baseline: ec62255976799781dd0236d39316a49c91582d7e9cf2530749098bbab35de169
---

# domain.app_http.STATUS

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`domain/app_http`](/modules/domain/app_http.md) |
| Signature | `STATUS: dict[str, int] = {code: int(status) for status, (_, codes) in REFUSALS.items() for code in codes}` |
| Code | `repo://src/eija_studio/domain/app_http.py#STATUS` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.app_http.REFUSALS](/symbols/domain/app_http/REFUSALS.md) - Constant `REFUSALS` in `domain/app_http`.

## Referenced by

* [domain.app_http.status_of](/symbols/domain/app_http/status_of.md) - The status a refusal with this code is answered with; a code missing from the table is a conflict.
<!-- okf:generated:end links -->
