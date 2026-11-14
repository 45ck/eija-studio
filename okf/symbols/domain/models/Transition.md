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
  sha256: 53db122d33dc852c55f9d355d47d8f92e8ef7dc91a7652ab6a4a739e66e6e882
description_override: 'One typed edge: action, from/to state, required role, guards, required effects and forbidden effects.'
notes_baseline: f60570af382ac190da1dd213126f92228cc2b09825ab2d524dac76c36995f933
verified:
- by: process:claude-code
  at: '2026-11-11T22:00:00Z'
  notes_sha256: 91430b5a498dbcea88f274353a617468c979ffd042d8fbbd5059593748f2e793
  sources_sha256: 367b2b58c938cda1290f127959a44e881fafabc73d141ccfdb443fc34cb75fed
- by: process:claude-code
  at: '2026-11-12T03:00:00Z'
  notes_sha256: 7c05068e9999438812403f4c20f764e3085173b93aeb21d1a4de69dc4dacd2bb
  sources_sha256: 9188dc5c1d75a36f889dd18b62c10a22ff3089b3848eca358b1af731d2d3a58e
- by: process:claude-code
  at: '2026-11-12T04:00:08Z'
  notes_sha256: 322a06cc8a6f080829242a9bf363d31558611695de61652958b7a5d1ae427a4c
  sources_sha256: f60570af382ac190da1dd213126f92228cc2b09825ab2d524dac76c36995f933
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
| `then` | `tuple[LinkedStep, ...]` | `Field(default=(), max_length=2)` |

## Methods

* [`admits`](/symbols/domain/models/Transition.admits.md) - `def admits(self, values: dict[str, Any]) -> ValueGuard \| None`
* [`guarded`](/symbols/domain/models/Transition.guarded.md) - `def guarded(self) -> Transition`
<!-- okf:generated:end facts -->

## Notes

The validator [guarded](/symbols/domain/models/Transition.guarded.md) refuses removal of any mandatory guard, duplicate guards or effects, an effect that is both required and forbidden, and a duplicate guard over record values. `conditions` holds those value guards (`[amount ≤ 500]`, [ADR-0234](/adrs/0234-guards-over-record-values.md)); it is left out of the dump when empty, so unguarded transitions keep their bytes. `after` holds a time event (`after(2 days)`, [ADR-0237](/adrs/0237-time-events.md)) and is left out of the dump when absent. `then` holds at most two steps on linked objects on different links (`target.lock`, [ADR-0241](/adrs/0241-actions-on-linked-objects.md)) and is left out when empty. Extra fields are rejected (`extra=forbid`), which is how unknown operators fail before preview.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.models.Delay](/symbols/domain/models/Delay.md) - A UML time event, ``after(14 days)`` (issue #93, ADR-0237): the transition may be taken only once the record has been in its source state this long.
* [domain.models.Guard](/symbols/domain/models/Guard.md) - Type alias `Guard` in `domain/models`.
* [domain.models.LinkedStep](/symbols/domain/models/LinkedStep.md) - What a transition does to an object the record links to, written ``target.lock`` (issue #93 item 4, ADR-0241): the object named by the record's `link` field ta…
* [domain.models.ValueGuard](/symbols/domain/models/ValueGuard.md) - A UML guard over one of the record's values, such as ``[amount > 500]`` (issue #93, ADR-0234).

## Referenced by

* [Execution](/contexts/execution.md) - Owns Trusted fixture actor state, preview instances, command replay, committed effect intents
* [application.access.meeting](/symbols/application/access/meeting.md) - A record's values that meet every guard over values of these transitions (ADR-0234): {} when they have none, None when no values meet them all.
* [application.diagrams.CONTRACTS](/symbols/application/diagrams/CONTRACTS.md) - Constant `CONTRACTS` in `application/diagrams`.
* [application.runtime.check_actor](/symbols/application/runtime/check_actor.md) - `def check_actor(actor: dict[str, Any], transition: Transition, command: ExecuteCommand) -> None` in `application/runtime`.
* [application.runtime.check_due](/symbols/application/runtime/check_due.md) - Refuse a transition with a time event, ``after(14 days)``, before the record has been in its source state that long (ADR-0237).
* [application.runtime.check_guards](/symbols/application/runtime/check_guards.md) - Refuse a transition whose guards over the record's values do not hold (ADR-0234).
* [application.runtime.check_linked](/symbols/application/runtime/check_linked.md) - The moves a transition makes on the objects the record links to, given each object's state (ADR-0241).
* [application.scxml.guard_condition](/symbols/application/scxml/guard_condition.md) - The transition's `cond`: the actor checks of `runtime.check_actor`, its guards over record values and the version check, over the event data.
* [application.scxml.hoisted](/symbols/application/scxml/hoisted.md) - The transitions each state or composite carries in the chart.
* [domain.impact.changed_fields](/symbols/domain/impact/changed_fields.md) - Semantic differences of one action's transition.
* [domain.impact.keyed](/symbols/domain/impact/keyed.md) - Both models' transitions keyed for comparison.
* [domain.linked.admitting](/symbols/domain/linked/admitting.md) - The first combination of states (as `combinations` orders them) from which `transition` can move every object it names; `{}` when it moves none, None when no c…
* [domain.linked.advance](/symbols/domain/linked/advance.md) - The objects' states after `transition` (unchanged when it moves none), or None when one of its moves is not possible from their states.
* [domain.linked.combinations](/symbols/domain/linked/combinations.md) - Every combination of states of the objects `transition` moves, one dict per combination; `[{}]` when it moves none.
* [domain.models.Transition.admits](/symbols/domain/models/Transition.admits.md) - The first condition these record values fail, or None when the transition's conditions all hold.
* [domain.models.Transition.guarded](/symbols/domain/models/Transition.guarded.md) - `def guarded(self) -> Transition` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.models.Workflow.transition_for](/symbols/domain/models/Workflow.transition_for.md) - The transition ``action`` takes from ``state``; without a state, or when it does not leave that state, any transition it labels (they differ only in id and sou…
* [domain.policy.transition](/symbols/domain/policy/transition.md) - A transition for a declared action, with the action's declared guards and effects and the pack's forbidden effects.
* [domain.transactions.Declare](/symbols/domain/transactions/Declare.md) - Type alias `Declare` in `domain/transactions`.
<!-- okf:generated:end links -->
