"""Static checks of the journey specification and the NOT_RUN contract (no browser needed)."""
# ruff: noqa: PLC0415 - the axe test imports the optional `hci` extra only after importorskip
import contextlib
import importlib.util
import inspect
import re
import sys
import types
from pathlib import Path

import pytest

from quality.hci import __main__ as cli
from quality.hci import journey, laws, serve_harness, server

ROOT = Path(__file__).resolve().parents[2]

INDEX = (journey.WEB / "index.html").read_text(encoding="utf-8")
STATIC_IDS = set(re.findall(r'id="([^"]+)"', INDEX))
DYNAMIC_ID_PREFIXES = ("q-",)  # review questions are rendered by app.js from the packet


def _ids(css: str) -> set[str]:
    return set(re.findall(r"#([A-Za-z][\w-]*)", css))


def test_journey_is_the_brief_journey_in_order():
    ids = [s.id for s in journey.journey()]
    assert len(ids) == len(set(ids))
    order = ["create-case", "ask-interpretations", "select-meaning", "reset-preview", "submit-teacher", "recommend-teacher",
             "approve-registrar", "denied-recommend", "run-verification", "open-review-subject",
             "acknowledge", "approve-exact", "apply-baseline"]
    assert [i for i in ids if i in order] == order
    assert ids.index("actor-unassigned") < ids.index("denied-recommend")


def test_every_selector_in_the_journey_exists_in_the_shipped_html():
    """A UI refactor that renames a control must break this cheap test before it breaks the browser run."""
    missing = set()
    for step in journey.journey():
        css = " ".join(filter(None, [step.ref.css, step.ref.within, step.expect.css if step.expect else "",
                                     *(step.decision.selectors if step.decision else ())]))
        for ident in _ids(css):
            if ident not in STATIC_IDS and not ident.startswith(DYNAMIC_ID_PREFIXES):
                missing.add((step.id, ident))
    assert not missing


def test_tab_buttons_referenced_by_the_journey_exist():
    for tab in re.findall(r'data-tab="(\w+)"', " ".join(s.ref.css or "" for s in journey.journey())):
        assert f'data-tab="{tab}"' in INDEX


def test_m_operators_are_justified_and_shift_counting_is_explicit():
    thoughts = [s.id for s in journey.journey() if s.think]
    assert "select-meaning" in thoughts and "create-case" not in thoughts  # M only at real decision/reading moments
    assert journey.keystrokes("abc") == 3
    assert journey.keystrokes("Ab.") == 4  # Shift for the capital counts as its own K
    assert journey.keystrokes(journey.REQUEST) == len(journey.REQUEST) + 1


def test_probe_never_mutates_the_page():
    """The instrumentation must only observe: no click/type/dispatch calls in the injected script."""
    source = journey.PROBE.read_text(encoding="utf-8")
    for forbidden in (".click(", ".dispatchEvent(", ".submit(", ".value =", "innerHTML =", ".remove()", ".appendChild("):
        assert forbidden not in source, forbidden


def _fake_playwright(monkeypatch, sync_playwright):
    """Stub the optional `hci` extra so these tests pass, and stay meaningful, in a `.[dev]`-only environment."""
    package = types.ModuleType("playwright")
    package.__path__ = []
    sync_api = types.ModuleType("playwright.sync_api")
    sync_api.sync_playwright = sync_playwright
    monkeypatch.setitem(sys.modules, "playwright", package)
    monkeypatch.setitem(sys.modules, "playwright.sync_api", sync_api)
    monkeypatch.setitem(sys.modules, "axe_playwright_python", types.ModuleType("axe_playwright_python"))


def test_missing_chrome_is_not_run_never_pass(monkeypatch):
    class Boom:
        def __enter__(self):
            raise RuntimeError("Executable doesn't exist at chrome.exe\nInstall it")

        def __exit__(self, *args):
            return False

    _fake_playwright(monkeypatch, Boom)
    ok, reason = journey.prerequisites()
    assert ok is False and "Chrome" in reason


def test_missing_python_packages_are_not_run_never_pass(monkeypatch):
    for name in ("playwright", "playwright.sync_api", "axe_playwright_python"):
        monkeypatch.setitem(sys.modules, name, None)  # None in sys.modules makes the import raise ImportError
    ok, reason = journey.prerequisites()
    assert ok is False and "python packages missing" in reason


def test_release_identity_on_unstamped_source_is_not_run_and_other_journey_failures_fail(monkeypatch, capsys):
    monkeypatch.setattr(journey, "prerequisites", lambda: (True, "154"))

    def blocked(**_):
        raise journey.ReleaseIdentityUnavailable("SOURCE_REVIEW_REQUIRED")

    monkeypatch.setattr(journey, "collect", blocked)
    assert cli.main(["run", "--identity", "release", "--out", "unused"]) == cli.NOT_RUN
    assert "NOT_RUN: SOURCE_REVIEW_REQUIRED" in capsys.readouterr().out

    def broken(**_):
        raise journey.JourneyError("step x: not reachable")

    monkeypatch.setattr(journey, "collect", broken)
    assert cli.main(["run", "--out", "unused"]) == 1  # a UI failure is a failure, not a traceback and not NOT_RUN
    assert "FAIL:" in capsys.readouterr().out


def test_studio_server_removes_its_scratch_directory_when_the_caller_raises(monkeypatch):
    seen = []

    @contextlib.contextmanager
    def fake_serve(scratch, identity, timeout):
        seen.append(scratch)
        (scratch / "server.log").write_text("http://127.0.0.1:1/#secret-launch-token", encoding="utf-8")
        yield "http://127.0.0.1:1/#secret-launch-token"

    monkeypatch.setattr(server, "_serve", fake_serve)
    with pytest.raises(RuntimeError, match="boom"), server.studio_server("cleanup-test"):
        assert seen[0].exists()
        raise RuntimeError("boom")
    assert not seen[0].exists()  # the log holding the launch token is gone even though the block failed


def test_serve_harness_identity_matches_the_kernel_test_harness():
    """serve_harness duplicates tests/conftest.py's harness identity; this catches drift between the two copies."""
    conftest = importlib.util.spec_from_file_location("kernel_conftest", ROOT / "tests" / "conftest.py")
    module = importlib.util.module_from_spec(conftest)
    conftest.loader.exec_module(module)
    assert serve_harness.HARNESS_MARK == module.HARNESS_MARK
    assert serve_harness.harness_identity() == module.harness_identity()
    assert serve_harness.harness_identity()["identity_source"] == "pytest-harness"


def test_axe_is_loaded_with_an_explicit_utf8_read():
    """The package default reads axe.min.js with the platform locale (cp1252 on this PC); we load it as UTF-8."""
    pytest.importorskip("axe_playwright_python", reason="NOT_RUN: hci extra not installed")
    from axe_playwright_python.base import AXE_FILE_PATH
    from axe_playwright_python.sync_playwright import Axe

    axe = Axe.from_file(AXE_FILE_PATH)
    assert axe.axe_script == AXE_FILE_PATH.read_bytes().decode("utf-8")
    assert not axe.axe_script.isascii()  # the file has non-ASCII text, so the encoding choice matters
    assert "from_file(AXE_FILE_PATH)" in inspect.getsource(journey.run_axe)


def test_cli_reports_not_run_with_exit_code_3(monkeypatch, capsys):
    monkeypatch.setattr(journey, "prerequisites", lambda: (False, "no chrome here"))
    assert cli.main(["prereq"]) == cli.NOT_RUN == 3
    assert "NOT_RUN: no chrome here" in capsys.readouterr().out
    assert cli.main(["run", "--out", str(Path("unused"))]) == 3


def test_documented_constants_are_the_constants_in_the_code():
    """Each README constant is bound to its label with a regex built from laws.py, so 'b = 0.500' in the README fails."""
    readme = (ROOT / "docs" / "hci" / "README.md").read_text(encoding="utf-8")
    fitts, hick, klm = laws.FittsModel(), laws.HickModel(), laws.KlmTimes()
    expected = [
        rf"`a = {fitts.a:.3f} s`, `b = {fitts.b:.3f} s/bit`",
        rf"`b = {hick.b:.3f} s/bit`",
        rf"`K` {klm.K:.2f} s.*`P` {klm.P:.2f} s.*`B` {klm.B:.2f} s.*`H` {klm.H:.2f} s.*`M` {klm.M:.2f} s",
        rf"MT = {round(fitts.a * 1000)} \+ {round(fitts.b * 1000)} \* ID",
        rf"`W < {laws.MIN_TARGET_PX:.0f} px`",
        rf"`ID > {laws.MAX_ID_BITS:.0f}` bits",
        rf"`n > {laws.MAX_CHOICES}`",
        rf"about {laws.DOHERTY_MS:.0f} ms",
    ]
    for pattern in expected:
        assert re.search(pattern, readme), pattern
    for source in ("MacKenzie", "Card, Moran", "Miller", "Cowan", "Doherty"):
        assert source in readme, source


def test_verification_and_deliberate_review_are_distinct_native_journey_actions(monkeypatch):
    steps = journey.journey()
    verify_index = next(index for index, step in enumerate(steps) if step.id == "run-verification")
    verify, review, answer = steps[verify_index:verify_index + 3]
    assert (verify.kind, verify.ref.css, verify.expect.kind, verify.view) == (
        "click", "#verify", "verification_ready", "evidence-verified",
    )
    assert (review.kind, review.ref.css, review.expect.kind, review.view) == (
        "click", "#review-subject", "review_ready", "evidence-review-open",
    )
    assert answer.id == "answer-authority"
    assert review.think is None  # A disclosure operation, not an invented additional mental decision.

    page = types.SimpleNamespace(on=lambda *_: None, locator=lambda _: types.SimpleNamespace(count=lambda: 1))
    runner = journey.Runner(page, "pointer", True)
    actions, checkpoints = [], []
    monkeypatch.setattr(runner, "_do_click", lambda step, *_: actions.append(step.id))
    monkeypatch.setattr(runner, "check", lambda _: None)
    monkeypatch.setattr(runner, "checkpoint", checkpoints.append)
    runner._run_step(verify)
    assert checkpoints == ["evidence-verified"]
    runner._run_step(review)
    assert actions == ["run-verification", "open-review-subject"]
    assert checkpoints == ["evidence-verified", "evidence-review-open"]
