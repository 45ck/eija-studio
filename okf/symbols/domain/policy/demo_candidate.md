---
type: Function
title: domain.policy.demo_candidate
description: The pack's baseline with its first supported meaning applied.
resource: repo://src/eija_studio/domain/policy.py#demo_candidate
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#demo_candidate
  title: domain/policy.py
  hash_method: ast-v2
  sha256: 7ad86b1c80751afbd28ef6c9005a13f5a6ffb3b33718628c99df6d05d44e599b
notes_baseline: 71134c53a66f93ebde1986af2cdab5e43f89829a1d3d4f2c122a2b460c6efa8e
---

# domain.policy.demo_candidate

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def demo_candidate(pack: Pack \| None=None) -> Workflow` |
| Code | `repo://src/eija_studio/domain/policy.py#demo_candidate` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The pack's baseline with its first supported meaning applied.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.policy.apply_meaning](/symbols/domain/policy/apply_meaning.md) - The candidate a supported pack meaning produces from ``model`` (policy-checked).
* [domain.policy.baseline](/symbols/domain/policy/baseline.md) - The pack's baseline workflow.
* [domain.policy.first_supported_meaning](/symbols/domain/policy/first_supported_meaning.md) - The id of the pack's first supported meaning (the demo candidate's meaning).

## Referenced by

* [application.diagram_catalog.demo_pair](/symbols/application/diagram_catalog/demo_pair.md) - Baseline and the demo candidate: the default pack's baseline with its first supported meaning applied.
<!-- okf:generated:end links -->
