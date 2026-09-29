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
| Mutation testing | cosmic-ray 8.7.0 (`mutation` extra) | mutmut 3.8.0 (no native Windows: fork-based, needs WSL/Docker), mutatest 3.1.0 (unmaintained since 2020), own engine (not needed) | `quality/mutation/` (~750 lines with reports): scratch-copy workspace, 2-worker sharding, 3 operators (identifier strings, return values, membership), result classification, ratchet, survivor report | cosmic-ray has no string, return or membership operator and no ratchet or survivor report; the engine, filters and session store are adopted unchanged. Operators can be upstreamed as a provider; `engine.py` is the only cosmic-ray-specific file ([ADR-0033](../adr/0033-mutation-tool-selection.md), [ADR-0034](../adr/0034-mutation-measurement-and-ratchet.md)) |

Lanes still to add rows: providers (agent CLIs), diagrams (Mermaid, PlantUML, Graphviz), formal (Bend, TLA+/TLC, Z3), testing (Hypothesis), mutation, lint and typing (Ruff, mypy, import-linter), metrics (radon, grimp), HCI (Playwright, axe-core), agents (MCP Python SDK), tracing (OpenFastTrace), knowledge base ([OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)), docs.
