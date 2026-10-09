"""The parts of PlantUML and Mermaid that read the same way: transitions, class members and associations (ADR-0190).

Both are line-oriented text with nearly the same arrows (`A --> B : label`, `A "1" *-- "1..*" B : role`) and member
lines (`+name : Type [1]` or `+Type name`). Each format module splits its own blocks and handles its own keywords,
then hands these lines here. Anything a line says that PlayIDE's vocabulary cannot hold becomes a skip on `Parsed`.
"""
from __future__ import annotations

import re
from collections.abc import Callable

from .model import Attr, Edge, Klass, Link, Parsed

INITIAL = "[*]"
_NAME = r'(?:\[\*\]|"[^"]+"|[^\s"]+)'
TRANSITION = re.compile(rf"^(?P<a>{_NAME})\s*-+(?:\[[^\]]*\])?(?:left|right|up|down|le|ri|l|r|u|d)?-*>\s*(?P<b>{_NAME})"
                        r"\s*(?::\s*(?P<label>.*))?$")
_MULT = r'(?:"(?P<{0}>[^"]*)")?'
RELATION = re.compile(rf'^(?P<a>[A-Za-z_][\w.]*)\s*{_MULT.format("ma")}\s*(?P<arrow>[<*o]?[|]?(?:--|\.\.)[|]?[>*o]?)\s*'
                      rf'{_MULT.format("mb")}\s*(?P<b>[A-Za-z_][\w.]*)\s*(?::\s*(?P<label>.*))?$')
_MEMBER_TYPED = re.compile(r"^(?P<name>[A-Za-z_]\w*)\s*:\s*(?P<type>[A-Za-z_][\w.]*)?\s*(?P<rest>.*)$")
_MEMBER_JAVA = re.compile(r"^(?P<type>[A-Za-z_][\w.]*)\s+(?P<name>[A-Za-z_]\w*)\s*(?P<rest>.*)$")
_BOUNDS = re.compile(r"\[\s*(?P<lo>\d+|\*)\s*(?:\.\.\s*(?P<hi>\d+|\*|n))?\s*\]")
_MAX = re.compile(r"maxLength\s*=\s*(?P<n>\d+)", re.IGNORECASE)


def unquote(name: str) -> str:
    return name[1:-1] if len(name) >= 2 and name[0] == name[-1] == '"' else name


def read_transition(line: str, where: str, parsed: Parsed, aliases: dict[str, str],
                    unescape: Callable[[str], str]) -> bool:
    """A `A --> B : label` line; `[*]` is the initial pseudostate as a source and a final state as a target."""
    found = TRANSITION.match(line)
    if found is None:
        return False
    a, b = (aliases.get(unquote(x), unquote(x)) for x in (found.group("a"), found.group("b")))
    label = unescape(found.group("label") or "").strip()
    if a == INITIAL and b == INITIAL:
        parsed.skip(where, line, "an arrow from the initial pseudostate straight to a final state")
    elif a == INITIAL:
        parsed.state(b)
        parsed.start(b, where)
    elif b == INITIAL:
        parsed.state(a)  # a final state: PlayIDE derives it (no transition leaves the state)
    else:
        parsed.state(a)
        parsed.state(b)
        parsed.edges.append(Edge(a, b, label, where))
    return True


def _bounds(rest: str) -> tuple[int, str]:
    found = _BOUNDS.search(rest)
    if found is None:
        return 0, "1"
    lo = 0 if found.group("lo") == "*" else int(found.group("lo"))
    hi = found.group("hi")
    upper = ("*" if hi in ("*", "n") else hi) if hi is not None else ("*" if found.group("lo") == "*" else found.group("lo"))
    return lo, upper


def read_member(text: str, where: str) -> Attr | None:
    """`+itemTitle : String [1] {maxLength = 200}` or `+String itemTitle`. None for a line that is not an attribute."""
    body = re.sub(r"^[+\-#~]\s*", "", text.strip())
    body = re.sub(r"^\{(?:static|abstract|field)\}\s*", "", body)
    if not body or "(" in body:
        return None
    found = _MEMBER_TYPED.match(body) or _MEMBER_JAVA.match(body)
    if found is None:
        return Attr(name=body.split()[0], type="", where=where)
    lower, upper = _bounds(found.group("rest") or "")
    maximum = _MAX.search(found.group("rest") or "")
    return Attr(name=found.group("name"), type=found.group("type") or "", lower=lower, upper=upper,
                max_length=int(maximum.group("n")) if maximum else None, where=where)


def _stereotypes(lines: list[tuple[str, str]]) -> list[str]:
    return [s.lower() for line, _ in lines for s in re.findall(r"<<\s*([\w ]+?)\s*>>", line)]


def _members(lines: list[tuple[str, str]]) -> list[tuple[str, str]]:
    return [(line, where) for line, where in lines if line.strip() and not line.strip().startswith("<<")]


def read_body(name: str, lines: list[tuple[str, str]], parsed: Parsed, record: bool, enum: bool) -> None:
    """The members of `class Name { ... }` (or an enumeration's literals)."""
    stereotypes, members = _stereotypes(lines), _members(lines)
    record = record or "record" in stereotypes
    if enum or "enumeration" in stereotypes:
        parsed.enums[name] = tuple(re.sub(r"[,;]$", "", line.strip()) for line, _ in members)
        return
    attributes = [attr for line, where in members if (attr := _attribute(name, line, where, parsed)) is not None]
    parsed.klass(Klass(name=name, attributes=tuple(attributes), record=record, where=lines[0][1] if lines else ""))


def _attribute(name: str, line: str, where: str, parsed: Parsed) -> Attr | None:
    if "(" in line:
        parsed.skip(where, f"{name}: {line.strip()}", "operations are not in PlayIDE's data vocabulary")
        return None
    return read_member(line, where)


_KINDS = {"*": "composition", "o": "aggregation"}


def read_relation(line: str, where: str, parsed: Parsed) -> bool:
    """A class relationship. Composition and aggregation keep the whole as the source, as `data.json` does."""
    found = RELATION.match(line)
    if found is None:
        return False
    arrow, a, b = found.group("arrow"), found.group("a"), found.group("b")
    ma, mb, label = (found.group(g) or "" for g in ("ma", "mb", "label"))
    label = re.sub(r"\s*[<>]$", "", re.sub(r"^[<>]\s*", "", label.strip()))
    if "|" in arrow or ".." in arrow:
        parsed.skip(where, line, "generalisation, realisation and dependency are not in PlayIDE's data vocabulary")
        return True
    kind, flipped = _kind(arrow)
    if flipped:
        a, b, ma, mb = b, a, mb, ma
    parsed.links.append(Link(a, b, kind, label, ma or "1", mb or "0..*", where))
    return True


def _kind(arrow: str) -> tuple[str, bool]:
    """The link's kind, and whether the file's right-hand class is the source (the whole, or an arrow's tail)."""
    if arrow[-1] in _KINDS:  # `A --* B`: the diamond is at B, so B is the whole
        return _KINDS[arrow[-1]], True
    return _KINDS.get(arrow[0], "association"), arrow[0] == "<"
