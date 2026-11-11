"""Intent eval harness (ADR-0229): the kernel grades whether a provider picked the meaning a request asked for.

Offline only: the fixture provider is deterministic and SYNTHETIC. Live runs are by hand with consent.
"""
from __future__ import annotations

import json

import pytest

from eija_studio.adapters.providers import OfflineProvider
from eija_studio.application.ports import ProviderResult
from eija_studio.domain.models import Alternative, Proposal
from quality.evals import intent

CASES = intent.load_cases()


def test_every_case_names_a_real_pack_and_meaning_and_ids_are_unique():
    assert len({c["id"] for c in CASES}) == len(CASES)
    for case in CASES:
        pack = intent.load_pack(intent.ROOT / "packs" / case["pack"])
        assert pack.meaning(case["expect"]) is not None, case["id"]
        assert case["kind"] in {"example", "paraphrase", "unsafe", "off_topic"}
        assert (case["kind"] == "unsafe") == (case["expect"] != "unsupported" and not pack.meaning(case["expect"]).supported)


def test_the_kernel_allows_every_supported_meaning_and_refuses_every_unsafe_one():
    report = intent.evaluate("offline")
    assert report["summary"]["kernel_disagreements"] == []
    assert report["evidence"] == "SYNTHETIC" and report["summary"]["cases"] == len(CASES)


def test_the_offline_fixture_answers_its_own_chat_examples():
    rows = intent.evaluate("offline")["results"]
    assert all(r["outcome"] == "correct" for r in rows if r["kind"] in {"example", "off_topic"})


def test_a_safe_answer_to_an_unsafe_request_is_graded_as_substituted():
    pack = intent.load_pack(intent.ROOT / "packs" / "refund-desk")
    assert intent.grade(pack, "agent_auto_approve", "agent_hands_off") == "substituted"
    assert intent.grade(pack, "agent_auto_approve", "agent_auto_approve") == "correct"
    assert intent.grade(pack, "agent_hands_off", "unsupported") == "wrong"
    assert intent.grade(pack, "unsupported", "agent_hands_off") == "wrong"  # off-topic answered with a change: wrong, not substituted
    assert intent.grade(pack, "agent_hands_off", None) == "invalid"


class _Swapper(OfflineProvider):
    """A negative control: always answers with the pack's first supported meaning, whatever was asked."""
    def propose(self, request, model):
        meaning = next(m for m in self.pack.meanings if m.supported)
        proposal = Proposal(summary="x", alternatives=(Alternative(interpretation=meaning.id, explanation="x"),), unknowns=())
        return ProviderResult(proposal, "swapper", "", {}, False)


def test_a_provider_that_swaps_meanings_is_caught_on_every_unsafe_case(monkeypatch):
    monkeypatch.setattr(intent, "create_provider", lambda name, model="", key=None, pack=None: _Swapper(pack))
    rows = intent.evaluate("swapper")["results"]
    assert all(r["outcome"] == "substituted" for r in rows if r["kind"] == "unsafe")


def test_a_negative_call_cap_is_refused_before_any_call(monkeypatch):
    monkeypatch.setattr(intent, "run_case", lambda *a, **k: pytest.fail("no case may run"))
    with pytest.raises(ValueError):
        intent.evaluate("offline", max_calls=-1)
    with pytest.raises(SystemExit):
        intent.main(["--max-calls", "-1"])


def test_max_calls_stops_the_run_and_says_so():
    report = intent.evaluate("offline", max_calls=3)
    assert report["summary"]["cases"] == 3 and report["stopped_at_call_limit"] is True


def test_a_networked_provider_without_consent_makes_no_call(tmp_path, monkeypatch):
    monkeypatch.setattr(intent, "evaluate", lambda *a, **k: pytest.fail("a live call was attempted without consent"))
    out = tmp_path / "r.json"
    assert intent.main(["--provider", "openai", "--model", "m", "--out", str(out)]) == 2
    assert intent.main(["--provider", "openai", "--model", "m", "--allow-network", "--out", str(out)]) == 2
    assert not out.exists()


def test_the_cli_writes_a_report(tmp_path):
    out = tmp_path / "r.json"
    assert intent.main(["--out", str(out)]) == 0
    assert json.loads(out.read_text(encoding="utf-8"))["scope"] == "intent-eval"
