# Change log

## 0.2.0 — 2026-09-27

First runnable unified local implementation, following the v0.1 consolidation specification.

Added browser Studio, CLI/semantic compiler, typed domain contracts, explicit semantic transactions, SQLite unit of work, current-authority checks before replay, transactional audit/outbox, subject-bound local evidence and review/apply, derived rule/state/journey views, fixed-point mapped impact, source-fixture checks, offline/OpenRouter/Codex proposal adapters, mock provider tests, regression/crash/concurrency tests, HTTP/browser-component/wheel smoke tests, source contracts, engineering review and agent handoff.

Additional review hardened receipt coverage (empty/missing/duplicated cells, false boolean types, invalid subject/state), provider accounting-envelope rejection and Codex output decoding. An early test mutated an already-true value to true; that test assertion was corrected to actually mutate the value, then the complete suite was rerun. Historical intermediate reports are not presented as current release evidence.

Not added: arbitrary-repository compiler, independent formal proofs, live credential-tested providers, institutional SSO, production effects, multi-tenant isolation, drag-and-drop diagram canvas, MCP server, independent hidden evaluation or measured human benefit. Ordinary browser-network testing was blocked by the environment; separate real TCP and Chromium component tests passed.
