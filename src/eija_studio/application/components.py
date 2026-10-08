"""The component diagram of an app built from the model (ADR-0155), extracted from the generated files themselves.

Nothing here is a description someone wrote: components are the generated modules, the EIJA modules they import and the
infrastructure they use; each dependency is an import statement, a page request to a route the server serves, or a
module reading a generated file by name. Each provider's interface is the set of names its users import from it. So
the diagram changes when the generated code changes, and cannot claim a dependency the code does not have.

Pure: parses text with `ast` and regular expressions, never imports or runs the generated code.
"""
from __future__ import annotations

import ast
import re
from typing import Any

FORMAT = "eija.components.v1"
INFRASTRUCTURE = {"sqlite3": ("SQLite", "database"), "http.server": ("HTTP server (standard library)", "framework")}
PAGE = "app/web"  # the browser page: index.html, app.js and app.css together
ROUTE = re.compile(r"/api/[a-z]+")


def _module(path: str) -> str:
    return path.removesuffix(".py").removesuffix("/__init__").replace("/", ".")


def _absolute(module: str, node: ast.ImportFrom) -> str:
    if not node.level:
        return node.module or ""
    package = module.split(".")[: -node.level]
    return ".".join([*package, node.module] if node.module else package)


def _imports(module: str, source: str) -> list[tuple[str, list[str]]]:
    """(imported module, names) for each import statement, relative imports made absolute."""
    found: list[tuple[str, list[str]]] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ImportFrom) and node.module != "__future__":
            found.append((_absolute(module, node), sorted(a.name for a in node.names)))
        elif isinstance(node, ast.Import):
            found.extend((a.name, []) for a in node.names)
    return found


def _kind(module: str, generated: set[str]) -> tuple[str, str] | None:
    """(name, stereotype) for an import worth drawing, or None for utility modules (json, re, pathlib, ...)."""
    if module in generated:
        return None  # drawn already
    if module.startswith("eija_studio."):
        return "EIJA " + module.removeprefix("eija_studio.").replace(".", " "), "kernel"
    return INFRASTRUCTURE.get(module)


def _stereotype(path: str) -> str:
    return "test" if path.startswith("tests/") else "executable" if path == "run.py" else "component"


class _Diagram:
    def __init__(self) -> None:
        self.components: dict[str, dict[str, Any]] = {}
        self.uses: dict[tuple[str, str], set[str]] = {}
        self.ignored: set[str] = set()

    def component(self, cid: str, name: str, stereotype: str, files: list[str] | None = None, lines: int = 0) -> None:
        self.components.setdefault(cid, {"id": cid, "name": name, "stereotype": stereotype, "files": files or [], "lines": lines})

    def use(self, source: str, target: str, names: list[str]) -> None:
        self.uses.setdefault((source, target), set()).update(names)


def _link(diagram: _Diagram, module: str, target: str, names: list[str], modules: dict[str, str]) -> None:
    """One import: to a generated module (or a submodule imported by name), to EIJA or infrastructure, or not drawn."""
    submodules = [f"{target}.{n}" for n in names if f"{target}.{n}" in modules]  # `from app import service`
    if submodules:
        for sub in submodules:
            diagram.use(module, sub, ["(module)"])
    elif target in modules:
        diagram.use(module, target, names)
    elif (kind := _kind(target, set(modules))) is not None:
        diagram.component(target, *kind)
        diagram.use(module, target, names)
    else:
        diagram.ignored.add(target.split(".", maxsplit=1)[0])


def _python(diagram: _Diagram, files: dict[str, str]) -> None:
    modules = {_module(p): p for p, text in files.items() if p.endswith(".py") and text.strip()}
    for module, path in sorted(modules.items()):
        diagram.component(module, module, _stereotype(path), [path], len(files[path].splitlines()))
    for module, path in sorted(modules.items()):
        for target, names in _imports(module, files[path]):
            _link(diagram, module, target, names, modules)


def _artifacts(diagram: _Diagram, files: dict[str, str]) -> None:
    """Generated JSON documents, and the modules that read them by file name."""
    for path in sorted(p for p in files if p.endswith(".json")):
        diagram.component(path, path.rsplit("/", 1)[-1], "artifact", [path], 0)
        for reader in [c for c in diagram.components.values() if c["files"] and c["files"][0].endswith(".py")]:
            if f'"{path.rsplit("/", 1)[-1]}"' in files[reader["files"][0]]:
                diagram.use(reader["id"], path, ["reads"])


def _page(diagram: _Diagram, files: dict[str, str]) -> list[str]:
    """The browser page and the server routes it calls. Returns routes the page calls that the server does not serve."""
    page = sorted(p for p in files if p.startswith(PAGE + "/"))
    if not page or "app/server.py" not in files:
        return []
    diagram.component(PAGE, "Web page", "browser", page, sum(len(files[p].splitlines()) for p in page))
    served = set(ROUTE.findall(files["app/server.py"]))
    called = set(ROUTE.findall(files.get(PAGE + "/app.js", "")))
    diagram.use(PAGE, "app.server", sorted(called & served))
    if any(f'"{p.rsplit("/", 1)[-1]}"' in files["app/server.py"] for p in page):
        diagram.use("app.server", PAGE, ["serves"])
    return sorted(called - served)


def app_components(files: dict[str, str]) -> dict[str, Any]:
    """Components, interfaces and dependencies of a generated app, read from its files (`app_files` output)."""
    diagram = _Diagram()
    _python(diagram, files)
    unserved = _page(diagram, files)
    _artifacts(diagram, files)
    provided: dict[str, set[str]] = {}
    for (_, target), names in diagram.uses.items():
        imported = names - {"reads", "serves"}  # file reads and serving are dependencies, not provided interfaces
        if imported:
            provided.setdefault(target, set()).update(imported)
    return {
        "format": FORMAT,
        "components": sorted(diagram.components.values(), key=lambda c: c["id"]),
        "interfaces": [{"provider": t, "names": sorted(n)} for t, n in sorted(provided.items())],
        "dependencies": [{"source": s, "target": t, "names": sorted(n)} for (s, t), n in sorted(diagram.uses.items())],
        "unserved_routes": unserved,
        "not_drawn": sorted(diagram.ignored),
    }
