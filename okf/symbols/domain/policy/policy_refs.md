---
type: Function
title: domain.policy.policy_refs
description: The laws and model elements a refusal points at (``law:<id>``, ``transition:<id>``, ``state:<id>``), sorted.
resource: repo://src/eija_studio/domain/policy.py#policy_refs
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#policy_refs
  title: domain/policy.py
  hash_method: ast-v2
  sha256: 0c13d0862f0696a8b32595094221f1a83f7aa6174f8b60ef5835d2868a3c8ccf
notes_baseline: 0aa4d54548a51d4e34e5fcc7074be31b82d03c23661777b941b176b86b52023a
---

# domain.policy.policy_refs

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def policy_refs(model: Workflow, pack: Pack \| None=None) -> list[str]` |
| Code | `repo://src/eija_studio/domain/policy.py#policy_refs` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The laws and model elements a refusal points at (``law:<id>``, ``transition:<id>``, ``state:<id>``), sorted.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.policy.law_violations](/symbols/domain/policy/law_violations.md) - `def law_violations(model: Workflow, pack: Pack | None=None) -> list[Violation]` in `domain/policy`.

## Referenced by

* [domain.policy.ensure_policy](/symbols/domain/policy/ensure_policy.md) - `def ensure_policy(model: Workflow, pack: Pack | None=None) -> None` in `domain/policy`.
<!-- okf:generated:end links -->
