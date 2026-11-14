---
type: Function
title: domain.laws.protects_absent
description: 'Whether ``law`` protects a state the model does not have: the law is broken, never vacuously kept.'
resource: repo://src/eija_studio/domain/laws.py#protects_absent
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#protects_absent
  title: domain/laws.py
  hash_method: ast-v2
  sha256: 543f93ee3c47c4527e6b1486022e1f001a56e344a68439d97b38fef4307e7fcf
notes_baseline: 9c13cf5c9191b0facb79e87b0c19ad17f3ef126154eaf46bc33a6393797d7e00
---

# domain.laws.protects_absent

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `def protects_absent(law: _Law, model: Workflow) -> bool` |
| Code | `repo://src/eija_studio/domain/laws.py#protects_absent` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Whether ``law`` protects a state the model does not have: the law is broken, never vacuously kept.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.protected](/symbols/domain/laws/protected.md) - The one state ``law`` protects, if it is a law of that kind.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
