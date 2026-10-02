"""Actual navigation handlers with isolated DOM/server doubles; not browser evidence.

Adapted from 45ck/eija-studio PR #68, commit
8cb646e600d44612b84fb0d60f81e9423d476111. Extend its list/load regression
to this workbench's selector, creation path and affordance prerequisite.
"""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import pytest

from eija_studio.adapters.providers.process import resolve_command, run_bounded

APP = Path(__file__).resolve().parents[1] / "src/eija_studio/resources/web/app.js"
SCRIPT = r"""
const fs = require("node:fs"), vm = require("node:vm");
const source = fs.readFileSync(process.argv[1], "utf8"), route = process.argv[2], scenario = process.argv[3];
class Element {
  constructor() {this.children = []; this.textContent = ""; this.dataset = {}; this.value = "";}
  append(...children) {this.children.push(...children);}
  replaceChildren(...children) {this.children = children;}
  setAttribute() {}
  removeAttribute() {}
}
const elements = new Map(), get = id => {
  if (!elements.has(id)) elements.set(id, new Element());
  return elements.get(id);
};
get("runtime-result").textContent = "Committed: Submit. Effects: audit";
const target = scenario === "same" ? "case-a" : "case-b", errors = [], renders = [], requests = [];
let pending;
const sandbox = {
  current: {case: {id: "case-a", version: 2}}, instance: {id: "preview-a", state: "Submitted"},
  busy: scenario === "busy",
  tab: "model", editId: "TR-SUBMIT", inspectorSelection: {kind:"transition", id:"TR-SUBMIT"},
  modelView: "working", historyModel: null, historyLabel: "", canvasDirection: "AUTO", caseViews: new Map(),
  $: get, el: () => new Element(), notice: () => {}, clearDiagnostic: () => {}, openIntent: () => {},
  document: {querySelectorAll: () => [], body: new Element()},
  captureTaskFocus: () => ({}), restoreTaskFocus: () => {},
  reportError: error => errors.push(error.message),
  api: async (path, body) => {
    requests.push({path, method: body === undefined ? "GET" : "POST"});
    if (path === "cases") return body === undefined
      ? [{id: target, request: "Synthetic navigation target", stage: "PREVIEW"}] : {id: target};
    if (scenario === "case_failure" && path === "cases/" + target) throw new Error("Case fetch unavailable");
    if (scenario === "affordance_failure" && path.endsWith("/affordances")) {
      throw new Error("Affordance fetch unavailable");
    }
    if (path.endsWith("/affordances")) return {affordances: []};
    if (path.endsWith("/history")) return {case_id: target, status: "ready"};
    return {case: {id: target, version: 3}};
  },
  render: () => renders.push({caseId: sandbox.current.case.id, instance: sandbox.instance,
                             result: get("runtime-result").textContent})
};
vm.createContext(sandbox);
for (const [start, end] of [
  ["async function task(", "async function cases("],
  ["async function cases(", "function switchTab("],
  ["async function load(", "async function command("],
  ['$("create").onclick=', '$("propose").onclick='],
  ['$("case-switcher").onchange=', '$("canvas-direction").onchange=']
]) {
  const first = source.indexOf(start), last = source.indexOf(end, first);
  if (first < 0 || last < 0) throw new Error("Actual handler boundary missing: " + start);
  vm.runInContext(source.slice(first, last), sandbox);
}
// Observe the actual task's promise without replacing its busy guard or error handling.
const actualTask = sandbox.task;
sandbox.task = (...args) => pending = actualTask(...args);
(async () => {
  await sandbox.cases();
  if (route === "list") get("case-list").children[0].onclick();
  if (route === "selector") {
    get("case-switcher").value = target;
    get("case-switcher").onchange({target: get("case-switcher")});
  }
  if (route === "create") get("create").onclick();
  await pending;
  process.stdout.write(JSON.stringify({caseId: sandbox.current.case.id, instance: sandbox.instance,
    result: get("runtime-result").textContent, selector: get("case-switcher").value,
    errors, renders, requests}));
})().catch(error => {process.stderr.write(String(error)); process.exitCode = 1;});
"""

SCENARIOS = [(route, scenario) for route in ("list", "selector", "create")
             for scenario in ("case_failure", "affordance_failure", "different", "same")
             if not (route == "create" and scenario == "same")] + [("selector", "busy")]


@pytest.mark.skipif(shutil.which("node") is None, reason="NOT_RUN: Node required for client-code regression")
@pytest.mark.parametrize(("route", "scenario"), SCENARIOS)
def test_case_navigation_preserves_preview_until_a_different_case_loads(route, scenario):
    node = shutil.which("node")
    assert node is not None
    result = run_bounded([*resolve_command(node), "-e", SCRIPT, str(APP), route, scenario],
                         input=None, env=dict(os.environ), timeout=10)
    assert result.returncode == 0, result.stdout + result.stderr
    observed = json.loads(result.stdout)
    assert observed["selector"] == observed["caseId"], "The case selector must identify the displayed model and preview"
    if scenario == "different":
        assert observed["caseId"] == "case-b"
        assert observed["instance"] is None
        assert observed["result"] == ""
        assert observed["renders"] == [{"caseId": "case-b", "instance": None, "result": ""}]
    else:
        assert observed["caseId"] == "case-a"
        assert observed["instance"] == {"id": "preview-a", "state": "Submitted"}
        assert observed["result"] == "Committed: Submit. Effects: audit"
    if scenario.endswith("failure"):
        expected = "Case fetch unavailable" if scenario == "case_failure" else "Affordance fetch unavailable"
        assert observed["errors"] == [expected]
        assert observed["renders"] == []
    elif scenario == "busy":
        assert observed["errors"] == []
        assert observed["renders"] == []
        assert observed["requests"] == [{"path": "cases", "method": "GET"}], "Busy navigation must not start a request"
    else:
        assert observed["errors"] == []
        assert len(observed["renders"]) == 1
    posts = [request for request in observed["requests"] if request["method"] == "POST"]
    assert posts == ([{"path": "cases", "method": "POST"}] if route == "create" else [])
