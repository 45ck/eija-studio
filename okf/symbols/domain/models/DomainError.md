---
type: Class
title: domain.models.DomainError
description: Error carrying a stable code and safe message; never provider secrets or arbitrary exception text.
resource: repo://src/eija_studio/domain/models.py#DomainError
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#DomainError
  title: domain/models.py
  hash_method: ast-sig-v1
  sha256: b037eaabf92c38019360ca28949d50750ce2ee846a1918a34a0cc21738d3f13b
description_override: Error carrying a stable code and safe message; never provider secrets or arbitrary exception text.
notes_baseline: 77f9cf4d4d3c50c25f84badd8160195603d82f388c3f2885c85146e56eaa205c
verified:
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: b4d2cd49ca0ca7ebd69c7fb5d4c841de0fc35a8ec7e631d7e9852934736b062e
  sources_sha256: 77f9cf4d4d3c50c25f84badd8160195603d82f388c3f2885c85146e56eaa205c
---

# domain.models.DomainError

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class DomainError(ValueError)` |
| Code | `repo://src/eija_studio/domain/models.py#DomainError` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Stable error code: never expose provider secrets or arbitrary exception text.
~~~
<!-- okf:generated:end facts -->

## Notes

Codes such as `POLICY_BLOCKED`, `STALE_VERSION` and `ROLE_DENIED` are the contract that HTTP and CLI map to responses and that tests assert. `details` is optional structured, safe-to-show data: a policy refusal carries `{codes, refs}` (the law codes and the `law:`/`transition:`/`state:` elements involved), which HTTP returns alongside the code.

<!-- okf:generated:begin links -->
## Referenced by

* [application.access.matrix](/symbols/application/access/matrix.md) - Every role's actions from every state, each tried in the kernel with the fixture actors in that role.
* [application.appgen.data_cases](/symbols/application/appgen/data_cases.md) - Record values to create with, and `check_values`' answer for each: a valid record, then each required value missing, each value of the wrong type, each text on…
* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
* [application.diagram_catalog.render_view](/symbols/application/diagram_catalog/render_view.md) - Generated diagram text for one view.
* [application.diagram_emitters.emit](/symbols/application/diagram_emitters/emit.md) - Serialise a diagram model.
* [application.diagrams.commit_sequence](/symbols/application/diagrams/commit_sequence.md) - The commit protocol of one action, in the order `application.runtime.execute` runs it: authority is checked BEFORE any replay lookup, then replay/operation bin…
* [application.edit_preview.preview_edit](/symbols/application/edit_preview/preview_edit.md) - The candidate edit would produce from this snapshot, or its refusal without a guessed model.
* [application.edit_proposal.propose_edit](/symbols/application/edit_proposal/propose_edit.md) - No persistence or evidence: resolve one request, then use the existing policy-checked projection.
* [application.history.history_view](/symbols/application/history/history_view.md) - Read-only models for navigation plus actual command audit entries; no invented legacy timestamps.
* [application.history.replay](/symbols/application/history/replay.md) - Fail closed when stored commands no longer explain the candidate under the exact active pack.
* [application.law_proof.prove_laws](/symbols/application/law_proof/prove_laws.md) - Every law of the pack, judged on `model` (the pack's own by default), with the evidence for each verdict.
* [application.law_proof.with_laws](/symbols/application/law_proof/with_laws.md) - The pack with its law file replaced by `laws` (a draft edited in PlayIDE), checked as the pack loader checks it.
* [application.memo.ensure_conforms](/symbols/application/memo/ensure_conforms.md) - `ensure(model, pack)` (the policy check): a pair it let through is remembered; any other is refused by it again, so the error is always the check's own.
* [application.plan.example_passes](/symbols/application/plan/example_passes.md) - Whether `request`, sent to the chat as it stands, becomes a plan the policy allows on `model`.
* [application.plan.preview_plan](/symbols/application/plan/preview_plan.md) - What the accepted steps would make of `model`.
* [application.plan.propose_plan](/symbols/application/plan/propose_plan.md) - Ask the proposer for a plan, re-check it, and preview it with every step accepted.
* [application.repository.read_repository_change_file](/symbols/application/repository/read_repository_change_file.md) - Bound the historical selection before dispatch; absence never bypasses validation.
* [application.repository.validate_change_revisions](/symbols/application/repository/validate_change_revisions.md) - Validate full object IDs before calling any configured repository port.
* [application.review.review_change](/symbols/application/review/review_change.md) - Everything a reviewer needs to check a change: what changed, how risky, and what the kernel does differently.
* [application.ripple.Build](/symbols/application/ripple/Build.md) - Type alias `Build` in `application/ripple`.
* [application.ripple.check_follow_ons](/symbols/application/ripple/check_follow_ons.md) - The proposer's follow-on steps, each re-checked on its own on top of the plan: a state-machine step through the policy (`base` with `plan` and the step), a scr…
* [application.ripple.ripple](/symbols/application/ripple/ripple.md) - Every diagram's effects of going from `base` to `candidate`.
* [application.runtime.check_actor](/symbols/application/runtime/check_actor.md) - `def check_actor(actor: dict[str, Any], transition: Transition, command: ExecuteCommand) -> None` in `application/runtime`.
* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault: Callable[[…` in `application/runtime`.
* [application.runtime.initialise](/symbols/application/runtime/initialise.md) - `def initialise(session: UnitOfWork, case_id: str, model: Workflow, *, state: str | None=None, pack: Pack | No…` in `application/runtime`.
* [application.scenario_run.record_steps](/symbols/application/scenario_run/record_steps.md) - What the kernel does for each (actor, action) in turn, written as scenario steps that expect exactly that.
* [application.scenario_run.run_scenarios](/symbols/application/scenario_run/run_scenarios.md) - Every scenario run on `model`; a model the policy refuses runs none of them.
* [application.scxml.to_scxml](/symbols/application/scxml/to_scxml.md) - The model as an SCXML document.
* [application.sequences.check_sequences](/symbols/application/sequences/check_sequences.md) - Every scenario drawn as a sequence and checked by the kernel on `model`; with `base` (the model in force) also on it, for the change.
* [application.service.Studio.apply](/symbols/application/service/Studio.apply.md) - `def apply(self, case_id: str, expected: int, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.approve](/symbols/application/service/Studio.approve.md) - `def approve(self, case_id: str, expected: int, subject_hash: str, answers: dict[str, str], acknowledge_unknow…` in `application/service`.
* [application.service.Studio.create](/symbols/application/service/Studio.create.md) - `def create(self, request: str) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.layout](/symbols/application/service/Studio.layout.md) - `def layout(self, case_id: str, expected: int, change: LayoutChange, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.propose](/symbols/application/service/Studio.propose.md) - `def propose(self, case_id: str, expected: int, *, consent: bool=False) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.redo](/symbols/application/service/Studio.redo.md) - Reapply the next undone typed command through the same interpreter and policy checks.
* [application.service.Studio.select](/symbols/application/service/Studio.select.md) - `def select(self, case_id: str, expected: int, interpretation: str, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.undo](/symbols/application/service/Studio.undo.md) - Undo the last owner semantic edit; the selected meaning remains an indivisible protected prefix.
* [application.service.Studio.verify](/symbols/application/service/Studio.verify.md) - `def verify(self, case_id: str, expected: int) -> dict[str, Any]` in `application/service`.
* [application.simulation.MemorySession.actor](/symbols/application/simulation/MemorySession.actor.md) - `def actor(self, actor_id: str) -> dict[str, Any]` in `application/simulation`.
* [application.simulation.MemorySession.update_instance](/symbols/application/simulation/MemorySession.update_instance.md) - `def update_instance(self, item: dict[str, Any], expected: int) -> None` in `application/simulation`.
* [domain.affordance.dry_run](/symbols/domain/affordance/dry_run.md) - {legal, codes, refs} of applying ``tx`` to ``model`` under ``pack``, without applying it anywhere.
* [domain.change_case.ChangeCase.at_version](/symbols/domain/change_case/ChangeCase.at_version.md) - `def at_version(self, expected: int) -> None` in `domain/change_case`.
* [domain.change_case.ChangeCase.executable](/symbols/domain/change_case/ChangeCase.executable.md) - `def executable(self) -> Workflow` in `domain/change_case`.
* [domain.change_case.ChangeCase.require_editable](/symbols/domain/change_case/ChangeCase.require_editable.md) - `def require_editable(self) -> None` in `domain/change_case`.
* [domain.data.check_values](/symbols/domain/data/check_values.md) - Validate a record's values against its entity.
* [domain.data.load_data](/symbols/domain/data/load_data.md) - The pack's data model, or None when the pack has no `data.json`.
* [domain.data.parse_data](/symbols/domain/data/parse_data.md) - `def parse_data(document: Any, pack_id: str) -> DataModel` in `domain/data`.
* [domain.models.Principal.require](/symbols/domain/models/Principal.require.md) - `def require(self, capability: str) -> None` in `domain/models`.
* [domain.pack.PackError](/symbols/domain/pack/PackError.md) - A pack that cannot be used.
* [domain.policy.apply_meaning](/symbols/domain/policy/apply_meaning.md) - The candidate a supported pack meaning produces from ``model`` (policy-checked).
* [domain.policy.ensure_policy](/symbols/domain/policy/ensure_policy.md) - `def ensure_policy(model: Workflow, pack: Pack | None=None) -> None` in `domain/policy`.
* [domain.policy.first_supported_meaning](/symbols/domain/policy/first_supported_meaning.md) - The id of the pack's first supported meaning (the demo candidate's meaning).
* [domain.policy.meaning_transactions](/symbols/domain/policy/meaning_transactions.md) - `def meaning_transactions(meaning_id: str, pack: Pack | None=None) -> tuple[Transaction, ...]` in `domain/policy`.
* [domain.policy.transition](/symbols/domain/policy/transition.md) - A transition for a declared action, with the action's declared guards and effects and the pack's forbidden effects.
* [domain.policy.what_if](/symbols/domain/policy/what_if.md) - What an UNSUPPORTED meaning would do to ``model`` (structure only, never a candidate), or None when it declares no transactions or they do not even apply struc…
* [domain.scenarios.load_scenarios](/symbols/domain/scenarios/load_scenarios.md) - The scenarios in `directory`, or None when it has no `scenarios.json`.
* [domain.scenarios.parse_scenarios](/symbols/domain/scenarios/parse_scenarios.md) - `def parse_scenarios(document: Any, pack_id: str) -> Scenarios` in `domain/scenarios`.
* [domain.screens.load_screens](/symbols/domain/screens/load_screens.md) - The pack's screens, or None when the pack has no `screens.json`.
* [domain.screens.parse_screens](/symbols/domain/screens/parse_screens.md) - `def parse_screens(document: Any, pack_id: str) -> Screens` in `domain/screens`.
* [domain.screens.require_buildable](/symbols/domain/screens/require_buildable.md) - `def require_buildable(screens: Screens, model: Workflow, data: DataModel | None) -> None` in `domain/screens`.
* [domain.transactions.parse_transaction](/symbols/domain/transactions/parse_transaction.md) - Validate one transaction document; a malformed one is ``EDIT_INVALID``, never a crash.
* [domain.transactions.refused](/symbols/domain/transactions/refused.md) - `def refused(code: str, message: str, *refs: str) -> DomainError` in `domain/transactions`.
<!-- okf:generated:end links -->
