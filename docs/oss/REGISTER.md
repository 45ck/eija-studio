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
| Cyclomatic complexity, maintainability index, raw size | [radon](https://github.com/rubik/radon) 6.0.1 | wily, xenon, lizard, pylint | `quality/metrics/complexity.py` (flattening and aggregation) | radon supplies the numbers; custom code only groups them per layer |
| Import graph and Martin package metrics | [grimp](https://github.com/seddonym/grimp) 3.17 | import-linter (contracts only), pydeps, pyreverse | `quality/metrics/structure.py` (Ca, Ce, I, A, D, SDP, cycles) | No tool computes Ca/Ce/I/A/D per layer with an ast-based abstractness count; replace with any graph library behind `collect()` |
| Coverage | [coverage.py](https://github.com/nedbat/coveragepy) 7.16.2 | pytest-cov | `quality/metrics/inventory.py` (run + per-layer aggregation) | Called directly so the run and JSON report are two explicit commands |
| Regression fits | Python standard library `statistics` | numpy, scipy | `quality/metrics/common.py` (`ols`, 20-line normal-equations `ols_multi`) | Two-parameter OLS on tens of points; adopt numpy if a lane needs more |
| Latency measurement | Starlette TestClient, uvicorn, httpx (already dependencies) | pytest-benchmark, locust, wrk | `quality/metrics/perf.py` (flows, percentiles, thresholds) | Per-endpoint p50/p95/p99 against Doherty on two transports; load testing is out of scope |
| Metrics dashboard and budgets | none suitable | SonarQube, CodeClimate, Grafana | `quality/metrics/{dashboard,svg,budgets,collect,aggregate}.py`; `quality/sessions/metrics.py` | Offline, deterministic, static HTML/SVG from one JSON schema; replace the renderer with any templater reading `reports/metrics.json` |

Lanes still to add rows: providers (agent CLIs), diagrams (Mermaid, PlantUML, Graphviz), formal (Bend, TLA+/TLC, Z3), testing (Hypothesis), mutation, lint and typing (Ruff, mypy, import-linter), metrics (radon, grimp), HCI (Playwright, axe-core), agents (MCP Python SDK), tracing (OpenFastTrace), knowledge base ([OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)), docs.
