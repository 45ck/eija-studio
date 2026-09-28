# Architecture decision records

Format: [MADR](https://adr.github.io/madr/); start new records from [template.md](template.md). A record is never rewritten after acceptance. It is superseded by a new one.

| ADR | Decision | Status |
|---|---|---|
| [0000](0000-poc-decision-log.md) | v0.2 POC decision log (ADR-001 … ADR-014: modular monolith, frozen vocabulary, AI proposal-only, SQLite unit of work, computed evidence, single local owner, …) | accepted |
| [0015](0015-open-source-under-apache-2.md) | Publish as open source under Apache-2.0 | accepted |
| [0016](0016-oss-first-adapters-not-engines.md) | OSS first: build adapters, not engines | accepted |
| [0017](0017-local-quality-gates.md) | Local quality gates: nox sessions + noslop enforcement | accepted |
| [0018](0018-formal-vv-portfolio.md) | Formal V&V portfolio: each technique is a distinct evidence kind | proposed |
| [0019](0019-diagrams-generated-from-executable-model.md) | Diagrams are generated projections of the executable model | proposed |
| [0020](0020-multi-provider-agent-adapters.md) | Proposal providers: Codex, Claude Code, OpenCode, Gemini CLI, OpenRouter | proposed |
| [0039](0039-hci-law-instrumentation.md) | HCI-law instrumentation: Playwright + axe-core + pure formula modules | accepted |
| [0040](0040-hci-budgets-as-ratchets-and-harness-identity.md) | HCI budgets are ratchets; browser tests opt-in; journey under the harness identity | accepted |

## Reserved numbers for capability lanes

Reserving numbers stops parallel lanes from colliding. A lane that needs more records uses its reserved block.

| Numbers | Lane |
|---|---|
| 0021–0022 | Agent providers (CLI adapters, contract suite) |
| 0023–0024 | Visual model: UML/diagram generation and visual diff |
| 0025–0026 | Formal: Bend laws and proofs |
| 0027–0028 | Formal: TLA+/TLC specification and trace conformance |
| 0029–0030 | Formal: Z3 policy soundness and bounded model checking |
| 0031–0032 | Testing: property-based and model-based tests |
| 0033–0034 | Mutation analysis |
| 0035–0036 | Quality gates, architecture fitness functions and static analysis |
| 0037–0038 | Metrics and quantitative models |
| 0039–0040 | HCI laws and usability instrumentation |
| 0041–0042 | Agent integration (MCP server, skills) |
| 0043–0044 | OSS community, documentation and release |
| 0045–0046 | Knowledge base: OKF v0.2 wiki deterministically linked to code |
