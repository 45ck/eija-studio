#!/usr/bin/env python3
"""Drive the real Studio (uvicorn on loopback, installed Chrome) to the Visual view and capture the
README screenshots: docs/assets/visual-diff.png and docs/assets/ripple.png.

The case is the excursion demo: baseline vs the recommend_only candidate, created through the offline
fixture provider. Also asserts, in the live browser, that the Studio page raised no Content-Security-Policy
violation and that the diagrams really rendered (SVGs present, no error text). If Chrome or Playwright is
missing the script prints NOT_RUN and exits 3; it never prints PASS without having driven a browser.
"""
from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
ASSETS = ROOT / "docs" / "assets"
SIDECAR = ASSETS / "visual-screenshots.json"


def source_record() -> dict:
    """What the committed PNGs were drawn from: the demo pair's semantic hashes and the vendored renderer.
    tests/test_visual_surface.py compares this with the current model, so a changed model that leaves stale
    screenshots is caught in the fast tier without a browser."""
    from eija_studio.application.diagram_catalog import demo_pair
    before, after = demo_pair()
    vendor = json.loads((ROOT / "src/eija_studio/resources/web/vendor/mermaid.VENDOR.json").read_text(encoding="utf-8"))
    return {"baseline_semantic_hash": before.semantic_hash, "candidate_semantic_hash": after.semantic_hash,
            "mermaid": vendor["version"], "images": ["ripple.png", "studio-visual.png", "visual-diff.png"]}


def start_server(temp: Path) -> tuple[subprocess.Popen, str]:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    log = temp / "server.log"
    log_handle = log.open("w")
    env = os.environ.copy() | {"PYTHONPATH": str(ROOT / "src"), "TMP": str(temp), "TEMP": str(temp)}
    server = subprocess.Popen([sys.executable, "-m", "eija_studio", "serve", "--workspace", str(temp / "workspace"), "--port", str(port)],
                              env=env, stdout=log_handle, stderr=subprocess.STDOUT)
    server.log_handle = log_handle  # closed by the caller after the server stops
    for _ in range(200):
        url = next((line for line in log.read_text().splitlines() if line.startswith("http://127.0.0.1:")), None)
        if url:
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                    return server, url
            except OSError:
                pass
        time.sleep(0.1)
    server.kill()
    raise RuntimeError("server did not start")


def idle(page) -> None:
    """Selector-based wait: Playwright's string predicates are eval'd and the Studio CSP (correctly) forbids eval."""
    page.locator("body:not([aria-busy])").wait_for(state="attached")


def main() -> int:
    try:
        from playwright.sync_api import Error, sync_playwright
    except ImportError:
        print(json.dumps({"status": "NOT_RUN", "reason": "playwright is not installed"}))
        return 3
    ASSETS.mkdir(parents=True, exist_ok=True)
    temp = ROOT / ".tmp" / "visual-capture"
    temp.mkdir(parents=True, exist_ok=True)
    workspace = tempfile.mkdtemp(prefix="run-", dir=temp)
    server, url = start_server(Path(workspace))
    checks = []
    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(channel="chrome", headless=True)
            except Error:
                print(json.dumps({"status": "NOT_RUN", "reason": "Google Chrome not found (Playwright channel 'chrome')"}))
                return 3
            page = browser.new_page(viewport={"width": 1500, "height": 1000}, device_scale_factor=1)
            problems: list[str] = []
            page.on("console", lambda m: problems.append(m.text) if "Content Security Policy" in m.text or (m.type == "error" and "404" not in m.text) else None)
            page.on("pageerror", lambda e: problems.append(str(e)))
            page.on("response", lambda r: problems.append(f"{r.status} {r.url}") if r.status >= 400 and not r.url.endswith("/favicon.ico") else None)
            page.goto(url)
            page.locator("#connection", has_text="offline").wait_for()
            page.click("#create")
            page.wait_for_selector("#workspace:not([hidden])")
            idle(page)
            page.click("#propose")
            page.wait_for_selector(".option")
            idle(page)
            page.get_by_role("button", name="Select this meaning", exact=True).click()
            page.wait_for_selector("#editor:not([hidden])")
            idle(page)
            page.click('[data-tab="visual"]')
            frame = page.frame_locator("#visual-frame")
            frame.locator("#panel-diff svg").wait_for(timeout=30000)
            frame.locator("#panel-impact svg").wait_for(timeout=30000)
            frame.locator("#panel-sequence svg").wait_for(timeout=30000)
            page.wait_for_timeout(800)
            assert frame.locator("p.error").count() == 0, "a panel failed to render"
            checks.append("before, after, diff, ripple and sequence rendered as SVG in the sandboxed frame")
            page.screenshot(path=str(ASSETS / "studio-visual.png"), full_page=False)
            assert "matches the evidence subject" in page.locator("#visual-source").inner_text()
            checks.append("generated-from hash matches the review packet's evidence subject")
            page.select_option("#visual-action", "Reject")
            frame.locator("#panel-sequence h3", has_text="Reject").wait_for()
            page.select_option("#visual-action", "Recommend")
            frame.locator("#panel-sequence h3", has_text="Recommend").wait_for()
            page.wait_for_timeout(1200)
            checks.append("selecting an action redraws the commit protocol")
            frame.locator("#panels").locator("#panel-diff").scroll_into_view_if_needed()
            frame.locator("#panel-diff").screenshot(path=str(ASSETS / "visual-diff.png"))
            frame.locator("#panel-impact").screenshot(path=str(ASSETS / "ripple.png"))
            assert not problems, problems
            checks.append("no CSP violation or JavaScript error on the Studio page or frame")
            browser.close()
    finally:
        server.kill()
        server.wait(timeout=30)
        server.log_handle.close()
        shutil.rmtree(workspace, ignore_errors=True)
    SIDECAR.write_bytes((json.dumps(source_record(), indent=2, sort_keys=True) + "\n").encode("utf-8"))
    print(json.dumps({"status": "PASS", "mode": "real server on loopback + installed Chrome", "checks": checks,
                      "images": ["docs/assets/visual-diff.png", "docs/assets/ripple.png", "docs/assets/studio-visual.png"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
