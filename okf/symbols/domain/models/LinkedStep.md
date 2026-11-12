---
type: Class
title: domain.models.LinkedStep
description: 'What a transition does to an object the record links to, written ``target.lock`` (issue #93 item 4, ADR-0241): the object named by the record''s `link` field takes `event` in its own lifecycle, in the same step.'
resource: repo://src/eija_studio/domain/models.py#LinkedStep
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#LinkedStep
  title: domain/models.py
  hash_method: ast-sig-v1
  sha256: 3e07d73046fae90194ac1017f7a54cc870803b75ab5c998cb4202ec24c391c88
notes_baseline: eeae4305a317bb62824d7111409b4bcaaf025fa6d7be7c579c656fdda343eb9b
---

# domain.models.LinkedStep

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class LinkedStep(Contract)` |
| Code | `repo://src/eija_studio/domain/models.py#LinkedStep` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
What a transition does to an object the record links to, written ``target.lock`` (issue #93 item 4, ADR-0241): the
object named by the record's `link` field takes `event` in its own lifecycle, in the same step.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `link` | `str` | `Field(pattern=LINK)` |
| `event` | `str` | `Field(pattern='^[a-z][a-zA-Z0-9]{0,39}$')` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.models.LINK](/symbols/domain/models/LINK.md) - Constant `LINK` in `domain/models`.

## Referenced by

* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
