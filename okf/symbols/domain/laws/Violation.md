---
type: Class
title: domain.laws.Violation
description: 'One broken law: its id, the code the policy reports, and the model elements involved.'
resource: repo://src/eija_studio/domain/laws.py#Violation
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#Violation
  title: domain/laws.py
  hash_method: ast-sig-v1
  sha256: 9fd5f24bccb475aef3a2d1f560a2b6791121205507643fe88165ed90cc1c7662
notes_baseline: 1aa5a7e776d65588caf190bad861c1c8a68e8d441fea53b4587466b5cafb9e22
---

# domain.laws.Violation

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `class Violation` |
| Code | `repo://src/eija_studio/domain/laws.py#Violation` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
One broken law: its id, the code the policy reports, and the model elements involved.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `law` | `str` |  |
| `code` | `str` |  |
| `refs` | `tuple[str, ...]` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.laws.evaluate_run](/symbols/domain/laws/evaluate_run.md) - Violations by one executed run: per-step laws on every step, sequence laws on the whole run.
* [domain.laws.evaluate_table](/symbols/domain/laws/evaluate_table.md) - Every violation of the applicable laws by the workflow's transition table, in law order.
* [domain.policy.law_violations](/symbols/domain/policy/law_violations.md) - `def law_violations(model: Workflow, pack: Pack | None=None) -> list[Violation]` in `domain/policy`.
<!-- okf:generated:end links -->
