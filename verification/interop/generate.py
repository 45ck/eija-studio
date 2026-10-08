"""Write (or check) the committed UML exports of every authored pack, and prove each one reads back unchanged.

    python -m verification.interop.generate          # rewrite verification/interop/generated/
    python -m verification.interop.generate --check  # exit 1 if a file is stale or an export does not round-trip

The files are derived (ADR-0093): change the pack, then regenerate. They let a reader open a pack in Enterprise
Architect, Papyrus, PlantUML, a Markdown reader or draw.io without installing EIJA. The round trip is the faithfulness
check: importing each export into its own pack must be CLEAN (nothing unmapped, nothing defaulted) and must leave the
state machine and the class model exactly as they were.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from eija_studio.application.interop import EXTENSIONS, FORMATS, export_model, import_model
from eija_studio.domain.data import data_for
from eija_studio.domain.pack import load_pack

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "generated"


def say(message: str) -> None:
    sys.stdout.write(message + "\n")
    sys.stdout.flush()


def packs() -> list[Path]:
    return sorted(p for p in (ROOT / "packs").iterdir() if (p / "pack.json").is_file())


def exports() -> dict[Path, str]:
    files: dict[Path, str] = {}
    for location in packs():
        pack = load_pack(location)
        for fmt in FORMATS:
            text, _ = export_model(fmt, pack, None, data_for(pack))
            files[OUT / f"{location.name}{EXTENSIONS[fmt]}"] = text
    return files


def round_trip_problems() -> list[str]:
    """Every way an export fails to read back as exactly the model it came from."""
    problems: list[str] = []
    for location in packs():
        pack = load_pack(location)
        data = data_for(pack)
        for fmt in FORMATS:
            text, _ = export_model(fmt, pack, None, data)
            report: dict[str, Any] = import_model(fmt, text, pack, None, data)
            where = f"{location.name} {fmt}"
            if report["status"] != "CLEAN" or report["defaulted"]:
                problems.append(f"{where}: {report['status']}, unmapped {report['unmapped']}, defaulted {report['defaulted']}")
            if report["state_machine"].get("changed") or report["state_machine"].get("transactions"):
                problems.append(f"{where}: the state machine changed on the way back")
            if data is not None and report["class_model"].get("candidate") != data.model_dump(mode="json"):
                problems.append(f"{where}: the class model changed on the way back")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m verification.interop.generate", description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true", help="Fail if a committed file is stale or an export does not round-trip")
    args = parser.parse_args(argv)
    files = exports()
    problems = round_trip_problems()
    if args.check:
        stale = sorted(str(p.relative_to(ROOT)) for p, text in files.items()
                       if not p.is_file() or p.read_text(encoding="utf-8") != text)
        extra = sorted(str(p.relative_to(ROOT)) for p in OUT.glob("*") if p not in files and p.name != "README.md")
        for path in stale + extra:
            say(f"stale: {path} (run python -m verification.interop.generate)")
        for problem in problems:
            say(f"round trip: {problem}")
        return 1 if stale or extra or problems else 0
    OUT.mkdir(parents=True, exist_ok=True)
    for path, text in files.items():
        path.write_text(text, encoding="utf-8", newline="\n")
        say(str(path.relative_to(ROOT)))
    for problem in problems:
        say(f"round trip: {problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
