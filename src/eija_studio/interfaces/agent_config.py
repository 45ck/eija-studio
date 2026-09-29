"""Copy-paste MCP client configuration for `eija mcp --print-config <client>`.

Pure text generation: no MCP SDK import, so it works before the `agents` extra is installed. Each
snippet follows the client's documented syntax (sources are listed in docs/agents/quickstart.md).
It does NOT install or verify anything in the client; the owner pastes it.
"""
from __future__ import annotations

import json
import re
import shlex
import sys
from pathlib import Path

from eija_studio.domain.models import DomainError

CLIENTS: tuple[str, ...] = ("claude", "codex", "opencode", "gemini")
SERVER_NAME = "eija"
#: Live (networked) provider calls one `eija mcp` session may make; SDK-free so the CLI can read it without the extra.
DEFAULT_MAX_PROVIDER_CALLS = 3


def _argv(python: str, workspace: Path) -> list[str]:
    return [python, "-m", "eija_studio", "mcp", "--workspace", str(workspace)]


def _toml(value: str) -> str:
    """A TOML basic string. JSON escapes are valid TOML, except ensure_ascii's surrogate pairs (non-BMP text) and a raw DEL."""
    return json.dumps(value, ensure_ascii=False).replace(chr(0x7F), "\\u007f")


#: Characters that still expand, or end the quote, inside double quotes in PowerShell (`$`, backtick, `"`) or cmd.exe (`%`).
_WINDOWS_UNSAFE = frozenset('$`"%')


def _shell_join(argv: list[str], windows: bool) -> str:
    """Quote for the pasting shell: POSIX single quotes (shlex), or on Windows double quotes around EVERY argument.

    Double quotes keep `&`, `;`, `|`, `<`, `>` and `^` literal in both cmd.exe and PowerShell (`subprocess.list2cmdline`
    quotes only arguments with whitespace, so a path like C:/R&D split at the ampersand). What double quotes cannot protect
    (`$`, a backtick, `%`, an embedded `"`) is refused, not guessed at: use a JSON/TOML client form instead."""
    if not windows:
        return " ".join(shlex.quote(a) for a in argv)
    for arg in argv:
        if _WINDOWS_UNSAFE & set(arg):
            raise DomainError("CONFIGURATION", f"{arg!r} contains a character (one of $ ` \" %) that PowerShell or cmd.exe would still "
                                               "expand inside quotes, so no safe one-line command can be printed; use a path without it, "
                                               "or print the codex, opencode or gemini configuration form instead")
    return " ".join('"' + re.sub(r"(\\+)$", r"\1\1", arg) + '"' for arg in argv)  # a trailing backslash must not escape the closing quote


def snippet(client: str, python: str, workspace: Path, *, windows: bool | None = None) -> str:
    """Return the config text for `client`. Raises ValueError for an unknown client.

    `windows` picks the shell quoting of the Claude one-liner (default: this platform). It establishes only
    that the text is well formed for that shell; it does not install or check anything in the client.
    """
    argv = _argv(python, workspace.resolve())
    if client == "claude":
        # `--scope project` writes .mcp.json in the current project; drop it for a private local scope.
        return ("claude mcp add --scope project " + SERVER_NAME + " -- "
                + _shell_join(argv, sys.platform == "win32" if windows is None else windows) + "\n")
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
