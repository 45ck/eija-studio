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
| Browser automation (HCI journey) | [Playwright for Python](https://playwright.dev/python/) (Apache-2.0), driving the installed Chrome (`channel="chrome"`, no download) | Selenium/WebDriver, Cypress, pytest-playwright | `quality/hci/journey.py` (journey as data + pointer/keyboard driver), `quality/hci/probe.js` (observe-only init script), `quality/hci/serve_harness.py` | The owner journey, exact-landing-point pointer model and focus/timing capture are EIJA-specific; the harness launcher exists because `eija serve` has no test-identity hook. Replacement path: pytest-playwright fixtures |
| WCAG 2.2 AA audit | [axe-core](https://github.com/dequelabs/axe-core) (MPL-2.0) via [axe-playwright-python](https://github.com/pamelafox/axe-playwright-python) (MIT) | pa11y, Lighthouse | `quality/hci/analysis.py` cross-view aggregation; `quality/hci/wcag.py` 2.5.8 spacing-exception geometry | axe reports per-node results only; the aggregation and the pure 2.5.8 spacing check are ours. Replacement path: axe's own `target-size` rule where it covers the exception |
| HCI predictive models | None packaged: Fitts (MacKenzie & Buxton 1992), Hick-Hyman, KLM (Card, Moran & Newell 1980) are published formulas | CogTool and web KLM calculators (GUI, no headless API) | `quality/hci/laws.py`, `analysis.py`, `recommend.py`, `report.py`, `budgets.py` | Each formula is a few lines with cited, swappable constants; the value is in the live-DOM inputs. Replacement path: a maintained Python library if one appears |
| HCI qualitative review | [hci-review-skill](https://github.com/45ck/hci-review-skill) (MIT, owner's pack; consulted, not a dependency) | Nielsen heuristic checklists | `docs/hci/README.md` protocol notes only | Human study is NOT_RUN in this lane |

Lanes still to add rows: providers (agent CLIs), diagrams (Mermaid, PlantUML, Graphviz), formal (Bend, TLA+/TLC, Z3), testing (Hypothesis), mutation, lint and typing (Ruff, mypy, import-linter), metrics (radon, grimp), agents (MCP Python SDK), tracing (OpenFastTrace), knowledge base ([OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)), docs.
