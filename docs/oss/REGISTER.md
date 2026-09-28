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
| SMT policy proof (lane smt-bmc) | [Z3](https://github.com/Z3Prover/z3) via `z3-solver==5.1.0.0` (MIT) | CVC5, Yices, CrossHair | `verification/smt/` (symbolic Transition grammar, clause-level encoding of `check_policy`, invariant statements, differential faithfulness harness, evidence report) | No tool derives an SMT model of a pydantic-based Python function; the encoding is hand-written and compared with the real function. Replace by CrossHair or an SMT-LIB export to a second solver ([ADR-0029](../adr/0029-z3-policy-soundness-proof.md)) |
| Bounded model checking of the runtime (lane smt-bmc) | Python stdlib (`sqlite3`, `unittest.mock`); pytest for tests | TLC (TLA+), Hypothesis stateful, CrossHair, Stateright | `verification/bmc/` (BFS over the real `runtime.execute`, database snapshot/restore, reference model and invariants, seeded-fault self-test, evidence report) | No mature checker executes an arbitrary Python callable against SQLite with a completeness statement at a depth and shortest traces. Complement with Hypothesis (ADR-0031) and TLC trace conformance (ADR-0027); see [ADR-0030](../adr/0030-bounded-model-checking-of-the-real-runtime.md) |

Lanes still to add rows: providers (agent CLIs), diagrams (Mermaid, PlantUML, Graphviz), formal (Bend, TLA+/TLC, Z3), testing (Hypothesis), mutation, lint and typing (Ruff, mypy, import-linter), metrics (radon, grimp), HCI (Playwright, axe-core), agents (MCP Python SDK), tracing (OpenFastTrace), knowledge base ([OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)), docs.
