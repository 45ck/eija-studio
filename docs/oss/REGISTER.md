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
| Property-based testing | [Hypothesis](https://github.com/HypothesisWorks/hypothesis) (MPL-2.0) | hand-rolled seeded loops, pytest-quickcheck | `tests/property/property_strategies.py`, `tests/property/conftest.py` (profiles, example-count report) | Workflow and receipt generators and the report writer encode EIJA contracts; the engine, shrinking and stateful machinery are Hypothesis ([ADR-0031](../adr/0031-property-based-testing-with-hypothesis.md)) |
| Schema-driven generation and validation | [hypothesis-jsonschema](https://github.com/python-jsonschema/hypothesis-jsonschema), [jsonschema](https://github.com/python-jsonschema/jsonschema) | Schemathesis (HTTP-oriented) | `tests/property/test_contract_schemas.py` (schema versus Pydantic drift, near-miss mutation) | Compares the committed `contracts/*.schema.json` with the Pydantic models in both directions; no tool does that comparison |
| Model-based reference for the runtime | Hypothesis `RuleBasedStateMachine` | Schemathesis stateful, TLA+ (formal lane) | `tests/property/property_reference.py`, `test_runtime_differential.py`, mutant controls ([ADR-0032](../adr/0032-stateful-differential-testing-and-negative-controls.md)) | The reference encodes EIJA's own rules from the specification text; replace with a model generated from the TLA+ specification when that lane lands |
| Property gates | nox | — | `quality/sessions/property.py` (`property`, `property_deep`) | Thin session wrappers, no logic |

Lanes still to add rows: providers (agent CLIs), diagrams (Mermaid, PlantUML, Graphviz), formal (Bend, TLA+/TLC, Z3), testing (Hypothesis), mutation, lint and typing (Ruff, mypy, import-linter), metrics (radon, grimp), HCI (Playwright, axe-core), agents (MCP Python SDK), tracing (OpenFastTrace), knowledge base ([OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)), docs.
