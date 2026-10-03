---
type: Module
title: domain.evidence_kinds
description: The registry of evidence kinds the kernel can assess (ADR-0145).
resource: repo://src/eija_studio/domain/evidence_kinds.py
tags:
- module
- domain
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/evidence_kinds.py
  title: domain/evidence_kinds.py
  hash_method: ast-api-v1
  sha256: 54b06034edfbc903e9ff8a56e0c163b1ed73ecf894b0a9e06d06987cd9f899f2
notes_baseline: 66b7a4e6ac2c24e3aabeee8f87aa4883c1e9ceaaa8108d09d439af14ec40dcc0
---

# domain.evidence_kinds

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | domain |
| Code | `repo://src/eija_studio/domain/evidence_kinds.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
The registry of evidence kinds the kernel can assess (ADR-0145).

A kind that is not registered here is UNKNOWN by construction: the kernel has no authority to establish a
claim it has no admissibility rule for. Adding a kind (a TLC model check, a property test, a mutation score)
means adding a module with a typed artifact shape and a pure ``check``, and one line here; nothing else in
the kernel changes.
~~~

## Public symbols

* [`KINDS`](/symbols/domain/evidence_kinds/KINDS.md) (constant) - no docstring

## Internal imports

* [`domain/formal`](/modules/domain/formal.md)
* [`domain/formal_bend`](/modules/domain/formal_bend.md)
* [`domain/formal_bmc`](/modules/domain/formal_bmc.md)
* [`domain/formal_smt`](/modules/domain/formal_smt.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.formal](/modules/domain/formal.md) - Primitives for per-kind admissibility of formal evidence (ADR-0145, ADR-0146).
* [domain.formal_bend](/modules/domain/formal_bend.md) - Admissibility of ``bend_proof`` receipts (ADR-0146; lane bend, ADR-0025 and ADR-0026).
* [domain.formal_bmc](/modules/domain/formal_bmc.md) - Admissibility of ``bounded_model_check`` receipts (ADR-0146; lane smt-bmc, ADR-0030).
* [domain.formal_smt](/modules/domain/formal_smt.md) - Admissibility of ``smt_proof`` receipts (ADR-0146; lane smt-bmc, ADR-0029).

## Referenced by

* [application.formal](/modules/application/formal.md) - Formal evidence in the application layer: seal what an adapter collected, and build the packet view.
* [domain.evidence](/modules/domain/evidence.md) - Compatibility is computed.
* [domain.evidence_kinds.KINDS](/symbols/domain/evidence_kinds/KINDS.md) - Constant `KINDS` in `domain/evidence_kinds`.
<!-- okf:generated:end links -->
