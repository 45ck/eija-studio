# Agents

Status as of 2026-09-29: **providers in open PR #4, MCP server and quickstarts in open PR #8; neither is on `main`.**

## What works today

Any agent that can read [`AGENTS.md`](https://github.com/45ck/eija-studio/blob/main/AGENTS.md) and run shell commands can use the CLI (`eija compile`, `eija propose`, `eija list`, `eija verify`, `eija export`), and the repository ships a skill file at `.agents/skills/eija-studio/SKILL.md`. On `main` the built-in proposal providers are the offline fixture, OpenRouter and Codex. See [Getting started](../getting-started.md) for provider setup and consent flags.

## The rule that does not change

Providers and agents **propose**. They never select meaning, mint receipts, approve or apply, and there is no approve or apply port for them. Live inference needs the owner's explicit permission for egress and spend: `--allow-network` at startup plus per-request consent. EIJA never reads token files and never turns a subscription login into an API key ([ADR-0020](../adr/0020-multi-provider-agent-adapters.md), `proposed`).

## Coming

| Piece | ADRs | Status |
|---|---|---|
| Claude Code, OpenCode and Gemini CLI proposal adapters with a shared contract suite | 0021-0022 | open PR #4 |
| MCP server (inspect, compile, verify; never approve or apply), agent skills, one-minute quickstarts for Claude Code, Codex, OpenCode and Gemini | 0041-0042 | open PR #8 |

When the agents lane merges, the per-agent setup lives in `docs/agents/quickstart.md`. Until then this project makes no claim of an MCP server.
