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
  sha256: 406083375a209a7febeefd1a852ebb12dbc45e1b1b91d79a2da165094250d026
description_override: 'Computes the review packet: subject, blockers, technical claims, impact, projections and critical questions for a Change Case.'
notes_baseline: 39b80d1f54fd75dd986cb54b6b5cb99a0b095f454cdc92e15cfb20cdb9b153c0
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: 2ff446bce73f01347f890a6fe117bbdaaf5ef2e4ea52c60224d7d0cd87941daa
  sources_sha256: 391b1f844ea4320be4abb9994678cd8d72f7bfb9563e2d4e99a7691f8ae9a7f0
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: 2ff446bce73f01347f890a6fe117bbdaaf5ef2e4ea52c60224d7d0cd87941daa
  sources_sha256: 94d02ec9df63ea410f322ccc595840e67e4a52cb702e37a78701958cd939e112
- by: process:wbs-1.5-agent
  at: '2026-09-29T12:00:00Z'
  notes_sha256: b6116e3d60a7b02a7dd27860c62e4827ce0c7b940e6f734927432393c4cb6e87
  sources_sha256: 39b80d1f54fd75dd986cb54b6b5cb99a0b095f454cdc92e15cfb20cdb9b153c0
---

# application.compiler.compile_case

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/compiler`](/modules/application/compiler.md) |
| Signature | `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool], active_version: int, scope: str='local-demo', pack: Pack \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/compiler.py#compile_case` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Eligibility is computed, never stored: blockers come from policy findings, source-fixture status, impact completeness, receipt status, stale baseline, scope and closed cases. Formal evidence per kind (ADR-0145) is part of the packet: a counterexample (`FAIL` or `CONFLICT`) blocks, while `UNKNOWN` and `NOT_RUN` never block and are never rounded up to `PASS`. `human_understanding` is always `UNKNOWN`. The formal part also lists the pack's declared verifiers, so a kind no registered evidence covers (TLC for a new pack) is visible as `NOT_RUN` with its reason. See [Review Packet](/language/review-packet.md) and [Local Decision](/language/local-decision.md).

<!-- okf:generated:begin links -->
## Depends on

* [application.compiler.subject_for](/symbols/application/compiler/subject_for.md) - `def subject_for(model: Workflow, layout: dict[str, Any], identity: dict[str, Any]) -> dict[str, Any]` in `application/compiler`.
* [application.formal.packet_view](/symbols/application/formal/packet_view.md) - The formal part of the review packet: per-kind claims, blockers, the full evidence list, explanations, and (with a pack) the pack's declared verifiers, so a ki…
* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.evidence.aggregate_status](/symbols/domain/evidence/aggregate_status.md) - `def aggregate_status(receipts: list[dict[str, Any]], subject: dict[str, Any], authenticator: Callable[[dict[s…` in `domain/evidence`.
* [domain.evidence.expected_shape](/symbols/domain/evidence/expected_shape.md) - The runtime matrix a receipt must cover under ``pack``: exactly ``model``'s states when it is known.
* [domain.evidence.receipt_status](/symbols/domain/evidence/receipt_status.md) - One receipt's applicability by its OWN declared claim and kind; an unauthentic receipt is FAIL.
* [domain.formal.Context](/symbols/domain/formal/Context.md) - What the kernel itself knows about the CURRENT subject, beyond the technical dimensions.
* [domain.impact.model_impact](/symbols/domain/impact/model_impact.md) - `def model_impact(before: Workflow, after: Workflow) -> dict[str, Any]` in `domain/impact`.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.policy.check_policy](/symbols/domain/policy/check_policy.md) - Sorted, de-duplicated policy codes of ``model`` under the pack (empty means the model conforms).
* [domain.policy.meaning_questions](/symbols/domain/policy/meaning_questions.md) - The pack's meaning-check questions, with expected answers read from the model where the pack says so.
* [domain.policy.projections](/symbols/domain/policy/projections.md) - Journey wording and rules derive from executable transitions, not AI copy.

## Referenced by

* [application.service.Studio.apply](/symbols/application/service/Studio.apply.md) - `def apply(self, case_id: str, expected: int, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.approve](/symbols/application/service/Studio.approve.md) - `def approve(self, case_id: str, expected: int, subject_hash: str, answers: dict[str, str], acknowledge_unknow…` in `application/service`.
* [application.service.Studio.view](/symbols/application/service/Studio.view.md) - `def view(self, case_id: str, scope: str='local-demo') -> dict[str, Any]` in `application/service`.
<!-- okf:generated:end links -->
