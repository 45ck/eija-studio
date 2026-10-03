"""Opt-in real-browser probe checks against synthetic, independently positioned DOM.

These exercise clipping geometry, not human cognition or the application's journey.
No application server or authenticated page is used. Native disclosure checks use ordinary keyboard input.
"""
from __future__ import annotations

import pytest

from quality.hci import journey

pytestmark = pytest.mark.hci

COUNTS = {"controls": 1, "content_groups": 1, "atoms": 2, "chunks": 2}
ZERO = dict.fromkeys(COUNTS, 0)


@pytest.fixture(scope="module")
def isolated_probe_browser():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci extra for browser geometry tests")
    with api.sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(channel="chrome", headless=True)
        except api.Error as exc:
            pytest.skip(f"NOT_RUN: isolated Chrome unavailable: {str(exc).splitlines()[0]}")
        try:
            yield browser
        finally:
            browser.close()


@pytest.fixture
def probe_page(isolated_probe_browser):
    context = isolated_probe_browser.new_context(viewport={"width": 800, "height": 600}, device_scale_factor=1)
    context.route("**/*", lambda route: route.abort())
    context.add_init_script(path=str(journey.PROBE))
    page = context.new_page()
    page.goto("data:text/html,<!doctype html><html><head><title>Probe fixture</title></head><body></body></html>")
    try:
        yield page
    finally:
        context.close()


def _fixture(button, text, *, nested=False, overflow="overflow:hidden", disabled=False, outer_top=100):
    bx, by = button
    tx, ty = text
    inner = '<div id="inner">' if nested else ""
    inner_end = "</div>" if nested else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Probe fixture</title>
    <style>
    html,body {{margin:0;padding:0;}}
    #outer {{position:absolute;left:100px;top:{outer_top}px;width:200px;height:100px;{overflow};}}
    #inner {{position:absolute;left:140px;top:0;width:160px;height:100px;overflow:hidden;}}
    #control,#copy {{position:absolute;box-sizing:border-box;width:80px;height:24px;margin:0;
        padding:0;border:0;font:16px/24px monospace;background:#eee;color:#111;}}
    #control {{left:{bx}px;top:{by}px;}}
    #copy {{left:{tx}px;top:{ty}px;}}
    </style></head><body><div id="outer">{inner}
    <button id="control" {'disabled' if disabled else ''}>Act</button><p id="copy">Copy</p>
    {inner_end}</div></body></html>"""


def _observe(page, button_point, text_point):
    return page.evaluate("""(points) => {
        const ids = ['control', 'copy'];
        const geometry = ids.map((id, index) => {
            const el = document.getElementById(id), r = el.getBoundingClientRect();
            const hit = document.elementFromPoint(...points[index]);
            return {id, x:r.x, y:r.y, w:r.width, h:r.height,
                paintedAtWitness: hit === el || el.contains(hit)};
        });
        return {geometry, controls:window.__hci.controls(), choices:window.__hci.choices(['#control']),
            screenChoices:window.__hci.screenChoices(), viewport:window.__hci.chunks('viewport'),
            page:window.__hci.chunks('page'), visible:ids.map(id => window.__hci.isVisible('#' + id)),
            interactions:window.__hci.interactions.length};
    }""", [button_point, text_point])


def _assert_chunks(observed, visible):
    expected = COUNTS if visible else ZERO
    excluded = ZERO if visible else COUNTS
    assert {key: observed[key] for key in COUNTS} == expected
    assert observed["raw"] == COUNTS
    assert observed["excluded_clipped"] == excluded
    assert all(observed[key] + observed["excluded_clipped"][key] == observed["raw"][key] for key in COUNTS)


# Witness points and expected boxes are fixed independently of the probe's helpers.
# A clipped element still has a nonzero bounding box wholly inside the 800x600 viewport.
@pytest.mark.parametrize(
    ("button", "text", "nested", "overflow", "visible", "button_point", "text_point"),
    [
        ((8, 8), (108, 48), False, "overflow:hidden", True, (148, 120), (248, 160)),
        ((240, 8), (240, 48), False, "overflow-x:clip;overflow-y:visible", False, (380, 120), (380, 160)),
        ((8, 140), (108, 140), False, "overflow-y:clip;overflow-x:visible", False, (148, 252), (248, 252)),
        ((160, 8), (160, 48), False, "overflow:hidden", True, (280, 120), (280, 160)),
        ((8, 80), (108, 80), False, "overflow:hidden", True, (148, 190), (248, 190)),
        ((80, 8), (80, 48), True, "overflow:hidden", False, (360, 120), (360, 160)),
        ((20, 8), (20, 48), True, "overflow:hidden", True, (280, 120), (280, 160)),
        ((8, 140), (108, 140), False, "overflow-x:clip;overflow-y:visible", True, (148, 252), (248, 252)),
        ((240, 8), (240, 48), False, "overflow-y:clip;overflow-x:visible", True, (380, 120), (380, 160)),
    ],
    ids=["normal", "fully-clipped-x", "fully-clipped-y", "partial-x", "partial-y",
         "nested-fully-clipped", "nested-partial", "x-clip-keeps-y-overflow", "y-clip-keeps-x-overflow"],
)
def test_probe_counts_match_ancestor_clipping(probe_page, button, text, nested, overflow,
                                            visible, button_point, text_point):
    probe_page.set_content(_fixture(button, text, nested=nested, overflow=overflow))
    measured = _observe(probe_page, button_point, text_point)
    for geometry, (x, y) in zip(measured["geometry"], (button, text), strict=True):
        assert {key: geometry[key] for key in ("x", "y", "w", "h")} == {
            "x": 100 + (140 if nested else 0) + x, "y": 100 + y, "w": 80, "h": 24,
        }
        assert geometry["paintedAtWitness"] is visible
    assert measured["visible"] == [visible, visible]
    assert [control["selector"] for control in measured["controls"]] == (["#control"] if visible else [])
    assert measured["choices"] == int(visible) and measured["screenChoices"] == int(visible)
    _assert_chunks(measured["viewport"], visible)
    _assert_chunks(measured["page"], visible)
    if visible:
        control = measured["controls"][0]
        assert (control["w"], control["h"], control["raw_w"], control["raw_h"]) == (80, 24, 80, 24)
        assert control["in_viewport"] is True and control["disabled"] is False
    assert measured["interactions"] == 0


def test_disabled_visible_controls_remain_content_but_are_not_choices(probe_page):
    probe_page.set_content(_fixture((8, 8), (108, 48), disabled=True))
    measured = _observe(probe_page, (148, 120), (248, 160))
    assert all(element["paintedAtWitness"] for element in measured["geometry"])
    assert measured["visible"] == [True, True]
    assert len(measured["controls"]) == 1 and measured["controls"][0]["disabled"] is True
    assert measured["choices"] == 0 and measured["screenChoices"] == 0
    _assert_chunks(measured["viewport"], True)
    _assert_chunks(measured["page"], True)
    assert measured["interactions"] == 0


def test_document_viewport_is_separate_from_ancestor_clipping(probe_page):
    probe_page.set_content(_fixture((8, 8), (108, 48), outer_top=700))
    measured = _observe(probe_page, (148, 720), (248, 760))
    assert not any(element["paintedAtWitness"] for element in measured["geometry"])
    assert measured["visible"] == [True, True]
    assert len(measured["controls"]) == 1 and measured["controls"][0]["in_viewport"] is False
    assert measured["choices"] == 1 and measured["screenChoices"] == 0
    _assert_chunks(measured["page"], True)
    assert {key: measured["viewport"][key] for key in COUNTS} == ZERO
    assert measured["viewport"]["raw"] == ZERO
    assert measured["viewport"]["excluded_clipped"] == ZERO
    assert measured["interactions"] == 0


DISCLOSURE_FIXTURE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Native disclosure probe</title>
<style>
html,body {margin:0;padding:0;font:16px/24px sans-serif;}
details {width:300px;} summary {height:28px;}
#outer {position:absolute;left:40px;top:40px;}
#outer-body,#inner {margin-left:20px;}
button {width:120px;height:28px;padding:0;border:0;}
#before,#after {position:absolute;left:400px;}
#before {top:20px;} #after {top:250px;}
</style></head><body>
<button id="before">Before</button>
<details id="outer"><summary id="outer-summary"><span id="outer-title">Outer</span></summary>
Outer direct body text
<div id="outer-body"><button id="outer-button">Outer action</button><p id="outer-copy">Outer copy</p>
<details id="inner"><summary id="inner-summary"><span id="inner-title">Inner</span></summary>
<button id="inner-button">Inner action</button><p id="inner-copy">Inner copy</p></details></div>
<summary id="second-summary">Second summary is content</summary>
</details><button id="after">After</button></body></html>"""


def _disclosure_observation(page):
    return page.evaluate("""() => {
        const ids=['outer-summary','outer-title','outer-button','outer-copy','inner-summary','inner-title','inner-button','inner-copy','second-summary'];
        return {elements:Object.fromEntries(ids.map(id=>{
            const el=document.getElementById(id),r=el.getBoundingClientRect(),x=r.x+r.width/2,y=r.y+r.height/2,hit=document.elementFromPoint(x,y);
            return [id,{raw:{x:r.x,y:r.y,w:r.width,h:r.height},probe:__hci.isVisible('#'+id),native:el.checkVisibility(),
                paintedWitness:hit===el||el.contains(hit),hit:__hci.hitOk(el,x,y)}];
        })),controls:__hci.controls(),choices:__hci.screenChoices(),tabbable:__hci.tabbableCount(),
            viewport:__hci.chunks('viewport'),page:__hci.chunks('page'),rawTarget:__hci.targetOf(document.getElementById('inner-button'))};
    }""")


def _tab_sequence(page):
    page.locator("#before").focus()
    sequence = []
    for _ in range(8):
        page.keyboard.press("Tab")
        current = page.evaluate("document.activeElement.id")
        sequence.append(current)
        if current == "after":
            return sequence
    raise AssertionError("Native Tab did not reach the fixture's final control: " + repr(sequence))


@pytest.mark.parametrize(("outer_open", "inner_open"), [(False, False), (False, True), (True, False), (True, True)])
def test_closed_native_details_visibility_and_keyboard(probe_page, outer_open, inner_open):
    probe_page.set_content(DISCLOSURE_FIXTURE)
    # Open by ordinary keyboard action first, so real layout exists before closing.
    for selector in ("#outer-summary", "#inner-summary"):
        probe_page.locator(selector).focus()
        probe_page.keyboard.press("Enter")
    if not inner_open:
        probe_page.locator("#inner-summary").focus()
        probe_page.keyboard.press("Enter")
    if not outer_open:
        probe_page.locator("#outer-summary").focus()
        probe_page.keyboard.press("Enter")
    observed = _disclosure_observation(probe_page)
    expected = {"outer-summary": True, "outer-title": True,
                "outer-button": outer_open, "outer-copy": outer_open,
                "inner-summary": outer_open, "inner-title": outer_open,
                "inner-button": outer_open and inner_open, "inner-copy": outer_open and inner_open,
                "second-summary": outer_open}
    assert {key: value["probe"] for key, value in observed["elements"].items()} == expected, observed
    for ident, visible in expected.items():
        element = observed["elements"][ident]
        assert element["native"] is visible, {"id": ident, "observed": observed}
        if not visible:
            assert not element["paintedWitness"] and not element["hit"], {"id": ident, "observed": observed}
    expected_tabs = ["outer-summary"]
    if outer_open:
        expected_tabs += ["outer-button", "inner-summary"]
        if inner_open:
            expected_tabs += ["inner-button"]
    expected_tabs += ["after"]
    assert _tab_sequence(probe_page) == expected_tabs
    # Secondary summary is rendered content when open, but is not a native Tab stop.
    expected_controls = {"#before", "#after", "#outer-summary"}
    if outer_open:
        expected_controls |= {"#outer-button", "#inner-summary", "#second-summary"}
        if inner_open:
            expected_controls.add("#inner-button")
    assert {item["selector"] for item in observed["controls"]} == expected_controls
    assert observed["choices"] == len(expected_controls)
    assert observed["tabbable"] == len(expected_tabs) + 1
    assert observed["rawTarget"]["raw"] == observed["elements"]["inner-button"]["raw"], "Raw geometric observation changed"
    if not outer_open:
        assert observed["elements"]["inner-button"]["raw"]["w"] > 0, "The regression requires a retained nonempty hidden box"
        assert observed["viewport"]["controls"] == observed["page"]["controls"] == 3
        assert observed["viewport"]["content_groups"] == observed["page"]["content_groups"] == 0
        assert observed["viewport"]["raw"]["controls"] == 3


def test_occluded_target_keeps_geometry_but_fails_pointer_witness(probe_page):
    probe_page.set_content(_fixture((8, 8), (108, 48)).replace("</body>", '<div id="cover" style="position:absolute;left:100px;top:100px;width:100px;height:50px;background:black"></div></body>'))
    observed = _observe(probe_page, (148, 120), (248, 160))
    assert observed["visible"] == [True, True]
    assert observed["geometry"][0]["paintedAtWitness"] is False
    assert probe_page.evaluate("__hci.hitOk(document.getElementById('control'),148,120)") is False
    assert observed["controls"][0]["in_viewport"] is True
    _assert_chunks(observed["viewport"], True)
    probe_page.keyboard.press("Tab")
    assert probe_page.evaluate("document.activeElement.id") == "control"
