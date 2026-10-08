# ADR-0038: Metric budgets are tests with a stated basis, and timing budgets are advisory in the full gate

* Status: accepted
* Date: 2026-09-28
* Lane: metrics

## Context and problem statement

Metrics that nobody enforces decay into a dashboard. But a budget can be dishonest in three ways: a limit chosen to make today's number pass and presented as a standard; a timing budget that fails because the machine is busy and trains people to ignore red; and a budget that silently passes when its input was never measured.

## Decision drivers

* A budget must say why its limit is what it is.
* A missing input is NOT_RUN, never PASS.
* Timing on a shared 16 GB PC is noisy; a failure must mean a real regression, so a timing budget cannot turn the shared full gate red on load alone.
* Budgets are used in three places (pytest, the nox session, the dashboard) and must have one definition.

## Considered options

* One table of budgets in code (`quality/metrics/budgets.py`), each tagged with a basis (principled, external, ratchet), evaluated by pytest, by `nox -s metrics` and by the renderer.
* Thresholds in a config file read by a generic gate (import-linter contracts, radon `--min`). Partly adopted elsewhere (the quality lane owns architecture fitness functions, ADR-0035); here the thresholds also cover measured models (R^2, percentiles) that those tools cannot express.
* No budgets, dashboard only. Rejected: nothing would fail.

## Decision outcome

Chosen option: one table in code, with three kinds of basis.

* Principled: holds at any size. No dependency cycles, the domain imports no other layer and has instability at most 0.1, no Stable Dependencies Principle violation, R^2 at least 0.9 for a linear fit, log-log exponent in [0.8, 1.2], every layer has a directly importing test, no lane report says FAIL, UNKNOWN or UNREADABLE (a present report must say PASS or NOT_RUN).
* External: a published threshold. Doherty and Thadani (1982): p95 of interactive endpoints under 400 ms. The `verify` endpoint is a long-running computation (one to a few seconds depending on machine load, because it runs a 125-cell isolated matrix), so it is budgeted separately at 10 s (Nielsen's limit for keeping attention) and its excess over 400 ms is reported, not hidden: it needs a progress indication in the UI.
* Ratchet: current value plus headroom, to catch regressions (minimum maintainability index 20, coverage at least 75 percent line+branch on a coverage report measured on the current tree, non-domain layers within 0.5 of the main sequence, the requested single-term closure fit at R^2 0.85, the verify() time fit at R^2 0.8 because ten points on a shared machine ranged from 0.896 to 0.99). Per-function cyclomatic complexity is deliberately NOT budgeted here: the quality lane owns it (`quality/gates/complexity_ratchet.py`, default 10 with a pinned debt list, stricter than anything this lane had), and one budget per property avoids two gates disagreeing. A ratchet is a guard rail and is labelled as one. It is tightened by a deliberate commit, never loosened to make a build pass without an ADR or a justification in the PR.

Deliberate non-budget: the domain layer's distance from the main sequence. The formula gives D = 1.0 (stable, and concrete because it holds frozen contracts and pure rules with no Protocol). Adding an abstraction only to move the number would be the speculative abstraction ADR-0016 and AGENTS.md forbid. The number is reported with its zone; the budgets check what matters for that layer (I near 0, Ce = 0).

Evaluation rules: an extractor that cannot find its section yields NOT_RUN. A coverage report that is not bound to the current source and test tree (SHA-256 recorded next to it) is NOT_RUN, not a pass on old evidence.

Timing budgets are marked `kind: timing` and are wall-clock measurements. In `nox -s metrics` (tag `full`, the shared gate) they are printed as advisory and cannot fail the session; the structural budgets and the drift check do. In `nox -s metrics_report` (tag `release`) they are enforced with `--fail-on all`, after one re-measurement of the timing sections when a timing budget failed; the report is the last measurement and `meta.timing_runs` lists every run, so a pass on the second attempt is disclosed. The wall-clock pytest guards and the slow tests (real uvicorn server, nested `pytest --collect-only`) carry `slow` and `timing` markers, are excluded from the default `pytest` run, and run inside `nox -s metrics` with one retry of the failures. Timing budgets are not part of `scripts/verify_release.py` or the release fixture: they measure a working tree on a machine, not the stamped identity.

The committed dashboard (`docs/metrics/index.html`, `latest.md`) is a deterministic rendering of the committed `docs/metrics/snapshot.json`; a test fails if they differ. A snapshot names its platform and commit; a new snapshot is produced deliberately with `python -m quality.metrics snapshot`. `drift` warns in the full tier when the snapshot's martin or complexity sections differ from the source tree and fails in the release tier (`--freshness require`); the tests and coverage sections are not checked for freshness.

### Consequences

* Good: one definition, three consumers, negative-control tests prove each family of budgets can fail.
* Good: the honest exceptions (domain D, verify latency, single-coefficient V+E fit) are visible with their reasons.
* Bad: ratchet limits are judgement; they will need revisiting as the code grows.
* Good: the default `pytest` run no longer starts a server or asserts on wall-clock time; that cost (about 40 seconds) moved into `nox -s metrics`.
* Bad: with timing advisory in the full gate, a real latency regression is only caught by the release tier, by a developer reading the advisory line, or by the dashboard.
* Revisit when: a Linux runner exists (then timing budgets move to a fixed reference machine) or when GitHub Actions becomes available again and can host the release tier.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| import-linter, radon `--min`, coverage `--fail-under` | Each expresses one family of limit; none expresses R^2 or percentile budgets over a measured model, and NOT_RUN semantics are missing | Delegate the structural families to the quality lane's gates and keep this table for the measured models |
| custom: `quality/metrics/budgets.py` | Small table plus evaluator (about 150 lines) | Replace the evaluator; ids and bases are the contract |
