# Symbols of domain.models

# Classes

* [domain.models.Alternative](Alternative.md) - `class Alternative(Contract)` in `domain/models`.
* [domain.models.Contract](Contract.md) - Base class for every domain contract: frozen and strict, unknown fields rejected.
* [domain.models.DomainError](DomainError.md) - Error carrying a stable code and safe message; never provider secrets or arbitrary exception text.
* [domain.models.ExecuteCommand](ExecuteCommand.md) - A preview command bound to an operation id, actor, instance, action and expected version.
* [domain.models.LayoutChange](LayoutChange.md) - `class LayoutChange(Contract)` in `domain/models`.
* [domain.models.Principal](Principal.md) - A named holder of capabilities (select, edit, approve, apply); OWNER has all four, AGENT has none.
* [domain.models.Proposal](Proposal.md) - `class Proposal(Contract)` in `domain/models`.
* [domain.models.SemanticTransaction](SemanticTransaction.md) - One typed business-meaning edit: enable recommendation or set the registrar rejection source.
* [domain.models.Transition](Transition.md) - One typed edge: action, from/to state, required role, guards, required effects and forbidden effects.
* [domain.models.Workflow](Workflow.md) - Immutable typed states, transitions, roles, guards and effect declarations with a normalised semantic hash.

# Constants

* [domain.models.AGENT](AGENT.md) - Constant `AGENT` in `domain/models`.
* [domain.models.BASE_GUARDS](BASE_GUARDS.md) - Constant `BASE_GUARDS` in `domain/models`.
* [domain.models.OWNER](OWNER.md) - Constant `OWNER` in `domain/models`.

# Functions

* [domain.models.canonical](canonical.md) - Canonical JSON text (sorted keys, no whitespace, no NaN) for a value or pydantic model.
* [domain.models.fingerprint](fingerprint.md) - SHA-256 of the canonical JSON of a value: the identity primitive used for models, subjects, artifacts and command bindings.

# Methods

* [domain.models.Principal.require](Principal.require.md) - `def require(self, capability: str) -> None` in `domain/models`.
* [domain.models.Proposal.unique](Proposal.unique.md) - `def unique(self) -> Proposal` in `domain/models`.
* [domain.models.Transition.guarded](Transition.guarded.md) - `def guarded(self) -> Transition` in `domain/models`.
* [domain.models.Workflow.coherent](Workflow.coherent.md) - `def coherent(self) -> Workflow` in `domain/models`.
* [domain.models.Workflow.semantic_hash](Workflow.semantic_hash.md) - Order-insensitive fingerprint of the workflow: definition order is non-semantic, identifiers, states, roles and rules are semantic.

# Type Aliases

* [domain.models.Guard](Guard.md) - Type alias `Guard` in `domain/models`.
* [domain.models.Interpretation](Interpretation.md) - Type alias `Interpretation` in `domain/models`.
