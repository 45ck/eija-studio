"""Static checks of the journey specification and the NOT_RUN contract (no browser needed)."""
import re
from pathlib import Path

from quality.hci import __main__ as cli
from quality.hci import journey, laws

INDEX = (journey.WEB / "index.html").read_text(encoding="utf-8")
STATIC_IDS = set(re.findall(r'id="([^"]+)"', INDEX))
DYNAMIC_ID_PREFIXES = ("q-",)  # review questions are rendered by app.js from the packet


def _ids(css: str) -> set[str]:
    return set(re.findall(r"#([A-Za-z][\w-]*)", css))


def test_journey_is_the_brief_journey_in_order():
    ids = [s.id for s in journey.journey()]
    assert len(ids) == len(set(ids))
    order = ["create-case", "ask-interpretations", "select-meaning", "reset-preview", "submit-teacher", "recommend-teacher",
             "approve-registrar", "denied-recommend", "run-verification", "acknowledge", "approve-exact", "apply-baseline"]
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


def test_missing_chrome_is_not_run_never_pass(monkeypatch):
    import playwright.sync_api as sync_api

    class Boom:
        def __enter__(self):
            raise RuntimeError("Executable doesn't exist at chrome.exe\nInstall it")

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(sync_api, "sync_playwright", lambda: Boom())
    ok, reason = journey.prerequisites()
    assert ok is False and "Chrome" in reason


def test_cli_reports_not_run_with_exit_code_3(monkeypatch, capsys):
    monkeypatch.setattr(journey, "prerequisites", lambda: (False, "no chrome here"))
    assert cli.main(["prereq"]) == cli.NOT_RUN == 3
    assert "NOT_RUN: no chrome here" in capsys.readouterr().out
    assert cli.main(["run", "--out", str(Path("unused"))]) == 3


def test_documented_constants_match_the_code():
    readme = (Path(__file__).resolve().parents[2] / "docs" / "hci" / "README.md").read_text(encoding="utf-8")
    for token in ("230", "166", "0.150", "0.28", "1.10", "0.40", "1.35", "400 ms", "24", "MacKenzie", "Card, Moran", "Miller", "Cowan", "Doherty"):
        assert token in readme, token
    assert laws.KlmTimes().M == 1.35
