---
type: Function
title: application.appgen.may_start
description: 'Whether the model lets this role start a record (ADR-0231): any role when it names no initiators.'
resource: repo://src/eija_studio/application/appgen.py#may_start
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#may_start
  title: application/appgen.py
  hash_method: ast-v2
  sha256: 3b816cc49ca05da1d8dd0fad22a42b7d356d2c3a87c3e335329f7a4380032329
notes_baseline: 2da56d366637d956976b4f3496966ee61ea432b1441e745849b74c0aaf26a955
---

# application.appgen.may_start

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def may_start(model: Workflow, role: str) -> bool` |
| Code | `repo://src/eija_studio/application/appgen.py#may_start` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Whether the model lets this role start a record (ADR-0231): any role when it names no initiators.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [application.appgen.start_cases](/symbols/application/appgen/start_cases.md) - Each active fixture actor starting a record, and the kernel's answer.
<!-- okf:generated:end links -->
