---
type: Module
title: domain.formal_bmc
description: Admissibility of ``bounded_model_check`` receipts (ADR-0146; lane smt-bmc, ADR-0030).
resource: repo://src/eija_studio/domain/formal_bmc.py
tags:
- module
- domain
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal_bmc.py
  title: domain/formal_bmc.py
  hash_method: ast-api-v1
  sha256: a93e0f819903408a95e4766fdaac3ee67b788f188c663aedaa1dc50ce9e59972
notes_baseline: 24ab9fe0623beca5b5df369d03b0a772a125b432dffe501ff41c45ac11d756d7
---

# domain.formal_bmc

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | domain |
| Code | `repo://src/eija_studio/domain/formal_bmc.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Admissibility of ``bounded_model_check`` receipts (ADR-0146; lane smt-bmc, ADR-0030).

Bounded means bounded: this kind can never say more than "no violation within depth k over the stated
alphabet". Recomputed here from the raw artifact: the declared depth is at least the kernel's minimum, every
explored model was searched without a time-cap cut, produced observations and provoked the outcome classes
it should (otherwise the alphabet never reached the interesting behaviour), no counterexample was found,
each seeded runtime fault was detected by the same search (the self-test is the negative control), and the
candidate under review is one of the models explored.

Accepted under the sealed local producer, not recomputed: the counts themselves (the search is not re-run
by the kernel) and the observed current bytes of the runtime sources.
~~~

## Public symbols

* [`DOES_NOT_ESTABLISH`](/symbols/domain/formal_bmc/DOES_NOT_ESTABLISH.md) (constant) - no docstring
* [`ESTABLISHES`](/symbols/domain/formal_bmc/ESTABLISHES.md) (constant) - no docstring
* [`KEYS`](/symbols/domain/formal_bmc/KEYS.md) (constant) - no docstring
* [`MIN_DEPTH`](/symbols/domain/formal_bmc/MIN_DEPTH.md) (constant) - no docstring
* [`MUTANTS`](/symbols/domain/formal_bmc/MUTANTS.md) (constant) - no docstring
* [`PREREQUISITES`](/symbols/domain/formal_bmc/PREREQUISITES.md) (constant) - no docstring
* [`PROTOCOL`](/symbols/domain/formal_bmc/PROTOCOL.md) (constant) - no docstring
* [`SOURCES`](/symbols/domain/formal_bmc/SOURCES.md) (constant) - no docstring
* [`SPEC`](/symbols/domain/formal_bmc/SPEC.md) (constant) - no docstring
* [`STATE_INVARIANTS`](/symbols/domain/formal_bmc/STATE_INVARIANTS.md) (constant) - no docstring
* [`STEP_INVARIANTS`](/symbols/domain/formal_bmc/STEP_INVARIANTS.md) (constant) - no docstring
* [`SUBJECT_FUNCTION`](/symbols/domain/formal_bmc/SUBJECT_FUNCTION.md) (constant) - no docstring
* [`check`](/symbols/domain/formal_bmc/check.md) (function) - no docstring
* [`describe`](/symbols/domain/formal_bmc/describe.md) (function) - no docstring
* [`explain`](/symbols/domain/formal_bmc/explain.md) (function) - The bounded search explains no policy error: its faults are runtime faults, not workflow faults.

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
* [domain.formal_bmc.DOES_NOT_ESTABLISH](/symbols/domain/formal_bmc/DOES_NOT_ESTABLISH.md) - Constant `DOES_NOT_ESTABLISH` in `domain/formal_bmc`.
* [domain.formal_bmc.ESTABLISHES](/symbols/domain/formal_bmc/ESTABLISHES.md) - Constant `ESTABLISHES` in `domain/formal_bmc`.
* [domain.formal_bmc.KEYS](/symbols/domain/formal_bmc/KEYS.md) - Constant `KEYS` in `domain/formal_bmc`.
* [domain.formal_bmc.MIN_DEPTH](/symbols/domain/formal_bmc/MIN_DEPTH.md) - Constant `MIN_DEPTH` in `domain/formal_bmc`.
* [domain.formal_bmc.MUTANTS](/symbols/domain/formal_bmc/MUTANTS.md) - Constant `MUTANTS` in `domain/formal_bmc`.
* [domain.formal_bmc.PREREQUISITES](/symbols/domain/formal_bmc/PREREQUISITES.md) - Constant `PREREQUISITES` in `domain/formal_bmc`.
* [domain.formal_bmc.PROTOCOL](/symbols/domain/formal_bmc/PROTOCOL.md) - Constant `PROTOCOL` in `domain/formal_bmc`.
* [domain.formal_bmc.SOURCES](/symbols/domain/formal_bmc/SOURCES.md) - Constant `SOURCES` in `domain/formal_bmc`.
* [domain.formal_bmc.SPEC](/symbols/domain/formal_bmc/SPEC.md) - Constant `SPEC` in `domain/formal_bmc`.
* [domain.formal_bmc.STATE_INVARIANTS](/symbols/domain/formal_bmc/STATE_INVARIANTS.md) - Constant `STATE_INVARIANTS` in `domain/formal_bmc`.
* [domain.formal_bmc.STEP_INVARIANTS](/symbols/domain/formal_bmc/STEP_INVARIANTS.md) - Constant `STEP_INVARIANTS` in `domain/formal_bmc`.
* [domain.formal_bmc.SUBJECT_FUNCTION](/symbols/domain/formal_bmc/SUBJECT_FUNCTION.md) - Constant `SUBJECT_FUNCTION` in `domain/formal_bmc`.
* [domain.formal_bmc.check](/symbols/domain/formal_bmc/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_bmc`.
* [domain.formal_bmc.describe](/symbols/domain/formal_bmc/describe.md) - `def describe(a: dict[str, Any]) -> dict[str, Any]` in `domain/formal_bmc`.
* [domain.formal_bmc.explain](/symbols/domain/formal_bmc/explain.md) - The bounded search explains no policy error: its faults are runtime faults, not workflow faults.
<!-- okf:generated:end links -->
