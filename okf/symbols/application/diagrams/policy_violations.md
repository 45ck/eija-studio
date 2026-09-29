---
type: Function
title: application.diagrams.policy_violations
description: 'Codes `domain.policy.check_policy` reports for `workflow` (empty: the protected policy accepts it).'
resource: repo://src/eija_studio/application/diagrams.py#policy_violations
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagrams.py#policy_violations
  title: application/diagrams.py
  hash_method: ast-v2
  sha256: 8d7ec5ea55052937a3d65de2a8a8017ae33a74721c7484b5c8daf80b9c524fed
notes_baseline: 00f9f075cf6537b84e7e32daef628da2da878394aeeca4033768c6f793897ff6
---

# application.diagrams.policy_violations

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/diagrams`](/modules/application/diagrams.md) |
| Signature | `def policy_violations(workflow: Workflow) -> tuple[str, ...]` |
| Code | `repo://src/eija_studio/application/diagrams.py#policy_violations` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Codes `domain.policy.check_policy` reports for `workflow` (empty: the protected policy accepts it).
A non-empty result means the runtime would raise POLICY_BLOCKED before doing anything else.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.policy.check_policy](/symbols/domain/policy/check_policy.md) - `def check_policy(model: Workflow) -> list[str]` in `domain/policy`.

## Referenced by

* [application.diagram_catalog.case_diagrams](/symbols/application/diagram_catalog/case_diagrams.md) - Every view for one change case as one JSON-friendly payload.
* [application.diagram_catalog.render_view](/symbols/application/diagram_catalog/render_view.md) - Generated diagram text for one view.
<!-- okf:generated:end links -->
