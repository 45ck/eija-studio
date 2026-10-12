"""Read-only presentation inspection within PlayIDE's authenticated boundary."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from eija_studio.application.presentation import app_presentation
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import Pack
from eija_studio.domain.screens import Screens
from eija_studio.interfaces.app_build import app_files
from eija_studio.interfaces.c4 import C4Request


def register(app: Any, studio: Any, resolve: Callable[[Any], Workflow],
             pack_of: Callable[[Any], Pack], screens_of: Callable[[Any, Workflow], Screens]) -> None:
    """Inspect the same generated snapshot as Build & run, without applying or starting it."""
    @app.post("/api/play/presentation")
    def inspect(body: C4Request) -> dict[str, Any]:
        baseline = studio.workbench()
        model, pack = resolve(body), pack_of(body.plan)
        screens = screens_of(body, model)
        files, _ = app_files(pack, model, screens, identity_provider=studio.identity_provider)
        report = app_presentation(files)
        current = studio.workbench()
        if (current["baseline_version"] != baseline["baseline_version"] or current["model"] != baseline["model"]
                or resolve(body).semantic_hash != model.semantic_hash):
            raise DomainError("MODEL_CHANGED", "The model changed during app-map inspection; refresh and try again")
        return report | {"baseline_version": baseline["baseline_version"],
                         "model_scope": "Candidate preview" if body.plan or body.case_id else "Active baseline",
                         "source_review": "SOURCE_REVIEW_REQUIRED" if baseline["source_review_required"]
                         else "RELEASE_FIXTURE_MATCH"}
