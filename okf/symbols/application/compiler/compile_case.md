---
type: Function
title: application.compiler.compile_case
description: 'Computes the review packet: subject, blockers, technical claims, impact, projections and critical questions for a Change Case.'
resource: repo://src/eija_studio/application/compiler.py#compile_case
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/compiler.py#compile_case
  title: application/compiler.py
  hash_method: ast-v2
  sha256: c587d997067425b2f597197e0d865f58d22e4af09c199f766262b21b8d4141e1
description_override: 'Computes the review packet: subject, blockers, technical claims, impact, projections and critical questions for a Change Case.'
notes_baseline: 6c1812fecd4c4226b95e23ee869102974b29321a822490849a6b5a5ac453db8e
---

# application.compiler.compile_case

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/compiler`](/modules/application/compiler.md) |
| Signature | `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool], active_version: int, scope: str='local-demo') -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/compiler.py#compile_case` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Eligibility is computed, never stored: blockers come from policy findings, source-fixture status, impact completeness, receipt status, stale baseline, scope and closed cases. `human_understanding` is always `UNKNOWN`. See [Review Packet](/language/review-packet.md) and [Local Decision](/language/local-decision.md).

<!-- okf:generated:begin links -->
## Depends on

* [application.compiler.subject_for](/symbols/application/compiler/subject_for.md) - `def subject_for(model: Workflow, layout: dict[str, Any], identity: dict[str, Any]) -> dict[str, Any]` in `application/compiler`.
* [application.formal.packet_view](/symbols/application/formal/packet_view.md) - The formal part of the review packet: per-kind claims, blockers, the full evidence list, explanations.
* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.evidence.aggregate_status](/symbols/domain/evidence/aggregate_status.md) - `def aggregate_status(receipts: list[dict[str, Any]], subject: dict[str, Any], authenticator: Callable[[dict[s…` in `domain/evidence`.
* [domain.evidence.receipt_status](/symbols/domain/evidence/receipt_status.md) - One receipt's applicability by its OWN declared claim and kind; an unauthentic receipt is FAIL.
* [domain.formal.Context](/symbols/domain/formal/Context.md) - What the kernel itself knows about the CURRENT subject, beyond the technical dimensions.
* [domain.impact.model_impact](/symbols/domain/impact/model_impact.md) - `def model_impact(before: Workflow, after: Workflow) -> dict[str, Any]` in `domain/impact`.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.
* [domain.policy.check_policy](/symbols/domain/policy/check_policy.md) - `def check_policy(model: Workflow) -> list[str]` in `domain/policy`.
* [domain.policy.meaning_questions](/symbols/domain/policy/meaning_questions.md) - `def meaning_questions(model: Workflow) -> list[dict[str, Any]]` in `domain/policy`.
* [domain.policy.projections](/symbols/domain/policy/projections.md) - Journey wording and rules derive from executable transitions, not AI copy.

## Referenced by

* [application.service.Studio.apply](/symbols/application/service/Studio.apply.md) - `def apply(self, case_id: str, expected: int, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.approve](/symbols/application/service/Studio.approve.md) - `def approve(self, case_id: str, expected: int, subject_hash: str, answers: dict[str, str], acknowledge_unknow…` in `application/service`.
* [application.service.Studio.view](/symbols/application/service/Studio.view.md) - `def view(self, case_id: str, scope: str='local-demo') -> dict[str, Any]` in `application/service`.
<!-- okf:generated:end links -->
