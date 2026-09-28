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
| Temporal model checking | [TLA+ / TLC](https://github.com/tlaplus/tlaplus) `tla2tools.jar` v1.7.4 (MIT), pinned by sha256 in `verification/tla/TOOLS.lock` | Apalache, Alloy 6, Quint, a Python explicit-state search | `verification/tla/Excursion.tla` (specification), `generate.py` (model data from the kernel), `tlc.py` (runner and output parser), `render.py` (counterexamples) | The specification is EIJA-specific; the generator exists so the transition table cannot drift from the code. Replace `generate.py` if a maintained Python-to-TLA+ translator appears |
| Model-to-code conformance | TLC trace validation idiom (Cirstea et al. 2024), TLC state-graph output | Hypothesis stateful testing (separate lane and evidence kind) | `verification/tla/abstraction.py`, `conformance.py`, `ExcursionTrace.tla` | A per-system encoder of runtime traces is unavoidable; it drives the real `execute` through the `SandboxFactory` port |
| Lint | [Ruff](https://docs.astral.sh/ruff/) | flake8 + plugins, pylint | — | Rules and per-file debt in `pyproject.toml` |
| Type checking | [mypy](https://mypy.readthedocs.io/) + pydantic plugin | pyright | — | Strict on domain and application; ratchet plan in `docs/quality/gates.md` |
| Architecture contracts | [import-linter](https://import-linter.readthedocs.io/) (grimp) | pytest-archon, custom AST test | `[tool.importlinter]` contracts | Also follows transitive imports, which the AST test cannot |
| Complexity budget | [radon](https://radon.readthedocs.io/), [xenon](https://github.com/rubik/xenon) | Ruff C901, lizard | `quality/gates/complexity_ratchet.py` (about 130 lines) | Neither tool can pin a named list of legacy functions while budgeting the rest; replace with C901 once the debt list is empty |
| Coverage | [coverage.py](https://coverage.readthedocs.io/), pytest-cov | — | — | — |
| Dependency hygiene | [deptry](https://deptry.com/) | pip-check-reqs, creosote | — | — |
| Vulnerability audit | [pip-audit](https://github.com/pypa/pip-audit) | safety, OSV-Scanner | — | — |
| Hook wiring | noslop hooks and Claude guardrails, adapted | pre-commit, husky | `.githooks/run-nox` (about 20 lines of shell) | noslop's Python pack hard-codes other gates; see ADR-0036 |

Lanes still to add rows: providers (agent CLIs), diagrams (Mermaid, PlantUML, Graphviz), formal (Bend, TLA+/TLC, Z3), testing (Hypothesis), mutation, metrics (radon, grimp), HCI (Playwright, axe-core), agents (MCP Python SDK), tracing (OpenFastTrace), knowledge base ([OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)), docs.
