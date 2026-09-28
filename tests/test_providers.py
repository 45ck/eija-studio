import json, subprocess
from pathlib import Path
import httpx, pytest
from eija_studio.adapters.providers import OpenRouterProvider, CodexProvider, OfflineProvider, parse_proposal
from eija_studio.domain.policy import baseline
from eija_studio.domain.models import DomainError


def proposal_json():
    return OfflineProvider().propose("Let teachers sign off excursions.",baseline()).proposal.model_dump_json()


def test_openrouter_wire_contract_and_no_tools():
    def handler(request):
        body=json.loads(request.content)
        assert str(request.url)=="https://openrouter.ai/api/v1/chat/completions"
        assert request.headers["Authorization"]=="Bearer test-secret"
        assert body["provider"]["require_parameters"]
        assert body["response_format"]["json_schema"]["strict"]
        assert "tools" not in body and body["max_tokens"]==1600
        return httpx.Response(200,json={"model":"fixture/model","choices":[{"finish_reason":"stop","message":{"content":proposal_json()}}],"usage":{"prompt_tokens":22,"secret_debug":"no"}})
    p=OpenRouterProvider("fixture/model","test-secret",transport=httpx.MockTransport(handler))
    result=p.propose("Let teachers sign off excursions.",baseline())
    assert result.provider=="openrouter" and result.usage=={"prompt_tokens":22}

@pytest.mark.parametrize("status,code",[(401,"PROVIDER_AUTH"),(429,"PROVIDER_RATE_LIMIT"),(503,"PROVIDER_HTTP_ERROR"),(302,"PROVIDER_HTTP_ERROR")])
def test_openrouter_errors_are_redacted_and_not_retried(status,code):
    calls=[]
    def handler(request):calls.append(request);return httpx.Response(status,text="secret-value")
    p=OpenRouterProvider("fixture/model","test-secret",transport=httpx.MockTransport(handler))
    with pytest.raises(DomainError) as e:p.propose("request",baseline())
    assert e.value.code==code and "secret-value" not in str(e.value) and len(calls)==1

@pytest.mark.parametrize("content",["not json",'{}','{"summary":"x","alternatives":[],"unknowns":[]}',"x"*65537],
                         ids=["not_json","empty_object","no_alternatives","oversized"])
def test_bad_proposals_fail_closed(content):
    with pytest.raises(DomainError):parse_proposal(content)


def test_provider_timeout_does_not_fallback():
    def handler(request):raise httpx.ReadTimeout("secret diagnostic")
    p=OpenRouterProvider("fixture/model","test-secret",transport=httpx.MockTransport(handler))
    with pytest.raises(DomainError) as e:p.propose("request",baseline())
    assert e.value.code=="PROVIDER_TRANSPORT" and "secret diagnostic" not in str(e.value)


def test_codex_invocation_reuses_cli_auth_without_exposing_keys(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY","never-forward");monkeypatch.setenv("CODEX_API_KEY","no-api-fallback")
    captured=[]
    def runner(args,**kwargs):
        captured.append((args,kwargs))
        assert "OPENROUTER_API_KEY" not in kwargs["env"] and "CODEX_API_KEY" not in kwargs["env"]
        if args[1:]==["exec","--help"]:return subprocess.CompletedProcess(args,0,"--output-schema --ephemeral --ignore-user-config --sandbox","")
        if args[1:]==["login","status"]:return subprocess.CompletedProcess(args,0,"Logged in using ChatGPT","")
        assert "--ignore-user-config" in args and "read-only" in args and "-"==args[-1]
        assert 'forced_login_method="chatgpt"' in args and "features.apps=false" in args
        assert "--dangerously-bypass-approvals-and-sandbox" not in args
        Path(args[args.index("--output-last-message")+1]).write_text(proposal_json())
        return subprocess.CompletedProcess(args,0,"","")
    result=CodexProvider(runner=runner).propose("Let teachers sign off excursions.",baseline())
    assert result.provider=="codex" and len(captured)==3


def test_codex_api_login_not_silently_substituted():
    def runner(args,**kwargs):
        out="--output-schema --ephemeral --ignore-user-config --sandbox" if args[1]=="exec" else "Logged in using an API key"
        return subprocess.CompletedProcess(args,0,out,"")
    p=CodexProvider(runner=runner)
    assert not p.doctor()["ready"]
    with pytest.raises(DomainError) as e:p.propose("request",baseline())
    assert e.value.code=="CODEX_NOT_READY"


def test_network_requires_both_startup_enable_and_request_consent(studio):
    class NeverCall:
        name="test-network";networked=True
        def propose(self,*args):raise AssertionError("Should not call")
    studio.provider=NeverCall()
    c=studio.create("Let teachers sign off excursions.")
    with pytest.raises(DomainError):studio.propose(c["id"],c["version"],consent=True)
    studio.allow_network=True
    with pytest.raises(DomainError):studio.propose(c["id"],c["version"],consent=False)


def test_proposal_cannot_overwrite_a_concurrently_discarded_case(studio):
    c=studio.create("Let teachers sign off excursions.")
    class RacingProvider:
        name="racing-fixture";networked=False
        def propose(self,request,model):
            studio.discard(c["id"],c["version"])
            return OfflineProvider().propose(request,model)
    studio.provider=RacingProvider()
    with pytest.raises(DomainError) as e:studio.propose(c["id"],c["version"])
    assert e.value.code=="STALE_VERSION"
    assert studio.view(c["id"])["case"]["stage"]=="DISCARDED"
    events=studio.view(c["id"])["observations"]["events"]
    assert any(x["kind"]=="ProviderCallNotAccepted" for x in events)


def test_selected_case_is_rejected_before_another_billable_call(studio,selected):
    class NeverCall:
        name="should-not-run";networked=True
        def propose(self,*args):raise AssertionError("must not run")
    studio.provider=NeverCall();studio.allow_network=True
    with pytest.raises(DomainError) as e:studio.propose(selected["id"],selected["version"],consent=True)
    assert e.value.code=="CASE_ALREADY_SELECTED"


@pytest.mark.parametrize('usage',[None,[],42])
def test_invalid_provider_accounting_envelope_fails_cleanly(usage):
    def handler(request):return httpx.Response(200,json={'choices':[{'finish_reason':'stop','message':{'content':proposal_json()}}],'usage':usage})
    provider=OpenRouterProvider('fixture/model','test-secret',transport=httpx.MockTransport(handler))
    with pytest.raises(DomainError) as e:provider.propose('request',baseline())
    assert e.value.code=='PROVIDER_OUTPUT_INVALID'
