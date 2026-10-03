---
type: Architecture Decision Record
title: 'ADR-0031: Property-based testing with Hypothesis, in two profiles'
description: 'The kernel''s guarantees are universally quantified: "every actor x state x action", "any order of definitions hashes the same", "any dependency graph closes to a fixed point", "any single-field edit of a receipt is dete…'
resource: repo://docs/adr/0031-property-based-testing-with-hypothesis.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0031-property-based-testing-with-hypothesis.md
  title: 0031-property-based-testing-with-hypothesis.md
  hash_method: lf-sha256-v1
  sha256: 5136fb36846ad6fdfa2af243d88afc9c5309deb6b2c8a83d634c762a32201cdd
notes_baseline: 49c951cc26ea2645dacb0f80c0caad78c9c4bfddf044dc8dba006d99d3c1be71
---

# ADR-0031: Property-based testing with Hypothesis, in two profiles

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-28 |
| Lane | property (testing) |
| Source | `repo://docs/adr/0031-property-based-testing-with-hypothesis.md` |

## Decision outcome (verbatim)

> Chosen option: "Hypothesis", because it is the standard property-based engine for Python, ships stateful (`RuleBasedStateMachine`) testing, shrinking and a pytest plugin, and is pinned in the `testing` extra.
>
> Two profiles, selected with `EIJA_HYPOTHESIS_PROFILE` (`tests/property/conftest.py`):
>
> * `ci`, the default: `derandomize=True`, database off, small example budgets (each test states its own base budget). The same examples run on every machine, so failures reproduce and the gate is not stochastic. Run by `nox -s property` (tag `full`).
> * `deep`: random seeds, ten times the budgets, failures saved to `.hypothesis/examples` (gitignored) and replayed by later runs. Run by `nox -s property_deep` (tag `release`). It finds bugs; it is not reproducible by design, so a `deep` failure is turned into an explicit regression test or `@example`.
>
> A bare `pytest` skips the property suite (it takes minutes) and says so; it runs with `pytest tests/property`, `-m property` or the nox sessions. Each nox run writes `reports/testing/property.json` (`property-deep.json` for deep): profile, library versions, per-test generated / valid / invalid example counts and, for the stateful test, how often each outcome (Committed, Replayed, each refusal code) was reached.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://tests/property/conftest.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0032: Stateful differential testing against a specification-derived reference, with mutant negative controls](/adrs/0032-stateful-differential-testing-and-negative-controls.md) - The runtime's promises are about *histories*: replay never repeats effects, a revoked actor cannot replay a cached success, a crash rolls back everything, an e…

## Referenced by

* [ADR-0028: Model-to-code conformance by exhaustive graph comparison and TLC trace validation](/adrs/0028-runtime-conformance-by-graph-comparison-and-trace-validation.md) - A TLA+ proof about `Excursion.tla` is a proof about the model.
* [ADR-0030: Bounded model checking by explicit-state search over the real runtime](/adrs/0030-bounded-model-checking-of-the-real-runtime.md) - The runtime matrix in `application/verifier.py` is one-step: five actors times five states times five actions, each cell from a fresh instance.
* [Testing: property-based and model-based tests](/lanes/0031-testing-property-based-and-model-based.md) - Capability lane with ADR numbers 0031–0032 reserved.
<!-- okf:generated:end links -->
