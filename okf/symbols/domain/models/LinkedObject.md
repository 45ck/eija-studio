---
type: Class
title: domain.models.LinkedObject
description: 'The lifecycle of the object a record links to through a reference field, such as a deploy request''s `target` service (issue #93 item 4, ADR-0241): a small state machine of its own, moved only by the record''s steps (`Tra…'
resource: repo://src/eija_studio/domain/models.py#LinkedObject
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#LinkedObject
  title: domain/models.py
  hash_method: ast-sig-v1
  sha256: 4b3171580f8d8e39960b57b16df822e25e8820b98e56a46e771f0083d3b7e1f6
notes_baseline: f2f9f2f02109d3604f2be2fb4dc1a7f8293187e780897e2f02ac605d734c5686
---

# domain.models.LinkedObject

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class LinkedObject(Contract)` |
| Code | `repo://src/eija_studio/domain/models.py#LinkedObject` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
The lifecycle of the object a record links to through a reference field, such as a deploy request's `target`
service (issue #93 item 4, ADR-0241): a small state machine of its own, moved only by the record's steps
(`Transition.then`). An object in a state with no move for the event refuses the record's step; so does an unknown
object or state.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `link` | `str` | `Field(pattern=LINK)` |
| `entity` | `str` | `Field(pattern='^[A-Z][A-Za-z0-9]{0,39}$')` |
| `states` | `tuple[str, ...]` | `Field(min_length=1, max_length=8)` |
| `initial` | `str` | `Field(min_length=1, max_length=60)` |
| `moves` | `tuple[Move, ...]` | `Field(min_length=1, max_length=32)` |

## Methods

* [`closed`](/symbols/domain/models/LinkedObject.closed.md) - `def closed(self) -> LinkedObject`
* [`events`](/symbols/domain/models/LinkedObject.events.md) - `def events(self) -> set[str]`
* [`move`](/symbols/domain/models/LinkedObject.move.md) - `def move(self, event: str, state: str \| None) -> str \| None`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.models.LINK](/symbols/domain/models/LINK.md) - Constant `LINK` in `domain/models`.
* [domain.models.Move](/symbols/domain/models/Move.md) - One transition in a linked object's lifecycle: `event` moves it from `from_state` to `to_state` (ADR-0241).

## Referenced by

* [domain.models.LinkedObject.closed](/symbols/domain/models/LinkedObject.closed.md) - `def closed(self) -> LinkedObject` in `domain/models`.
* [domain.models.LinkedObject.events](/symbols/domain/models/LinkedObject.events.md) - `def events(self) -> set[str]` in `domain/models`.
* [domain.models.LinkedObject.move](/symbols/domain/models/LinkedObject.move.md) - The state `event` moves the object to from `state`, or None when it has no such move (or the state is unknown).
* [domain.models.Workflow.lifecycle](/symbols/domain/models/Workflow.lifecycle.md) - `def lifecycle(self, link: str) -> LinkedObject | None` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
