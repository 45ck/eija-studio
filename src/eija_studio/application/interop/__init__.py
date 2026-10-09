"""UML interchange: export a pack to XMI, PlantUML, Mermaid or draw.io, and import from them through the kernel (ADR-0190).

`export_model` writes the model in force (or a candidate) faithfully and lists what no UML file carries.
`import_model` reads a file, turns its state machine into typed edits the kernel applies and judges, validates its
class model as a `data.json`, and reports every element as mapped, defaulted or not imported, with the reason.
Nothing here writes a file or changes the model in force.
"""
from __future__ import annotations

from pathlib import PurePath
from typing import Any

from eija_studio.domain.data import DataModel
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import Pack

from . import drawio, drawio_reader, mermaid, plantuml, xmi, xmi_reader
from .mapping import import_parsed
from .model import Parsed
from .start import start_documents

FORMATS = ("xmi", "plantuml", "mermaid", "drawio")
EXTENSIONS = {"xmi": ".xmi", "plantuml": ".puml", "mermaid": ".md", "drawio": ".drawio"}
MEDIA_TYPES = {"xmi": "application/vnd.xmi+xml", "plantuml": "text/plain", "mermaid": "text/markdown", "drawio": "application/xml"}
MAX_CHARS = 2_000_000  # text formats; XMI and draw.io also enforce their own byte limit
_WRITERS = {"xmi": xmi.export, "plantuml": plantuml.export, "mermaid": mermaid.export, "drawio": drawio.export}
_READERS = {"xmi": xmi_reader.parse, "plantuml": plantuml.parse, "mermaid": mermaid.parse, "drawio": drawio_reader.parse}
_SUFFIXES = {".xmi": "xmi", ".uml": "xmi", ".xml": "xmi", ".puml": "plantuml", ".plantuml": "plantuml", ".pu": "plantuml",
             ".iuml": "plantuml", ".wsd": "plantuml", ".mmd": "mermaid", ".mermaid": "mermaid", ".md": "mermaid",
             ".drawio": "drawio", ".dio": "drawio"}


def _need(fmt: str) -> None:
    if fmt not in FORMATS:
        raise DomainError("FORMAT_UNSUPPORTED", f"UML interchange formats: {', '.join(FORMATS)}")


def export_model(fmt: str, pack: Pack, model: Workflow | None = None, data: DataModel | None = None) -> tuple[str, dict[str, Any]]:
    """(file text, report). The report names the format, the model's hash and the parts of the pack not carried."""
    _need(fmt)
    model = model if model is not None else pack.model
    if model.id != pack.id:
        raise DomainError("WORKFLOW_PACK_MISMATCH", f"Workflow {model.id!r} does not belong to pack {pack.id!r}")
    return _WRITERS[fmt](pack, model, data)


def detect_format(name: str, text: str) -> str:
    """The format of an uploaded file, from its name, else from its first bytes."""
    by_name = _SUFFIXES.get(PurePath(name).suffix.lower()) if name else None
    head = text.lstrip()[:4000]
    if "<mxfile" in head or head.startswith("<mxGraphModel"):
        return "drawio"
    if by_name:
        return by_name
    if head.startswith("<"):
        return "xmi"
    if "@startuml" in head:
        return "plantuml"
    if any(k in head for k in ("stateDiagram", "classDiagram", "```mermaid")):
        return "mermaid"
    raise DomainError("FORMAT_UNKNOWN", "Not a UML file PlayIDE reads: XMI, PlantUML, Mermaid or draw.io")


def parse_file(fmt: str, text: str) -> Parsed:
    _need(fmt)
    if len(text) > MAX_CHARS:
        raise DomainError("IMPORT_TOO_LARGE", f"A UML file is read up to {MAX_CHARS} characters")
    return _READERS[fmt](text)


def import_model(fmt: str, text: str, pack: Pack, model: Workflow | None = None,
                 data: DataModel | None = None) -> dict[str, Any]:
    """The import report for `text` against the model in force (`model`, else the pack's own) and its class model."""
    model = model if model is not None else pack.model
    return import_parsed(fmt, parse_file(fmt, text), pack, model, data)


def start_from_file(fmt: str, text: str, name: str, pack_id: str, record: str = "Record") -> tuple[dict[str, Any], dict[str, Any]]:
    """A new system's documents from a UML file, and the import report (`PackError` when the kernel refuses them)."""
    return start_documents(fmt, parse_file(fmt, text), name, pack_id, record)
