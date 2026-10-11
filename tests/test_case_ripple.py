"""A persisted review case compares its whole change against its retained baseline."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from eija_studio.domain.change_case import OwnerPlanRequest
from eija_studio.domain.models import OWNER, Workflow
from eija_studio.interfaces.http import create_app

HEADERS = {"Authorization": "Bearer ripple-case-test", "Origin": "http://127.0.0.1:8765"}


def workspace_state(studio):
    with studio.store.transaction() as session:
        return session.active(), session.effect_counts(), studio.store.list_cases()


@pytest.mark.parametrize("origin", ["pack_meaning", "owner_plan"])
def test_whole_case_effects_survive_promotion_and_reopening(studio, selected, origin):
    if origin == "owner_plan":
        case = studio.from_plan(OwnerPlanRequest.model_validate({
            "request": "Review the accepted recommendation workflow",
            "pack_id": studio.pack.id, "expected_pack_digest": studio.pack.digest,
            "expected_baseline_version": selected["baseline_version"],
            "expected_baseline_semantic_hash": Workflow.model_validate(selected["baseline"]).semantic_hash,
            "expected_candidate_semantic_hash": Workflow.model_validate(selected["candidate"]).semantic_hash,
            "steps": [{"transaction": tx, "author": "you", "round": 1, "request": "Recommendation workflow"}
                      for tx in selected["transactions"]],
        }), OWNER)
    else:
        case = selected
    before = workspace_state(studio)
    with TestClient(create_app(studio, "ripple-case-test"), base_url="http://127.0.0.1:8765") as client:
        response = client.post("/api/play/ripple", json={"case_id": case["id"]}, headers=HEADERS)
        assert response.status_code == 200
        report = response.json()
        assert report["before_model"] == Workflow.model_validate(case["baseline"]).semantic_hash
        assert report["model"] == Workflow.model_validate(case["candidate"]).semantic_hash
        assert any(item["text"] == "Adds state Recommended" for item in report["diagrams"]["states"])
        assert any(item["text"] == "New use case Recommend" for item in report["diagrams"]["usecases"])
        assert report["diagrams"]["components"]
        # An explicitly selected round compares the case candidate before and after
        # that round, rather than counting the whole initial selection again.
        round_report = client.post("/api/play/ripple", json={"case_id": case["id"], "since": []}, headers=HEADERS).json()
        assert round_report["before_model"] == round_report["model"]
        assert all(not items for items in round_report["diagrams"].values())
    assert workspace_state(studio) == before
