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
| Knowledge base format | [OKF v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md) (Apache-2.0) | OKF v0.1 profiles (Calvin Ops, ProofMap Lite), pdoc, mkdocstrings | `quality/okf/` (extractors, hash methods, gate) | No OSS tool links OKF concepts to Python symbols with normalised hashes; the format itself stays standard ([ADR-0045](../adr/0045-okf-knowledge-base-linked-to-code.md)) |
| Frontmatter and YAML | PyYAML (`safe_load`, `safe_dump`) | ruamel.yaml, python-frontmatter (evaluated, dropped: it only wrapped `yaml.load`) | `quality/okf/pages.py` | The `---` split, deterministic write order and marker-preserving merge are custom; YAML parsing is not |
| Markdown link extraction | markdown-it-py | regex | `quality/okf/checks.py` | Only the gate rules are custom |
| Python symbol resolution and hashing | stdlib `ast` | griffe, libcst | `quality/okf/codelink.py` | Canonical AST JSON; the committed hashes were reproduced on CPython 3.11.15, 3.12.10 and 3.13.12 on 2026-09-29 (`quality/okf/crosscheck.py`): evidence for these sources, not a general guarantee ([ADR-0046](../adr/0046-code-link-hash-methods-and-stale-semantics.md)); griffe could later feed `ast-api-v1` |

Lanes still to add rows: providers (agent CLIs), diagrams (Mermaid, PlantUML, Graphviz), formal (Bend, TLA+/TLC, Z3), testing (Hypothesis), mutation, lint and typing (Ruff, mypy, import-linter), metrics (radon, grimp), HCI (Playwright, axe-core), agents (MCP Python SDK), tracing (OpenFastTrace), docs.
