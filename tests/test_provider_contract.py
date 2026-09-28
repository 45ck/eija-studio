"""Shared contract for every agent-CLI proposal provider, run with a MOCKED process runner.

PASS here means the adapter's isolation, parsing and error handling hold against faked CLI output. It says
nothing about whether the real vendor CLI behaves this way: that is scripts/live_provider_smoke.py, recorded
separately in evidence/live-providers/.
"""
import importlib.util
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Callable

import pytest

from eija_studio.adapters.providers import (ClaudeCodeProvider, CodexProvider, GeminiCliProvider, OfflineProvider, OpenCodeProvider,
                                            create_provider, PROVIDER_NAMES)
from eija_studio.adapters.providers.process import CliTimeout
from eija_studio.domain.models import DomainError
from eija_studio.domain.policy import baseline

CANARY = "CANARY-REQUEST-7c1f"
SECRETS = {"OPENROUTER_API_KEY": "sk-or-never", "ANTHROPIC_API_KEY": "sk-ant-never", "GEMINI_API_KEY": "gem-never",
           "GOOGLE_API_KEY": "goog-never", "OPENAI_API_KEY": "sk-oa-never", "CODEX_API_KEY": "codex-never",
           "CLAUDE_CODE_OAUTH_TOKEN": "oauth-never", "GH_TOKEN": "ghp-never", "AWS_SECRET_ACCESS_KEY": "aws-never",
           "OPENCODE_SERVER_PASSWORD": "pw-never", "EIJA_STUDIO_TOKEN": "studio-never"}


def proposal_text() -> str:
    return OfflineProvider().propose("Let teachers sign off excursions.", baseline()).proposal.model_dump_json()


def envelope(**kw):
    return subprocess.CompletedProcess(["x"], kw.pop("rc", 0), kw.pop("out", ""), kw.pop("err", ""))


# --- per-vendor fakes: how each CLI reports a model reply --------------------------------------------------
def emit_codex(text: str, args: list[str]):
    Path(args[args.index("--output-last-message") + 1]).write_text(text, encoding="utf-8")
    return envelope()


def emit_claude(text: str, args: list[str]):
    try:
        parsed = json.loads(text)
    except ValueError:
        parsed = None
    body = {"type": "result", "subtype": "success", "is_error": False, "result": text, "modelUsage": {"claude-fixture-1": {}},
            "usage": {"input_tokens": 5, "output_tokens": 7, "secret_debug": "no"}, "total_cost_usd": 0.01}
    if isinstance(parsed, dict):
        body["structured_output"] = parsed
    return envelope(out=json.dumps(body))


def emit_opencode(text: str, args: list[str]):
    events = [{"type": "step_start"}, {"type": "text", "part": {"type": "text", "text": text}}, {"type": "step_finish"}]
    return envelope(out="\n".join(json.dumps(e) for e in events))


def emit_gemini(text: str, args: list[str]):
    return envelope(out=json.dumps({"session_id": "s", "response": text, "stats": {"models": {"gemini-fixture": {"tokens": {"total": 9}}}}}))


@dataclass(frozen=True)
class Spec:
    name: str
    make: Callable[..., object]
    help_text: str
    version_args: tuple
    help_args: tuple
    login_args: tuple | None
    logged_in: tuple  # (returncode, stdout)
    logged_out: tuple | None
    emit: Callable
    lockdown: tuple  # argv fragments that switch the CLI's tools off
    env_lockdown: tuple = ()  # env entries the adapter must pass


SPECS = [
    Spec("codex", CodexProvider, "--output-schema --ephemeral --ignore-user-config --sandbox --output-last-message --skip-git-repo-check",
         ("--version",), ("exec", "--help"), ("login", "status"), (0, "Logged in using ChatGPT"), (0, "Logged in using an API key"), emit_codex,
         (("--sandbox", "read-only"), ("--ignore-user-config",), ("--ephemeral",), ("-c", "features.shell_tool=false"), ("-c", 'web_search="disabled"'))),
    Spec("claude", ClaudeCodeProvider, "--json-schema --output-format --tools --safe-mode --no-session-persistence --permission-mode --permission-prompts --disable-slash-commands",
         ("--version",), ("--help",), ("auth", "status"), (0, json.dumps({"loggedIn": True, "authMethod": "claude.ai", "email": "x@y"})),
         (0, json.dumps({"loggedIn": True, "authMethod": "console"})), emit_claude,
         (("--tools", ""), ("--safe-mode",), ("--permission-mode", "dontAsk"), ("--permission-prompts", "none"), ("--no-session-persistence",))),
    Spec("opencode", OpenCodeProvider, "--format --pure --model", ("--version",), ("run", "--help"), ("auth", "list"),
         (0, "\x1b[90m Credentials\x1b[0m\n 2 credentials"), (0, "Credentials ~/auth.json\n 0 credentials"), emit_opencode,
         (("--pure",),), ("OPENCODE_CONFIG_CONTENT", "XDG_CONFIG_HOME")),
    Spec("gemini", GeminiCliProvider, "--prompt --output-format --approval-mode --admin-policy --extensions", ("--version",), ("--help",), None,
         (0, ""), None, emit_gemini, (("--approval-mode", "plan"), ("--admin-policy",), ("-e", "none"))),
]
IDS = [s.name for s in SPECS]


class Harness:
    """A mocked runner that records every call and answers by the argv it recognises."""

    def __init__(self, spec: Spec, reply: Callable | None = None, *, main_error: Exception | None = None, logged_out=False):
        self.spec, self.calls, self.mains = spec, [], []
        self.reply, self.main_error, self.logged_out = reply, main_error, logged_out
        self.cwd_listing: list[str] = []

    def __call__(self, args, *, input=None, env, timeout, cwd=None):
        rest = tuple(args[1:])
        self.calls.append({"args": list(args), "input": input, "env": dict(env), "timeout": timeout, "cwd": cwd})
        if rest == self.spec.version_args:
            return envelope(out="9.9.9-fixture")
        if rest == self.spec.help_args:
            return envelope(out=self.spec.help_text)
        if self.spec.login_args and rest == self.spec.login_args:
            rc, out = self.spec.logged_out if self.logged_out and self.spec.logged_out else self.spec.logged_in
            return envelope(rc=rc, out=out)
        self.mains.append(self.calls[-1])
        self.cwd_listing = sorted(os.listdir(cwd)) if cwd else []
        if self.main_error:
            raise self.main_error
        return self.reply(args)


def provider(spec: Spec, harness: Harness, **kw):
    return spec.make(runner=harness, **kw)


def ok(spec: Spec, text: str | None = None):
    return Harness(spec, lambda args: spec.emit(text if text is not None else proposal_text(), list(args)))


@pytest.fixture(autouse=True)
def secret_env(monkeypatch):
    for k, v in SECRETS.items():
        monkeypatch.setenv(k, v)


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_valid_output_becomes_a_proposal_result(spec):
    h = ok(spec)
    result = provider(spec, h).propose(CANARY, baseline())
    assert result.provider == spec.name and result.live and len(result.proposal.alternatives) == 3
    assert "secret_debug" not in result.usage  # only allow-listed numeric accounting survives
    assert len(h.mains) == 1


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
@pytest.mark.parametrize("text", ["not json {", "{}", '{"summary":"x","alternatives":[],"unknowns":[]}',
                                  '{"summary":"x","alternatives":[{"interpretation":"approve_everything","explanation":"y"}],"unknowns":[]}',
                                  proposal_text().replace("recommend_only", "final_authority", 1), "x" * 70000],
                         ids=["malformed_json", "empty_object", "schema_violation_no_alternatives", "wrong_interpretation_label",
                              "wrong_label_in_valid_shape", "oversized"])
def test_bad_model_output_fails_closed_without_repair(spec, text):
    with pytest.raises(DomainError) as e:
        provider(spec, ok(spec, text)).propose(CANARY, baseline())
    assert e.value.code == "PROVIDER_OUTPUT_INVALID"


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_nonzero_exit_is_sanitised_and_never_retried(spec):
    h = Harness(spec, lambda args: envelope(rc=1, err="boom sk-secret-diagnostic /home/user/.tokens"))
    with pytest.raises(DomainError) as e:
        provider(spec, h).propose(CANARY, baseline())
    assert e.value.code == "PROVIDER_PROCESS_FAILED"
    assert "sk-secret-diagnostic" not in str(e.value) and ".tokens" not in str(e.value)
    assert len(h.mains) == 1  # no retry and no fallback to another provider


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_auth_failure_is_classified_not_leaked(spec):
    h = Harness(spec, lambda args: envelope(rc=1, out="", err="Error: 401 Unauthorized: token abc123"))
    with pytest.raises(DomainError) as e:
        provider(spec, h).propose(CANARY, baseline())
    assert e.value.code == "PROVIDER_AUTH" and "abc123" not in str(e.value)


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_timeout_reports_and_does_not_retry(spec):
    h = Harness(spec, main_error=CliTimeout("partial output with secret"))
    p = provider(spec, h, timeout=7)
    with pytest.raises(DomainError) as e:
        p.propose(CANARY, baseline())
    assert e.value.code == "PROVIDER_TIMEOUT" and "secret" not in str(e.value)
    assert len(h.mains) == 1 and h.mains[0]["timeout"] == 7


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_environment_allow_list_excludes_every_secret(spec):
    h = ok(spec)
    provider(spec, h).propose(CANARY, baseline())
    assert h.calls, "no calls recorded"
    for call in h.calls:  # probes AND the main call
        assert not set(SECRETS) & {k.upper() for k in call["env"]}
        assert not set(SECRETS.values()) & set(call["env"].values())
        assert "PATH" in {k.upper() for k in call["env"]}


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_prompt_goes_on_stdin_never_argv(spec):
    h = ok(spec)
    provider(spec, h).propose(CANARY, baseline())
    main = h.mains[0]
    assert CANARY in main["input"] and "INPUT DATA" in main["input"]
    assert not any(CANARY in a for a in main["args"])
    assert all(c["input"] is None for c in h.calls if c is not main)  # probes carry no user data


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_tool_lockdown_flags_are_present(spec):
    h = ok(spec)
    provider(spec, h).propose(CANARY, baseline())
    main = h.mains[0]
    args = main["args"]
    for fragment in spec.lockdown:
        assert any(args[i:i + len(fragment)] == list(fragment) for i in range(len(args))), fragment
    for name in spec.env_lockdown:
        assert name in main["env"]
    for banned in ("--dangerously-bypass-approvals-and-sandbox", "--dangerously-skip-permissions", "--yolo", "-y", "bypassPermissions",
                   "--allow-dangerously-skip-permissions", "danger-full-access", "workspace-write"):
        assert banned not in args


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_runs_in_an_isolated_working_directory(spec):
    h = ok(spec)
    provider(spec, h).propose(CANARY, baseline())
    cwd = Path(h.mains[0]["cwd"])
    assert cwd.resolve() != Path.cwd().resolve() and cwd.name.startswith(f"eija-{spec.name}-")  # a fresh directory, not the checkout
    assert set(h.cwd_listing) <= {"proposal.schema.json", "policy", "xdg-config"}  # only files the adapter itself created
    assert not cwd.exists()  # removed afterwards


@pytest.mark.parametrize("spec", [s for s in SPECS if s.logged_out], ids=[s.name for s in SPECS if s.logged_out])
def test_logged_out_blocks_before_any_billable_call(spec):
    h = Harness(spec, lambda args: pytest.fail("must not run"), logged_out=True)
    p = provider(spec, h)
    assert p.doctor()["ready"] is False
    with pytest.raises(DomainError) as e:
        p.propose(CANARY, baseline())
    assert e.value.code == "PROVIDER_NOT_READY" and not h.mains


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_missing_required_flag_blocks_readiness(spec):
    h = ok(spec)
    h.spec = Spec(**{**spec.__dict__, "help_text": "no relevant flags"})
    report = provider(spec, h).doctor()
    assert report["ready"] is False and report["missing_flags"] and report["live_test"] == "NOT_RUN"


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_doctor_reports_version_and_login_without_identity(spec):
    report = provider(spec, ok(spec)).doctor()
    assert report["ready"] is True and report["cli_version"] == "9.9.9-fixture" and report["required_flags_present"]
    assert "x@y" not in json.dumps(report)  # account identifiers are not surfaced
    assert report["login"] in {"LOGGED_IN", "UNKNOWN"}


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_not_installed_is_reported_not_raised(spec):
    report = spec.make(executable="eija-definitely-not-installed").doctor()
    assert report["ready"] is False and "not installed" in report["reason"] and report["live_test"] == "NOT_RUN"


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_model_name_cannot_inject_a_flag(spec):
    with pytest.raises(DomainError) as e:
        spec.make(model="--dangerously-skip-permissions")
    assert e.value.code == "CONFIGURATION"
    h = ok(spec)
    spec.make(model="vendor/model-1.2", runner=h).propose(CANARY, baseline())
    args = h.mains[0]["args"]
    assert "vendor/model-1.2" in args and args[args.index("vendor/model-1.2") - 1] in {"--model", "-m"}


def test_gemini_fence_is_unwrapped_but_still_validated():
    spec = SPECS[3]
    fenced = "```json\n" + proposal_text() + "\n```"
    assert provider(spec, ok(spec, fenced)).propose(CANARY, baseline()).proposal.alternatives
    with pytest.raises(DomainError):
        provider(spec, ok(spec, "```json\n{}\n```")).propose(CANARY, baseline())


def test_claude_error_envelope_is_not_treated_as_success():
    spec = SPECS[1]
    bad = json.dumps({"type": "result", "subtype": "error_during_execution", "is_error": True, "api_error_status": 429, "result": "secret text"})
    with pytest.raises(DomainError) as e:
        provider(spec, Harness(spec, lambda args: envelope(out=bad))).propose(CANARY, baseline())
    assert e.value.code == "PROVIDER_RATE_LIMIT" and "secret text" not in str(e.value)


def test_opencode_error_event_with_exit_zero_is_a_failure():
    spec = SPECS[2]
    event = json.dumps({"type": "error", "error": {"name": "APIError", "data": {"statusCode": 401, "message": "User not found. token-xyz"}}})
    with pytest.raises(DomainError) as e:
        provider(spec, Harness(spec, lambda args: envelope(out=event))).propose(CANARY, baseline())
    assert e.value.code == "PROVIDER_AUTH" and "token-xyz" not in str(e.value)


def test_gemini_auth_envelope_maps_to_auth_error():
    spec = SPECS[3]
    body = json.dumps({"error": {"type": "Error", "message": "Please set an Auth method GEMINI_API_KEY", "code": 41}})
    with pytest.raises(DomainError) as e:
        provider(spec, Harness(spec, lambda args: envelope(rc=41, out=body))).propose(CANARY, baseline())
    assert e.value.code == "PROVIDER_AUTH"


def test_claude_does_not_use_bare_mode_that_would_ignore_the_subscription_login():
    h = ok(SPECS[1])
    provider(SPECS[1], h).propose(CANARY, baseline())
    assert "--bare" not in h.mains[0]["args"]


def test_registry_builds_every_named_provider_and_rejects_unknown():
    assert set(PROVIDER_NAMES) == {"offline", "openrouter", "anthropic", "codex", "claude", "opencode", "gemini"}
    for name in PROVIDER_NAMES:
        p = create_provider(name, "")
        assert p.name == name and isinstance(p.networked, bool)
    assert create_provider("offline").networked is False
    with pytest.raises(ValueError):
        create_provider("nope")


def _smoke_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "live_provider_smoke.py"
    spec = importlib.util.spec_from_file_location("live_provider_smoke", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_live_smoke_refuses_without_consent_and_makes_no_call(tmp_path, monkeypatch):
    module = _smoke_module()
    monkeypatch.setattr(module, "run_smoke", lambda *a, **k: pytest.fail("a live call was attempted without consent"))
    out = tmp_path / "evidence.json"
    assert module.main(["--provider", "claude", "--out", str(out)]) == 2
    assert not out.exists()
    assert module.main(["--provider", "claude", "--consent", "--timeout", "999", "--out", str(out)]) == 2


def test_live_smoke_records_not_run_when_the_cli_is_signed_out(tmp_path, monkeypatch):
    module = _smoke_module()
    class SignedOut:
        timeout = 1
        def doctor(self): return {"ready": False, "login": "NOT_LOGGED_IN", "login_detail": "0 stored credentials"}
        def propose(self, *a): pytest.fail("must not call a signed-out CLI")
    monkeypatch.setattr(module, "create_provider", lambda name, model: SignedOut())
    out = tmp_path / "evidence.json"
    assert module.main(["--provider", "opencode", "--consent", "--out", str(out)]) == 0
    record = json.loads(out.read_text(encoding="utf-8"))["results"]["opencode"]
    assert record["status"] == "NOT_RUN" and "credentials" in record["reason"]
