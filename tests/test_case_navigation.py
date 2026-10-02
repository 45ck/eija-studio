"""Execute the actual case-list and loader code with isolated DOM/server doubles."""
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
const source = fs.readFileSync(process.argv[1], "utf8"), scenario = process.argv[2];
class Element {
  constructor() {this.children = []; this.textContent = "";}
  append(...children) {this.children.push(...children);}
  replaceChildren(...children) {this.children = children;}
}
const elements = new Map(), get = id => {
  if (!elements.has(id)) elements.set(id, new Element());
  return elements.get(id);
};
get("runtime-result").textContent = "Committed: Submit. Effects: audit";
const target = scenario === "same" ? "case-a" : "case-b", errors = [], renders = [];
const sandbox = {
  current: {case: {id: "case-a", version: 2}}, instance: {id: "preview-a", state: "Submitted"},
  $: get, el: () => new Element(), notice: () => {},
  task: async action => {try {await action();} catch(error) {errors.push(error.message);}},
  api: async path => {
    if (path === "cases") return [{id: target, request: "Synthetic navigation target", stage: "PREVIEW"}];
    if (scenario === "failed") throw new Error("The next case could not be loaded");
    return {case: {id: target, version: 3}};
  },
  render: () => renders.push({caseId: sandbox.current.case.id, instance: sandbox.instance,
                             result: get("runtime-result").textContent})
};
vm.createContext(sandbox);
vm.runInContext(source.slice(source.indexOf("async function cases("), source.indexOf("function switchTab(")), sandbox);
vm.runInContext(source.slice(source.indexOf("async function load("), source.indexOf("async function command(")), sandbox);
(async () => {
  await sandbox.cases();
  await get("case-list").children[0].onclick();
  process.stdout.write(JSON.stringify({caseId: sandbox.current.case.id, instance: sandbox.instance,
    result: get("runtime-result").textContent, errors, renders}));
})().catch(error => {process.stderr.write(String(error)); process.exitCode = 1;});
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="NOT_RUN: Node is required for client-code regression")
@pytest.mark.parametrize("scenario", ["failed", "different", "same"])
def test_case_navigation_preserves_preview_until_a_different_case_loads(scenario):
    node = shutil.which("node")
    assert node is not None
    result = run_bounded([*resolve_command(node), "-e", SCRIPT, str(APP), scenario],
                         input=None, env=dict(os.environ), timeout=10)
    assert result.returncode == 0, result.stdout + result.stderr
    observed = json.loads(result.stdout)
    if scenario == "different":
        assert observed["caseId"] == "case-b"
        assert observed["instance"] is None
        assert observed["result"] == ""
        assert observed["renders"] == [{"caseId": "case-b", "instance": None, "result": ""}]
    else:
        assert observed["caseId"] == "case-a"
        assert observed["instance"] == {"id": "preview-a", "state": "Submitted"}
        assert observed["result"] == "Committed: Submit. Effects: audit"
    if scenario == "failed":
        assert observed["errors"] == ["The next case could not be loaded"]
        assert observed["renders"] == []
    else:
        assert observed["errors"] == []
        assert len(observed["renders"]) == 1
