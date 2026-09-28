# ADR-0021: Agent-CLI providers run in one isolated, bounded, tree-killing base class

* Status: accepted
* Date: 2026-09-28
* Lane: providers (implements [ADR-0020](0020-multi-provider-agent-adapters.md))

## Context and problem statement

Codex, Claude Code, OpenCode and Gemini CLI are agents with shell and file tools. EIJA calls them only to obtain an untrusted `Proposal`. Each call must not read the user's files, forward secrets, be steered through argv, outlive its deadline, or return more than a bounded reply. The first Codex adapter solved this once, inline; four more copies would drift.

## Decision drivers

* Windows first: npm installs vendor CLIs as `.cmd` shims, and running a `.cmd` through cmd.exe re-parses arguments (BatBadBut class of argument injection).
* Subscription logins must keep working, so credentials cannot be stripped along with the environment, and token files must never be read by EIJA.
* A killed CLI can leave grandchildren (node children, MCP servers) running and holding pipes.
* Each vendor differs in how it disables tools and forces structured output; the differences belong in thin adapters, the safety properties in one place.

## Considered options

* One `CliProposalProvider` base plus thin vendor adapters (chosen).
* One adapter per vendor, each owning its own subprocess code.
* Vendor SDKs or the Agent Client Protocol for every agent.

## Decision outcome

Chosen option: "base class plus thin adapters", because the safety properties are identical across vendors and are then tested once by a shared contract suite.

The base class guarantees, for every CLI: an empty temporary working directory; an environment allow-list (system and locale variables, plus a per-vendor config-directory variable) with a second filter that drops any name that looks like a key, token, secret, password or auth variable; the prompt on **stdin** only (argv carries fixed flags and a validated model name); `shell=False`; output capped while it is produced; a wall-clock deadline; kill of the process **tree** on timeout or overflow; no automatic retry or fallback; and sanitised error codes (`PROVIDER_AUTH`, `PROVIDER_TIMEOUT`, ...), never raw CLI output.

Decisions inside that:

1. **npm shims are unwrapped, never executed through cmd.exe.** `resolve_command` parses the exact shape npm generates and runs `node <script>` directly; a `.cmd` it does not recognise is refused.
2. **Process tree kill uses psutil** (the `providers` extra), snapshotting descendants before and while the process runs, then killing them; POSIX also kills the process group. Without psutil, Windows falls back to `taskkill /T /F` and POSIX to `killpg`. A descendant that reparents before it was ever observed can survive; the extra makes that window small, not zero.
3. **Claude Code uses `--safe-mode`, not `--bare`.** `--bare` never reads OAuth or the keychain, so it silently requires an API key and defeats the subscription login. `--safe-mode` disables the account's CLAUDE.md, hooks, skills, plugins and MCP while auth still works; `--tools ""` removes built-in tools and `--permission-mode dontAsk --permission-prompts none` denies anything that would prompt.
4. **`ANTHROPIC_API_KEY`, `CLAUDE_CODE_OAUTH_TOKEN`, `OPENAI_API_KEY`, `GEMINI_API_KEY` and similar are never forwarded.** A CLI provider is the login path; the keyed paths are the separate `openrouter` and `anthropic` providers with a key held in memory only.
5. **CLIs without a structured-output flag** (OpenCode, Gemini) get the schema in the prompt; the reply is validated by the same `Proposal` model, and at most one outer Markdown fence is removed. This is a request, not a guarantee, and is labelled so.
6. **OpenCode** additionally gets an empty `XDG_CONFIG_HOME` (user plugins, instructions and MCP are not loaded; credentials live in the data directory and still work), deny-all permissions in inline config, and treats an `error` event as failure because it exits 0 on API errors. **Gemini** gets a deny-all admin-tier policy file and plan mode.

### Consequences

* Good: adding a CLI is one small module plus one row in the contract-suite table; the safety tests come for free.
* Good: no vendor SDK, no token handling in EIJA.
* Bad: the OpenCode and Gemini tool-lockdown mechanisms are documented behaviour, not live-verified here (no login on the reference machine). Only the contract test (flags present) covers them.
* Bad: the CLI flags are moving targets. `doctor()` refuses a CLI whose help lacks a required flag rather than running with weaker isolation.
* Revisit when: a vendor ships a stable sandboxed non-interactive mode or ACP support that removes the need for flag-level lockdown.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| psutil | Adopted for the process tree | Drop to taskkill/killpg (already the fallback) |
| Windows Job Objects (ctypes) | More robust than parent links but ~60 lines of ctypes with a spawn race, and Python's Popen cannot create the child suspended | Adopt if a mature wrapper appears; the kill function is one place |
| Vendor SDKs (Codex SDK, Claude Agent SDK, Gemini SDK) | Would move token handling and tool policy into EIJA; the Agent SDK is itself an agent harness | Revisit if a vendor SDK offers no-tools, no-config structured output |
| Agent Client Protocol | Not supported uniformly by all four CLIs | Revisit when it is |
