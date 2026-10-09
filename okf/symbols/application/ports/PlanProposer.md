---
type: Class
title: application.ports.PlanProposer
description: 'Turns a chat request into {summary, meaning, steps: [{transaction, why}]}.'
resource: repo://src/eija_studio/application/ports.py#PlanProposer
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/ports.py#PlanProposer
  title: application/ports.py
  hash_method: ast-sig-v1
  sha256: be31c95fdddd1374cd3511a1d7e65f9c370379ecf2a8685459cd381c4d17e115
notes_baseline: 23a738b968486f8a1f3066db0c47631f83697ac983c9ab532cfdea5f4cdd882c
---

# application.ports.PlanProposer

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/ports`](/modules/application/ports.md) |
| Signature | `class PlanProposer(Protocol)` |
| Code | `repo://src/eija_studio/application/ports.py#PlanProposer` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Turns a chat request into {summary, meaning, steps: [{transaction, why}]}. Untrusted; no IO or persistence.
With `grows`, the system is one the person started, so a step may name a state, action or role it lacks (ADR-0201).
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `name` | `str` |  |
| `live` | `bool` |  |

## Protocol members

Structural interface implemented by adapters; not a class to instantiate.

* `def propose(self, request: str, model: Workflow, pack: Pack, *, grows: bool=False) -> dict[str, Any]`
* `def follow_on(self, ripple: dict[str, Any], model: Workflow, pack: Pack) -> dict[str, Any]`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.plan.example_passes](/symbols/application/plan/example_passes.md) - Whether `request`, sent to the chat as it stands, becomes a plan the policy allows on `model`.
* [application.plan.propose_plan](/symbols/application/plan/propose_plan.md) - Ask the proposer for a plan, re-check it, and preview it with every step accepted.
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service`.
<!-- okf:generated:end links -->
