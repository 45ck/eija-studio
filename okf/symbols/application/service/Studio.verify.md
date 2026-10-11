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
  sha256: 70a425a682f05ec57bf879d236b6a485fd1cffa84cf1df991e0ef783f22e0ff2
description_override: Runs the runtime matrix in a sandbox and stores a sealed receipt; refuses a source that differs from the release fixture.
notes_baseline: b7bf3985fe556ac02ed7b2dfb3c880e92f45aacdb8113d25d0b5d0b4dd835af8
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

<!-- okf:generated:begin links -->
## Depends on

* [application.compiler.subject_for](/symbols/application/compiler/subject_for.md) - `def subject_for(model: Workflow, layout: dict[str, Any], identity: dict[str, Any]) -> dict[str, Any]` in `application/compiler`.
* [application.formal.attach](/symbols/application/formal/attach.md) - Sealed receipts for every registered kind the source returned, skipping an exact repeat of the latest one.
* [application.history.replay](/symbols/application/history/replay.md) - Fail closed when stored commands no longer explain the candidate under the exact active pack.
* [application.service.now](/symbols/application/service/now.md) - `def now() -> str` in `application/service`.
* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict[str, Any], sandbox: SandboxFactory, pack: Pack | None=None)…` in `application/verifier`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
<!-- okf:generated:end links -->
