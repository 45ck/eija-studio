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
  sha256: e2c67c17d126ccd08a3febcc633b11490a0a55c91bc2ba4600acecdc90114ba2
description_override: Error carrying a stable code and safe message; never provider secrets or arbitrary exception text.
notes_baseline: e51e8680f0e3eb4e95e1784b1a10b92d0be9861b06588e7b951caa1af39cd2ee
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

Codes such as `POLICY_BLOCKED`, `STALE_VERSION` and `ROLE_DENIED` are the contract that HTTP and CLI map to responses and that tests assert.

<!-- okf:generated:begin links -->
## Referenced by

* [application.diagram_catalog.render_view](/symbols/application/diagram_catalog/render_view.md) - Generated diagram text for one view.
* [application.diagram_emitters.emit](/symbols/application/diagram_emitters/emit.md) - Serialise a diagram model.
* [application.diagrams.commit_sequence](/symbols/application/diagrams/commit_sequence.md) - The commit protocol of one action, in the order `application.runtime.execute` runs it: authority is checked BEFORE any replay lookup, then replay/operation bin…
* [application.runtime.check_actor](/symbols/application/runtime/check_actor.md) - `def check_actor(actor: dict[str, Any], transition: Transition, command: ExecuteCommand) -> None` in `application/runtime`.
* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault: Callable[[…` in `application/runtime`.
* [application.runtime.initialise](/symbols/application/runtime/initialise.md) - `def initialise(session: UnitOfWork, case_id: str, model: Workflow, *, state: str | None=None) -> dict[str, An…` in `application/runtime`.
* [application.service.Studio.apply](/symbols/application/service/Studio.apply.md) - `def apply(self, case_id: str, expected: int, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.approve](/symbols/application/service/Studio.approve.md) - `def approve(self, case_id: str, expected: int, subject_hash: str, answers: dict[str, str], acknowledge_unknow…` in `application/service`.
* [application.service.Studio.create](/symbols/application/service/Studio.create.md) - `def create(self, request: str) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.edit](/symbols/application/service/Studio.edit.md) - `def edit(self, case_id: str, expected: int, tx: SemanticTransaction, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.layout](/symbols/application/service/Studio.layout.md) - `def layout(self, case_id: str, expected: int, change: LayoutChange, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.propose](/symbols/application/service/Studio.propose.md) - `def propose(self, case_id: str, expected: int, *, consent: bool=False) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.select](/symbols/application/service/Studio.select.md) - `def select(self, case_id: str, expected: int, interpretation: str, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.verify](/symbols/application/service/Studio.verify.md) - `def verify(self, case_id: str, expected: int) -> dict[str, Any]` in `application/service`.
* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict[str, Any], sandbox: SandboxFactory) -> dict[str, Any]` in `application/verifier`.
* [domain.change_case.ChangeCase.at_version](/symbols/domain/change_case/ChangeCase.at_version.md) - `def at_version(self, expected: int) -> None` in `domain/change_case`.
* [domain.change_case.ChangeCase.executable](/symbols/domain/change_case/ChangeCase.executable.md) - `def executable(self) -> Workflow` in `domain/change_case`.
* [domain.change_case.ChangeCase.require_editable](/symbols/domain/change_case/ChangeCase.require_editable.md) - `def require_editable(self) -> None` in `domain/change_case`.
* [domain.models.Principal.require](/symbols/domain/models/Principal.require.md) - `def require(self, capability: str) -> None` in `domain/models`.
* [domain.policy.apply_transaction](/symbols/domain/policy/apply_transaction.md) - `def apply_transaction(model: Workflow, tx: SemanticTransaction) -> Workflow` in `domain/policy`.
* [domain.policy.ensure_policy](/symbols/domain/policy/ensure_policy.md) - `def ensure_policy(model: Workflow) -> None` in `domain/policy`.
<!-- okf:generated:end links -->
