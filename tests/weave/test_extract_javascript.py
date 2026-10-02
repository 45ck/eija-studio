"""Handwritten syntax oracles, independent of the adapter's traversal rules."""

from __future__ import annotations

import gc
from hashlib import sha256
from types import SimpleNamespace
from urllib.parse import unquote

import pytest

from eija_studio.weave import extract_javascript as js


@pytest.fixture
def parse():
    try:
        js._load_parser()
    except (ImportError, ValueError, OSError) as error:
        pytest.skip(f"NOT_RUN: pinned JavaScript parser unavailable ({type(error).__name__})")
    return js.syntax_reader


def by_fragment(result):
    return {unquote(item["reference"].split("#", 1)[1]): item for item in result["symbols"]}


@pytest.mark.parametrize(
    "line_endings", [(b"\n",), (b"\r\n",), (b"\r",), (b"\r", b"\n", b"\r\n")],
    ids=["lf", "crlf", "bare-cr", "mixed"],
)
def test_handwritten_expected_sites_and_exact_byte_slices(parse, line_endings):
    lines = [
        "/* 😀 prefix */",
        'async function cases() { return "café"; }',
        "function load() { return 2; }",
        "const task = async (name) => name;",
        '$("create").onclick = () => { return 3; };',
        "$('case-switcher').onchange = function () { return 4; };",
    ]
    source = b"".join(line.encode() + line_endings[index % len(line_endings)] for index, line in enumerate(lines))
    result = parse("ui/app.js", source)
    assert result["status"] == "EXTRACTED"
    expected = {
        "js/function/cases": (2, b'async function cases() { return "caf\xc3\xa9"; }'),
        "js/function/load": (3, b"function load() { return 2; }"),
        "js/function/task": (4, b"task = async (name) => name"),
        'js/assignment/$("create").onclick': (5, b'$("create").onclick = () => { return 3; }'),
        'js/assignment/$("case-switcher").onchange': (
            6,
            b"$('case-switcher').onchange = function () { return 4; }",
        ),
    }
    actual = by_fragment(result)
    assert set(actual) == set(expected)
    for fragment, (line, raw) in expected.items():
        item = actual[fragment]
        assert item["start_line"] == item["end_line"] == line
        assert source[item["start_byte"] : item["end_byte"]] == raw
        assert item["source_sha256"] == sha256(raw).hexdigest()
        assert item["reference"].startswith("repo://ui/app.js#js/")
    assert result["semantic_complete"] is False


def test_format_and_comments_preserve_syntax_not_raw_bytes(parse):
    before = b"function alpha(a){return a+1;}"
    after = b"// moved\r\n\r\nfunction alpha( a ) { /* remark */ return a + 1; }\r\n"
    a, b = (parse("app.js", data)["symbols"][0] for data in (before, after))
    assert a["syntax_digest"] == b["syntax_digest"]
    assert a["source_sha256"] != b["source_sha256"]
    assert a["reference"] == b["reference"]
    assert (a["start_line"], b["start_line"]) == (1, 3)


@pytest.mark.parametrize(
    "after",
    [
        b"function alpha(a){return a-1;}",
        b"function alpha(a){return a+2;}",
        b"function alpha(a){return a+1}",
        b"function alpha(a){return\na+1;}",
    ],
)
def test_body_operators_literals_punctuation_and_asi_are_significant(parse, after):
    before = parse("app.js", b"function alpha(a){return a+1;}")["symbols"][0]
    changed = parse("app.js", after)["symbols"][0]
    assert before["reference"] == changed["reference"]
    assert before["syntax_digest"] != changed["syntax_digest"]


@pytest.mark.parametrize(
    "before,after",
    [
        (b"function f(){return 'a b'}", b"function f(){return 'a  b'}"),
        (b"function f(){return `a\nb`}", b"function f(){return `a\r\nb`}"),
        (b"function f(){return /a+/g}", b"function f(){return /a*/g}"),
        (b"const f = () => 1;", b"let f = () => 1;"),
        (b"function f(){}", b"export function f(){}"),
    ],
)
def test_token_contents_and_declaration_kind_are_not_normalized(parse, before, after):
    assert (
        parse("app.js", before)["symbols"][0]["syntax_digest"]
        != parse("app.js", after)["symbols"][0]["syntax_digest"]
    )


def test_source_order_does_not_change_symbol_identity_or_digest(parse):
    a = b"function alpha(){return 1;}\nfunction beta(){return 2;}"
    b = b"function beta(){return 2;}\nfunction alpha(){return 1;}"
    facts = [by_fragment(parse("a.js", data)) for data in (a, b)]
    assert list(facts[0]) == list(facts[1])
    for name in facts[0]:
        assert facts[0][name]["syntax_digest"] == facts[1][name]["syntax_digest"]


def test_added_removed_and_unchanged_are_independently_nameable(parse):
    before = by_fragment(parse("a.js", b"function gone(){}\nfunction stays(){}"))
    after = by_fragment(parse("a.js", b"function newName(){}\nfunction stays(){}"))
    assert set(before) - set(after) == {"js/function/gone"}
    assert set(after) - set(before) == {"js/function/newName"}
    assert before["js/function/stays"]["syntax_digest"] == after["js/function/stays"]["syntax_digest"]


@pytest.mark.parametrize(
    "source",
    [
        b"$(selector).onclick = () => 1;",
        b'$("id")[event] = () => 1;',
        b'$("id")["onclick"] = () => 1;',
        b'lookup("id").onclick = () => 1;',
        b'$("id", other).onclick = () => 1;',
        b'$("escaped\\x41").onclick = () => 1;',
        b'$("id")?.onclick = () => 1;',
        b'$?.("id").onclick = () => 1;',
        b'$("id").onclick = function () {};' + b"\n$(`id`).onclick = () => 1;",
    ],
)
def test_dynamic_or_unsupported_target_is_explicit_gap(parse, source):
    result = parse("a.js", source)
    assert result["status"] == "PARTIAL"
    assert {gap["reason"] for gap in result["gaps"]} == {"DYNAMIC_ASSIGNMENT_TARGET"}
    assert len(result["symbols"]) == (1 if b"$(`id`)" in source else 0)


def test_literal_quote_style_matches_target_but_not_token_digest(parse):
    a = parse("a.js", b'$("id").onclick = () => 1;')["symbols"][0]
    b = parse("a.js", b"$('id').onclick = () => 1;")["symbols"][0]
    assert a["reference"] == b["reference"]
    assert a["syntax_digest"] != b["syntax_digest"]


def test_duplicate_functions_and_assignments_remain_ambiguous(parse):
    source = b'function twice(){}\nfunction twice(){return 1}\n$("id").onclick=()=>1;\n$("id").onclick=()=>2;'
    result = parse("a.js", source)
    assert result["status"] == "PARTIAL"
    assert len(result["symbols"]) == 4
    assert len({item["reference"] for item in result["symbols"]}) == 2
    assert "DUPLICATE_REFERENCE" in {gap["reason"] for gap in result["gaps"]}


def test_parse_error_keeps_valid_recovered_syntax_partial(parse):
    result = parse("a.js", b"function intact(){return 1;}\nfunction broken( { ???")
    assert result["status"] == "PARTIAL"
    assert "PARSE_ERROR" in {gap["reason"] for gap in result["gaps"]}
    assert "js/function/intact" in by_fragment(result)


def test_missing_token_does_not_claim_complete(parse):
    result = parse("a.js", b"function broken(){ return 1;")
    assert result["status"] == "PARTIAL"
    assert not result["symbols"]
    assert "PARSE_ERROR" in {gap["reason"] for gap in result["gaps"]}


def test_nested_names_are_not_falsely_top_level_and_classes_have_gap(parse):
    result = parse("a.js", b"function outer(){function inner(){}}\nclass A {method(){}}")
    assert set(by_fragment(result)) == {"js/function/outer"}
    assert "UNCLASSIFIED_CLASS" in {gap["reason"] for gap in result["gaps"]}


def test_export_and_multiple_function_values(parse):
    result = parse("a.js", b"export function api(){}\nconst a=(x=>x), b=function(){};\nexport const c=()=>1;")
    assert result["status"] == "EXTRACTED"
    assert set(by_fragment(result)) == {"js/function/api", "js/function/a", "js/function/b", "js/function/c"}


def test_missing_dependency_and_wrong_version_are_not_run(monkeypatch):
    def missing():
        raise ImportError("do not expose package loader details")

    monkeypatch.setattr(js, "_load_parser", missing)
    result = js.syntax_reader("a.js", b"function a(){}")
    assert result["status"] == "NOT_RUN"
    assert not result["symbols"]
    assert result["gaps"][0]["reason"] == "PARSER_UNAVAILABLE"
    assert "loader details" not in str(result)


@pytest.mark.parametrize(
    "path,data,reason",
    [
        ("a.ts", b"", "UNSUPPORTED_LANGUAGE"),
        ("../a.js", b"", "INVALID_PATH"),
        ("/a.js", b"", "INVALID_PATH"),
        ("a\\b.js", b"", "INVALID_PATH"),
        ("a.js", b"\xff", "NON_UTF8"),
        ("a.js", "not bytes", "SOURCE_LIMIT"),
        pytest.param("a.js", b"x" * (js.MAX_BYTES + 1), "SOURCE_LIMIT", id="oversized-source"),
    ],
)
def test_bad_input_stays_unsupported_without_loading_parser(monkeypatch, path, data, reason):
    def forbidden():
        pytest.fail("parser should not be loaded for rejected input")

    monkeypatch.setattr(js, "_load_parser", forbidden)
    result = js.syntax_reader(path, data)
    assert result["status"] == "NOT_RUN"
    assert result["gaps"][0]["reason"] == reason


def test_repeatable_and_no_target_execution(parse, tmp_path):
    marker = tmp_path / "must-not-exist"
    source = (f'function trap(){{require("fs").writeFileSync({str(marker)!r},"executed")}}\ntrap();').encode()
    first = parse("a.js", source)
    assert first == parse("a.js", source)
    assert not marker.exists()


def test_symbol_output_bound_is_partial_and_exact_bound_is_complete(parse, monkeypatch):
    monkeypatch.setattr(js, "MAX_SYMBOLS", 2)
    exact = parse("a.js", b"function a(){}\nfunction b(){}")
    over = parse("a.js", b"function a(){}\nfunction b(){}\nfunction c(){}")
    assert exact["status"] == "EXTRACTED"
    assert over["status"] == "PARTIAL"
    assert len(over["symbols"]) == 2
    assert "SYMBOL_LIMIT" in {gap["reason"] for gap in over["gaps"]}


def test_dependency_version_mismatch_does_not_initialize_parser(monkeypatch):
    monkeypatch.setattr(js.metadata, "version", lambda _: "0.0.0")
    result = js.syntax_reader("a.js", b"function f(){}")
    assert result["status"] == "NOT_RUN"
    assert result["parser_version"] is None
    assert result["grammar_version"] is None


@pytest.mark.parametrize("spec", [None, SimpleNamespace(loader=None)], ids=["missing-spec", "missing-loader"])
def test_missing_worker_module_loader_is_not_run(monkeypatch, spec):
    versions = {"tree-sitter": js.PARSER_VERSION, "tree-sitter-javascript": js.GRAMMAR_VERSION}
    monkeypatch.setattr(js.metadata, "version", versions.__getitem__)
    monkeypatch.setattr(js.util, "spec_from_file_location", lambda *args: spec)
    result = js.syntax_reader("a.js", b"function f(){}")
    assert result["status"] == "NOT_RUN"
    assert result["gaps"][0]["reason"] == "PARSER_UNAVAILABLE"


def test_invalid_worker_loader_source_is_not_run(monkeypatch):
    versions = {"tree-sitter": js.PARSER_VERSION, "tree-sitter-javascript": js.GRAMMAR_VERSION}
    monkeypatch.setattr(js.metadata, "version", versions.__getitem__)

    def invalid_module(*args):
        raise SyntaxError("private loader detail")

    loader = SimpleNamespace(exec_module=invalid_module)
    monkeypatch.setattr(js.util, "spec_from_file_location", lambda *args: SimpleNamespace(loader=loader))
    monkeypatch.setattr(js.util, "module_from_spec", lambda *args: SimpleNamespace())
    result = js.syntax_reader("a.js", b"function f(){}")
    assert result["status"] == "NOT_RUN"
    assert "private loader detail" not in str(result)


def test_large_handwritten_shape_under_forced_gc_preserves_ranges(parse):
    source = "\r\n".join(
        f'function f{index}(){{ const x = "café"; return () => x + {index}; }}' for index in range(800)
    ).encode()
    previous = gc.get_threshold()
    try:
        gc.set_threshold(1, 1, 1)
        result = parse("large.js", source)
    finally:
        gc.set_threshold(*previous)
    assert result["status"] == "EXTRACTED"
    assert len(result["symbols"]) == 800
    actual = by_fragment(result)
    for index in (0, 17, 400, 799):
        item = actual[f"js/function/f{index}"]
        assert item["start_line"] == item["end_line"] == index + 1
        assert source[item["start_byte"] : item["end_byte"]].startswith(f"function f{index}()".encode())


@pytest.mark.parametrize("ending", [b"\n", b"\r\n", b"\r"], ids=["lf", "crlf", "bare-cr"])
@pytest.mark.parametrize("kind,body", [
    ("asi", [b"return", b"value;"]),
    ("line-comment", [b"// comment", b"return 1;"]),
    ("continuation", [b'return "a\\', b'b";']),
    ("template", [b"return `a", b"b`;"]),
])
def test_parser_newline_view_preserves_original_tokens_ranges_and_asi(parse, ending, kind, body):
    lines = [b"/* prefix */", b"function target() {", *body, b"}", b"/* trailing */", b"const stop = 0;"]
    data = ending.join(lines)
    result = parse("physical.js", data)
    assert result["status"] == "EXTRACTED"
    fact = by_fragment(result)["js/function/target"]
    raw = ending.join(lines[1:5])
    assert (fact["start_line"], fact["end_line"]) == (2, 5)
    assert fact["start_byte"] == len(lines[0]) + len(ending)
    assert fact["end_byte"] == fact["start_byte"] + len(raw)
    assert data[fact["start_byte"]:fact["end_byte"]] == raw
    assert fact["source_sha256"] == sha256(raw).hexdigest()
    lf_fact = by_fragment(parse("physical.js", b"\n".join(lines)))["js/function/target"]
    if kind in {"continuation", "template"} and ending != b"\n":
        # Raw token spellings remain significant even when the parser view normalizes a delimiter.
        assert fact["syntax_digest"] != lf_fact["syntax_digest"]
    else:
        assert fact["syntax_digest"] == lf_fact["syntax_digest"]
    if kind == "asi":
        same_line = parse("physical.js", b"function target() {return value;}")["symbols"][0]
        assert fact["syntax_digest"] != same_line["syntax_digest"]


@pytest.mark.parametrize("ending", [b"\n", b"\r\n", b"\r"], ids=["lf", "crlf", "bare-cr"])
def test_invalid_literal_newline_stays_partial_and_preserves_recovered_source(parse, ending):
    intact = b"function intact() {return 7;}"
    lines = [b'function broken() {return "a', b'b";}', intact]
    data = ending.join(lines)
    result = parse("physical.js", data)
    assert result["status"] == "PARTIAL"
    assert "PARSE_ERROR" in {gap["reason"] for gap in result["gaps"]}
    facts = by_fragment(result)
    assert "js/function/broken" not in facts
    fact = facts["js/function/intact"]
    assert (fact["start_line"], fact["end_line"]) == (3, 3)
    assert data[fact["start_byte"]:fact["end_byte"]] == intact
    assert fact["source_sha256"] == sha256(intact).hexdigest()
