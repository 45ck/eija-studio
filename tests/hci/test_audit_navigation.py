"""Disclosure navigation remains a real, unmodelled audit action, not a hidden-control shortcut."""
from __future__ import annotations

import pytest

from quality.hci import journey


class AuditPage:
    def __init__(self, *, hidden=False, disclosure=True, opens=True):
        self.hidden, self.disclosure, self.opens = hidden, disclosure, opens
        self.events = []

    def on(self, *_):
        pass

    def locator(self, selector):
        return AuditLocator(self, selector)


class AuditLocator:
    def __init__(self, page, selector):
        self.page, self.selector = page, selector

    def is_visible(self):
        return not self.page.hidden

    def count(self):
        return int(self.page.disclosure)

    def get_attribute(self, name):
        assert name == "open"
        return None if self.page.hidden else ""

    def locator(self, selector):
        assert self.selector == "#reference-views" and selector == "summary"
        return AuditLocator(self.page, "summary")

    def click(self):
        self.page.events.append(("click", self.selector))
        if self.selector == "summary":
            if self.page.opens:
                self.page.hidden = False
        elif self.page.hidden:
            raise RuntimeError("The reference target is still hidden")


def audit(page, monkeypatch):
    runner = journey.Runner(page, "pointer", audit=True)
    monkeypatch.setattr(runner, "settle", lambda: page.events.append(("settle", None)))
    monkeypatch.setattr(runner, "checkpoint", lambda name: page.events.append(("checkpoint", name)))
    runner._audit_visit("impact")
    assert runner.operators == [] and runner.steps == []  # coverage visit is explicitly outside the modelled journey


def test_hidden_reference_is_opened_by_clicking_the_native_summary_before_its_target(monkeypatch):
    page = AuditPage(hidden=True)
    audit(page, monkeypatch)
    assert page.events == [
        ("click", "summary"), ("settle", None),
        ("click", '[data-tab="impact"]'), ("settle", None), ("checkpoint", "impact-tab"),
    ]


def test_visible_reference_needs_no_disclosure_action(monkeypatch):
    page = AuditPage()
    audit(page, monkeypatch)
    assert page.events == [("click", '[data-tab="impact"]'), ("settle", None), ("checkpoint", "impact-tab")]


def test_work_area_choice_counts_the_reference_branch_as_well_as_primary_tabs():
    assert ".tabs button" in journey.TABS.selectors
    assert "#reference-views > summary" in journey.TABS.selectors


@pytest.mark.parametrize("disclosure,opens", [(False, True), (True, False)])
def test_a_missing_or_broken_disclosure_does_not_fabricate_a_successful_audit(monkeypatch, disclosure, opens):
    page = AuditPage(hidden=True, disclosure=disclosure, opens=opens)
    with pytest.raises(RuntimeError, match="still hidden"):
        audit(page, monkeypatch)
    assert not any(event == "checkpoint" for event, _ in page.events)
