---
type: Class
title: domain.scenarios.Then
description: 'What a step must do: move the record to `state`, or be refused with `refused` (a kernel refusal code).'
resource: repo://src/eija_studio/domain/scenarios.py#Then
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/scenarios.py#Then
  title: domain/scenarios.py
  hash_method: ast-sig-v1
  sha256: 76ad22bc117d8d81691a25d80e5d7030d174c9092248cb692d8b889ed23b45ed
notes_baseline: 940f8ad98eb47c343cc41dd995698b319afdd434979e036a674090fac50618e5
---

# domain.scenarios.Then

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/scenarios`](/modules/domain/scenarios.md) |
| Signature | `class Then(Contract)` |
| Code | `repo://src/eija_studio/domain/scenarios.py#Then` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
What a step must do: move the record to `state`, or be refused with `refused` (a kernel refusal code).
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `state` | `str \| None` | `Field(default=None, pattern=NAME)` |
| `refused` | `str \| None` | `Field(default=None, pattern='^[A-Z][A-Z0-9_:]{0,59}$')` |

## Methods

* [`one`](/symbols/domain/scenarios/Then.one.md) - `def one(self) -> Then`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.scenarios.NAME](/symbols/domain/scenarios/NAME.md) - Constant `NAME` in `domain/scenarios`.

## Referenced by

* [domain.scenarios.ScenarioStep](/symbols/domain/scenarios/ScenarioStep.md) - `class ScenarioStep(Contract)` in `domain/scenarios`.
* [domain.scenarios.Then.one](/symbols/domain/scenarios/Then.one.md) - `def one(self) -> Then` in `domain/scenarios`.
<!-- okf:generated:end links -->
