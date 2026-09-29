"""Reference canonical serialiser, strict decoder, length-safe framing and Merkle root.

Value domain V (the "committed artefact subset"; design document section 4):

    V ::= None | bool | int n with |n| <= 2**53 - 1 | str (Unicode scalar values only, no lone surrogates)
        | list of V | dict from str to V

Everything else (float, tuple, set, bytes, non-str keys, out-of-range int, lone surrogate) raises
``InvalidValue``: refusing is the only safe answer, because each of them either has two spellings or
collapses two distinct values into one text (measured for the kernel's ``canonical()`` in the tests).

dumps(x) is RFC 8785 restricted to V: no whitespace; strings escaped per RFC 8785 section 3.2.2.2; integers
in decimal; object members sorted by the UTF-16 code-unit sequence of the raw key (section 3.2.3); UTF-8.

Theorems (paper proofs in the design document; here they are tested exhaustively on small domains):

  T1 determinism. dumps(x) is a function of the abstract value: dict insertion order is not observed.
  T2 injectivity. loads(dumps(x)) == x for all x in V, hence dumps is injective on V. Type tags are
     distinguished by the first byte, the JSON grammar is unambiguous, the string escape is injective
     and inverted by unescape, integers are canonical decimals.
  T3 framing. frame(tag, fields) is injective on (tag, tuple of byte strings): each field is preceded
     by its length as 8 bytes big-endian and the arity is stated, so the code is prefix-free.
  T4 root. merkle_root depends on the SET of leaf byte strings only (leaves are sorted, duplicates refused)
     and a leaf change changes the root, except with the probability of a SHA-256 collision (assumption A-SHA).
"""
from __future__ import annotations

import hashlib
from typing import Any

MAX_SAFE = 2**53 - 1


class InvalidValue(ValueError):
    pass


_ESC = {0x08: "\\b", 0x09: "\\t", 0x0A: "\\n", 0x0C: "\\f", 0x0D: "\\r", 0x22: '\\"', 0x5C: "\\\\"}


def _string(s: str) -> str:
    out = ['"']
    for ch in s:
        cp = ord(ch)
        if 0xD800 <= cp <= 0xDFFF:
            raise InvalidValue("lone surrogate")
        if cp in _ESC:
            out.append(_ESC[cp])
        elif cp < 0x20:
            out.append("\\u%04x" % cp)
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def _utf16_key(k: str) -> bytes:
    return k.encode("utf-16-be")  # big-endian bytes compare exactly like unsigned 16-bit code units


def _text(x: Any) -> str:
    if x is None:
        return "null"
    if x is True:
        return "true"
    if x is False:
        return "false"
    t = type(x)
    if t is int:
        if not -MAX_SAFE <= x <= MAX_SAFE:
            raise InvalidValue("integer outside the IEEE-754 safe range")
        return str(x)
    if t is str:
        return _string(x)
    if t is list:
        return "[" + ",".join(_text(v) for v in x) + "]"
    if t is dict:
        for k in x:
            if type(k) is not str:
                raise InvalidValue("object key is not a str")
        return "{" + ",".join(_string(k) + ":" + _text(x[k]) for k in sorted(x, key=_utf16_key)) + "}"
    raise InvalidValue(f"type {t.__name__} is outside the value domain")


def dumps(x: Any) -> bytes:
    return _text(x).encode("utf-8")


class _Parser:
    def __init__(self, text: str):
        self.s, self.i = text, 0

    def fail(self, why: str):
        raise InvalidValue(f"{why} at {self.i}")

    def peek(self) -> str:
        return self.s[self.i] if self.i < len(self.s) else ""

    def take(self, lit: str) -> None:
        if not self.s.startswith(lit, self.i):
            self.fail(f"expected {lit!r}")
        self.i += len(lit)

    def value(self) -> Any:
        c = self.peek()
        if c == "n":
            self.take("null")
            return None
        if c == "t":
            self.take("true")
            return True
        if c == "f":
            self.take("false")
            return False
        if c == '"':
            return self.string()
        if c == "[":
            self.i += 1
            out: list = []
            if self.peek() == "]":
                self.i += 1
                return out
            while True:
                out.append(self.value())
                if self.peek() == ",":
                    self.i += 1
                elif self.peek() == "]":
                    self.i += 1
                    return out
                else:
                    self.fail("expected , or ]")
        if c == "{":
            self.i += 1
            obj: dict = {}
            if self.peek() == "}":
                self.i += 1
                return obj
            while True:
                if self.peek() != '"':
                    self.fail("expected key")
                k = self.string()
                if k in obj:
                    self.fail("duplicate key")
                self.take(":")
                obj[k] = self.value()
                if self.peek() == ",":
                    self.i += 1
                elif self.peek() == "}":
                    self.i += 1
                    return obj
                else:
                    self.fail("expected , or }")
        return self.integer()

    def integer(self) -> int:
        j = self.i
        if self.peek() == "-":
            self.i += 1
        d = self.i
        while self.peek().isdigit() and self.peek().isascii():
            self.i += 1
        digits = self.s[d:self.i]
        if not digits or (len(digits) > 1 and digits[0] == "0") or (self.s[j] == "-" and digits == "0"):
            self.fail("not a canonical integer")
        n = int(self.s[j:self.i])
        if not -MAX_SAFE <= n <= MAX_SAFE:
            self.fail("integer outside the safe range")
        return n

    def string(self) -> str:
        self.take('"')
        out = []
        while True:
            c = self.peek()
            if c == "":
                self.fail("unterminated string")
            self.i += 1
            if c == '"':
                return "".join(out)
            if c == "\\":
                e = self.peek()
                self.i += 1
                simple = {"b": "\b", "t": "\t", "n": "\n", "f": "\f", "r": "\r", '"': '"', "\\": "\\"}
                if e in simple:
                    out.append(simple[e])
                elif e == "u":
                    h = self.s[self.i:self.i + 4]
                    if len(h) != 4 or any(x not in "0123456789abcdef" for x in h):
                        self.fail("bad \\u escape")
                    cp = int(h, 16)
                    self.i += 4
                    if cp >= 0x20:
                        self.fail("non-canonical \\u escape")  # the writer only emits \\u for controls
                    out.append(chr(cp))
                else:
                    self.fail("bad escape")
            else:
                if ord(c) < 0x20 or c in _ESC_CHARS:
                    self.fail("unescaped character that the writer would escape")
                out.append(c)


_ESC_CHARS = {'"', "\\"}


def loads(b: bytes) -> Any:
    """Strict inverse of dumps: accepts exactly the texts dumps can produce (including key order)."""
    text = b.decode("utf-8")
    p = _Parser(text)
    v = p.value()
    if p.i != len(text):
        p.fail("trailing data")
    if dumps(v) != b:
        raise InvalidValue("not in canonical form (key order or spelling)")
    return v


def frame(tag: bytes, fields: tuple[bytes, ...]) -> bytes:
    """Length-safe pre-image: 8-byte length of the tag, the tag, 8-byte arity, then 8-byte length + bytes per field."""
    parts = [len(tag).to_bytes(8, "big"), tag, len(fields).to_bytes(8, "big")]
    for f in fields:
        parts.append(len(f).to_bytes(8, "big"))
        parts.append(f)
    return b"".join(parts)


def digest(tag: bytes, *fields: bytes) -> str:
    return hashlib.sha256(frame(tag, tuple(fields))).hexdigest()


def naive_concat_digest(*fields: bytes) -> str:
    """The flawed scheme (fields concatenated with no length): kept only as a negative control."""
    return hashlib.sha256(b"".join(fields)).hexdigest()


def merkle_root(leaves: list[bytes], tag: bytes = b"eija.merkle.v0") -> str:
    """Root over a SET of leaves. Leaves and interior nodes carry different domain tags."""
    uniq = sorted(set(leaves))
    if len(uniq) != len(leaves):
        raise InvalidValue("duplicate leaf")
    level = [digest(tag + b".leaf", leaf) for leaf in uniq]
    if not level:
        return digest(tag + b".empty")
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            pair = level[i:i + 2]
            nxt.append(digest(tag + b".node", *(p.encode("ascii") for p in pair)))
        level = nxt
    return level[0]
