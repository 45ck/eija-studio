"""Versioned exact generated-app selection and evidence contracts; no authority is implied by a hash."""
from __future__ import annotations

from typing import Annotated, Any, Literal, Self
from pydantic import Field, model_validator
from .models import Contract, fingerprint

Digest = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]


class GeneratedBuildSubject(Contract):
    format: Literal["eija.build-subject.v1"]
    model_hash: Digest
    workflow_digest: Digest
    pack_digest: Digest
    data_digest: Digest | None
    screens_digest: Digest
    templates_digest: Digest
    template_paths: tuple[str, ...]
    implementation_digest: Digest
    payload_paths: tuple[str, ...]
    generated_files_hash: Digest
    digest: Digest

    @model_validator(mode="after")
    def consistent_digest(self) -> Self:
        if self.digest != fingerprint(self.model_dump(mode="json", exclude={"digest"})):
            raise ValueError("Generated subject digest does not match its contents")
        return self


class GeneratedChecker(Contract):
    id: Literal["generated-unittest-conformance-v1"]
    digest: Digest


class GeneratedCheckConfiguration(Contract):
    runner: Literal["python-unittest-discover"]
    arguments: tuple[str, ...]
    timeout_seconds: int = Field(gt=0, strict=True)
    python_version: str
    platform: str
    environment_digest: Digest
    runner_environment_digest: Digest
    isolation: Literal["isolated-python-fresh-bytecode-v1"]


class GeneratedAppBinding(Contract):
    format: Literal["eija.generated-app-review.v1"]
    subject: GeneratedBuildSubject
    checker: GeneratedChecker
    configuration: GeneratedCheckConfiguration
    digest: Digest

    @model_validator(mode="after")
    def consistent_digest(self) -> Self:
        if self.digest != fingerprint(self.model_dump(mode="json", exclude={"digest"})):
            raise ValueError("Generated review digest does not match its contents")
        return self


class GeneratedAppActivation(Contract):
    format: Literal["eija.generated-app-activation.v1"]
    case_id: str
    baseline_version: int = Field(ge=1, strict=True)
    binding: GeneratedAppBinding
    subject_hash: Digest


def generated_receipt_status(receipt: dict[str, Any], binding: GeneratedAppBinding,
                             authentic: bool) -> str:
    """Compute a scoped process observation, never trust its submitted status field."""
    if not authentic:
        return "FAIL"
    if (receipt.get("claim"), receipt.get("kind"), receipt.get("producer"), receipt.get("method")) != (
            "generated_app_conformance", "generated_app_execution", "eija-generated-app-verifier", binding.checker.id):
        return "UNKNOWN"
    artifact = receipt.get("artifact")
    if not isinstance(artifact, dict) or receipt.get("artifact_hash") != fingerprint(artifact):
        return "FAIL"
    subject = receipt.get("subject")
    if not isinstance(subject, dict):
        return "FAIL"
    if subject.get("generated_app") != binding.digest:
        return "STALE"
    return _execution_status(artifact, binding)


def _execution_status(artifact: dict[str, Any], binding: GeneratedAppBinding) -> str:
    expected = {"binding_digest": binding.digest, "subject_digest": binding.subject.digest,
                "checker": binding.checker.model_dump(mode="json"),
                "configuration": binding.configuration.model_dump(mode="json")}
    if any(artifact.get(key) != value for key, value in expected.items()):
        return "STALE"
    if artifact.get("before") != binding.subject.digest or artifact.get("after") != binding.subject.digest:
        return "FAIL"
    observations = (artifact.get("returncode"), artifact.get("timed_out"), artifact.get("tests_run"))
    if observations != (0, False, 6):
        return "FAIL"
    if tuple(type(value) for value in observations) != (int, bool, int):
        return "FAIL"
    return "PASS"
