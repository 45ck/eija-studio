---
type: Function
title: domain.policy.baseline
description: The trusted four-state excursion workflow (Draft, Submitted, Approved, Rejected) that every Change Case starts from.
resource: repo://src/eija_studio/domain/policy.py#baseline
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#baseline
  title: domain/policy.py
  hash_method: ast-v2
  sha256: 821029d1f7e3057b4e51323b8d32473c549f214b7145bc83df7798b4af46f075
description_override: The trusted four-state excursion workflow (Draft, Submitted, Approved, Rejected) that every Change Case starts from.
notes_baseline: 61a4225c98115fc3a26eab1353aec521afc46101581d02e2acc091e40db6078e
verified:
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: 3e0cf050751c4e95a0bbbe403b3b3821f86fa5580e12b815453e07413faed137
  sources_sha256: 61a4225c98115fc3a26eab1353aec521afc46101581d02e2acc091e40db6078e
---

# domain.policy.baseline

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def baseline(pack: Pack \| None=None) -> Workflow` |
| Code | `repo://src/eija_studio/domain/policy.py#baseline` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The pack's baseline workflow.
~~~
<!-- okf:generated:end facts -->

## Notes

The pack's baseline workflow (`pack.model`); for the excursion pack Submit and Revise belong to the Teacher, Approve and Reject to the Registrar. It passes [check_policy](/symbols/domain/policy/check_policy.md); the tests assert that rather than assume it.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.diagram_catalog.demo_pair](/symbols/application/diagram_catalog/demo_pair.md) - Baseline and the demo candidate: the default pack's baseline with its first supported meaning applied.
* [domain.policy.demo_candidate](/symbols/domain/policy/demo_candidate.md) - The pack's baseline with its first supported meaning applied.
<!-- okf:generated:end links -->
