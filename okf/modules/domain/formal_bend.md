---
type: Module
title: domain.formal_bend
description: Admissibility of ``bend_proof`` receipts (ADR-0146; lane bend, ADR-0025 and ADR-0026).
resource: repo://src/eija_studio/domain/formal_bend.py
tags:
- module
- domain
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal_bend.py
  title: domain/formal_bend.py
  hash_method: ast-api-v1
  sha256: 2bfe9af05e530ab1edb5c1a15fd502c461a3e3ed074990eb4b2802ad96522b3e
notes_baseline: 68a54e4ed9355f87b53c45f8b94aee1b1fa058befb5599e24c55f040b6266f9e
---

# domain.formal_bend

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | domain |
| Code | `repo://src/eija_studio/domain/formal_bend.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Admissibility of ``bend_proof`` receipts (ADR-0146; lane bend, ADR-0025 and ADR-0026).

Recomputed here from the raw artifact: every required law is PROVEN by the full ``--verdict`` run, every
seeded-unsafe model makes exactly the laws it was seeded to break fail (the kernel pins that expectation,
it does not read the artifact's own), each unsafe model has a confirmed concrete counterexample, the model
was checked against the runtime by a conformance test above a declared minimum, and the model that was
proved is the model of the CURRENT baseline and candidate.

Accepted under the sealed local producer, not recomputed: that Bend's kernel really answered ``PROVEN``
(no proof certificate leaves the container), and the observed current bytes of the model files.
~~~

## Public symbols

* [`ACCEPTED_BEND_VERSIONS`](/symbols/domain/formal_bend/ACCEPTED_BEND_VERSIONS.md) (constant) - no docstring
* [`CONTROLS`](/symbols/domain/formal_bend/CONTROLS.md) (constant) - no docstring
* [`DOES_NOT_ESTABLISH`](/symbols/domain/formal_bend/DOES_NOT_ESTABLISH.md) (constant) - no docstring
* [`ESTABLISHES`](/symbols/domain/formal_bend/ESTABLISHES.md) (constant) - no docstring
* [`KEYS`](/symbols/domain/formal_bend/KEYS.md) (constant) - no docstring
* [`LAWS`](/symbols/domain/formal_bend/LAWS.md) (constant) - no docstring
* [`MIN_CONFORMANCE_CELLS`](/symbols/domain/formal_bend/MIN_CONFORMANCE_CELLS.md) (constant) - no docstring
* [`MODEL_FILES`](/symbols/domain/formal_bend/MODEL_FILES.md) (constant) - no docstring
* [`PREREQUISITES`](/symbols/domain/formal_bend/PREREQUISITES.md) (constant) - no docstring
* [`PROTOCOL`](/symbols/domain/formal_bend/PROTOCOL.md) (constant) - no docstring
* [`SPEC`](/symbols/domain/formal_bend/SPEC.md) (constant) - no docstring
* [`check`](/symbols/domain/formal_bend/check.md) (function) - no docstring
* [`describe`](/symbols/domain/formal_bend/describe.md) (function) - no docstring
* [`explain`](/symbols/domain/formal_bend/explain.md) (function) - Negative-control counterexamples whose fault class is one the kernel's own policy reports.

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
* [domain.formal_bend.ACCEPTED_BEND_VERSIONS](/symbols/domain/formal_bend/ACCEPTED_BEND_VERSIONS.md) - Constant `ACCEPTED_BEND_VERSIONS` in `domain/formal_bend`.
* [domain.formal_bend.CONTROLS](/symbols/domain/formal_bend/CONTROLS.md) - Constant `CONTROLS` in `domain/formal_bend`.
* [domain.formal_bend.DOES_NOT_ESTABLISH](/symbols/domain/formal_bend/DOES_NOT_ESTABLISH.md) - Constant `DOES_NOT_ESTABLISH` in `domain/formal_bend`.
* [domain.formal_bend.ESTABLISHES](/symbols/domain/formal_bend/ESTABLISHES.md) - Constant `ESTABLISHES` in `domain/formal_bend`.
* [domain.formal_bend.KEYS](/symbols/domain/formal_bend/KEYS.md) - Constant `KEYS` in `domain/formal_bend`.
* [domain.formal_bend.LAWS](/symbols/domain/formal_bend/LAWS.md) - Constant `LAWS` in `domain/formal_bend`.
* [domain.formal_bend.MIN_CONFORMANCE_CELLS](/symbols/domain/formal_bend/MIN_CONFORMANCE_CELLS.md) - Constant `MIN_CONFORMANCE_CELLS` in `domain/formal_bend`.
* [domain.formal_bend.MODEL_FILES](/symbols/domain/formal_bend/MODEL_FILES.md) - Constant `MODEL_FILES` in `domain/formal_bend`.
* [domain.formal_bend.PREREQUISITES](/symbols/domain/formal_bend/PREREQUISITES.md) - Constant `PREREQUISITES` in `domain/formal_bend`.
* [domain.formal_bend.PROTOCOL](/symbols/domain/formal_bend/PROTOCOL.md) - Constant `PROTOCOL` in `domain/formal_bend`.
* [domain.formal_bend.SPEC](/symbols/domain/formal_bend/SPEC.md) - Constant `SPEC` in `domain/formal_bend`.
* [domain.formal_bend.check](/symbols/domain/formal_bend/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_bend`.
* [domain.formal_bend.describe](/symbols/domain/formal_bend/describe.md) - `def describe(a: dict[str, Any]) -> dict[str, Any]` in `domain/formal_bend`.
* [domain.formal_bend.explain](/symbols/domain/formal_bend/explain.md) - Negative-control counterexamples whose fault class is one the kernel's own policy reports.
<!-- okf:generated:end links -->
