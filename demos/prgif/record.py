"""Record a page with the existing demos harness (`demos.lib.Recorder`: system Chrome, Playwright video)."""
from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from demos.lib import Recorder, Scene


@dataclass(frozen=True)
class Take:
    video: Path
    lead_in_s: float  # blank time before the first page load; trimmed from the GIF
    skipped: tuple[str, ...]


def record(out_dir: Path, act: Callable[[Scene], None], *, viewport: tuple[int, int], headed: bool) -> Take:
    """Run `act` on a recorded page and return the new video.

    Raises `demos.lib.BrowserUnavailableError` when Chrome cannot be launched (NOT_RUN for the caller)."""
    before = set(out_dir.glob("*.webm")) if out_dir.exists() else set()
    loaded: list[float] = []
    with Recorder(headless=not headed, viewport=viewport).session(out_dir) as scene:
        started = time.monotonic()
        scene.page.once("load", lambda *_: loaded.append(time.monotonic() - started))
        act(scene)
        skipped = tuple(scene.skipped)
    new = sorted(set(out_dir.glob("*.webm")) - before, key=lambda p: p.stat().st_mtime)
    if not new:
        raise RuntimeError("the browser produced no video")
    return Take(video=new[-1], lead_in_s=loaded[0] if loaded else 0.0, skipped=skipped)
