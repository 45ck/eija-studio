---
type: Module
title: application.formal
description: 'Formal evidence in the application layer: seal what an adapter collected, and build the packet view.'
resource: repo://src/eija_studio/application/formal.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/formal.py
  title: application/formal.py
  hash_method: ast-api-v1
  sha256: b4fb97437f415e0069783af1e7121021bf60e642e4144693fe95533b9ce138a6
notes_baseline: d585e142cd0ef76c9cbd7e1ef1ed7c8d446fbf515709afe88aea3b18d49959e9
---

# application.formal

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/formal.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Formal evidence in the application layer: seal what an adapter collected, and build the packet view.

The adapter (behind the ``FormalEvidenceSource`` port) only reads tool reports; the kernel (``domain.evidence``)
recomputes every verdict. Nothing here reads a status label from an artifact.
~~~

## Public symbols

* [`BLOCKING`](/symbols/application/formal/BLOCKING.md) (constant) - no docstring
* [`READS_REPORTS`](/symbols/application/formal/READS_REPORTS.md) (constant) - no docstring
* [`attach`](/symbols/application/formal/attach.md) (function) - Sealed receipts for every registered kind the source returned, skipping an exact repeat of the latest one.
* [`for_pack`](/symbols/application/formal/for_pack.md) (function) - Artifacts of a kind this pack does not verify from the reports become one NOT_RUN artifact with the pack's reason.
* [`pack_not_run`](/symbols/application/formal/pack_not_run.md) (function) - Why ``kind`` is NOT_RUN for ``pack`` (None when the pack verifies it from the checkout's reports).
* [`packet_view`](/symbols/application/formal/packet_view.md) (function) - The formal part of the review packet: per-kind claims, blockers, the full evidence list, explanations, and (with a pack…
* [`verifier_view`](/symbols/application/formal/verifier_view.md) (function) - Every verifier the pack declares, with the status its mode implies before any evidence is read: a kind that is not prod…
* [`what_if_model`](/symbols/application/formal/what_if_model.md) (function) - The workflow an unsupported interpretation would produce, or None (supported, unknown, or no transactions).

## Internal imports

* [`application/ports`](/modules/application/ports.md)
* [`application/witness_inspection`](/modules/application/witness_inspection.md)
* [`domain/evidence`](/modules/domain/evidence.md)
* [`domain/evidence_kinds`](/modules/domain/evidence_kinds.md)
* [`domain/formal`](/modules/domain/formal.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/policy`](/modules/domain/policy.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.ports](/modules/application/ports.md) - Application-owned ports.
* [application.witness_inspection](/modules/application/witness_inspection.md) - Immutable display projections of the deciding formal record, never new evidence or verdicts.
* [domain.evidence](/modules/domain/evidence.md) - Compatibility is computed.
* [domain.evidence_kinds](/modules/domain/evidence_kinds.md) - The registry of evidence kinds the kernel can assess (ADR-0145).
* [domain.formal](/modules/domain/formal.md) - Primitives for per-kind admissibility of formal evidence (ADR-0145, ADR-0146).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.

## Referenced by

* [application.compiler](/modules/application/compiler.md) - Compiler: model → projections + impacts + obligations + computed review packet.
* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [application.formal.BLOCKING](/symbols/application/formal/BLOCKING.md) - Constant `BLOCKING` in `application/formal`.
* [application.formal.READS_REPORTS](/symbols/application/formal/READS_REPORTS.md) - Constant `READS_REPORTS` in `application/formal`.
* [application.formal.attach](/symbols/application/formal/attach.md) - Sealed receipts for every registered kind the source returned, skipping an exact repeat of the latest one.
* [application.formal.for_pack](/symbols/application/formal/for_pack.md) - Artifacts of a kind this pack does not verify from the reports become one NOT_RUN artifact with the pack's reason.
* [application.formal.pack_not_run](/symbols/application/formal/pack_not_run.md) - Why ``kind`` is NOT_RUN for ``pack`` (None when the pack verifies it from the checkout's reports).
* [application.formal.packet_view](/symbols/application/formal/packet_view.md) - The formal part of the review packet: per-kind claims, blockers, the full evidence list, explanations, and (with a pack) the pack's declared verifiers, so a ki…
* [application.formal.verifier_view](/symbols/application/formal/verifier_view.md) - Every verifier the pack declares, with the status its mode implies before any evidence is read: a kind that is not produced for this pack (``not_run``) is NOT_…
* [application.formal.what_if_model](/symbols/application/formal/what_if_model.md) - The workflow an unsupported interpretation would produce, or None (supported, unknown, or no transactions).
<!-- okf:generated:end links -->
