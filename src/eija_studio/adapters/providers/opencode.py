"""OpenCode CLI adapter (``opencode run --format json``), after ``opencode auth login``.

OpenCode has no structured-output flag and no tools-off flag, so: the schema is requested in the prompt and the
reply is validated here; tools are denied through inline config (``OPENCODE_CONFIG_CONTENT``); the user's
config directory is swapped for an empty one (XDG_CONFIG_HOME) so their plugins, instructions and MCP servers
are not loaded, while credentials (a separate data directory) keep working.

The deny-all permission config and the success event shape (``text`` events) are NOT live-verified: the
reference machine had no OpenCode credentials. Only the error-event shape was observed.
"""
from __future__ import annotations
import json
import re
import subprocess
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from ._common import json_object, status_failure_code, unwrap_single_fence
from .cli_base import CliProposalProvider, Extracted, Invocation, LoginState, StatusRunner, strip_ansi

DENY_ALL_CONFIG = json.dumps({"permission": {"*": "deny"}, "share": "disabled", "autoupdate": False}, sort_keys=True)


class OpenCodeProvider(CliProposalProvider):
    name, label, default_executable = "opencode", "OpenCode", "opencode"
    help_args = ("run", "--help")
    required_flags = ("--format", "--pure", "--model")
    schema_in_prompt = True

    def login_state(self, status: StatusRunner) -> LoginState:
        text = strip_ansi(status(("auth", "list")).stdout)
        match = re.search(r"(\d+)\s+credentials?", text)
        if not match:
            return LoginState("UNKNOWN", "opencode auth list output not recognised")
        count = int(match.group(1))
        if count == 0:
            return LoginState("NOT_LOGGED_IN", "0 stored credentials; run opencode auth login")
        return LoginState("LOGGED_IN", f"{count} stored credential(s)")

    def invocation(self, work: Path) -> Invocation:
        config_home = work / "xdg-config"
        config_home.mkdir()
        args = ["run", "--format", "json", "--pure"]
        if self.model:
            args += ["--model", self.model]
        env = {"XDG_CONFIG_HOME": str(config_home), "OPENCODE_CONFIG_CONTENT": DENY_ALL_CONFIG,
               "OPENCODE_DISABLE_PROJECT_CONFIG": "1", "OPENCODE_DISABLE_AUTOUPDATE": "1"}
        return Invocation(tuple(args), env)

    @staticmethod
    def _events(stdout: str) -> Iterator[dict[str, Any]]:
        """JSON-lines events; lines that are not one JSON object are skipped."""
        for line in stdout.splitlines():
            event = json_object(line)
            if event is not None:
                yield event

    @staticmethod
    def _error_status(event: dict[str, Any]) -> Any:
        error = event.get("error")
        data = error.get("data") if isinstance(error, dict) else None
        return data.get("statusCode") if isinstance(data, dict) else None

    @staticmethod
    def _text_of(event: dict[str, Any]) -> str | None:
        part = event.get("part")
        if event.get("type") == "text" and isinstance(part, dict) and isinstance(part.get("text"), str):
            return str(part["text"])
        return None

    def extract(self, result: subprocess.CompletedProcess, work: Path) -> Extracted:
        parts: list[str] = []
        for event in self._events(self.stdout_within_cap(result)):
            if event.get("type") == "error":
                # OpenCode exits 0 on API errors; the error event is the only signal.
                raise self.fail(status_failure_code(self._error_status(event)))
            text = self._text_of(event)
            if text is not None:
                parts.append(text)
        if not parts:
            raise self.fail("PROVIDER_OUTPUT_INVALID")
        return Extracted(unwrap_single_fence("".join(parts)), self.model or "opencode-default", {"accounting": "Not reported by this adapter"})
