"""Code-link hashing: what changes a hash and, just as important, what must not."""
import ast
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from quality.okf import codelink as cl  # noqa: E402

BASE = '''"""Module doc."""
CONST = ("a", "b")
_private = 1


class Thing(Base):
    """A thing."""
    name: str = "x"

    def run(self, value: int) -> int:
        """Run it."""
        return value + 1


def check(model: dict) -> list:
    """Check the model."""
    errors = []
    if not model:
        errors.append("EMPTY")
    return errors
'''


def digest(tmp_path: Path, text: str, uri: str, method: str, crlf: bool = False) -> str:
    target = tmp_path / "mod.py"
    data = text.replace("\n", "\r\n") if crlf else text
    target.write_bytes(data.encode("utf-8"))
    return cl.digest(tmp_path, cl.parse_uri(uri), method)


def test_formatting_comments_and_line_endings_do_not_change_a_symbol_hash(tmp_path):
    original = digest(tmp_path, BASE, "repo://mod.py#check", cl.AST_SYMBOL)
    reformatted = BASE.replace("errors = []", "# a comment\n    errors=[  ]").replace('"EMPTY"', "'EMPTY'")
    assert digest(tmp_path, reformatted, "repo://mod.py#check", cl.AST_SYMBOL) == original
    assert digest(tmp_path, BASE, "repo://mod.py#check", cl.AST_SYMBOL, crlf=True) == original


@pytest.mark.parametrize("edit", [
    ('"EMPTY"', '"EMPTY_MODEL"'),                        # a literal an oracle might assert on
    ("if not model:", "if model is None:"),               # a guard
    ('"""Check the model."""', '"""Check the model, strictly."""'),   # a docstring states an invariant
    ("-> list:", "-> tuple:"),                            # the signature
])
def test_semantic_edits_change_the_symbol_hash(tmp_path, edit):
    original = digest(tmp_path, BASE, "repo://mod.py#check", cl.AST_SYMBOL)
    assert digest(tmp_path, BASE.replace(*edit), "repo://mod.py#check", cl.AST_SYMBOL) != original


def test_editing_one_symbol_leaves_a_sibling_hash_alone(tmp_path):
    thing = digest(tmp_path, BASE, "repo://mod.py#Thing", cl.AST_SYMBOL)
    edited = BASE.replace('"EMPTY"', '"CHANGED"')
    assert digest(tmp_path, edited, "repo://mod.py#Thing", cl.AST_SYMBOL) == thing


def test_class_signature_hash_ignores_method_bodies_but_not_signatures_or_fields(tmp_path):
    original = digest(tmp_path, BASE, "repo://mod.py#Thing", cl.AST_SIG)
    assert digest(tmp_path, BASE.replace("value + 1", "value + 2"), "repo://mod.py#Thing", cl.AST_SIG) == original
    assert digest(tmp_path, BASE.replace("value: int", "value: float"), "repo://mod.py#Thing", cl.AST_SIG) != original
    assert digest(tmp_path, BASE.replace('name: str = "x"', 'name: str = "y"'), "repo://mod.py#Thing", cl.AST_SIG) != original
    # ...while the full-AST hash of the same class does see a body edit
    body = digest(tmp_path, BASE, "repo://mod.py#Thing", cl.AST_SYMBOL)
    assert digest(tmp_path, BASE.replace("value + 1", "value + 2"), "repo://mod.py#Thing", cl.AST_SYMBOL) != body


def test_method_addressing_and_module_api_hash(tmp_path):
    method = digest(tmp_path, BASE, "repo://mod.py#Thing.run", cl.AST_SYMBOL)
    assert digest(tmp_path, BASE.replace("value + 1", "value + 9"), "repo://mod.py#Thing.run", cl.AST_SYMBOL) != method
    api = digest(tmp_path, BASE, "repo://mod.py", cl.AST_API)
    assert digest(tmp_path, BASE.replace('"EMPTY"', '"X"'), "repo://mod.py", cl.AST_API) == api      # body only
    assert digest(tmp_path, BASE.replace("def check(model: dict)", "def check(model: dict, *, strict=False)"), "repo://mod.py", cl.AST_API) != api
    assert digest(tmp_path, BASE + "\ndef added(): ...\n", "repo://mod.py", cl.AST_API) != api
    assert digest(tmp_path, BASE.replace("_private = 1", "_private = 2"), "repo://mod.py", cl.AST_API) == api   # private is not API


def test_public_symbol_enumeration_excludes_private_names():
    names = {(n, k) for n, k, _ in cl.public_symbols(ast.parse(BASE))}
    assert names == {("CONST", "constant"), ("Thing", "class"), ("check", "function")}


def test_unresolvable_references_raise(tmp_path):
    (tmp_path / "mod.py").write_text(BASE, encoding="utf-8")
    with pytest.raises(cl.Unresolved):
        cl.digest(tmp_path, cl.parse_uri("repo://mod.py#renamed"), cl.AST_SYMBOL)
    with pytest.raises(cl.Unresolved):
        cl.digest(tmp_path, cl.parse_uri("repo://missing.py#check"), cl.AST_SYMBOL)
    with pytest.raises(cl.Unresolved):
        cl.digest(tmp_path, cl.parse_uri("repo://mod.py#Thing.absent"), cl.AST_SYMBOL)
    assert not cl.resolves(tmp_path, cl.parse_uri("repo://mod.py#renamed"))
    assert cl.resolves(tmp_path, cl.parse_uri("repo://mod.py#Thing.run"))


@pytest.mark.parametrize("uri", ["http://x/y.py", "repo:///abs.py", "repo://../escape.py", "repo://a\\b.py", "repo://"])
def test_unsafe_or_foreign_uris_are_rejected(uri):
    with pytest.raises(ValueError):
        cl.parse_uri(uri)


def test_document_fragments_hash_their_own_row_only(tmp_path):
    (tmp_path / "m.csv").write_text("id,area\nAC01,One\nAC02,Two\n", encoding="utf-8")
    one = cl.digest(tmp_path, cl.parse_uri("repo://m.csv#AC01"), cl.CSV_ROW)
    (tmp_path / "m.csv").write_text("id,area\nAC01,One\nAC02,Changed\n", encoding="utf-8")
    assert cl.digest(tmp_path, cl.parse_uri("repo://m.csv#AC01"), cl.CSV_ROW) == one
    assert cl.digest(tmp_path, cl.parse_uri("repo://m.csv#AC02"), cl.CSV_ROW) != one
    with pytest.raises(cl.Unresolved):
        cl.digest(tmp_path, cl.parse_uri("repo://m.csv#AC09"), cl.CSV_ROW)

    doc = "## Ubiquitous language\n\n**Alpha Beta:** first  definition.\n\n**Gamma:** second.\n"
    (tmp_path / "a.md").write_text(doc, encoding="utf-8")
    alpha = cl.digest(tmp_path, cl.parse_uri("repo://a.md#alpha-beta"), cl.MD_TERM)
    (tmp_path / "a.md").write_text(doc.replace("second", "changed").replace("first  definition", "first definition"), encoding="utf-8")
    assert cl.digest(tmp_path, cl.parse_uri("repo://a.md#alpha-beta"), cl.MD_TERM) == alpha      # whitespace-insensitive
    assert cl.digest(tmp_path, cl.parse_uri("repo://a.md#gamma"), cl.MD_TERM) != cl.digest(tmp_path, cl.parse_uri("repo://a.md#alpha-beta"), cl.MD_TERM)

    table = "| Numbers | Lane |\n|---|---|\n| 0045–0046 | Knowledge base |\n| 0047–0048 | Other |\n"
    (tmp_path / "t.md").write_text(table, encoding="utf-8")
    row = cl.digest(tmp_path, cl.parse_uri("repo://t.md#0045-0046"), cl.MD_ROW)
    (tmp_path / "t.md").write_text(table.replace("Other", "Changed"), encoding="utf-8")
    assert cl.digest(tmp_path, cl.parse_uri("repo://t.md#0045-0046"), cl.MD_ROW) == row
