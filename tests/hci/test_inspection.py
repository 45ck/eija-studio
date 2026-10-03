"""Inspection contracts without a browser; no claim of executed UI coverage."""

import copy
import hashlib
import inspect
from pathlib import Path
from types import SimpleNamespace

import pytest

from quality.hci import inspection
from quality.hci import journey as journey_module
from quality.hci.journey import JourneyError


def payload():
    return {
        "case": {
            "id": "CASE-1",
            "version": 4,
            "stage": "PREVIEW",
            "candidate": {"state": "one"},
            "private": "omit",
        },
        "packet": {"subject_hash": "subject", "subject": {"semantic": "semantic"}, "private": "omit"},
    }


def test_required_scope_is_independent_and_does_not_count_mutually_exclusive_drawers():
    expected = {
        f"workspace-{name}-{width}"
        for name in ("work-views", "panels", "layout", "connections")
        for width in (1440, 320)
    }
    expected |= {
        f"intent-{name}-{width}" for name in ("record", "controls", "alternatives") for width in (1440, 320)
    }
    expected |= {"domain-inspector-1440", "canvas-view-1440", "runtime-attempt-1440", "runtime-attempt-320"}
    assert set(inspection.required_states()) == expected
    assert len(inspection.required_states()) == 18
    assert {row["id"] for row in inspection.PLANNED} == {
        "intermediate-widths",
        "scrolled-detail-content",
        "compact-panes",
        "proposal-failures",
        "formal-and-agent-details",
    }


def test_subject_binds_observed_case_revision_candidate_and_packet_without_full_payload():
    data = payload()
    observed = inspection.case_subject(data)
    assert observed["case_id"] == "CASE-1" and observed["revision"] == 4
    assert observed["semantic_hash"] == "semantic" and observed["subject_hash"] == "subject"
    assert "private" not in str(observed)
    equivalent = copy.deepcopy(data)
    equivalent["case"]["candidate"] = dict(reversed(list(data["case"]["candidate"].items())))
    assert inspection.case_subject(equivalent) == observed
    equivalent["case"]["candidate"]["state"] = "two"
    assert inspection.case_subject(equivalent)["candidate_json_sha256"] != observed["candidate_json_sha256"]
    data["case"]["candidate"] = None
    assert inspection.case_subject(data)["candidate_json_sha256"] is None


class Page:
    def __init__(self):
        self.observed = {"case_id": "CASE-1", "stage": "PREVIEW"}
        self.screenshots = []

    def on(self, *_):
        pass

    def evaluate(self, _):
        return copy.deepcopy(self.observed)

    def screenshot(self, *, path, full_page):
        assert full_page is False
        self.screenshots.append(path)
        Path(path).write_bytes(b"unit-test-image-bytes")


class Recorder:
    def __init__(self):
        self.views = {}

    def settle(self):
        pass

    def checkpoint(self, name):
        self.views[name] = {"geometry": {"innerWidth": 1440}}


@pytest.fixture
def observation(tmp_path):
    result = {"states": [{"id": "example", "status": "NOT_RUN", "reason": "not reached"}]}
    run = inspection.Inspection(Page(), tmp_path, result)
    run.runner = Recorder()
    run.subject = inspection.case_subject(payload())
    return run, result["states"][0]


def test_observation_retains_real_checkpoint_subject_requests_and_screenshot_hash(observation):
    run, row = observation
    run.observe(
        "example", lambda: run.requests.append({"method": "GET", "path": "/api/cases/CASE-1"}), story="US03"
    )
    assert row["status"] == "PASS" and "reason" not in row
    assert row["view"] == "inspection/example"
    assert row["subject"] == inspection.case_subject(payload())
    view = run.runner.views[row["view"]]
    assert view["geometry"] == {"innerWidth": 1440} and view["observed"] == run.page.observed
    assert row["screenshot"] == {
        "path": "inspection/example.png",
        "sha256": hashlib.sha256(b"unit-test-image-bytes").hexdigest(),
    }
    assert len(row["requests"]) == 1


@pytest.mark.parametrize(
    "failure",
    [
        "post",
        "changed-case",
        "changed-candidate",
        "unbound",
        "wrong-visible-case",
        "wrong-visible-stage",
        "prepare-error",
        "image-error",
    ],
)
def test_no_pass_when_preparation_identity_or_read_only_boundary_fails(observation, failure):
    run, row = observation

    def prepare():
        if failure == "post":
            run.requests.append({"method": "POST", "path": "/api/cases/CASE-1/edit"})
        elif failure.startswith("changed-"):
            run.subject = {
                **run.subject,
                "case_id" if failure == "changed-case" else "candidate_json_sha256": "changed",
            }
        elif failure == "unbound":
            run.subject = None
        elif failure == "wrong-visible-case":
            run.page.observed["case_id"] = "CASE-2"
        elif failure == "wrong-visible-stage":
            run.page.observed["stage"] = "APPLIED"
        elif failure == "prepare-error":
            raise JourneyError("native activation failed")
        else:
            run.page.screenshot = lambda **_: (_ for _ in ()).throw(OSError("image failed"))

    with pytest.raises((JourneyError, OSError)):
        run.observe("example", prepare, story="US03")
    assert row["status"] == "FAIL" and row["reason"]
    assert "view" not in row and "screenshot" not in row


def test_response_identity_only_accepts_successful_real_case_get(observation):
    run, _ = observation
    original = run.subject
    for method, status, path in [
        ("POST", 200, "/api/cases/CASE-1"),
        ("GET", 503, "/api/cases/CASE-1"),
        ("GET", 200, "/api/cases"),
        ("GET", 200, "/api/cases/CASE-1/history"),
    ]:
        response = SimpleNamespace(
            request=SimpleNamespace(method=method),
            status=status,
            url="http://127.0.0.1:1" + path,
            json=dict,
        )
        run._response(response)
        assert run.subject == original
    data = payload()
    data["case"]["version"] = 5
    run._response(
        SimpleNamespace(
            request=SimpleNamespace(method="GET"),
            status=200,
            url="http://127.0.0.1:1/api/cases/CASE-1",
            json=lambda: data,
        )
    )
    assert run.subject["revision"] == 5


def test_observation_script_is_read_only_and_setup_selects_use_native_keys():
    for forbidden in (".click(", ".focus(", ".open=", ".open =", ".scrollTop=", ".dispatchEvent(", ".value="):
        assert forbidden not in inspection.OBSERVE.replace("window.__hci.focus()", "readFocus()")
    source = inspect.getsource(inspection.Inspection)
    assert ".select_option(" not in source
    assert 'self.runner.modality = "keyboard"' in source
    assert "replace(step, view=None, audit_visit=None)" in source


def test_error_reason_does_not_export_private_launch_url():
    assert "secret" not in inspection.safe_reason(RuntimeError("failed http://127.0.0.1:1/#secret next"))
    assert inspection.safe_reason(RuntimeError()) == "RuntimeError: "


def test_unavailable_server_retains_every_missing_state_without_claiming_a_pass(tmp_path, monkeypatch):
    def unavailable(*_):
        raise RuntimeError("fixture unavailable http://127.0.0.1:1/#secret")

    monkeypatch.setattr(inspection, "studio_server", unavailable)
    raw = inspection.run_inspection(None, out=tmp_path)
    assert len(raw["states"]) == 18
    assert all(row["status"] == "NOT_RUN" and "fixture unavailable" in row["reason"] for row in raw["states"])
    assert not raw["views"] and len(raw["errors"]) == 2
    assert "secret" not in str(raw)


def test_tooling_hashes_bind_code_probe_and_budget_bytes_but_not_runtime_caches(tmp_path):
    for name, data in {
        "journey.py": b"driver",
        "inspection.py": b"inspection",
        "probe.js": b"probe",
        "budgets.json": b"{}",
    }.items():
        (tmp_path / name).write_bytes(data)
    (tmp_path / "capture.png").write_bytes(b"image")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "inspection.pyc").write_bytes(b"cache")
    observed = journey_module.tooling_hashes(tmp_path)
    assert set(observed) == {"journey.py", "inspection.py", "probe.js", "budgets.json"}
    assert observed["inspection.py"] == hashlib.sha256(b"inspection").hexdigest()
    (tmp_path / "inspection.py").write_bytes(b"changed")
    assert journey_module.tooling_hashes(tmp_path)["inspection.py"] != observed["inspection.py"]
