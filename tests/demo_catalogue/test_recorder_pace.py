"""Scene pacing: a shorter cut tightens holds and motion, never what runs or what is asserted."""
from __future__ import annotations

from types import SimpleNamespace

from demos.lib.recorder import Scene


class _Page:
    def __init__(self) -> None:
        self.viewport_size = {"width": 1440, "height": 900}
        self.waited: list[int] = []

    def wait_for_timeout(self, ms: int) -> None:
        self.waited.append(ms)


def test_pace_scales_waits_and_never_reaches_zero():
    page = _Page()
    scene = Scene(page=page, dry_run=False, pace=0.8)  # type: ignore[arg-type]
    scene.wait(1000)
    scene.wait(1)
    assert page.waited == [800, 1]
    assert Scene(page=page, dry_run=False)._paced(550) == 550  # type: ignore[arg-type]


def test_a_dry_run_never_waits_whatever_the_pace():
    page = _Page()
    Scene(page=page, dry_run=True, pace=2.0).wait(1000)  # type: ignore[arg-type]
    assert page.waited == []


def test_only_a_box_wholly_inside_the_viewport_skips_the_scroll():
    scene = Scene(page=SimpleNamespace(viewport_size={"width": 1440, "height": 900}), dry_run=False)  # type: ignore[arg-type]
    assert scene._on_screen({"x": 10, "y": 10, "width": 100, "height": 40})
    assert not scene._on_screen({"x": 10, "y": 880, "width": 100, "height": 40})
    assert not scene._on_screen({"x": -5, "y": 10, "width": 100, "height": 40})
