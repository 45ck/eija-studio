---
type: Architecture Decision Record
title: 'ADR-0021: Agent-CLI providers run in one isolated, bounded, tree-killing base class'
description: Codex, Claude Code, OpenCode and Gemini CLI are agents with shell and file tools.
resource: repo://docs/adr/0021-cli-provider-isolation-and-process-tree-kill.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0021-cli-provider-isolation-and-process-tree-kill.md
  title: 0021-cli-provider-isolation-and-process-tree-kill.md
  hash_method: lf-sha256-v1
  sha256: 4d18f0aab6780416ff1f3f197f2d9ed94b88663cb31019c432bd07e98a0732e5
notes_baseline: c884feee8b7bdfe8d5b9251853d11aa5e344308d84fd735347cc89e3580a8dff
---

# ADR-0021: Agent-CLI providers run in one isolated, bounded, tree-killing base class

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-28 |
| Lane | providers (implements [ADR-0020](repo://docs/adr/0020-multi-provider-agent-adapters.md)) |
| Source | `repo://docs/adr/0021-cli-provider-isolation-and-process-tree-kill.md` |

## Decision outcome (verbatim)

> Chosen option: "base class plus thin adapters", because the safety properties are identical across vendors and are then tested once by a shared contract suite.
>
> The base class guarantees, for every CLI: an empty temporary working directory; an environment allow-list (system and locale variables, plus a per-vendor config-directory variable) with a second filter that drops any name that looks like a key, token, secret, password or auth variable; the prompt on **stdin** only (argv carries fixed flags and a validated model name); `shell=False`; output capped while it is produced; a wall-clock deadline; kill of the process **tree** on timeout or overflow; no automatic retry or fallback; and sanitised error codes (`PROVIDER_AUTH`, `PROVIDER_TIMEOUT`, ...), never raw CLI output.
>
> Decisions inside that:
>
> 1. **npm shims are unwrapped, never executed through cmd.exe.** `resolve_command` parses the exact shape npm generates and runs `node <script>` directly; a `.cmd` it does not recognise is refused.
> 2. **Process tree kill is layered.** On Windows the child is placed in a Job Object with kill-on-close (`_winjob.py`, about 100 lines of ctypes), so descendants are followed by membership and a grandchild that outlives a fast-exiting parent cannot escape; on POSIX the child starts in its own session and the process group is killed. psutil (the `providers` extra) snapshots descendants right after start and every 50 ms as a second layer, and Windows falls back to `taskkill /T /F` without it. A descendant that deliberately breaks away (double fork with `setsid`, `CREATE_BREAKAWAY_FROM_JOB`) or that was spawned in the microseconds before the job is attached can survive. If one keeps a pipe open, the runner still returns its timeout and leaves the reader thread to be reaped: closing a pipe a thread is blocked reading would hang the caller (found in review, regression-tested).
> 3. **Claude Code uses `--safe-mode`, not `--bare`.** `--bare` never reads OAuth or the keychain, so it silently requires an API key and defeats the subscription login. `--safe-mode` disables the account's CLAUDE.md, hooks, skills, plugins and MCP while auth still works; `--tools ""` removes built-in tools and `--permission-mode dontAsk --permission-prompts none` denies anything that would prompt.
> 4. **`ANTHROPIC_API_KEY`, `CLAUDE_CODE_OAUTH_TOKEN`, `OPENAI_API_KEY`, `GEMINI_API_KEY` and similar are never forwarded.** A CLI provider is the login path; the keyed paths are the separate `openrouter` and `anthropic` providers with a key held in memory only.
> 5. **CLIs without a structured-output flag** (OpenCode, Gemini) get the schema in the prompt; the reply is validated by the same `Proposal` model, and at most one outer Markdown fence is removed. This is a request, not a guarantee, and is labelled so.
> 6. **OpenCode** additionally gets an empty `XDG_CONFIG_HOME` (OpenCode's own config, plugins and MCP entries are not read from the user's directory; credentials live in the data directory and still work; other discovery paths such as `~/.agents/skills` are still visible, and the deny-all permission config is what stops the model using them), deny-all permissions in inline config, and treats an `error` event as failure because it exits 0 on API errors. **Gemini** gets a deny-all admin-tier policy file and plan mode.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0020: Proposal providers for Codex, Claude Code, OpenCode, Gemini CLI and OpenRouter](/adrs/0020-multi-provider-agent-adapters.md) - People use different agent CLIs, often with subscription logins rather than API keys.

## Referenced by

* [Agent providers (CLI adapters, contract suite)](/lanes/0021-agent-providers.md) - Capability lane with ADR numbers 0021–0022 reserved.
<!-- okf:generated:end links -->
