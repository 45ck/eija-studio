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
* Ruff, mypy, import-linter layering contracts, complexity and coverage ratchets and noslop hooks (ADR-0035 and ADR-0036, merged PR #3). Every gate, its tool and its threshold is in [Quality gates](../quality/gates.md).
* The [verification report](../verification/VERIFICATION.md) and acceptance matrix.

## Not on `main` yet

| Piece | ADRs | Status |
|---|---|---|
| Hypothesis property-based and model-based tests | 0031-0032 | branch pushed (`lane/property`), no PR |
| Mutation analysis | 0033-0034 | planned |

Documentation gates from the oss lane, all added by open PR #14 and so on `main` only when it merges: `docs_links`, `readme_diagram` and `community_files` (fast and full tiers), `docs` (`mkdocs build --strict`) and `pr_status` (release tier). `docs_links` is the link validator: the MkDocs build downgrades unresolved-link findings to `info`. The limits of each gate are in [ADR-0043](../adr/0043-readme-truthfulness-and-docs-site.md).
