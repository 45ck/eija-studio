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
  sha256: f12db5d3d54d3c694dd8a7370f8d65061aba64fde51152fe2d6da7f8451d2f88
notes_baseline: 51226ffcc2def1501bca3f7e23fb6c58ecb2fae37823234dc8117e61313ae4a5
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
