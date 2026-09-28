"""Claude Code CLI adapter using the user's subscription login (``claude auth login``).

``--bare`` is deliberately NOT used: it never reads OAuth/keychain, so it would silently require an API key.
Isolation instead comes from ``--safe-mode`` (no CLAUDE.md, hooks, skills, plugins or MCP from the user's
account) plus ``--tools ""`` (no built-in tools) and denial of anything that would prompt.
"""
from __future__ import annotations
import json
import subprocess
from pathlib import Path
from ._common import MAX_ENVELOPE_BYTES, compact_schema_json, safe_usage
from .cli_base import CliProposalProvider, Extracted, Invocation, LoginState, StatusRunner

TOKEN_FIELDS = frozenset({"input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"})


class ClaudeCodeProvider(CliProposalProvider):
    name, label, default_executable = "claude", "Claude Code", "claude"
    required_flags = ("--json-schema", "--output-format", "--tools", "--safe-mode", "--no-session-persistence",
                      "--permission-mode", "--permission-prompts", "--disable-slash-commands")
    # CLAUDE_CONFIG_DIR / git-bash path are locations, not secrets. ANTHROPIC_API_KEY and
    # CLAUDE_CODE_OAUTH_TOKEN are never forwarded: this provider is the subscription-login path.
    extra_env = frozenset({"CLAUDE_CONFIG_DIR", "CLAUDE_CODE_GIT_BASH_PATH"})

    def login_state(self, status: StatusRunner) -> LoginState:
        result = status(("auth", "status"))
        try:
            data = json.loads(result.stdout)
        except ValueError:
            data = None
        if result.returncode != 0 or not isinstance(data, dict):
            return LoginState("NOT_LOGGED_IN", "claude auth status did not report a login")
        if data.get("loggedIn") is True and data.get("authMethod") == "claude.ai":
            return LoginState("LOGGED_IN", f"claude.ai subscription login ({data.get('subscriptionType', 'plan unknown')})")
        return LoginState("NOT_LOGGED_IN", "Not a claude.ai subscription login (use the Anthropic API provider for API keys)")

    def invocation(self, work: Path) -> Invocation:
        args = ["-p", "--output-format", "json", "--json-schema", compact_schema_json(), "--tools", "", "--safe-mode",
                "--no-session-persistence", "--permission-mode", "dontAsk", "--permission-prompts", "none", "--disable-slash-commands"]
        if self.model:
            args += ["--model", self.model]
        return Invocation(tuple(args))

    def extract(self, result: subprocess.CompletedProcess, work: Path) -> Extracted:
        if len(result.stdout.encode("utf-8")) > MAX_ENVELOPE_BYTES:
            raise self.fail("PROVIDER_OUTPUT_INVALID")
        try:
            envelope = json.loads(result.stdout)
        except ValueError:
            raise self.fail("PROVIDER_OUTPUT_INVALID") from None
        if not isinstance(envelope, dict):
            raise self.fail("PROVIDER_OUTPUT_INVALID")
        if envelope.get("is_error") or envelope.get("subtype") != "success":
            status = envelope.get("api_error_status")
            raise self.fail("PROVIDER_AUTH" if status in (401, 403) else "PROVIDER_RATE_LIMIT" if status == 429 else "PROVIDER_PROCESS_FAILED")
        structured = envelope.get("structured_output")
        text = json.dumps(structured) if isinstance(structured, dict) else envelope.get("result")
        models = envelope.get("modelUsage")
        model = sorted(models)[0] if isinstance(models, dict) and models else ""
        usage = safe_usage(envelope.get("usage"), TOKEN_FIELDS) | safe_usage(envelope, frozenset({"total_cost_usd"}))
        usage["accounting"] = "Subscription usage; total_cost_usd is a list-price estimate from the CLI, not an invoice"
        return Extracted(text if isinstance(text, str) else "", model, usage)
