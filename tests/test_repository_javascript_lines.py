"""Real worker facts must select the same physical lines as captured source excerpts."""

from __future__ import annotations

from hashlib import sha256

import pytest

from eija_studio.adapters import repository_analysis as analysis
from eija_studio.adapters import repository_change_snapshot as snapshot


@pytest.mark.parametrize("endings", [(b"\r",), (b"\r", b"\n", b"\r\n")], ids=["bare-cr", "mixed"])
@pytest.mark.parametrize("suffix", ["comments", "declarations"])
def test_real_worker_selected_source_uses_original_physical_lines(endings, suffix):
    path = "src/physical.js"
    reference = "repo://src/physical.js#js/function/target"
    # This hand-authored inventory is the line oracle; never split source using production code.
    content = [f"/* prefix café {index} */" for index in range(11)] + [
        "function target() {", "  return `café\u2028same physical\u2029line`;", "}",
    ] + [f"/* suffix {index} */" if suffix == "comments" else f"const suffix{index} = {index};" for index in range(6)]
    physical = [line.encode("utf-8") + (endings[index % len(endings)] if index < len(content) - 1 else b"")
                for index, line in enumerate(content)]
    data = b"".join(physical)
    exact_definition = b"".join(physical[11:13]) + b"}"
    exact_excerpt = b"".join(physical[8:17])
    start_byte = len(b"".join(physical[:11]))

    facts = analysis.syntax_reader(path, data)  # The fixed subprocess parses real original bytes.
    if facts["status"] == "NOT_RUN" and {gap["reason"] for gap in facts["gaps"]} == {"PARSER_UNAVAILABLE"}:
        pytest.skip("NOT_RUN: pinned JavaScript parser unavailable")
    assert facts["status"] == "EXTRACTED", facts
    assert len(facts["symbols"]) == 1
    validated = analysis._validated_facts(path, data, facts)
    side = snapshot._Side("a" * 40, "b" * 40, {path: snapshot._Object("100644", "c" * 40, "blob")})
    side.capture.files[path] = data
    side.facts[path] = validated

    selected = snapshot.selected_side(side, path, reference)
    assert selected is not None and selected["status"] == "captured"
    # Old LF-only facts could label prefix comments as the selected function's source.
    assert selected["text"].encode("utf-8") == exact_excerpt
    assert exact_definition in selected["text"].encode("utf-8")
    assert selected["range"] == {"start": 9, "end": 17}
    assert selected["truncated"] is False
    assert selected["file_sha256"] == sha256(data).hexdigest()
    assert selected["snippet_sha256"] == sha256(exact_excerpt).hexdigest()
    assert selected["symbol"]["reference"] == reference
    assert (selected["symbol"]["start_line"], selected["symbol"]["end_line"]) == (12, 14)

    raw = facts["symbols"][0]
    assert raw["start_byte"] == start_byte
    assert raw["end_byte"] == start_byte + len(exact_definition)
    assert data[raw["start_byte"]:raw["end_byte"]] == exact_definition
    assert raw["source_sha256"] == sha256(exact_definition).hexdigest()
    assert side.capture.files[path] == data
