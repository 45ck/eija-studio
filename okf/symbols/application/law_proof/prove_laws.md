---
type: Function
title: application.law_proof.prove_laws
description: Every law of the pack, judged on `model` (the pack's own by default), with the evidence for each verdict.
resource: repo://src/eija_studio/application/law_proof.py#prove_laws
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/law_proof.py#prove_laws
  title: application/law_proof.py
  hash_method: ast-v2
  sha256: 0364c50f57aee51fdd020399cf73db706fea0f08ecc12d827698e8c88644faf8
notes_baseline: d255cd047fabf9f2a7f534fbbda704d8d5cc5cdfdb34bf8c8da3b7ddc5027ebe
---

# application.law_proof.prove_laws

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/law_proof`](/modules/application/law_proof.md) |
| Signature | `def prove_laws(pack: Pack, model: Workflow \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/law_proof.py#prove_laws` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every law of the pack, judged on `model` (the pack's own by default), with the evidence for each verdict.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.law_proof.FORMAT](/symbols/application/law_proof/FORMAT.md) - Constant `FORMAT` in `application/law_proof`.
* [application.law_proof.LIMITS](/symbols/application/law_proof/LIMITS.md) - Constant `LIMITS` in `application/law_proof`.
* [domain.laws.evaluate_table](/symbols/domain/laws/evaluate_table.md) - Every violation of the applicable laws by the workflow's transition table, in law order.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.policy.check_policy](/symbols/domain/policy/check_policy.md) - Sorted, de-duplicated policy codes of ``model`` under the pack (empty means the model conforms).
<!-- okf:generated:end links -->
