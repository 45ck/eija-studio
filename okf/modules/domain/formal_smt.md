---
type: Module
title: domain.formal_smt
description: Admissibility of ``smt_proof`` receipts (ADR-0146; lane smt-bmc, ADR-0029).
resource: repo://src/eija_studio/domain/formal_smt.py
tags:
- module
- domain
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal_smt.py
  title: domain/formal_smt.py
  hash_method: ast-api-v1
  sha256: c9185b2da0afc8b90bb4c74359c5123f6948bb090b75a3b7e78861de2a9ad56f
notes_baseline: 7ffc946360dc1b1bb13fed782802972cea5d20cfdba05826744215351ab9b081
---

# domain.formal_smt

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | domain |
| Code | `repo://src/eija_studio/domain/formal_smt.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Admissibility of ``smt_proof`` receipts (ADR-0146; lane smt-bmc, ADR-0029).

Recomputed here from the raw artifact: every required invariant is ``proved`` (a refuted one is a FAIL and
its witness is shown), the proof is not vacuous, the accepted set was enumerated completely and contains the
candidate under review, the encoding of the policy agrees with the real ``check_policy`` on a declared
minimum number of differential candidates with no disagreement, each named leave-one-out control produced a
counterexample, and the sources the report is about are the sources now in the checkout.

Accepted under the sealed local producer, not recomputed: that Z3 answered ``unsat`` (no checkable proof
object is exported), and the observed current bytes of the policy sources.
~~~

## Public symbols

* [`ACCEPTED_Z3_PACKAGES`](/symbols/domain/formal_smt/ACCEPTED_Z3_PACKAGES.md) (constant) - no docstring
* [`DOES_NOT_ESTABLISH`](/symbols/domain/formal_smt/DOES_NOT_ESTABLISH.md) (constant) - no docstring
* [`ESTABLISHES`](/symbols/domain/formal_smt/ESTABLISHES.md) (constant) - no docstring
* [`INVARIANTS`](/symbols/domain/formal_smt/INVARIANTS.md) (constant) - no docstring
* [`KEYS`](/symbols/domain/formal_smt/KEYS.md) (constant) - no docstring
* [`MIN_DIFFERENTIAL_CANDIDATES`](/symbols/domain/formal_smt/MIN_DIFFERENTIAL_CANDIDATES.md) (constant) - no docstring
* [`NAMED_CONTROLS`](/symbols/domain/formal_smt/NAMED_CONTROLS.md) (constant) - no docstring
* [`PREREQUISITES`](/symbols/domain/formal_smt/PREREQUISITES.md) (constant) - no docstring
* [`PROTOCOL`](/symbols/domain/formal_smt/PROTOCOL.md) (constant) - no docstring
* [`SOURCES`](/symbols/domain/formal_smt/SOURCES.md) (constant) - no docstring
* [`SPEC`](/symbols/domain/formal_smt/SPEC.md) (constant) - no docstring
* [`SUBJECT_FUNCTION`](/symbols/domain/formal_smt/SUBJECT_FUNCTION.md) (constant) - no docstring
* [`check`](/symbols/domain/formal_smt/check.md) (function) - no docstring
* [`describe`](/symbols/domain/formal_smt/describe.md) (function) - no docstring
* [`explain`](/symbols/domain/formal_smt/explain.md) (function) - Leave-one-out counterexamples for the policy clauses behind the policy errors the kernel reports.

## Internal imports

* [`domain/formal`](/modules/domain/formal.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.formal](/modules/domain/formal.md) - Primitives for per-kind admissibility of formal evidence (ADR-0145, ADR-0146).

## Referenced by

* [domain.evidence_kinds](/modules/domain/evidence_kinds.md) - The registry of evidence kinds the kernel can assess (ADR-0145).
* [domain.formal_smt.ACCEPTED_Z3_PACKAGES](/symbols/domain/formal_smt/ACCEPTED_Z3_PACKAGES.md) - Constant `ACCEPTED_Z3_PACKAGES` in `domain/formal_smt`.
* [domain.formal_smt.DOES_NOT_ESTABLISH](/symbols/domain/formal_smt/DOES_NOT_ESTABLISH.md) - Constant `DOES_NOT_ESTABLISH` in `domain/formal_smt`.
* [domain.formal_smt.ESTABLISHES](/symbols/domain/formal_smt/ESTABLISHES.md) - Constant `ESTABLISHES` in `domain/formal_smt`.
* [domain.formal_smt.INVARIANTS](/symbols/domain/formal_smt/INVARIANTS.md) - Constant `INVARIANTS` in `domain/formal_smt`.
* [domain.formal_smt.KEYS](/symbols/domain/formal_smt/KEYS.md) - Constant `KEYS` in `domain/formal_smt`.
* [domain.formal_smt.MIN_DIFFERENTIAL_CANDIDATES](/symbols/domain/formal_smt/MIN_DIFFERENTIAL_CANDIDATES.md) - Constant `MIN_DIFFERENTIAL_CANDIDATES` in `domain/formal_smt`.
* [domain.formal_smt.NAMED_CONTROLS](/symbols/domain/formal_smt/NAMED_CONTROLS.md) - Constant `NAMED_CONTROLS` in `domain/formal_smt`.
* [domain.formal_smt.PREREQUISITES](/symbols/domain/formal_smt/PREREQUISITES.md) - Constant `PREREQUISITES` in `domain/formal_smt`.
* [domain.formal_smt.PROTOCOL](/symbols/domain/formal_smt/PROTOCOL.md) - Constant `PROTOCOL` in `domain/formal_smt`.
* [domain.formal_smt.SOURCES](/symbols/domain/formal_smt/SOURCES.md) - Constant `SOURCES` in `domain/formal_smt`.
* [domain.formal_smt.SPEC](/symbols/domain/formal_smt/SPEC.md) - Constant `SPEC` in `domain/formal_smt`.
* [domain.formal_smt.SUBJECT_FUNCTION](/symbols/domain/formal_smt/SUBJECT_FUNCTION.md) - Constant `SUBJECT_FUNCTION` in `domain/formal_smt`.
* [domain.formal_smt.check](/symbols/domain/formal_smt/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_smt`.
* [domain.formal_smt.describe](/symbols/domain/formal_smt/describe.md) - `def describe(a: dict[str, Any]) -> dict[str, Any]` in `domain/formal_smt`.
* [domain.formal_smt.explain](/symbols/domain/formal_smt/explain.md) - Leave-one-out counterexamples for the policy clauses behind the policy errors the kernel reports.
<!-- okf:generated:end links -->
