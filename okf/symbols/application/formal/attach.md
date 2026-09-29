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
  sha256: 90f1e925d585c388fdabbcd1c089ca229a57dbad4e8adfded1a9ebdf483a5ce5
notes_baseline: 67a1e4b98b606b1ae731c4167512004859b10379c9ae024dcd478d4b08220326
---

# application.formal.attach

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/formal`](/modules/application/formal.md) |
| Signature | `def attach(source: FormalEvidenceSource \| None, baseline: Workflow, candidate: Workflow, subject: dict[str, Any], existing: list[dict[str, Any]], seal: Callable[[dict[str, Any]], dict[str, Any]], stamp: str, new_id: Callable[[], str]) -> list[dict[str, Any]]` |
| Code | `repo://src/eija_studio/application/formal.py#attach` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Sealed receipts for every registered kind the source returned, skipping an exact repeat of the latest one.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.ports.FormalEvidenceSource](/symbols/application/ports/FormalEvidenceSource.md) - Where formal artifacts come from (Docker, Java, z3 or saved reports are adapter prerequisites).
* [domain.evidence_kinds.KINDS](/symbols/domain/evidence_kinds/KINDS.md) - Constant `KINDS` in `domain/evidence_kinds`.
* [domain.formal.FORMAL_PRODUCER](/symbols/domain/formal/FORMAL_PRODUCER.md) - Constant `FORMAL_PRODUCER` in `domain/formal`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.

## Referenced by

* [application.service.Studio.formal_view](/symbols/application/service/Studio.formal_view.md) - Formal evidence for a bare workflow (``eija compile``): collected and sealed in memory, never stored, never a decision.
* [application.service.Studio.verify](/symbols/application/service/Studio.verify.md) - `def verify(self, case_id: str, expected: int) -> dict[str, Any]` in `application/service`.
<!-- okf:generated:end links -->
