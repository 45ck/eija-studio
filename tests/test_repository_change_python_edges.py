"""Pure historical-source oracles: ambiguous identities and physical source lines."""
from __future__ import annotations

import pytest

from eija_studio.adapters import repository_changes as changes
from eija_studio.adapters import repository_analysis as analysis
from eija_studio.adapters import repository_change_snapshot as snapshot
from eija_studio.weave import codelink


@pytest.mark.parametrize(("source", "fragment", "lines"), [
    ("def f():\n    return 1\n\ndef f():\n    return 2\n", "f", [1, 4]),
    ("class C:\n    def f(self):\n        return 1\n\n    def f(self):\n        return 2\n", "C.f", [2, 5]),
])
def test_redefined_python_reference_is_ambiguous_not_unchanged(source, fragment, lines):
    before = analysis._python_facts("src/repeated.py", source.encode())
    after_source = source.replace("return 2", "return 3")
    after = analysis._python_facts("src/repeated.py", after_source.encode())
    reference = "repo://src/repeated.py#" + fragment
    for facts in (before, after):
        assert facts["status"] == "PARTIAL"
        assert "DUPLICATE_REFERENCE" in {gap["reason"] for gap in facts["gaps"]}
        matches = [item for item in facts["symbols"] if item["reference"] == reference]
        assert [item["start_line"] for item in matches] == lines
    old = [item for item in before["symbols"] if item["reference"] == reference]
    new = [item for item in after["symbols"] if item["reference"] == reference]
    assert old[0]["syntax_digest"] == new[0]["syntax_digest"]
    assert old[1]["syntax_digest"] != new[1]["syntax_digest"]
    selected = next(item for item in snapshot._symbol_changes(before, after) if item["reference"] == reference)
    assert selected["status"] == "ambiguous"
    assert selected["before"] is None and selected["after"] is None
    side = changes._Side("a" * 40, "b" * 40, {"src/repeated.py": changes._Object("100644", "c" * 40, "blob")})
    side.capture.files["src/repeated.py"] = source.encode()
    side.facts["src/repeated.py"] = before
    reader = object.__new__(changes.RepositoryChanges)
    assert reader._selected_side(side, "src/repeated.py", reference) == {
        "status": "ambiguous", "blob": "c" * 40, "reference": reference,
    }


@pytest.mark.parametrize("separator", ["\u2028", "\u2029", "\v", "\f"])
@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"])
@pytest.mark.parametrize("terminated", [False, True])
def test_unicode_string_whitespace_does_not_renumber_source_lines(separator, newline, terminated):
    source = newline.join(["value = '" + separator.join(["piece"] * 20) + "'", "def target():", "    return 1"])
    if terminated:
        source += newline
    node = codelink.parse_module(source).body[1]
    assert (node.lineno, node.end_lineno) == (2, 3)
    excerpt = snapshot._excerpt(source.encode(), node.lineno, node.end_lineno)
    assert excerpt["text"].encode() == source.encode()
    assert "def target():" in excerpt["text"]
    assert excerpt["range"] == {"start": 1, "end": 3}
    assert excerpt["truncated"] is False


def test_symbol_cap_does_not_make_a_truncated_duplicate_look_unique():
    def fact(name):
        return {"reference": "repo://src/repeated.py#" + name, "kind": "function", "syntax_digest": "a" * 64,
                "start_line": 1, "end_line": 1}

    prefix = [fact(f"f{index}") for index in range(analysis.MAX_SYMBOLS - 1)]
    duplicate = fact("ambiguous_at_cap")
    incoming = {"status": "EXTRACTED", "method": "python_ast_ast-v2", "symbols": [*prefix, duplicate, dict(duplicate)], "gaps": []}
    result = analysis._validated_facts("src/repeated.py", b"captured source\n", incoming)
    assert result["status"] == "PARTIAL"
    assert result["symbols"] == []
    assert "SYMBOL_LIMIT" in {gap["reason"] for gap in result["gaps"]}
    assert snapshot._symbol_changes(result, result) == []
