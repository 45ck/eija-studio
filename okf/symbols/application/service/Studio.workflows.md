---
type: Method
title: application.service.Studio.workflows
description: Baseline and candidate of a case, for read-only projections (diagrams).
resource: repo://src/eija_studio/application/service.py#Studio.workflows
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.workflows
  title: application/service.py
  hash_method: ast-v2
  sha256: 15665eeb2cca1e7e3532790c8a054556cb21ea6a341b57885ab11f05a9e623f6
notes_baseline: 176ec1782436efe330dbbbf22dbc287a3448d88af19bd87b2ce4367c12f0294d
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
