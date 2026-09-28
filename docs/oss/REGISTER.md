# OSS-first register

[ADR-0016](../adr/0016-oss-first-adapters-not-engines.md): adopt open source first; write only EIJA-specific glue. Every lane adds its rows here. A row with custom code must fill in the last two columns.

| Capability | OSS adopted | Alternatives checked | EIJA custom glue | Why custom was needed / replacement path |
|---|---|---|---|---|
| Web API | FastAPI, Uvicorn, Starlette | — | `interfaces/http.py` | Thin interface layer only |
| Contracts and validation | Pydantic v2, JSON Schema | attrs, msgspec | `domain/models.py` | Domain contracts are the kernel |
| Persistence | SQLite (stdlib) | SQLAlchemy | `adapters/sqlite_store.py` | Unit-of-work semantics are kernel invariants; replaceable behind the `UnitOfWork` port |
| HTTP client | httpx | requests | `adapters/providers/openrouter.py`, `anthropic_api.py` | — |
| Test runner | pytest | unittest | — | — |
| Gate orchestration | nox | tox, just, make | `noxfile.py` plugin loader (15 lines) | — |
| Hook enforcement | [noslop](https://github.com/45ck/noslop) | pre-commit, husky | — | — |
| ADR format | MADR | Nygard ADRs, log4brains | — | — |
| Lint | [Ruff](https://docs.astral.sh/ruff/) | flake8 + plugins, pylint | — | Rules and per-file debt in `pyproject.toml` |
| Type checking | [mypy](https://mypy.readthedocs.io/) + pydantic plugin | pyright | — | Strict on domain and application; ratchet plan in `docs/quality/gates.md` |
| Architecture contracts | [import-linter](https://import-linter.readthedocs.io/) (grimp) | pytest-archon, custom AST test | `[tool.importlinter]` contracts | Also follows transitive imports, which the AST test cannot |
| Complexity budget | [radon](https://radon.readthedocs.io/), [xenon](https://github.com/rubik/xenon) | Ruff C901, lizard | `quality/gates/complexity_ratchet.py` (about 130 lines) | Neither tool can pin a named list of legacy functions while budgeting the rest; replace with C901 once the debt list is empty |
| Coverage | [coverage.py](https://coverage.readthedocs.io/), pytest-cov | — | — | — |
| Dependency hygiene | [deptry](https://deptry.com/) | pip-check-reqs, creosote | — | — |
| Vulnerability audit | [pip-audit](https://github.com/pypa/pip-audit) | safety, OSV-Scanner | — | — |
| Hook wiring | noslop hooks and Claude guardrails, adapted | pre-commit, husky | `.githooks/run-nox` (about 20 lines of shell) | noslop's Python pack hard-codes other gates; see ADR-0036 |
| Agent CLIs as proposal providers | Vendor CLIs (Codex, Claude Code, OpenCode, Gemini CLI) with their own logins, called headless | Vendor SDKs, Claude Agent SDK, Agent Client Protocol (not uniform across the four) | `adapters/providers/cli_base.py` + one thin module per CLI | Isolation policy (empty cwd, env allow-list, stdin prompt, tools off) and per-CLI flags are EIJA-specific; replace when a vendor ships a stable sandboxed structured-output mode |
| Process-tree kill and bounded capture | psutil (extra `providers`) with `taskkill /T` and `killpg` as fallbacks | Windows Job Objects via ctypes, `subprocess` alone | `adapters/providers/process.py` | Byte caps while streaming, deadline and shim unwrapping have no OSS equivalent; kill lives in one function |
| npm `.cmd` shim handling on Windows | Node itself (`node script.js`) | Running the `.cmd` through cmd.exe (BatBadBut argument injection) | `process._unwrap_node_shim` | Parses only the exact npm shim shape and refuses anything else |
| Provider contract testing | pytest parametrization | Hypothesis (a later testing-lane concern) | `tests/test_provider_contract.py` | One table row per CLI; mocked runner, not live |
| Live provider smoke | The vendor CLIs themselves | — | `scripts/live_provider_smoke.py` | Consent gate and evidence recording only |
| Demo capture | Playwright (system Chrome, built-in video) | [demo-machine](https://github.com/45ck/demo-machine), OBS, screen recorders | `demos/lib/recorder.py`: synthetic cursor overlay, eased motion, typing cadence, captions (~200 lines) | Owner chose a hand-authored version over demo-machine (ADR-0047); Chromium does not render the OS pointer into video, so a cursor overlay is unavoidable; scenario steps can be lowered into a demo-machine spec later |

Lanes still to add rows: providers (agent CLIs), diagrams (Mermaid, PlantUML, Graphviz), formal (Bend, TLA+/TLC, Z3), testing (Hypothesis), mutation, metrics (radon, grimp), HCI (Playwright, axe-core), agents (MCP Python SDK), tracing (OpenFastTrace), knowledge base ([OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)), docs.
