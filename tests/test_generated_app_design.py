"""Generated app task/reflow regressions using the real generated HTTP/SQLite service.

Opt in with EIJA_BROWSER_TESTS=1 and -m browser after the endpoint browser preflight.
The viewport tests are browser emulation, not physical-device or human-comprehension evidence.
All evaluated waits use explicit functions so the generated app keeps its normal no-unsafe-eval CSP.
"""
from __future__ import annotations

import http.client
import importlib
import json
import os
import sys
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from time import monotonic

import pytest

from eija_studio.bootstrap import source_identity
from eija_studio.domain.pack import load_pack
from eija_studio.interfaces.app_build import app_files

ROOT = Path(__file__).resolve().parents[1]
PACK = load_pack(ROOT / "packs/refund-desk")
LONG_TITLE = "Refund for " + "LongOrderReference" * 9
pytestmark = [
    pytest.mark.browser,
    pytest.mark.slow,
    pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1",
                       reason="NOT_RUN: real-browser generated-app checks; set EIJA_BROWSER_TESTS=1"),
]


@pytest.fixture(scope="module")
def chrome():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci extra")
    with api.sync_playwright() as playwright:
        executable = os.environ.get("EIJA_CHROMIUM")
        try:
            browser = (playwright.chromium.launch(headless=True, executable_path=executable) if executable
                       else playwright.chromium.launch(channel="chrome", headless=True))
        except api.Error as error:
            pytest.skip(f"NOT_RUN: Chrome unavailable: {str(error).splitlines()[0]}")
        try:
            yield browser
        finally:
            browser.close()


@pytest.fixture
def generated_server(tmp_path):
    """Generate the actual files without a nested conformance run; use an isolated real SQLite database."""
    out = tmp_path / "built-refund"
    files, _ = app_files(PACK, PACK.model, identity_provider=source_identity)
    for relative, text in files.items():
        target = out / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(text.encode("utf-8"))
    saved = {name: value for name, value in sys.modules.items() if name == "app" or name.startswith("app.")}
    for name in saved:
        del sys.modules[name]
    sys.path.insert(0, str(out))
    service = server = thread = None
    try:
        service_module = importlib.import_module("app.service")
        server_module = importlib.import_module("app.server")
        service = service_module.Service(str(tmp_path / "app.sqlite3"))
        server = ThreadingHTTPServer(("127.0.0.1", 0), server_module.handler_for(service))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        if server:
            server.shutdown()
            server.server_close()
        if thread:
            thread.join(timeout=10)
        if service:
            service.db.close()
        sys.path.remove(str(out))
        for name in [name for name in sys.modules if name == "app" or name.startswith("app.")]:
            del sys.modules[name]
        sys.modules.update(saved)


@pytest.fixture
def app_page(chrome, generated_server):
    context = chrome.new_context(viewport={"width": 1600, "height": 1000}, reduced_motion="reduce")
    page = context.new_page()
    errors = []
    violations = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("console", lambda message: violations.append(message.text) if "content security policy" in message.text.lower()
            or "violates the following" in message.text.lower() else None)
    try:
        yield page, generated_server
        assert errors == [], "\n".join(errors)
        assert violations == [], "\n".join(violations)
    finally:
        context.close()


def request(base_url, path, body=None):
    connection = http.client.HTTPConnection(base_url.removeprefix("http://"), timeout=10)
    payload = None if body is None else json.dumps(body).encode()
    connection.request("GET" if body is None else "POST", path, body=payload,
                       headers={} if body is None else {"Content-Type": "application/json"})
    response = connection.getresponse()
    value = response.status, json.loads(response.read())
    connection.close()
    return value


def open_app(page, base_url):
    page.goto(base_url + "/#actor=customer-a")
    page.wait_for_function("() => document.getElementById('create-button').disabled === false")
    assert page.locator("html").get_attribute("data-frontend") == "react"


def fill_refund(page, title=LONG_TITLE):
    page.locator("#title").fill(title)
    page.locator("#field-orderNumber").fill("ORDER-2048")
    page.locator("#field-reason").select_option("Damaged")
    page.locator("#field-amount").fill("25")


def create_refund(page):
    fill_refund(page)
    page.locator("#create-button").click()
    page.wait_for_function("() => document.getElementById('current-state').textContent === 'Requested'")
    page.wait_for_function("() => document.activeElement.id === 'result'")


def keyboard_to(page, locator):
    """Native traversal, not programmatic focus or dispatch of the desired click."""
    for _ in range(80):
        if locator.evaluate("node => node === document.activeElement"):
            return
        page.keyboard.press("Tab")
    raise AssertionError("Native Tab traversal could not reach the generated control")


@pytest.mark.parametrize("width", [320, 768, 1024, 1600])
@pytest.mark.parametrize("scheme", ["light", "dark"])
def test_long_rules_records_and_controls_reflow_without_losing_text(app_page, width, scheme):
    page, base_url = app_page
    page.set_viewport_size({"width": width, "height": 1000})
    page.emulate_media(color_scheme=scheme)
    open_app(page, base_url)
    create_refund(page)
    assert page.locator("#detail-title").inner_text() == LONG_TITLE
    assert not page.locator("#runtime-details").evaluate("node => node.open")
    page.locator("#runtime-details > summary").click()
    assert page.locator("#rules").inner_text().count("PaymentGateway") == 2
    actual_rules = page.locator("#rules tr").evaluate_all(
        "rows => rows.map(row => Array.from(row.cells, cell => cell.querySelector('.rule-value').textContent))")
    expected = [[t.action, t.from_state, t.to_state, t.role] for t in PACK.model.transitions]
    assert actual_rules == expected
    geometry = page.evaluate("""() => {
      const outside = [];
      const subjects = document.querySelectorAll('.panel, .rules, .rules td, .rule-value, input, select, button, .flow li, .values dd');
      for (const node of subjects) {
        if (!node.getClientRects().length) continue;
        const box = node.getBoundingClientRect();
        if (box.left < -1 || box.right > innerWidth + 1 || node.scrollWidth > node.clientWidth + 1) {
          outside.push({tag:node.tagName,id:node.id,text:node.textContent,width:box.width});
        }
      }
      return {page:document.documentElement.scrollWidth,width:innerWidth,outside};
    }""")
    assert geometry["page"] <= width + 1 and geometry["outside"] == [], geometry
    assert page.locator("#records .chip").evaluate("""node => {
      const style=getComputedStyle(node);
      return node.getBoundingClientRect().height <= parseFloat(style.lineHeight)
        + parseFloat(style.paddingTop) + parseFloat(style.paddingBottom) + 1;
    }""")  # a long title must not squeeze 'Requested' into a column of letters
    assert page.locator("#actor-role").inner_text() == "Customer"
    assert page.locator("#record-state").inner_text() == "Current state Requested"
    assert page.locator(".rules th").evaluate_all(
        "cells => cells.every(cell => cell.getAttribute('scope') === 'col')")
    assert page.locator("#title").evaluate("node => Number.parseFloat(getComputedStyle(node).fontSize)") >= 16
    assert "Local fixture actors" in page.locator(".runtime-scope").inner_text()
    assert "No login or external delivery." in page.locator(".runtime-scope").inner_text()


@pytest.mark.parametrize("width", [320, 1600])
def test_compact_rule_panel_preserves_headers_and_gives_values_readable_width(app_page, width):
    page, base_url = app_page
    page.set_viewport_size({"width": width, "height": 1000})
    open_app(page, base_url)
    page.locator("#runtime-details > summary").click()
    cells = page.locator("#rules td").evaluate_all("""nodes => nodes.map(node => {
      const label=node.querySelector('.rule-label'), value=node.querySelector('.rule-value');
      const header=document.getElementById(node.getAttribute('headers'));
      return {label:label.textContent,visualLabel:getComputedStyle(label).display,
        hidden:label.getAttribute('aria-hidden'),value:value.textContent,width:value.getBoundingClientRect().width,
        header:header.textContent,scope:header.getAttribute('scope'),role:node.getAttribute('role')};
    })""")
    expected = [text for transition in PACK.model.transitions
                for text in (transition.action, transition.from_state, transition.to_state, transition.role)]
    assert [cell["value"] for cell in cells] == expected
    assert min(cell["width"] for cell in cells) >= 150, cells
    assert all(cell["visualLabel"] == "block" and cell["hidden"] == "true" for cell in cells), cells
    assert all(cell["label"] == cell["header"] and cell["scope"] == "col" and cell["role"] == "cell"
               for cell in cells), cells
    assert page.get_by_role("columnheader").count() == 4
    assert page.get_by_role("table").count() == 1


def test_keyboard_action_cancel_restores_opener_and_commit_focuses_observed_outcome(app_page):
    page, base_url = app_page
    open_app(page, base_url)
    create_refund(page)
    opener = page.locator("#options button[title=Withdraw]")
    assert {"quiet", "action-choice"} <= set(opener.get_attribute("class").split())
    assert "→" not in opener.inner_text()
    keyboard_to(page, opener)
    assert opener.evaluate("node => getComputedStyle(node).outlineStyle") != "none"
    page.keyboard.press("Enter")
    page.wait_for_function("() => document.activeElement.closest('#action-screen') !== null")
    assert page.locator(".action-consequence").inner_text() == "Requested → Withdrawn"
    assert "→" not in page.locator("#action-screen button:not(.quiet)").inner_text()
    page.keyboard.press("Tab")  # the close button follows the confirmation button
    assert page.locator("#action-screen button.quiet").evaluate("node => node === document.activeElement")
    page.keyboard.press("Enter")
    assert page.locator("#action-screen").is_hidden()
    assert opener.evaluate("node => node === document.activeElement")
    assert request(base_url, "/api/records")[1][0]["version"] == 0
    page.keyboard.press("Enter")
    page.wait_for_function("() => document.activeElement.closest('#action-screen') !== null")
    page.keyboard.press("Enter")
    page.wait_for_function("() => document.getElementById('current-state').textContent === 'Withdrawn'")
    page.wait_for_function("() => document.activeElement.id === 'result'")
    assert page.locator("#result").inner_text() == "Withdraw completed. State: Withdrawn."
    assert "No further actions from this state." in page.locator("#options").inner_text()
    records = request(base_url, "/api/records")[1]
    view = request(base_url, f"/api/records/{records[0]['id']}?actor=customer-a")[1]
    assert view["record"]["version"] == 1 and len(view["history"]) == 1
    assert view["history"][0]["effect"] == "Audit:RequestWithdrawn"


def test_create_refusal_keeps_form_values_and_exposes_a_focused_semantic_error(app_page):
    page, base_url = app_page
    open_app(page, base_url)
    assert page.locator("#title").evaluate(
        "node => node.required && [...node.labels].some(label => label.textContent.startsWith('Record name'))")
    fill_refund(page, title="   ")  # HTML accepts it; the actual server rejects the trimmed title.
    page.locator("#create-button").click()
    page.wait_for_function("() => document.activeElement.id === 'create-feedback'")
    assert "INVALID_TITLE" in page.locator("#create-feedback").inner_text()
    assert page.locator("#title").input_value() == "   "
    assert page.locator("#field-orderNumber").input_value() == "ORDER-2048"
    assert page.locator("#field-reason").input_value() == "Damaged"
    assert page.locator("#field-amount").input_value() == "25"
    assert page.locator("#title").get_attribute("aria-invalid") == "true"
    assert page.locator("#title").get_attribute("aria-describedby") == "create-feedback"
    assert request(base_url, "/api/records")[1] == []
    page.locator("#title").fill("Replace the damaged order")
    assert page.locator("#create-feedback").is_hidden()
    assert page.locator("#title").get_attribute("aria-invalid") is None
    page.locator("#create-button").click()
    page.wait_for_function("() => document.activeElement.id === 'result'")
    assert len(request(base_url, "/api/records")[1]) == 1


def test_stale_confirmation_shows_refusal_then_refreshes_without_a_second_commit(app_page):
    page, base_url = app_page
    open_app(page, base_url)
    create_refund(page)
    page.locator("#options button[title=Withdraw]").click()
    record = request(base_url, "/api/records")[1][0]
    status, winner = request(base_url, f"/api/records/{record['id']}/act",
                             {"action": "Withdraw", "actor": "customer-a", "expected_version": 0,
                              "operation_id": "other-browser-winner"})
    assert status == 200 and winner["record"]["state"] == "Withdrawn"
    page.locator("#action-screen button:not(.quiet)").click()
    page.wait_for_function("() => document.activeElement.id === 'result'")
    assert "STALE_VERSION" in page.locator("#result").inner_text()
    assert "Review the refreshed state" in page.locator("#result").inner_text()
    assert page.locator("#current-state").inner_text() == "Withdrawn"
    view = request(base_url, f"/api/records/{record['id']}?actor=customer-a")[1]
    assert view["record"]["version"] == 1 and len(view["history"]) == 1


def test_initial_read_failure_has_a_visible_keyboard_retry_that_only_reads(app_page):
    page, base_url = app_page
    requests = []
    page.on("request", lambda entry: requests.append((entry.method, entry.url)))
    page.route("**/api/app", lambda route: route.abort())
    page.goto(base_url + "/#actor=customer-a")
    page.wait_for_selector("#load-feedback:not([hidden])")
    assert "App data could not be loaded" in page.locator("#load-error").inner_text()
    assert page.locator("#create-button").is_disabled()
    page.unroute("**/api/app")
    keyboard_to(page, page.locator("#retry-load"))
    page.keyboard.press("Enter")
    page.wait_for_function("() => document.getElementById('create-button').disabled === false")
    assert page.locator("#load-feedback").is_hidden()
    assert page.locator("#actor").evaluate("node => node === document.activeElement")
    assert all(method == "GET" for method, _ in requests)
    assert request(base_url, "/api/records")[1] == []


def test_role_read_failure_disables_stale_actions_until_reload_succeeds(app_page):
    page, base_url = app_page
    open_app(page, base_url)
    create_refund(page)
    requests = []
    page.on("request", lambda entry: requests.append((entry.method, entry.url)))
    page.route("**/api/records/*?actor=*", lambda route: route.abort())
    page.locator("#actor").select_option("support-bot")
    page.wait_for_selector("#load-feedback:not([hidden])")
    assert "SupportAgent" in page.locator("#actor-role").inner_text()
    assert page.locator("#current-state").inner_text() == "Requested"
    assert page.locator("#options button").evaluate_all("buttons => buttons.every(button => button.disabled)")
    assert page.locator("#create-button").is_disabled()
    assert "Actions are paused" in page.locator("#load-error").inner_text()
    page.unroute("**/api/records/*?actor=*")
    page.locator("#retry-load").click()
    page.wait_for_function("() => document.getElementById('create-button').disabled === false")
    assert page.locator("#options button[title=AssessRequest]").is_enabled()
    assert page.locator("#options button[title=Withdraw]").is_disabled()
    assert all(method == "GET" for method, _ in requests)
    assert request(base_url, "/api/records")[1][0]["version"] == 0


def test_committed_action_with_failed_refresh_keeps_receipt_and_pauses_stale_commands(app_page):
    page, base_url = app_page
    open_app(page, base_url)
    create_refund(page)
    page.locator("#options button[title=Withdraw]").click()
    page.route("**/api/records/*?actor=*", lambda route: route.abort())
    page.locator("#action-screen button:not(.quiet)").click()
    page.wait_for_selector("#load-feedback:not([hidden])")
    assert page.locator("#result").inner_text() == "Withdraw completed. State: Withdrawn."
    assert page.locator("#current-state").inner_text() == "Requested"  # retained last observation
    assert page.locator("#options button").evaluate_all("buttons => buttons.every(button => button.disabled)")
    assert page.locator("#create-button").is_disabled()
    record = request(base_url, "/api/records")[1][0]
    assert record["state"] == "Withdrawn" and record["version"] == 1
    page.unroute("**/api/records/*?actor=*")
    page.locator("#retry-load").click()
    page.wait_for_function("() => document.getElementById('current-state').textContent === 'Withdrawn'")
    page.wait_for_function("() => document.getElementById('create-button').disabled === false")
    assert page.locator("#load-feedback").is_hidden()
    assert "Audit:RequestWithdrawn" in page.locator("#history").inner_text()
    view = request(base_url, f"/api/records/{record['id']}?actor=customer-a")[1]
    assert len(view["history"]) == 1 and view["record"]["version"] == 1


def test_keyboard_record_selection_moves_focus_to_selected_detail(app_page):
    page, base_url = app_page
    open_app(page, base_url)
    create_refund(page)
    first = request(base_url, "/api/records")[1][0]
    fill_refund(page, title="A second refund")
    page.locator("#create-button").click()
    page.wait_for_function("() => document.getElementById('detail-title').textContent === 'A second refund'")
    page.wait_for_function("() => document.activeElement.id === 'result'")
    button = page.locator("#records button").filter(has_text=LONG_TITLE)
    keyboard_to(page, button)
    page.keyboard.press("Enter")
    page.wait_for_function("() => document.activeElement.id === 'detail-title'")
    assert page.locator("#detail-title").inner_text() == LONG_TITLE
    assert page.locator("#records button[aria-current=true]").inner_text().startswith(LONG_TITLE)
    assert request(base_url, f"/api/records/{first['id']}?actor=customer-a")[1]["record"]["version"] == 0


def test_delayed_old_role_view_cannot_replace_the_current_roles_actions(app_page):
    page, base_url = app_page
    open_app(page, base_url)
    create_refund(page)
    held = []
    ready = threading.Event()

    def hold_customer_view(route):
        held.append((route, route.fetch()))  # retain an actual server response; delay only its delivery
        ready.set()

    page.route("**/api/records/*?actor=customer-a", hold_customer_view)
    page.locator("#actor").select_option("supervisor-on-shift")
    page.wait_for_function("() => document.getElementById('create-button').disabled === false")
    with page.expect_request(lambda entry: "?actor=customer-a" in entry.url):
        page.locator("#actor").select_option("customer-a")
    page.wait_for_function("() => document.getElementById('actor-role').textContent === 'Customer'")
    deadline = monotonic() + 5
    while not ready.is_set() and monotonic() < deadline:
        page.wait_for_timeout(20)  # pump browser events until the actual route.fetch callback has completed
    assert ready.is_set(), "The delayed route handler did not retain the actual response in time"
    assert len(held) == 1
    page.locator("#actor").select_option("support-bot")
    page.wait_for_function("() => document.getElementById('create-button').disabled === false")
    assert page.locator("#options button[title=AssessRequest]").is_enabled()
    route, response = held[0]
    with page.expect_response(lambda entry: "?actor=customer-a" in entry.url):
        route.fulfill(response=response)
    page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
    assert page.locator("#actor").input_value() == "support-bot"
    assert "SupportAgent" in page.locator("#actor-role").inner_text()
    assert page.locator("#options button[title=AssessRequest]").is_enabled()
    assert page.locator("#options button[title=Withdraw]").is_disabled()
    assert page.locator("#load-feedback").is_hidden()
    page.unroute("**/api/records/*?actor=customer-a")


def test_tall_app_keeps_actor_identity_and_focused_outcome_below_opaque_header(app_page):
    page, base_url = app_page
    page.set_viewport_size({"width": 768, "height": 1000})
    open_app(page, base_url)
    create_refund(page)
    geometry = page.evaluate("""() => {
      const bar = document.querySelector('.bar'), outcome = document.getElementById('result');
      const header = bar.getBoundingClientRect(), result = outcome.getBoundingClientRect();
      return {position:getComputedStyle(bar).position,background:getComputedStyle(bar).backgroundColor,
        panel:getComputedStyle(document.documentElement).getPropertyValue('--panel').trim(),
        top:header.top,bottom:header.bottom,measured:Number.parseFloat(
          document.documentElement.style.getPropertyValue('--app-bar-height')),
        outcome:{top:result.top,bottom:result.bottom},height:innerHeight,focus:document.activeElement.id};
    }""")
    assert geometry["position"] == "sticky" and geometry["top"] == pytest.approx(0, abs=1), geometry
    assert geometry["background"] != "rgba(0, 0, 0, 0)"
    assert geometry["measured"] == pytest.approx(geometry["bottom"] - geometry["top"], abs=1), geometry
    assert geometry["outcome"]["top"] >= geometry["bottom"] + 1, geometry
    assert geometry["outcome"]["bottom"] <= geometry["height"], geometry
    assert geometry["focus"] == "result"
    assert page.locator("#actor").is_visible() and page.locator("#actor-role").inner_text() == "Customer"
    assert page.locator("#app-name").inner_text() == PACK.pack.name
    opener = page.locator("#options button[title=Withdraw]")
    keyboard_to(page, opener)
    page.keyboard.press("Enter")
    page.wait_for_function("() => document.activeElement.closest('#action-screen') !== null")
    page.keyboard.press("Enter")
    page.wait_for_function("() => document.getElementById('current-state').textContent === 'Withdrawn'")
    page.wait_for_function("() => document.activeElement.id === 'result'")
    assert page.locator("#result").evaluate("""node => {
      const result=node.getBoundingClientRect(), bar=document.querySelector('.bar').getBoundingClientRect();
      return result.top > bar.bottom && result.bottom <= innerHeight;
    }""")
    assert page.locator("#actor-role").inner_text() == "Customer"


def test_short_embedded_app_keeps_header_in_normal_flow_and_focus_visible(app_page):
    page, base_url = app_page
    page.set_viewport_size({"width": 768, "height": 280})
    open_app(page, base_url)
    assert page.locator(".bar").evaluate("node => getComputedStyle(node).position") == "static"
    create_refund(page)
    observed = page.locator("#result").evaluate("""node => {
      const result=node.getBoundingClientRect(), bar=document.querySelector('.bar').getBoundingClientRect();
      return {top:result.top,bottom:result.bottom,height:innerHeight,header:bar.bottom,scrollY};
    }""")
    assert observed["top"] >= 0 and observed["bottom"] <= observed["height"], observed
    assert observed["scrollY"] > 0 and observed["header"] <= 0, observed
    assert page.locator(".bar").evaluate("node => getComputedStyle(node).position") == "static"


def open_runtime_inspector(page, base_url):
    """An isolated parent records the real app's messages; it does not stand in for PlayIDE's receiver."""
    # Use the real fixture's origin rather than an intercepted, otherwise unbound port.
    # PlayIDE's cross-origin receiver has its own end-to-end browser journey.
    parent_url = base_url + "/runtime-parent"
    page.route(parent_url, lambda route: route.fulfill(
        body='<!doctype html><title>Runtime protocol inspector</title><iframe id="observed-app" name="generated-run" width="1100" height="850"></iframe>',
        content_type="text/html", headers={
            "Content-Security-Policy": "default-src 'self'; frame-src 'self'",
            "Referrer-Policy": "no-referrer",
        }))
    page.goto(parent_url)
    page.evaluate("""appUrl => {
      window.runtimeEvents = [];
      window.runtimeInspection = [];
      const frame = document.getElementById('observed-app');
      addEventListener('message', event => {
        window.runtimeInspection.push({type:event.data && event.data.type,origin:event.origin,
          fromFrame:event.source === frame.contentWindow});
        if (event.source !== frame.contentWindow || event.origin !== new URL(appUrl).origin) return;
        if (event.data.type === 'playide.runtime.ready.v1') {
          event.source.postMessage({type:'playide.runtime.connect.v1',modelHash:event.data.modelHash,
            subjectHash:event.data.subjectHash,
            nonce:'5fac2043-63c6-4e1a-866e-ddcd15e0a700'}, event.origin);
        } else if (event.data.type === 'playide.runtime.v1') window.runtimeEvents.push(event.data);
      });
      frame.src = appUrl + '/#actor=customer-a';
    }""", base_url)
    frame_element = page.locator("#observed-app").element_handle()
    assert frame_element is not None
    frame = frame_element.content_frame()
    assert frame is not None
    # contentWindow also exists for the iframe's initial about:blank document. Observe
    # the actual generated app navigation and DOM before diagnosing its handshake.
    frame.wait_for_url(base_url + "/#actor=customer-a")
    frame.wait_for_function("() => document.getElementById('create-button').disabled === false")
    try:
        frame.wait_for_function("() => typeof runtimeConnection !== 'undefined' && runtimeConnection !== null")
    except Exception as error:
        inspection = page.evaluate("() => ({origin:location.origin,messages:window.runtimeInspection})")
        observed = frame.evaluate("""() => ({url:location.href,origin:location.origin,
          ancestors:Array.from(location.ancestorOrigins || []),referrer:document.referrer,
          parentOrigin:typeof runtimeParentOrigin === 'undefined' ? null : runtimeParentOrigin,
          modelHash:typeof state === 'undefined' || !state.app ? null : state.app.model_hash})""")
        raise AssertionError(f"Loaded generated-app handshake failed: parent={inspection}; app={observed}") from error
    assert frame.evaluate("() => document.referrer") == ""
    return frame


def test_embedded_app_sends_exact_real_commit_without_private_record_values(app_page):
    page, base_url = app_page
    frame = open_runtime_inspector(page, base_url)
    create_refund(frame)
    assert page.evaluate("() => window.runtimeEvents") == []
    frame.locator("#options button[title=Withdraw]").click()
    assert page.evaluate("() => window.runtimeEvents") == []  # opening a screen is not a commit
    frame.locator("#action-screen button:not(.quiet)").click()
    page.wait_for_function("() => window.runtimeEvents.length === 1")
    frame.wait_for_function("() => document.getElementById('current-state').textContent === 'Withdrawn'")
    event = page.evaluate("() => window.runtimeEvents[0]")
    record = request(base_url, "/api/records")[1][0]
    history = request(base_url, f"/api/records/{record['id']}?actor=customer-a")[1]["history"]
    assert event == {"type": "playide.runtime.v1", "nonce": "5fac2043-63c6-4e1a-866e-ddcd15e0a700",
                     "modelHash": PACK.model.semantic_hash,
                     "subjectHash": request(base_url, "/api/app")[1]["subject"]["digest"], "recordId": record["id"],
                     "operationId": history[0]["operation"], "action": "Withdraw", "from": "Requested",
                     "to": record["state"], "actorId": "customer-a", "version": record["version"],
                     "kind": "committed", "effects": [history[0]["effect"]]}
    assert record["version"] == 1 and len(history) == 1
    assert LONG_TITLE not in json.dumps(event) and "ORDER-2048" not in json.dumps(event)


def test_embedded_real_refusal_reports_attempted_baseline_without_movement(app_page):
    page, base_url = app_page
    frame = open_runtime_inspector(page, base_url)
    create_refund(frame)
    frame.locator("#options button[title=Withdraw]").click()
    record = request(base_url, "/api/records")[1][0]
    status, winner = request(base_url, f"/api/records/{record['id']}/act",
                             {"action": "Withdraw", "actor": "customer-a", "expected_version": 0,
                              "operation_id": "other-browser-winner"})
    assert status == 200 and winner["record"]["state"] == "Withdrawn"
    frame.locator("#action-screen button:not(.quiet)").click()
    page.wait_for_function("() => window.runtimeEvents.length === 1")
    frame.wait_for_function("() => document.getElementById('current-state').textContent === 'Withdrawn'")
    event = page.evaluate("() => window.runtimeEvents[0]")
    assert event["kind"] == "refused" and event["code"] == "STALE_VERSION"
    assert event["version"] == 0 and event["from"] == event["to"] == "Requested" and event["effects"] == []
    assert event["modelHash"] == PACK.model.semantic_hash and event["recordId"] == record["id"]
    assert event["actorId"] == "customer-a" and event["action"] == "Withdraw"
    view = request(base_url, f"/api/records/{record['id']}?actor=customer-a")[1]
    assert view["record"]["version"] == 1 and len(view["history"]) == 1


def test_model_navigation_focuses_real_panels_and_preserves_the_selected_record(app_page):
    page, base_url = app_page
    open_app(page, base_url)
    navigation = request(base_url, "/api/app")[1]["navigation"]
    assert navigation["schema_version"] == "eija.navigation.v1"
    destinations = {entry["kind"]: entry for entry in navigation["destinations"] if entry["kind"] != "action"}
    detail = page.locator(f'[data-nav-id="{destinations["detail"]["id"]}"]')
    assert detail.is_disabled()
    page.locator(f'[data-nav-id="{destinations["create"]["id"]}"]').click()
    page.wait_for_function("() => document.activeElement.id === 'title'")
    assert request(base_url, "/api/records")[1] == []
    create_refund(page)
    record = request(base_url, "/api/records")[1][0]
    page.locator(f'[data-nav-id="{destinations["records"]["id"]}"]').click()
    page.wait_for_function("() => document.activeElement.id === 'records-title'")
    assert page.locator("#detail-title").inner_text() == record["title"]
    detail.click()
    page.wait_for_function("() => document.activeElement.id === 'detail-title'")
    action = next(entry for entry in navigation["destinations"] if entry["use_case"] == "Withdraw")
    page.locator(f'#options [data-nav-id="{action["id"]}"]').click()
    page.wait_for_function("() => document.activeElement.closest('#action-screen') !== null")
    assert request(base_url, "/api/records")[1][0]["version"] == 0


def test_missing_navigation_binding_disables_an_otherwise_allowed_action(app_page):
    """Injected broken descriptor is a UI negative control, not a changed approved app."""
    page, base_url = app_page
    descriptor = request(base_url, "/api/app")[1]
    descriptor["navigation"]["destinations"] = [entry for entry in descriptor["navigation"]["destinations"]
                                                    if entry["use_case"] != "Withdraw"]
    page.route("**/api/app", lambda route: route.fulfill(json=descriptor))
    open_app(page, base_url)
    create_refund(page)
    action = page.locator("#options button[title=Withdraw]")
    assert action.is_disabled()
    assert "no checked navigation destination" in page.locator("#options").inner_text()
    record = request(base_url, "/api/records")[1][0]
    view = request(base_url, f'/api/records/{record["id"]}?actor=customer-a')[1]
    assert next(option for option in view["options"] if option["action"] == "Withdraw")["allowed"] is True
    assert record["version"] == 0
