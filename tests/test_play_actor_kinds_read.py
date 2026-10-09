"""PlayIDE draws an AI agent, a timer and an external system the same way in every view, in a real browser, at the
1600-pixel width the demo is recorded at: a box marked «agent», «timer» or «system» in the use case diagram's
colours on the Components tab's System lens and on the Sequences tab (a person stays a stick figure), a tag under
the role on the Permissions tab, and nothing on the Components tab hidden under its lens bar.

Marked `browser`: it runs only with EIJA_BROWSER_TESTS=1 (NOT_RUN otherwise). It uses the installed Chrome, or the
Chromium at EIJA_CHROMIUM, and never downloads a browser.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from test_play_place import _launch

ROOT = Path(__file__).resolve().parents[1]

# How each actor is drawn on a diagram, by the id its head has there: "actor" for a stick figure, else its fill.
LOOKS = """([key, prefix]) => { const g = window.PlayIDE.diagram(key), out = {};
    for (const c of Object.values(g.getDataModel().cells || {})) {
        if (!c.id || !c.id.startsWith(prefix)) continue;
        const s = g.getCellStyle(c); out[c.id.slice(prefix.length)] = s.shape === "actor" ? "actor" : s.fillColor; }
    return out; }"""
# The lowest edge of the lens bar, and the highest drawn shape under it, in page pixels.
UNDER_BAR = """() => { const g = window.PlayIDE.diagram("components"), bar = document.getElementById("component-bar").getBoundingClientRect();
    const box = g.container.getBoundingClientRect();
    const tops = Object.values(g.getDataModel().cells || {}).filter((c) => c.isVertex && c.isVertex()).map((c) => g.view.getState(c))
        .filter((s) => s && box.left + s.x < bar.right).map((s) => box.top + s.y);
    return [bar.bottom, Math.min(...tops)]; }"""


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")
def test_agents_timers_and_systems_look_the_same_in_every_view():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=ROOT / "packs/refund-desk") as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 900})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            page.click("#tab-usecases")
            usecases = page.evaluate(LOOKS, ["usecases", "role:"])
            assert usecases["Customer"] == "actor" and usecases["SupportAgent"] != "actor"
            # The System lens draws each actor as the use case diagram does, and clear of the lens bar.
            page.click("#tab-components")
            page.click("#component-lens [data-lens=system]")
            page.wait_for_selector("#landscape-summary:not(:empty)")
            # Workflows beside this one may declare a role too (card-payment shares the refund class): where they agree, the
            # lens draws the role as here; where they differ, it is a box naming each kind.
            lens = page.evaluate(LOOKS, ["components", "system:actor:"])
            kinds = page.evaluate("() => Object.fromEntries(window.PlayLandscape.result().actors.map((a) => [a.name, a.kinds]))")
            assert all(lens[role] == look for role, look in usecases.items() if len(kinds[role]) == 1), (lens, usecases, kinds)
            for role in (r for r in usecases if len(kinds[r]) > 1):
                label = page.evaluate("(id) => window.PlayIDE.diagram('components').getDataModel().getCell(id).value", "system:actor:" + role)
                assert label.startswith("«" + " | ".join(kinds[role]) + "»"), label
            bar, top = page.evaluate(UNDER_BAR)
            assert top >= bar, f"a shape at {top} is under the lens bar, which ends at {bar}"
            page.click("#component-lens [data-lens=app]")
            page.wait_for_timeout(300)  # the lens switch refits
            bar, top = page.evaluate(UNDER_BAR)
            assert top >= bar, f"a shape at {top} is under the lens bar, which ends at {bar}"
            # The Sequences tab's lifelines too, by role.
            page.click("#tab-sequences")
            page.wait_for_selector("#sequence-canvas svg")
            heads = page.evaluate(LOOKS, ["sequences", "head:actor:"])
            roles = page.evaluate("() => Object.fromEntries([...document.querySelectorAll('#seq-actor option')].map((o) => o.textContent.split(' : ')))")
            assert heads and all(look == usecases[roles[actor]] for actor, look in heads.items()), (heads, roles)
            # The Permissions tab names the kind under each role that is not a person.
            page.click("#tab-access")
            page.wait_for_selector(".access-grid th")
            tags = page.evaluate("() => [...document.querySelectorAll('.access-grid th[scope=col]')].map((t) => t.textContent)")
            assert "SupportAgentAI agent" in tags and "SlaTimertimer" in tags and "PaymentGatewayexternal system" in tags and "Customer" in tags
            assert errors == []
        finally:
            chrome.close()
