---
type: Architecture Decision Record
title: 'ADR-0037: Measure design, performance and scaling with radon, grimp and coverage.py, and fit models rather than assert them'
description: EIJA Studio claims a clean layered design (domain and application never import adapters), an O(V+E) impact closure and an interactive local UI.
resource: repo://docs/adr/0037-metrics-and-quantitative-models.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0037-metrics-and-quantitative-models.md
  title: 0037-metrics-and-quantitative-models.md
  hash_method: lf-sha256-v1
  sha256: bea151867a106d4541508671fc4dcebc519e092e591fad1ace60fbc0c3dab3ae
notes_baseline: 84e45c54955ef7e7f66ca9ae5df4e620f329b41442a9a478ecd11c58a070f890
---

# ADR-0037: Measure design, performance and scaling with radon, grimp and coverage.py, and fit models rather than assert them

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-28 |
| Lane | metrics |
| Source | `repo://docs/adr/0037-metrics-and-quantitative-models.md` |

## Decision outcome (verbatim)

> Chosen option: the first, because it keeps every number traceable to a named formula and source and needs no new heavyweight dependency.
>
> The package `quality/metrics/` produces one document, `reports/metrics.json` (schema `eija.metrics.v1`), with eight sections: Martin package metrics (grimp + ast), cyclomatic complexity and maintainability (radon), test inventory and coverage (ast, pytest collection, coverage.py), aggregation of other lanes' reports, HTTP latency on two transports (Starlette TestClient and a real uvicorn server on an ephemeral port) against the 100 ms and 400 ms thresholds, a fit of `verify_runtime` time against matrix size, a fit of `domain.impact.closure` time against graph size, and verification yield (states explored per technique).
>
> Design rules that are part of the decision:
>
> 1. Sections split into deterministic (structure, complexity, inventory, aggregation) and measurements (performance, scaling, yield). The document says which; drift checks apply only to the rendering of a committed snapshot, never to timings.
> 2. Every collector states `not_measured`. Every section is `MEASURED` or `NOT_RUN` with a reason.
> 3. Models are fitted, then falsified: the closure fit is compared with a quadratic alternative and with the log-log exponent; the requested single-coefficient V+E model is reported and budgeted (SCALE-04, R^2 at least 0.85, because it fits at about 0.90 to 0.93), and a two-term model (node cost and edge cost fitted separately, SCALE-01) is reported beside it; the two-term fit is not evidence for the single-term model.
> 4. Measurement harness overrides are explicit: the identity provider keeps its real byte hashing but is forced `trusted_fixture=True` (marked `identity_source: metrics-harness`), the same idiom as `tests/conftest.py`; the kernel's actor list is patched only inside the measurement of matrix size, never in the kernel.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://docs/metrics/README.md`
* `repo://quality/gates/complexity_ratchet.py`
* `repo://tests/conftest.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0038: Metric budgets are tests with a stated basis, and timing budgets are advisory in the full gate](/adrs/0038-metric-budgets-as-tests.md) - Metrics that nobody enforces decay into a dashboard.

## Referenced by

* [ADR-0097: Impact, ranking and evidence-status mathematics: fixed points, integer relevance, greedy selection, count vectors, and no confidence percentage](/adrs/0097-weave-impact-ranking-math.md) - The weave graph must answer six questions about a change: what does it affect, what should an agent or a person read, which tests give the cheapest useful re-c…
* [Metrics and quantitative models](/lanes/0037-metrics-and-quantitative-models.md) - Capability lane with ADR numbers 0037–0038 reserved.
<!-- okf:generated:end links -->
