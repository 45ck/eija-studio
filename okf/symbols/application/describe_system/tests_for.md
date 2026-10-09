---
type: Function
title: application.describe_system.tests_for
description: 'Test cases for a new system, recorded by the kernel: the way to each end state, and the first step taken by a role that may not take it.'
resource: repo://src/eija_studio/application/describe_system.py#tests_for
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/describe_system.py#tests_for
  title: application/describe_system.py
  hash_method: ast-v2
  sha256: 1413e0a67c32200430a10edf7be7a77dbf46d677cddb28299624b69f2a05db12
notes_baseline: 51349a0c69b7374c9671e50d7630504ef3e50f4b6b7632ca04a82cbe93c36407
---

# application.describe_system.tests_for

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/describe_system`](/modules/application/describe_system.md) |
| Signature | `def tests_for(pack: Pack, record: str, model: Workflow \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/describe_system.py#tests_for` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Test cases for a new system, recorded by the kernel: the way to each end state, and the first step taken by a
role that may not take it. They pin down what the kernel does now, so a later change that alters it shows.
`model` is the model to record on (the pack's own when None).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.describe_system.describe_documents](/symbols/application/describe_system/describe_documents.md) - The documents of a new system described in `text`, checked by the kernel, and what the describer read.
<!-- okf:generated:end links -->
