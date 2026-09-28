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
| Machine-checked laws | [Bend 2](https://github.com/bendlang/bend) (Apache-2.0) `bend PROOF.bend --verdict`; BendTT kernel (Lean 4) | Lean 4, Coq, Agda, Dafny (heavier, no laws/proof convention), Z3 and TLA+ (own lanes, different claims) | `verification/bend/bend_generate.py` (Workflow to `main.bend`), `LAWS.bend`, `PROOF.bend` | Bend has no JSON/Python import, so the model must be generated from the executable Workflow to avoid drift (ADR-0025, ADR-0026); replace the generator if Bend gains structured import |
| Pinned proof container | Docker, `ubuntu:24.04` (digest-pinned), Lean 4.34.0 (compiles the BendTT kernel only) | WSL, the official `install.sh` (always installs latest), native install | `verification/bend/Dockerfile`, `verification/bend/bend_runner.py` (verdict classification, `NOT_RUN`, report) | Bend does not run on native Windows and verdicts must be reproducible (ADR-0025); on Linux/macOS/WSL replace `Checker` with a native `bend` call |
| Bend negative controls, conformance, slicing | pytest, Docker | mutation tools (mutate Python, not a Bend model) | `bend_controls.py`, `bend_conformance.py`, `bend_slicing.py` | A proof must be shown to fail on unsafe models and to agree with the runtime on a sample (ADR-0026); no OSS tool attributes a Bend failure to one law |

Lanes still to add rows: providers (agent CLIs), diagrams (Mermaid, PlantUML, Graphviz), formal (TLA+/TLC, Z3; Bend rows are above), testing (Hypothesis), mutation, lint and typing (Ruff, mypy, import-linter), metrics (radon, grimp), HCI (Playwright, axe-core), agents (MCP Python SDK), tracing (OpenFastTrace), knowledge base ([OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)), docs.
