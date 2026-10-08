"""PlayIDE routes for UML interchange (ADR-0190): export the model on screen, and read a UML file as a report.

`/api/play/export` writes the model the page shows (the model in force, or with the previewed plan) in one of the four
formats. `/api/play/import` reads an uploaded file against the model in force and returns the import report: its
typed edits are offered to the person as a plan, the same as drawn edits, so nothing is applied or saved from here.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal

from pydantic import Field

from eija_studio.application.interop import EXTENSIONS, MAX_CHARS, MEDIA_TYPES, detect_format, export_model, import_model
from eija_studio.domain.data import data_for
from eija_studio.domain.models import Contract, Workflow

Format = Literal["xmi", "plantuml", "mermaid", "drawio"]


class ExportRequest(Contract):
    case_id: str | None = None
    model: Workflow | None = None
    plan: list[dict[str, Any]] | None = Field(default=None, max_length=12)  # a previewed plan exports the model it shows
    format: Format


class ImportRequest(Contract):
    case_id: str | None = None
    model: Workflow | None = None  # the model the page shows; it must still be the one in force
    filename: str = Field(default="", max_length=200)
    format: Format | None = None  # None: from the file name, else its content
    text: str = Field(min_length=1, max_length=MAX_CHARS)


def register(app, studio, resolve: Callable[[Any], Workflow], request_type: type) -> None:
    """`resolve` is PlayIDE's own: it reads `request_type` (its build request) as the model the page is about."""
    @app.post("/api/play/export")
    def play_export(body: ExportRequest):
        """The model on screen as a UML file, with what no UML file carries."""
        model = resolve(request_type(case_id=body.case_id, model=body.model, plan=body.plan))
        text, report = export_model(body.format, studio.pack, model, data_for(studio.pack))
        name = f"{studio.pack.id}{EXTENSIONS[body.format]}"
        return {"filename": name, "media_type": MEDIA_TYPES[body.format], "text": text, "report": report}

    @app.post("/api/play/import")
    def play_import(body: ImportRequest):
        """A UML file read against the model in force: typed edits, the kernel's verdict and every element's fate."""
        model = resolve(request_type(case_id=body.case_id, model=body.model))
        fmt = body.format or detect_format(body.filename, body.text)
        return import_model(fmt, body.text, studio.pack, model, data_for(studio.pack))
