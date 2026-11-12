# Symbols of domain.models

# Classes

* [domain.models.Alternative](Alternative.md) - `class Alternative(Contract)` in `domain/models`.
* [domain.models.Composite](Composite.md) - A UML composite state (issue #93 item 3, ADR-0240): a named group of states, or of other composites, with the child a transition into the group enters first.
* [domain.models.Contract](Contract.md) - Base class for every domain contract: frozen and strict, unknown fields rejected.
* [domain.models.Delay](Delay.md) - A UML time event, ``after(14 days)`` (issue #93, ADR-0237): the transition may be taken only once the record has been in its source state this long.
* [domain.models.DomainError](DomainError.md) - Error carrying a stable code and safe message; never provider secrets or arbitrary exception text.
* [domain.models.ExecuteCommand](ExecuteCommand.md) - A preview command bound to an operation id, actor, instance, action and expected version.
* [domain.models.LayoutChange](LayoutChange.md) - `class LayoutChange(Contract)` in `domain/models`.
* [domain.models.LinkedObject](LinkedObject.md) - The lifecycle of the object a record links to through a reference field, such as a deploy request's `target` service (issue #93 item 4, ADR-0241): a small state machine of its own, moved only by the record's steps (`Tra…
* [domain.models.LinkedStep](LinkedStep.md) - What a transition does to an object the record links to, written ``target.lock`` (issue #93 item 4, ADR-0241): the object named by the record's `link` field takes `event` in its own lifecycle, in the same step.
* [domain.models.Move](Move.md) - One transition in a linked object's lifecycle: `event` moves it from `from_state` to `to_state` (ADR-0241).
* [domain.models.Principal](Principal.md) - A named holder of capabilities (select, edit, approve, apply); OWNER has all four, AGENT has none.
* [domain.models.Proposal](Proposal.md) - `class Proposal(Contract)` in `domain/models`.
* [domain.models.Receive](Receive.md) - A signal another workflow of the system sends that starts a record here (issue #93 item 5, ADR-0242): the signal effect `signal` declared by the pack `sender`.
* [domain.models.SemanticTransaction](SemanticTransaction.md) - One typed business-meaning edit: enable recommendation or set the registrar rejection source.
* [domain.models.Transition](Transition.md) - One typed edge: action, from/to state, required role, guards, required effects and forbidden effects.
* [domain.models.ValueGuard](ValueGuard.md) - A UML guard over one of the record's values, such as ``[amount > 500]`` (issue #93, ADR-0234).
* [domain.models.Workflow](Workflow.md) - Immutable typed states, transitions, roles, guards and effect declarations with a normalised semantic hash.

# Constants

* [domain.models.AGENT](AGENT.md) - Constant `AGENT` in `domain/models`.
* [domain.models.BASE_GUARDS](BASE_GUARDS.md) - Constant `BASE_GUARDS` in `domain/models`.
* [domain.models.LINK](LINK.md) - Constant `LINK` in `domain/models`.
* [domain.models.MEANING_ID](MEANING_ID.md) - Constant `MEANING_ID` in `domain/models`.
* [domain.models.OWNER](OWNER.md) - Constant `OWNER` in `domain/models`.
* [domain.models.SECONDS](SECONDS.md) - Constant `SECONDS` in `domain/models`.
* [domain.models.SYMBOLS](SYMBOLS.md) - Constant `SYMBOLS` in `domain/models`.

# Functions

* [domain.models.canonical](canonical.md) - Canonical JSON text (sorted keys, no whitespace, no NaN) for a value or pydantic model.
* [domain.models.fingerprint](fingerprint.md) - SHA-256 of the canonical JSON of a value: the identity primitive used for models, subjects, artifacts and command bindings.
* [domain.models.guard_keys](guard_keys.md) - Value guards as a set compared by their JSON, as the semantic hash compares them.
* [domain.models.iso_date](iso_date.md) - The date a YYYY-MM-DD string names, or None.

# Methods

* [domain.models.Delay.due](Delay.due.md) - `def due(self, elapsed: float | None) -> bool` in `domain/models`.
* [domain.models.Delay.seconds](Delay.seconds.md) - `def seconds(self) -> int` in `domain/models`.
* [domain.models.Delay.span](Delay.span.md) - The duration in words: ``2 days``, ``1 hour``.
* [domain.models.LinkedObject.closed](LinkedObject.closed.md) - `def closed(self) -> LinkedObject` in `domain/models`.
* [domain.models.LinkedObject.events](LinkedObject.events.md) - `def events(self) -> set[str]` in `domain/models`.
* [domain.models.LinkedObject.move](LinkedObject.move.md) - The state `event` moves the object to from `state`, or None when it has no such move (or the state is unknown).
* [domain.models.Principal.require](Principal.require.md) - `def require(self, capability: str) -> None` in `domain/models`.
* [domain.models.Proposal.unique](Proposal.unique.md) - `def unique(self) -> Proposal` in `domain/models`.
* [domain.models.Transition.admits](Transition.admits.md) - The first condition these record values fail, or None when the transition's conditions all hold.
* [domain.models.Transition.guarded](Transition.guarded.md) - `def guarded(self) -> Transition` in `domain/models`.
* [domain.models.ValueGuard.comparable](ValueGuard.comparable.md) - `def comparable(self) -> ValueGuard` in `domain/models`.
* [domain.models.ValueGuard.holds](ValueGuard.holds.md) - `def holds(self, values: dict[str, Any]) -> bool` in `domain/models`.
* [domain.models.Workflow.ancestors](Workflow.ancestors.md) - The composites holding a state or composite, innermost first.
* [domain.models.Workflow.coherent](Workflow.coherent.md) - `def coherent(self) -> Workflow` in `domain/models`.
* [domain.models.Workflow.composite](Workflow.composite.md) - `def composite(self, name: str) -> Composite | None` in `domain/models`.
* [domain.models.Workflow.entry](Workflow.entry.md) - The plain state a transition into `name` enters: a composite's initial child, followed down.
* [domain.models.Workflow.leaves](Workflow.leaves.md) - The plain states inside a composite, in model order; a plain state is its own only leaf.
* [domain.models.Workflow.lifecycle](Workflow.lifecycle.md) - `def lifecycle(self, link: str) -> LinkedObject | None` in `domain/models`.
* [domain.models.Workflow.longest_wait](Workflow.longest_wait.md) - The longest time event on any transition, in seconds; 0 when the model has none (ADR-0237).
* [domain.models.Workflow.parent](Workflow.parent.md) - The composite that directly holds a state or composite, or None at the top level.
* [domain.models.Workflow.receiving](Workflow.receiving.md) - The declaration that `signal` from `sender` starts a record here, if there is one (ADR-0242).
* [domain.models.Workflow.semantic_hash](Workflow.semantic_hash.md) - Order-insensitive fingerprint of the workflow: definition order is non-semantic, identifiers, states, roles and rules are semantic.
* [domain.models.Workflow.sources](Workflow.sources.md) - The states ``action`` leaves, in model order.
* [domain.models.Workflow.transition_for](Workflow.transition_for.md) - The transition ``action`` takes from ``state``; without a state, or when it does not leave that state, any transition it labels (they differ only in id and source, ADR-0232).

# Type Aliases

* [domain.models.Comparison](Comparison.md) - Type alias `Comparison` in `domain/models`.
* [domain.models.Guard](Guard.md) - Type alias `Guard` in `domain/models`.
* [domain.models.Interpretation](Interpretation.md) - Type alias `Interpretation` in `domain/models`.
* [domain.models.JsonInt](JsonInt.md) - Type alias `JsonInt` in `domain/models`.
* [domain.models.TimeUnit](TimeUnit.md) - Type alias `TimeUnit` in `domain/models`.
