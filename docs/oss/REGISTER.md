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
| Diagram rendering in Studio, GitHub and standalone HTML | [Mermaid](https://github.com/mermaid-js/mermaid) 12.0.0 (vendored unmodified from npm, MIT, sha256 recorded in `resources/web/vendor/mermaid.VENDOR.json`) | PlantUML, Graphviz, D2, server-side SVG | `interfaces/render_html.py`, `resources/web/visual-frame.*` | Thin glue: a sandboxed frame and a self-contained page around the vendored renderer ([ADR-0024](../adr/0024-sandboxed-frame-for-mermaid-rendering.md)) |
| Diagram text generation (Mermaid, PlantUML, DOT) | Pydantic `model_fields` introspection; `domain.impact.model_impact` | Structurizr, pyreverse, hand-written diagrams | `application/diagrams.py`, `diagram_emitters.py`, `diagram_catalog.py` | No tool emits UML from EIJA's `Workflow` guards, effects and impact closure; generators are the only custom part ([ADR-0023](../adr/0023-generated-uml-and-visual-diff.md)). Replacement path: any renderer that reads the three text formats |
| Diagram syntax validation | PlantUML `-syntax` (jar, optional), pydot 4.0.1, Graphviz `dot` (optional), Mermaid `parse`/`render` in Chrome | Mermaid CLI (pulls a bundled Chromium) | `scripts/validate_diagram_syntax.py` | Uses the installed Chrome instead of downloading a browser; missing tools report `NOT_RUN` |
| Browser drive and screenshots | Playwright 1.63.0 with installed Google Chrome (`channel`/`executable_path`) | Selenium, Puppeteer | `scripts/capture_visual_screenshots.py` | Playwright is the register's HCI tool; no browser download |
| Lint | [Ruff](https://docs.astral.sh/ruff/) | flake8 + plugins, pylint | — | Rules and per-file debt in `pyproject.toml` |
| Type checking | [mypy](https://mypy.readthedocs.io/) + pydantic plugin | pyright | — | Strict on domain and application; ratchet plan in `docs/quality/gates.md` |
| Architecture contracts | [import-linter](https://import-linter.readthedocs.io/) (grimp) | pytest-archon, custom AST test | `[tool.importlinter]` contracts | Also follows transitive imports, which the AST test cannot |
| Complexity budget | [radon](https://radon.readthedocs.io/), [xenon](https://github.com/rubik/xenon) | Ruff C901, lizard | `quality/gates/complexity_ratchet.py` (about 130 lines) | Neither tool can pin a named list of legacy functions while budgeting the rest; replace with C901 once the debt list is empty |
| Coverage | [coverage.py](https://coverage.readthedocs.io/), pytest-cov | — | — | — |
| Dependency hygiene | [deptry](https://deptry.com/) | pip-check-reqs, creosote | — | — |
| Vulnerability audit | [pip-audit](https://github.com/pypa/pip-audit) | safety, OSV-Scanner | — | — |
| Hook wiring | noslop hooks and Claude guardrails, adapted | pre-commit, husky | `.githooks/run-nox` (about 20 lines of shell) | noslop's Python pack hard-codes other gates; see ADR-0036 |
| Diagram syntax validation | PlantUML `-syntax` (jar, optional; GPL-licensed, downloaded on demand by the person running the gate, never vendored or shipped, and not pinned by hash: the report prints its version), pydot 4.0.1, Graphviz `dot` (optional), Mermaid `parse`/`render` in Chrome | Mermaid CLI (pulls a bundled Chromium) | `scripts/validate_diagram_syntax.py` | Uses the installed Chrome (Playwright `channel="chrome"`) instead of downloading a browser; a missing tool reports `NOT_RUN` and fails the release session unless `EIJA_ALLOW_NOT_RUN=1` |
| Browser drive and screenshots | Playwright 1.63.0 with installed Google Chrome (`channel="chrome"`) | Selenium, Puppeteer | `scripts/capture_visual_screenshots.py` | Playwright is the register's HCI tool; no browser download |

Lanes still to add rows: providers (agent CLIs), diagrams (Mermaid, PlantUML, Graphviz), formal (Bend, TLA+/TLC, Z3), testing (Hypothesis), mutation, metrics (radon, grimp), HCI (Playwright, axe-core), agents (MCP Python SDK), tracing (OpenFastTrace), knowledge base ([OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)), docs.
