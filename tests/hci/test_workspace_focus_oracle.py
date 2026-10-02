"""Counterexamples for the actual Workspace replay's native-focus oracle."""
from __future__ import annotations

from importlib import import_module
from pathlib import Path

import pytest

@pytest.fixture
def oracle(monkeypatch):
    pytest.importorskip("playwright.sync_api", reason="NOT_RUN: optional Playwright runtime needed by replay oracle")
    monkeypatch.syspath_prepend(str(Path(__file__).parent))
    return import_module("workspace_shell_review")


def owned(control="close-workspace"):
    return {"tag": "BUTTON", "id": control, "control": control, "inside": True,
            "documentHasFocus": True, "dialogOpen": True, "dialogModal": True}


def boundary():
    return {"tag": "BODY", "id": "", "control": "", "inside": False,
            "documentHasFocus": False, "dialogOpen": True, "dialogModal": True}


def test_only_the_recorded_external_ua_boundary_is_recognized(oracle):
    assert oracle.workspace_focus_kind(boundary()) == "ua_boundary"
    assert oracle.workspace_focus_kind(owned()) == "dialog"


@pytest.mark.parametrize("overrides", [
    {"tag": "BUTTON", "id": "start-intent", "documentHasFocus": True},
    {"tag": "BUTTON", "id": "start-intent"},
    {"tag": "INPUT", "id": "request", "documentHasFocus": True},
    {"documentHasFocus": True},
    {"id": "unexpected-body"},
    {"dialogOpen": False},
    {"dialogModal": False},
    {"inside": True},
    {"documentHasFocus": None},
    {"tag": "HTML"},
])
def test_background_page_and_incomplete_modality_never_count_as_ua_boundary(oracle, overrides):
    with pytest.raises(AssertionError):
        oracle.workspace_focus_kind(boundary() | overrides)


@pytest.mark.parametrize("expected", ["close-workspace", "workspace-layout-summary"])
def test_forward_and_backward_reentry_require_the_exact_boundary_control(oracle, expected):
    oracle.assert_workspace_reentry(owned(expected), expected)
    with pytest.raises(AssertionError, match="wrong dialog control"):
        oracle.assert_workspace_reentry(owned("another-control"), expected)
    with pytest.raises(AssertionError, match="did not return"):
        oracle.assert_workspace_reentry(boundary(), expected)
    with pytest.raises(AssertionError):
        oracle.assert_workspace_reentry(boundary() | {"tag": "BUTTON", "id": "open-workspace"}, expected)


@pytest.mark.parametrize("field", ["dialogOpen", "dialogModal", "documentHasFocus"])
def test_an_inside_node_is_not_success_when_the_document_or_modal_loses_focus(oracle, field):
    with pytest.raises(AssertionError):
        oracle.assert_workspace_reentry(owned() | {field: False}, "close-workspace")
