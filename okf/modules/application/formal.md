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
  sha256: f95bbfd328d0ad223a9f9e815c047d0e1069344e8d429272714be6d8ce1e85b0
notes_baseline: 6a29cbe6dc51c1acacc436fae8738c02155e122e69c75d9b4d204b5788876d78
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
* [`WHAT_IF_FAULTS`](/symbols/application/formal/WHAT_IF_FAULTS.md) (constant) - no docstring
* [`attach`](/symbols/application/formal/attach.md) (function) - Sealed receipts for every registered kind the source returned, skipping an exact repeat of the latest one.
* [`packet_view`](/symbols/application/formal/packet_view.md) (function) - The formal part of the review packet: per-kind claims, blockers, the full evidence list, explanations.
* [`what_if_model`](/symbols/application/formal/what_if_model.md) (function) - The workflow an unsupported interpretation would produce (recommendation enabled, the fault applied), or None.

## Internal imports

* [`application/ports`](/modules/application/ports.md)
* [`domain/evidence`](/modules/domain/evidence.md)
* [`domain/evidence_kinds`](/modules/domain/evidence_kinds.md)
* [`domain/formal`](/modules/domain/formal.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/policy`](/modules/domain/policy.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.ports](/modules/application/ports.md) - Application-owned ports.
* [domain.evidence](/modules/domain/evidence.md) - Compatibility is computed.
* [domain.evidence_kinds](/modules/domain/evidence_kinds.md) - The registry of evidence kinds the kernel can assess (ADR-0145).
* [domain.formal](/modules/domain/formal.md) - Primitives for per-kind admissibility of formal evidence (ADR-0145, ADR-0146).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.policy](/modules/domain/policy.md) - Protected excursion policy.

## Referenced by

* [application.compiler](/modules/application/compiler.md) - Compiler: model → projections + impacts + obligations + computed review packet.
* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [application.formal.BLOCKING](/symbols/application/formal/BLOCKING.md) - Constant `BLOCKING` in `application/formal`.
* [application.formal.WHAT_IF_FAULTS](/symbols/application/formal/WHAT_IF_FAULTS.md) - Constant `WHAT_IF_FAULTS` in `application/formal`.
* [application.formal.attach](/symbols/application/formal/attach.md) - Sealed receipts for every registered kind the source returned, skipping an exact repeat of the latest one.
* [application.formal.packet_view](/symbols/application/formal/packet_view.md) - The formal part of the review packet: per-kind claims, blockers, the full evidence list, explanations.
* [application.formal.what_if_model](/symbols/application/formal/what_if_model.md) - The workflow an unsupported interpretation would produce (recommendation enabled, the fault applied), or None.
<!-- okf:generated:end links -->
