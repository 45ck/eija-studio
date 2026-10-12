---
type: Method
title: application.service.Studio.verify
description: Runs the runtime matrix in a sandbox and stores a sealed receipt; refuses a source that differs from the release fixture.
resource: repo://src/eija_studio/application/service.py#Studio.verify
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.verify
  title: application/service.py
  hash_method: ast-v2
  sha256: aa187aa889f7242549dae7c08976663d1b2894fee752373bf6a0e791d58d132c
description_override: Runs the runtime matrix in a sandbox and stores a sealed receipt; refuses a source that differs from the release fixture.
notes_baseline: 1cf91076c4c75b6ba5d724b2aa50b25bcaf23033c41824ac0bfc0433a898e78c
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: 56f0ccbab358790d8de0e49cde7f9024d5f5ec3f0263df470c46d9943a65df6a
  sources_sha256: 6203f98aec197026c9e5cc2ee8781bc93af1b541464e98684ecfb516bbcc9c3a
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: 56f0ccbab358790d8de0e49cde7f9024d5f5ec3f0263df470c46d9943a65df6a
  sources_sha256: a9ed783a70558b432f88de89917d691d55c2272d4b60c8ae9cb0ca119d9b82d4
- by: process:wbs-1.5-agent
  at: '2026-09-29T12:00:00Z'
  notes_sha256: 1736d73398d6735d08651269065d70ae2776ea2d04ecfe339cd39add3a1baf33
  sources_sha256: f5bc6b23b2b222232a737f2892c86137b1815030ca006a4489de2b0e3f5bd5c7
- by: process:codex-ide-integration
  at: '2026-10-02T05:15:30Z'
  notes_sha256: 1736d73398d6735d08651269065d70ae2776ea2d04ecfe339cd39add3a1baf33
  sources_sha256: 41377bd722fc2f8c6bedb11ed9c90def97da991e6b05c342257ed7fc55a265cd
- by: process:playide-activation
  at: '2026-10-10T14:05:00+11:00'
  notes_sha256: be4981cad511acb284bab2ef9e8963f93edabb4b76573a765fbe4f4a57ccd677
  sources_sha256: b7bf3985fe556ac02ed7b2dfb3c880e92f45aacdb8113d25d0b5d0b4dd835af8
- by: process:playide-activation
  at: '2026-10-10T02:55:29+00:00'
  notes_sha256: be4981cad511acb284bab2ef9e8963f93edabb4b76573a765fbe4f4a57ccd677
  sources_sha256: b7bf3985fe556ac02ed7b2dfb3c880e92f45aacdb8113d25d0b5d0b4dd835af8
- by: process:playide-exact-app
  at: '2026-10-11T09:17:31Z'
  notes_sha256: ebc55ccf334804edbe5f53e8db22ad3cb6d5c17c7eca559e83502031f4e41b42
  sources_sha256: 2e7c3b7b9141f43216cb208a127ce6f25a6b6dbde83975104539a7c30244c92d
- by: process:playide-service-cohesion
  at: '2026-10-12T05:30:41Z'
  notes_sha256: 632c5cde10cc5cfa60147d9044667950ecce91272a9cd92b8d1a6c2487ad8b98
  sources_sha256: 1cf91076c4c75b6ba5d724b2aa50b25bcaf23033c41824ac0bfc0433a898e78c
---

# application.service.Studio.verify

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def verify(self, case_id: str, expected: int) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.verify` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Verification clears any current decision and never approves. Besides the runtime receipt it appends the formal-evidence receipts of the configured source (collected outside the transaction; a missing prerequisite is a `NOT_RUN` artifact, never omitted). A kind the studio's pack does not verify from the checkout's reports (its verifier is `generated`, `not_run` or undeclared) is replaced by a `NOT_RUN` artifact carrying the pack's reason, so another pack's proof never counts for this one. See [verify_runtime](/symbols/application/verifier/verify_runtime.md) and [Evidence Receipt](/language/evidence-receipt.md).

The protected selection and replayed history are checked inside the unit of work
before receipts or case state are written. A corrupt persisted selection refuses
without replacing an existing decision or evidence record.

Exact-app cases execute the separate frozen generated checker outside the transaction. Before retaining sealed receipts, verification rechecks case version, active baseline, measured implementation/environment and captured app bytes. A later pass does not erase a retained failure.

The generated checker observation is collected and sealed through `generated_app.verify_app`, using the service's existing signer, clock and receipt ID source. Its receipt can record a failed run; a signature does not turn that observation into a passing verdict. Studio retains source-review refusal, replay, final freshness/version checks and all persistence.

<!-- okf:generated:begin links -->
## Depends on

* [application.compiler.subject_for](/symbols/application/compiler/subject_for.md) - `def subject_for(model: Workflow, layout: dict[str, Any], identity: dict[str, Any]) -> dict[str, Any]` in `application/compiler`.
* [application.formal.attach](/symbols/application/formal/attach.md) - Sealed receipts for every registered kind the source returned, skipping an exact repeat of the latest one.
* [application.generated_app.bind_subject](/symbols/application/generated_app/bind_subject.md) - `def bind_subject(subject: dict[str, Any], binding: GeneratedAppBinding | None) -> dict[str, Any]` in `application/generated_app`.
* [application.history.replay](/symbols/application/history/replay.md) - Fail closed when stored commands no longer explain the candidate under the exact active pack.
* [application.service.now](/symbols/application/service/now.md) - `def now() -> str` in `application/service`.
* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict[str, Any], sandbox: SandboxFactory, pack: Pack | None=None)…` in `application/verifier`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
<!-- okf:generated:end links -->
