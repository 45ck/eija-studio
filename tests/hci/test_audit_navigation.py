"""Workspace audit navigation records real gestures and choices without hidden-control shortcuts."""
from __future__ import annotations

import pytest

from quality.hci import journey


WORKSPACE_VIEWS = ("model", "code", "change", "review", "try", "evidence", "impact", "visual", "source")


class AuditPage:
    def __init__(self, *, primary=(), dialog_open=False, opener=True, opens=True,
                 views=WORKSPACE_VIEWS, visible_choices=None, disabled=()):
        self.primary, self.dialog_open, self.opener, self.opens = primary, dialog_open, opener, opens
        self.views = views
        self.disabled = disabled
        self.visible_choices = len(views) if visible_choices is None else visible_choices
        self.events = []

    def on(self, *_):
        pass

    def locator(self, selector):
        return AuditLocator(self, selector)

    def evaluate(self, expression, argument=None):
        if expression == "(s) => window.__hci.choices(s)":
            assert argument == ["#workspace-dialog [data-workspace-view]"]
            assert self.dialog_open
            return self.visible_choices
        assert expression == "() => window.__hci.geometry()"
        return {"innerWidth": 1440, "innerHeight": 900}


class AuditLocator:
    def __init__(self, page, selector):
        self.page, self.selector = page, selector

    def is_visible(self):
        if self.selector == "#workspace-dialog":
            return self.page.dialog_open
        if self.selector == "#open-workspace":
            return self.page.opener
        if self.selector.startswith('[data-workspace-view="'):
            return self.page.dialog_open and self.count() == 1
        return self.count() == 1

    def count(self):
        if self.selector.startswith('[data-tab="'):
            return int(self.selector.split('"')[1] in self.page.primary)
        if self.selector.startswith('[data-workspace-view="'):
            return self.page.views.count(self.selector.split('"')[1])
        if self.selector == "#open-workspace":
            return int(self.page.opener)
        return 1

    def evaluate_all(self, _):
        assert self.selector == "#workspace-dialog [data-workspace-view]"
        return [{"view": view, "name": view.title(), "disabled": view in self.page.disabled}
                for view in self.page.views]

    def click(self):
        if not self.is_visible():
            raise RuntimeError("The navigation target is unavailable")
        self.page.events.append(("click", self.selector))
        if self.selector == "#open-workspace":
            if self.page.opens:
                self.page.dialog_open = True
        elif self.selector.startswith('[data-workspace-view="'):
            self.page.dialog_open = False


def audit(page, monkeypatch, tab="impact"):
    runner = journey.Runner(page, "pointer", audit=True)
    monkeypatch.setattr(runner, "settle", lambda: page.events.append(("settle", None)))

    def checkpoint(name):
        page.events.append(("checkpoint", name))
        runner.views[name] = {}

    monkeypatch.setattr(runner, "checkpoint", checkpoint)
    runner._audit_visit(tab)
    assert runner.operators == [] and runner.steps == []  # coverage visit is explicitly outside the modelled journey
    return runner


def test_auxiliary_view_opens_workspace_and_observes_all_choices_before_its_target(monkeypatch):
    page = AuditPage()
    runner = audit(page, monkeypatch)
    assert page.events == [
        ("click", "#open-workspace"), ("settle", None),
        ("checkpoint", "workspace-menu-1440-impact"),
        ("click", '[data-workspace-view="impact"]'), ("settle", None), ("checkpoint", "impact-tab"),
    ]
    assert [event["action"] for event in runner.audit_navigation] == ["click", "observe_choices", "click"]
    observed = runner.audit_navigation[1]
    assert observed["inventory_count"] == 9
    assert observed["n_choices"] == 9
    assert [choice["view"] for choice in observed["choices"]] == list(WORKSPACE_VIEWS)
    assert runner.views["workspace-menu-1440-impact"]["work_view_choices"] == observed
    assert not page.dialog_open


def test_visible_primary_needs_no_workspace_action(monkeypatch):
    page = AuditPage(primary=("model",))
    runner = audit(page, monkeypatch, "model")
    assert page.events == [("click", '[data-tab="model"]'), ("settle", None), ("checkpoint", "model-tab")]
    assert runner.audit_navigation == [{"action": "click", "selector": '[data-tab="model"]', "view": "model"}]


def test_work_area_choice_counts_workspace_as_well_as_primary_buttons():
    assert ".tabs button" in journey.TABS.selectors
    assert "#open-workspace" in journey.TABS.selectors


@pytest.mark.parametrize("opener,opens", [(False, True), (True, False)])
def test_a_missing_or_broken_workspace_does_not_fabricate_a_successful_audit(monkeypatch, opener, opens):
    page = AuditPage(opener=opener, opens=opens)
    with pytest.raises((RuntimeError, journey.JourneyError)):
        audit(page, monkeypatch)
    assert not any(event == "checkpoint" for event, _ in page.events)


@pytest.mark.parametrize("views,visible_choices,disabled", [
    (WORKSPACE_VIEWS[:-1], 8, ()), (WORKSPACE_VIEWS, 8, ("source",)),
    ((*WORKSPACE_VIEWS[:-1], "model"), 9, ()), (WORKSPACE_VIEWS, 0, ()),
    (WORKSPACE_VIEWS, 10, ()),
])
def test_missing_disabled_duplicate_or_invalid_menu_choices_are_not_reported_as_complete(
        monkeypatch, views, visible_choices, disabled):
    page = AuditPage(views=views, visible_choices=visible_choices, disabled=disabled)
    with pytest.raises(journey.JourneyError, match="all nine"):
        audit(page, monkeypatch)
    assert not any(event == "checkpoint" for event, _ in page.events)


def test_scrolled_menu_records_visible_choices_separately_from_all_available_routes(monkeypatch):
    page = AuditPage(visible_choices=4)
    runner = audit(page, monkeypatch)
    observed = runner.audit_navigation[1]
    assert observed["inventory_count"] == 9 and observed["n_choices"] == 4
    assert len(observed["choices"]) == 9
    assert observed["geometry"] == {"innerWidth": 1440, "innerHeight": 900}
    assert runner.views["workspace-menu-1440-impact"]["work_view_choices"] == observed


def test_an_already_open_workspace_is_observed_without_reopening_it(monkeypatch):
    page = AuditPage(dialog_open=True, primary=("model",))
    runner = audit(page, monkeypatch, "model")
    assert ("click", "#open-workspace") not in page.events
    assert [event["action"] for event in runner.audit_navigation] == ["observe_choices", "click"]
    assert runner.audit_navigation[-1]["selector"] == '[data-workspace-view="model"]'
    assert not page.dialog_open
