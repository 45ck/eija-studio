# OSS-first register

[ADR-0016](../adr/0016-oss-first-adapters-not-engines.md): adopt open source first; write only EIJA-specific glue. Every lane adds its rows here. A row with custom code must fill in the last two columns.

| Capability | OSS adopted | Alternatives checked | EIJA custom glue | Why custom was needed / replacement path |
|---|---|---|---|---|
| Web API | FastAPI, Uvicorn, Starlette | — | `interfaces/http.py` | Thin interface layer only |
| Contracts and validation | Pydantic v2, JSON Schema | attrs, msgspec | `domain/models.py` | Domain contracts are the kernel |
| Persistence | SQLite (stdlib) | SQLAlchemy | `adapters/sqlite_store.py` | Unit-of-work semantics are kernel invariants; replaceable behind the `UnitOfWork` port |
| HTTP client | httpx | requests | `adapters/providers.py` | — |
| Test runner | pytest | unittest | — | — |
| Gate orchestration | nox | tox, just, make | `noxfile.py` plugin loader (15 lines) | — |
| Hook enforcement | [noslop](https://github.com/45ck/noslop) | pre-commit, husky | — | — |
| ADR format | MADR | Nygard ADRs, log4brains | — | — |
| Cyclomatic complexity, maintainability index, raw size | [radon](https://github.com/rubik/radon) 6.0.1 (pinned once, in the `lint` extra) | wily, xenon, lizard, pylint | `quality/metrics/complexity.py` (flattening and aggregation for the dashboard) | radon supplies the numbers; custom code only groups them per layer. Per-function complexity is budgeted by the quality lane's ratchet (row below), this lane budgets only the maintainability index |
| Import graph and Martin package metrics | [grimp](https://github.com/seddonym/grimp) 3.17 | import-linter (contracts only), pydeps, pyreverse | `quality/metrics/structure.py` (Ca, Ce, I, A, D, SDP, cycles) | No tool computes Ca/Ce/I/A/D per layer with an ast-based abstractness count; replace with any graph library behind `collect()` |
| Regression fits | Python standard library `statistics` | numpy, scipy | `quality/metrics/common.py` (`ols`, 20-line normal-equations `ols_multi`) | Two-parameter OLS on tens of points; adopt numpy if a lane needs more |
| Latency measurement | Starlette TestClient, uvicorn, httpx (already dependencies) | pytest-benchmark, locust, wrk | `quality/metrics/perf.py` (flows, percentiles, thresholds) | Per-endpoint p50/p95/p99 against Doherty on two transports; load testing is out of scope |
| Metrics dashboard and budgets | none suitable | SonarQube, CodeClimate, Grafana, matplotlib and Vega-Lite (static SVG export) | `quality/metrics/{dashboard,svg,budgets,collect,aggregate}.py`; `quality/sessions/metrics.py` | Offline, deterministic (byte-identical) static HTML/SVG from one JSON schema with no new dependency. matplotlib is adoptable but adds a large numeric dependency (declined for numpy in ADR-0037) and font-dependent text layout; Vega-Lite needs a Node toolchain. Replace the renderer with any templater reading `reports/metrics.json` |
| Demo capture | Playwright (system Chrome, built-in video) | [demo-machine](https://github.com/45ck/demo-machine), OBS, screen recorders | `demos/lib/recorder.py`: synthetic cursor overlay, eased motion, typing cadence, captions (about 270 lines) | Owner chose a hand-authored version over demo-machine (ADR-0047); Chromium does not render the OS pointer into video, so a cursor overlay is unavoidable; scenario steps can be lowered into a demo-machine spec later |
| Lint | [Ruff](https://docs.astral.sh/ruff/) | flake8 + plugins, pylint | — | Rules and per-file debt in `pyproject.toml` |
| Type checking | [mypy](https://mypy.readthedocs.io/) + pydantic plugin | pyright | — | Strict on domain and application; ratchet plan in `docs/quality/gates.md` |
| Architecture contracts | [import-linter](https://import-linter.readthedocs.io/) (grimp) | pytest-archon, custom AST test | `[tool.importlinter]` contracts | Also follows transitive imports, which the AST test cannot |
| Complexity budget | [radon](https://radon.readthedocs.io/), [xenon](https://github.com/rubik/xenon) | Ruff C901, lizard | `quality/gates/complexity_ratchet.py` (about 130 lines) | Neither tool can pin a named list of legacy functions while budgeting the rest; replace with C901 once the debt list is empty |
| Coverage | [coverage.py](https://coverage.readthedocs.io/), pytest-cov | — | `quality/metrics/inventory.py` (binds `reports/coverage` to a hash of src/ and tests/ and aggregates per layer for the dashboard) | The quality lane owns the gate (`nox -s coverage`); the metrics lane runs the same coverage.py pin from the `lint` extra and refuses a report from another tree |
| Dependency hygiene | [deptry](https://deptry.com/) | pip-check-reqs, creosote | — | — |
| Vulnerability audit | [pip-audit](https://github.com/pypa/pip-audit) | safety, OSV-Scanner | — | — |
| Hook wiring | noslop hooks and Claude guardrails, adapted | pre-commit, husky | `.githooks/run-nox` (about 20 lines of shell) | noslop's Python pack hard-codes other gates; see ADR-0036 |

Lanes still to add rows: providers (agent CLIs), diagrams (Mermaid, PlantUML, Graphviz), formal (Bend, TLA+/TLC, Z3), testing (Hypothesis), mutation, HCI (Playwright, axe-core), agents (MCP Python SDK), tracing (OpenFastTrace), knowledge base ([OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)), docs.
