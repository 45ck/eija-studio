# Roadmap

Status as of **2026-09-29**, checked against `origin/main` at `ddc43b9` and the open pull requests of [45ck/eija-studio](https://github.com/45ck/eija-studio/pulls). A row says **on main** only if you can reproduce it from a checkout of `main`. Statuses go stale; the date is the honest part. Live status is the pull request list.

Status vocabulary: **on main**, **open PR #n** (implemented on a branch, not merged), **branch pushed** (work exists on a branch, no PR), **planned** (nothing built yet).

## Where EIJA is today

Version 0.2.0 is a bounded local proof of concept for one synthetic domain, the excursion approval workflow: a browser Studio, a CLI semantic compiler, a deterministic kernel with authority-before-replay, SQLite unit of work, computed subject-bound evidence, fixed-point impact analysis, and offline, OpenRouter and Codex proposal providers. Foundation work (Apache-2.0, OSS register, ADRs, nox gate plugins, Windows durability) is merged. The release fixture check is currently mismatched by design until the owner re-stamps after the kernel-touching lanes settle; agents never stamp.

Not built, and not claimed: an arbitrary-repository compiler, formal proofs, live credential-tested providers, institutional identity, drag-and-drop diagram canvas, MCP server, measured human benefit.

## The 13 capability lanes

Each lane has a branch `lane/<name>` and a reserved [ADR](adr/README.md) number block.

| # | Lane | Goal | ADR block | Status |
|---|---|---|---|---|
| 1 | providers | Codex, Claude Code, OpenCode, Gemini CLI and OpenRouter proposal adapters over one subprocess-isolation base and a shared contract suite; providers stay proposal-only | 0021-0022 | open PR #4 |
| 2 | visual | UML and state diagrams generated from the executable model (Mermaid, PlantUML, DOT), semantic before/after diff, Studio "Visual" view | 0023-0024 | open PR #6 |
| 3 | bend | Bend 2 laws and proofs over all action sequences, generated from the model (`bend_proof`) | 0025-0026 | planned |
| 4 | tla | TLA+/TLC specification of the workflow and commit protocol, plus trace conformance (`tlc_model_check`) | 0027-0028 | planned |
| 5 | smt-bmc | Z3 policy soundness over the transaction grammar (`smt_proof`) and bounded exhaustive runtime search (`bounded_model_check`) | 0029-0030 | branch pushed (`lane/smt-bmc`), no PR |
| 6 | testing | Hypothesis property-based and model-based differential tests (`property_test`) | 0031-0032 | planned |
| 7 | mutation | Mutation analysis of the suite (`mutation_score`: fault-detection power, not correctness) | 0033-0034 | planned |
| 8 | quality | Ruff, mypy, import-linter architecture contracts, complexity budgets, coverage ratchets, noslop hooks | 0035-0036 | open PR #3 |
| 9 | metrics | Package metrics, latency, fitted scaling models and a dashboard | 0037-0038 | planned |
| 10 | hci | Measured HCI budgets on the running Studio: Fitts, Hick-Hyman, KLM-GOMS, WCAG 2.2, Doherty | 0039-0040 | open PR #7 |
| 11 | agents | MCP server that can inspect and verify but never approve or apply; skills and one-minute quickstarts for Claude Code, Codex, OpenCode and Gemini | 0041-0042 | open PR #8 |
| 12 | oss | README, community files, roadmap, docs site, link and diagram-drift gates | 0043-0044 | this pull request |
| 13 | okf | Knowledge base: an OKF v0.2 wiki deterministically linked to code | 0045-0046 | planned |

Lane hubs: [formal V&V](lanes/formal.md), [visual](lanes/visual.md), [agents](lanes/agents.md), [quality](lanes/quality.md), [metrics](lanes/metrics.md), [HCI](lanes/hci.md), [knowledge base](lanes/knowledge-base.md).

## Beyond the 13

Further work is tracked outside this table. The lane map and product thesis are in open PR #9 (`docs/engineering/LANE-MAP.md`, `docs/engineering/PRODUCT-THESIS.md`), so they are not linked from here until they merge. Per that PR, and all **planned** unless stated:

| Lane | Goal | ADR block | Status |
|---|---|---|---|
| demos | Scripted live-demo harness and honest scenario registry (cursor and typing recordings of the Studio) | 0047-0048 | open PR #5 |
| ddd-language | Ubiquitous-language editor and DDD tree in the Studio | 0051-0052 | planned |
| uml-editor | Drag-and-drop UML that issues typed semantic transactions | 0049-0050 | planned |
| imagegen | Consent-gated image generation through the provider port | 0053-0054 | planned |
| personas-e2e | Personas, ICP and persona-driven end-to-end scenarios | 0055-0056 | planned |
| ux, weave, dod, studio-ux | HCI research and prototype, linked-graph compiler, definition of done and scorecard, port of the redesign | 0057-0136 | planned |

## Milestones, in the order they unlock trust

1. **Merge the foundation lanes**: quality, providers, visual, agents. Result: enforced layering and typing, five agent CLIs as proposers, generated diagrams and the diff, an MCP surface.
2. **Owner re-stamps the release fixture** once the kernel-touching lanes settle. Result: `eija doctor` reports `release_fixture_matches: true` and verify and apply work from a clean checkout again.
3. **Formal and testing lanes**: Bend, TLA+, Z3 and bounded search, Hypothesis, mutation. Each lands as its own evidence kind with stated assumptions and bounds; a proof about a model is never presented as a proof about the runtime.
4. **Generated-artefact lanes**: metrics, HCI, knowledge base, then a single regeneration pass of committed snapshots and the README status table.
5. **Wave 2**: DDD language tree, drag-and-drop UML editor, image generation, personas and persona-driven end-to-end tests, then re-record the demos.

## Non-goals

A universal code compiler, a replacement for human code review outside the modelled domain, automatic approval of any kind, production deployment without the changes listed in [Security and trust](SECURITY_AND_TRUST.md), and any claim of measured human benefit without a real human study.

## How to change this page

Edit the table when a pull request merges or opens, update the date at the top, and keep the status vocabulary. Do not mark a row **on main** on the strength of a branch or a description.
