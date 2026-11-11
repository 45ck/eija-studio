---
type: Function
title: domain.value_guards.valuations
description: One record's values for each combination of `points` over the guarded attributes, in a fixed order; a value of None is left out.
resource: repo://src/eija_studio/domain/value_guards.py#valuations
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/value_guards.py#valuations
  title: domain/value_guards.py
  hash_method: ast-v2
  sha256: e36f57440cf97671556825ac2269e6df58ba27cec48bcfcccebfcfafd25d425c
notes_baseline: d7f406e464e4053cca654497f921b50f96794f1a6abff37bf623ff312266be2e
---

# domain.value_guards.valuations

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/value_guards`](/modules/domain/value_guards.md) |
| Signature | `def valuations(model: Workflow) -> list[dict[str, Any]] \| None` |
| Code | `repo://src/eija_studio/domain/value_guards.py#valuations` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
One record's values for each combination of `points` over the guarded attributes, in a fixed order; a value of
None is left out. [{}] for a model without value guards; None when there are more than `MAX_VALUATIONS`.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.value_guards.combinations](/symbols/domain/value_guards/combinations.md) - `valuations` over these guards, grouped by attribute.
* [domain.value_guards.guards_by_attribute](/symbols/domain/value_guards/guards_by_attribute.md) - Every value guard of the model, grouped by the attribute it reads, attributes in name order.
<!-- okf:generated:end links -->
