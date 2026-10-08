# Agent quickstart: connect your agent in about a minute

EIJA Studio ships an MCP (Model Context Protocol) server so that Claude Code, Codex, OpenCode and Gemini CLI can create cases, request untrusted proposals, read derived views and run technical verification, **without** any way to select a meaning, edit, approve or apply. Read the [agent contract](contract.md) first (two minutes).

## 1. Install the server once

```bash
git clone https://github.com/45ck/eija-studio && cd eija-studio
python -m venv .venv                      # Python 3.11+
.venv/bin/python -m pip install -e ".[agents]"        # Windows: .venv\Scripts\python
```

The `agents` extra installs the official [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) (`mcp==2.2.0`). The server is `eija mcp --workspace PATH` over stdio; the workspace is a folder that holds the SQLite database and local keys, and is created on first use. It defaults to the offline fixture provider (deterministic, no network, not a model).

Use the same explicit `--pack PATH` and `--repo PATH` for Studio and MCP. `--repo` connects a local Git repository read-only: tracked Python and annotated UI facts, declared bindings, hashes and coverage gaps. It does not execute the target or modify its code. For first self-dogfooding use `--pack packs/eija-review-slice --repo .` with a **fresh** workspace; this pack is a declared reference journey, not a complete extracted specification of EIJA. `--print-config` preserves both paths. Existing workspaces remain bound to the exact pack content; legacy identity requires an explicit migration instead of silent adoption.

Read `pack()` to see domain terms and source connections; use `repository_impact(term)` and `repository_source(reference)` for known links. Once an owner selects a case, `affordances(case_id)` shows available typed edits and `edit_check(case_id, proposal)` checks a proposed edit without persisting or applying it. These tools help an agent explain its intended change while leaving selection and application with the owner.

## 2. Print the config for your client

```bash
.venv/bin/python -m eija_studio mcp --workspace ~/eija-workspace --print-config claude    # or codex | opencode | gemini
```

This prints a copy-paste snippet with absolute paths, so it works from any directory. It writes nothing. The Claude one-liner is quoted for the shell you print it from (every argument in double quotes on Windows for cmd.exe and PowerShell, single quotes elsewhere; on Windows a path containing `$`, a backtick, `%` or a double quote is refused because those still expand inside quotes, so use the `.mcp.json` or another JSON form for such a path); pasting it into a different shell needs its own quoting, or use the `.mcp.json` form below. The snippets below show the same result with placeholders: replace `PY` with the absolute path of your venv's Python and `WS` with the absolute workspace path.

### Claude Code

```bash
claude mcp add --scope project eija -- PY -m eija_studio mcp --workspace WS
```

`--scope project` writes `.mcp.json` in the current project (shareable; Claude Code asks you to approve it on first use). **Never put an API key in that file**: it is meant to be committed (see "Using a live model provider" below). Use `--scope local` (the default, private to you and this project) or `--scope user` (all projects) if you prefer. Verify with `claude mcp list`, or `/mcp` inside a session.

```json
{ "mcpServers": { "eija": { "type": "stdio", "command": "PY", "args": ["-m", "eija_studio", "mcp", "--workspace", "WS"] } } }
```

### Codex CLI

Add to `~/.codex/config.toml` (or run `codex mcp add eija -- PY -m eija_studio mcp --workspace WS`):

```toml
[mcp_servers.eija]
command = "PY"
args = ["-m", "eija_studio", "mcp", "--workspace", "WS"]
startup_timeout_sec = 30   # default is 10; the first import of the SDK can be slower
enabled = true
```

`codex mcp list` shows configured servers. On Windows, escape backslashes in TOML strings or use single-quoted literal strings.

### OpenCode

Add to `opencode.json` (project) or `~/.config/opencode/opencode.json` (global):

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "eija": { "type": "local", "command": ["PY", "-m", "eija_studio", "mcp", "--workspace", "WS"], "enabled": true }
  }
}
```

`opencode mcp list` shows status. Note that `command` is a single array (executable and arguments together), unlike the other clients.

### Gemini CLI

Add to `~/.gemini/settings.json` (user) or `.gemini/settings.json` (project):

```json
{
  "mcpServers": {
    "eija": { "command": "PY", "args": ["-m", "eija_studio", "mcp", "--workspace", "WS"], "timeout": 60000, "trust": false }
  }
}
```

Keep `"trust": false`: Gemini then asks before each tool call. Do not set it to true for a server you have not audited. `gemini mcp add --scope project --timeout 60000 eija PY -m eija_studio mcp --workspace WS` writes this same file shape.

## 3. First conversation

Ask your agent: *"Use the eija MCP server. Read eija://agent/contract, create a case for 'Let teachers sign off excursions.', propose, and show me the view."* Expect:

1. `create_case` returns a case id and `owner_next`.
2. `propose` returns a proposal labelled `UNTRUSTED_PROPOSAL` from the offline fixture (`live: false`).
3. `view_case` shows `human_understanding: UNKNOWN` and that **you** must select a meaning in the browser.
4. `eija serve --workspace WS --open` opens the Studio where you select, review and decide. After you select a meaning, the agent can `verify`, `impact` and `render` it.

## Using a live model provider (optional, owner decision)

By default nothing leaves your machine. To let `propose` call a networked provider, you (not the agent) start the server with both flags, e.g. `eija mcp --workspace WS --provider openrouter --model MODEL --allow-network --egress-consent`. Without both flags the command refuses to start. Tool arguments can never grant consent, and the key is never passed through the agent.

**Read this before you pass `--egress-consent`.** It is *standing* consent, not per-request consent. It is set once when the server starts and covers every `propose` call for as long as the server runs. The agent can call `propose` as often as it likes, and each call sends the case request text to the provider and may spend money on a paid one, without asking you again. Two limits apply:

* `--max-provider-calls N` (default 3; `0` forbids live calls) caps networked provider calls per server session. Attempts are counted before the call, including attempts the kernel then refuses. Beyond the cap `propose` returns the tool error `PROVIDER_CALL_LIMIT`; only you can raise it, by restarting the server. Restarting resets the count, so it is a per-session brake, not a budget: also set a spend limit on the provider account.
* Requests must stay synthetic: assume anything in a case request reaches the provider.

**Where the key goes.** The server is started by your agent client (stdio), so its environment is whatever the client gives it. Do not paste the key into the client's config: for Claude Code project scope (`.mcp.json`) that writes a secret into a file made to be committed, and the other clients' config files are just as easy to commit or sync by accident. Export `OPENROUTER_API_KEY` in the shell that launches the client and use the client's environment passthrough (inherit or reference by name), never a literal value:

| Client | Passthrough (documented; not run live here) |
|---|---|
| Claude Code | The server inherits the shell environment; nothing to add. To be explicit use `"env": { "OPENROUTER_API_KEY": "${OPENROUTER_API_KEY}" }` (variable reference, not the key) |
| Codex CLI | `env_vars = ["OPENROUTER_API_KEY"]` in `[mcp_servers.eija]` (forwards by name; do not use `env = { ... = "sk-..." }`) |
| Gemini CLI | It redacts variables matching `*KEY*` from what servers inherit, so declare it: `"env": { "OPENROUTER_API_KEY": "$OPENROUTER_API_KEY" }` (reference, not the key) |
| OpenCode | `environment` exists for local servers, but inheritance and `{env:VAR}` substitution for local servers are undocumented: UNVERIFIED. Export the variable in the launching shell, run `eija doctor --provider openrouter` to confirm the server side sees it, and do not write the key into `opencode.json` |

Never commit the key or a config file that contains it. If a key was ever written into a committed config, treat it as leaked and rotate it. A live provider call has NOT_RUN status in this repository's tests: only the offline provider and a mocked networked provider are exercised.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `MISSING_EXTRA` | Install the extra: `pip install -e ".[agents]"` in the venv that `PY` points to |
| Client times out at startup | Raise the startup timeout (Codex `startup_timeout_sec`, Gemini `timeout`); check `PY` is absolute |
| `verify` returns `SOURCE_REVIEW_REQUIRED` | The checkout differs from the owner-stamped release fixture (expected on a modified tree). The owner reviews the source; do not restamp |
| `verify` returns `MEANING_REQUIRED` | Correct: only the owner selects a meaning, in Studio |
| `DIAGRAMS_NOT_AVAILABLE` | A custom server has no diagram renderer; the CLI server wires text diagram formats by default |
| `FORMAT_UNSUPPORTED` for SVG | Built-in MCP rendering provides Mermaid, PlantUML and DOT source; use the Studio for visual rendering |
| Nothing prints to the terminal | Correct: stdout is the protocol channel; logs go to stderr |

## Verification status of the client syntax (checked 2026-09-29 on this repository's development machine)

Each snippet printed by `eija mcp --print-config <client>` was fed to the real client CLI inside a scratch, project-scoped directory (no global client config modified):

| Client (version) | What was actually checked | Result |
|---|---|---|
| Claude Code 2.1.284 | `claude mcp add --scope project` wrote `.mcp.json`; `claude mcp get eija` read it back | Verified: same `mcpServers.eija` shape as shown. Server start is not run: Claude Code waits for project approval in an interactive session (NOT_RUN) |
| Codex CLI 0.144.1 | `[mcp_servers.eija]` file loaded via `CODEX_HOME`; `codex mcp list` / `get` | Verified: parsed, `startup_timeout_sec` and enabled shown. Server start not run (NOT_RUN) |
| OpenCode 1.4.3 | `opencode.json` in a scratch project; `opencode mcp list` | Verified end to end: status `connected` (it started `eija mcp` and completed the MCP handshake) |
| Gemini CLI 0.37.1 | `gemini mcp add --scope project` wrote `.gemini/settings.json` | Verified: the CLI writes the same `mcpServers.eija` keys. `gemini mcp list` printed nothing in the scratch directory (likely folder trust), so connection is unverified. `trust: false` matches the documented `--trust` flag |

The environment-passthrough rows above come from each client's documentation, not from a live run.

## What has actually been exercised per client

| Client | Status | Evidence and limit |
|---|---|---|
| Claude Code 2.1.284 | Round-trip run once by the lane author: `tools/list` returned the seven tools and `create_case` + `propose` executed | Reported in PR #8 (about US$0.11). The transcript is not committed, so this repository cannot re-check it |
| OpenCode 1.4.3 | Connected: `opencode mcp list` printed `eija connected` for the generated `opencode.json` (2026-09-29) | Connection and startup only; no tool call was made from OpenCode |
| Codex CLI 0.144.1 | Config accepted: `codex mcp get eija` showed the entry enabled, stdio, `startup_timeout_sec: 30` | Config parsing only; no connection was made |
| Gemini CLI 0.37.1 | NOT_RUN | `gemini mcp list` printed nothing with the generated file (inconclusive); the JSON is parse-tested only |

## Sources for the client syntax

* Claude Code: `claude mcp add --help` (2.1.284) and <https://code.claude.com/docs/en/mcp> (scopes, `.mcp.json`, project approval).
* Codex CLI: `codex mcp add --help` (0.144.1) and <https://learn.chatgpt.com/docs/extend/mcp?surface=cli> (`[mcp_servers.<name>]`, `startup_timeout_sec`).
* OpenCode: `opencode mcp --help` (1.4.3) and <https://opencode.ai/docs/mcp-servers/> (`mcp` object, `type: "local"`, `command` array).
* Gemini CLI: `gemini mcp add --help` (0.37.1) and <https://github.com/google-gemini/gemini-cli/blob/main/docs/tools/mcp-server.md> (`mcpServers`, `trust`, `timeout`).
* MCP itself: <https://modelcontextprotocol.io> and the Python SDK linked above.

Client CLIs change quickly. If a snippet stops working, run the client's own `mcp add --help` and adapt the command and arguments; the server side (`eija mcp --workspace WS`) does not change.
