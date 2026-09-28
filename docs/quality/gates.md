# Quality gates

Every gate is a nox session in `quality/sessions/` ([ADR-0017](../adr/0017-local-quality-gates.md)) whose thresholds live in
`pyproject.toml` or a checked-in baseline, so tightening or loosening a threshold is one reviewable diff
([ADR-0035](../adr/0035-static-analysis-and-architecture-fitness-functions.md)). Hosted CI is unavailable, so these local runs
are the evidence; a green run shows that this checkout on this machine passed, not a remote attestation.

```sh
nox -t fast       # pre-commit: lint, types, architecture, complexity, deps, then the whole test suite
nox -t full       # the PR gate; the pre-push hook runs it without the duplicate `tests` session (below)
nox -t release    # maintainer release evidence (network, stamped fixture)
nox -s typecheck  # any single gate
```

**Ratchet rule.** A threshold may tighten and never loosen. Where the current code already violates a rule, the violation is
recorded as named debt (a per-file ignore, a baseline entry, a per-module override) with the reason next to it. Debt entries
are removed in the commit that fixes them. Nothing is silenced with a blanket ignore.

**Cost.** The fast tier includes the whole pytest suite (about 125 tests). Measured on the shared PC: about 30 s on an idle machine
and 90 s or more with several lanes running. `nox -t full` runs that suite twice, once in `coverage` (with `--cov`) and once in the
foundation lane's `tests` session, about 3.4 minutes under load. The pre-push hook therefore runs `nox -t full -k "not tests"`,
because `coverage` already ran the identical suite. A bare `nox -t full` still runs both; removing `tests` from the `full` tag is
the foundation lane's change (`quality/sessions/tests.py`) and is listed as an owner follow-up.

**Missing prerequisites report `NOT_RUN`, never PASS.** The only gate here that needs anything outside the venv is `audit`
(network). nox exits 0 for a skipped session, and an exit code cannot tell NOT_RUN from PASS, so `audit` **fails** offline with a
`NOT_RUN` message unless `EIJA_ALLOW_NOT_RUN=1` is set (then it skips, prints NOT_RUN, and the reader must not count it as PASS).
Any script that aggregates nox results must treat a skipped session as NOT_RUN. The reachability probe is a TCP connect to
`pypi.org:443`, so it does not prove the advisory API answers. Tests that need a `lint`-extra tool (radon, ruff, mypy,
import-linter) skip with a `NOT_RUN:` reason when it is missing; the baseline suite still runs with only `.[dev]`, but the gates
need `.[dev,lint]`.

## Gates

| Gate (nox session) | Tier | Tool (pinned in the `lint` extra) | Configuration | Threshold today | Ratchet |
|---|---|---|---|---|---|
| `lint` | fast, full | Ruff 0.16.9 `check`; `ruff format --check` on lane-owned files only | `[tool.ruff]` | Rules `E W F I B S SIM UP C4 PIE RUF PLE PLW PLC PERF T20`; zero findings after documented per-file debt | Remove a `per-file-ignores` entry when its file is next touched for a real change |
| `typecheck` | fast, full | mypy 2.3.1 with the pydantic plugin | `[tool.mypy]` | `eija_studio.domain` and `.application`: all `--strict` flags; whole package: `check_untyped_defs`, `warn_unused_ignores`, `strict_equality` | See "mypy ratchet plan" below |
| `architecture` | fast, full | import-linter 2.15 (grimp) | `[tool.importlinter]` | 3 contracts kept, 0 broken (see below) | New contracts may be added; a contract is never weakened without a superseding ADR |
| `complexity` | fast, full | xenon 0.9.3 (radon 6.0.1) plus `quality/gates/complexity_ratchet.py` | `quality/gates/complexity_baseline.json` | xenon: average rank A, no module worse than D. Per function (including methods of nested classes): cyclomatic complexity at most 10, except 7 recorded legacy functions pinned at today's value. Roots: `src/eija_studio`, `quality`, and `verification` once it exists. `tests/` and `scripts/` are outside the ratchet | `python -m quality.gates.complexity_ratchet --update` lowers or removes debt and never adds or raises any (growth stays a failure, covered by a test); the gate fails if debt improved but the baseline was not tightened |
| `dependencies` | fast, full | deptry 0.25.1 | `[tool.deptry]` | 0 issues: every import declared, every runtime dependency used, no transitive imports | Adding a rule ignore needs a written reason in `pyproject.toml` |
| `coverage` | full | pytest-cov 7.1.0 (coverage.py 7.16.2), branch coverage | `[tool.coverage.*]` | `fail_under = 78` (measured 78.72 % on 2026-09-28, Windows 11, Python 3.12) | Raise `fail_under` to the new floor whenever coverage rises; reports go to `reports/coverage/` (gitignored) |
| `audit` | release | pip-audit 2.10.1 against the PyPI advisory database | `requirements-tested.txt` | 0 known vulnerabilities in the measured runtime pins. **Currently FAILS**: see "Known audit findings" | Fixes are pin bumps in the tested set (an owner decision). Offline it fails with NOT_RUN (see above) |
| `tests` (foundation lane) | fast, full | pytest | `[tool.pytest.ini_options]` | all pass | not this lane |

### Architecture contracts

1. **Layers**: `interfaces > bootstrap > adapters > application > domain`. A lower layer never imports a higher one.
2. **Vendor-free kernel**: `eija_studio.domain` and `eija_studio.application` import none of `fastapi`, `starlette`, `httpx`,
   `uvicorn`, `sqlite3`, `subprocess`, `socket`, `urllib`, `http`, `requests`, `aiohttp`, `ftplib`, directly or transitively
   through `eija_studio` modules. Third-party internals are not part of the import graph, so a vendor library that itself
   opens sockets is not seen. Filesystem and `os` process calls are not covered (Ruff `S` rules catch some).
3. **Only bootstrap wires adapters**: `domain`, `application` and `interfaces` never import `eija_studio.adapters` directly
   (`bootstrap` may). Indirect reach through `bootstrap` is allowed by design.

The layers contract is `exhaustive`: a new `eija_studio` subpackage added by another lane fails the gate until it is given a
layer (or an `exhaustive_ignores` entry with a reason), so it cannot sit outside the layer order unnoticed.

The older AST test `tests/test_http_and_architecture.py::test_architecture_dependency_direction` stays: it catches direct
imports in a few lines of standard library, whereas import-linter also follows transitive imports.
`tests/test_quality_gates.py` proves the contracts can fail: it copies the kernel, seeds forbidden imports, and requires all
three contracts to break; a second case seeds `urllib`/`socket` into `application` and an unlayered subpackage. The same file
holds negative controls for Ruff (`shell=True` in the domain) and mypy strict (untyped def, implicit Optional). There is no
committed negative control for the coverage floor or deptry, and the ADR does not claim one.

### mypy ratchet plan

`domain` and `application` are strict and green. "Strict" here means annotated, not modelled: about 50 annotations are
`dict[str, Any]` because the packet, receipt and case payloads are still untyped bags, so `warn_return_any` and
`disallow_any_generics` pass without adding real shape safety. Introducing TypedDicts or pydantic models for those payloads is a
ratchet item, and `disallow_any_explicit` stays off until then. `adapters`, `interfaces` and `bootstrap` pass the default profile above but
are not yet strict (about 60 missing annotations under `--strict`). Order of work, one module per change, each removing
a debt line: (1) annotate the provider table in `bootstrap.py` and drop its `arg-type` override, (2) `adapters.*`,
(3) `interfaces.*`. `ignore_errors` is never used. The analysis platform is pinned to `linux` because the process-group calls
in `adapters/providers.py` are POSIX-only branches that a Windows host would otherwise flag.

### Ruff debt inventory

The kernel is written in a compact one-line style and other lanes edit it in parallel, so `ruff format` is deliberately not run
over `src/`, `tests/` or `scripts/`. `[tool.ruff.lint.per-file-ignores]` in `pyproject.toml` is the authoritative list; every entry there is still needed
(a run with the table removed was checked). By group:

* Style debt in all legacy trees: `E401 E501 E701 E702 I001`, plus `UP035` across `src/`.
* Unused imports (`F401`) in `cli.py` and four test files; `PLC0415` (import inside a function) in `cli.py`, two tests and
  `scripts/`; `SIM117`, `SIM300` in two tests.
* Subprocess findings: `S603`/`S607`/`PLW1510` (no `check=`) in `scripts/`, `tests/test_runtime.py`, `adapters/providers.py` (fixed
  argv, no shell) and the gate sessions.
* Real kernel debt: `B905`/`RUF007` (`domain/impact.py`), `UP017`/`RUF001`/`RUF005` (`application/service.py`),
  `UP017`/`PLW2901` (`application/verifier.py`), `PLW0108` (`bootstrap.py`), `T201` (print) in `cli.py`.
* `scripts/` also ignores `B023`: the two hits in `scripts/http_smoke.py` are false positives (the closures run in the same
  loop iteration). `S608` in `adapters/sqlite_store.py` is a false positive (table name from a closed literal tuple).

`assert` in `src/` is not ignored by path: the only one (`application/verifier.py`) is a documented mypy narrowing and carries an
inline `# noqa: S101`.

### Complexity debt (legacy, pinned)

`domain/evidence.py::assess_receipt` 45, `interfaces/cli.py::main` 33, `application/verifier.py::verify_runtime` 23,
`domain/policy.py::check_policy` 21, `adapters/providers.py::OpenRouterProvider.propose` 17,
`application/compiler.py::compile_case` 16, `application/runtime.py::execute` 16. Other lanes may not increase these numbers;
splitting any of them is a kernel change that needs a regression test.

### Known audit findings

`nox -s audit` on 2026-09-28 (network available) reports advisories against the pins in `requirements-tested.txt`: `starlette==0.50.0`
(five PYSEC advisories, fixed in 1.0.1 to 1.3.1), `anyio==4.13.0` (two CVEs, fixed in 4.14.2), `click==8.1.8` (fixed in 8.3.3),
`pytest==9.0.2` (fixed in 9.0.3) and `setuptools==82.0.1` (fixed in 83.0.0). This lane does not change dependency pins: they define the
measured tested set and the owner-stamped release, so a bump is an owner decision with a re-measurement. The gate stays honest and red
in the release tier until then. Whether a given advisory is reachable from a local single-owner tool is a separate assessment that
this gate does not make.

## Hooks and agent guardrails (noslop)

`npx -y @45ck/noslop init` generated the starting files, which were adapted (ADR-0036): `noslop check` hard-codes black,
`ruff select=ALL` and `typos`, and its installer overwrites `pyproject.toml` and `AGENTS.md`, so those outputs were discarded.

| File | Job |
|---|---|
| `.githooks/pre-commit` | `nox -t fast` |
| `.githooks/pre-push` | `nox -t full` |
| `.githooks/commit-msg` | Conventional Commits subject; rejects `[skip ci]`-style bypass text; allows git-generated merge and revert subjects |
| `.githooks/run-nox` | Finds `.venv/Scripts/python.exe` or `.venv/bin/python` (Git Bash on Windows and POSIX), sets TMP/TEMP inside the checkout, probes for nox, pytest-cov, ruff, mypy, import-linter, xenon, radon and deptry and prints the `.[dev,lint]` instruction if any is missing |
| `.claude/settings.json`, `.claude/hooks/pre-tool-use.sh` | Tripwire against the known bypass forms (the long no-verify flag, `git commit -n` and clusters like `-nm`, `core.hooksPath` overrides, `HUSKY=`/`SKIP=` variables, `[skip ci]`) and denies Edit/Write of hooks and agent settings and force-pushes (`git push -f`, the long force flag; `--force-with-lease` is allowed); the hook works without `jq` |
| `.github/workflows/quality.yml`, `guardrails.yml` | `workflow_dispatch` only (hosted CI unavailable) |

**Two different activation models.** The git hooks in `.githooks/` do nothing until `core.hooksPath` is set (below). The Claude
Code files in `.claude/` are different: Claude Code loads `.claude/settings.json` automatically, so the deny rules and the
PreToolUse hook are **live in every clone and worktree as soon as this branch merges**, with no enable step. They are a
best-effort tripwire, not a security control: text matching cannot stop an agent that can run arbitrary shell (aliases, scripts,
redirect writes, `git -c` variants not yet listed). The real control is review of any diff that touches `.githooks/` or
`.claude/`, which the manual `guardrails` workflow and a human reviewer apply.

### Enabling the hooks (one line, per clone)

```sh
git config core.hooksPath .githooks && npx -y @45ck/noslop doctor
```

`core.hooksPath` is repository configuration shared by every worktree, so the quality branch does not run it. Once enabled,
every commit and push in every worktree that contains `.githooks/` needs the lint extra:
`.venv/Scripts/python -m pip install -e ".[dev,lint]"`. Without it the hook fails with that instruction instead of silently
passing. The pre-commit hook checks the working tree, not the index. Before enabling, `noslop doctor` passes 5 of 6 checks and
fails exactly one (`core.hooksPath` not set): report that as PARTIAL (expected), not PASS. The hooks were exercised on Windows
Git Bash only; POSIX behaviour is by construction, not measured.

## What these gates do not establish

Passing them shows that style, typing, layering, complexity and dependency hygiene are within budget. It says nothing about
whether the kernel's semantics are right; that is the job of the tests and of the formal and testing lanes. Coverage counts
executed lines, not verified behaviour, and `interfaces/cli.py` is 0 % covered because no test drives the CLI yet.
