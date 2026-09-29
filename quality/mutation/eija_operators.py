"""cosmic-ray operator plugin: three fault classes the stock operators lack (ADR-0033).

cosmic-ray has no string-constant or return-value mutation, yet the kernel's authority and evidence code
is mostly *names*: roles, states, effect names, error codes. A guard that compares against the wrong role
name or returns the wrong status string is exactly the fault that must not survive. Each operator follows
the stock `Operator` contract and are registered through a dist-info entry point that `engine` writes
into the scratch workspace (no install step, nothing in the shipped package).

* `eija/ReplaceStringLiteral`: identifier-like strings (no whitespace) become `XX<s>XX`. Prose (messages,
  docstrings), `Literal[...]` type arguments and bytes are left alone: their text is not behaviour.
* `eija/ReplaceReturnValue`: `return <expr>` becomes `return None`.
* `eija/ReplaceMembership`: `a in b` becomes `a not in b` and back (loop `for x in y` is untouched).
"""
from __future__ import annotations

import re

import parso
from cosmic_ray.operators.operator import Example, Operator
from parso.python import tree

_STRING = re.compile(r"^(?P<prefix>[rRuU]?)(?P<quote>'''|\"\"\"|'|\")(?P<body>.*)(?P=quote)$", re.DOTALL)


def _mutable_string(node) -> bool:
    if not isinstance(node, tree.String):
        return False
    match = _STRING.match(node.value)
    if match is None or not match["body"] or re.search(r"\s", match["body"]):
        return False  # bytes/f-string prefixes, empty strings and prose are out of scope
    if node.parent is not None and node.parent.type == "simple_stmt":
        return False  # docstring
    ancestor = node.parent
    while ancestor is not None:
        first = ancestor.children[0] if getattr(ancestor, "children", None) else None
        if ancestor.type in {"atom_expr", "power"} and isinstance(first, tree.Name) and first.value == "Literal":
            return False
        ancestor = ancestor.parent
    return True


class ReplaceStringLiteral(Operator):
    """Wrap an identifier-like string constant in `XX...XX`."""

    def mutation_positions(self, node):
        if _mutable_string(node):
            yield (node.start_pos, node.end_pos)

    def mutate(self, node, index):
        assert index == 0
        match = _STRING.match(node.value)
        quote = match["quote"]
        return tree.String(f"{match['prefix']}{quote}XX{match['body']}XX{quote}", node.start_pos, prefix=node.prefix)

    @classmethod
    def examples(cls):
        return (Example("x = 'Teacher'", "x = 'XXTeacherXX'"),)


class ReplaceReturnValue(Operator):
    """Replace a returned expression with `None`."""

    def mutation_positions(self, node):
        if isinstance(node, tree.ReturnStmt) and len(node.children) == 2 and node.children[1].get_code().strip() != "None":
            expr = node.children[1]
            yield (expr.start_pos, expr.end_pos)

    def mutate(self, node, index):
        assert index == 0 and isinstance(node, tree.ReturnStmt)
        node.children[1] = parso.parse(" None")
        return node

    @classmethod
    def examples(cls):
        return (Example("def f():\n    return 1", "def f():\n    return None"),)


class ReplaceMembership(Operator):
    """Negate a membership test."""

    @staticmethod
    def _is_negated(node) -> bool:
        return node.type == "comp_op" and [c.value for c in node.children] == ["not", "in"]

    def mutation_positions(self, node):
        plain = isinstance(node, tree.Keyword) and node.value == "in" and node.parent is not None and node.parent.type == "comparison"
        if plain or self._is_negated(node):
            yield (node.start_pos, node.end_pos)

    def mutate(self, node, index):
        assert index == 0
        if self._is_negated(node):
            return tree.Keyword("in", node.start_pos, prefix=node.get_first_leaf().prefix)
        node.value = "not in"
        return node

    @classmethod
    def examples(cls):
        return (Example("x = a in b", "x = a not in b"), Example("x = a not in b", "x = a in b"))


_OPERATORS = {op.__name__: op for op in (ReplaceStringLiteral, ReplaceReturnValue, ReplaceMembership)}


class OperatorProvider:
    """cosmic-ray operator provider (entry point group `cosmic_ray.operator_providers`, name `eija`)."""

    def __iter__(self):
        return iter(_OPERATORS)

    def __getitem__(self, name):
        return _OPERATORS[name]
