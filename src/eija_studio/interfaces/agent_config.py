"""Copy-paste MCP client configuration for `eija mcp --print-config <client>`.

Pure text generation: no MCP SDK import, so it works before the `agents` extra is installed. Each
snippet follows the client's documented syntax (sources are listed in docs/agents/quickstart.md).
It does NOT install or verify anything in the client; the owner pastes it.
"""
from __future__ import annotations

import json
import shlex
from pathlib import Path

CLIENTS: tuple[str, ...] = ("claude", "codex", "opencode", "gemini")
SERVER_NAME = "eija"


def _argv(python: str, workspace: Path) -> list[str]:
    return [python, "-m", "eija_studio", "mcp", "--workspace", str(workspace)]


def _toml(value: str) -> str:
    return json.dumps(value)  # a JSON string is a valid TOML basic string for paths/ascii text


def snippet(client: str, python: str, workspace: Path) -> str:
    """Return the config text for `client`. Raises ValueError for an unknown client."""
    argv = _argv(python, workspace.resolve())
    if client == "claude":
        # `--scope project` writes .mcp.json in the current project; drop it for a private local scope.
        return "claude mcp add --scope project " + SERVER_NAME + " -- " + " ".join(shlex.quote(a) for a in argv)
    if client == "codex":
        return "\n".join([f"[mcp_servers.{SERVER_NAME}]", f"command = {_toml(argv[0])}",
                          "args = [" + ", ".join(_toml(a) for a in argv[1:]) + "]",
                          "startup_timeout_sec = 30", "enabled = true"]) + "\n"
    if client == "opencode":
        return json.dumps({"$schema": "https://opencode.ai/config.json",
                           "mcp": {SERVER_NAME: {"type": "local", "command": argv, "enabled": True}}}, indent=2) + "\n"
    if client == "gemini":
        return json.dumps({"mcpServers": {SERVER_NAME: {"command": argv[0], "args": argv[1:], "timeout": 60000,
                                                        "trust": False}}}, indent=2) + "\n"
    raise ValueError(f"Unknown client {client!r}; choose one of {', '.join(CLIENTS)}")
