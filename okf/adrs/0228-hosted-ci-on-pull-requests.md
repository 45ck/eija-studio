---
type: Architecture Decision Record
title: 'ADR-0228: Hosted CI on pull requests, nightly full tier and auto-merge'
description: ADR-0017 kept the GitHub workflows on manual `workflow_dispatch` because hosted CI was not available.
resource: repo://docs/adr/0228-hosted-ci-on-pull-requests.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0228-hosted-ci-on-pull-requests.md
  title: 0228-hosted-ci-on-pull-requests.md
  hash_method: lf-sha256-v1
  sha256: cdd93d4a6edf5482b746b4c87f6875085058b3c8a8ffeca2eed3833d510f50d1
notes_baseline: 4affef182831a26409fe37c999f5f88c9f330d5df323569c64ff8e16a6e9e1dd
---

# ADR-0228: Hosted CI on pull requests, nightly full tier and auto-merge

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-11 |
| Lane | quality / delivery |
| Source | `repo://docs/adr/0228-hosted-ci-on-pull-requests.md` |

## Decision outcome (verbatim)

> `.github/workflows/quality.yml`:
>
> * `fast` job: every pull request to `main` and every push to `main` runs `nox -t fast` on Python 3.12 (about 2 minutes of tests on 4 cores, under 15 minutes cap).
> * `full` job: nightly at 15:17 UTC, and on manual dispatch, runs `nox -t full` (about 13 minutes, 30-minute cap; amended 14 November 2026: 43 minutes measured after the 11 to 14 November gates, 60-minute cap, see [the second tests and gates inspection](repo://docs/quality/inspections/2026-11-14-tests-gates-docs-deeper.md#r1-the-full-tier)). The nightly run skips itself when `main` has not changed for 26 hours. A failed nightly run opens one issue, "Nightly full tier failed on main", or comments on it if it is already open.
> * Docs-only changes are **not** excluded with `paths-ignore`. The fast tier contains docs gates (`docs_links`, `adr_index`, `community_files`), and a required check that never starts leaves a pull request blocked.
> * Concurrency groups cancel a superseded run on the same ref; pip caching is keyed on `pyproject.toml`.
>
> `.github/workflows/guardrails.yml` now runs automatically on pull requests that touch `.githooks/**`, `.claude/settings.json` or `.claude/hooks/**`, and again when labels change, requiring the `noslop-approved` label. Manual dispatch with a PR number remains.
>
> `test.yml` (release verification and HTTP smoke on Python 3.11 and 3.13) stays manual: it is release evidence, not a per-change gate.
>
> Merging: the `fast` check is to be a required status on `main`, with GitHub's native auto-merge allowed, so a pull request merges itself when green. Both are repository settings that only the owner can change; until they are set, the check is advisory and merges stay manual.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)
* Amendment, 13 November 2026: a skipped gate is not a green gate
* Amendment, 17 November 2026: the billing lock is gone; a CI budget test

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://.claude/settings.json`
* `repo://pyproject.toml`
* `repo://quality/sessions/browser.py`
* `repo://tests/test_ci_budget.py`
* `repo://tests/test_syntax_validator.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0017: Local quality gates with nox sessions and noslop enforcement](/adrs/0017-local-quality-gates.md) - Hosted CI was not available for this repository when this was written (September 2026).

## Referenced by

* [ADR-0017: Local quality gates with nox sessions and noslop enforcement](/adrs/0017-local-quality-gates.md) - Hosted CI was not available for this repository when this was written (September 2026).
* [ADR-0036: noslop guardrails adapted to run nox tiers; hook enablement is an explicit step](/adrs/0036-noslop-hooks-adapted-to-nox.md) - noslop installs git hooks and agent guardrails, but `noslop init` writes a generic Python pack: `black`, `ruff select=ALL`, `typos`, `mypy .`, plain `pytest`.
<!-- okf:generated:end links -->
