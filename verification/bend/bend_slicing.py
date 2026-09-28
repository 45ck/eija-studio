"""Split ``LAWS.bend`` / ``PROOF.bend`` per law, so a failing proof can be attributed to one law.

``bend PROOF.bend`` reports the first failure of the whole file, and a failing shared lemma fails
every law that shares the file. To say *which laws* an unsafe model breaks, the runner checks one law
at a time: ``LAWS.bend`` keeps its vocabulary and only the chosen ``law``; ``PROOF.bend`` keeps only
the proof of that law and the lemmas it (transitively) uses. Slicing changes no proof text.

What this establishes: a per-law verdict from Bend itself. What it does NOT establish: anything Bend
did not check; a sliced run is weaker than the full run and is never used as the passing verdict
(the full ``bend PROOF.bend --verdict`` run is).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_ITEM = re.compile(r"^(?P<kind>def|law|type|import|@unsafe)\b(?P<rest>.*)$")
_NAME = {"def": re.compile(r"^def\s+([^\s(:]+)"), "law": re.compile(r"^law\s+([^\s:]+)"),
         "type": re.compile(r"^type\s+([A-Za-z0-9_.]+)")}
_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_.]*")


@dataclass(frozen=True)
class Item:
    kind: str
    name: str
    text: str  # includes the comment block that precedes the item


def parse_items(source: str) -> list[Item]:
    """Top-level items of a Bend file. Comments and blank lines attach to the next item."""
    items: list[Item] = []
    pending: list[str] = []
    current: list[str] | None = None
    kind = name = ""

    def close() -> None:
        nonlocal current
        if current is not None:
            items.append(Item(kind, name, "".join(current).rstrip("\n") + "\n"))
            current = None

    for line in source.splitlines(keepends=True):
        m = _ITEM.match(line)
        if m:
            close()
            kind = m.group("kind")
            pattern = _NAME.get(kind)
            found = pattern.match(line) if pattern else None
            name = found.group(1) if found else line.strip()
            current = [*pending, line]
            pending = []
        elif current is not None and (line.startswith((" ", "\t")) or not line.strip()):
            current.append(line)
        else:  # a col-0 comment (or stray text) belongs to whatever follows
            close()
            pending.append(line)
    close()
    return items


def law_names(laws_source: str) -> list[str]:
    return [i.name for i in parse_items(laws_source) if i.kind == "law"]


def law_comments(laws_source: str) -> dict[str, str]:
    """The comment block directly above each law (its plain-language statement)."""
    out: dict[str, str] = {}
    for item in parse_items(laws_source):
        if item.kind != "law":
            continue
        lines = item.text.splitlines()
        at = next(i for i, ln in enumerate(lines) if ln.startswith("law "))
        block: list[str] = []
        for ln in reversed(lines[:at]):
            if not ln.startswith("#"):
                break
            block.append(ln.lstrip("# ").rstrip())
        out[item.name] = " ".join(c for c in reversed(block) if c)
    return out


def proof_names(proof_source: str, alias: str = "Laws") -> set[str]:
    prefix = alias + "."
    return {i.name[len(prefix):] for i in parse_items(proof_source) if i.kind == "def" and i.name.startswith(prefix)}


def slice_for_law(laws_source: str, proof_source: str, law: str, alias: str = "Laws") -> tuple[str, str]:
    """(LAWS.bend, PROOF.bend) texts containing only ``law`` and the proof machinery it needs."""
    laws_items = parse_items(laws_source)
    names = {i.name for i in laws_items if i.kind == "law"}
    if law not in names:
        raise KeyError(f"no law named {law!r}")
    laws_text = "".join(i.text + "\n" for i in laws_items if i.kind != "law" or i.name == law)

    proof_items = parse_items(proof_source)
    proofs = {alias + "." + n for n in names}
    local = {i.name: i for i in proof_items if i.kind == "def" and i.name not in proofs}
    target = alias + "." + law
    wanted = next((i for i in proof_items if i.name == target), None)
    if wanted is None:
        raise KeyError(f"PROOF.bend has no proof named {target}")
    needed: set[str] = set()
    stack = [wanted]
    while stack:
        item = stack.pop()
        for ident in _IDENT.findall(item.text):
            dep = local.get(ident)
            if dep is not None and dep.name not in needed:
                needed.add(dep.name)
                stack.append(dep)
    keep = [i for i in proof_items if i.kind == "import" or i.name in needed or i is wanted]
    return laws_text, "".join(i.text + "\n" for i in keep)
