---
type: Module
title: domain.laws
description: 'Typed law DSL of a domain pack: what a workflow may never do, stated as data (WBS 1.1/1.2).'
resource: repo://src/eija_studio/domain/laws.py
tags:
- module
- domain
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py
  title: domain/laws.py
  hash_method: ast-api-v1
  sha256: 3b6790cf48320e851fafa1ec44c57f02cdd739312cff69fc4554ba453898a775
notes_baseline: da85625c81c5b015d58d3e0889e960981185132f878e5ea7e79b52a0c9467bfb
---

# domain.laws

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | domain |
| Code | `repo://src/eija_studio/domain/laws.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Typed law DSL of a domain pack: what a workflow may never do, stated as data (WBS 1.1/1.2).

A law is a small typed record (a discriminated union on ``kind``); its ``code`` is the error code the policy
reports when the law is violated, and its ``id`` is the stable reference a refusal points at (``law:<id>``).
``evaluate_table`` judges a workflow's transition table; ``evaluate_run`` judges one executed run (a sequence
of steps), which is where sequence laws such as ``path_requires`` bite at runtime.

Nothing here names a domain: every state, role, action and effect comes from the pack.
~~~

## Public symbols

* [`ActionRequiresGuard`](/symbols/domain/laws/ActionRequiresGuard.md) (class) - Every transition performing ``action`` carries at least ``guards``.
* [`ActionSourceIn`](/symbols/domain/laws/ActionSourceIn.md) (class) - Every transition performing ``action`` starts in one of ``states``.
* [`ActionTarget`](/symbols/domain/laws/ActionTarget.md) (class) - Every transition performing ``action`` ends in ``state``.
* [`CODE`](/symbols/domain/laws/CODE.md) (constant) - no docstring
* [`ClosedShape`](/symbols/domain/laws/ClosedShape.md) (class) - The workflow has exactly these states and actions and this initial state.
* [`ForbiddenEffects`](/symbols/domain/laws/ForbiddenEffects.md) (class) - No transition requires any of ``effects`` and every transition declares them forbidden.
* [`LAW_ID`](/symbols/domain/laws/LAW_ID.md) (constant) - no docstring
* [`LAW_KINDS`](/symbols/domain/laws/LAW_KINDS.md) (constant) - no docstring
* [`Law`](/symbols/domain/laws/Law.md) (type-alias) - no docstring
* [`Name`](/symbols/domain/laws/Name.md) (type-alias) - no docstring
* [`OnlyRoleHolds`](/symbols/domain/laws/OnlyRoleHolds.md) (class) - Every transition performing ``action`` is held by ``role``.
* [`PathRequires`](/symbols/domain/laws/PathRequires.md) (class) - Every path from the initial state to ``state`` passes through ``via`` (a sequence law).
* [`RequiresEvidence`](/symbols/domain/laws/RequiresEvidence.md) (class) - A review needs evidence of this kind; judged by the evidence matrix, never by the table.
* [`RoleNeverEnters`](/symbols/domain/laws/RoleNeverEnters.md) (class) - No transition held by ``role`` enters ``state``.
* [`RoleNeverHolds`](/symbols/domain/laws/RoleNeverHolds.md) (class) - No transition performing ``action`` is held by ``role``.
* [`StateFinal`](/symbols/domain/laws/StateFinal.md) (class) - No transition leaves ``state``.
* [`StateOnlyVia`](/symbols/domain/laws/StateOnlyVia.md) (class) - Every transition entering ``state`` performs one of ``actions``.
* [`Step`](/symbols/domain/laws/Step.md) (class) - One executed transition of a run.
* [`Violation`](/symbols/domain/laws/Violation.md) (class) - One broken law: its id, the code the policy reports, and the model elements involved.
* [`When`](/symbols/domain/laws/When.md) (class) - Condition under which a law applies.
* [`applies`](/symbols/domain/laws/applies.md) (function) - no docstring
* [`evaluate_run`](/symbols/domain/laws/evaluate_run.md) (function) - Violations by one executed run: per-step laws on every step, sequence laws on the whole run.
* [`evaluate_table`](/symbols/domain/laws/evaluate_table.md) (function) - Every violation of the applicable laws by the workflow's transition table, in law order.
* [`reachable`](/symbols/domain/laws/reachable.md) (function) - States reachable from ``start`` without passing through ``blocked`` (cycle-safe).

## Internal imports

* [`domain/models`](/modules/domain/models.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).

## Referenced by

* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.
* [domain.laws.ActionRequiresGuard](/symbols/domain/laws/ActionRequiresGuard.md) - Every transition performing ``action`` carries at least ``guards``.
* [domain.laws.ActionSourceIn](/symbols/domain/laws/ActionSourceIn.md) - Every transition performing ``action`` starts in one of ``states``.
* [domain.laws.ActionTarget](/symbols/domain/laws/ActionTarget.md) - Every transition performing ``action`` ends in ``state``.
* [domain.laws.CODE](/symbols/domain/laws/CODE.md) - Constant `CODE` in `domain/laws`.
* [domain.laws.ClosedShape](/symbols/domain/laws/ClosedShape.md) - The workflow has exactly these states and actions and this initial state.
* [domain.laws.ForbiddenEffects](/symbols/domain/laws/ForbiddenEffects.md) - No transition requires any of ``effects`` and every transition declares them forbidden.
* [domain.laws.LAW_ID](/symbols/domain/laws/LAW_ID.md) - Constant `LAW_ID` in `domain/laws`.
* [domain.laws.LAW_KINDS](/symbols/domain/laws/LAW_KINDS.md) - Constant `LAW_KINDS` in `domain/laws`.
* [domain.laws.Law](/symbols/domain/laws/Law.md) - Type alias `Law` in `domain/laws`.
* [domain.laws.Name](/symbols/domain/laws/Name.md) - Type alias `Name` in `domain/laws`.
* [domain.laws.OnlyRoleHolds](/symbols/domain/laws/OnlyRoleHolds.md) - Every transition performing ``action`` is held by ``role``.
* [domain.laws.PathRequires](/symbols/domain/laws/PathRequires.md) - Every path from the initial state to ``state`` passes through ``via`` (a sequence law).
* [domain.laws.RequiresEvidence](/symbols/domain/laws/RequiresEvidence.md) - A review needs evidence of this kind; judged by the evidence matrix, never by the table.
* [domain.laws.RoleNeverEnters](/symbols/domain/laws/RoleNeverEnters.md) - No transition held by ``role`` enters ``state``.
* [domain.laws.RoleNeverHolds](/symbols/domain/laws/RoleNeverHolds.md) - No transition performing ``action`` is held by ``role``.
* [domain.laws.StateFinal](/symbols/domain/laws/StateFinal.md) - No transition leaves ``state``.
* [domain.laws.StateOnlyVia](/symbols/domain/laws/StateOnlyVia.md) - Every transition entering ``state`` performs one of ``actions``.
* [domain.laws.Step](/symbols/domain/laws/Step.md) - One executed transition of a run.
* [domain.laws.Violation](/symbols/domain/laws/Violation.md) - One broken law: its id, the code the policy reports, and the model elements involved.
* [domain.laws.When](/symbols/domain/laws/When.md) - Condition under which a law applies.
* [domain.laws.applies](/symbols/domain/laws/applies.md) - `def applies(law: _Law, actions: set[str]) -> bool` in `domain/laws`.
* [domain.laws.evaluate_run](/symbols/domain/laws/evaluate_run.md) - Violations by one executed run: per-step laws on every step, sequence laws on the whole run.
* [domain.laws.evaluate_table](/symbols/domain/laws/evaluate_table.md) - Every violation of the applicable laws by the workflow's transition table, in law order.
* [domain.laws.reachable](/symbols/domain/laws/reachable.md) - States reachable from ``start`` without passing through ``blocked`` (cycle-safe).
<!-- okf:generated:end links -->
