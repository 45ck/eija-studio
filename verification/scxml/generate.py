"""Write (or check) the committed SCXML export of every authored pack: verification/scxml/generated/<pack>.scxml.

    python -m verification.scxml.generate          # rewrite the files
    python -m verification.scxml.generate --check  # exit 1 if any file differs from a fresh export

The files are derived (ADR-0093): change the pack's model, then regenerate. They let a reader, or another SCXML
engine, see the statechart without installing EIJA.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from eija_studio.application.scxml import to_scxml
from eija_studio.domain.pack import load_pack

from .differential import packs, say

OUT = Path(__file__).resolve().parent / "generated"


def expected() -> dict[Path, str]:
    return {OUT / f"{location.name}.scxml": to_scxml(load_pack(location)) for location in packs()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m verification.scxml.generate", description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true", help="Fail if a committed file is stale or missing")
    args = parser.parse_args(argv)
    files = expected()
    if args.check:
        stale = sorted(str(p.relative_to(OUT.parents[2])) for p, text in files.items()
                       if not p.is_file() or p.read_text(encoding="utf-8") != text)
        extra = sorted(str(p.relative_to(OUT.parents[2])) for p in OUT.glob("*.scxml") if p not in files)
        for path in stale + extra:
            say(f"stale: {path} (run python -m verification.scxml.generate)")
        return 1 if stale or extra else 0
    OUT.mkdir(parents=True, exist_ok=True)
    for path, text in files.items():
        path.write_text(text, encoding="utf-8", newline="\n")
        say(str(path.relative_to(OUT.parents[2])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
