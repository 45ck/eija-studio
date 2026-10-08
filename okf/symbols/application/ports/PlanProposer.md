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
  sha256: 792d36912e1e5b3454c5f962ebe5652d198e460f99bfe738880666e5dfa8499f
notes_baseline: b300d1274dbaf7430aded666bb18f5d6d79370fb3e0b0654252180d8045e24b4
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
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `name` | `str` |  |
| `live` | `bool` |  |

## Protocol members

Structural interface implemented by adapters; not a class to instantiate.

* `def propose(self, request: str, model: Workflow, pack: Pack) -> dict[str, Any]`
* `def follow_on(self, ripple: dict[str, Any], model: Workflow, pack: Pack) -> dict[str, Any]`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.plan.propose_plan](/symbols/application/plan/propose_plan.md) - Ask the proposer for a plan, re-check it, and preview it with every step accepted.
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service`.
<!-- okf:generated:end links -->
