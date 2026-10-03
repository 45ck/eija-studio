---
type: Module
title: domain.affordance
description: 'Affordance map (WBS 1.3): which single edits the kernel would accept, and why the others are refused.'
resource: repo://src/eija_studio/domain/affordance.py
tags:
- module
- domain
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/affordance.py
  title: domain/affordance.py
  hash_method: ast-api-v1
  sha256: 2f637e16c26ed8b6c1aa5979d3951808320673484c5d5b2b228d5e883694875a
notes_baseline: b05c1dce05a78943e8ad0cc97136e5459462e12fc699a0f832186e47afd09dae
---

# domain.affordance

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | domain |
| Code | `repo://src/eija_studio/domain/affordance.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Affordance map (WBS 1.3): which single edits the kernel would accept, and why the others are refused.

For every transition end x state, and every transition x declared role, the edit is DRY-RUN through the same
``policy.apply_transactions`` a real edit uses, so "legal" here means exactly "the edit endpoint would accept it"
and an illegal entry lists exactly the codes and refs that edit would be refused with. Nothing is written.
~~~

## Public symbols

* [`affordances`](/symbols/domain/affordance/affordances.md) (function) - Every single-step retarget and role change of ``model``, each with its dry-run verdict.
* [`dry_run`](/symbols/domain/affordance/dry_run.md) (function) - {legal, codes, refs} of applying ``tx`` to ``model`` under ``pack``, without applying it anywhere.

## Internal imports

* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/policy`](/modules/domain/policy.md)
* [`domain/transactions`](/modules/domain/transactions.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.
* [domain.transactions](/modules/domain/transactions.md) - Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.

## Referenced by

* [application.edit_proposal](/modules/application/edit_proposal.md) - A read-only offline proposal over one captured candidate; owner edits keep their existing boundary.
* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [domain.affordance.affordances](/symbols/domain/affordance/affordances.md) - Every single-step retarget and role change of ``model``, each with its dry-run verdict.
* [domain.affordance.dry_run](/symbols/domain/affordance/dry_run.md) - {legal, codes, refs} of applying ``tx`` to ``model`` under ``pack``, without applying it anywhere.
<!-- okf:generated:end links -->
