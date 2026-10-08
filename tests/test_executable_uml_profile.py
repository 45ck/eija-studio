"""The executable UML semantics table (docs/architecture/executable-uml.md, ADR-0160) names every guard and change kind.

A guard or transaction kind added to the code without a row stating its meaning when it runs fails here, so the
supported semantics stay explicit.
"""
from __future__ import annotations

from pathlib import Path
from typing import get_args

from eija_studio.domain.models import Guard
from eija_studio.domain.transactions import TRANSACTION_KINDS

DOC = Path(__file__).resolve().parents[1] / "docs" / "architecture" / "executable-uml.md"


def _rows() -> str:
    return "\n".join(line for line in DOC.read_text(encoding="utf-8").splitlines() if line.startswith("|"))


def test_every_guard_has_a_stated_meaning():
    missing = [g for g in get_args(Guard) if f"Guard `{g}`" not in _rows()]
    assert missing == []


def test_every_change_kind_has_a_stated_meaning():
    missing = [k for k in TRANSACTION_KINDS if f"| `{k}` |" not in _rows()]
    assert missing == []
