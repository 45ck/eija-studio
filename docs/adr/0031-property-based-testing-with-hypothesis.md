# ADR-0031: Property-based testing with Hypothesis, in two profiles

* Status: accepted
* Date: 2026-09-28
* Lane: property (testing)

## Context and problem statement

The kernel's guarantees are universally quantified: "every actor x state x action", "any order of definitions hashes the same", "any dependency graph closes to a fixed point", "any single-field edit of a receipt is detected". The existing suite checks hand-picked examples and one bounded 125-cell matrix. Example tests cannot say that the *next* input, or the next *sequence* of inputs, behaves. We need generated inputs, shrinking to minimal counterexamples, and a way to run more of them before a release than on every push, without making the gate flaky.

## Decision drivers

* Reproducibility: a red PR gate must reproduce on another machine; a green one must not be luck.
* Depth on demand: a release tier should search harder than the PR tier.
* OSS first ([ADR-0016](0016-oss-first-adapters-not-engines.md)): no custom generator engine.
* Honest evidence: example counts are reported, and a missing install is `NOT_RUN`.

## Considered options

* Hypothesis (MPL-2.0) with `hypothesis-jsonschema` for schema-driven generation (chosen)
* Hand-rolled random loops with a seed (rejected: no shrinking, no stateful engine, no example database)
* Schemathesis (rejected for this lane: it drives an HTTP API from OpenAPI; the contract-drift question here is schema versus Pydantic model, not schema versus server)
* pytest-quickcheck (unmaintained, no stateful testing)

## Decision outcome

Chosen option: "Hypothesis", because it is the standard property-based engine for Python, ships stateful (`RuleBasedStateMachine`) testing, shrinking and a pytest plugin, and is pinned in the `testing` extra.

Two profiles, selected with `EIJA_HYPOTHESIS_PROFILE` (`tests/property/conftest.py`):

* `ci`, the default: `derandomize=True`, database off, small example budgets (each test states its own base budget). The same examples run on every machine, so failures reproduce and the gate is not stochastic. Run by `nox -s property` (tag `full`).
* `deep`: random seeds, ten times the budgets, failures saved to `.hypothesis/examples` (gitignored) and replayed by later runs. Run by `nox -s property_deep` (tag `release`). It finds bugs; it is not reproducible by design, so a `deep` failure is turned into an explicit regression test or `@example`.

A bare `pytest` skips the property suite (it takes minutes) and says so; it runs with `pytest tests/property`, `-m property` or the nox sessions. Each nox run writes `reports/testing/property.json` (`property-deep.json` for deep): profile, library versions, per-test generated / valid / invalid example counts and, for the stateful test, how often each outcome (Committed, Replayed, each refusal code) was reached.

### Consequences

* Good: universally quantified claims are exercised over generated inputs, with minimal counterexamples.
* Good: the `ci` tier is deterministic; the `deep` tier scales without changing any test.
* Bad: minutes rather than seconds, and generators are code that can be wrong. Mitigation: negative controls ([ADR-0032](0032-stateful-differential-testing-and-negative-controls.md)).
* Bad: `hypothesis-jsonschema` handles the Pydantic-emitted schemas today; an unsupported keyword in a future schema fails the contract tests loudly rather than skipping.
* Revisit when: the suite exceeds five minutes in the `ci` profile, or Hypothesis changes the statistics collector or the per-test settings attribute that `conftest.py` and the mutant tests rely on (versions are pinned).

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| Hypothesis, hypothesis-jsonschema, jsonschema | Fully used. Custom code is limited to strategies for EIJA workflows, a receipt mutation engine, profile wiring and the JSON report writer | Any of the three can be replaced independently; the report writer reads Hypothesis' statistics collector |
