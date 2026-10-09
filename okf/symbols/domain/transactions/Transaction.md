---
type: Type Alias
title: domain.transactions.Transaction
description: Type alias `Transaction` in `domain/transactions`.
resource: repo://src/eija_studio/domain/transactions.py#Transaction
tags:
- symbol
- domain
- type-alias
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/transactions.py#Transaction
  title: domain/transactions.py
  hash_method: ast-v2
  sha256: 05d2a2dc07a94cd006a2f94c4062e8d3329ebafb02ba7d40bab783d4b68835d8
notes_baseline: bbf66a75700d12e5c4e3bea707bdeef96801f20d4e89ecc7422d68d48c8a7027
---

# domain.transactions.Transaction

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | type-alias |
| Module | [`domain/transactions`](/modules/domain/transactions.md) |
| Signature | `Transaction = Annotated[Union[AddState, RenameState, RemoveState, SetInitial, AddTransition, RetargetTransition, RemoveTransition, SetRole, SetGuards, SetEffec…` |
| Code | `repo://src/eija_studio/domain/transactions.py#Transaction` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.transactions.AddState](/symbols/domain/transactions/AddState.md) - `class AddState(Contract)` in `domain/transactions`.
* [domain.transactions.AddTransition](/symbols/domain/transactions/AddTransition.md) - A transition performing a declared action; its guards and effects are the action's declared ones.
* [domain.transactions.RemoveState](/symbols/domain/transactions/RemoveState.md) - `class RemoveState(Contract)` in `domain/transactions`.
* [domain.transactions.RemoveTransition](/symbols/domain/transactions/RemoveTransition.md) - `class RemoveTransition(Contract)` in `domain/transactions`.
* [domain.transactions.RenameState](/symbols/domain/transactions/RenameState.md) - `class RenameState(Contract)` in `domain/transactions`.
* [domain.transactions.RetargetTransition](/symbols/domain/transactions/RetargetTransition.md) - Move one end of a transition to another state (the drag-and-drop edit).
* [domain.transactions.SetEffects](/symbols/domain/transactions/SetEffects.md) - `class SetEffects(Contract)` in `domain/transactions`.
* [domain.transactions.SetGuards](/symbols/domain/transactions/SetGuards.md) - `class SetGuards(Contract)` in `domain/transactions`.
* [domain.transactions.SetInitial](/symbols/domain/transactions/SetInitial.md) - `class SetInitial(Contract)` in `domain/transactions`.
* [domain.transactions.SetRole](/symbols/domain/transactions/SetRole.md) - `class SetRole(Contract)` in `domain/transactions`.

## Referenced by

* [application.data_steps.Step](/symbols/application/data_steps/Step.md) - Type alias `Step` in `application/data_steps`.
* [application.data_steps.split](/symbols/application/data_steps/split.md) - The kernel transactions and the data-model steps, each in plan order (role-kind steps are in neither).
* [application.edit_preview.EditPreview](/symbols/application/edit_preview/EditPreview.md) - An uncommitted candidate bound to a captured case revision; no evidence or edit authority.
* [application.edit_preview.preview_edit](/symbols/application/edit_preview/preview_edit.md) - The candidate edit would produce from this snapshot, or its refusal without a guessed model.
* [application.history.command_event](/symbols/application/history/command_event.md) - Append-only command provenance; decision and receipt payloads remain in their existing audit.
* [application.new_system.declare](/symbols/application/new_system/declare.md) - `pack` with every action and role `transactions` name but it does not declare yet, declared exactly as a sketch declares them (ADR-0201): an action gets the ba…
* [application.new_system.new_names](/symbols/application/new_system/new_names.md) - The actions and roles `transactions` name that `pack` does not declare, in order of first use.
* [application.ports.EditProposer](/symbols/application/ports/EditProposer.md) - Offline request resolution only; returns an untrusted transaction and performs no IO or persistence.
* [application.service.Studio.edit](/symbols/application/service/Studio.edit.md) - `def edit(self, case_id: str, expected: int, tx: Transaction, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.edit_check](/symbols/application/service/Studio.edit_check.md) - Dry-run one edit: {legal, codes, refs}.
* [application.service.Studio.edit_preview](/symbols/application/service/Studio.edit_preview.md) - Read-only edit preview bound to one case snapshot; the owner edit still requires capability and CAS.
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service`.
* [domain.affordance.dry_run](/symbols/domain/affordance/dry_run.md) - {legal, codes, refs} of applying ``tx`` to ``model`` under ``pack``, without applying it anywhere.
* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.pack.Meaning](/symbols/domain/pack/Meaning.md) - One interpretation of a request.
* [domain.policy.apply_structural_all](/symbols/domain/policy/apply_structural_all.md) - ``model`` with every transaction applied in order; structure only, no policy (what-if and meaning previews).
* [domain.policy.apply_transaction](/symbols/domain/policy/apply_transaction.md) - Apply one transaction (policy-checked).
* [domain.policy.apply_transactions](/symbols/domain/policy/apply_transactions.md) - Apply an edit sequence as one change: the start must conform, the result must conform (intermediate steps need only be coherent workflows).
* [domain.policy.meaning_transactions](/symbols/domain/policy/meaning_transactions.md) - `def meaning_transactions(meaning_id: str, pack: Pack | None=None) -> tuple[Transaction, ...]` in `domain/policy`.
* [domain.transactions.TransactionDocument](/symbols/domain/transactions/TransactionDocument.md) - One semantic transaction as a JSON document (contracts/semantic-transaction.schema.json).
* [domain.transactions.apply_structural](/symbols/domain/transactions/apply_structural.md) - ``model`` with ``tx`` applied.
* [domain.transactions.element_refs](/symbols/domain/transactions/element_refs.md) - The model elements a transaction names (for refusal details).
* [domain.transactions.parse_transaction](/symbols/domain/transactions/parse_transaction.md) - Validate one transaction document; a malformed one is ``EDIT_INVALID``, never a crash.
<!-- okf:generated:end links -->
