---
type: Class
title: domain.models.Delay
description: 'A UML time event, ``after(14 days)`` (issue #93, ADR-0237): the transition may be taken only once the record has been in its source state this long.'
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
  sha256: 9f9a9399db3d64d6bf33d905063b93cc2e8d1a2e867e10c40255017e9da3a588
notes_baseline: 07711c4826052dc8c9990fe95792d0109d1c93381d05e12d8a31427fb653b7f8
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
A UML time event, ``after(14 days)`` (issue #93, ADR-0237): the transition may be taken only once the record has
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

* [application.scenario_run.record_steps](/symbols/application/scenario_run/record_steps.md) - What the kernel does for each (actor, action) in turn, written as scenario steps that expect exactly that.
* [domain.models.Delay.due](/symbols/domain/models/Delay.due.md) - `def due(self, elapsed: float | None) -> bool` in `domain/models`.
* [domain.models.Delay.seconds](/symbols/domain/models/Delay.seconds.md) - `def seconds(self) -> int` in `domain/models`.
* [domain.models.Delay.span](/symbols/domain/models/Delay.span.md) - The duration in words: ``2 days``, ``1 hour``.
* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
* [domain.scenarios.ScenarioStep](/symbols/domain/scenarios/ScenarioStep.md) - `class ScenarioStep(Contract)` in `domain/scenarios`.
<!-- okf:generated:end links -->
