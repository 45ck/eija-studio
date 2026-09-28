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
from pathlib import Path
from ._common import MAX_ENVELOPE_BYTES, unwrap_single_fence
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

    def extract(self, result: subprocess.CompletedProcess, work: Path) -> Extracted:
        if len(result.stdout.encode("utf-8")) > MAX_ENVELOPE_BYTES:
            raise self.fail("PROVIDER_OUTPUT_INVALID")
        parts: list[str] = []
        for line in result.stdout.splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if not isinstance(event, dict):
                continue
            if event.get("type") == "error":
                # OpenCode exits 0 on API errors; the error event is the only signal.
                error = event.get("error")
                data = error.get("data") if isinstance(error, dict) else None
                status = data.get("statusCode") if isinstance(data, dict) else None
                raise self.fail("PROVIDER_AUTH" if status in (401, 403) else "PROVIDER_RATE_LIMIT" if status == 429 else "PROVIDER_PROCESS_FAILED")
            part = event.get("part")
            if event.get("type") == "text" and isinstance(part, dict) and isinstance(part.get("text"), str):
                parts.append(part["text"])
        if not parts:
            raise self.fail("PROVIDER_OUTPUT_INVALID")
        return Extracted(unwrap_single_fence("".join(parts)), self.model or "opencode-default", {"accounting": "Not reported by this adapter"})
