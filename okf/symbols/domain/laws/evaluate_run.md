---
type: Function
title: domain.laws.evaluate_run
description: 'Violations by one executed run: per-step laws on every step, sequence laws on the whole run.'
resource: repo://src/eija_studio/domain/laws.py#evaluate_run
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#evaluate_run
  title: domain/laws.py
  hash_method: ast-v2
  sha256: 0c68034c5103df1fc5a786be2183b10380a14fe63ed68c3cf6ebea980098e8b1
notes_baseline: 5b3fe9f4f0514e1aa29ec2834d89fb4e5cc45f5fb25764f55a46327528c2449a
---

# domain.laws.evaluate_run

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `def evaluate_run(laws: Sequence[_Law], initial: str, steps: Sequence[Step], actions: set[str]) -> list[Violation]` |
| Code | `repo://src/eija_studio/domain/laws.py#evaluate_run` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Violations by one executed run: per-step laws on every step, sequence laws on the whole run.

``actions`` is the action set of the workflow the run executed (for ``when`` conditions). Structural laws
(``closed_shape``, ``action_requires_guard``) and evidence requirements are about the table, not a run, and are
not judged here. Only
a step's REQUIRED effects are known, so the ``forbidden_effects`` law judges that nothing forbidden ran.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.PathRequires](/symbols/domain/laws/PathRequires.md) - Every path from the initial state to ``state`` passes through ``via`` (a sequence law).
* [domain.laws.Step](/symbols/domain/laws/Step.md) - One executed transition of a run.
* [domain.laws.Violation](/symbols/domain/laws/Violation.md) - One broken law: its id, the code the policy reports, and the model elements involved.
* [domain.laws.applies](/symbols/domain/laws/applies.md) - `def applies(law: _Law, actions: set[str]) -> bool` in `domain/laws`.
<!-- okf:generated:end links -->
