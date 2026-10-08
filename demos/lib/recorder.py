"""Cursor motion, natural typing and caption overlays for scripted demo recordings.

This module knows nothing about EIJA. It drives a real Chromium page (via Playwright) with a
synthetic on-page cursor (Chromium does not render the OS pointer into recorded video) whose motion
is eased across the path, and with per-character typing delay so recordings read as a person working,
not a script executing.

Two modes share one code path:

* **record** — cursor overlay, easing, typing cadence, captions, video capture.
* **dry run** — the *same interactions* (real clicks, real form input, real assertions) with the
  cosmetics skipped: no video, no overlay, no delays. A scenario that references a control the Studio
  no longer has fails here, so demos double as a fast scripted UI regression check.
"""
# ruff: noqa: PLC0415
# PLC0415 (import outside top level) is intentional in this file: Playwright is the optional `demos` extra,
# so it is imported lazily inside the functions that need it. That keeps `import demos.lib` (and therefore
# `python -m demos list|registry`) working without it; the CLI preflights the extra and reports NOT_RUN.
from __future__ import annotations

import random
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from playwright.sync_api import Page

# Injected once per page. Deliberately asset-free so a scenario needs nothing beyond Playwright.
_OVERLAY_CSS = """
#__demo_cursor{position:fixed;z-index:2147483647;width:26px;height:26px;margin:-13px 0 0 -13px;
  border-radius:50%;background:rgba(20,20,20,.9);border:3px solid #fff;
  box-shadow:0 2px 8px rgba(0,0,0,.45);pointer-events:none;transition:transform .12s ease;top:0;left:0}
.__demo_ring{position:fixed;z-index:2147483646;width:26px;height:26px;margin:-13px 0 0 -13px;
  border-radius:50%;border:3px solid rgba(255,176,32,.95);pointer-events:none;
  animation:__demo_ring .55s ease-out forwards}
@keyframes __demo_ring{from{transform:scale(1);opacity:1}to{transform:scale(3.2);opacity:0}}
#__demo_card{position:fixed;inset:0;z-index:2147483645;display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:14px;background:#14261f;color:#fff;
  font-family:system-ui,sans-serif;text-align:center;opacity:0;pointer-events:none;
  transition:opacity .5s ease}
#__demo_card.show{opacity:1}
#__demo_card h1{font-size:54px;margin:0;font-weight:700;letter-spacing:-.02em}
#__demo_card p{font-size:22px;margin:0;opacity:.8;max-width:900px}
#__demo_caption{position:fixed;z-index:2147483646;left:50%;bottom:32px;transform:translateX(-50%);
  max-width:80vw;padding:10px 18px;border-radius:8px;background:rgba(20,20,20,.88);color:#fff;
  font:500 18px/1.45 system-ui,sans-serif;text-align:center;pointer-events:none;opacity:0;
  transition:opacity .25s ease}
#__demo_caption.show{opacity:1}
.__demo_highlight{outline:3px solid #ffb020 !important;outline-offset:2px !important}
"""
_OVERLAY_JS = (
    "() => { for (const id of ['__demo_cursor','__demo_caption','__demo_card']) { "
    "if (!document.getElementById(id)) { const d=document.createElement('div'); d.id=id; "
    "document.body.appendChild(d); } } }"
)
_VISIBLE_TIMEOUT_MS = 10_000


@dataclass
class Scene:
    """The narration surface a scenario script calls into. One Scene per take."""

    page: Page
    dry_run: bool
    seed: int = 0
    skipped: list[str] = field(default_factory=list)
    _cursor: tuple[float, float] = (0.0, 0.0)
    _rng: random.Random = field(init=False)

    def __post_init__(self) -> None:
        # Typing cadence only: it needs to look human, not be unpredictable; the seed just fixes the cadence.
        self._rng = random.Random(self.seed)  # noqa: S311

    # -- lifecycle --------------------------------------------------------------------------------

    def goto(self, url: str) -> None:
        """Navigate and (re)install the overlay, which a navigation would have discarded."""
        self.page.goto(url)
        self.page.wait_for_load_state("domcontentloaded")
        if not self.dry_run:
            self.page.add_style_tag(content=_OVERLAY_CSS)
            self.page.evaluate(_OVERLAY_JS)

    def wait_for(self, selector: str, *, timeout_ms: int = _VISIBLE_TIMEOUT_MS) -> None:
        """Wait (in both modes) until `selector` matches, e.g. until startup requests have finished."""
        self.page.wait_for_selector(selector, state="attached", timeout=timeout_ms)

    def skip(self, reason: str) -> None:
        """Record that part of a scenario could not run (missing prerequisite). Never silent."""
        self.skipped.append(reason)

    # -- interaction primitives (same effect in both modes) ---------------------------------------

    def move_to(self, target: str, *, duration_ms: int = 550) -> None:
        """Ease the cursor to an element's centre. `target` is a Playwright selector."""
        locator = self.page.locator(target).first
        locator.wait_for(state="visible", timeout=_VISIBLE_TIMEOUT_MS)
        if self.dry_run:
            return
        locator.evaluate("el => el.scrollIntoView({behavior: 'smooth', block: 'center'})")
        self.page.wait_for_timeout(650)  # let the smooth scroll settle before measuring
        box = locator.bounding_box()
        if box is None:
            raise ValueError(f"target has no layout box: {target!r}")
        self._animate_to(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, duration_ms)

    def click(self, target: str, *, duration_ms: int = 550) -> None:
        self.move_to(target, duration_ms=duration_ms)
        self._press_feedback()
        self.page.locator(target).first.click()

    def type_text(self, target: str, text: str, *, clear: bool = False,
                  delay_range_ms: tuple[int, int] = (35, 120)) -> None:
        """Click into `target`, optionally clear it, then enter `text`.

        Record mode types one character at a time with varied delay; dry run fills instantly."""
        self.click(target)
        locator = self.page.locator(target).first
        if clear:
            locator.fill("")
        if self.dry_run:
            locator.fill(text)
            return
        low, high = delay_range_ms
        for char in text:
            locator.press_sequentially(char, delay=0)
            time.sleep(self._rng.uniform(low, high) / 1000)

    def select_option(self, target: str, value: str) -> None:
        self.move_to(target)
        self._press_feedback()
        self.page.locator(target).first.select_option(value)

    def check(self, target: str) -> None:
        self.move_to(target)
        self._press_feedback()
        self.page.locator(target).first.check()

    # -- narration and assertions -----------------------------------------------------------------

    def highlight(self, target: str, *, duration_ms: int = 900) -> None:
        """Briefly outline an element to draw the eye without interacting with it."""
        locator = self.page.locator(target).first
        locator.wait_for(state="visible", timeout=_VISIBLE_TIMEOUT_MS)
        if self.dry_run:
            return
        locator.evaluate(
            "(el, ms) => { el.classList.add('__demo_highlight'); "
            "setTimeout(() => el.classList.remove('__demo_highlight'), ms); }",
            duration_ms,
        )
        self.wait(duration_ms)

    def caption(self, text: str, *, hold_ms: int | None = None) -> None:
        """Narrate: show `text`, then hold long enough to read it *before* the next action runs.

        The caption stays up until the next caption or `clear_caption()`, so the words never
        disappear while the viewer is still looking at the thing they describe."""
        if not text.strip():
            raise ValueError("caption text must not be empty")
        if self.dry_run:
            return
        self.page.evaluate(
            # A modal <dialog> paints in the top layer, above the overlay: move caption and cursor into it.
            "(t) => { const c=document.getElementById('__demo_caption'); if(!c) return; "
            "const host=document.querySelector('dialog[open]:modal') || document.body; "
            "host.append(c); const k=document.getElementById('__demo_cursor'); if(k) host.append(k); "
            "c.textContent=t; c.classList.add('show'); }",
            text,
        )
        self.wait(hold_ms if hold_ms is not None else max(1400, 55 * len(text)))

    def clear_caption(self) -> None:
        if not self.dry_run:
            self.page.evaluate("() => document.getElementById('__demo_caption')?.classList.remove('show')")

    def title_card(self, title: str, subtitle: str = "", *, hold_ms: int = 2600) -> None:
        """Full-screen title/end card that fades in over the page and out again."""
        if not title.strip():
            raise ValueError("title must not be empty")
        if self.dry_run:
            return
        self.clear_caption()
        self.page.evaluate(
            "([t, s]) => { const c=document.getElementById('__demo_card'); if(!c) return; "
            "c.replaceChildren(); const h=document.createElement('h1'); h.textContent=t; c.append(h); "
            "if (s) { const p=document.createElement('p'); p.textContent=s; c.append(p); } "
            "c.classList.add('show'); }",
            [title, subtitle],
        )
        self.wait(hold_ms)
        self.page.evaluate("() => document.getElementById('__demo_card')?.classList.remove('show')")
        self.wait(550)

    def expect_text(self, target: str, needle: str, *, timeout_ms: int = 15_000) -> None:
        """Assert (in both modes) that `target` shows `needle`: the demo is also an e2e check."""
        from playwright.sync_api import expect

        expect(self.page.locator(target).first).to_contain_text(needle, timeout=timeout_ms)

    def wait(self, ms: int) -> None:
        if not self.dry_run:
            self.page.wait_for_timeout(ms)

    # -- internals --------------------------------------------------------------------------------

    def _animate_to(self, x: float, y: float, duration_ms: int, *, steps: int = 18) -> None:
        start_x, start_y = self._cursor
        for i in range(1, steps + 1):
            t = i / steps
            eased = t * t * (3 - 2 * t)  # smoothstep: ease-in/out without an easing dependency
            cx, cy = start_x + (x - start_x) * eased, start_y + (y - start_y) * eased
            self.page.mouse.move(cx, cy)
            self.page.evaluate(
                "([x, y]) => { const c=document.getElementById('__demo_cursor'); "
                "if (c) { c.style.left = x+'px'; c.style.top = y+'px'; } }",
                [cx, cy],
            )
            self.page.wait_for_timeout(max(1, duration_ms // steps))
        self._cursor = (x, y)

    def _press_feedback(self) -> None:
        if self.dry_run:
            return
        self.page.evaluate(
            "() => { const c=document.getElementById('__demo_cursor'); if(!c) return; "
            "c.style.transform='scale(.75)'; setTimeout(() => c.style.transform='scale(1)', 140); "
            "const r=document.createElement('div'); r.className='__demo_ring'; "
            "r.style.left=c.style.left; r.style.top=c.style.top; document.body.appendChild(r); "
            "setTimeout(() => r.remove(), 600); }"
        )
        self.page.wait_for_timeout(180)


class BrowserUnavailableError(RuntimeError):
    """The browser could not be launched (Chrome not installed, sandbox refused): a missing prerequisite,
    reported as NOT_RUN by the CLI. Errors raised while a scenario runs are not this type: those fail."""


class Recorder:
    """Launches the installed system Chrome (no browser download) and yields a `Scene`."""

    def __init__(self, *, headless: bool = True, viewport: tuple[int, int] = (1440, 900)) -> None:
        self.headless = headless
        self.viewport = viewport

    @contextmanager
    def session(self, out_dir: Path, *, dry_run: bool = False, seed: int = 0) -> Iterator[Scene]:
        """Yield a `Scene` on a real page. In record mode the video lands under `out_dir`; a dry run
        writes nothing to disk."""
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright

        size = {"width": self.viewport[0], "height": self.viewport[1]}
        with sync_playwright() as pw:
            try:
                browser = pw.chromium.launch(channel="chrome", headless=self.headless)
            except PlaywrightError as error:
                raise BrowserUnavailableError(f"could not launch the system Chrome: {error}") from error
            options: dict[str, Any] = {"viewport": size}
            if not dry_run:
                out_dir.mkdir(parents=True, exist_ok=True)
                # The Studio ships a strict CSP (style-src 'self'), which rightly blocks the injected
                # cursor/caption styles. Bypass it for this recording context ONLY; the app's own
                # policy is untouched and dry runs (which inject nothing) keep the real CSP.
                options.update(record_video_dir=str(out_dir), record_video_size=size, bypass_csp=True)
            context = browser.new_context(**options)
            page = context.new_page()
            try:
                yield Scene(page=page, dry_run=dry_run, seed=seed)
            finally:
                context.close()  # flushes the video file (if any) to out_dir
                browser.close()
