# Symbols of domain.transactions

# Classes

* [domain.transactions.AddState](AddState.md) - `class AddState(Contract)` in `domain/transactions`.
* [domain.transactions.AddTransition](AddTransition.md) - A transition performing a declared action; its guards and effects are the action's declared ones.
* [domain.transactions.RemoveState](RemoveState.md) - `class RemoveState(Contract)` in `domain/transactions`.
* [domain.transactions.RemoveTransition](RemoveTransition.md) - `class RemoveTransition(Contract)` in `domain/transactions`.
* [domain.transactions.RenameState](RenameState.md) - `class RenameState(Contract)` in `domain/transactions`.
* [domain.transactions.RetargetTransition](RetargetTransition.md) - Move one end of a transition to another state (the drag-and-drop edit).
* [domain.transactions.SetEffects](SetEffects.md) - `class SetEffects(Contract)` in `domain/transactions`.
* [domain.transactions.SetGuards](SetGuards.md) - `class SetGuards(Contract)` in `domain/transactions`.
* [domain.transactions.SetInitial](SetInitial.md) - `class SetInitial(Contract)` in `domain/transactions`.
* [domain.transactions.SetRole](SetRole.md) - `class SetRole(Contract)` in `domain/transactions`.
* [domain.transactions.TransactionDocument](TransactionDocument.md) - One semantic transaction as a JSON document (contracts/semantic-transaction.schema.json).

# Constants

* [domain.transactions.TRANSACTION_KINDS](TRANSACTION_KINDS.md) - Constant `TRANSACTION_KINDS` in `domain/transactions`.

# Functions

* [domain.transactions.apply_structural](apply_structural.md) - ``model`` with ``tx`` applied.
* [domain.transactions.element_refs](element_refs.md) - The model elements a transaction names (for refusal details).
* [domain.transactions.parse_transaction](parse_transaction.md) - Validate one transaction document; a malformed one is ``EDIT_INVALID``, never a crash.
* [domain.transactions.refused](refused.md) - `def refused(code: str, message: str, *refs: str) -> DomainError` in `domain/transactions`.

# Type Aliases

* [domain.transactions.Declare](Declare.md) - Type alias `Declare` in `domain/transactions`.
* [domain.transactions.Name](Name.md) - Type alias `Name` in `domain/transactions`.
* [domain.transactions.Transaction](Transaction.md) - Type alias `Transaction` in `domain/transactions`.
* [domain.transactions.TransitionId](TransitionId.md) - Type alias `TransitionId` in `domain/transactions`.
