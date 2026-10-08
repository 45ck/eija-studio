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
  sha256: 95c06725a076c12c8e5398d6ba858b03bf8895e7dabc9bbd10f4b84f40637d75
notes_baseline: e89f2354d1ea13818543f15c37620584a157dfb8f1e10fa8b9285e8c95b39a2c
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
