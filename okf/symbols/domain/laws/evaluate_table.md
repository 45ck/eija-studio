---
type: Function
title: domain.laws.evaluate_table
description: Every violation of the applicable laws by the workflow's transition table, in law order.
resource: repo://src/eija_studio/domain/laws.py#evaluate_table
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#evaluate_table
  title: domain/laws.py
  hash_method: ast-v2
  sha256: fc87a9035c3ea52fcd924602461f21aa3a33ea7c8c7c5d2d2bc80942c7118bf5
notes_baseline: 88c8752b2e99d5cdca61f0887f132d93e6e6564d0c0a119d954e00b6100ac9e5
---

# domain.laws.evaluate_table

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `def evaluate_table(laws: Sequence[_Law], model: Workflow) -> list[Violation]` |
| Code | `repo://src/eija_studio/domain/laws.py#evaluate_table` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every violation of the applicable laws by the workflow's transition table, in law order.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.Violation](/symbols/domain/laws/Violation.md) - One broken law: its id, the code the policy reports, and the model elements involved.
* [domain.laws.applies](/symbols/domain/laws/applies.md) - `def applies(law: _Law, actions: set[str]) -> bool` in `domain/laws`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [application.law_proof.prove_laws](/symbols/application/law_proof/prove_laws.md) - Every law of the pack, judged on `model` (the pack's own by default), with the evidence for each verdict.
* [domain.policy.law_violations](/symbols/domain/policy/law_violations.md) - `def law_violations(model: Workflow, pack: Pack | None=None) -> list[Violation]` in `domain/policy`.
<!-- okf:generated:end links -->
