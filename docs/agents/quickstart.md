# Agent quickstart: connect your agent in about a minute

EIJA Studio ships an MCP (Model Context Protocol) server so that Claude Code, Codex, OpenCode and Gemini CLI can create cases, request untrusted proposals, read derived views and run technical verification, **without** any way to select a meaning, edit, approve or apply. Read the [agent contract](contract.md) first (two minutes).

## 1. Install the server once

```bash
git clone https://github.com/45ck/eija-studio && cd eija-studio
python -m venv .venv                      # Python 3.11+
.venv/bin/python -m pip install -e ".[agents]"        # Windows: .venv\Scripts\python
```

The `agents` extra installs the official [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) (`mcp==2.2.0`). The server is `eija mcp --workspace PATH` over stdio; the workspace is a folder that holds the SQLite database and local keys, and is created on first use. It defaults to the offline fixture provider (deterministic, no network, not a model).

## 2. Print the config for your client

```bash
.venv/bin/python -m eija_studio mcp --workspace ~/eija-workspace --print-config claude    # or codex | opencode | gemini
```

This prints a copy-paste snippet with absolute paths, so it works from any directory. It writes nothing. The snippets below show the same result with placeholders: replace `PY` with the absolute path of your venv's Python and `WS` with the absolute workspace path.

### Claude Code

```bash
claude mcp add --scope project eija -- PY -m eija_studio mcp --workspace WS
```

`--scope project` writes `.mcp.json` in the current project (shareable; Claude Code asks you to approve it on first use). Use `--scope local` (the default, private to you and this project) or `--scope user` (all projects) if you prefer. Verify with `claude mcp list`, or `/mcp` inside a session.

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

Keep `"trust": false`: Gemini then asks before each tool call. Do not set it to true for a server you have not audited. `gemini mcp add --help` documents a CLI equivalent (untested here; the settings file above is the documented, tested-by-parse form).

## 3. First conversation

Ask your agent: *"Use the eija MCP server. Read eija://agent/contract, create a case for 'Let teachers sign off excursions.', propose, and show me the view."* Expect:

1. `create_case` returns a case id and `owner_next`.
2. `propose` returns a proposal labelled `UNTRUSTED_PROPOSAL` from the offline fixture (`live: false`).
3. `view_case` shows `human_understanding: UNKNOWN` and that **you** must select a meaning in the browser.
4. `eija serve --workspace WS --open` opens the Studio where you select, review and decide. After you select a meaning, the agent can `verify`, `impact` and `render` it.

## Using a live model provider (optional, owner decision)

By default nothing leaves your machine. To let `propose` call a networked provider, you (not the agent) start the server with both flags, e.g. `eija mcp --workspace WS --provider openrouter --model MODEL --allow-network --egress-consent` with `OPENROUTER_API_KEY` in the server's environment. Without both flags the command refuses to start. Tool arguments can never grant consent, and the key is never passed through the agent.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `MISSING_EXTRA` | Install the extra: `pip install -e ".[agents]"` in the venv that `PY` points to |
| Client times out at startup | Raise the startup timeout (Codex `startup_timeout_sec`, Gemini `timeout`); check `PY` is absolute |
| `verify` returns `SOURCE_REVIEW_REQUIRED` | The checkout differs from the owner-stamped release fixture (expected on a modified tree). The owner reviews the source; do not restamp |
| `verify` returns `MEANING_REQUIRED` | Correct: only the owner selects a meaning, in Studio |
| `DIAGRAMS_NOT_AVAILABLE` | No diagram renderer is wired into this server yet; use `format=json` or `text` |
| Nothing prints to the terminal | Correct: stdout is the protocol channel; logs go to stderr |

## Sources for the client syntax (checked 2026-09-28)

* Claude Code: `claude mcp add --help` (2.1.284) and <https://code.claude.com/docs/en/mcp> (scopes, `.mcp.json`, project approval).
* Codex CLI: `codex mcp add --help` (0.144.1) and <https://learn.chatgpt.com/docs/extend/mcp?surface=cli> (`[mcp_servers.<name>]`, `startup_timeout_sec`).
* OpenCode: `opencode mcp --help` (1.4.3) and <https://opencode.ai/docs/mcp-servers/> (`mcp` object, `type: "local"`, `command` array).
* Gemini CLI: `gemini mcp add --help` (0.37.1) and <https://github.com/google-gemini/gemini-cli/blob/main/docs/tools/mcp-server.md> (`mcpServers`, `trust`, `timeout`).
* MCP itself: <https://modelcontextprotocol.io> and the Python SDK linked above.

Client CLIs change quickly. If a snippet stops working, run the client's own `mcp add --help` and adapt the command and arguments; the server side (`eija mcp --workspace WS`) does not change.
