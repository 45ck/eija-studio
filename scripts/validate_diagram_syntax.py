#!/usr/bin/env python3
"""Check that generated diagram text is accepted by the real renderers (release evidence, not a unit test).

  mermaid   the vendored mermaid.min.js, run in installed Google Chrome via Playwright: parse AND render
  plantuml  `java -jar plantuml.jar -syntax` (jar path: --plantuml-jar or $EIJA_PLANTUML_JAR)
  dot       pydot's DOT grammar; additionally Graphviz `dot -Tsvg` when it is on PATH

A missing prerequisite (Chrome, Playwright, Java, the jar, pydot) is reported NOT_RUN for that renderer,
never PASS. Exit code: 0 all requested renderers PASS or NOT_RUN, 1 any FAIL. `--require` turns NOT_RUN
into exit code 3 for callers that need evidence.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from eija_studio.application.diagram_catalog import VIEW_FORMATS, VIEWS, demo_pair, render_view  # noqa: E402
from eija_studio.domain.models import Workflow  # noqa: E402

MERMAID_JS = ROOT / "src" / "eija_studio" / "resources" / "web" / "vendor" / "mermaid.min.js"
CHROME = [Path(p) for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe")]


def hostile_workflow() -> Workflow:
    """Names a hostile or careless model file could contain; escaping must keep them inert."""
    def t(i: str, a: str, f: str, to: str, role: str):
        guards = ["actor_active", "role_current", "state_equals", "expected_version", "operation_binding"]
        return {"id": i, "action": a, "from_state": f, "to_state": to, "role": role, "guards": guards,
                "required_effects": ["Audit:X"], "forbidden_effects": []}
    return Workflow.model_validate({"initial_state": "start", "states": ["start", 'end', 'a "quoted" <b>x</b>', "semi;colon #hash", "{brace}"],
        "transitions": [t("T-1", "Go", "start", "end", "Teacher"), t("T-2", 'Say "hi"; <i>', "end", 'a "quoted" <b>x</b>', "Reg;Role"),
                        t("T-3", "Next", "semi;colon #hash", "{brace}", "Teacher")]})


def corpus() -> dict[str, dict[str, str]]:
    """{format: {name: text}} for every view/format pair emitted, for the demo pair and a hostile model."""
    before, after = demo_pair()
    hostile = hostile_workflow()
    out: dict[str, dict[str, str]] = {"mermaid": {}, "plantuml": {}, "dot": {}}
    for fmt in out:
        for view in VIEWS:
            if fmt not in VIEW_FORMATS[view]:
                continue
            if view == "sequence":
                for t in after.transitions:
                    out[fmt][f"demo/sequence-{t.action}"] = render_view(view, fmt, before, after, t.action)
                out[fmt]["hostile/sequence"] = render_view(view, fmt, hostile, None, 'Say "hi"; <i>')
            else:
                out[fmt][f"demo/{view}"] = render_view(view, fmt, before, after)
                if view in {"state", "journey"}:
                    out[fmt][f"hostile/{view}"] = render_view(view, fmt, hostile)
    return out


def check_mermaid(texts: dict[str, str]) -> dict:
    chrome = next((str(p) for p in CHROME if p.is_file()), None)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"status": "NOT_RUN", "reason": "playwright is not installed"}
    if chrome is None:
        return {"status": "NOT_RUN", "reason": "Google Chrome not found"}
    failures = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=chrome, headless=True)
        page = browser.new_page()
        page.set_content("<!doctype html><html><body><div id='out'></div></body></html>")
        page.add_script_tag(path=str(MERMAID_JS))
        page.evaluate("mermaid.initialize({startOnLoad:false, securityLevel:'strict', htmlLabels:false})")
        for i, (name, text) in enumerate(sorted(texts.items())):
            error = page.evaluate("""async ([id, text]) => {
                try { await mermaid.parse(text); const r = await mermaid.render(id, text);
                      return r.svg.includes('Syntax error') ? 'rendered an error diagram' : ''; }
                catch (e) { return String(e && e.message || e); } }""", [f"d{i}", text])
            if error:
                failures[name] = error[:400]
        version = json.loads(MERMAID_JS.with_name("mermaid.VENDOR.json").read_text(encoding="utf-8"))["version"]
        browser.close()
    return {"status": "FAIL" if failures else "PASS", "checked": len(texts), "failures": failures, "renderer": f"vendored mermaid {version} in installed Chrome"}


def check_plantuml(texts: dict[str, str], jar: str | None) -> dict:
    jar = jar or os.environ.get("EIJA_PLANTUML_JAR")
    if not jar or not Path(jar).is_file():
        return {"status": "NOT_RUN", "reason": "no PlantUML jar (pass --plantuml-jar or set EIJA_PLANTUML_JAR)"}
    if shutil.which("java") is None:
        return {"status": "NOT_RUN", "reason": "java is not on PATH"}
    failures = {}
    for name, text in sorted(texts.items()):
        run = subprocess.run(["java", "-Djava.awt.headless=true", "-jar", jar, "-charset", "UTF-8", "-syntax"], input=text, text=True,
                             capture_output=True, encoding="utf-8", timeout=120)
        if run.returncode != 0 or run.stdout.startswith("ERROR"):
            failures[name] = (run.stdout or run.stderr)[:400]
    return {"status": "FAIL" if failures else "PASS", "checked": len(texts), "failures": failures, "renderer": "PlantUML -syntax"}


def check_dot(texts: dict[str, str]) -> dict:
    try:
        import pydot
    except ImportError:
        return {"status": "NOT_RUN", "reason": "pydot is not installed"}
    failures = {}
    dot = shutil.which("dot")
    for name, text in sorted(texts.items()):
        try:
            graphs = pydot.graph_from_dot_data(text)
            if not graphs:
                failures[name] = "pydot parsed no graph"
        except Exception as exc:  # noqa: BLE001 - any parse failure is a finding
            failures[name] = str(exc)[:400]
            continue
        if dot:
            run = subprocess.run([dot, "-Tsvg"], input=text, text=True, capture_output=True, encoding="utf-8")
            if run.returncode != 0:
                failures[name] = run.stderr[:400]
    return {"status": "FAIL" if failures else "PASS", "checked": len(texts), "failures": failures,
            "renderer": "pydot grammar" + (" + graphviz dot" if dot else " (graphviz `dot` not on PATH: layout not exercised)")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plantuml-jar")
    parser.add_argument("--require", action="store_true", help="exit 3 when any renderer is NOT_RUN")
    args = parser.parse_args()
    texts = corpus()
    report = {"mermaid": check_mermaid(texts["mermaid"]), "plantuml": check_plantuml(texts["plantuml"], args.plantuml_jar),
              "dot": check_dot(texts["dot"])}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if any(r["status"] == "FAIL" for r in report.values()):
        return 1
    return 3 if args.require and any(r["status"] == "NOT_RUN" for r in report.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
