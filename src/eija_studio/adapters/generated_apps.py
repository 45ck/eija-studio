"""Retain exact selected app bytes and run their existing generated unittest checker locally."""
from __future__ import annotations

import os
import platform
import re
import subprocess
import sys
from contextlib import suppress
from importlib.resources import files as resource_files
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from eija_studio.application.ports import GeneratedSnapshot, GeneratedSubjectValidator, IdentityProvider
from eija_studio.domain.generated_app import GeneratedAppBinding
from eija_studio.domain.models import DomainError, Workflow, fingerprint
from eija_studio.domain.pack import Pack

ARGUMENTS = ("-I", "-B", "-m", "unittest", "discover", "-s", "tests", "-t", ".")
TIMEOUT_SECONDS = 600


def _snapshot(pack: Pack, model: Workflow, identity_provider: IdentityProvider,
              templates: dict[str, str], assemble: GeneratedSnapshot) -> tuple[dict[str, str], dict, GeneratedAppBinding]:
    identity = identity_provider()
    root = resource_files("eija_studio.resources").joinpath("appgen")
    static = {target: root.joinpath(source).read_text(encoding="utf-8") for source, target in templates.items()}
    configuration = {"runner": "python-unittest-discover", "arguments": list(ARGUMENTS),
                     "timeout_seconds": TIMEOUT_SECONDS, "python_version": platform.python_version(),
                     "platform": sys.platform, "environment_digest": identity["environment"],
                     "runner_environment_digest": fingerprint(_environment()),
                     "isolation": "isolated-python-fresh-bytecode-v1"}
    files, manifest, binding = assemble(pack, model, static, identity, configuration)
    if identity_provider() != identity:
        raise DomainError("APP_BUILD_CHANGED", "Implementation or checker environment changed during capture")
    return files, manifest, binding


class GeneratedApps:
    """The private artifact directory is content-addressed; an existing payload is never silently repaired."""

    def __init__(self, workspace: Path, *, templates: dict[str, str], subject_file: str,
                 assemble: GeneratedSnapshot, validate: GeneratedSubjectValidator):
        self.root = workspace / "generated-reviews"
        self.templates, self.subject_file = dict(templates), subject_file
        self.assemble, self.validate = assemble, validate

    def capture(self, pack: Pack, model: Workflow, expected_digest: str,
                identity_provider: IdentityProvider) -> GeneratedAppBinding:
        files, _, binding = _snapshot(pack, model, identity_provider, self.templates, self.assemble)
        if binding.subject.digest != expected_digest:
            raise DomainError("APP_BUILD_CHANGED", "The generated app differs from the inspected build; rebuild and inspect again")
        out = self.root / binding.digest
        if not out.exists():
            self.root.mkdir(parents=True, exist_ok=True)
            with TemporaryDirectory(prefix="capture-", dir=self.root, ignore_cleanup_errors=True) as temporary:
                staged = Path(temporary) / "payload"
                staged.mkdir()
                for relative, content in files.items():
                    path = staged / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(content.encode("utf-8"))
                # A concurrent complete capture is acceptable only after the same check below.
                with suppress(FileExistsError):
                    staged.rename(out)
        self._check_payload(binding, identity_provider)
        return binding

    def _check_payload(self, binding: GeneratedAppBinding, identity_provider: IdentityProvider) -> None:
        out = self.root / binding.digest
        expected = {*binding.subject.payload_paths, self.subject_file}
        found = {p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file()
                 and "__pycache__" not in p.relative_to(out).parts}
        if out.is_symlink() or found != expected or any(p.is_symlink() for p in out.rglob("*")):
            raise DomainError("APP_BUILD_CHANGED", "The retained generated app has missing, added or linked files")
        try:
            files = {name: (out / name).read_bytes().decode("utf-8") for name in expected}
        except (OSError, UnicodeError) as error:
            raise DomainError("APP_BUILD_CHANGED", "The retained generated app cannot be read") from error
        self.validate(files, identity_provider()["implementation"], binding)

    def current(self, pack: Pack, model: Workflow, binding: GeneratedAppBinding,
                identity_provider: IdentityProvider) -> dict[str, Any]:
        try:
            _, manifest, measured = _snapshot(pack, model, identity_provider, self.templates, self.assemble)
            if measured != binding:
                return {"freshness": "STALE", "detail": "The model, contracts, generator or checker configuration changed"}
            self._check_payload(binding, identity_provider)
        except (DomainError, OSError, ValueError) as error:
            return {"freshness": "STALE", "detail": str(error)}
        return {"freshness": "CURRENT", "cases": manifest["oracle"]["cases"],
                "detail": "Selected generated bytes and current generator/checker identity match"}

    def verify(self, binding: GeneratedAppBinding, identity_provider: IdentityProvider) -> dict[str, Any]:
        self._check_payload(binding, identity_provider)
        artifact = {"binding_digest": binding.digest, "subject_digest": binding.subject.digest,
                    "checker": binding.checker.model_dump(mode="json"),
                    "configuration": binding.configuration.model_dump(mode="json"),
                    "before": binding.subject.digest}
        with TemporaryDirectory(prefix="checker-cache-", dir=self.root, ignore_cleanup_errors=True) as cache:
            observation = _run(self.root / binding.digest, Path(cache))
        self._check_payload(binding, identity_provider)
        return artifact | observation | {"after": binding.subject.digest}


def _environment() -> dict[str, str]:
    """Only OS bootstrap variables; no provider credentials, path overrides or Python startup settings."""
    return {key: value for key, value in os.environ.items() if key.upper() in {"SYSTEMROOT", "WINDIR"}}


def _run(out: Path, cache: Path) -> dict[str, Any]:
    env = _environment()
    try:
        run = subprocess.run(  # noqa: S603 - fixed checker argv and server-owned fresh cache; no shell or user command
            [sys.executable, "-X", f"pycache_prefix={cache}", *ARGUMENTS], cwd=out, env=env, capture_output=True,
                             text=True, timeout=TIMEOUT_SECONDS, check=False)
    except subprocess.TimeoutExpired:
        return {"returncode": None, "timed_out": True, "tests_run": 0, "stdout": "", "stderr": "Checker timed out"}
    count = re.search(r"^Ran (\d+) tests? in ", run.stderr, re.MULTILINE)
    return {"returncode": run.returncode, "timed_out": False, "tests_run": int(count[1]) if count else 0,
            "stdout": run.stdout, "stderr": run.stderr}
