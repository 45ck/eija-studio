"""Second inspection of running and checking in place (2026-11-14): every answer the page asks the server for is shown
only while it is the newest on its channel and about the view on show (`ticket` in play.js). The first inspection found
that class of defect four times (D-02, D-06, D-09, D-11), each fixed on its own; this pins one rule for all of them.

A request in the run, check and lens modules either takes a ticket in the function that makes it, or is listed below
with the guard it has instead. A new request that does neither fails here."""
from __future__ import annotations

import re
from pathlib import Path

WEB = Path(__file__).resolve().parents[1] / "src/eija_studio/resources/web"
MODULES = ("play.js", "play-run.js", "play-tests.js", "play-laws.js", "play-access.js", "play-sequence.js",
           "play-missing.js", "play-roles.js")
CALL = re.compile(r"(?<![\w.])(?:P\.)?api\(\s*[`\"]/api/")
FUNCTION = re.compile(r"^(\s*)(?:async\s+)?function\s+(\w+)\s*\(")

# (module, function) -> the guard it has instead of a ticket. Each is a decision, not a gap.
OTHER_GUARD = {
    ("play.js", "ask"): "the chat plan: its answer becomes a new plan card, tied to the plan it was asked on",
    ("play.js", "refreshPlan"): "a sequence number per plan; a newer tick or another plan drops it",
    ("play.js", "refreshRipple"): "a sequence number and the plan it was asked for",
    ("play.js", "loadScreens"): "returns the answer to its caller and keeps it only for the same view and screens",
    ("play.js", "showEffects"): "a sequence number and the effects key it was asked about",
    ("play.js", "activated"): "start-up: nothing is on show yet",
    ("play.js", "start"): "start-up: nothing is on show yet",
    ("play-run.js", "stop"): "an action (stop the running app), not an answer that is shown",
    ("play-laws.js", "proveNow"): "one proof per model and draft at a time (D-11), dropped if either changed",
    ("play-tests.js", "run"): "the newest run only, which re-runs on the model shown (D-09)",
    ("play-roles.js", "permissions"): "a cache keyed by the view it was asked about",
    ("play-missing.js", "load"): "a sequence number; every change asks again",
}


def _requests():
    for module in MODULES:
        lines = (WEB / module).read_text(encoding="utf-8").splitlines()
        starts = [(i, m.group(2), len(m.group(1))) for i, line in enumerate(lines) if (m := FUNCTION.match(line))]
        for i, line in enumerate(lines):
            if not CALL.search(line):
                continue
            at, name, indent = max(s for s in starts if s[0] <= i)
            end = next((j for j, _, d in starts if j > at and d <= indent), len(lines))
            yield module, name, "\n".join(lines[at:end])


def test_every_request_drops_an_answer_for_another_view():
    unguarded = sorted({(module, name) for module, name, body in _requests()
                        if "ticket(" not in body and (module, name) not in OTHER_GUARD})
    assert unguarded == [], f"take a ticket (P.ticket) before asking, or list the other guard: {unguarded}"


def test_the_list_of_other_guards_has_no_stale_entries():
    found = {(module, name) for module, name, _ in _requests()}
    assert set(OTHER_GUARD) <= found


def test_a_ticket_is_current_only_for_the_newest_question_about_the_view_on_show():
    source = (WEB / "play.js").read_text(encoding="utf-8")
    body = source[source.index("function ticket("):source.index("function el(")]
    assert "tickets[channel] === n" in body and 'viewKey() + "\\u0000" + also() === at' in body
    assert "ticket," in source[source.index("window.PlayIDE = {"):]  # the modules reach it through the bridge
