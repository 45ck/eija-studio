"""SD05: server workflow versus visible Dagre path geometry, including a lying endpoint.

Real loopback Studio, offline provider, fresh disposable workspace, normal release
identity. Only GET requests are allowed. The fault lives in this page's SVG, never
in source or server state. This checks endpoint fidelity, not readable routing,
absence of overlaps, model correctness or human comprehension.
"""
from __future__ import annotations

import json
from urllib.parse import urlsplit

import pytest

from quality.hci.server import studio_server

pytestmark = pytest.mark.hci


OBSERVE = """() => {
    const board = document.querySelector('#model-canvas svg.model-svg');
    const nodes = [...board.querySelectorAll('.model-node')].map(group => ({
        id:group.getAttribute('data-eija-id'),
        label:group.querySelector('.state-label').textContent,
        rect:group.querySelector('rect.state-box')
    }));
    function contacts(path, length) {
        const point = path.getPointAtLength(length);
        const screen = new DOMPoint(point.x, point.y).matrixTransform(path.getScreenCTM());
        return {
            screen:{x:screen.x, y:screen.y},
            nodes:nodes.filter(node => {
                const local = screen.matrixTransform(node.rect.getScreenCTM().inverse());
                return node.rect.isPointInStroke(local);
            }).map(node => node.label).sort()
        };
    }
    const edges = [...board.querySelectorAll('.model-edge')].map(group => {
        const path = group.querySelector('path.edge-line');
        const length = path.getTotalLength(), style = getComputedStyle(path);
        return {id:group.getAttribute('data-eija-id'),
            label:group.querySelector('.edge-label').textContent,
            accessible:group.getAttribute('aria-label'),
            d:path.getAttribute('d'), hit:group.querySelector('.edge-hit').getAttribute('d'),
            length, stroke:style.stroke, opacity:style.opacity, visibility:style.visibility,
            source:contacts(path, 0), target:contacts(path, length)};
    });
    return {nodes:nodes.map(node => {
        const box = node.rect.getBBox(), matrix = node.rect.getScreenCTM();
        return {id:node.id, label:node.label,
            box:{x:box.x, y:box.y, width:box.width, height:box.height},
            rounded:{rx:node.rect.rx.baseVal.value, ry:node.rect.ry.baseVal.value},
            stroke:{color:getComputedStyle(node.rect).stroke, width:getComputedStyle(node.rect).strokeWidth},
            screenMatrix:{a:matrix.a, b:matrix.b, c:matrix.c, d:matrix.d, e:matrix.e, f:matrix.f}};
    }), edges};
}"""

MISDIRECT = r"""(path, wrongState) => {
    const board = path.closest('svg');
    const node = [...board.querySelectorAll('.model-node')].find(group =>
        group.querySelector('.state-label').textContent === wrongState);
    const rect = node.querySelector('rect.state-box');
    // The midpoint of a straight side is on the painted rounded rectangle border.
    const wrong = new DOMPoint(rect.x.baseVal.value, rect.y.baseVal.value + rect.height.baseVal.value / 2)
        .matrixTransform(rect.getScreenCTM()).matrixTransform(path.getScreenCTM().inverse());
    const original = path.getAttribute('d');
    const terminal = /L\s*[-+0-9.eE]+\s+[-+0-9.eE]+\s*$/;
    if (!terminal.test(original)) throw new Error('Negative control requires a terminal line segment');
    path.setAttribute('d', original.replace(terminal, `L ${wrong.x} ${wrong.y}`));
    return original;
}"""


@pytest.fixture(scope="module")
def endpoint_browser():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: Playwright is required for rendered endpoint checks")
    with api.sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(channel="chrome", headless=True)
        except api.Error as error:
            pytest.skip(f"NOT_RUN: isolated Chrome unavailable: {str(error).splitlines()[0]}")
        try:
            yield api, browser
        finally:
            browser.close()


def endpoint_problems(model, pack_id, observed):
    """Expected topology is server JSON; actual contact comes from browser path/shape geometry."""
    nodes, edges = observed["nodes"], observed["edges"]
    assert sorted(node["label"] for node in nodes) == sorted(model["states"])
    assert all(node["id"] == f"{pack_id}.state.{node['label']}" for node in nodes)
    expected = {f"{pack_id}.transition.{item['id']}": item for item in model["transitions"]}
    assert sorted(edge["id"] for edge in edges) == sorted(expected)
    problems = []
    for edge in edges:
        transition = expected[edge["id"]]
        assert edge["label"] == transition["action"]
        assert edge["accessible"] == (f"{transition['action']}, {transition['role']}, "
                                      f"{transition['from_state']} to {transition['to_state']}. Select transition.")
        assert edge["length"] > 0 and edge["stroke"] != "none"
        assert float(edge["opacity"]) > 0 and edge["visibility"] == "visible"
        for endpoint, field in (("source", "from_state"), ("target", "to_state")):
            wanted = transition[field]
            if edge[endpoint]["nodes"] != [wanted]:
                problems.append(f"{transition['id']} {endpoint}: expected border of {wanted}; got {edge[endpoint]['nodes']}")
    return problems


def _read_only_route(route, origin, refused):
    request = route.request
    if request.method != "GET" or urlsplit(request.url).netloc != origin:
        refused.append({"method": request.method, "path": urlsplit(request.url).path})
        route.abort()
    else:
        route.continue_()


def _check_fault(page, model, pack_id, before):
    transition = model["transitions"][0]
    wrong_state = next(state for state in model["states"] if state != transition["to_state"])
    edge_id = f"{pack_id}.transition.{transition['id']}"
    edge_index = next(index for index, edge in enumerate(before["edges"]) if edge["id"] == edge_id)
    visible_path = page.locator("#model-canvas .model-edge").nth(edge_index).locator(".edge-line")
    assert visible_path.count() == 1
    original = visible_path.evaluate(MISDIRECT, wrong_state)
    try:
        changed = page.evaluate(OBSERVE)
        faults = endpoint_problems(model, pack_id, changed)
        assert len(faults) == 1 and faults[0].startswith(f"{transition['id']} target:")
        old_edge = next(edge for edge in before["edges"] if edge["id"] == edge_id)
        bad_edge = next(edge for edge in changed["edges"] if edge["id"] == edge_id)
        assert bad_edge["target"]["nodes"] == [wrong_state]
        assert bad_edge["d"] != old_edge["d"] and bad_edge["hit"] == old_edge["hit"]
        for key in ("id", "label", "accessible", "source"):
            assert bad_edge[key] == old_edge[key]
        assert changed["nodes"] == before["nodes"]
        assert [edge for edge in changed["edges"] if edge["id"] != edge_id] == [
            edge for edge in before["edges"] if edge["id"] != edge_id]
    finally:
        visible_path.evaluate("(path, original) => path.setAttribute('d', original)", original)
    restored = page.evaluate(OBSERVE)
    assert endpoint_problems(model, pack_id, restored) == []
    assert restored == before
    return {"transition": transition["id"], "wrong_state": wrong_state, "failures": faults, "mutated": changed}


@pytest.mark.parametrize("direction", ("LR", "TB"))
def test_rendered_endpoints_match_server_and_detect_a_lying_visible_path(endpoint_browser, tmp_path, direction):
    api, browser = endpoint_browser
    refused = []
    with studio_server("rendered-endpoints-" + direction, identity="release") as url:
        context = browser.new_context(viewport={"width": 1600, "height": 1100}, device_scale_factor=1)
        context.route("**/*", lambda route: _read_only_route(route, urlsplit(url).netloc, refused))
        page = context.new_page()
        try:
            with page.expect_response(lambda response: urlsplit(response.url).path == "/api/workbench") as response:
                page.goto(url)
            authoritative = response.value.json()
            model, pack_id = authoritative["model"], authoritative["pack"]["id"]
            api.expect(page.locator("#model-canvas svg.model-svg")).to_be_visible()
            canvas_view = page.locator("details#canvas-view")
            if canvas_view.get_attribute("open") is None:
                page.locator("#canvas-view > summary").click()
            api.expect(canvas_view).to_have_attribute("open", "")
            api.expect(page.locator("#canvas-direction")).to_be_visible()
            page.locator("#canvas-direction").select_option(direction)
            api.expect(page.locator("#model-canvas svg")).to_have_attribute("data-direction", direction)
            before = page.evaluate(OBSERVE)
            evidence = {"scope": "Read-only default-pack baseline; normal release identity; no owner operations",
                        "browser": browser.version, "direction": direction, "pack": authoritative["pack"],
                        "server_workflow": model, "before": before}
            (tmp_path / "rendered-endpoints-before.json").write_text(
                json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
            assert endpoint_problems(model, pack_id, before) == []
            control = _check_fault(page, model, pack_id, before)
            with page.expect_response(lambda response: urlsplit(response.url).path == "/api/workbench") as reloaded:
                page.reload()
            assert reloaded.value.json()["model"] == model
            assert refused == []
            evidence.update({"negative_control": control, "refused_requests": refused,
                             "restoration": "exact geometry restored; server model unchanged"})
            (tmp_path / "rendered-endpoints.json").write_text(
                json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
        finally:
            context.close()
