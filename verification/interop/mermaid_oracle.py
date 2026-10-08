"""Mermaid's own parser reads every Mermaid export, and must read what PlayIDE reads (ADR-0190).

The vendored Mermaid (`resources/web/vendor/mermaid.min.js`, the same bytes PlayIDE renders with) runs in a headless
Chromium and parses each block of each pack's Mermaid export. Its diagram database is compared with PlayIDE's own
reading of the same text: the states, every transition with its full label, the initial state, the classes with their
annotations and member lines, the associations with their kind, ends and role, and the notes. A disagreement means
the export would show engineers something other than the model, so the check fails.

    python -m verification.interop.mermaid_oracle --out reports/interop/mermaid.json

Without Playwright or a Chromium the report is NOT_RUN (exit 3), never PASS. Set EIJA_CHROMIUM to a browser
executable, or install Chrome for `channel="chrome"`.
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import re
from pathlib import Path
from typing import Any

from eija_studio.application.interop import export_model, mermaid
from eija_studio.domain.data import data_for
from eija_studio.domain.pack import load_pack

from .generate import ROOT, packs, say

VENDOR = ROOT / "src/eija_studio/resources/web/vendor/mermaid.min.js"
READ_DB = """async text => {
  await mermaid.parse(text);
  const db = (await mermaid.mermaidAPI.getDiagramFromText(text)).db;
  const plain = v => JSON.parse(JSON.stringify(v instanceof Map ? Object.fromEntries(v) : v));
  const out = {};
  for (const k of ['getRelations', 'getClasses', 'getStates', 'getNotes']) { if (db[k]) out[k] = plain(db[k]()); }
  return out;
}"""
_KINDS = {0: "aggregation", 1: "extension", 2: "composition", 3: "association", 4: "lollipop"}


def _decoded(text: str) -> str:
    """Mermaid keeps `#59;` as its own placeholder (`\ufb02\u00b0\u00b059\u00b6\u00df`) until it renders; decode both forms."""
    text = re.sub("\ufb02\u00b0\u00b0(\\d+)\u00b6\u00df", lambda m: f"#{m.group(1)};", text)
    text = re.sub("\ufb02\u00b0(\\w+)\u00b6\u00df", lambda m: f"#{m.group(1)};", text)
    return mermaid.unescape(text)


def _states_view(db: dict[str, Any]) -> dict[str, Any]:
    names = {k: (v.get("descriptions") or [k])[0] for k, v in db.get("getStates", {}).items()}
    initial = [names.get(r["id2"], r["id2"]) for r in db["getRelations"] if r["id1"] == "root_start"]
    edges = sorted((names.get(r["id1"], r["id1"]), names.get(r["id2"], r["id2"]), _decoded(r["relationTitle"]))
                   for r in db["getRelations"] if "root_start" not in (r["id1"], r["id2"]) and r["id2"] != "root_end")
    states = sorted(n for k, n in names.items() if k not in ("root_start", "root_end"))
    return {"states": states, "initial": initial, "edges": [list(e) for e in edges]}


def _classes_view(db: dict[str, Any]) -> dict[str, Any]:
    classes = {name: {"annotations": sorted(c.get("annotations", [])),
                      "members": [_decoded(m["id"]) for m in c.get("members", [])]}
               for name, c in db.get("getClasses", {}).items()}
    links = sorted([r["id1"], r["id2"], _KINDS.get(r["relation"]["type1"], "none"), _KINDS.get(r["relation"]["type2"], "none"),
                    r.get("relationTitle1", ""), r.get("relationTitle2", ""), _decoded(r.get("title", ""))]
                   for r in db["getRelations"])
    notes = sorted([n["class"], _decoded(n["text"])] for n in db.get("getNotes", {}).values())
    return {"classes": classes, "links": links, "notes": notes}


def _ours(text: str) -> dict[str, Any]:
    """The same views, from PlayIDE's reader."""
    parsed = mermaid.parse(text)
    out: dict[str, Any] = {}
    if parsed.states is not None:
        out["state"] = {"states": sorted(parsed.states), "initial": [parsed.initial] if parsed.initial else [],
                        "edges": [list(e) for e in sorted((e.source, e.target, e.label) for e in parsed.edges)]}
    if parsed.classes is not None:
        classes = {k.name: {"annotations": ["record"] if k.record else [], "members": [_member(a) for a in k.attributes]}
                   for k in parsed.classes}
        classes |= {name: {"annotations": ["enumeration"], "members": list(lits)} for name, lits in parsed.enums.items()}
        kinds = {"composition": "composition", "aggregation": "aggregation", "association": "none"}
        links = sorted([x.source, x.target, kinds[x.kind], "association" if x.kind == "association" else "none",
                        x.source_multiplicity, x.target_multiplicity, x.role] for x in parsed.links)
        out["class"] = {"classes": classes, "links": links, "notes": sorted([k.name, k.description] for k in parsed.classes if k.description)}
    return out


def _member(attr: Any) -> str:
    bound = "1" if attr.lower >= 1 else "0..1"
    return f"{attr.name} : {attr.type} [{bound}]" + (f" maxLength={attr.max_length}" if attr.max_length is not None else "")


def _blocks(text: str) -> list[str]:
    return [m.group("body").strip("\n") + "\n" for m in re.finditer(r"^```mermaid\n(?P<body>.*?)^```", text, re.M | re.S)]


def _theirs(page: Any, text: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for block in _blocks(text):
        db = page.evaluate(READ_DB, block)
        if block.startswith("stateDiagram"):
            out["state"] = _states_view(db)
        else:
            out["class"] = _classes_view(db)
    return out


# Deliberately unfaithful exports the check must catch: if one agrees, the oracle is blind to that defect.
CONTROLS = {
    "unescaped ';' in a transition label": lambda text: text.replace("Audit:LoanCheckedOut, ", "Audit:LoanCheckedOut; ", 1),  # vocab-ok: a negative control planted in one fixture pack's export
    "unescaped braces in a member line": lambda text: text.replace("maxLength=200", "{maxLength=200}", 1),
    "unescaped quote in a note": lambda text: text.replace("borrowing one copy", 'borrowing "one" copy', 1),
}


def _agrees(page: Any, api: Any, text: str) -> bool:
    try:
        return _theirs(page, text) == _ours(text)
    except api.Error:
        return False  # Mermaid could not parse it at all


def _browser(api: Any, playwright: Any) -> Any:
    executable = os.environ.get("EIJA_CHROMIUM")
    if executable:
        return playwright.chromium.launch(headless=True, executable_path=executable)
    try:
        return playwright.chromium.launch(channel="chrome", headless=True)
    except api.Error:
        return playwright.chromium.launch(headless=True)


def run() -> dict[str, Any]:
    try:
        api = importlib.import_module("playwright.sync_api")  # optional: absent means NOT_RUN
    except ImportError:
        return {"status": "NOT_RUN", "reason": "Playwright is not installed (the visual or hci extra)"}
    results, failures = [], []
    with api.sync_playwright() as playwright:
        try:
            browser = _browser(api, playwright)
        except api.Error as error:
            return {"status": "NOT_RUN", "reason": f"no Chromium: {str(error).splitlines()[0]}"}
        page = browser.new_page()
        page.set_content("<html><body></body></html>")
        page.add_script_tag(content=VENDOR.read_text(encoding="utf-8"))
        for location in packs():
            pack = load_pack(location)
            text, _ = export_model("mermaid", pack, None, data_for(pack))
            theirs, ours = _theirs(page, text), _ours(text)
            agree = theirs == ours
            results.append({"pack": location.name, "agree": agree, "diagrams": sorted(theirs)})
            if not agree:
                failures.append({"pack": location.name, "mermaid": theirs, "playide": ours})
        loan = load_pack(ROOT / "packs" / "library-loan")  # vocab-ok: a negative control planted in one fixture pack's export
        base = export_model("mermaid", loan, None, data_for(loan))[0]
        controls = {name: not _agrees(page, api, change(base)) for name, change in CONTROLS.items()}
        browser.close()
    blind = sorted(name for name, caught in controls.items() if not caught)
    return {"status": "PASS" if not failures and not blind else "FAIL", "engine": "mermaid 12.0.0 (vendored)",
            "controls_caught": controls, "packs": results, "disagreements": failures}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m verification.interop.mermaid_oracle", description=__doc__.split("\n")[0])
    parser.add_argument("--out", type=Path, help="Write the JSON report here")
    args = parser.parse_args(argv)
    report = run()
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    say(f"mermaid oracle: {report['status']}" + (f" ({report.get('reason')})" if report.get("reason") else ""))
    return {"PASS": 0, "NOT_RUN": 3}.get(report["status"], 1)


if __name__ == "__main__":
    raise SystemExit(main())
