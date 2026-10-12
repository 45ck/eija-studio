---
type: Method
title: application.service.Studio.workflows
description: Baseline and candidate of a case, for read-only projections (diagrams).
resource: repo://src/eija_studio/application/service.py#Studio.workflows
tags:
- symbol
- application
- method
status: deprecated
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.workflows
  title: application/service.py
  hash_method: ast-v2
  sha256: 082a8f25faaa3f24ce7f34cf93bc7f5d06660c4e434e51661b2504757a23c2ac
notes_baseline: 086c1f9ef49faa8fe20d9a8347e126a96190f2bc2c3374a77fc7e2910c71132b
---

# application.service.Studio.workflows

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def workflows(self, case_id: str) -> tuple[Workflow, Workflow \| None]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.workflows` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Baseline and candidate of a case, for read-only projections (diagrams). No authority, no writes.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
