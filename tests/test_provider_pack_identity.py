"""Concrete pack isolation with mocked transports/runners; no vendor process or network is used."""
from __future__ import annotations

import json

import httpx
import pytest

from eija_studio.adapters.providers import AnthropicApiProvider, OpenRouterProvider, PROVIDER_NAMES, create_provider
from eija_studio.adapters.providers._common import build_prompt, parse_proposal, system_prompt
from eija_studio.domain import pack as pack_module
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import PACKS_ROOT, load_pack, parse_pack
from test_provider_contract import Harness, SPECS


def variants():
    """Same id and workflow; different reviewed meaning sets, never registered by this helper."""
    original = json.loads((PACKS_ROOT / "excursion" / "pack.json").read_text(encoding="utf-8"))
    original["pack"]["id"] = original["model"]["id"] = "provider-isolation"
    results = []
    for prefix in ("left", "right"):
        data = json.loads(json.dumps(original))
        renamed = {meaning["id"]: prefix + "_" + meaning["id"] for meaning in data["meanings"]}
        for meaning in data["meanings"]:
            meaning["id"] = renamed[meaning["id"]]
        fixture = data["fixtures"]["proposals"]
        alternatives = fixture["fallback"] + [item for rule in fixture["rules"] for item in rule["alternatives"]]
        for alternative in alternatives:
            alternative["interpretation"] = renamed[alternative["interpretation"]]
        results.append(parse_pack(data))
    return tuple(results)


def reply(pack):
    return json.dumps({"summary": "Synthetic pack isolation fixture", "alternatives": [
        {"interpretation": pack.meanings[0].id, "explanation": "Fixture only"}], "unknowns": []})


@pytest.mark.parametrize("name", PROVIDER_NAMES)
def test_registry_preserves_the_exact_pack_snapshot_for_every_provider(name):
    left, right = variants()
    first, second = (create_provider(name, "fixture-model", "synthetic-test-key", pack) for pack in (left, right))
    assert first.pack is left and second.pack is right
    assert left.id == right.id and left.digest != right.digest


def test_explicit_helpers_do_not_consult_the_global_pack_registry(monkeypatch):
    left, right = variants()

    def unexpected_lookup(*args, **kwargs):
        raise AssertionError("A concrete snapshot must not be resolved again by id")

    monkeypatch.setattr("eija_studio.adapters.providers._common.find_pack", unexpected_lookup)
    for chosen, other in ((left, right), (right, left)):
        prompt = build_prompt("synthetic", chosen.model, pack=chosen)
        assert chosen.meanings[0].id in prompt and other.meanings[0].id not in prompt
        assert parse_proposal(reply(chosen), chosen.model, chosen).alternatives[0].interpretation == chosen.meanings[0].id
        with pytest.raises(DomainError) as rejected:
            parse_proposal(reply(other), chosen.model, chosen)
        assert rejected.value.code == "PROVIDER_OUTPUT_INVALID"


@pytest.mark.parametrize("provider_type", (OpenRouterProvider, AnthropicApiProvider))
def test_mock_http_providers_keep_same_id_pack_prompts_and_outputs_isolated(provider_type):
    left, right = variants()
    outputs = [left, right, right]
    prompts = []

    def handler(request):
        body = json.loads(request.content)
        prompts.append(body.get("system") or body["messages"][0]["content"])
        text = reply(outputs[len(prompts) - 1])
        if provider_type is OpenRouterProvider:
            return httpx.Response(200, json={"choices": [{"finish_reason": "stop", "message": {"content": text}}]})
        return httpx.Response(200, json={"stop_reason": "end_turn", "content": [{"type": "text", "text": text}]})

    transport = httpx.MockTransport(handler)
    a = provider_type("fixture-model", "synthetic-test-key", transport=transport, pack=left)
    b = provider_type("fixture-model", "synthetic-test-key", transport=transport, pack=right)
    assert a.propose("synthetic", left.model).proposal.alternatives[0].interpretation == left.meanings[0].id
    assert b.propose("synthetic", right.model).proposal.alternatives[0].interpretation == right.meanings[0].id
    with pytest.raises(DomainError) as rejected:
        a.propose("synthetic", left.model)
    assert rejected.value.code == "PROVIDER_OUTPUT_INVALID"
    for prompt, chosen, other in ((prompts[0], left, right), (prompts[1], right, left), (prompts[2], left, right)):
        assert chosen.meanings[0].id in prompt and other.meanings[0].id not in prompt


@pytest.mark.parametrize("spec", SPECS, ids=lambda spec: spec.name)
def test_mock_cli_providers_keep_same_id_pack_prompts_and_outputs_isolated(spec):
    left, right = variants()
    first = Harness(spec, lambda args: spec.emit(reply(left), list(args)))
    second = Harness(spec, lambda args: spec.emit(reply(right), list(args)))
    a, b = spec.make(runner=first, pack=left), spec.make(runner=second, pack=right)
    assert a.propose("synthetic", left.model).proposal.alternatives[0].interpretation == left.meanings[0].id
    assert b.propose("synthetic", right.model).proposal.alternatives[0].interpretation == right.meanings[0].id
    first.reply = lambda args: spec.emit(reply(right), list(args))
    with pytest.raises(DomainError) as rejected:
        a.propose("synthetic", left.model)
    assert rejected.value.code == "PROVIDER_OUTPUT_INVALID"
    assert all(left.meanings[0].id in call["input"] and right.meanings[0].id not in call["input"] for call in first.mains)
    assert right.meanings[0].id in second.mains[0]["input"] and left.meanings[0].id not in second.mains[0]["input"]


@pytest.mark.parametrize("spec", SPECS, ids=lambda spec: spec.name)
def test_wrong_workflow_rejected_before_cli_preflight_or_invocation(spec):
    left, _ = variants()
    calls = []

    def never_called(*args, **kwargs):
        calls.append(args)
        raise AssertionError("No vendor process is allowed for a pack mismatch")

    provider = spec.make(runner=never_called, pack=left)
    wrong = Workflow.model_validate(left.model.model_dump(mode="json") | {"id": "unrecognised-workflow"})
    with pytest.raises(DomainError) as rejected:
        provider.propose("synthetic", wrong)
    assert rejected.value.code == "PROVIDER_PACK_MISMATCH" and calls == []


@pytest.mark.parametrize("provider_type", (OpenRouterProvider, AnthropicApiProvider))
def test_wrong_workflow_rejected_before_http_request(provider_type):
    left, _ = variants()
    calls = []

    def never_called(request):
        calls.append(request)
        raise AssertionError("No HTTP request is allowed for a pack mismatch")

    provider = provider_type("fixture-model", "synthetic-test-key", pack=left, transport=httpx.MockTransport(never_called))
    wrong = Workflow.model_validate(left.model.model_dump(mode="json") | {"id": "unrecognised-workflow"})
    with pytest.raises(DomainError) as rejected:
        provider.propose("synthetic", wrong)
    assert rejected.value.code == "PROVIDER_PACK_MISMATCH" and calls == []


@pytest.mark.parametrize("name", PROVIDER_NAMES)
def test_constructor_without_pack_captures_default_snapshot(name, tmp_path, monkeypatch):
    left, right = variants()
    location = tmp_path / "pack.json"
    location.write_text(left.model_dump_json(), encoding="utf-8")
    monkeypatch.setenv("EIJA_PACK", str(location))
    original = create_provider(name, "fixture-model", "synthetic-test-key")
    location.write_text(right.model_dump_json(), encoding="utf-8")
    later = create_provider(name, "fixture-model", "synthetic-test-key")
    assert original.pack.digest == left.digest and later.pack.digest == right.digest
    assert left.meanings[0].id in system_prompt(left.model, original.pack)
    assert right.meanings[0].id not in system_prompt(left.model, original.pack)


def test_legacy_id_lookup_remains_fail_closed_and_unknown_model_is_not_prompted(tmp_path, monkeypatch):
    left, right = variants()
    monkeypatch.setattr(pack_module, "_LOADED", {})
    monkeypatch.setattr(pack_module, "_SOURCES", {})
    for index, pack in enumerate((left, right)):
        path = tmp_path / f"pack-{index}.json"
        path.write_text(pack.model_dump_json(), encoding="utf-8")
        load_pack(path)
    with pytest.raises(DomainError) as ambiguous:
        system_prompt(left.model)
    assert ambiguous.value.code == "PACK_IDENTITY_REQUIRED"
    with pytest.raises(DomainError) as ambiguous_output:
        parse_proposal(reply(left), left.model)
    assert ambiguous_output.value.code == "PACK_IDENTITY_REQUIRED"
    unknown = Workflow.model_validate(left.model.model_dump(mode="json") | {"id": "unrecognised-workflow"})
    with pytest.raises(DomainError) as missing:
        build_prompt("synthetic", unknown)
    assert missing.value.code == "PROVIDER_PACK_REQUIRED"
