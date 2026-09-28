# ADR-0037: Measure design, performance and scaling with radon, grimp and coverage.py, and fit models rather than assert them

* Status: accepted
* Date: 2026-09-28
* Lane: metrics

## Context and problem statement

EIJA Studio claims a clean layered design (domain and application never import adapters), an O(V+E) impact closure and an interactive local UI. None of that was measured. Without numbers, "clean", "fast" and "linear" are opinions, and a regression is invisible until a review notices it. We need reproducible quantitative evidence that (a) states its formula and source, (b) separates deterministic structure from noisy timing, and (c) never turns a missing input into a pass.

## Decision drivers

* ADR-0016: adopt mature open source, write only the glue.
* Honest evidence: a measurement is not a proof, a static proxy is not a runtime guarantee, an absent prerequisite is NOT_RUN.
* Reproducibility: structural metrics must be a pure function of the source tree; timings must be labelled measurements with their platform.
* The machine is shared (16 GB, several agents): collectors must be light and serial.

## Considered options

* Adopt radon (cyclomatic complexity, maintainability index, raw counts), grimp (import graph), coverage.py (coverage) and the standard library (`statistics`, `time`) for fits and timings; write collectors, budgets and a static renderer.
* Adopt a hosted quality service (SonarQube, CodeClimate). Rejected: network and account dependency, opaque formulas, no place for domain-specific models such as the runtime-matrix cost.
* Adopt wily, pylint or xenon as the front end. Rejected as the primary path: they wrap the same radon numbers with a CLI-shaped output; the Martin package metrics and the performance and scaling models need custom collection anyway, so one small package keeps a single JSON schema.
* Adopt numpy/scipy for regression. Rejected: two-parameter least squares on tens of points needs `statistics.linear_regression` and a 20-line normal-equations solver, not a 30 MB dependency.
* Adopt pytest-benchmark or locust for latency. Rejected for now: the questions are per-endpoint percentiles on an in-process app and a real uvicorn server, which a 60-line harness answers; load testing is a different question (concurrent users) that this lane does not claim to answer.

## Decision outcome

Chosen option: the first, because it keeps every number traceable to a named formula and source and needs no new heavyweight dependency.

The package `quality/metrics/` produces one document, `reports/metrics.json` (schema `eija.metrics.v1`), with eight sections: Martin package metrics (grimp + ast), cyclomatic complexity and maintainability (radon), test inventory and coverage (ast, pytest collection, coverage.py), aggregation of other lanes' reports, HTTP latency on two transports (Starlette TestClient and a real uvicorn server on an ephemeral port) against the 100 ms and 400 ms thresholds, a fit of `verify_runtime` time against matrix size, a fit of `domain.impact.closure` time against graph size, and verification yield (states explored per technique).

Design rules that are part of the decision:

1. Sections split into deterministic (structure, complexity, inventory, aggregation) and measurements (performance, scaling, yield). The document says which; drift checks apply only to the rendering of a committed snapshot, never to timings.
2. Every collector states `not_measured`. Every section is `MEASURED` or `NOT_RUN` with a reason.
3. Models are fitted, then falsified: the closure fit is compared with a quadratic alternative and with the log-log exponent; the single-coefficient V+E model is reported as measured even where its R^2 is only about 0.9, and a two-term model (node cost and edge cost fitted separately) is reported beside it.
4. Measurement harness overrides are explicit: the identity provider keeps its real byte hashing but is forced `trusted_fixture=True` (marked `identity_source: metrics-harness`), the same idiom as `tests/conftest.py`; the kernel's actor list is patched only inside the measurement of matrix size, never in the kernel.

### Consequences

* Good: a regression in layering, complexity, coverage or latency becomes a failing budget (ADR-0038) with the formula and source documented in `docs/metrics/README.md`.
* Good: the dashboard (`docs/metrics/index.html`) is static, offline and reproducible from the committed snapshot.
* Good: the analysis surfaced real findings instead of confirming expectations, for example that the domain layer sits in Martin's "zone of pain" by construction (D = 1.0) and that `verify` takes one to a few seconds and exceeds the Doherty threshold.
* Bad: timing measurements depend on the machine and its load; a budget on them can fail on a busy PC. They are labelled as such and the snapshot names the platform.
* Bad: module-level coupling and a Protocol/ABC share are proxies for the class-level definitions in Martin's papers.
* Revisit when: another platform (Linux CI, macOS) produces a snapshot, or a second lane needs a numerical library, at which point adopting numpy for all lanes may be cheaper than each lane's own solver.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| radon, grimp, coverage.py | Used directly; the custom code only shapes their output | Swap the collector functions; the JSON schema does not change |
| wily, xenon, pylint | Same radon numbers with a different CLI; no Martin metrics, no timing models | Add as extra front ends if a team prefers them |
| pytest-benchmark, locust | Answer micro-benchmark and load questions, not per-endpoint percentiles against Doherty on two transports | Replace `perf.py` transports behind the `Call` signature |
| numpy, scipy | Overkill for two-parameter OLS on tens of points | Replace `common.ols`/`ols_multi`; tests pin their behaviour |
| custom: `quality/metrics/` (collectors, budgets, SVG renderer) | No OSS tool produces this combined, offline, deterministic dashboard from EIJA's own models | Keep the collectors; the renderer can be replaced by any templating tool reading `metrics.json` |
