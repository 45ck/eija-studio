# Proposal providers

EIJA asks a model for an **untrusted proposal**: alternative readings of a change request. AI proposes; the kernel checks; the local owner decides. No provider can select a meaning, approve, apply, mint a receipt or touch protected policy. See [ADR-0020](adr/0020-multi-provider-agent-adapters.md), [ADR-0021](adr/0021-cli-provider-isolation-and-process-tree-kill.md) and [ADR-0022](adr/0022-live-provider-evidence-and-not-run.md).

| `--provider` | Backend | Auth (delegated, never read by EIJA) | Structured output | Tools off by (requested, not verified live) |
|---|---|---|---|---|
| `offline` | Deterministic fixture, not an LLM | none | n/a | n/a |
| `codex` | Codex CLI | `codex login` (ChatGPT sign-in; an API-key login is refused) | `--output-schema` | `--sandbox read-only`, shell/apps/web features off |
| `claude` | Claude Code CLI | `claude auth login` (claude.ai subscription; API-key logins refused here) | `--json-schema` | `--tools ""`, `--safe-mode`, `--permission-mode dontAsk` |
| `opencode` | OpenCode CLI | `opencode auth login` | prompt only, validated | inline deny-all permission config, empty config dir |
| `gemini` | Gemini CLI | the CLI's own Google sign-in | prompt only, validated | deny-all admin policy file, plan mode |
| `openrouter` | HTTPS | `OPENROUTER_API_KEY` or `--ask-key` (memory only) | `json_schema` strict | no `tools` in request |
| `anthropic` | HTTPS (optional) | `ANTHROPIC_API_KEY` or `--ask-key` (memory only) | `output_config.format` | no `tools` in request |

## Setup

```bash
py -3.12 -m venv .venv && .venv/Scripts/python -m pip install -e ".[dev,providers]"
.venv/Scripts/eija doctor --provider claude      # installed? version? required flags? signed in?
.venv/Scripts/eija propose "Let teachers sign off excursions." --provider claude --allow-network --consent
```

`doctor` uses only the vendor's official commands (`--version`, `--help`, `claude auth status`, `codex login status`, `opencode auth list`). It never opens an auth or token file and never calls a model. `live_test` is always `NOT_RUN` there. Gemini CLI has no login-status command, so its login shows `UNKNOWN` until a call is made and `doctor` reports `READY (login unverified)`: a call may be attempted, no login was confirmed (`login_verified: false`). `--model` is required for the two HTTPS providers (no default model, so a metered call never picks a model and price for you); a CLI's own default model is used when none is given.

Network use needs both `--allow-network` at start and per-request consent, exactly as for OpenRouter. A subscription CLI still sends data to the vendor and may consume plan usage.

## What is and is not sent

Sent to the model: the fixed instructions, your request text, and the synthetic baseline workflow (as canonical JSON), on **stdin**. For prompt-only providers the JSON Schema is appended.

Not sent, and expected not to be readable by the model: your repository (the CLI runs in an empty temporary directory that is removed afterwards), your environment (see below), and your CLI configuration where the CLI allows it (`--safe-mode`, `--ignore-user-config`, empty `XDG_CONFIG_HOME`). EIJA **requests** that the CLI disable its tools (flags in the table above), so tool output is not expected to be sent. Whether each CLI honours those flags is **not verified live**: the tests prove the flags are passed, and a schema-valid reply proves nothing about tool use (evidence records carry `lockdown_verified: false`). The vendor still sees the prompt and your account identity, as with any use of that CLI.

Child environment: an allow-list of system, locale and profile-location variables plus one config-directory variable per vendor (`CODEX_HOME`, `CLAUDE_CONFIG_DIR`). Any variable whose name looks like a key, token, secret, password or auth value is dropped even if allow-listed. `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `CLAUDE_CODE_OAUTH_TOKEN`, proxy credentials and studio tokens are never forwarded; sign in with the CLI instead. Non-secret network settings (`HTTPS_PROXY`, `NO_PROXY`, `SSL_CERT_FILE`, `NODE_EXTRA_CA_CERTS`) are also **not** forwarded today, so a CLI behind a corporate proxy or custom CA may fail with an opaque `PROVIDER_PROCESS_FAILED` or `PROVIDER_AUTH`; an explicit opt-in list is an open follow-up.

## Failure behaviour

One call, no retry, no fallback to another provider. Errors are stable codes with fixed text (`PROVIDER_NOT_READY`, `PROVIDER_AUTH`, `PROVIDER_RATE_LIMIT`, `PROVIDER_TIMEOUT`, `PROVIDER_OUTPUT_INVALID`, `PROVIDER_PROCESS_FAILED`); raw CLI output is never returned or stored. Output is capped at 256 KiB per stream while it is produced, the proposal at 64 KiB. On timeout the whole process tree is killed (psutil from the `providers` extra; `taskkill /T` or the process group otherwise). Usage may still have been billed when a call times out.

Windows: npm installs vendor CLIs as `.cmd` shims. EIJA unwraps the standard npm shim to `node <script>` and refuses any other `.cmd`, so arguments never pass through cmd.exe.

## Live evidence

Contract tests use a mocked runner and prove isolation and parsing, not vendor behaviour. Live results are recorded by hand, one provider at a time:

```bash
python scripts/live_provider_smoke.py --provider claude --consent
```

The current record is `evidence/live-providers/2026-09-28-windows.json`. `PASS` = a live call returned a schema-valid proposal (nothing about quality); `NOT_RUN` = a prerequisite was missing (reason recorded); `FAIL` = a call was made and failed.

| Provider | 2026-09-28 Windows result |
|---|---|
| `claude` 2.1.284 | PASS, schema-valid, model reported by the CLI |
| `codex` 0.144.1 | PASS, schema-valid, model not reported by the CLI |
| `opencode` 1.4.3 | NOT_RUN: 0 stored credentials |
| `gemini` 0.37.1 | NOT_RUN: CLI reported no auth method configured (exit 41) |
| `openrouter`, `anthropic` | NOT_RUN: no key in the environment |

Unverified live: tool lockdown for **every** CLI (claude and codex included; only the flags are tested), OpenCode's deny-all config and success event shape, OpenCode and Gemini stdin ingestion (Gemini gets a fixed `-p` instruction and the prompt on stdin), Gemini's deny-all policy and prompt-only JSON, the Anthropic structured-output request shape. A canary probe (planted file in the temporary directory, prompt asking for it) is the open follow-up that would verify lockdown.

## Known limits

* A CLI can ignore its own lockdown flags after an upgrade. `doctor` refuses CLIs whose `--help` lacks a required flag; it cannot prove a flag is honoured. Re-run the smoke after upgrades.
* A descendant that detaches from the process tree before it is observed can survive a timeout kill. Windows tracks descendants by polling (about 0.3 s), with no Job Object, so processes also outlive an EIJA process that is itself killed.
* Gemini: a supplemental `--admin-policy` file is ignored by the CLI when system-level `.toml` policies already exist (its policy-engine documentation); the CLI then follows the system policy, which may be less strict than the deny-all file. Not detected by `doctor`.
* POSIX (`killpg` fallback) is untested: the test suite has run on Windows only.
* Executables are looked up on `PATH` only (never the current directory) and only from absolute `PATH` entries.
* Prompt-only providers may wrap JSON in a Markdown fence; one outer fence is removed and the rest is validated. Anything else is rejected without repair.
* `total_cost_usd` from Claude Code is a list-price estimate for a subscription, not an invoice.
