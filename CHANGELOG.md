# Change log

## Unreleased

Summary of the open-source foundation since 0.2.0. Nothing here changes kernel behaviour except where stated.

### Added

- Apache-2.0 licence, NOTICE, [ADR](docs/adr/README.md) index in MADR format (ADR-0015 to ADR-0020), OSS-first register ([docs/oss/REGISTER.md](docs/oss/REGISTER.md)), lane conventions in `AGENTS.md`, and nox gate sessions loaded as plugins from `quality/sessions/` (PR #2).
- Durable and ephemeral SQLite profiles, an application-owned `SandboxFactory` port, and a fast Windows test suite (PR #1). This is a kernel change: it means the source no longer matches the owner-stamped release fixture, so `eija doctor` reports `release_fixture_matches: false` and verify/apply return `SOURCE_REVIEW_REQUIRED` until the maintainer re-stamps.
- Front-door documentation (oss lane): README rewrite with a before/after state diagram generated from `domain.policy`, `docs/getting-started.md` (the previous README's install, provider and verification detail), CONTRIBUTING, CODE_OF_CONDUCT (Contributor Covenant 2.1), SECURITY, CITATION.cff, issue and pull-request templates, `docs/ROADMAP.md`, lane hub pages, a banner, ADR-0043.
- MkDocs Material configuration (`mkdocs.yml`, extra `docs`), and nox sessions `docs_links`, `readme_diagram`, `community_files` (fast and full), `docs` and `pr_status` (release; both `NOT_RUN` when their prerequisite is absent). `community_files` is skipped, never green, when PyYAML is missing. No deployment: hosted CI is unavailable.

### Changed

- The README is now the project's front door. Installation, OpenRouter, Codex, first-demonstration, compiler and operations detail moved to `docs/getting-started.md` without removal.

### Not added

Everything not on `main` in the [roadmap](docs/ROADMAP.md): formal V&V beyond the Bend laws (TLA+, Z3), property and mutation testing, metrics, HCI instrumentation, MCP server, knowledge base. Providers, visual, agents, HCI, metrics, Z3 and OKF work exists on open pull requests and is not part of this entry; the quality gates (lint, typing, architecture, complexity, coverage, dependencies), the demo harness and the Bend laws are already on `main`. See the [roadmap](docs/ROADMAP.md).

## 0.2.0 — 2026-09-27

First runnable unified local implementation, following the v0.1 consolidation specification.

Added browser Studio, CLI/semantic compiler, typed domain contracts, explicit semantic transactions, SQLite unit of work, current-authority checks before replay, transactional audit/outbox, subject-bound local evidence and review/apply, derived rule/state/journey views, fixed-point mapped impact, source-fixture checks, offline/OpenRouter/Codex proposal adapters, mock provider tests, regression/crash/concurrency tests, HTTP/browser-component/wheel smoke tests, source contracts, engineering review and agent handoff.

Additional review hardened receipt coverage (empty/missing/duplicated cells, false boolean types, invalid subject/state), provider accounting-envelope rejection and Codex output decoding. An early test mutated an already-true value to true; that test assertion was corrected to actually mutate the value, then the complete suite was rerun. Historical intermediate reports are not presented as current release evidence.

Not added: arbitrary-repository compiler, independent formal proofs, live credential-tested providers, institutional SSO, production effects, multi-tenant isolation, drag-and-drop diagram canvas, MCP server, independent hidden evaluation or measured human benefit. Ordinary browser-network testing was blocked by the environment; separate real TCP and Chromium component tests passed.
