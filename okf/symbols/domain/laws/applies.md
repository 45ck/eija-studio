---
type: Function
title: domain.laws.applies
description: '`def applies(law: _Law, actions: set[str]) -> bool` in `domain/laws`.'
resource: repo://src/eija_studio/domain/laws.py#applies
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#applies
  title: domain/laws.py
  hash_method: ast-v2
  sha256: b146eb6c2b124179a5cf65adb62da8103d2b9459abc81603eb684646debf93ea
notes_baseline: 2cdd14a5816721d057513865db363c9cdf8dcbb9a98a9c21493a6bf5d72dad68
---

# domain.laws.applies

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `def applies(law: _Law, actions: set[str]) -> bool` |
| Code | `repo://src/eija_studio/domain/laws.py#applies` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.laws.evaluate_run](/symbols/domain/laws/evaluate_run.md) - Violations by one executed run: per-step laws on every step, sequence laws on the whole run.
* [domain.laws.evaluate_table](/symbols/domain/laws/evaluate_table.md) - Every violation of the applicable laws by the workflow's transition table, in law order.
<!-- okf:generated:end links -->
