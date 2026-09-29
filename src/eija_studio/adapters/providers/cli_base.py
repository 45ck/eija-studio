"""One base class owns subprocess isolation for every agent-CLI proposal provider.

Established here, for all CLIs alike: an empty temporary working directory, an environment allow-list that
never forwards API keys or tokens, the prompt on STDIN (never argv), bounded output, a deadline with
process-tree kill, no automatic retry or fallback, and sanitised errors (raw CLI output is never returned).
NOT established here: that a CLI honours its own tool-disabling flags. Each adapter names those flags, the
contract tests assert they are present, and the live smoke report says whether a real call worked.

Authentication is always delegated to the vendor CLI's own login. EIJA never reads a token file.
"""
from __future__ import annotations
import os
import re
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping
import subprocess
from eija_studio.domain.models import Workflow, DomainError
from eija_studio.application.ports import ProviderResult
from ._common import MAX_ENVELOPE_BYTES, build_prompt, json_object, parse_proposal, validate_model_name
from .process import CliOutputLimit, CliShimUnsupported, CliTimeout, Runner, resolve_command, run_bounded

BASE_ENV_ALLOW = frozenset({
    "PATH", "PATHEXT", "COMSPEC", "SYSTEMROOT", "SYSTEMDRIVE", "WINDIR", "HOME", "HOMEDRIVE", "HOMEPATH", "USERPROFILE",
    "USERNAME", "USER", "LOGNAME", "APPDATA", "LOCALAPPDATA", "PROGRAMDATA", "PROGRAMFILES", "PROGRAMFILES(X86)", "PROGRAMW6432",
    "TEMP", "TMP", "TMPDIR", "LANG", "LC_ALL", "TZ", "TERM", "OS", "PROCESSOR_ARCHITECTURE", "NUMBER_OF_PROCESSORS",
    "XDG_RUNTIME_DIR", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME", "DBUS_SESSION_BUS_ADDRESS",
})
# Belt and braces: even if an adapter allow-lists a name, a secret-looking name is never forwarded.
SECRET_NAME = re.compile(r"KEY|TOKEN|SECRET|PASSW|CREDENTIAL|AUTH|COOKIE|SESSION_ID", re.IGNORECASE)
PROBE_TIMEOUT = 20.0
_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
# Deliberately narrow: a bare "log in" or "401" also appears in file names, prose and line numbers.
_AUTH = re.compile(r"not logged in|please log ?in|/login\b|unauthori[sz]ed|(?:http|status|error|code)[ :=]*40[13]\b|\b40[13] forbidden"
                   r"|authenticat(?:ion|e) (?:failed|required|error)|invalid api key|api key (?:is )?(?:missing|invalid|not set)"
                   r"|credentials? (?:are |is )?(?:missing|invalid|expired|not found)|auth method")
_RATE_LIMIT = re.compile(r"rate.?limit|(?:http|status|error|code)[ :=]*429\b|\b429 too many|quota|usage limit|overloaded|resource.?exhausted")
PREFLIGHT_TTL = 60.0  # seconds a READY result is reused by propose(); `eija doctor` itself is never cached

MESSAGES = {
    "PROVIDER_NOT_READY": "{label} is not ready: run eija doctor and sign in with the vendor CLI (no key is read or forwarded)",
    "PROVIDER_TIMEOUT": "{label} timed out and its process tree was killed; no automatic retry. Account usage may still have occurred",
    "PROVIDER_AUTH": "{label} reported an authentication problem; sign in again with the vendor CLI. No raw diagnostics are exposed",
    "PROVIDER_RATE_LIMIT": "{label} reported a rate or usage limit; no automatic retry or fallback",
    "PROVIDER_PROCESS_FAILED": "{label} failed; inspect the vendor CLI locally. No raw diagnostics are exposed",
    "PROVIDER_OUTPUT_INVALID": "{label} did not produce a bounded, valid proposal envelope",
}


StatusRunner = Callable[[tuple[str, ...]], subprocess.CompletedProcess]


@dataclass(frozen=True)
class Invocation:
    """What an adapter wants run. ``args`` follow the executable and never contain the request text."""
    args: tuple[str, ...]
    env: Mapping[str, str] = field(default_factory=dict)  # trusted constants only, never user text or secrets


@dataclass(frozen=True)
class Extracted:
    text: str
    model: str = ""
    usage: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LoginState:
    """``UNKNOWN`` means the CLI has no official status command; only ``NOT_LOGGED_IN`` blocks a call."""
    state: str  # LOGGED_IN | NOT_LOGGED_IN | UNKNOWN
    detail: str = ""


def build_environment(source: Mapping[str, str], allowed: frozenset[str], extra: Mapping[str, str] | None = None) -> dict[str, str]:
    """Allow-list the child environment. Pure function so tests can prove secrets never pass."""
    env = {k: v for k, v in source.items() if k.upper() in allowed and not SECRET_NAME.search(k)}
    env.update(extra or {})
    return env


def strip_ansi(text: str) -> str:
    return _ANSI.sub("", text)


def has_flag(help_text: str, flag: str) -> bool:
    """Whole-token match, so ``--tools`` is not satisfied by ``--tools-foo``. Says the flag is documented, not honoured."""
    return re.search(rf"(?<![\w-]){re.escape(flag)}(?![\w-])", help_text) is not None


class CliProposalProvider:
    """Template for a vendor CLI adapter. Subclasses set the class attributes and override four hooks."""

    name: str = ""
    label: str = ""
    default_executable: str = ""
    networked = True
    extra_env: frozenset[str] = frozenset()
    help_args: tuple[str, ...] = ("--help",)
    version_args: tuple[str, ...] = ("--version",)
    required_flags: tuple[str, ...] = ()
    schema_in_prompt = False  # True for CLIs with no structured-output flag

    def __init__(self, model: str = "", executable: str | None = None, *, runner: Runner | None = None, timeout: float = 120) -> None:
        self.model = validate_model_name(model)
        self.executable = executable or self.default_executable
        self.runner, self.timeout = runner, timeout
        self._ready_at: float | None = None

    # ---- hooks -----------------------------------------------------------------------------------
    def login_state(self, status: StatusRunner) -> LoginState:
        """Interpret the vendor's OFFICIAL status command (run via ``status``). Never open token files."""
        raise NotImplementedError

    def invocation(self, work: Path) -> Invocation:
        raise NotImplementedError

    def extract(self, result: subprocess.CompletedProcess, work: Path) -> Extracted:
        raise NotImplementedError

    def stdout_within_cap(self, result: subprocess.CompletedProcess) -> str:
        """The CLI's stdout, or PROVIDER_OUTPUT_INVALID when it exceeds the envelope cap."""
        if len(result.stdout.encode("utf-8")) > MAX_ENVELOPE_BYTES:
            raise self.fail("PROVIDER_OUTPUT_INVALID")
        return str(result.stdout)

    def json_envelope(self, result: subprocess.CompletedProcess) -> dict[str, Any]:
        """stdout as exactly one bounded JSON object, or PROVIDER_OUTPUT_INVALID."""
        envelope = json_object(self.stdout_within_cap(result))
        if envelope is None:
            raise self.fail("PROVIDER_OUTPUT_INVALID")
        return envelope

    def classify_failure(self, result: subprocess.CompletedProcess) -> str:
        """Map a failed run to a stable code from its output. The output itself is never returned."""
        text = strip_ansi(f"{result.stdout}\n{result.stderr}").lower()
        # Rate limits first: "usage limit reached, please log in to upgrade" is a limit, not a sign-in problem.
        if _RATE_LIMIT.search(text):
            return "PROVIDER_RATE_LIMIT"
        if _AUTH.search(text):
            return "PROVIDER_AUTH"
        return "PROVIDER_PROCESS_FAILED"

    # ---- plumbing --------------------------------------------------------------------------------
    def fail(self, code: str) -> DomainError:
        return DomainError(code, MESSAGES[code].format(label=self.label))

    def environment(self, extra: Mapping[str, str] | None = None) -> dict[str, str]:
        return build_environment(os.environ, BASE_ENV_ALLOW | self.extra_env, extra)

    def _prefix(self) -> list[str]:
        # An injected runner is a test double: no resolution, argv[0] is the bare configured name.
        return [self.executable] if self.runner else resolve_command(self.executable)

    def _run(self, args: list[str], *, input: str | None, timeout: float, cwd: str | None, extra_env: Mapping[str, str] | None = None):
        runner = self.runner or run_bounded
        return runner(args, input=input, env=self.environment(extra_env), timeout=timeout, cwd=cwd)

    def _probe(self, prefix: list[str], args: tuple[str, ...], cwd: str) -> subprocess.CompletedProcess:
        return self._run([*prefix, *args], input=None, timeout=PROBE_TIMEOUT, cwd=cwd)

    # ---- doctor ----------------------------------------------------------------------------------
    def doctor(self) -> dict:
        """Report installed / version / required flags / login using the vendor's official commands only.

        Never reads auth or token files and never makes a model call. ``live_test`` stays NOT_RUN: only
        scripts/live_provider_smoke.py with explicit consent can change that, and it records its own evidence.
        """
        report: dict[str, Any] = {"provider": self.name, "ready": False, "live_test": "NOT_RUN"}
        try:
            prefix = self._prefix()
        except FileNotFoundError:
            return report | {"reason": f"{self.label} CLI not installed"}
        except CliShimUnsupported:
            return report | {"reason": f"{self.label} launcher cannot be run without cmd.exe; refused (argument-injection risk)"}
        try:
            version, missing, login = self._diagnose(prefix)
        except (CliTimeout, CliOutputLimit):
            return report | {"reason": f"{self.label} diagnostic timed out or was too large"}
        except OSError:
            return report | {"reason": f"{self.label} diagnostic failed"}
        return report | self._readiness(version, missing, login)

    def _diagnose(self, prefix: list[str]) -> tuple[subprocess.CompletedProcess, list[str], LoginState]:
        """Run the three local probes (version, help, login status) in a throwaway directory."""
        with tempfile.TemporaryDirectory(prefix=f"eija-{self.name}-doctor-") as probe_dir:
            version = self._probe(prefix, self.version_args, probe_dir)
            helped = self._probe(prefix, self.help_args, probe_dir)
            help_text = strip_ansi(f"{helped.stdout}\n{helped.stderr}")  # some CLIs print help on stderr
            missing = [flag for flag in self.required_flags if not has_flag(help_text, flag)]
            login = self.login_state(lambda args: self._probe(prefix, args, probe_dir))
        return version, missing, login

    @staticmethod
    def _readiness(version: subprocess.CompletedProcess, missing: list[str], login: LoginState) -> dict[str, Any]:
        first_line = (strip_ansi(version.stdout).strip().splitlines() or [""])[0][:80]
        ready = not missing and login.state != "NOT_LOGGED_IN"
        # ``ready`` means "a call may be attempted". Only ``login_verified`` says the vendor CLI confirmed a login.
        status = "NOT_RUN" if not ready else "READY" if login.state == "LOGGED_IN" else "READY_LOGIN_UNVERIFIED"
        return {"ready": ready, "status": status, "login_verified": login.state == "LOGGED_IN",
                "cli_version": first_line if version.returncode == 0 else "", "required_flags_present": not missing,
                "missing_flags": missing, "login": login.state, "login_detail": login.detail}

    def _preflight_ready(self) -> bool:
        """Run doctor() before a call, reusing a READY result for PREFLIGHT_TTL seconds (each doctor is several processes)."""
        now = time.monotonic()
        if self._ready_at is not None and now - self._ready_at < PREFLIGHT_TTL:
            return True
        ready = bool(self.doctor()["ready"])
        self._ready_at = now if ready else None
        return ready

    # ---- propose ---------------------------------------------------------------------------------
    def propose(self, request: str, model: Workflow) -> ProviderResult:
        """One synthetic-safe call. Establishes a schema-valid Proposal or a sanitised DomainError.

        Does not establish that the interpretation is correct, and never retries or falls back.
        """
        if not self._preflight_ready():
            raise self.fail("PROVIDER_NOT_READY")
        try:
            prefix = self._prefix()
        except (FileNotFoundError, CliShimUnsupported):
            raise self.fail("PROVIDER_NOT_READY") from None
        prompt = build_prompt(request, model, schema_in_prompt=self.schema_in_prompt)
        with tempfile.TemporaryDirectory(prefix=f"eija-{self.name}-") as directory:
            work = Path(directory)
            call = self.invocation(work)
            try:
                result = self._run([*prefix, *call.args], input=prompt, timeout=self.timeout, cwd=directory, extra_env=call.env)
            except CliTimeout:
                raise self.fail("PROVIDER_TIMEOUT") from None
            except CliOutputLimit:
                raise self.fail("PROVIDER_OUTPUT_INVALID") from None
            except OSError:
                raise self.fail("PROVIDER_PROCESS_FAILED") from None
            if result.returncode != 0:
                raise self.fail(self.classify_failure(result))
            extracted = self.extract(result, work)
        return ProviderResult(parse_proposal(extracted.text, model), self.name, extracted.model or "unreported",
                              dict(extracted.usage), True)
