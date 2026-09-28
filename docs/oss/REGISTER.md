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
| Documentation site | [MkDocs](https://www.mkdocs.org/), [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/), PyMdown Extensions | Sphinx, Docusaurus, VitePress | `mkdocs.yml`, nox session `docs` (`quality/sessions/oss.py`) | Configuration only. No deployment: hosted CI is unavailable (ADR-0043) |
| README diagram | [Mermaid](https://github.com/mermaid-js/mermaid) (rendered by GitHub and Material) | PlantUML, Graphviz, hand-drawn SVG | `scripts/gen_readme_diagram.py` | Projects `domain.policy` models into Mermaid text between README markers and fails on drift. Superseded by the visual lane's generators (ADR-0023) |
| Link checking | — | lychee, markdown-link-check | `scripts/check_doc_links.py` (stdlib) | Offline relative-link and anchor check for README, community files and docs; both alternatives need a Rust binary or Node. Replace with lychee to add external-link checking |
| Community files | [Contributor Covenant 2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) (verbatim), [Citation File Format](https://citation-file-format.github.io/), GitHub issue forms, shields.io static badges | cffconvert (rejected: it resolved to `jsonschema` 3.2.0 when tried, a conflict risk for other lanes' extras) | `scripts/check_community_files.py` (stdlib) | Presence, CITATION/pyproject version agreement, roadmap covers all lane ADR blocks. Not a full CFF schema validation |

Lanes still to add rows: providers (agent CLIs), diagrams (Mermaid, PlantUML, Graphviz), formal (Bend, TLA+/TLC, Z3), testing (Hypothesis), mutation, lint and typing (Ruff, mypy, import-linter), metrics (radon, grimp), HCI (Playwright, axe-core), agents (MCP Python SDK), tracing (OpenFastTrace), knowledge base ([OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)), docs.
