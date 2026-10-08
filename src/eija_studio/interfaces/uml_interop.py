"""`eija uml export` and `eija uml import`: UML interchange from the command line (ADR-0190).

Export prints the file (or writes `--out`) and lists on stderr what no UML file carries. Import prints the JSON report
and, with `--out-dir`, writes the candidate `workflow.json` and `data.json` so they can go through `eija laws`,
`eija render` and `eija build`. Neither command changes a pack: keeping an import is an owner's decision.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from eija_studio.application.interop import EXTENSIONS, FORMATS, detect_format, export_model, import_model
from eija_studio.domain.data import data_for
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import Pack

PACK_HELP = "Domain pack directory or JSON file (defaults to EIJA_PACK or packs/default.json)"


def add_parser(subs) -> None:
    uml = subs.add_parser("uml", help="Export the model to XMI, PlantUML, Mermaid or draw.io, or import one through the kernel")
    actions = uml.add_subparsers(dest="uml_command", required=True)
    export = actions.add_parser("export", help="Write the pack's state machine, class model and use cases in a UML format")
    export.add_argument("--format", choices=FORMATS, required=True, dest="fmt")
    export.add_argument("--pack", type=Path, help=PACK_HELP)
    export.add_argument("--workflow", type=Path, help="Export this workflow JSON instead of the pack's own model")
    export.add_argument("--out", type=Path, help="Write here instead of stdout (LF, UTF-8); conventional suffixes: "
                        + ", ".join(EXTENSIONS.values()))
    imported = actions.add_parser("import", help="Read a UML file as typed edits the kernel checks; report what was not mapped")
    imported.add_argument("file", type=Path)
    imported.add_argument("--format", choices=FORMATS, dest="fmt", help="Defaults to the file's suffix, else its content")
    imported.add_argument("--pack", type=Path, help=PACK_HELP)
    imported.add_argument("--workflow", type=Path, help="Compare with this workflow JSON instead of the pack's own model")
    imported.add_argument("--out-dir", type=Path, help="Write the candidate workflow.json and data.json here")


def _model(args, pack: Pack) -> Workflow:
    return Workflow.model_validate_json(args.workflow.read_text(encoding="utf-8")) if args.workflow else pack.model


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def export_command(args, pack: Pack) -> int:
    text, report = export_model(args.fmt, pack, _model(args, pack), data_for(pack))
    if args.out is None:
        sys.stdout.buffer.write(text.encode("utf-8"))
        sys.stdout.buffer.flush()
    else:
        _write(args.out, text)
        sys.stdout.write(f"{args.out}\n")
    sys.stderr.write("not carried by any UML file: " + "; ".join(report["not_carried"]) + "\n")
    return 0


def import_command(args, pack: Pack) -> int:
    """Exit 0 when every element was imported and the kernel accepts the result; 2 otherwise (the report says why)."""
    text = args.file.read_text(encoding="utf-8")
    fmt = args.fmt or detect_format(args.file.name, text)
    report = import_model(fmt, text, pack, _model(args, pack), data_for(pack))
    if args.out_dir is not None:
        for name, part in (("workflow.json", report["state_machine"]), ("data.json", report["class_model"])):
            if part.get("candidate") is not None:
                _write(args.out_dir / name, json.dumps(part["candidate"], indent=2, ensure_ascii=False) + "\n")
    sys.stdout.write(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    return 0 if report["status"] == "CLEAN" else 2


def uml_command(args, pack: Pack) -> int:
    """`pack` is the resolved `--pack` (the CLI resolves it, so this module needs no composition root)."""
    if args.uml_command == "export":
        return export_command(args, pack)
    if args.uml_command == "import":
        return import_command(args, pack)
    raise DomainError("CONFIGURATION", "eija uml export|import")
