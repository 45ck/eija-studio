"""PO-D10: metamorphic invariance and sensitivity of the hash methods the weave reuses from the okf lane.

A hash method decides what counts as a change (freshness), so a false invariance hides a change (false COVERED) and a
false sensitivity creates noise. The relations below are stated without knowing the implementation; the module under test
is ``quality/okf/codelink.py`` (okf lane). If it is not importable the tests are skipped: NOT_RUN, never a pass.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from conftest import ROOT

CANDIDATES = [ROOT / "quality" / "okf" / "codelink.py", ROOT.parent / "okf" / "quality" / "okf" / "codelink.py"]


@pytest.fixture(scope="module")
def codelink():
    for path in CANDIDATES:
        if path.is_file():
            spec = importlib.util.spec_from_file_location("weave_okf_codelink", path)
            module = importlib.util.module_from_spec(spec)
            sys.modules["weave_okf_codelink"] = module
            spec.loader.exec_module(module)
            return module
    pytest.skip("NOT_RUN: quality/okf/codelink.py is not present in this tree or the sibling okf worktree")


@pytest.fixture()
def digest(codelink, tmp_path):
    def _digest(source: str, fragment: str | None = "f", method: str = "ast-v1") -> str:
        (tmp_path / "m.py").write_bytes(source.encode("utf-8"))
        if hasattr(codelink._digest_text, "cache_clear"):
            codelink._digest_text.cache_clear()
        return codelink.digest(tmp_path, codelink.CodeRef("m.py", fragment), method)
    return _digest


BASE = 'def f(a, b):\n    """doc"""\n    return a + b  # note\n'


@pytest.mark.parametrize("name, edited", [
    ("comment", BASE.replace("# note", "# a different note")),
    ("crlf", BASE.replace("\n", "\r\n")),
    ("spacing", BASE.replace("a + b", "a  +  b")),
    ("blank_lines", "\n\n" + BASE + "\n\n"),
    ("trailing_whitespace", BASE.replace("return a + b", "return a + b   ")),
])
def test_po_d10_ast_v1_is_invariant_under_edits_that_do_not_change_the_syntax_tree(digest, name, edited) -> None:
    assert digest(BASE) == digest(edited), name


@pytest.mark.parametrize("name, edited", [
    ("operator", BASE.replace("a + b", "a - b")),
    ("rename_parameter", BASE.replace("(a, b)", "(x, b)").replace("a + b", "x + b")),
    ("docstring", BASE.replace('"""doc"""', '"""doc two"""')),
    ("constant", BASE.replace("return a + b", "return a + b + 1")),
    ("default_argument", BASE.replace("(a, b)", "(a, b=1)")),
])
def test_po_d10_ast_v1_is_sensitive_to_edits_that_change_meaning_or_stated_invariants(digest, name, edited) -> None:
    assert digest(BASE) != digest(edited), name


def test_po_d10_ast_sig_v1_ignores_the_body_and_sees_the_signature(digest) -> None:
    assert digest(BASE, method="ast-sig-v1") == digest(BASE.replace("a + b", "a * b"), method="ast-sig-v1")
    assert digest(BASE, method="ast-sig-v1") != digest(BASE.replace("(a, b)", "(a, b, c=1)"), method="ast-sig-v1")


def test_po_d10_lf_sha256_v1_folds_line_endings_and_sees_every_other_byte(digest) -> None:
    assert digest(BASE, None, "lf-sha256-v1") == digest(BASE.replace("\n", "\r\n"), None, "lf-sha256-v1")
    assert digest(BASE, None, "lf-sha256-v1") != digest(BASE + " ", None, "lf-sha256-v1")


def test_po_d10_a_missing_symbol_is_unresolved_never_a_digest(codelink, digest) -> None:
    with pytest.raises(codelink.Unresolved):
        digest(BASE, fragment="g")


@pytest.mark.xfail(strict=True, reason="FINDING (2026-09-29): a string literal holding a lone surrogate escape makes codelink.digest raise "
                                       "UnicodeEncodeError instead of Unresolved or a digest; a link check would abort rather than report. "
                                       "Fix in the okf lane; when fixed this test XPASSes and strict mode asks for the marker to be removed.")
def test_po_d10_a_lone_surrogate_string_literal_does_not_crash_the_hash(codelink, digest) -> None:
    try:
        digest('def f():\n    return "\\ud800"\n')
    except codelink.Unresolved:
        pass  # an explicit, typed refusal is acceptable; an uncaught UnicodeEncodeError is not
