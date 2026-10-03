---
type: Architecture Decision Record
title: 'ADR-0032: Stateful differential testing against a specification-derived reference, with mutant negative controls'
description: 'The runtime''s promises are about *histories*: replay never repeats effects, a revoked actor cannot replay a cached success, a crash rolls back everything, an edit makes old instances stale but an edit back does not.'
resource: repo://docs/adr/0032-stateful-differential-testing-and-negative-controls.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0032-stateful-differential-testing-and-negative-controls.md
  title: 0032-stateful-differential-testing-and-negative-controls.md
  hash_method: lf-sha256-v1
  sha256: ca6d348aed65acecbe0a6f73b2a4ff45f9ab1e8a1d8fcd1dca6c781415a39677
notes_baseline: 32ce3a589042bf30b782ef46cf54cd815c35ba4685e8a84c6efb67c3a61267d3
---

# ADR-0032: Stateful differential testing against a specification-derived reference, with mutant negative controls

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-28 |
| Lane | property (testing) |
| Source | `repo://docs/adr/0032-stateful-differential-testing-and-negative-controls.md` |

## Decision outcome (verbatim)

> Chosen option: "stateful differential test plus explicit mutants".
>
> * `tests/property/property_reference.py` is the reference model. Its docstring cites the ARCHITECTURE.md "Runtime commit sequence" and ADR-007/011 clauses it implements, and records the one ordering the specification leaves open (where "is the action modelled?" sits). It shares the policy vocabulary with the kernel and the same authors and project, so it is a *differential oracle*, not a blinded holdout. Reports and documentation say so.
> * `tests/property/test_runtime_differential.py` generates sequences (fresh, replayed and conflicting operation ids; correct and stale versions; injected faults after each commit step; actor revocation, reassignment and re-roling; reset; the typed rejection-source edit) and, after each step, compares instances, audit, outbox, operations and case version with the reference, and each outcome (committed, replayed, refusal code) with its prediction. After the run it requires that every outcome kind was reached, so the walk cannot pass by never leaving the start state.
> * `test_reference_detects_mutants.py` and `test_properties_detect_mutants.py` monkeypatch deliberately wrong behaviour into the running kernel (replay before authority, conflict answered as replay, stale version ignored, assignment or revocation unchecked; order-sensitive or field-dropping hashes; a depth-capped or off-by-one closure; an assessor that skips the artifact hash, trusts the matrix or ignores the subject; schemas that are looser or stricter than the model) and require the relevant property to fail with an `AssertionError`.
> * A property that finds a real kernel defect does not silently patch the kernel in this lane: it is committed as `xfail(strict=True)` with the reason, and the fix is a separate kernel change.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://tests/property/property_reference.py`
* `repo://tests/property/test_runtime_differential.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0033: Mutation analysis with cosmic-ray, run natively on Windows](/adrs/0033-mutation-tool-selection.md) - The kernel test suite (88 tests at the start of this lane) passes, but a green suite says nothing about whether it would notice a wrong guard, a swapped role o…

## Referenced by

* [ADR-0031: Property-based testing with Hypothesis, in two profiles](/adrs/0031-property-based-testing-with-hypothesis.md) - The kernel's guarantees are universally quantified: "every actor x state x action", "any order of definitions hashes the same", "any dependency graph closes to…
* [Testing: property-based and model-based tests](/lanes/0031-testing-property-based-and-model-based.md) - Capability lane with ADR numbers 0031–0032 reserved.
<!-- okf:generated:end links -->
