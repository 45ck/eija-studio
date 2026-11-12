---
type: Class
title: domain.models.Delay
description: 'A UML time event, ``after(14 days)`` (issue #93, ADR-0236): the transition may be taken only once the record has been in its source state this long.'
resource: repo://src/eija_studio/domain/models.py#Delay
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#Delay
  title: domain/models.py
  hash_method: ast-sig-v1
  sha256: 189a7a2bef70395d9dd28fb60bec222bbaccebefbe0772c7ca4aba1c7da89177
notes_baseline: 6a2eef8c186b1273cf163c3a5c45715028d04ed9fe0c164ada25083c0190ba4e
---

# domain.models.Delay

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class Delay(Contract)` |
| Code | `repo://src/eija_studio/domain/models.py#Delay` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
A UML time event, ``after(14 days)`` (issue #93, ADR-0236): the transition may be taken only once the record has
been in its source state this long. Time is measured from when the record entered that state, which every
committed step does, a step back into the same state included. An unknown entry time never counts as due.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `amount` | `StrictInt` | `Field(ge=1, le=10000)` |
| `unit` | `TimeUnit` |  |

## Methods

* [`due`](/symbols/domain/models/Delay.due.md) - `def due(self, elapsed: float \| None) -> bool`
* [`seconds`](/symbols/domain/models/Delay.seconds.md) - `def seconds(self) -> int`
* [`span`](/symbols/domain/models/Delay.span.md) - `def span(self) -> str`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.models.TimeUnit](/symbols/domain/models/TimeUnit.md) - Type alias `TimeUnit` in `domain/models`.

## Referenced by

* [domain.models.Delay.due](/symbols/domain/models/Delay.due.md) - `def due(self, elapsed: float | None) -> bool` in `domain/models`.
* [domain.models.Delay.seconds](/symbols/domain/models/Delay.seconds.md) - `def seconds(self) -> int` in `domain/models`.
* [domain.models.Delay.span](/symbols/domain/models/Delay.span.md) - The duration in words: ``2 days``, ``1 hour``.
* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
* [domain.scenarios.ScenarioStep](/symbols/domain/scenarios/ScenarioStep.md) - `class ScenarioStep(Contract)` in `domain/scenarios`.
<!-- okf:generated:end links -->
