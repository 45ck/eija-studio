"""The accessibility check on the generated screens (ADR-0218): each check against its WCAG 2.2 AA criteria, and each
able to fail (a negative oracle per check), so a pass on the shipped templates means something."""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eija_studio.application.screen_access import check_accessibility, contrast, themes
from eija_studio.domain.data import data_for
from eija_studio.domain.pack import load_pack
from eija_studio.domain.screens import CREATE, Screens, screens_for
from eija_studio.interfaces.http import create_app
from kernel_support import harness_studio

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "src/eija_studio/resources/appgen/web"
LOAN = load_pack(ROOT / "packs" / "library-loan")
EXCURSION = load_pack(ROOT / "packs" / "excursion")
CSS, JS, HTML = ((APP / name).read_text(encoding="utf-8") for name in ("app.css.tmpl", "app.js.tmpl", "index.html.tmpl"))


def report(screens: Screens | None = None, pack=LOAN, *, css: str = CSS, js: str = JS, html: str = HTML) -> dict[str, str]:
    screens = screens or screens_for(pack, pack.model, data_for(pack))
    result = check_accessibility(screens, pack.model, data_for(pack), theme_css=css, page_js=js, page_html=html)
    return {c["check"]: c["status"] for c in result["checks"]}


def edited(screens: Screens, which, **change) -> Screens:
    document = screens.model_dump(mode="json")
    for screen in document["screens"]:
        if screen["use_case"] == which:
            screen.update(change)
    return Screens.model_validate(document)


def test_the_shipped_page_and_the_library_screens_pass_every_check():
    assert set(report().values()) == {"PASS"}
    assert len(report()) == 9


def test_contrast_is_the_wcag_ratio():
    assert contrast("#000000", "#ffffff") == 21.0 and contrast("#777777", "#ffffff") == 4.48
    assert themes(":root{--ink:#fff;--bg:#000000}")["dark"] == {"ink": "#ffffff", "bg": "#000000"}  # #rgb is expanded


def test_low_contrast_in_the_dark_theme_fails():
    assert "--muted:#9aa3b5" in CSS  # the dark theme's secondary text
    statuses = report(css=CSS.replace("--muted:#9aa3b5", "--muted:#3a4150", 1))
    assert statuses["contrast-dark"] == "FAIL" and statuses["contrast-light"] == "PASS"


def test_a_colour_written_outside_the_theme_fails():
    assert report(css=CSS + "\n.extra{color:#999}")["theme-colours"] == "FAIL"


def test_a_repeated_label_and_alike_actions_fail():
    screens = screens_for(LOAN, LOAN.model, data_for(LOAN))
    fields = [f.model_dump() for f in screens.screen(CREATE).fields]
    repeated = edited(screens, CREATE, fields=[fields[0], {**fields[1], "label": fields[0]["label"] or fields[0]["attribute"]}])
    assert report(repeated)["distinct-labels"] == "FAIL"
    return_screen = screens.screen("Return")
    alike = edited(screens, "MarkOverdue", title=return_screen.title)  # Return and MarkOverdue are both offered on loan
    assert report(alike)["actions-told-apart"] == "FAIL"


def test_attribute_names_shown_as_labels_are_advice_not_a_failure():
    assert report(pack=EXCURSION)["labels-read-as-words"] == "WARN"


@pytest.mark.parametrize(("check", "js", "html"), [
    ("keyboard-order", JS + '\nel("div", "", { tabindex: "2" });', HTML),
    ("labelled-controls", JS, HTML.replace('<label class="actor">', '<span class="actor">')),
    ("required-in-code", JS.replace("input.required = true", "input.dataset.required = 1"), HTML),
])
def test_the_page_template_checks_can_fail(check, js, html):
    assert report(js=js, html=html)[check] == "FAIL"


def test_the_designer_gets_the_check_with_the_screens(tmp_path):
    app = create_app(harness_studio(tmp_path / "workspace"), "synthetic-screen-access-test")
    try:
        client = TestClient(app, base_url="http://127.0.0.1:8765")
        headers = {"Authorization": "Bearer synthetic-screen-access-test", "Origin": "http://127.0.0.1:8765"}
        result = client.post("/api/play/screens", json={}, headers=headers).json()["accessibility"]
        assert result["standard"] == "WCAG 2.2 AA" and result["failed"] == 0
        assert {c["check"] for c in result["checks"]} >= {"contrast-light", "contrast-dark", "keyboard-order", "distinct-labels"}
    finally:
        app.state.play.stop()


browser = pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1",
                             reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")


@pytest.mark.browser
@pytest.mark.slow
@browser
def test_the_check_shows_in_the_designer_and_axe_agrees_on_the_built_app_in_a_real_browser():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci extra")
    axe_module = pytest.importorskip("axe_playwright_python.sync_playwright", reason="NOT_RUN: install the hci extra")
    from axe_playwright_python.base import AXE_FILE_PATH  # noqa: PLC0415 - optional hci extra
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=ROOT / "packs/library-loan") as server, api.sync_playwright() as playwright:
        executable = os.environ.get("EIJA_CHROMIUM")
        try:
            chrome = (playwright.chromium.launch(headless=True, executable_path=executable) if executable
                      else playwright.chromium.launch(channel="chrome", headless=True))
        except api.Error as exc:
            pytest.skip(f"NOT_RUN: Chrome unavailable: {str(exc).splitlines()[0]}")
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 900})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            page.click("#tab-screens")
            page.wait_for_selector("#screen-a11y:not([hidden])")
            assert page.inner_text("#screen-a11y summary") == "✓\nAccessibility (WCAG 2.2 AA): 9 of 9 checks pass"
            page.evaluate("PlayIDE.runAs('librarian')")
            page.wait_for_function("document.getElementById('run-frame').src.startsWith('http')", timeout=90_000)
            built = chrome.new_page()
            axe = axe_module.Axe.from_file(AXE_FILE_PATH)
            for scheme in ("light", "dark"):  # the browser's own judgement of the page the check passed
                built.emulate_media(color_scheme=scheme)
                built.goto(page.eval_on_selector("#run-frame", "frame => frame.src"))
                built.wait_for_selector("#actor-role")
                tags = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]
                violations = axe.run(built, options={"runOnly": {"type": "tag", "values": tags}}).response["violations"]
                assert [v["id"] for v in violations] == [], scheme
            assert errors == []
        finally:
            chrome.close()
