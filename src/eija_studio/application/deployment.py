"""The deployment diagram of an app built from the model (ADR-0206), read from the generated files themselves.

As with the component diagram (ADR-0155), nothing here is a description someone wrote. The nodes are where the
generated files run: the browser that loads the page, the Python process that `run.py` starts, and the SQLite database
file that process opens, all on one computer. The address, port and database path are the defaults `run.py` and
`app/server.py` declare, with the option and environment variable that change them. Each communication path is an
HTTP route the page calls and the server serves, or the `sqlite3` connection; each artifact is a group of generated
files, plus the installed EIJA package the app imports.

Pure: parses text with `ast` and regular expressions, never imports or runs the generated code.
"""
from __future__ import annotations

import ast
import re
from typing import Any

FORMAT = "eija.deployment.v1"
HOST = re.compile(r"ThreadingHTTPServer\(\(\s*\"([^\"]+)\"")
ROUTE = re.compile(r"/api/[a-z]+")
PAGE = "app/web"


def _literal(node: ast.expr | None) -> str | None:
    """The text a default comes to, as far as its constants show: `int(os.environ.get("PORT", "8000"))` is 8000, and
    `Path(__file__).resolve().parent / "data" / "app.sqlite3"` is data/app.sqlite3 (beside run.py)."""
    if isinstance(node, ast.Constant):
        return str(node.value)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        anchor = not isinstance(node.left, ast.BinOp) and "__file__" in ast.unparse(node.left)  # the folder of run.py
        parts = [None if anchor else _literal(node.left), _literal(node.right)]
        return "/".join(p for p in parts if p)
    if isinstance(node, ast.Call):
        return next((v for v in map(_literal, reversed(node.args)) if v is not None), None)
    return None


def _environment(node: ast.expr | None) -> str | None:
    """The environment variable a default reads, if any (`os.environ.get("PORT", ...)`)."""
    calls = [n for n in ast.walk(node) if isinstance(n, ast.Call) and ast.unparse(n.func).endswith("environ.get") and n.args] if node else []
    return _literal(calls[0].args[0]) if calls else None


def _options(run: str) -> dict[str, dict[str, str | None]]:
    """Each option run.py declares: its default and the environment variable that sets the default."""
    options = {}
    for node in ast.walk(ast.parse(run)):
        if isinstance(node, ast.Call) and ast.unparse(node.func).endswith("add_argument") and node.args:
            default = next((k.value for k in node.keywords if k.arg == "default"), None)
            options[_literal(node.args[0]) or ""] = {"default": _literal(default), "environment": _environment(default)}
    return options


def _group(files: dict[str, str], prefix: str, suffix: str) -> list[str]:
    return sorted(p for p in files if p.startswith(prefix) and p.endswith(suffix) and files[p].strip())


def _nodes(files: dict[str, str], options: dict[str, dict[str, str | None]], kernel: str) -> list[dict[str, Any]]:
    host = HOST.search(files.get("app/server.py", ""))
    port, data = options.get("--port", {}), options.get("--data", {})
    page = _group(files, PAGE + "/", "")
    process = {"id": "node:process", "name": "Python process", "stereotype": "executionEnvironment",
               "address": f"{host.group(1) if host else 'unknown host'}:{port.get('default') or 'unknown port'}",
               "set_by": [x for x in ("--port", port.get("environment")) if x and "--port" in options],
               "artifacts": [{"name": "run.py", "files": ["run.py"]},
                             {"name": "app (generated package)", "files": [p for p in _group(files, "app/", ".py") if not p.startswith(PAGE)]},
                             {"name": "model files", "files": _group(files, "app/", ".json")},
                             {"name": f"eija_studio {kernel} (installed)", "files": []}]}
    nodes = [{"id": "node:browser", "name": "Web browser", "stereotype": "executionEnvironment", "address": None, "set_by": [],
              "artifacts": [{"name": "Web page", "files": page}]}] if page else []
    nodes.append(process)
    if any("import sqlite3" in text for text in files.values()):
        nodes.append({"id": "node:database", "name": (data.get("default") or "database").rsplit("/", 1)[-1], "stereotype": "artifact",
                      "address": data.get("default"), "set_by": ["--data"] if "--data" in options else [], "artifacts": []})
    return nodes


def _paths(files: dict[str, str], nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ids = {n["id"] for n in nodes}
    served = set(ROUTE.findall(files.get("app/server.py", "")))
    called = set(ROUTE.findall(files.get(PAGE + "/app.js", "")))
    paths = []
    if "node:browser" in ids and served:
        paths.append({"source": "node:browser", "target": "node:process", "protocol": "HTTP", "names": sorted(called & served)})
    if "node:database" in ids:
        paths.append({"source": "node:process", "target": "node:database", "protocol": "sqlite3", "names": []})
    return paths


def app_deployment(files: dict[str, str], kernel: str) -> dict[str, Any]:
    """Where a generated app runs (`app_files` output), with `kernel` the installed eija_studio version it imports."""
    options = _options(files.get("run.py", ""))
    nodes = _nodes(files, options, kernel)
    return {
        "format": FORMAT,
        "device": "This computer",
        "nodes": nodes,
        "paths": _paths(files, nodes),
        "start": "python run.py" + "".join(f" [{flag} …]" for flag in sorted(options)),
        "limits": ["One process and one database file per workflow: two workflows that share a class keep two copies of it, "
                   "and nothing is shared at run time until workflows send each other messages (#93)."],
    }
