---
type: Architecture Decision Record
title: 'ADR-0038: Metric budgets are tests with a stated basis, and timing budgets are advisory in the full gate'
description: Metrics that nobody enforces decay into a dashboard.
resource: repo://docs/adr/0038-metric-budgets-as-tests.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0038-metric-budgets-as-tests.md
  title: 0038-metric-budgets-as-tests.md
  hash_method: lf-sha256-v1
  sha256: 4d126b79ee0cd2504cfd7e7e3e44ef767ef200b233882921d26e1a651b99da41
notes_baseline: 2766a0f48ecdfac84805c89a51a2ce4aaf933f2a20c89fca4bb11e9224e4d847
---

# ADR-0038: Metric budgets are tests with a stated basis, and timing budgets are advisory in the full gate

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-28 |
| Lane | metrics |
| Source | `repo://docs/adr/0038-metric-budgets-as-tests.md` |

## Decision outcome (verbatim)

> Chosen option: one table in code, with three kinds of basis.
>
> * Principled: holds at any size. No dependency cycles, the domain imports no other layer and has instability at most 0.1, no Stable Dependencies Principle violation, R^2 at least 0.9 for a linear fit, log-log exponent in [0.8, 1.2], every layer has a directly importing test, no lane report says FAIL, UNKNOWN or UNREADABLE (a present report must say PASS or NOT_RUN).
> * External: a published threshold. Doherty and Thadani (1982): p95 of interactive endpoints under 400 ms. The `verify` endpoint is a long-running computation (one to a few seconds depending on machine load, because it runs a 125-cell isolated matrix), so it is budgeted separately at 10 s (Nielsen's limit for keeping attention) and its excess over 400 ms is reported, not hidden: it needs a progress indication in the UI.
> * Ratchet: current value plus headroom, to catch regressions (minimum maintainability index 20, coverage at least 75 percent line+branch on a coverage report measured on the current tree, non-domain layers within 0.5 of the main sequence, the requested single-term closure fit at R^2 0.85, the verify() time fit at R^2 0.8 because ten points on a shared machine ranged from 0.896 to 0.99). Per-function cyclomatic complexity is deliberately NOT budgeted here: the quality lane owns it (`quality/gates/complexity_ratchet.py`, default 10 with a pinned debt list, stricter than anything this lane had), and one budget per property avoids two gates disagreeing. A ratchet is a guard rail and is labelled as one. It is tightened by a deliberate commit, never loosened to make a build pass without an ADR or a justification in the PR.
>
> Deliberate non-budget: the domain layer's distance from the main sequence. The formula gives D = 1.0 (stable, and concrete because it holds frozen contracts and pure rules with no Protocol). Adding an abstraction only to move the number would be the speculative abstraction ADR-0016 and AGENTS.md forbid. The number is reported with its zone; the budgets check what matters for that layer (I near 0, Ce = 0).
>
> Evaluation rules: an extractor that cannot find its section yields NOT_RUN. A coverage report that is not bound to the current source and test tree (SHA-256 recorded next to it) is NOT_RUN, not a pass on old evidence.
>
> Timing budgets are marked `kind: timing` and are wall-clock measurements. In `nox -s metrics` (tag `full`, the shared gate) they are printed as advisory and cannot fail the session; the structural budgets and the drift check do. In `nox -s metrics_report` (tag `release`) they are enforced with `--fail-on all`, after one re-measurement of the timing sections when a timing budget failed; the report is the last measurement and `meta.timing_runs` lists every run, so a pass on the second attempt is disclosed. The wall-clock pytest guards and the slow tests (real uvicorn server, nested `pytest --collect-only`) carry `slow` and `timing` markers, are excluded from the default `pytest` run, and run inside `nox -s metrics` with one retry of the failures. Timing budgets are not part of `scripts/verify_release.py` or the release fixture: they measure a working tree on a machine, not the stamped identity.
>
> The committed dashboard (`docs/metrics/index.html`, `latest.md`) is a deterministic rendering of the committed `docs/metrics/snapshot.json`; a test fails if they differ. A snapshot names its platform and commit; a new snapshot is produced deliberately with `python -m quality.metrics snapshot`. `drift` warns in the full tier when the snapshot's martin or complexity sections differ from the source tree and fails in the release tier (`--freshness require`); the tests and coverage sections are not checked for freshness.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://docs/metrics/snapshot.json`
* `repo://quality/gates/complexity_ratchet.py`
* `repo://quality/metrics/budgets.py`
* `repo://scripts/verify_release.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0035: Static analysis, architecture fitness functions and ratcheted budgets](/adrs/0035-static-analysis-and-architecture-fitness-functions.md) - The kernel's central claims (a vendor-free domain, authority checked before replay, computed evidence) hold only while the code keeps its shape.

## Referenced by

* [ADR-0037: Measure design, performance and scaling with radon, grimp and coverage.py, and fit models rather than assert them](/adrs/0037-metrics-and-quantitative-models.md) - EIJA Studio claims a clean layered design (domain and application never import adapters), an O(V+E) impact closure and an interactive local UI.
* [Metrics and quantitative models](/lanes/0037-metrics-and-quantitative-models.md) - Capability lane with ADR numbers 0037–0038 reserved.
<!-- okf:generated:end links -->
