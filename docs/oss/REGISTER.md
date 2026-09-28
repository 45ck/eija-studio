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
| Machine-checked laws | [Bend 2](https://github.com/bendlang/bend) (Apache-2.0) `bend PROOF.bend --verdict`; BendTT kernel (Lean 4) | Lean 4, Coq, Agda, Dafny (heavier, no laws/proof convention), Z3 and TLA+ (own lanes, different claims) | `verification/bend/bend_generate.py` (Workflow to `main.bend`), `LAWS.bend`, `PROOF.bend` | Bend has no JSON/Python import, so the model must be generated from the executable Workflow to avoid drift (ADR-0025, ADR-0026); replace the generator if Bend gains structured import |
| Pinned proof container | Docker, `ubuntu:24.04` (digest-pinned), Lean 4.34.0 (compiles the BendTT kernel only) | WSL, the official `install.sh` (always installs latest), native install | `verification/bend/Dockerfile`, `verification/bend/bend_runner.py` (verdict classification, `NOT_RUN`, report) | Bend does not run on native Windows and verdicts must be reproducible (ADR-0025); on Linux/macOS/WSL replace `Checker` with a native `bend` call |
| Bend negative controls, conformance, slicing | pytest, Docker | mutation tools (mutate Python, not a Bend model) | `bend_controls.py`, `bend_conformance.py`, `bend_slicing.py` | A proof must be shown to fail on unsafe models and to agree with the runtime on a sample (ADR-0026); no OSS tool attributes a Bend failure to one law |
| Demo capture | Playwright (system Chrome, built-in video) | [demo-machine](https://github.com/45ck/demo-machine), OBS, screen recorders | `demos/lib/recorder.py`: synthetic cursor overlay, eased motion, typing cadence, captions (about 270 lines) | Owner chose a hand-authored version over demo-machine (ADR-0047); Chromium does not render the OS pointer into video, so a cursor overlay is unavoidable; scenario steps can be lowered into a demo-machine spec later |
| Lint | [Ruff](https://docs.astral.sh/ruff/) | flake8 + plugins, pylint | — | Rules and per-file debt in `pyproject.toml` |
| Type checking | [mypy](https://mypy.readthedocs.io/) + pydantic plugin | pyright | — | Strict on domain and application; ratchet plan in `docs/quality/gates.md` |
| Architecture contracts | [import-linter](https://import-linter.readthedocs.io/) (grimp) | pytest-archon, custom AST test | `[tool.importlinter]` contracts | Also follows transitive imports, which the AST test cannot |
| Complexity budget | [radon](https://radon.readthedocs.io/), [xenon](https://github.com/rubik/xenon) | Ruff C901, lizard | `quality/gates/complexity_ratchet.py` (about 130 lines) | Neither tool can pin a named list of legacy functions while budgeting the rest; replace with C901 once the debt list is empty |
| Coverage | [coverage.py](https://coverage.readthedocs.io/), pytest-cov | — | — | — |
| Dependency hygiene | [deptry](https://deptry.com/) | pip-check-reqs, creosote | — | — |
| Vulnerability audit | [pip-audit](https://github.com/pypa/pip-audit) | safety, OSV-Scanner | — | — |
| Hook wiring | noslop hooks and Claude guardrails, adapted | pre-commit, husky | `.githooks/run-nox` (about 20 lines of shell) | noslop's Python pack hard-codes other gates; see ADR-0036 |

Lanes still to add rows: providers (agent CLIs), diagrams (Mermaid, PlantUML, Graphviz), formal (Bend, TLA+/TLC, Z3), testing (Hypothesis), mutation, metrics (radon, grimp), HCI (Playwright, axe-core), agents (MCP Python SDK), tracing (OpenFastTrace), knowledge base ([OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)), docs.
