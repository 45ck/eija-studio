"""Differential source facts, exact capture identity, and deliberately wrong oracles."""
from __future__ import annotations

import hashlib
import json

import pytest

from eija_studio.adapters import repository_analysis as analysis
from eija_studio.adapters.repository_capture import _Capture, TEXT_SUFFIXES
from eija_studio.weave.index import WEB_SUFFIXES, dhash
from repository_python_v1_oracle import _facts as original_facts
from repository_python_v1_oracle import _validated_facts as original_validated_facts


PROGRAMS = {
    "ordinary": "def run(value=1):\n    return value + 1\n",
    "private_closure": "def _helper():\n    return 3\ndef run():\n    return _helper()\n",
    "private_only": "def _hidden():\n    return 3\n_hidden_value = 8\n",
    "members": "class C:\n    def _helper(self):\n        return 1\n    def run(self):\n        return self._helper()\n    def __call__(self):\n        return 2\n",
    "decorators": "@first\n@second(3)\ndef run():\n    return 1\n",
    "async": "async def run():\n    return await work()\n",
    "duplicate_function": "def f():\n    return 1\ndef f():\n    return 2\n",
    "duplicate_method": "class C:\n    def f(self):\n        return 1\n    def f(self):\n        return 2\n",
    "duplicate_class": "class C:\n    def first(self):\n        return 1\nclass C:\n    def later(self):\n        return 2\n",
    "rebound_kind": "def Value():\n    return 1\nValue = 3\n",
    "assignments": "VALUE = 3\nAlias: type = object\na = b = 7\n_hidden = 4\n",
    "test_classification": "def test_rule():\n    return 1\nclass Test:\n    def test_method(self):\n        return 2\n",
    "unicode": "TITLE = '雪'\ndef café():\n    return TITLE\n",
    "unicode_separator": "VALUE = 'one\u2028two\u2029three'\ndef run():\n    return VALUE\n",
    "surrogate": "VALUE = '\\ud800'\ndef run():\n    return VALUE\n",
    "duplicate_surrogate": "VALUE = '\\ud800'\nVALUE = '\\ud801'\n",
    "empty": "",
    "malformed": "def broken(:\n    pass\n",
    "unexecuted": "raise RuntimeError('source must never execute')\ndef run():\n    return 1\n",
}


@pytest.mark.parametrize("path", ["src/sample.py", "tests/test_sample.py", "scripts/check_雪#.py"])
@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"])
@pytest.mark.parametrize("program", PROGRAMS.values(), ids=PROGRAMS.keys())
def test_captured_bytes_match_frozen_filesystem_adapter(path, newline, program):
    data = program.replace("\n", newline).encode("utf-8")
    expected = original_facts(path, data, None)
    actual = analysis._facts(path, data, None)
    assert actual == expected
    assert json.dumps(actual, sort_keys=True, ensure_ascii=True) == json.dumps(expected, sort_keys=True, ensure_ascii=True)


@pytest.mark.parametrize("count", [1023, 1024, 1025])
def test_symbol_limit_preserves_exact_all_or_none_inventory(count):
    facts = {"status": "EXTRACTED", "method": "python_ast_ast-v2", "gaps": [], "symbols": [
        {"reference": f"repo://src/sample.py#f{index}", "kind": "function", "syntax_digest": "a" * 64,
         "start_line": 1, "end_line": 1} for index in range(count)
    ]}
    result = analysis._validated_facts("src/sample.py", b"captured\n", facts)
    assert result == original_validated_facts("src/sample.py", b"captured\n", facts)
    assert len(result["symbols"]) == (count if count <= 1024 else 0)


def test_differential_oracle_detects_wrong_range_digest_kind_and_duplicate_omission():
    path = "tests/test_sample.py"
    data = b"@decorator\ndef test_rule():\n    return 1\ndef test_rule():\n    return 2\n"
    expected = original_facts(path, data, None)
    assert len(expected["symbols"]) == 2
    for field, wrong in [("start_line", 99), ("syntax_digest", "0" * 64), ("kind", "method")]:
        changed = analysis._facts(path, data, None)
        changed["symbols"][0][field] = wrong
        with pytest.raises(AssertionError):
            assert changed == expected
    omitted = analysis._facts(path, data, None)
    omitted["symbols"].pop()
    with pytest.raises(AssertionError):
        assert omitted == expected


def test_capture_policy_hash_matches_previous_graph_helper_for_unicode_and_order():
    captured = _Capture(files={"src/雪#.py": "print('雪')\r\n".encode(), "README.md": b"sample\n"})
    payload = [[path, digest] for path, digest in captured.hashes.items()]
    expected = dhash("eija.repository.source.v1", payload)
    assert expected == "sha256:5fd991107564245638bdb6570e5ab537abb70a7479348b6b60e5872a034448ff"
    assert captured.source_hash == expected
    assert _Capture(files=dict(reversed(list(captured.files.items())))).source_hash == expected
    assert captured.source_hash != "sha256:" + hashlib.sha256(json.dumps(payload).encode()).hexdigest()
    assert set(WEB_SUFFIXES) <= TEXT_SUFFIXES
