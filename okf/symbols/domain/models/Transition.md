---
type: Class
title: domain.models.Transition
description: 'One typed edge: action, from/to state, required role, guards, required effects and forbidden effects.'
resource: repo://src/eija_studio/domain/models.py#Transition
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#Transition
  title: domain/models.py
  hash_method: ast-sig-v1
  sha256: 9943be8cb40da385f94314253350665e17b5a7624de7f802b286638f8b806450
description_override: 'One typed edge: action, from/to state, required role, guards, required effects and forbidden effects.'
notes_baseline: 9188dc5c1d75a36f889dd18b62c10a22ff3089b3848eca358b1af731d2d3a58e
verified:
- by: process:claude-code
  at: '2026-11-11T22:00:00Z'
  notes_sha256: 91430b5a498dbcea88f274353a617468c979ffd042d8fbbd5059593748f2e793
  sources_sha256: 367b2b58c938cda1290f127959a44e881fafabc73d141ccfdb443fc34cb75fed
- by: process:claude-code
  at: '2026-11-12T03:00:00Z'
  notes_sha256: 7c05068e9999438812403f4c20f764e3085173b93aeb21d1a4de69dc4dacd2bb
  sources_sha256: 9188dc5c1d75a36f889dd18b62c10a22ff3089b3848eca358b1af731d2d3a58e
---

# domain.models.Transition

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class Transition(Contract)` |
| Code | `repo://src/eija_studio/domain/models.py#Transition` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `id` | `str` | `Field(pattern='^[A-Z][A-Z0-9_-]{0,63}$')` |
| `action` | `str` | `Field(min_length=1, max_length=60)` |
| `from_state` | `str` | `Field(min_length=1, max_length=60)` |
| `to_state` | `str` | `Field(min_length=1, max_length=60)` |
| `role` | `str` | `Field(min_length=1, max_length=60)` |
| `guards` | `tuple[Guard, ...]` |  |
| `required_effects` | `tuple[str, ...]` |  |
| `forbidden_effects` | `tuple[str, ...]` |  |
| `conditions` | `tuple[ValueGuard, ...]` | `Field(default=(), max_length=8)` |
| `after` | `Delay \| None` | `None` |

## Methods

* [`admits`](/symbols/domain/models/Transition.admits.md) - `def admits(self, values: dict[str, Any]) -> ValueGuard \| None`
* [`guarded`](/symbols/domain/models/Transition.guarded.md) - `def guarded(self) -> Transition`
<!-- okf:generated:end facts -->

## Notes

The validator [guarded](/symbols/domain/models/Transition.guarded.md) refuses removal of any mandatory guard, duplicate guards or effects, an effect that is both required and forbidden, and a duplicate guard over record values. `conditions` holds those value guards (`[amount ≤ 500]`, [ADR-0234](/adrs/0234-guards-over-record-values.md)); it is left out of the dump when empty, so unguarded transitions keep their bytes. `after` holds a time event (`after(2 days)`, [ADR-0237](/adrs/0237-time-events.md)) and is left out of the dump when absent. Extra fields are rejected (`extra=forbid`), which is how unknown operators fail before preview.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.models.Delay](/symbols/domain/models/Delay.md) - A UML time event, ``after(14 days)`` (issue #93, ADR-0237): the transition may be taken only once the record has been in its source state this long.
* [domain.models.Guard](/symbols/domain/models/Guard.md) - Type alias `Guard` in `domain/models`.
* [domain.models.ValueGuard](/symbols/domain/models/ValueGuard.md) - A UML guard over one of the record's values, such as ``[amount > 500]`` (issue #93, ADR-0234).

## Referenced by

* [Execution](/contexts/execution.md) - Owns Trusted fixture actor state, preview instances, command replay, committed effect intents
* [application.diagrams.CONTRACTS](/symbols/application/diagrams/CONTRACTS.md) - Constant `CONTRACTS` in `application/diagrams`.
* [application.runtime.check_actor](/symbols/application/runtime/check_actor.md) - `def check_actor(actor: dict[str, Any], transition: Transition, command: ExecuteCommand) -> None` in `application/runtime`.
* [application.runtime.check_due](/symbols/application/runtime/check_due.md) - Refuse a transition with a time event, ``after(14 days)``, before the record has been in its source state that long (ADR-0237).
* [application.runtime.check_guards](/symbols/application/runtime/check_guards.md) - Refuse a transition whose guards over the record's values do not hold (ADR-0234).
* [application.scxml.guard_condition](/symbols/application/scxml/guard_condition.md) - The transition's `cond`: the actor checks of `runtime.check_actor`, its guards over record values and the version check, over the event data.
* [application.scxml.hoisted](/symbols/application/scxml/hoisted.md) - The transitions each state or composite carries in the chart.
* [domain.impact.changed_fields](/symbols/domain/impact/changed_fields.md) - Semantic differences of one action's transition.
* [domain.impact.keyed](/symbols/domain/impact/keyed.md) - Both models' transitions keyed for comparison.
* [domain.models.Transition.admits](/symbols/domain/models/Transition.admits.md) - The first condition these record values fail, or None when the transition's conditions all hold.
* [domain.models.Transition.guarded](/symbols/domain/models/Transition.guarded.md) - `def guarded(self) -> Transition` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.models.Workflow.transition_for](/symbols/domain/models/Workflow.transition_for.md) - The transition ``action`` takes from ``state``; without a state, or when it does not leave that state, any transition it labels (they differ only in id and sou…
* [domain.policy.transition](/symbols/domain/policy/transition.md) - A transition for a declared action, with the action's declared guards and effects and the pack's forbidden effects.
* [domain.transactions.Declare](/symbols/domain/transactions/Declare.md) - Type alias `Declare` in `domain/transactions`.
<!-- okf:generated:end links -->
