"""Clipping accounting stays auditable, including traces recorded before the correction."""
import pytest

from quality.hci import analysis


def _pass(chunks):
    return {"views": {"fixture": {"chunks_viewport": chunks, "chunks_page": {"chunks": 15}}}}


def test_legacy_trace_does_not_invent_zero_exclusions_or_raw_measurements():
    observed = {"controls": 3, "content_groups": 2, "atoms": 6, "chunks": 5}
    row = analysis.working_memory(_pass(observed))["views"][0]
    assert row["chunks_viewport"] == 5 and row["chunks_page"] == 15
    assert row["raw_chunks_viewport"] is None
    assert row["excluded_clipped_chunks"] is None


@pytest.mark.parametrize(("raw_chunks", "excluded_chunks"), [(5, 0), (12, 7)])
def test_new_trace_reports_exact_raw_and_clipped_counts(raw_chunks, excluded_chunks):
    observed = {"controls": 3, "content_groups": 2, "atoms": 6, "chunks": 5,
                "raw": {"chunks": raw_chunks}, "excluded_clipped": {"chunks": excluded_chunks}}
    result = analysis.working_memory(_pass(observed))
    row = result["views"][0]
    assert row["raw_chunks_viewport"] == raw_chunks
    assert row["excluded_clipped_chunks"] == excluded_chunks
    assert row["chunks_viewport"] + row["excluded_clipped_chunks"] == row["raw_chunks_viewport"]
    assert row["controls"] == 3 and row["content_groups"] == 2 and row["atoms_viewport"] == 6
    assert row["over_miller_9"] is False and row["over_cowan_4"] is True
    assert result["summary"]["max_chunks_viewport"] == 5
