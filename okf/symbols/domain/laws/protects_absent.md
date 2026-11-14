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
  sha256: 894c1d601e53eb12956d2de0ae3d5d282ab30feceb42dc792561a736c8ffd193
notes_baseline: 086cc01ac2168a6fde1457c30e72dc2fae86d0b60b16f320137df2c15003e64d
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

* [domain.laws.PROTECTING](/symbols/domain/laws/PROTECTING.md) - Constant `PROTECTING` in `domain/laws`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
