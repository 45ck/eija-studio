# ADR-0020: Proposal providers for Codex, Claude Code, OpenCode, Gemini CLI and OpenRouter

* Status: accepted
* Date: 2026-09-28

## Context and problem statement

People use different agent CLIs, often with subscription logins rather than API keys. EIJA should accept interpretations from any of them without giving any of them authority.

## Decision outcome

One `CliProposalProvider` base class owns subprocess isolation: an empty working directory, an environment allow-list, structured output, a timeout, and killing the process tree on both Windows and POSIX. Each vendor is a thin adapter. Authentication is always delegated to the official CLI's own login, for example `codex login` or the `claude` subscription login. EIJA never reads token files and never turns a subscription into an API key.

A shared contract test suite runs against every adapter with a mocked runner. Live smoke tests are opt-in, need owner consent, and record the CLI version. Providers stay proposal-only: they can never select meaning, mint receipts, approve or apply.
