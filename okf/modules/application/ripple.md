---
type: Module
title: application.ripple
description: 'Ripple (ADR-0158): what one change to the state machine does to every other diagram of the same system, and the follow-on edits that would keep them in agreement.'
resource: repo://src/eija_studio/application/ripple.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/ripple.py
  title: application/ripple.py
  hash_method: ast-api-v1
  sha256: 6ea0785d0cfbf11cae3e8e3cd19807aa55d4537e3ddc44eb49a1c326cd76a2a4
notes_baseline: d6a5dd672779966af5e98c2f589c034f87c7876bc1699f6699436950f450a082
---

# application.ripple

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/ripple.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Ripple (ADR-0158): what one change to the state machine does to every other diagram of the same system, and the
follow-on edits that would keep them in agreement.

PlayIDE draws five diagrams of one system: the state machine, the class diagram, the use cases, the screens and the
components of the built app, beside the sequence diagrams that are its scenarios (ADR-0195). Only the state machine, the data model and the screens are authored; the others are
read from them (ADR-0153 to ADR-0155). So a change to the state machine ripples: a new action is a new use case and
needs a screen, a removed one leaves its screen pointing at nothing (and the app can no longer be built), a new state
is a new literal of the record's state enumeration, and the generated code changes. `ripple` computes all of it
deterministically from the two models, the screens and the two builds' files. It is a review aid: the kernel, the
policy and the conformance tests still decide.

Follow-on edits come from the plan proposer, so they are untrusted like any AI step. `check_follow_ons` re-checks each
one: a state-machine step through the policy, a screen step through the screen design check. Nothing is saved.
~~~

## Public symbols

* [`Build`](/symbols/application/ripple/Build.md) (type-alias) - no docstring
* [`FORMAT`](/symbols/application/ripple/FORMAT.md) (constant) - no docstring
* [`MAX_FOLLOW_ONS`](/symbols/application/ripple/MAX_FOLLOW_ONS.md) (constant) - no docstring
* [`check_follow_ons`](/symbols/application/ripple/check_follow_ons.md) (function) - The proposer's follow-on steps, each re-checked on its own on top of the plan: a state-machine step through the policy…
* [`enumeration`](/symbols/application/ripple/enumeration.md) (function) - The name of the record's state enumeration on the class diagram: its literals are the state machine's states.
* [`ripple`](/symbols/application/ripple/ripple.md) (function) - Every diagram's effects of going from `base` to `candidate`.

## Internal imports

* [`application/class_build`](/modules/application/class_build.md)
* [`application/data_steps`](/modules/application/data_steps.md)
* [`application/diagrams`](/modules/application/diagrams.md)
* [`application/plan`](/modules/application/plan.md)
* [`domain/data`](/modules/domain/data.md)
* [`domain/laws`](/modules/domain/laws.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/policy`](/modules/domain/policy.md)
* [`domain/screens`](/modules/domain/screens.md)
* [`domain/transactions`](/modules/domain/transactions.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.class_build](/modules/application/class_build.md) - What the built app does with each part of the class diagram (#145, ADR-0205): the record class is built and checked; the other classes and the associations are…
* [application.data_steps](/modules/application/data_steps.md) - Data-model steps in a chat plan (ADR-0202): add an attribute to a class, remove one, or make one required or optional; and the step that changes the kind of ac…
* [application.diagrams](/modules/application/diagrams.md) - Diagram models derived from the executable Workflow (ADR-0019, ADR-0023).
* [application.plan](/modules/application/plan.md) - Plan mode for the PlayIDE chat (ADR-0156): an AI proposes a change as numbered typed steps; the person accepts or rejects each one and sees what the accepted o…
* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.laws](/modules/domain/laws.md) - Typed law DSL of a domain pack: what a workflow may never do, stated as data (WBS 1.1/1.2).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.
* [domain.screens](/modules/domain/screens.md) - Screens: the user interface of a pack's app, designed against its use cases and data model (ADR-0154).
* [domain.transactions](/modules/domain/transactions.md) - Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.

## Referenced by

* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [application.ripple.Build](/symbols/application/ripple/Build.md) - Type alias `Build` in `application/ripple`.
* [application.ripple.FORMAT](/symbols/application/ripple/FORMAT.md) - Constant `FORMAT` in `application/ripple`.
* [application.ripple.MAX_FOLLOW_ONS](/symbols/application/ripple/MAX_FOLLOW_ONS.md) - Constant `MAX_FOLLOW_ONS` in `application/ripple`.
* [application.ripple.check_follow_ons](/symbols/application/ripple/check_follow_ons.md) - The proposer's follow-on steps, each re-checked on its own on top of the plan: a state-machine step through the policy (`base` with `plan` and the step), a scr…
* [application.ripple.enumeration](/symbols/application/ripple/enumeration.md) - The name of the record's state enumeration on the class diagram: its literals are the state machine's states.
* [application.ripple.ripple](/symbols/application/ripple/ripple.md) - Every diagram's effects of going from `base` to `candidate`.
<!-- okf:generated:end links -->
