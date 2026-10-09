---
type: Class
title: domain.models.Contract
description: 'Base class for every domain contract: frozen and strict, unknown fields rejected.'
resource: repo://src/eija_studio/domain/models.py#Contract
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#Contract
  title: domain/models.py
  hash_method: ast-sig-v1
  sha256: 13c7cce1eef29efa373e8a053caddb16b9bab3cf15342d024340ed1379f4c73a
description_override: 'Base class for every domain contract: frozen and strict, unknown fields rejected.'
notes_baseline: 5053b280e054b67051413e1455ce4535d9f574101cd731628bcb0a4ce6eee0e0
---

# domain.models.Contract

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class Contract(BaseModel)` |
| Code | `repo://src/eija_studio/domain/models.py#Contract` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

The reason unknown fields and operators die at the boundary (acceptance [AC01](/requirements/ac01.md)). Contracts are immutable; a change produces a new value through validation, never `model_copy(update=...)`.

<!-- okf:generated:begin links -->
## Referenced by

* [application.data_steps.AddAttribute](/symbols/application/data_steps/AddAttribute.md) - `class AddAttribute(Contract)` in `application/data_steps`.
* [application.data_steps.RemoveAttribute](/symbols/application/data_steps/RemoveAttribute.md) - `class RemoveAttribute(Contract)` in `application/data_steps`.
* [application.data_steps.SetRequired](/symbols/application/data_steps/SetRequired.md) - `class SetRequired(Contract)` in `application/data_steps`.
* [application.edit_preview.EditPreview](/symbols/application/edit_preview/EditPreview.md) - An uncommitted candidate bound to a captured case revision; no evidence or edit authority.
* [application.edit_proposal.EditProposalPack](/symbols/application/edit_proposal/EditProposalPack.md) - `class EditProposalPack(Contract)` in `application/edit_proposal`.
* [application.edit_proposal.TypedEditProposal](/symbols/application/edit_proposal/TypedEditProposal.md) - `class TypedEditProposal(Contract)` in `application/edit_proposal`.
* [application.witness_inspection.InspectionContext](/symbols/application/witness_inspection/InspectionContext.md) - The case revision and review scope captured by the compiler, not inferred by a browser.
* [application.witness_inspection.InspectionModel](/symbols/application/witness_inspection/InspectionModel.md) - A supplied specimen, a validated projection of it, or an explicit absence of model data.
* [application.witness_inspection.InspectionNavigation](/symbols/application/witness_inspection/InspectionNavigation.md) - Current artifacts have no complete witness-reference contract, so no link is emitted.
* [application.witness_inspection.InspectionReceipt](/symbols/application/witness_inspection/InspectionReceipt.md) - Identity of the exact deciding intact receipt; its seal is deliberately not projected.
* [application.witness_inspection.InspectionRecord](/symbols/application/witness_inspection/InspectionRecord.md) - One exact JSON-pointer location within the deciding artifact, labelled by its known origin.
* [application.witness_inspection.InspectionReview](/symbols/application/witness_inspection/InspectionReview.md) - Full review identity; subject_json retains every subject field, including presentation.
* [application.witness_inspection.InspectionStep](/symbols/application/witness_inspection/InspectionStep.md) - An ordered literal recorded step.
* [application.witness_inspection.WitnessInspection](/symbols/application/witness_inspection/WitnessInspection.md) - Supplemental record inspection; availability never changes the existing evidence status.
* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.data.Association](/symbols/domain/data/Association.md) - `class Association(Contract)` in `domain/data`.
* [domain.data.Attribute](/symbols/domain/data/Attribute.md) - `class Attribute(Contract)` in `domain/data`.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.data.Entity](/symbols/domain/data/Entity.md) - `class Entity(Contract)` in `domain/data`.
* [domain.laws.When](/symbols/domain/laws/When.md) - Condition under which a law applies.
* [domain.models.Alternative](/symbols/domain/models/Alternative.md) - `class Alternative(Contract)` in `domain/models`.
* [domain.models.ExecuteCommand](/symbols/domain/models/ExecuteCommand.md) - `class ExecuteCommand(Contract)` in `domain/models`.
* [domain.models.LayoutChange](/symbols/domain/models/LayoutChange.md) - `class LayoutChange(Contract)` in `domain/models`.
* [domain.models.Principal](/symbols/domain/models/Principal.md) - `class Principal(Contract)` in `domain/models`.
* [domain.models.Proposal](/symbols/domain/models/Proposal.md) - `class Proposal(Contract)` in `domain/models`.
* [domain.models.SemanticTransaction](/symbols/domain/models/SemanticTransaction.md) - DEPRECATED closed vocabulary, superseded by the open one in ``domain.transactions`` (WBS 1.3).
* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.ActionSpec](/symbols/domain/pack/ActionSpec.md) - The declared guards and required effects of one action; the policy holds every transition to them.
* [domain.pack.Actor](/symbols/domain/pack/Actor.md) - `class Actor(Contract)` in `domain/pack`.
* [domain.pack.Effect](/symbols/domain/pack/Effect.md) - A typed effect.
* [domain.pack.Effects](/symbols/domain/pack/Effects.md) - `class Effects(Contract)` in `domain/pack`.
* [domain.pack.Fixtures](/symbols/domain/pack/Fixtures.md) - `class Fixtures(Contract)` in `domain/pack`.
* [domain.pack.Journey](/symbols/domain/pack/Journey.md) - `class Journey(Contract)` in `domain/pack`.
* [domain.pack.Language](/symbols/domain/pack/Language.md) - `class Language(Contract)` in `domain/pack`.
* [domain.pack.Meaning](/symbols/domain/pack/Meaning.md) - One interpretation of a request.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.PackInfo](/symbols/domain/pack/PackInfo.md) - `class PackInfo(Contract)` in `domain/pack`.
* [domain.pack.ProposalRule](/symbols/domain/pack/ProposalRule.md) - Offline fixture: when the lower-cased request contains every ``all`` word and at least one ``any`` word.
* [domain.pack.Proposals](/symbols/domain/pack/Proposals.md) - `class Proposals(Contract)` in `domain/pack`.
* [domain.pack.Question](/symbols/domain/pack/Question.md) - A meaning-check question for the owner.
* [domain.pack.Role](/symbols/domain/pack/Role.md) - `class Role(Contract)` in `domain/pack`.
* [domain.pack.Term](/symbols/domain/pack/Term.md) - `class Term(Contract)` in `domain/pack`.
* [domain.pack.Verifier](/symbols/domain/pack/Verifier.md) - An evidence kind that applies to this pack (``kind`` is the evidence kind's name).
* [domain.scenarios.Scenario](/symbols/domain/scenarios/Scenario.md) - `class Scenario(Contract)` in `domain/scenarios`.
* [domain.scenarios.ScenarioStep](/symbols/domain/scenarios/ScenarioStep.md) - `class ScenarioStep(Contract)` in `domain/scenarios`.
* [domain.scenarios.Scenarios](/symbols/domain/scenarios/Scenarios.md) - `class Scenarios(Contract)` in `domain/scenarios`.
* [domain.scenarios.Then](/symbols/domain/scenarios/Then.md) - What a step must do: move the record to `state`, or be refused with `refused` (a kernel refusal code).
* [domain.screens.Screen](/symbols/domain/screens/Screen.md) - `class Screen(Contract)` in `domain/screens`.
* [domain.screens.ScreenField](/symbols/domain/screens/ScreenField.md) - `class ScreenField(Contract)` in `domain/screens`.
* [domain.screens.Screens](/symbols/domain/screens/Screens.md) - `class Screens(Contract)` in `domain/screens`.
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
<!-- okf:generated:end links -->
