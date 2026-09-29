# Quality gates

Every gate is a nox session in `quality/sessions/` ([ADR-0017](../adr/0017-local-quality-gates.md)) whose thresholds live in
`pyproject.toml` or a checked-in baseline, so tightening or loosening a threshold is one reviewable diff
([ADR-0035](../adr/0035-static-analysis-and-architecture-fitness-functions.md)). Hosted CI is unavailable, so these local runs
are the evidence; a green run shows that this checkout on this machine passed, not a remote attestation.

```sh
nox -t fast       # pre-commit: about 2 minutes on the reference PC (most of it the test suite)
nox -t full       # pre-push and the PR gate
nox -t release    # maintainer release evidence (network, stamped fixture)
nox -s typecheck  # any single gate
```

**Ratchet rule.** A threshold may tighten and never loosen. Where the current code already violates a rule, the violation is
recorded as named debt (a per-file ignore, a baseline entry, a per-module override) with the reason next to it. Debt entries
are removed in the commit that fixes them. Nothing is silenced with a blanket ignore.

**Missing prerequisites report `NOT_RUN`, never PASS.** The only gate here that needs anything outside the venv is `audit`
(network).

## Gates

| Gate (nox session) | Tier | Tool (pinned in the `lint` extra) | Configuration | Threshold today | Ratchet |
|---|---|---|---|---|---|
| `lint` | fast, full | Ruff 0.16.9 `check`; `ruff format --check` on lane-owned files only | `[tool.ruff]` | Rules `E W F I B S SIM UP C4 PIE RUF PLE PLW PLC PERF T20`; zero findings after documented per-file debt | Remove a `per-file-ignores` entry when its file is next touched for a real change |
| `typecheck` | fast, full | mypy 2.3.1 with the pydantic plugin | `[tool.mypy]` | `eija_studio.domain` and `.application`: all `--strict` flags; whole package: `check_untyped_defs`, `warn_unused_ignores`, `strict_equality` | See "mypy ratchet plan" below |
| `architecture` | fast, full | import-linter 2.15 (grimp) | `[tool.importlinter]` | 3 contracts kept, 0 broken (see below) | New contracts may be added; a contract is never weakened without a superseding ADR |
| `complexity` | fast, full | xenon 0.9.3 (radon 6.0.1) plus `quality/gates/complexity_ratchet.py` | `quality/gates/complexity_baseline.json` | xenon: average rank A, no module worse than D. Per function: cyclomatic complexity at most 10, except 7 recorded legacy functions pinned at today's value | `python -m quality.gates.complexity_ratchet --update` lowers or removes debt and never adds any; the gate fails if debt improved but the baseline was not tightened |
| `dependencies` | fast, full | deptry 0.25.1 | `[tool.deptry]` | 0 issues: every import declared, every runtime dependency used, no transitive imports | Adding a rule ignore needs a written reason in `pyproject.toml` |
| `coverage` | full | pytest-cov 7.1.0 (coverage.py 7.16.2), branch coverage | `[tool.coverage.*]` | `fail_under = 78` (measured 78.72 % on 2026-09-28, Windows 11, Python 3.12) | Raise `fail_under` to the new floor whenever coverage rises; reports go to `reports/coverage/` (gitignored) |
| `audit` | release | pip-audit 2.10.1 against the PyPI advisory database | `requirements-tested.txt` | 0 known vulnerabilities in the measured runtime pins. **Currently FAILS**: see "Known audit findings" | Fixes are pin bumps in the tested set (an owner decision). NOT_RUN without network |
| `tests` (foundation lane) | fast, full | pytest | `[tool.pytest.ini_options]` | all pass | not this lane |

### Architecture contracts

1. **Layers**: `interfaces > bootstrap > adapters > application > domain`. A lower layer never imports a higher one.
2. **Vendor-free kernel**: `eija_studio.domain` and `eija_studio.application` import none of `fastapi`, `starlette`, `httpx`,
   `uvicorn`, `sqlite3`, `subprocess`, directly or transitively.
3. **Only bootstrap wires adapters**: `domain`, `application` and `interfaces` never import `eija_studio.adapters` directly
   (`bootstrap` may). Indirect reach through `bootstrap` is allowed by design.

The older AST test `tests/test_http_and_architecture.py::test_architecture_dependency_direction` stays: it catches direct
imports in a few lines of standard library, whereas import-linter also follows transitive imports.
`tests/test_quality_gates.py` proves the contracts can fail: it copies the kernel, seeds forbidden imports, and requires all
three contracts to break.

### mypy ratchet plan

`domain` and `application` are strict and green. `adapters`, `interfaces` and `bootstrap` pass the default profile above but
are not yet strict (about 60 missing annotations under `--strict`). Order of work, one module per change, each removing
a debt line: (1) annotate the provider table in `bootstrap.py` and drop its `arg-type` override, (2) `adapters.*`,
(3) `interfaces.*`. `ignore_errors` is never used. The analysis platform is pinned to `linux` because the process-group calls
in `adapters/providers.py` are POSIX-only branches that a Windows host would otherwise flag.

### Ruff debt inventory

The kernel is written in a compact one-line style and other lanes edit it in parallel, so `ruff format` is deliberately not run
over `src/`, `tests/` or `scripts/`. The formatting-class findings (`E401 E501 E701 E702 I001`) are ignored per path there. Real
findings are ignored per file and named in `[tool.ruff.lint.per-file-ignores]` (for example `B905`/`RUF007` in
`domain/impact.py`, and `S608` in `adapters/sqlite_store.py`, a false positive because the table name comes from a closed literal
tuple). `assert` in `src/` is not ignored: the only one (`application/verifier.py`) is a documented mypy narrowing.

### Complexity debt (legacy, pinned)

`domain/evidence.py::assess_receipt` 44, `interfaces/cli.py::main` 31, `application/verifier.py::verify_runtime` 23,
`domain/policy.py::check_policy` 21, `application/runtime.py::execute` 16, `application/compiler.py::compile_case` 15
(`quality/gates/complexity_baseline.json` is the source of truth). Other lanes may not increase these numbers; splitting any of
them is a kernel change that needs a regression test. The 25 functions (5 mutation, 20 okf) the okf and mutation lanes added over the budget were
refactored on the integration branch (2026-09-29), so they add no debt.

### Lane trees merged on 2026-09-29

The graph (weave), okf, mutation and prgif lanes were merged without ever passing these gates as a whole. Fixed at the root:
per-function complexity (refactors above), `deptry` (parso declared, numpy and scipy declared for the networkx PageRank oracle),
import-linter and the SDP metric (the formal adapters now read the evidence-kind registry only), the metrics lane restored from
its reviewed tip, and the ruff findings that had a safe or behaviour-preserving fix. What remains is named debt in
`[tool.ruff.lint.per-file-ignores]` with the reason per rule in the comment above it: tree-level idioms (`assert` in checks,
`print` in command-line reports, seeded `random.Random` fixtures, fixed-argv subprocess, lazy optional imports) and per-file
loop-shape style in reference code that other tests compare against. `deptry` excludes `docs/weave/research` (recorded probes,
not part of any gate) and lists the optional comparison engines (duckdb, rustworkx, ladybug, pyshacl, rdflib, clingo) as
lazy imports that report `NOT_RUN` when absent.

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
| `.githooks/run-nox` | Finds `.venv/Scripts/python.exe` or `.venv/bin/python` (Git Bash on Windows and POSIX), sets TMP/TEMP inside the checkout, fails loudly if nox is missing |
| `.claude/settings.json`, `.claude/hooks/pre-tool-use.sh` | **Active for every agent automatically** (not opt-in). Deny force-pushes and `--no-verify` on `git commit`/`git push`, and edits to hooks and agent settings; ordinary `--force` operations (worktree removal, pip) and text that merely mentions a flag are allowed; the hook works without `jq` |
| `.github/workflows/quality.yml`, `guardrails.yml` | `workflow_dispatch` only (hosted CI unavailable) |

### Toolchain with uv (Windows reference PC)

The sessions use `python=False`, so nox never creates its own virtualenv and the `-db uv` backend flag has nothing to
switch: the environment is the one the sessions run in. Build that environment with uv once per worktree, keeping uv's cache
off the slow system drive, and run nox through it:

```sh
export UV_CACHE_DIR=C:/Dev/.uv-cache TMP="$PWD/.tmp" TEMP="$PWD/.tmp"   # Git Bash; .tmp is gitignored
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe -e ".[dev,lint,testing,mutation,metrics,hci,agents,providers,docs,visual,demos,graph,okf,graph-formal,smt]"
source .venv/Scripts/activate            # or .venv/bin/activate on POSIX
nox -l                                   # lists every session
nox -t fast
```

`dev` and `lint` are enough for the fast tier. The other extras are the capability lanes' tools (`smt` Z3, `graph-formal`
clingo, `okf` PyYAML, `hci`/`visual`/`demos` Playwright driving the installed Chrome, and so on); a session whose optional
tool is absent reports `NOT_RUN`, never PASS. `.githooks/run-nox` finds `.venv` on its own, so the hooks need no activation.

### Enabling the hooks (one line, per clone)

```sh
git config core.hooksPath .githooks && npx -y @45ck/noslop doctor
```

`core.hooksPath` is repository configuration shared by every worktree, so the quality branch does not run it. Once enabled,
every commit and push in every worktree that contains `.githooks/` needs the lint extra:
`.venv/Scripts/python -m pip install -e ".[dev,lint]"`. Without it the hook fails with that instruction instead of silently
passing. The pre-commit hook checks the working tree, not the index. Before enabling, `noslop doctor` reports exactly one failed
check (`core.hooksPath` not set).

### Parallel test runs (pytest-xdist)

The pytest-driven CPU-bound sessions (`tests`, `property`, `coverage`) run on 4 workers with
`--dist loadfile` (all tests of a file on one worker, so module fixtures and the stateful Hypothesis test with its post-run
assertion behave as they do serially). The switch is `quality/tools/parallel.py`:

* `EIJA_SERIAL=1` forces the serial run (use it to debug a failure); a missing `pytest-xdist` also gives the serial run, never an error.
* `EIJA_XDIST_WORKERS=N` changes the worker count (default 4; the PC has 12 logical cores but shares 16 GB RAM with other sessions).
* Deliberately serial: `okf_tools` (measured: 92 s serial, 88 to 116 s with `-n 4`, its subprocess-heavy tests sit in one file), the heavy formal sessions (Z3, TLC, Bend, Chrome: RAM-bound), `metrics` (its slow and timing tests assert on
  wall-clock, which parallel load would disturb; 5 tests, 16 s), `providers_contract` and `demos_registry` (measured: no gain
  with `-n 4`, one file dominates and `loadfile` keeps it on one worker), and `hci_docs` (not pytest).
* xdist-safe by inspection and by measurement: tests use `tmp_path` or unique `mkdtemp` scratch dirs, HTTP tests use Starlette
  `TestClient` (no sockets, no fixed ports), and the full suite ran green at `-n 4` and `-n 8` with the same counts as serial.
* Coverage: pytest-cov combines the per-worker data itself; the floor is unchanged (78) and the measured total is identical.
* Hypothesis stays deterministic: `tests/conftest.py` loads a derandomized profile (`derandomize=True`, `database=None`) for every
  test that does not choose its own, `tests/property` keeps `ci` (derandomized) or `deep` (random, release only), and the
  property report is merged from the workers by the controller (`workeroutput`), not overwritten by whichever worker finished last.
* Negative control: `tests/tools/test_parallel_gate.py` plants a failing test in a nested project and requires the `-n 2` run to
  fail with exactly the counts of the serial run (3 passed, 1 failed).

**MEASUREMENT** (2026-09-29, reference PC, Windows 11, 12 logical cores; one run each, wall-clock, another agent session was
running on the same machine, so read these as a ratio, not as a benchmark; "serial" is the pre-change command or `EIJA_SERIAL=1`):

| Gate | Serial | `-n 4 --dist loadfile` | Result equality |
|------|--------|------------------------|-----------------|
| `nox -s tests` (pytest 1509 passed, 153 skipped, 1 xfailed) | 3 min 48 s (pytest 224 s) | 1 min 14 s (pytest 73 s); `-n 8`: pytest 57 s | same counts |
| `nox -s property` (91 passed, 6 xfailed) | 1 min 51 s | 36 s | `property.json` identical in profile, totals (9257 generated, 7809 valid examples), per-test example counts (77 tests) and stateful outcome histogram |
| `nox -s coverage` | 4 min 13 s | 1 min 34 s | same pass counts, total 93.88 % in both, floor 78 unchanged |
| `nox -t fast` (21 sessions) | 4 min 48 s | 2 min 28 s | all sessions green in both; 1518 passed, 153 skipped, 1 xfailed |

Where the remaining `nox -t fast` time goes (parallel run): `tests` about 1 min, `providers_contract` 27 s, `demos_registry` 16 s,
`graph_metamodel` 7 s, everything else under 5 s. A further speed-up needs the provider process-tree tests split across files.

## What these gates do not establish

Passing them shows that style, typing, layering, complexity and dependency hygiene are within budget. It says nothing about
whether the kernel's semantics are right; that is the job of the tests and of the formal and testing lanes. Coverage counts
executed lines, not verified behaviour, and `interfaces/cli.py` is 0 % covered because no test drives the CLI yet.

## Notes for lane authors

* **New modules need tests at or above the coverage floor.** Headroom is under one point (floor 78, measured 78.7); adding an under-tested module trips the gate. Add tests; do not lower the floor.
* **Moving a function** (for example `adapters/providers.py` into a package) leaves a stale key in `complexity_baseline.json`, and `--update` will not add the moved entry. Rename the key by hand in the same change, and say so in the PR.
* **Optional extras are not dev groups** for deptry: only `dev` and `lint` are. A lane that imports its extra's package from `src/` or a tooling tree is fine; declare the distribution-to-module name in `[tool.deptry.package_module_name_map]` when they differ.
* **`typecheck_win32`** (full tier) re-runs mypy as `win32` so Windows-only branches are checked; the default `typecheck` runs as `linux`.
