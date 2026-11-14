---
type: Function
title: domain.impact.model_changes
description: 'What changed outside the transitions that changes what the kernel does: how a record starts, and the lifecycles of linked objects.'
resource: repo://src/eija_studio/domain/impact.py#model_changes
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/impact.py#model_changes
  title: domain/impact.py
  hash_method: ast-v2
  sha256: 2686c971c1b94fbfd71b02398f1ea3960a9defb816d542f48e9233cfd831cb08
notes_baseline: 4d22db97d90001f5887fff0345bf58b5500f7ecd42097029f4b2af531018dd33
---

# domain.impact.model_changes

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/impact`](/modules/domain/impact.md) |
| Signature | `def model_changes(before: Workflow, after: Workflow) -> list[str]` |
| Code | `repo://src/eija_studio/domain/impact.py#model_changes` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
What changed outside the transitions that changes what the kernel does: how a record starts, and the lifecycles
of linked objects. States alone and composite states (drawing only, ADR-0240) change no step.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.models.canonical](/symbols/domain/models/canonical.md) - `def canonical(value: Any) -> str` in `domain/models`.

## Referenced by

* [domain.impact.model_impact](/symbols/domain/impact/model_impact.md) - The ripple of a change.
<!-- okf:generated:end links -->
