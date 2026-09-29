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
  sha256: 4fd44ad2297d38eb44fad59a9f0e30dd379c87493b038495824a267e7f13561c
notes_baseline: e583bc3bed72f945aadbce27f18af49f47ab463b625df46aced78885eed2ce7b
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
* [`attach`](/symbols/application/formal/attach.md) (function) - Sealed receipts for every registered kind the source returned, skipping an exact repeat of the latest one.
* [`packet_view`](/symbols/application/formal/packet_view.md) (function) - The formal part of the review packet: per-kind claims, blockers, the full evidence list, explanations.
* [`what_if_model`](/symbols/application/formal/what_if_model.md) (function) - The workflow an unsupported interpretation would produce, or None (supported, unknown, or no transactions).

## Internal imports

* [`application/ports`](/modules/application/ports.md)
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
* [application.formal.attach](/symbols/application/formal/attach.md) - Sealed receipts for every registered kind the source returned, skipping an exact repeat of the latest one.
* [application.formal.packet_view](/symbols/application/formal/packet_view.md) - The formal part of the review packet: per-kind claims, blockers, the full evidence list, explanations.
* [application.formal.what_if_model](/symbols/application/formal/what_if_model.md) - The workflow an unsupported interpretation would produce, or None (supported, unknown, or no transactions).
<!-- okf:generated:end links -->
