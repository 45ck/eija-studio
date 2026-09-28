"""Codex CLI adapter (ChatGPT sign-in only). API-key logins are never silently substituted."""
from __future__ import annotations
import json
import subprocess
from pathlib import Path
from ._common import MAX_OUTPUT_BYTES, proposal_schema
from .cli_base import CliProposalProvider, Extracted, Invocation, LoginState, StatusRunner


class CodexProvider(CliProposalProvider):
    name, label, default_executable = "codex", "Codex", "codex"
    help_args = ("exec", "--help")
    required_flags = ("--output-schema", "--ephemeral", "--ignore-user-config", "--sandbox", "--output-last-message", "--skip-git-repo-check",
                      "--ignore-rules", "--cd")
    extra_env = frozenset({"CODEX_HOME"})  # a directory path; auth still lives in the CLI's own login

    def login_state(self, status: StatusRunner) -> LoginState:
        result = status(("login", "status"))
        text = (result.stdout + result.stderr).lower()
        if result.returncode == 0 and "chatgpt" in text:
            return LoginState("LOGGED_IN", "ChatGPT sign-in detected")
        return LoginState("NOT_LOGGED_IN", "ChatGPT sign-in not detected (an API-key login is deliberately not used)")

    def invocation(self, work: Path) -> Invocation:
        schema = work / "proposal.schema.json"
        schema.write_text(json.dumps(proposal_schema()), encoding="utf-8")
        args = ["exec", "--ignore-user-config", "--ignore-rules", "--ephemeral", "--sandbox", "read-only", "--skip-git-repo-check",
                "--cd", str(work), "--output-schema", str(schema), "--output-last-message", str(work / "proposal.json"), "--color", "never",
                "-c", 'forced_login_method="chatgpt"', "-c", 'approval_policy="never"', "-c", 'web_search="disabled"',
                "-c", "features.shell_tool=false", "-c", "features.unified_exec=false", "-c", "features.apps=false",
                "-c", "features.skill_mcp_dependency_install=false", "-c", 'history.persistence="none"']
        if self.model:
            args += ["--model", self.model]
        return Invocation((*args, "-"))

    def extract(self, result: subprocess.CompletedProcess, work: Path) -> Extracted:
        output = work / "proposal.json"
        if not output.is_file() or output.is_symlink() or output.stat().st_size > MAX_OUTPUT_BYTES:
            raise self.fail("PROVIDER_OUTPUT_INVALID")
        try:
            text = output.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            raise self.fail("PROVIDER_OUTPUT_INVALID") from None
        return Extracted(text, "",  # the CLI does not report which model ran; a requested --model is not evidence of it
                         {"accounting": "Check Codex; this adapter does not infer USD cost from subscription usage"})
