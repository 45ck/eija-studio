"""Shared generation and exact-app evidence operations for the existing kernel and checker."""
from __future__ import annotations

from typing import Any, Callable
from eija_studio.domain.change_case import ChangeCase
from eija_studio.domain.data import DataModel, data_for
from eija_studio.domain.pack import Pack
from eija_studio.domain.screens import Screens, screens_for
from eija_studio.domain.evidence import combine
from eija_studio.domain.generated_app import GeneratedAppBinding, generated_receipt_status
from eija_studio.domain.models import DomainError, Workflow, canonical, fingerprint
from .appgen import generate
from .build_subject import SUBJECT_FILE, build_subject, checked_build_subject
from .ports import GeneratedApps, IdentityProvider

TEMPLATES = {
    "init.py.tmpl": "app/__init__.py", "service.py.tmpl": "app/service.py",
    "server.py.tmpl": "app/server.py", "build_identity.py.tmpl": "app/build_identity.py",
    "web/index.html.tmpl": "app/web/index.html", "web/app.js.tmpl": "app/web/app.js",
    "web/app.css.tmpl": "app/web/app.css", "run.py.tmpl": "run.py",
    "test_conformance.py.tmpl": "tests/test_conformance.py",
    "react-source/main.jsx": "frontend/main.jsx",
    "react-source/controller.js": "frontend/controller.js",
    "react-source/app.css": "frontend/app.css",
    "react-source/package.json": "frontend/package.json",
    "react-source/package-lock.json": "frontend/package-lock.json",
    "react-source/build.mjs": "frontend/build.mjs",
    "react-source/build-manifest.json": "frontend/build-manifest.json",
    "react-source/LICENSES.txt": "frontend/LICENSES.txt",
}


def assemble_app(pack: Pack, model: Workflow, data: DataModel | None, screens: Screens,
                 static: dict[str, str], implementation: str) -> tuple[dict[str, str], dict[str, Any]]:
    """One generator and snapshot identity for previews and approved artifacts."""
    generated, manifest = generate(pack, model, data, screens)
    files = static | {"tests/__init__.py": ""} | generated
    manifest["subject"] = build_subject(files, implementation_digest=implementation, template_paths=static)
    files[SUBJECT_FILE] = canonical(manifest["subject"]) + "\n"
    return files, manifest


def review_snapshot(pack: Pack, model: Workflow, static: dict[str, str], identity: dict[str, Any],
                    configuration: dict[str, Any]) -> tuple[dict[str, str], dict[str, Any], GeneratedAppBinding]:
    """Derive canonical contracts and the review binding through the shared pure assembler."""
    data = data_for(pack)
    screens = screens_for(pack, model, data)
    files, manifest = assemble_app(pack, model, data, screens, static, identity["implementation"])
    body = {"format": "eija.generated-app-review.v1", "subject": manifest["subject"],
            "checker": {"id": "generated-unittest-conformance-v1", "digest": fingerprint({
                "template": files["tests/test_conformance.py"], "implementation": identity["implementation"]})},
            "configuration": configuration}
    return files, manifest, GeneratedAppBinding.model_validate(body | {"digest": fingerprint(body)})


def validate_review_payload(files: dict[str, str], implementation: str, binding: GeneratedAppBinding) -> None:
    """The selected payload and installed implementation must satisfy the same build-subject contract."""
    checked_build_subject(files, implementation_digest=implementation,
                          expected_subject=binding.subject.model_dump(mode="json"))


def app_build_view(case: ChangeCase, current: dict[str, Any] | None,
                   authentic: Callable[[dict[str, Any]], bool]) -> dict[str, Any]:
    """Keep workflow evidence separate from generated application execution evidence."""
    binding = case.app_build
    if binding is None:
        return {"binding": None, "subject": None, "freshness": "UNBOUND", "conformance": {"status": "NOT_RUN"},
                "limitations": ["Historical or workflow-only review; no exact generated application approval."]}
    observed = current or {"freshness": "UNAVAILABLE", "detail": "Generated-app measurement is unavailable"}
    receipts = [r for r in case.receipts if r.get("claim") == "generated_app_conformance"]
    statuses = [generated_receipt_status(r, binding, authentic(r)) for r in receipts]
    status = combine(statuses) if statuses else "NOT_RUN"
    if observed["freshness"] != "CURRENT" and status == "PASS":
        status = "STALE"
    limitations = ["Local application and synthetic fixture actors; no authentication or external delivery proof.",
                   "Generated storage, data validation and effects are compared with the installed kernel."]
    if status == "CONFLICT":
        limitations.append("A later passing check does not erase an earlier failure; repair and create a new exact-app review.")
    return {"binding": binding.model_dump(mode="json"), "subject": binding.subject.model_dump(mode="json"),
            "freshness": observed["freshness"], "conformance": {"status": status,
                "checker": binding.checker.id, "cases": observed.get("cases"), "detail": observed.get("detail", "")},
            "limitations": limitations}


def app_build_blockers(case: ChangeCase, view: dict[str, Any]) -> list[str]:
    if case.app_build is None:
        return []
    blockers = []
    if view["freshness"] != "CURRENT":
        blockers.append("APP_BUILD_" + view["freshness"])
    if view["conformance"]["status"] != "PASS":
        blockers.append("APP_CONFORMANCE_" + view["conformance"]["status"])
    return blockers


def bind_subject(subject: dict[str, Any], binding: GeneratedAppBinding | None) -> dict[str, Any]:
    return subject | {"generated_app": binding.digest} if binding is not None else subject


def capture_app(case: ChangeCase, expected_digest: str, pack: Pack, apps: GeneratedApps | None,
                identity_provider: IdentityProvider) -> tuple[ChangeCase, str]:
    """Bind the checked payload to this exact selected case; persistence stays in Studio."""
    if apps is None:
        raise DomainError("APP_BUILD_UNAVAILABLE", "Generated application checking is unavailable")
    binding = apps.capture(pack, case.executable(), expected_digest, identity_provider)
    bound = ChangeCase.model_validate(case.model_dump(mode="json") | {"app_build": binding.model_dump(mode="json")})
    return bound, binding.digest


def app_current(case: ChangeCase, pack: Pack, apps: GeneratedApps | None,
                identity_provider: IdentityProvider) -> dict[str, Any] | None:
    """Remeasure a selected application's current bytes through the existing port."""
    if case.app_build is None or apps is None:
        return None
    return apps.current(pack, case.executable(), case.app_build, identity_provider)


def require_app_current(case: ChangeCase, current: dict[str, Any] | None) -> None:
    """A workflow-only historical case remains unbound; a bound app must still be current."""
    if case.app_build is not None and (current is None or current["freshness"] != "CURRENT"):
        raise DomainError("APP_BUILD_CHANGED", "The selected generated app changed or is unavailable; inspect a fresh build")


def verify_app(case: ChangeCase, subject: dict[str, Any], apps: GeneratedApps | None,
               identity_provider: IdentityProvider, seal: Callable[[dict[str, Any]], dict[str, Any]],
               stamp: Callable[[], str], new_id: Callable[[], str]) -> list[dict[str, Any]]:
    """Seal the observed checker artifact, without approving or writing the case."""
    if case.app_build is None:
        return []
    if apps is None:
        raise DomainError("APP_BUILD_UNAVAILABLE", "Generated application checking is unavailable")
    artifact = apps.verify(case.app_build, identity_provider)
    return [seal({"id": new_id(), "claim": "generated_app_conformance", "kind": "generated_app_execution",
        "subject": subject, "producer": "eija-generated-app-verifier", "method": case.app_build.checker.id,
        "created_at": stamp(), "artifact_hash": fingerprint(artifact), "artifact": artifact})]


def activation_association(case: ChangeCase, subject_hash: str) -> dict[str, Any] | None:
    """Exact-app provenance to be committed atomically with the active model by Studio."""
    if case.app_build is None:
        return None
    return {"format": "eija.generated-app-activation.v1", "case_id": case.id, "baseline_version": case.baseline_version + 1,
            "binding": case.app_build.model_dump(mode="json"), "subject_hash": subject_hash}
