"""PlantUML itself reads every PlantUML export, and must read what PlayIDE reads (ADR-0190).

PlantUML (the MIT-licensed build, run as a separate Java process, never shipped) checks each pack's PlantUML export
with `-checkonly`, then writes its own XMI of every block (`-xmi:star`). That XMI is PlantUML's reading of the text:
the states and their transitions with labels, the classes with stereotypes and attribute lines, and the associations
with their names, ends and aggregation. It is compared with PlayIDE's reading of the same text. A disagreement means
PlantUML would draw something other than the model, so the check fails.

    python -m verification.interop.plantuml_oracle --out reports/interop/plantuml.json

Needs Java and the pinned jar (`JAR_NAME`, sha256 `JAR_SHA256`), found at $EIJA_PLANTUML_JAR or in `.tmp/tools/`:

    curl -o .tmp/tools/plantuml-mit-1.2026.8.jar \\
      https://repo1.maven.org/maven2/net/sourceforge/plantuml/plantuml-mit/1.2026.8/plantuml-mit-1.2026.8.jar

Without them the report is NOT_RUN (exit 3), never PASS. PlantUML's XMI 1.x writer turns a `:` inside a label into a
space, so labels are compared with that one substitution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from eija_studio.application.interop import export_model, plantuml
from eija_studio.domain.data import data_for
from eija_studio.domain.pack import load_pack

from .generate import ROOT, packs, say

JAR_NAME = "plantuml-mit-1.2026.8.jar"
JAR_SHA256 = "8a171e8941d1f68f4ec28f5c180a4bf8d54a2cd679348370d4ba59fc9fb910e3"
UML = "{href://org.omg/UML/1.3}"


def _jar() -> Path | None:
    path = Path(os.environ.get("EIJA_PLANTUML_JAR") or ROOT / ".tmp" / "tools" / JAR_NAME)
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != JAR_SHA256:
        return None
    return path


def _plantuml(java: str, jar: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([java, "-Djava.awt.headless=true", "-jar", str(jar), *args],  # noqa: S603 - fixed argv, no shell
                          capture_output=True, text=True, timeout=300, check=False)


def _names(root: ET.Element) -> dict[str, str]:
    return {e.get("xmi.id", ""): e.get("name", "") for e in root.iter() if e.get("xmi.id")}


def _ends(assoc: ET.Element) -> list[ET.Element]:
    return list(assoc.iter(f"{UML}AssociationEnd"))


def _theirs_states(root: ET.Element) -> dict[str, Any]:
    names = _names(root)
    states = sorted(e.get("name", "") for e in root.iter(f"{UML}State") if e.get("name"))
    initial, edges = [], []
    for assoc in root.iter(f"{UML}Association"):
        a, b = (names.get(e.get("type", ""), "") for e in _ends(assoc))
        if not a and b:
            initial.append(b)
        elif a and b:
            edges.append([a, b, assoc.get("name", "")])
    return {"states": states, "initial": initial, "edges": sorted(edges)}


def _theirs_classes(root: ET.Element) -> dict[str, Any]:
    names = _names(root)
    classes = {k.get("name", ""): {"stereotypes": sorted(s.get("name", "") for s in k.iter(f"{UML}Stereotype")),
                                   "attributes": [a.get("name", "") for a in k.iter(f"{UML}Attribute")]}
               for k in root.iter(f"{UML}Class")}
    links = []
    for assoc in root.iter(f"{UML}Association"):
        ends = [[names.get(e.get("type", ""), ""), e.get("name", ""), e.get("aggregation", "none")] for e in _ends(assoc)]
        if all(end[0] for end in ends):  # an end with no name is a note's anchor line, not an association
            links.append([assoc.get("name", ""), *ends])
    return {"classes": classes, "links": sorted(links)}


def _ours(text: str) -> dict[str, Any]:
    parsed = plantuml.parse(text)
    states = {"states": sorted(parsed.states or []), "initial": [parsed.initial] if parsed.initial else [],
              "edges": sorted([e.source, e.target, e.label.replace(":", " ")] for e in parsed.edges)}
    classes: dict[str, Any] = {
        k.name: {"stereotypes": ["record"] if k.record else [],
                 "attributes": [f"{a.name} : {a.type} [{'1' if a.lower else '0..1'}]"
                                + (f" {{maxLength = {a.max_length}}}" if a.max_length is not None else "") for a in k.attributes]}
        for k in parsed.classes or []}
    classes |= {name: {"stereotypes": [], "attributes": list(literals)} for name, literals in parsed.enums.items()}
    whole = {"composition": "composite", "aggregation": "aggregate", "association": "none"}
    links = sorted([x.role, [x.source, x.source_multiplicity, whole[x.kind]], [x.target, x.target_multiplicity, "none"]]
                   for x in parsed.links)
    return {"state": states, "class": {"classes": classes, "links": links}}


# Deliberately unfaithful exports the check must catch: if one agrees, the oracle is blind to that defect.
CONTROLS = {
    "creole line break left in a label": lambda text: text.replace(" : CheckOut [", " : Check\\nOut [", 1),  # vocab-ok: a negative control planted in one fixture pack's export
    "association ends left unquoted": lambda text: text.replace('Item "1" *-- "1..*" Copy', "Item 1 *-- 1..* Copy", 1),
    "stereotype written inside the class body": lambda text: text.replace("class Loan <<record>> {", "class Loan {\n  <<record>>", 1),
}


def _check(java: str, jar: Path, location: Path, scratch: Path, text: str | None = None) -> dict[str, Any]:
    pack = load_pack(location)
    text = text if text is not None else export_model("plantuml", pack, None, data_for(pack))[0]
    source = scratch / f"{location.name}.puml"
    source.write_text(text, encoding="utf-8", newline="\n")
    syntax = _plantuml(java, jar, "-checkonly", str(source))
    if syntax.returncode != 0:
        return {"pack": location.name, "syntax": False, "agree": False, "plantuml": syntax.stdout[-2000:], "playide": None}
    _plantuml(java, jar, "-xmi:star", "-o", str(scratch), str(source))
    theirs: dict[str, Any] = {}
    for kind in ("states", "classes"):
        path = scratch / f"{pack.id}-{kind}.xmi"
        if path.is_file():
            root = ET.fromstring(path.read_text(encoding="utf-8"))  # noqa: S314 - PlantUML's own output, written just now
            theirs["state" if kind == "states" else "class"] = _theirs_states(root) if kind == "states" else _theirs_classes(root)
    ours = _ours(text)
    if "class" not in theirs:
        ours.pop("class")
    return {"pack": location.name, "syntax": syntax.returncode == 0, "agree": theirs == ours, "plantuml": theirs, "playide": ours}


def run() -> dict[str, Any]:
    java, jar = shutil.which("java"), _jar()
    if java is None or jar is None:
        return {"status": "NOT_RUN", "reason": f"needs java and {JAR_NAME} (sha256 {JAR_SHA256[:12]}...); see the module docstring"}
    with tempfile.TemporaryDirectory(dir=ROOT / ".tmp" if (ROOT / ".tmp").is_dir() else None) as scratch:
        results = [_check(java, jar, location, Path(scratch)) for location in packs()]
        loan = ROOT / "packs" / "library-loan"  # vocab-ok: a negative control planted in one fixture pack's export
        base = export_model("plantuml", load_pack(loan), None, data_for(load_pack(loan)))[0]
        controls = {name: not _check(java, jar, loan, Path(scratch), change(base))["agree"] for name, change in CONTROLS.items()}
    failed = [r for r in results if not (r["syntax"] and r["agree"])]
    blind = sorted(name for name, caught in controls.items() if not caught)
    return {"status": "FAIL" if failed or blind else "PASS", "engine": JAR_NAME, "controls_caught": controls,
            "packs": [{k: r[k] for k in ("pack", "syntax", "agree")} for r in results], "disagreements": failed}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m verification.interop.plantuml_oracle", description=__doc__.split("\n")[0])
    parser.add_argument("--out", type=Path, help="Write the JSON report here")
    args = parser.parse_args(argv)
    report = run()
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    say(f"plantuml oracle: {report['status']}" + (f" ({report.get('reason')})" if report.get("reason") else ""))
    return {"PASS": 0, "NOT_RUN": 3}.get(report["status"], 1)


if __name__ == "__main__":
    raise SystemExit(main())
