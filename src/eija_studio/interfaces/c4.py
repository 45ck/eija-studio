"""C4 structural inspection under the existing authenticated PlayIDE boundary."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydantic import Field

from eija_studio import __version__
from eija_studio.application.c4 import app_c4
from eija_studio.application.plan import MAX_DRAFT_STEPS
from eija_studio.domain.models import Contract, DomainError, Workflow
from eija_studio.domain.pack import Pack
from eija_studio.domain.screens import Screens
from eija_studio.interfaces.app_build import app_files


class C4Request(Contract):
    case_id: str | None = None
    model: Workflow | None = None
    screens: dict[str, Any] | None = None
    plan: list[dict[str, Any]] | None = Field(default=None, max_length=MAX_DRAFT_STEPS)


def register(app: Any, studio: Any, resolve: Callable[[Any], Workflow],
             pack_of: Callable[[Any], Pack], screens_of: Callable[[Any, Workflow], Screens]) -> None:
    """Reuse PlayIDE's active/candidate resolver and generated-source projection."""
    @app.post("/api/play/c4")
    def inspect(body: C4Request) -> dict[str, Any]:
        baseline = studio.workbench()
        model, pack = resolve(body), pack_of(body.plan)
        screens = screens_of(body, model)
        files, manifest = app_files(pack, model, screens, identity_provider=studio.identity_provider)
        current = studio.workbench()
        if (current["baseline_version"] != baseline["baseline_version"] or current["model"] != baseline["model"]
                or resolve(body).semantic_hash != model.semantic_hash):
            raise DomainError("MODEL_CHANGED", "The model changed during architecture inspection; refresh and try again")
        report = app_c4(files, kernel_version=__version__)
        return report | {"baseline_version": baseline["baseline_version"],
                         "baseline_model_hash": Workflow.model_validate(baseline["model"]).semantic_hash,
                         "model_scope": "Candidate preview" if body.plan or body.case_id else "Active baseline",
                         "source_review": "SOURCE_REVIEW_REQUIRED" if baseline["source_review_required"] else "RELEASE_FIXTURE_MATCH",
                         "generation": {"oracle_cases": manifest["oracle"]["cases"], "conformance": "NOT_RUN",
                                        "scope": "Files generated in memory for structural inspection; no build or activation occurs"}}
