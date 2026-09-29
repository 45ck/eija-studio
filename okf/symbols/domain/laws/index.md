# Symbols of domain.laws

# Classes

* [domain.laws.ActionRequiresGuard](ActionRequiresGuard.md) - Every transition performing ``action`` carries at least ``guards``.
* [domain.laws.ActionSourceIn](ActionSourceIn.md) - Every transition performing ``action`` starts in one of ``states``.
* [domain.laws.ActionTarget](ActionTarget.md) - Every transition performing ``action`` ends in ``state``.
* [domain.laws.ClosedShape](ClosedShape.md) - The workflow has exactly these states and actions and this initial state.
* [domain.laws.ForbiddenEffects](ForbiddenEffects.md) - No transition requires any of ``effects`` and every transition declares them forbidden.
* [domain.laws.OnlyRoleHolds](OnlyRoleHolds.md) - Every transition performing ``action`` is held by ``role``.
* [domain.laws.PathRequires](PathRequires.md) - Every path from the initial state to ``state`` passes through ``via`` (a sequence law).
* [domain.laws.RequiresEvidence](RequiresEvidence.md) - A review needs evidence of this kind; judged by the evidence matrix, never by the table.
* [domain.laws.RoleNeverEnters](RoleNeverEnters.md) - No transition held by ``role`` enters ``state``.
* [domain.laws.RoleNeverHolds](RoleNeverHolds.md) - No transition performing ``action`` is held by ``role``.
* [domain.laws.StateFinal](StateFinal.md) - No transition leaves ``state``.
* [domain.laws.StateOnlyVia](StateOnlyVia.md) - Every transition entering ``state`` performs one of ``actions``.
* [domain.laws.Step](Step.md) - One executed transition of a run.
* [domain.laws.Violation](Violation.md) - One broken law: its id, the code the policy reports, and the model elements involved.
* [domain.laws.When](When.md) - Condition under which a law applies.

# Constants

* [domain.laws.CODE](CODE.md) - Constant `CODE` in `domain/laws`.
* [domain.laws.LAW_ID](LAW_ID.md) - Constant `LAW_ID` in `domain/laws`.
* [domain.laws.LAW_KINDS](LAW_KINDS.md) - Constant `LAW_KINDS` in `domain/laws`.

# Functions

* [domain.laws.applies](applies.md) - `def applies(law: _Law, actions: set[str]) -> bool` in `domain/laws`.
* [domain.laws.evaluate_run](evaluate_run.md) - Violations by one executed run: per-step laws on every step, sequence laws on the whole run.
* [domain.laws.evaluate_table](evaluate_table.md) - Every violation of the applicable laws by the workflow's transition table, in law order.
* [domain.laws.reachable](reachable.md) - States reachable from ``start`` without passing through ``blocked`` (cycle-safe).

# Type Aliases

* [domain.laws.Law](Law.md) - Type alias `Law` in `domain/laws`.
* [domain.laws.Name](Name.md) - Type alias `Name` in `domain/laws`.
