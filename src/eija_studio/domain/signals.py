"""Signals between workflows (issue #93 item 5, ADR-0242): what makes a signal effect well formed.

A signal is an effect named `Signal:Name` that one workflow's step writes to its outbox for another workflow of the
system, named by its pack id in `recipient`. The receiving workflow says which signals start a record there
(`Workflow.receives`); the system landscape checks that both ends agree.
"""
from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

SIGNAL = re.compile(r"Signal:[A-Z][A-Za-z0-9]{0,59}")  # a signal effect's name


def signal_problems(pack_id: str, catalog: Iterable[Any]) -> list[str]:
    """A signal is named Signal:Name and goes to another workflow; nothing else may take a signal's name."""
    effects = list(catalog)
    found = [f"effects.catalog[{e.id}]: a signal is named Signal:Name and goes to another workflow" for e in effects
             if e.kind == "signal" and (not SIGNAL.fullmatch(e.id) or e.recipient == pack_id)]
    return found + [f"effects.catalog[{e.id}]: only a signal may be named Signal:" for e in effects
                    if e.kind != "signal" and e.id.startswith("Signal:")]
