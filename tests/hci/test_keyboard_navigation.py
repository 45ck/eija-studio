"""Deterministic driver checks; these model keyboard behavior, not browser conformance."""
from __future__ import annotations

import pytest

from quality.hci import journey


class KeyPage:
    """A roving-tabindex tablist between two ordinary Tab stops.

    Focus changes only through keyboard.press. The driver cannot use direct focus,
    locator activation, JavaScript mutation or another unrecorded shortcut.
    """

    tabs = ("model", "code", "change", "try", "evidence")

    def __init__(self, *, selected=0, focused="before", vertical=False, broken=(), enter_loses_focus=False):
        self.selected = selected
        self.focused = focused
        self.vertical = vertical
        self.broken = set(broken)
        self.enter_loses_focus = enter_loses_focus
        self.keyboard = self
        self.keys = []
        self.observed = []

    def on(self, *_):
        pass

    def locator(self, name):
        return KeyLocator(self, name)

    def press(self, key):
        self.keys.append(key)
        if key not in self.broken:
            self._move(key)
        self.observed.append(self.focus_snapshot())

    def _move(self, key):
        if key == "Tab":
            order = ("before", self.tabs[self.selected], "after")
            self.focused = order[(order.index(self.focused) + 1) % len(order)] if self.focused in order else order[0]
            return
        if key == "Enter":
            if self.enter_loses_focus:
                self.focused = "body"
            return
        if key not in {"ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "Home", "End"}:
            raise AssertionError(f"Unexpected key {key}")
        if self.focused not in self.tabs:
            return
        previous, following = ("ArrowUp", "ArrowDown") if self.vertical else ("ArrowLeft", "ArrowRight")
        if key == "Home":
            self.selected = 0
        elif key == "End":
            self.selected = len(self.tabs) - 1
        elif key == following:
            self.selected = (self.selected + 1) % len(self.tabs)
        elif key == previous:
            self.selected = (self.selected - 1) % len(self.tabs)
        self.focused = self.tabs[self.selected]

    def focus_snapshot(self):
        lost = self.focused == "body"
        return {
            "name": self.focused, "selector": f"#{self.focused}", "visible_ring": not lost,
            "focus_visible": not lost, "lost": lost,
            "rect": None if lost else {"x": 20, "y": 20, "w": 80, "h": 30},
        }

    def evaluate(self, source, *_):
        if source == "() => window.__hci.focus()":
            return self.focus_snapshot()
        raise AssertionError(f"Unexpected page evaluation (possible navigation bypass): {source}")


class KeyLocator:
    def __init__(self, page, name):
        self.page = page
        self.name = name

    def evaluate(self, source, *_):
        assert not any(token in source for token in (".focus(", ".click(", ".dispatchEvent(", ".tabIndex ="))
        if source == "(el) => el === document.activeElement":
            return self.page.focused == self.name
        if "window.__hci.targetOf(el)" in source:
            box = {"x": 20, "y": 20, "w": 80, "h": 30}
            return {"name": self.name, "selector": f"#{self.name}", "effective": box, "raw": box}
        if "tablist" in source:
            if self.name not in self.page.tabs or self.page.focused not in self.page.tabs:
                return None
            return {"current": self.page.tabs.index(self.page.focused),
                    "target": self.page.tabs.index(self.name), "vertical": self.page.vertical}
        raise AssertionError(f"Unexpected locator evaluation: {source}")

    def focus(self, *_):
        raise AssertionError("Direct locator.focus bypasses keyboard navigation")

    def click(self, *_):
        raise AssertionError("Locator.click bypasses keyboard activation")

    def press(self, *_):
        raise AssertionError("Locator.press can focus implicitly; use page.keyboard.press")


def _run(page, name, *, click=False, monkeypatch=None):
    runner = journey.Runner(page, "keyboard", audit=False)
    step = journey.Step("navigate", "Navigate with keys", "click", journey.Ref(css=f"#{name}"))
    record = {}
    if click:
        def record_interaction(item):
            item["interaction"] = {"kind": "keyboard"}
            item["focus_lost_after"] = page.focused == "body"

        monkeypatch.setattr(runner, "_record_interaction", record_interaction)
        runner._do_click(step, page.locator(name), record)
    else:
        runner._focus_to(step, page.locator(name), record)
    return runner, record


def _assert_trace(page, runner, record, expected):
    assert page.keys == expected
    assert [op["note"] for op in runner.operators if op["op"] == "K"] == expected
    assert record["tab_presses"] == expected.count("Tab")
    assert record["navigation_keys"] == [key for key in expected if key != "Enter"]
    assert len(record["focus_stops"]) == len(expected)
    for key, actual, observed in zip(expected, record["focus_stops"], page.observed, strict=True):
        assert actual["key"] == key
        assert all(actual[field] == value for field, value in observed.items())


def test_ordinary_control_uses_real_tabs_and_records_each_stop():
    page = KeyPage()
    runner, record = _run(page, "after")
    _assert_trace(page, runner, record, ["Tab", "Tab"])
    assert page.focused == "after"
    assert record["target"]["selector"] == "#after"


def test_inactive_tab_is_reached_through_the_roving_tabstop_and_arrow_keys():
    page = KeyPage()
    runner, record = _run(page, "try")
    _assert_trace(page, runner, record, ["Tab", "ArrowRight", "ArrowRight", "ArrowRight"])
    assert page.focused == "try" and page.selected == 3


def test_first_tab_is_reached_with_home_after_entering_the_tablist():
    page = KeyPage(selected=3)
    runner, record = _run(page, "model")
    _assert_trace(page, runner, record, ["Tab", "Home"])
    assert page.focused == "model" and page.selected == 0


def test_an_earlier_nonfirst_tab_uses_left_arrow_without_invented_tab_presses():
    page = KeyPage(selected=4, focused="evidence")
    runner, record = _run(page, "change")
    _assert_trace(page, runner, record, ["ArrowLeft", "ArrowLeft"])
    assert page.focused == "change" and record["tab_presses"] == 0


@pytest.mark.parametrize(("selected", "focused", "target", "expected"), [
    (1, "code", "change", ["ArrowDown"]),
    (3, "try", "code", ["ArrowUp", "ArrowUp"]),
])
def test_vertical_tablists_use_their_keyboard_axis(selected, focused, target, expected):
    page = KeyPage(selected=selected, focused=focused, vertical=True)
    runner, record = _run(page, target)
    _assert_trace(page, runner, record, expected)
    assert page.focused == target


def test_already_focused_control_does_not_invent_navigation():
    page = KeyPage(focused="after")
    runner, record = _run(page, "after")
    _assert_trace(page, runner, record, [])
    assert record["target"]["selector"] == "#after"


def test_unsupported_home_falls_back_to_real_arrow_navigation_once():
    page = KeyPage(selected=3, focused="try", broken={"Home"})
    runner, record = _run(page, "model")
    _assert_trace(page, runner, record, ["Home", "ArrowLeft", "ArrowLeft", "ArrowLeft"])
    assert page.focused == "model"


@pytest.mark.parametrize("lose_focus", [False, True])
def test_enter_activation_has_its_own_operator_and_focus_observation(monkeypatch, lose_focus):
    page = KeyPage(enter_loses_focus=lose_focus)
    runner, record = _run(page, "code", click=True, monkeypatch=monkeypatch)
    _assert_trace(page, runner, record, ["Tab", "ArrowRight", "Enter"])
    assert record["focus_stops"][-1]["lost"] is lose_focus
    assert record["focus_lost_after"] is lose_focus
    assert record["interaction"]["kind"] == "keyboard"


@pytest.mark.parametrize("target", ["code", "unreachable"])
def test_broken_navigation_fails_within_the_existing_budget_and_keeps_observations(target):
    page = KeyPage(focused="model", broken={"ArrowRight"})
    runner = journey.Runner(page, "keyboard", audit=False)
    step = journey.Step("blocked", "Blocked navigation", "click", journey.Ref(css=f"#{target}"))
    record = {}
    with pytest.raises(journey.JourneyError, match="not reachable"):
        runner._focus_to(step, page.locator(target), record)
    expected = ["ArrowRight" if target == "code" else "Tab"] * journey.MAX_TABS
    _assert_trace(page, runner, record, expected)
    assert journey.MAX_TABS == 150
    assert page.focused != target
