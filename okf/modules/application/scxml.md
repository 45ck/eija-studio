---
type: Module
title: application.scxml
description: The workflow state machine as a W3C SCXML statechart (ADR-0165).
resource: repo://src/eija_studio/application/scxml.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/scxml.py
  title: application/scxml.py
  hash_method: ast-api-v1
  sha256: 5a3cb70dd987944e95d873ecc91db3cdbe878ea84bf28c8e736c6cf13466257e
notes_baseline: 8176d080a1fce9f300122901ad46ad5dc21dc1bd84ac873209122a88087f95d9
---

# application.scxml

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/scxml.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
The workflow state machine as a W3C SCXML statechart (ADR-0165).

SCXML is the W3C standard for executable state machines, with a normative interpretation algorithm. Exporting the
model to it does two things. Any SCXML engine can run the state diagram, so the model is not locked to EIJA. And an
independent engine gives a second opinion on what the diagram means: `verification/scxml/differential.py` runs every
case of the app oracle (ADR-0150) on the exported chart and requires the same outcome as the kernel.

The export is a projection of one run-to-completion step of `runtime.execute`, not a second interpreter that anything
runs in production. What it keeps and what it leaves to the kernel:

* A state is an atomic `<state>`; the initial state is the chart's `initial`.
* An action is an event. A transition fires on its action's event from its source state only (`state_equals`).
* The actor is resolved by whoever sends the event, as the kernel's `UnitOfWork.actor` port does, and travels in the
  event data (`event_data`). `actor_active`, `role_current` and `actor_assigned` (when the transition has it) become
  the transition's `cond`, and an actor not in the directory sends `known` False.
* A guard over the record's values (`[amount > 500]`, ADR-0234) becomes a `cond` term over the event data too: whoever
  sends the event reads the record's values, as the kernel's `UnitOfWork.values` port does, and attaches each guarded
  attribute as `value_<name>` with `has_<name>` (False when the record has no value). The data model has already
  checked each value's type, so the chart compares without a type test.
* A time event (`after(14 days)`, ADR-0236) becomes a `cond` term over the event data as well: whoever sends the event
  reads how long the record has been in its state, as the kernel's `UnitOfWork.elapsed` port does, and attaches it as
  `elapsed` in seconds, with `has_elapsed` False when it is unknown, which is never due. It is not a delayed `<send>`: in the kernel a time
  event makes a step allowed, and an actor (usually a «timer» role) still takes it through the same checks.
* `expected_version` is a `version` variable in the datamodel, compared in the `cond` and incremented when the
  transition fires.
* Each required effect is appended, in declared order, to an `effects` list in the datamodel. Writing the audit log
  and the outbox stays with the kernel's typed adapters.
* `operation_binding` (an idempotent replay of the same operation id) is a property of the storage port, checked by the
  app's own conformance run. It is not projected.

Expressions use the Python datamodel, so the chart runs on engines with a Python datamodel. The states, transitions
and events are plain SCXML; an ECMAScript engine needs only the `cond` and `expr` strings rewritten.

Pure: no IO, no clock. The same pack and model always give the same bytes.
~~~

## Public symbols

* [`FORMAT`](/symbols/application/scxml/FORMAT.md) (constant) - no docstring
* [`NAMESPACE`](/symbols/application/scxml/NAMESPACE.md) (constant) - no docstring
* [`event_data`](/symbols/application/scxml/event_data.md) (function) - What the sender of an event attaches: the actor as the directory knows it (None if unknown), the version, the record's…
* [`guard_condition`](/symbols/application/scxml/guard_condition.md) (function) - The transition's `cond`: the actor checks of `runtime.check_actor`, its guards over record values and the version check…
* [`scxml_id`](/symbols/application/scxml/scxml_id.md) (function) - An XML/SCXML-safe id for a state or event name.
* [`to_scxml`](/symbols/application/scxml/to_scxml.md) (function) - The model as an SCXML document.

## Internal imports

* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/policy`](/modules/domain/policy.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.

## Referenced by

* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
* [application.scxml.FORMAT](/symbols/application/scxml/FORMAT.md) - Constant `FORMAT` in `application/scxml`.
* [application.scxml.NAMESPACE](/symbols/application/scxml/NAMESPACE.md) - Constant `NAMESPACE` in `application/scxml`.
* [application.scxml.event_data](/symbols/application/scxml/event_data.md) - What the sender of an event attaches: the actor as the directory knows it (None if unknown), the version, the record's value of each guarded attribute in `attr…
* [application.scxml.guard_condition](/symbols/application/scxml/guard_condition.md) - The transition's `cond`: the actor checks of `runtime.check_actor`, its guards over record values and the version check, over the event data.
* [application.scxml.scxml_id](/symbols/application/scxml/scxml_id.md) - An XML/SCXML-safe id for a state or event name.
* [application.scxml.to_scxml](/symbols/application/scxml/to_scxml.md) - The model as an SCXML document.
<!-- okf:generated:end links -->
