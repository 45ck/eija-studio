"""Gemini CLI adapter (headless ``-p`` with ``-o json``), after the CLI's own Google sign-in.

Gemini CLI has no official login-status command and no structured-output flag. So login is reported UNKNOWN
(never guessed from token files) and the live call decides; the schema is requested in the prompt and the
reply is validated here. Tools are switched off with an admin-tier deny-all policy file plus plan mode.
The deny-all policy is documented behaviour (policy-engine.md) but was NOT live-verified: the reference
machine had no Gemini sign-in.
"""
from __future__ import annotations
import subprocess
from pathlib import Path
from typing import Any
from ._common import first_key, json_object, safe_usage, unwrap_single_fence, with_accounting
from .cli_base import CliProposalProvider, Extracted, Invocation, LoginState, StatusRunner

DENY_ALL_POLICY = '[[rule]]\ntoolName = "*"\ndecision = "deny"\npriority = 999\ndenyMessage = "EIJA proposal calls run with all tools disabled"\n'
STDIN_INSTRUCTION = "Follow the instructions supplied on stdin. Reply with only the requested JSON object."
AUTH_EXIT_CODE = 41  # observed for gemini-cli 0.37 with no auth method configured


class GeminiCliProvider(CliProposalProvider):
    name, label, default_executable = "gemini", "Gemini CLI", "gemini"
    required_flags = ("--prompt", "--output-format", "--approval-mode", "--admin-policy", "--extensions")
    schema_in_prompt = True

    def login_state(self, status: StatusRunner) -> LoginState:
        return LoginState("UNKNOWN", "Gemini CLI has no official login-status command; a live call reports an auth error if not signed in")

    def invocation(self, work: Path) -> Invocation:
        policy_dir = work / "policy"
        policy_dir.mkdir()
        (policy_dir / "deny-all.toml").write_text(DENY_ALL_POLICY, encoding="utf-8", newline="\n")
        args = ["-p", STDIN_INSTRUCTION, "-o", "json", "--approval-mode", "plan", "--admin-policy", str(policy_dir), "-e", "none"]
        if self.model:
            args += ["-m", self.model]
        return Invocation(tuple(args))

    def classify_failure(self, result: subprocess.CompletedProcess) -> str:
        error = (json_object(result.stdout) or {}).get("error")
        if result.returncode == AUTH_EXIT_CODE or (isinstance(error, dict) and error.get("code") == AUTH_EXIT_CODE):
            return "PROVIDER_AUTH"
        return super().classify_failure(result)

    @staticmethod
    def _usage(stats: Any, model: str) -> dict[str, Any]:
        """Token counts for ``model`` from the CLI's ``stats.models`` block, allow-listed."""
        models = stats.get("models") if isinstance(stats, dict) else None
        entry = models.get(model) if isinstance(models, dict) else None
        tokens = entry.get("tokens") if isinstance(entry, dict) else None
        return with_accounting(safe_usage(tokens, frozenset({"input", "prompt", "candidates", "total"})),
                               "Subscription or free-tier usage; no USD inferred")

    def extract(self, result: subprocess.CompletedProcess, work: Path) -> Extracted:
        envelope = self.json_envelope(result)
        if "error" in envelope:  # the exit code may still be 0
            raise self.fail(self.classify_failure(result))
        response = envelope.get("response")
        if not isinstance(response, str):
            raise self.fail("PROVIDER_OUTPUT_INVALID")
        stats = envelope.get("stats")
        model = first_key(stats.get("models") if isinstance(stats, dict) else None)
        return Extracted(unwrap_single_fence(response), model or self.model, self._usage(stats, model))
