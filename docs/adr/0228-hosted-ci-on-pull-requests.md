# ADR-0228: Hosted CI on pull requests, nightly full tier and auto-merge

* Status: accepted
* Date: 2026-11-11
* Lane: quality / delivery

## Context and problem statement

ADR-0017 kept the GitHub workflows on manual `workflow_dispatch` because hosted CI was not available. The repository is now public, and GitHub's standard hosted runners are free for public repositories. With every check run by hand inside an agent session, finished pull requests waited for someone to run the gates: #210 and #212 sat green-but-unchecked from 8 to 11 November 2026 because the sessions that opened them were paused. Merge evidence lived in session transcripts rather than on the pull request.

This record supersedes only the "manual dispatch until hosted CI is enabled" part of ADR-0017. Its nox sessions, tiers and noslop hooks stand.

## Decision drivers

* Lead time: a pull request gets a result in minutes without a human or agent having to run anything.
* Cost: $0 a month. Only standard Linux runners; larger and macOS runners are billed even for public repositories.
* One definition of a gate: the hosted job runs the same `nox -t fast` / `nox -t full` a contributor runs locally.
* No weaker gates: nothing is skipped, quarantined or relaxed to get a hosted run green.

## Considered options

* GitHub Actions on standard runners, triggered on pull requests, pushes to main and a nightly schedule (chosen).
* Keep manual dispatch and rely on local runs (rejected: the stall described above).
* A third-party CI service (rejected: a second configuration to keep in step, no cost advantage for a public repository).
* Self-hosted runners (rejected: a machine to maintain, and a security risk for pull requests from forks).

## Decision outcome

`.github/workflows/quality.yml`:

* `fast` job: every pull request to `main` and every push to `main` runs `nox -t fast` on Python 3.12 (about 2 minutes of tests on 4 cores, under 15 minutes cap).
* `full` job: nightly at 15:17 UTC, and on manual dispatch, runs `nox -t full` (about 13 minutes, 30-minute cap). The nightly run skips itself when `main` has not changed for 26 hours. A failed nightly run opens one issue, "Nightly full tier failed on main", or comments on it if it is already open.
* Docs-only changes are **not** excluded with `paths-ignore`. The fast tier contains docs gates (`docs_links`, `adr_index`, `community_files`), and a required check that never starts leaves a pull request blocked.
* Concurrency groups cancel a superseded run on the same ref; pip caching is keyed on `pyproject.toml`.

`.github/workflows/guardrails.yml` now runs automatically on pull requests that touch `.githooks/**`, `.claude/settings.json` or `.claude/hooks/**`, and again when labels change, requiring the `noslop-approved` label. Manual dispatch with a PR number remains.

`test.yml` (release verification and HTTP smoke on Python 3.11 and 3.13) stays manual: it is release evidence, not a per-change gate.

Merging: the `fast` check is to be a required status on `main`, with GitHub's native auto-merge allowed, so a pull request merges itself when green. Both are repository settings that only the owner can change; until they are set, the check is advisory and merges stay manual.

### Consequences

* Good: every pull request carries its own gate result; paused agent sessions no longer stall merges.
* Good: a nightly full tier catches the slow gates (`formal_tla`, `coverage`, mutation-adjacent sessions) without slowing pull requests.
* Bad: browser tests (`EIJA_BROWSER_TESTS=1`) and `audit` network checks are not in the hosted fast tier; they stay local or in the full tier as before.
* Bad: hosted results are Linux-only; the Windows reference PC remains the place where Windows-specific behaviour is checked.
* Revisit when: the fast job exceeds 10 minutes, the repository becomes private (standard runners then bill per minute), or GitHub changes public-repository runner pricing.

## OSS check (required for any custom module)

No custom module. GitHub Actions and the existing nox sessions only.
