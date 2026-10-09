---
type: Module
title: domain.transactions
description: 'Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.'
resource: repo://src/eija_studio/domain/transactions.py
tags:
- module
- domain
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/transactions.py
  title: domain/transactions.py
  hash_method: ast-api-v1
  sha256: c0a48f14894c0e325ec18d6dcd6a1d171b49e85e8168cd1ee36e78649d934131
notes_baseline: 30de18e749153d4b3c5063694a60c48e4d07e41860a69ff471a2bd2c2caa9863
---

# domain.transactions

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | domain |
| Code | `repo://src/eija_studio/domain/transactions.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.

A transaction is a small typed record, a discriminated union on ``kind``. ``apply_structural`` applies one to a
workflow and returns the new workflow; it checks structure only (the element exists, the result is a coherent
workflow). Whether the result is ALLOWED is the policy's job (``domain.policy.apply_transactions``), so a refusal
names the law it breaks. Nothing here names a domain: states, roles and actions come from the model and the pack.

Terms (``rename_term``/``bind_term``) are not in this vocabulary yet: a term lives in the pack's language, not in
a case's workflow, and binding needs the weave index (WBS 1.6). See docs/engineering/FUTURE-WORK.md.
~~~

## Public symbols

* [`AddState`](/symbols/domain/transactions/AddState.md) (class) - no docstring
* [`AddTransition`](/symbols/domain/transactions/AddTransition.md) (class) - A transition performing a declared action; its guards and effects are the action's declared ones.
* [`Declare`](/symbols/domain/transactions/Declare.md) (type-alias) - no docstring
* [`Name`](/symbols/domain/transactions/Name.md) (type-alias) - no docstring
* [`RemoveState`](/symbols/domain/transactions/RemoveState.md) (class) - no docstring
* [`RemoveTransition`](/symbols/domain/transactions/RemoveTransition.md) (class) - no docstring
* [`RenameState`](/symbols/domain/transactions/RenameState.md) (class) - no docstring
* [`RetargetTransition`](/symbols/domain/transactions/RetargetTransition.md) (class) - Move one end of a transition to another state (the drag-and-drop edit).
* [`SetEffects`](/symbols/domain/transactions/SetEffects.md) (class) - no docstring
* [`SetGuards`](/symbols/domain/transactions/SetGuards.md) (class) - no docstring
* [`SetInitial`](/symbols/domain/transactions/SetInitial.md) (class) - no docstring
* [`SetRole`](/symbols/domain/transactions/SetRole.md) (class) - no docstring
* [`TRANSACTION_KINDS`](/symbols/domain/transactions/TRANSACTION_KINDS.md) (constant) - no docstring
* [`Transaction`](/symbols/domain/transactions/Transaction.md) (type-alias) - no docstring
* [`TransactionDocument`](/symbols/domain/transactions/TransactionDocument.md) (class) - One semantic transaction as a JSON document (contracts/semantic-transaction.schema.json).
* [`TransitionId`](/symbols/domain/transactions/TransitionId.md) (type-alias) - no docstring
* [`apply_structural`](/symbols/domain/transactions/apply_structural.md) (function) - ``model`` with ``tx`` applied.
* [`element_refs`](/symbols/domain/transactions/element_refs.md) (function) - The model elements a transaction names (for refusal details).
* [`parse_transaction`](/symbols/domain/transactions/parse_transaction.md) (function) - Validate one transaction document; a malformed one is ``EDIT_INVALID``, never a crash.
* [`refused`](/symbols/domain/transactions/refused.md) (function) - no docstring

## Internal imports

* [`domain/models`](/modules/domain/models.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).

## Referenced by

* [adapters.edit_proposals](/modules/adapters/edit_proposals.md) - Bounded offline request fixture: exact model names and complete phrases, never an LLM.
* [application.edit_preview](/modules/application/edit_preview.md) - Read-only edit projection over one captured case, using the same interpreter as owner edits.
* [application.edit_proposal](/modules/application/edit_proposal.md) - A read-only offline proposal over one captured candidate; owner edits keep their existing boundary.
* [application.history](/modules/application/history.md) - Semantic history is a projection of typed commands, replayed by the existing policy interpreter.
* [application.new_system](/modules/application/new_system.md) - Start a new system (ADR-0185): the pack documents for a system started from a sketch or copied from a template.
* [application.plan](/modules/application/plan.md) - Plan mode for the PlayIDE chat (ADR-0156): an AI proposes a change as numbered typed steps; the person accepts or rejects each one and sees what the accepted o…
* [application.ports](/modules/application/ports.md) - Application-owned ports.
* [application.ripple](/modules/application/ripple.md) - Ripple (ADR-0158): what one change to the state machine does to every other diagram of the same system, and the follow-on edits that would keep them in agreeme…
* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [domain.affordance](/modules/domain/affordance.md) - Affordance map (WBS 1.3): which single edits the kernel would accept, and why the others are refused.
* [domain.change_case](/modules/domain/change_case.md) - Module `domain/change_case` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.
* [interfaces.http](/modules/interfaces/http.md) - Loopback-only local adapter.
* [interfaces.mcp_server](/modules/interfaces/mcp_server.md) - MCP (Model Context Protocol) adapter: the agent-facing face of EIJA Studio.
* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [interfaces.play_systems](/modules/interfaces/play_systems.md) - PlayIDE's systems (ADR-0185): start a new system from a sketch or a template, open one you made before, and save the work in progress to carry on later.
* [domain.transactions.AddState](/symbols/domain/transactions/AddState.md) - `class AddState(Contract)` in `domain/transactions`.
* [domain.transactions.AddTransition](/symbols/domain/transactions/AddTransition.md) - A transition performing a declared action; its guards and effects are the action's declared ones.
* [domain.transactions.Declare](/symbols/domain/transactions/Declare.md) - Type alias `Declare` in `domain/transactions`.
* [domain.transactions.Name](/symbols/domain/transactions/Name.md) - Type alias `Name` in `domain/transactions`.
* [domain.transactions.RemoveState](/symbols/domain/transactions/RemoveState.md) - `class RemoveState(Contract)` in `domain/transactions`.
* [domain.transactions.RemoveTransition](/symbols/domain/transactions/RemoveTransition.md) - `class RemoveTransition(Contract)` in `domain/transactions`.
* [domain.transactions.RenameState](/symbols/domain/transactions/RenameState.md) - `class RenameState(Contract)` in `domain/transactions`.
* [domain.transactions.RetargetTransition](/symbols/domain/transactions/RetargetTransition.md) - Move one end of a transition to another state (the drag-and-drop edit).
* [domain.transactions.SetEffects](/symbols/domain/transactions/SetEffects.md) - `class SetEffects(Contract)` in `domain/transactions`.
* [domain.transactions.SetGuards](/symbols/domain/transactions/SetGuards.md) - `class SetGuards(Contract)` in `domain/transactions`.
* [domain.transactions.SetInitial](/symbols/domain/transactions/SetInitial.md) - `class SetInitial(Contract)` in `domain/transactions`.
* [domain.transactions.SetRole](/symbols/domain/transactions/SetRole.md) - `class SetRole(Contract)` in `domain/transactions`.
* [domain.transactions.TRANSACTION_KINDS](/symbols/domain/transactions/TRANSACTION_KINDS.md) - Constant `TRANSACTION_KINDS` in `domain/transactions`.
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.
* [domain.transactions.TransactionDocument](/symbols/domain/transactions/TransactionDocument.md) - One semantic transaction as a JSON document (contracts/semantic-transaction.schema.json).
* [domain.transactions.TransitionId](/symbols/domain/transactions/TransitionId.md) - Type alias `TransitionId` in `domain/transactions`.
* [domain.transactions.apply_structural](/symbols/domain/transactions/apply_structural.md) - ``model`` with ``tx`` applied.
* [domain.transactions.element_refs](/symbols/domain/transactions/element_refs.md) - The model elements a transaction names (for refusal details).
* [domain.transactions.parse_transaction](/symbols/domain/transactions/parse_transaction.md) - Validate one transaction document; a malformed one is ``EDIT_INVALID``, never a crash.
* [domain.transactions.refused](/symbols/domain/transactions/refused.md) - `def refused(code: str, message: str, *refs: str) -> DomainError` in `domain/transactions`.
<!-- okf:generated:end links -->
