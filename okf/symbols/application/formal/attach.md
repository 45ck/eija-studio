---
type: Function
title: application.formal.attach
description: Sealed receipts for every registered kind the source returned, skipping an exact repeat of the latest one.
resource: repo://src/eija_studio/application/formal.py#attach
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/formal.py#attach
  title: application/formal.py
  hash_method: ast-v2
  sha256: 94cf7541e52424212daa6288d58e8c6974fcce75ba9230dbc6a173e3bdfd15aa
notes_baseline: f891542bc4c25de5407f7da7d73e30008f440a55af6074fec003c17e44a30be0
---

# application.formal.attach

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/formal`](/modules/application/formal.md) |
| Signature | `def attach(source: FormalEvidenceSource \| None, baseline: Workflow, candidate: Workflow, subject: dict[str, Any], existing: list[dict[str, Any]], seal: Callable[[dict[str, Any]], dict[str, Any]], stamp: str, new_id: Callable[[], str], pack: Pack \| None=None) -> list[dict[str, Any]]` |
| Code | `repo://src/eija_studio/application/formal.py#attach` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Sealed receipts for every registered kind the source returned, skipping an exact repeat of the latest one.
With a ``pack``, a kind the pack does not verify from the checkout's reports is NOT_RUN with the pack's reason.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.formal.for_pack](/symbols/application/formal/for_pack.md) - Artifacts of a kind this pack does not verify from the reports become one NOT_RUN artifact with the pack's reason.
* [application.ports.FormalEvidenceSource](/symbols/application/ports/FormalEvidenceSource.md) - Where formal artifacts come from (Docker, Java, z3 or saved reports are adapter prerequisites).
* [domain.evidence_kinds.KINDS](/symbols/domain/evidence_kinds/KINDS.md) - Constant `KINDS` in `domain/evidence_kinds`.
* [domain.formal.FORMAL_PRODUCER](/symbols/domain/formal/FORMAL_PRODUCER.md) - Constant `FORMAL_PRODUCER` in `domain/formal`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.service.Studio.formal_view](/symbols/application/service/Studio.formal_view.md) - Formal evidence for a bare workflow (``eija compile``): collected and sealed in memory, never stored, never a decision.
* [application.service.Studio.verify](/symbols/application/service/Studio.verify.md) - `def verify(self, case_id: str, expected: int) -> dict[str, Any]` in `application/service`.
<!-- okf:generated:end links -->
