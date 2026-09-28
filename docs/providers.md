# Proposal providers

EIJA asks a model for an **untrusted proposal**: alternative readings of a change request. AI proposes; the kernel checks; the local owner decides. No provider can select a meaning, approve, apply, mint a receipt or touch protected policy. See [ADR-0020](adr/0020-multi-provider-agent-adapters.md), [ADR-0021](adr/0021-cli-provider-isolation-and-process-tree-kill.md) and [ADR-0022](adr/0022-live-provider-evidence-and-not-run.md).

| `--provider` | Backend | Auth (delegated, never read by EIJA) | Structured output | Tools off by |
|---|---|---|---|---|
| `offline` | Deterministic fixture, not an LLM | none | n/a | n/a |
| `codex` | Codex CLI | `codex login` (ChatGPT sign-in; an API-key login is refused) | `--output-schema` | `--sandbox read-only`, shell/apps/web features off |
| `claude` | Claude Code CLI | `claude auth login` (claude.ai subscription; API-key logins refused here) | `--json-schema` | `--tools ""`, `--safe-mode`, `--permission-mode dontAsk` |
| `opencode` | OpenCode CLI | `opencode auth login` | prompt only, validated | inline deny-all permission config (`OPENCODE_CONFIG_CONTENT`), `--pure`, `XDG_CONFIG_HOME` pointed at an empty directory |
| `gemini` | Gemini CLI | the CLI's own Google sign-in | prompt only, validated | deny-all admin policy file, plan mode |
| `openrouter` | HTTPS | `OPENROUTER_API_KEY` or `--ask-key` (memory only) | `json_schema` strict | no `tools` in request |
| `anthropic` | HTTPS (optional) | `ANTHROPIC_API_KEY` or `--ask-key` (memory only); also needs an explicit `--model` (no default is baked in) | `output_config.format` | no `tools` in request |

## Setup

```bash
py -3.12 -m venv .venv && .venv/Scripts/python -m pip install -e ".[dev,providers]"
.venv/Scripts/eija doctor --provider claude      # installed? version? required flags? signed in?
.venv/Scripts/eija propose "Let teachers sign off excursions." --provider claude --allow-network --consent
```

`doctor` uses only the vendor's official commands (`--version`, `--help`, `claude auth status`, `codex login status`, `opencode auth list`). It never opens an auth or token file and never calls a model. `live_test` is always `NOT_RUN` there. Gemini CLI has no login-status command, so its login shows `UNKNOWN` until a call is made.

Network use needs both `--allow-network` at start and per-request consent, exactly as for OpenRouter. A subscription CLI still sends data to the vendor and may consume plan usage.

## What is and is not sent

Sent to the model: the fixed instructions, your request text, and the synthetic baseline workflow (as canonical JSON), on **stdin**. For prompt-only providers the JSON Schema is appended.

Not sent, and not readable by the model: your repository (the CLI runs in an empty temporary directory that is removed afterwards), your environment (see below), and any tool output, because tools are disabled. Your CLI configuration is left out where the CLI offers a switch for it (`--safe-mode`, `--ignore-user-config`, `--pure` with an empty `XDG_CONFIG_HOME`), but that is the CLI's own promise and is not proven here: OpenCode, for example, still lists skills (`opencode debug skill` on the reference machine showed them, with its `skill` tool disabled by the deny-all config) from `~/.agents/skills`, and the only thing keeping the model from using one is the deny-all permission config (its `skill` tool is denied). The vendor still sees the prompt and your account identity, as with any use of that CLI.

Child environment: an allow-list of system, locale and profile-location variables plus one config-directory variable per vendor (`CODEX_HOME`, `CLAUDE_CONFIG_DIR`). Any variable whose name looks like a key, token, secret, password or auth value is dropped even if allow-listed. `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `CLAUDE_CODE_OAUTH_TOKEN`, proxy credentials and studio tokens are never forwarded; sign in with the CLI instead.

## Failure behaviour

One call, no retry, no fallback to another provider. Errors are stable codes with fixed text (`PROVIDER_NOT_READY`, `PROVIDER_AUTH`, `PROVIDER_RATE_LIMIT`, `PROVIDER_TIMEOUT`, `PROVIDER_OUTPUT_INVALID`, `PROVIDER_PROCESS_FAILED`); raw CLI output is never returned or stored. Output is capped at 256 KiB per stream while it is produced, the proposal at 64 KiB. On timeout or overflow the whole process tree is killed: a Windows Job Object with kill-on-close (or, on POSIX, the process group the child was started in), plus psutil from the `providers` extra, which snapshots descendants right after start and every 50 ms; without psutil Windows falls back to `taskkill /T`. If a descendant outlives the tree kill and keeps a pipe open, the call still returns its timeout; the reader thread is left to be reaped rather than blocking the caller. Usage may still have been billed when a call times out.

Before each call `propose` runs `doctor` again (`--version`, `--help` and the vendor's login-status command: three short local CLI runs, roughly 10 s in total on the reference machine) so a signed-out or upgraded CLI is caught before anything billable. The smoke evidence's `latency_s` includes that cost.

Windows: npm installs vendor CLIs as `.cmd` shims. EIJA unwraps the standard npm shim to `node <script>` and refuses any other `.cmd`, so arguments never pass through cmd.exe.

## Live evidence

Contract tests use a mocked runner and prove isolation and parsing, not vendor behaviour. Live results are recorded by hand, one provider at a time:

```bash
python scripts/live_provider_smoke.py --provider claude --consent
```

The current record is `evidence/live-providers/2026-09-28-windows.json`. It supersedes `evidence/live-provider-status.json`, which is the frozen v0.2.0 release snapshot (listed in `MANIFEST.json`, so it is not edited): that file still says Codex is `NOT_RUN` because no Codex executable or login existed when v0.2.0 was cut. `PASS` = a live call returned a schema-valid proposal (nothing about quality); `NOT_RUN` = a prerequisite was missing (reason recorded); `FAIL` = a call was made and failed.

| Provider | 2026-09-28 Windows result |
|---|---|
| `claude` 2.1.284 | PASS, schema-valid, model reported by the CLI |
| `codex` 0.144.1 | PASS, schema-valid, model not reported by the CLI |
| `opencode` 1.4.3 | NOT_RUN: 0 stored credentials |
| `gemini` 0.37.1 | NOT_RUN: CLI reported no auth method configured (exit 41) |
| `openrouter`, `anthropic` | NOT_RUN: no key in the environment |

Unverified live: OpenCode's deny-all config and success event shape, Gemini's deny-all policy and prompt-only JSON, the Anthropic structured-output request shape.

## Known limits

* A CLI can ignore its own lockdown flags after an upgrade. `doctor` refuses CLIs whose `--help` lacks a required flag; it cannot prove a flag is honoured. Re-run the smoke after upgrades.
* A descendant that deliberately breaks away from the process tree (a POSIX double fork with `setsid`, or `CREATE_BREAKAWAY_FROM_JOB` where the job allows it) before it is observed can survive a timeout kill. The Windows job is attached a few microseconds after `Popen` returns; a child spawned in that gap is only caught by the psutil scan.
* The shared contract suite (`tests/test_provider_contract.py`) runs the full secret, stdin, lockdown, working-directory and no-retry matrix over the four CLI adapters. The two HTTP providers get a smaller matrix over a mock transport (no tools in the request, key only in a header, one attempt, sanitised errors, size cap, wrong-label rejection); they have no subprocess, environment or working directory to isolate.
* Prompt-only providers may wrap JSON in a Markdown fence; one outer fence is removed and the rest is validated. Anything else is rejected without repair.
* `total_cost_usd` from Claude Code is a list-price estimate for a subscription, not an invoice.
