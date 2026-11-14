---
type: Method
title: application.service.Studio.record
description: 'Append one event to the audit log: how a live chat call that leaves the machine is recorded (ADR-0230).'
resource: repo://src/eija_studio/application/service.py#Studio.record
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.record
  title: application/service.py
  hash_method: ast-v2
  sha256: d3d97ea02374f29985d5d48a493ed3928b2dbc2c11ebf3810408699154a4a39d
notes_baseline: d48fa115f087aa452b51b317ae7c8cf3e3b81175696edc9dd15a3d72a44ca80c
---

# application.service.Studio.record

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def record(self, kind: str, body: dict[str, Any]) -> None` |
| Code | `repo://src/eija_studio/application/service.py#Studio.record` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Append one event to the audit log: how a live chat call that leaves the machine is recorded (ADR-0230).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
