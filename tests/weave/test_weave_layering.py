"""The weave package imports the standard library, pydantic (through the pack) and eija_studio.domain only.

It does not import application, adapters, bootstrap or interfaces: the CLI in ``interfaces`` calls into it, never the reverse.
Negative control: a planted import of the application layer is flagged.
"""
from __future__ import annotations

import ast

from weave_support import ROOT

ALLOWED = ("eija_studio.domain", "eija_studio.weave")


def offending(source: str) -> list[str]:
    bad: list[str] = []
    for node in ast.walk(ast.parse(source)):
        names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""] if isinstance(node, ast.ImportFrom) and node.level == 0 else []
        bad += [n for n in names if n.startswith("eija_studio") and n != "eija_studio" and not n.startswith(ALLOWED)]
    return bad


def test_weave_imports_only_domain() -> None:
    files = sorted((ROOT / "src" / "eija_studio" / "weave").glob("*.py"))
    assert len(files) >= 10
    assert {f.name: offending(f.read_text(encoding="utf-8")) for f in files if offending(f.read_text(encoding="utf-8"))} == {}


def test_negative_control_an_application_import_is_flagged() -> None:
    assert offending("from eija_studio.application.diagrams import state_graph\n") == ["eija_studio.application.diagrams"]
    assert offending("import eija_studio.adapters.sqlite_store\n") == ["eija_studio.adapters.sqlite_store"]
    assert offending("from eija_studio.domain.pack import Pack\nfrom eija_studio import __version__\n") == []
