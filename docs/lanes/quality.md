# Quality

Status as of 2026-09-29. Hosted CI is unavailable, so every gate runs locally through nox ([ADR-0017](../adr/0017-local-quality-gates.md)) and its result is local evidence.

## Tiers

| Tier | Command | Purpose |
|---|---|---|
| fast | `nox -t fast` | Seconds; before every commit |
| full | `nox -t full` | The PR gate |
| release | `nox -t release` | Maintainer evidence; may need Docker, Java or Chromium; a missing prerequisite reports `NOT_RUN` |

## On `main`

* `tests`: the kernel regression suite (unit, integration, crash recovery, concurrency).
* `release_fixture`: owner-only; current bytes must match the owner-stamped fixture. Agents never stamp it.
* The [verification report](../verification/VERIFICATION.md) and acceptance matrix.

## Not on `main` yet

| Piece | ADRs | Status |
|---|---|---|
| Ruff, mypy, import-linter layering contracts, complexity and coverage ratchets, noslop hooks | 0035-0036 | open PR #3 |
| Hypothesis property-based and model-based tests | 0031-0032 | planned |
| Mutation analysis | 0033-0034 | planned |

Documentation gates from the oss lane: `docs_links` (fast), `readme_diagram` (fast), `community_files` (fast) and `docs` (release, `mkdocs build --strict`). See [ADR-0043](../adr/0043-readme-truthfulness-and-docs-site.md).
