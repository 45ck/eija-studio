#!/usr/bin/env python3
"""Check that generated diagram text is accepted by the real renderers (release evidence, not a unit test).

  mermaid   the vendored mermaid.min.js, run in installed Google Chrome via Playwright: parse AND render
  plantuml  `java -jar plantuml.jar -syntax` (jar path: --plantuml-jar or $EIJA_PLANTUML_JAR)
  dot       pydot's DOT grammar; additionally Graphviz `dot -Tsvg` when it is on PATH

A missing prerequisite (Chrome, Playwright, Java, the jar, pydot) is reported NOT_RUN for that renderer,
never PASS. Exit code: 1 any FAIL; 3 any NOT_RUN unless `--allow-not-run`; else 0. The release gate
(quality/sessions/visual.py) therefore fails when a renderer could not run, and dev machines opt out
explicitly with `--allow-not-run` (the JSON still says NOT_RUN).
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
from eija_studio.application.diagram_catalog import VIEW_FORMATS, VIEWS, demo_pair, render_view
from eija_studio.domain.models import Workflow

MERMAID_JS = ROOT / "src" / "eija_studio" / "resources" / "web" / "vendor" / "mermaid.min.js"


HOSTILE_ACTION = 'Say "hi"; <i>'
# Text a hostile or careless model file could carry. PlantUML evaluates `%name(...)` in labels (verified
# with 1.2025.4: %getenv read an environment variable, %load_json read a local file), so those are here too.
HOSTILE_STATES = ("start", "end", 'a "quoted" <b>x</b>', "semi;colon #hash", "{brace}", "%getenv(PLANTUML_SECRETVAR)",
                  "%load_json(secret.json)", "!include secret.puml", "%%{init: {}}%%",
                  "tail:", ":::cls", "`tick")  # Mermaid: a trailing colon, `:::` and a leading backtick break the parse unescaped
MARKER = "TOPSECRET-eija-hostile"  # value of PLANTUML_SECRETVAR in the injection check; must never reach output


def hostile_workflow() -> Workflow:
    """One shared hostile fixture (tests and this validator): escaping must keep every name inert."""
    def t(i: str, a: str, f: str, to: str, role: str):
        guards = ["actor_active", "role_current", "state_equals", "expected_version", "operation_binding"]
        return {"id": i, "action": a, "from_state": f, "to_state": to, "role": role, "guards": guards,
                "required_effects": ["Audit:X"], "forbidden_effects": []}
    return Workflow.model_validate({"id": "hostile", "initial_state": "start", "states": list(HOSTILE_STATES), "transitions": [
        t("T-1", "Go", "start", "end", "Teacher"), t("T-2", HOSTILE_ACTION, "end", 'a "quoted" <b>x</b>', "Reg;Role"),
        t("T-3", "Next", "semi;colon #hash", "{brace}", "Teacher"), t("T-4", "%date()", "{brace}", "%getenv(PLANTUML_SECRETVAR)", "%version()"),
        t("T-5", "Load", "%load_json(secret.json)", "!include secret.puml", "Teacher"), t("T-6", "Init", "%%{init: {}}%%", "start", "Teacher"),
        t("T-7", "colon:", "tail:", ":::cls", "`r"), t("T-8", "`tick action", ":::cls", "`tick", "Role:")]})


def hostile_candidate() -> Workflow:
    """A candidate of the hostile model (initial state moved, a role and a guard changed, one action removed),
    so the diff and ripple views also carry hostile names and the `~`, `+ start` and `- start` labels."""
    data = hostile_workflow().model_dump(mode="json")
    data["initial_state"] = "end"
    data["transitions"] = [t for t in data["transitions"] if t["id"] != "T-8"]
    for t in data["transitions"]:
        if t["id"] == "T-1":
            t["role"] = "Registrar"
        if t["id"] == "T-2":
            t["guards"] = [*t["guards"], "actor_assigned"]
    return Workflow.model_validate(data)


def corpus() -> dict[str, dict[str, str]]:
    """{format: {name: text}} for every view/format pair emitted, for the demo pair and a hostile model."""
    before, after = demo_pair()
    hostile, moved = hostile_workflow(), hostile_candidate()
    out: dict[str, dict[str, str]] = {"mermaid": {}, "plantuml": {}, "dot": {}}
    for fmt, bucket in out.items():
        for view in VIEWS:
            if fmt not in VIEW_FORMATS[view]:
                continue
            if view == "sequence":
                for t in after.transitions:
                    bucket[f"demo/sequence-{t.action}"] = render_view(view, fmt, before, after, t.action)
                bucket["hostile/sequence"] = render_view(view, fmt, hostile, None, HOSTILE_ACTION)
            else:
                bucket[f"demo/{view}"] = render_view(view, fmt, before, after)
                if view in {"state", "journey"}:
                    bucket[f"hostile/{view}"] = render_view(view, fmt, hostile)
                if view in {"diff", "impact"}:
                    bucket[f"hostile/{view}"] = render_view(view, fmt, hostile, moved)
    return out


def launch_chrome(playwright):
    """The installed Google Chrome, found by Playwright's `channel="chrome"` on every OS; None when absent."""
    from playwright.sync_api import Error
    try:
        return playwright.chromium.launch(channel="chrome", headless=True)
    except Error:
        return None


def check_mermaid(texts: dict[str, str]) -> dict:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"status": "NOT_RUN", "reason": "playwright is not installed"}
    failures = {}
    with sync_playwright() as p:
        browser = launch_chrome(p)
        if browser is None:
            return {"status": "NOT_RUN", "reason": "Google Chrome not found (Playwright channel 'chrome')"}
        page = browser.new_page()
        page.set_content("<!doctype html><html><body><div id='out'></div></body></html>")
        page.add_script_tag(path=str(MERMAID_JS))
        # The options the Studio frame and the standalone HTML page use, so what is checked is what ships.
        page.evaluate("mermaid.initialize({startOnLoad:false, securityLevel:'strict', htmlLabels:true, theme:'default'})")
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
    """`-syntax` on every text, plus an injection check: the hostile diagrams are rendered with
    PLANTUML_SECRETVAR set and the value must not appear in the output (PlantUML would evaluate an
    unescaped `%getenv(...)` label). The jar is used as found and is NOT pinned; its version is reported."""
    jar = jar or os.environ.get("EIJA_PLANTUML_JAR")
    if not jar or not Path(jar).is_file():
        return {"status": "NOT_RUN", "reason": "no PlantUML jar (pass --plantuml-jar or set EIJA_PLANTUML_JAR)"}
    if shutil.which("java") is None:
        return {"status": "NOT_RUN", "reason": "java is not on PATH"}
    base = ["java", "-Djava.awt.headless=true", "-jar", jar, "-charset", "UTF-8"]
    version = subprocess.run([*base, "-version"], text=True, capture_output=True, encoding="utf-8", errors="replace", timeout=120).stdout.splitlines()
    failures = {}
    env = os.environ | {"PLANTUML_SECRETVAR": MARKER}
    for name, text in sorted(texts.items()):
        run = subprocess.run([*base, "-syntax"], input=text, text=True, capture_output=True, encoding="utf-8", errors="replace", timeout=120, env=env)
        if run.returncode != 0 or run.stdout.startswith("ERROR"):
            failures[name] = (run.stdout or run.stderr)[:400]
        elif name.startswith("hostile/"):
            shown = subprocess.run([*base, "-ttxt", "-pipe"], input=text, text=True, capture_output=True, encoding="utf-8", errors="replace", timeout=120, env=env)
            if MARKER in shown.stdout + shown.stderr:
                failures[name] = "PlantUML evaluated a label: the environment marker reached the output"
    return {"status": "FAIL" if failures else "PASS", "checked": len(texts), "failures": failures,
            "renderer": "PlantUML -syntax, jar not pinned: " + " ".join(version[:1])}


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
        except Exception as exc:
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
    parser.add_argument("--allow-not-run", action="store_true", help="exit 0 although a renderer is NOT_RUN (dev machines only)")
    args = parser.parse_args()
    texts = corpus()
    report = {"mermaid": check_mermaid(texts["mermaid"]), "plantuml": check_plantuml(texts["plantuml"], args.plantuml_jar),
              "dot": check_dot(texts["dot"])}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if any(r["status"] == "FAIL" for r in report.values()):
        return 1
    not_run = [k for k, r in report.items() if r["status"] == "NOT_RUN"]
    if not_run:
        print("NOT_RUN: " + ", ".join(not_run) + (" (allowed)" if args.allow_not_run else ": this is not a pass"), file=sys.stderr)
    return 3 if not_run and not args.allow_not_run else 0


if __name__ == "__main__":
    raise SystemExit(main())
