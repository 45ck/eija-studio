---
type: Architecture Decision Record
title: 'ADR-0035: Static analysis, architecture fitness functions and ratcheted budgets'
description: The kernel's central claims (a vendor-free domain, authority checked before replay, computed evidence) hold only while the code keeps its shape.
resource: repo://docs/adr/0035-static-analysis-and-architecture-fitness-functions.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0035-static-analysis-and-architecture-fitness-functions.md
  title: 0035-static-analysis-and-architecture-fitness-functions.md
  hash_method: lf-sha256-v1
  sha256: 1b5a87d28a087fee37591b10aa00006983cdd59e4a5bc45b6995108bcb157b43
notes_baseline: ddc01bbf661652da7ddbeeeac5a7828f8bf59df70f069087c318235ff1a0153c
---

# ADR-0035: Static analysis, architecture fitness functions and ratcheted budgets

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-28 |
| Lane | quality |
| Source | `repo://docs/adr/0035-static-analysis-and-architecture-fitness-functions.md` |

## Decision outcome (verbatim)

> Chosen option: separate, tiered nox sessions in `quality/sessions/quality.py`, each tool configured in `pyproject.toml`, all pinned in the `lint` extra.
>
> * **Ratchet, not cliff.** The current code passes every gate except the release-tier audit. Existing violations are named debt: per-file ruff ignores, per-module mypy overrides, a complexity baseline. Thresholds tighten, never loosen; debt is deleted in the commit that fixes it.
> * **Architecture as fitness functions** with import-linter: layers `interfaces > bootstrap > adapters > application > domain`, a vendor-free domain and application, and adapters wired only by bootstrap. `tests/test_quality_gates.py` seeds violations into a copy of the kernel and requires the contracts to break.
> * **mypy strict where invariants live** (`domain`, `application`), default profile elsewhere with a written module-by-module plan. No `ignore_errors`.
> * **Complexity**: xenon enforces average and module rank; a small custom ratchet (`quality/gates/complexity_ratchet.py`) adds the per-function debt list xenon cannot express. `--update` can only lower debt.
> * **Coverage** is branch coverage with `fail_under` at the floor of the measured value.
> * **Dependency hygiene**: deptry in the fast tier; pip-audit in the release tier because it needs network, reporting `NOT_RUN` when offline.
> * **Kernel edits** were limited to type annotations with no behaviour change (`dict[str, Any]`, callable types, one narrowing `assert`).

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://docs/quality/gates.md`
* `repo://pyproject.toml`
* `repo://quality/gates/complexity_ratchet.py`
* `repo://quality/sessions/quality.py`
* `repo://tests/test_quality_gates.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0017: Local quality gates with nox sessions and noslop enforcement](/adrs/0017-local-quality-gates.md) - Hosted CI is not currently available for this repository.

## Referenced by

* [ADR-0038: Metric budgets are tests with a stated basis, and timing budgets are advisory in the full gate](/adrs/0038-metric-budgets-as-tests.md) - Metrics that nobody enforces decay into a dashboard.
* [ADR-0097: Impact, ranking and evidence-status mathematics: fixed points, integer relevance, greedy selection, count vectors, and no confidence percentage](/adrs/0097-weave-impact-ranking-math.md) - The weave graph must answer six questions about a change: what does it affect, what should an agent or a person read, which tests give the cheapest useful re-c…
* [Quality gates, architecture fitness functions and static analysis](/lanes/0035-quality-gates-architecture-fitness.md) - Capability lane with ADR numbers 0035–0036 reserved.
<!-- okf:generated:end links -->
