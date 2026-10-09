"""Offline system describer for PlayIDE's "Describe your app" start (ADR-0203): a fixed library of app shapes and a
small reader for the fields and roles a description names, never an LLM. Its answer is untrusted, like any proposal;
the application builds the system's documents from it and the kernel's pack check decides whether they are a system.

The reader picks the app shape whose keywords the description uses most (the shapes are data in
`packs/describe-shapes.json`: orders, support tickets, bookings, approvals, loans, hiring, deliveries, publishing and
bugs), else a plain one. Role nouns the
description uses replace the shape's own (a coffee shop's barista for the order flow's staff role). Fields come from
"with …" and "has …" lists: a name with "(a, b, c)" after it is a choice, words such as price or quantity are numbers,
date or deadline are dates, and anything else is text. It says what it read and what it assumed, in words.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from typing import Any

from eija_studio.domain.pack import PACKS_ROOT

FIELD_NAME = re.compile(r"^[a-z][a-zA-Z0-9_]{0,39}$")
MAX_FIELDS = 12

SHAPES_FILE = PACKS_ROOT / "describe-shapes.json"  # the shapes are data beside the packs, never named in code


@lru_cache(maxsize=1)
def _library() -> dict[str, Any]:
    document = json.loads(SHAPES_FILE.read_text(encoding="utf-8"))
    return {"shapes": tuple(document["shapes"]), "plain": document["plain"]}


NUMBER = ("price", "cost", "amount", "total", "quantity", "qty", "count", "number", "age", "rating", "score", "budget", "hours", "weight")
DATE = ("date", "deadline", "due", "when", "birthday", "start", "end", "day")
NOT_FIELDS = ("to", "be", "been", "can", "will", "no", "not", "many", "multiple", "them", "it", "they", "this", "that", "who", "which")
BOOLEAN_PREFIX = ("is", "has", "paid", "urgent", "vip")
THING = re.compile(r"\b(?:track|tracks|tracking|manage|manages|managing|organise|organize|log|logs)\s+(?:my\s+|our\s+|the\s+|all\s+)?([a-z]{3,30}?)s\b", re.I)
LIST = re.compile(r"\b(?:with|has|have|having|records?|stores?|captures?|fields?:?)\s+(?:an?\s+|the\s+|their\s+|its\s+)?([^.;\n]+)", re.I)


def _words(text: str) -> list[str]:
    return re.findall(r"[a-zà-ÿ]+", text.lower())


def _score(shape: dict[str, Any], text: str, words: list[str]) -> int:
    singular = {w[:-1] if w.endswith("s") and len(w) > 3 else w for w in words}
    return sum(1 for k in shape["keywords"] if (k in text.lower() if " " in k else k in singular or k in words))


def _shape(text: str) -> dict[str, Any]:
    words = _words(text)
    scores = [(_score(s, text, words), -n, s) for n, s in enumerate(_library()["shapes"])]
    best = max(scores, key=lambda x: (x[0], x[1]))
    return best[2] if best[0] > 0 else _library()["plain"]


def _camel(name: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in re.split(r"[\s_-]+", name.strip()) if part)


def _roles(shape: dict[str, Any], text: str) -> dict[str, str]:
    """Each of the shape's roles, renamed to a noun the description uses for it, first-mentioned first."""
    lower = text.lower()
    renamed: dict[str, str] = {}
    for role, nouns in shape["roles"].items():
        found = [(lower.find(n), n) for n in nouns if re.search(rf"\b{re.escape(n)}s?\b", lower)]
        if found:
            renamed[role] = _camel(min(found)[1])
    used = list(renamed.values())
    return {role: name if used.count(name) == 1 else role for role, name in renamed.items()}


def _starts_or_ends(low: str, words: tuple[str, ...], starts: bool) -> bool:
    return any(low == w or low.endswith(w) or (starts and low.startswith(w)) for w in words)


def _field_type(name: str, choices: list[str]) -> str:
    low = name.lower()
    if choices:
        return "choice"
    if _starts_or_ends(low, NUMBER, True):
        return "number"
    if _starts_or_ends(low, DATE, False):
        return "date"
    return "boolean" if low.split(" ")[0] in BOOLEAN_PREFIX and " " not in low.strip() else "text"


def _choices(raw: str) -> tuple[str, list[str]]:
    """`size (small, medium) extra` as `size extra` and its choices."""
    match = re.match(r"^(.*?)\s*\(([^)]*)\)\s*(.*)$", raw)
    if not match:
        return raw, []
    rest = (match.group(1) + " " + match.group(3)).strip()
    return rest, [_camel(c) or c for c in re.split(r",|/|\bor\b", match.group(2)) if c.strip()]


def _field_name(raw: str) -> tuple[str, list[str]] | None:
    raw = re.sub(r"\b(required|optional|must have|an?|the|some|optional)\b", " ", raw, flags=re.I)
    words = re.findall(r"[A-Za-z][A-Za-z0-9]*", raw)[:3]
    if not words or words[0].lower() in NOT_FIELDS:
        return None
    name = words[0].lower() + "".join(w[:1].upper() + w[1:].lower() for w in words[1:])
    return None if not FIELD_NAME.match(name) or name == "title" else (name, words)


def _field(raw: str) -> dict[str, Any] | None:
    raw, choices = _choices(raw.strip())
    required = bool(re.search(r"\brequired\b|\bmust\b", raw, re.I))
    named = _field_name(raw)
    if named is None:
        return None
    name, words = named
    field = {"name": name, "type": _field_type(" ".join(words), choices), "required": required}
    return field | ({"choices": list(dict.fromkeys(choices))[:32]} if choices else {})


def _split_list(text: str) -> list[str]:
    """`a size (small, medium, large), notes and a price` as its items; commas inside brackets stay with their item."""
    items, depth, current = [], 0, ""
    for ch in text:
        depth += ch == "("
        depth -= ch == ")"
        if ch == "," and depth == 0:
            items.append(current)
            current = ""
        else:
            current += ch
    items.append(current)
    out = []
    for item in items:
        out += [part for part in re.split(r"\s+(?:and|&|plus)\s+(?![^(]*\))", item) if part.strip()]
    return out


def _fields(text: str) -> list[dict[str, Any]]:
    found: dict[str, dict[str, Any]] = {}
    for match in LIST.finditer(text):
        for item in _split_list(match.group(1)):
            field = _field(item)
            if field is not None:
                found.setdefault(field["name"], field)
    return list(found.values())[:MAX_FIELDS]


def _sketch(shape: dict[str, Any], roles: dict[str, str]) -> str:
    def rename(line: str) -> str:
        head, role = line.rsplit("[", 1)
        role = role.rstrip("]")
        return f"{head}[{roles.get(role, role)}]"
    return "\n".join(rename(line) for line in shape["lines"])


class OfflineSystemDescriber:
    name, live = "offline-describe-fixture-v1", False

    def describe(self, text: str) -> dict[str, Any]:
        shape = _shape(text)
        roles = _roles(shape, text)
        own = _fields(text)
        fields = [f for f in shape["fields"] if f["name"] not in {x["name"] for x in own}] + own
        record, name = shape["record"], shape["name"]
        thing = THING.search(text) if shape["id"] == "plain" else None
        if thing:
            record, name = _camel(thing.group(1)), _camel(thing.group(1)) + "s"
        return {"name": name, "record": record, "sketch": _sketch(shape, roles), "fields": fields,
                "template": shape["id"], "reading": _reading(shape, roles, own)}


def _reading(shape: dict[str, Any], roles: dict[str, str], own: list[dict[str, Any]]) -> list[str]:
    """What the reader read and assumed, in words."""
    reading = [f"Read with the offline “{shape['name']}” template (a fixed shape, not a live model)."]
    renamed = [f"{new} for {old}" for old, new in roles.items() if new != old]
    if renamed:
        reading.append("Roles from your words: " + ", ".join(renamed) + ".")
    if own:
        reading.append("Fields from your words: " + ", ".join(f["name"] for f in own) + ".")
    return reading
