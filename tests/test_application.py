import copy, json
import pytest
from eija_studio.bootstrap import build_studio
from eija_studio.domain.models import OWNER, AGENT, DomainError, SemanticTransaction, LayoutChange, fingerprint
from eija_studio.domain.change_case import ChangeCase
from eija_studio.application.compiler import compile_case
from kernel_support import approve, reject_from
from eija_studio.domain.transactions import parse_transaction


def test_agent_cannot_choose_meaning_or_approve(studio,selected):
    with pytest.raises(DomainError): studio.approve(selected["id"],selected["version"],"x",{},True,AGENT)
    c=studio.create("Let teachers sign off excursions.");c=studio.propose(c["id"],c["version"])
    with pytest.raises(DomainError):studio.select(c["id"],c["version"],"recommend_only",AGENT)


def test_unsupported_meaning_is_not_silently_downgraded(studio):
    c=studio.create("Let teachers sign off excursions.");c=studio.propose(c["id"],c["version"])
    with pytest.raises(DomainError) as e:studio.select(c["id"],c["version"],"final_approval",OWNER)
    assert e.value.code=="MEANING_UNSUPPORTED" and studio.view(c["id"])["case"]["candidate"] is None


def test_preview_save_discard_do_not_change_baseline(studio,selected):
    with studio.store.transaction() as u: before=u.active()
    c=studio.save(selected["id"],selected["version"])
    studio.reset_preview(c["id"],c["version"])
    studio.discard(c["id"],c["version"])
    with studio.store.transaction() as u: assert u.active()==before
    with pytest.raises(DomainError):studio.reset_preview(c["id"],c["version"]+1)


def test_verifier_produces_125_observations_and_human_unknown(studio,verified):
    receipt=verified["receipts"][-1]
    assert len(receipt["artifact"]["cells"])==125
    packet=studio.view(verified["id"])["packet"]
    assert packet["eligible"] and packet["human_understanding"]=="UNKNOWN"
    assert packet["technical_claims"]["runtime_matrix"]=="PASS"


def test_live_candidate_edit_invalidates_immutable_receipt_and_decision(studio,verified):
    before=json.dumps(verified["receipts"],sort_keys=True)
    c=approve(studio,verified)
    c=studio.edit(c["id"],c["version"],reject_from("Submitted"),OWNER)
    assert json.dumps(c["receipts"],sort_keys=True)==before
    assert c["decision"] is None
    assert studio.view(c["id"])["packet"]["technical_claims"]["runtime_matrix"]=="STALE"
    with pytest.raises(DomainError):studio.apply(c["id"],c["version"],OWNER)


def test_layout_keeps_domain_evidence_but_clears_exact_decision(studio,verified):
    first=studio.view(verified["id"])["packet"]
    c=approve(studio,verified)
    c=studio.layout(c["id"],c["version"],LayoutChange(node="Submitted",x=120,y=80),OWNER)
    p=studio.view(c["id"])["packet"]
    assert p["subject"]["semantic"]==first["subject"]["semantic"]
    assert p["subject"]["presentation"]!=first["subject"]["presentation"]
    assert p["technical_claims"]["runtime_matrix"]=="PASS" and c["decision"] is None


def test_same_transaction_from_two_views_same_hash(studio,selected):
    tx1=parse_transaction({"kind":"retarget_transition","transition":"TR-REJECT","end":"source","state":"Submitted"})
    tx2=parse_transaction({"state":"Submitted","end":"source","transition":"TR-REJECT","kind":"retarget_transition"})
    from eija_studio.domain.policy import apply_transaction
    case=ChangeCase.model_validate(selected)
    assert apply_transaction(case.candidate,tx1).semantic_hash==apply_transaction(case.candidate,tx2).semantic_hash

@pytest.mark.parametrize("dimension",["implementation","policy","environment","harness"])
def test_subject_dimension_substitution_cannot_pass(studio,verified,dimension):
    identity=studio.identity_provider();identity[dimension]="different"
    case=ChangeCase.model_validate(verified)
    p=compile_case(case,identity,studio.signer.authentic,case.baseline_version)
    assert not p["eligible"] and p["technical_claims"]["runtime_matrix"]=="STALE"


def test_technical_pass_cannot_establish_field_approval(studio,verified):
    packet=studio.view(verified["id"],scope="field-use")["packet"]
    assert packet["human_understanding"]=="UNKNOWN" and not packet["eligible"]
    assert "HUMAN_FIELD_EVIDENCE_REQUIRED" in packet["blockers"]


def test_relabelled_browser_claim_never_becomes_human_proof(studio,verified):
    case=copy.deepcopy(verified)
    r=case["receipts"][0];r["claim"]="human_understanding";r["kind"]="browser_test";r["status"]="PASS";r["admissible"]=True
    # Even an internally sealed browser claim cannot satisfy runtime/human obligations.
    case["receipts"][0]=studio.signer.seal(r)
    case=ChangeCase.model_validate(case)
    p=compile_case(case,studio.identity_provider(),studio.signer.authentic,case.baseline_version,"field-use")
    assert not p["eligible"] and p["human_understanding"]=="UNKNOWN"


def test_tampered_raw_artifact_is_not_accepted(studio,verified):
    case=copy.deepcopy(verified);case["receipts"][0]["artifact"]["cells"][0]["actual"]["accepted"]=not case["receipts"][0]["artifact"]["cells"][0]["actual"]["accepted"]
    c=ChangeCase.model_validate(case)
    p=compile_case(c,studio.identity_provider(),studio.signer.authentic,c.baseline_version)
    assert not p["eligible"] and p["technical_claims"]["runtime_matrix"]=="FAIL"


def test_wrong_answers_do_not_approve(studio,verified):
    p=studio.view(verified["id"])["packet"]
    with pytest.raises(DomainError) as e:studio.approve(verified["id"],verified["version"],p["subject_hash"],{"authority":"Teacher"},True,OWNER)
    assert e.value.code=="MEANING_CHECK_FAILED"


def test_core_change_requires_source_review(studio,verified):
    original=studio.identity_provider
    studio.identity_provider=lambda:original()|{"trusted_fixture":False}
    p=studio.view(verified["id"])["packet"]
    assert not p["eligible"] and "SOURCE_REVIEW_REQUIRED" in p["blockers"]
    with pytest.raises(DomainError):studio.verify(verified["id"],verified["version"])


def test_complete_local_request_to_apply_and_export(studio,verified):
    c=approve(studio,verified);c=studio.apply(c["id"],c["version"],OWNER)
    assert c["stage"]=="APPLIED"
    with studio.store.transaction() as u:assert u.active()["version"]==1
    export=studio.export(c["id"])
    assert export["payload_hash"]==fingerprint(export["payload"])
    assert export["payload"]["packet"]["human_understanding"]=="UNKNOWN"
    assert "receipt.key" not in json.dumps(export)


def test_two_approved_cases_cannot_silently_overwrite(studio,verified):
    c1=approve(studio,verified)
    c2=studio.create("Let teachers sign off excursions.");c2=studio.propose(c2["id"],c2["version"])
    c2=studio.select(c2["id"],c2["version"],"recommend_only",OWNER);c2=studio.verify(c2["id"],c2["version"]);c2=approve(studio,c2)
    studio.apply(c1["id"],c1["version"],OWNER)
    with pytest.raises(DomainError):studio.apply(c2["id"],c2["version"],OWNER)


def test_restart_preserves_cases_and_receipt_signatures(studio,verified,open_studio):
    reopened=open_studio(studio.store.directory)
    assert reopened.view(verified["id"])["packet"]["eligible"]


def test_backup_is_restorable(studio,verified,tmp_path):
    target=tmp_path/"backup.sqlite3";studio.store.backup(target)
    import sqlite3
    with sqlite3.connect(target) as db:assert db.execute("SELECT COUNT(*) FROM cases").fetchone()[0]==1


def test_old_review_subject_is_rejected_even_when_evidence_still_applies(studio,verified):
    old=studio.view(verified["id"])["packet"]
    c=studio.layout(verified["id"],verified["version"],LayoutChange(node="Submitted",x=9,y=8),OWNER)
    with pytest.raises(DomainError) as e:
        studio.approve(c["id"],c["version"],old["subject_hash"],{q["id"]:q["expected"] for q in old["questions"]},True,OWNER)
    assert e.value.code=="SUBJECT_CHANGED"


def test_conflicting_authenticated_receipts_do_not_average_into_pass(studio,verified):
    c=copy.deepcopy(verified);r=copy.deepcopy(c["receipts"][0]);cell=r["artifact"]["cells"][0]
    cell["actual"]["accepted"]=not cell["expected"]["accepted"]
    r["artifact_hash"]=fingerprint(r["artifact"]);r["id"]="counterexample"
    c["receipts"].append(studio.signer.seal(r));case=ChangeCase.model_validate(c)
    p=compile_case(case,studio.identity_provider(),studio.signer.authentic,case.baseline_version)
    assert p["technical_claims"]["runtime_matrix"]=="CONFLICT" and not p["eligible"]

@pytest.mark.parametrize('mutation', ['empty_observations','missing_cell','duplicate_cell','wrong_boolean_type','wrong_matrix','unknown_claim','nontext_state','invalid_subject'])
def test_authenticated_malformed_receipts_cannot_fake_coverage(studio,verified,mutation):
    c=copy.deepcopy(verified);r=c['receipts'][0];a=r['artifact']
    if mutation=='empty_observations':a['cells']=[{}];a['expected_cells']=1
    elif mutation=='missing_cell':a['cells'].pop();a['expected_cells']-=1
    elif mutation=='duplicate_cell':a['cells'][0]=copy.deepcopy(a['cells'][1])
    elif mutation=='wrong_boolean_type':
        a['cells'][0]['actual']['accepted']=1;a['cells'][0]['expected']['accepted']=1
    elif mutation=='wrong_matrix':a['matrix']['actors']=['registrar']
    elif mutation=='unknown_claim':r['claim']='human_understanding'
    elif mutation=='nontext_state':a['cells'][0]['actual']['state']=[]
    elif mutation=='invalid_subject':r['subject']=[]
    r['artifact_hash']=fingerprint(a);c['receipts'][0]=studio.signer.seal(r)
    case=ChangeCase.model_validate(c);p=compile_case(case,studio.identity_provider(),studio.signer.authentic,case.baseline_version)
    assert not p['eligible']
