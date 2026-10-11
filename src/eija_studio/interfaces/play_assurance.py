"""Read-only assurance review. Draft prose and laws never gain application authority."""
from __future__ import annotations

import json
from collections.abc import Callable
from importlib.resources import files
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import Field, ValidationError

from eija_studio.application.capabilities import capability_map
from eija_studio.application.law_proof import with_laws
from eija_studio.application.plan import MAX_DRAFT_STEPS
from eija_studio.application.requirement_trace import requirement_review
from eija_studio.domain.models import Contract, DomainError, Workflow, fingerprint
from eija_studio.domain.pack import Pack, pack_directory


class AssuranceCompareRequest(Contract):
    case_id: str | None = None
    model: Workflow | None = None
    plan: list[dict[str, Any]] | None = Field(default=None, max_length=MAX_DRAFT_STEPS)
    laws: list[dict[str, Any]] | None = Field(default=None, max_length=200)
    requirement_drafts: dict[str, str] = Field(default_factory=dict, max_length=28)


Reference = Annotated[str, Field(min_length=1, max_length=800)]


class RequirementLinks(Contract):
    satisfies: list[Reference] = Field(default_factory=list, max_length=32)
    verifies: list[Reference] = Field(default_factory=list, max_length=32)
    laws: list[Reference] = Field(default_factory=list, max_length=64)
    model: list[Reference] = Field(default_factory=list, max_length=64)


class RequirementLinksDocument(Contract):
    schema_version: Literal["eija.requirement-links.v1"] = Field(alias="schema")
    scope: str = Field(min_length=1, max_length=1000)
    required_bindings: list[Reference] = Field(min_length=1, max_length=32)
    links: dict[str, RequirementLinks] = Field(max_length=28)


def _snapshot_rows(document: dict[str, Any]) -> list[dict[str, Any]]:
    if (document.get("schema") != "eija.acceptance-snapshot.v1" or not isinstance(document.get("rows"), list)
            or len(document["rows"]) != 28):
        raise DomainError("ACCEPTANCE_SNAPSHOT_INVALID", "The packaged acceptance snapshot is unavailable")
    rows = document["rows"]
    if any(not isinstance(row, dict) or document.get("row_hashes", {}).get(row.get("id")) != fingerprint(row) for row in rows):
        raise DomainError("ACCEPTANCE_SNAPSHOT_INVALID", "The packaged requirement row identity is invalid")
    return rows


def _read_requirement_links(declared: Path, folder: Path, rows: list[dict[str, Any]]) -> RequirementLinksDocument:
    if declared.is_symlink() or not declared.resolve().is_relative_to(folder.resolve()):
        raise DomainError("ACCEPTANCE_SNAPSHOT_INVALID", "Declared requirement links must remain in the selected pack")
    if declared.stat().st_size > 32768:
        raise DomainError("ACCEPTANCE_SNAPSHOT_INVALID", "Declared requirement links exceed the supported size")
    try:
        links = RequirementLinksDocument.model_validate_json(declared.read_text(encoding="utf-8"))
    except (OSError, ValueError, ValidationError):
        raise DomainError("ACCEPTANCE_SNAPSHOT_INVALID", "Declared requirement links are unreadable") from None
    if set(links.links) - {row["id"] for row in rows}:
        raise DomainError("ACCEPTANCE_SNAPSHOT_INVALID", "Declared links reference an unknown acceptance requirement")
    return links


def _pack_requirement_links(pack: Pack | None, rows: list[dict[str, Any]]) -> RequirementLinksDocument | None:
    folder = pack_directory(pack) if pack is not None else None
    declared = folder / "requirements.json" if folder is not None else None
    if folder is None or declared is None or not declared.is_file():
        return None
    return _read_requirement_links(declared, folder, rows)


def acceptance_snapshot(pack: Pack | None = None) -> dict[str, Any]:
    """Only the explicit packaged snapshot; never discover or traverse the caller's cwd."""
    document = json.loads(files("eija_studio.resources").joinpath("acceptance_snapshot.json").read_text(encoding="utf-8"))
    rows = _snapshot_rows(document)
    links = _pack_requirement_links(pack, rows)
    if links is not None:
        document["traceability"] = links.model_dump(mode="json", by_alias=True)
    return document


def register(app: Any, studio: Any, resolve: Callable[[Any], Workflow], pack_of: Callable[[Any], Any]) -> None:
    """Register authenticated read/compare routes under the existing loopback HTTP boundary."""
    def report(body: AssuranceCompareRequest | None = None) -> dict[str, Any]:
        baseline = studio.workbench()
        model = resolve(body) if body is not None else Workflow.model_validate(baseline["model"])
        pack = pack_of(body.plan) if body is not None else studio.pack
        if body is not None and body.laws is not None:
            pack = with_laws(pack, body.laws)
        return {"capabilities": capability_map(studio.pack, model),
                "traceability": requirement_review(studio.pack, model, acceptance_snapshot(studio.pack),
                                                    connection=baseline.get("connection"),
                                                    drafts=body.requirement_drafts if body else None,
                                                    candidate_pack=pack,
                                                    baseline=Workflow.model_validate(baseline["model"])),
                "source_review": {"status": "SOURCE_REVIEW_REQUIRED" if baseline["source_review_required"] else "RELEASE_FIXTURE_MATCH",
                                  "scope": "Implementation identity only; this review cannot approve, activate or promote source trust."},
                "baseline_version": baseline["baseline_version"],
                "model_scope": "Candidate preview" if body and (body.plan or body.case_id) else "Active baseline"}

    @app.get("/api/play/assurance")
    def assurance() -> dict[str, Any]:
        return report()

    @app.post("/api/play/assurance/compare")
    def compare(body: AssuranceCompareRequest) -> dict[str, Any]:
        return report(body)
