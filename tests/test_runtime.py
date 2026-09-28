from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
import pytest
from eija_studio.domain.models import ExecuteCommand, DomainError


def command(item, actor="teacher-assigned", action="Recommend", **changes):
    return ExecuteCommand.model_validate({"operation_id":uuid4().hex,"instance_id":item["id"],"actor_id":actor,"action":action,"expected_version":item["version"]}|changes)


def setup(studio, selected, state="Submitted"):
    return studio.reset_preview(selected["id"],selected["version"],state)


def test_one_commit_one_audit_one_enqueue(studio,selected):
    item=setup(studio,selected)
    result=studio.execute(selected["id"],command(item))
    assert result["committed"] and result["instance"]["state"]=="Recommended"
    with studio.store.transaction() as u:
        data=u.observations(selected["id"])
    events=[e for e in data["events"] if e["kind"]=="Audit:ExcursionRecommended"]
    assert len(events)==1 and len(data["outbox"])==1

@pytest.mark.parametrize("actor,action,code",[("teacher-unassigned","Recommend","ASSIGNMENT_DENIED"),("teacher-revoked","Recommend","ACTOR_REVOKED"),("teacher-assigned","Approve","ROLE_DENIED"),("viewer","Recommend","ROLE_DENIED")])
def test_trusted_actor_guards(studio,selected,actor,action,code):
    item=setup(studio,selected)
    with pytest.raises(DomainError) as e: studio.execute(selected["id"],command(item,actor,action))
    assert e.value.code==code
    assert studio.view(selected["id"])["observations"]["instances"][0]["state"]=="Submitted"


def test_duplicate_is_bound_and_does_not_repeat_effects(studio,selected):
    item=setup(studio,selected); cmd=command(item)
    studio.execute(selected["id"],cmd); again=studio.execute(selected["id"],cmd)
    assert again["duplicate"] and not again["committed"] and again["effects"]==[]
    assert len(studio.view(selected["id"])["observations"]["outbox"])==1
    other=setup(studio,selected)
    with pytest.raises(DomainError) as e: studio.execute(selected["id"],command(other,operation_id=cmd.operation_id))
    assert e.value.code=="OPERATION_CONFLICT"


def test_revocation_is_rechecked_before_replay(studio,selected):
    item=setup(studio,selected); cmd=command(item); studio.execute(selected["id"],cmd)
    with studio.store.transaction() as u: u.db.execute("UPDATE actors SET assigned=0 WHERE id='teacher-assigned'")
    with pytest.raises(DomainError) as e: studio.execute(selected["id"],cmd)
    assert e.value.code=="ASSIGNMENT_DENIED"


def test_cross_actor_replay_does_not_expose_original(studio,selected):
    item=setup(studio,selected); cmd=command(item); studio.execute(selected["id"],cmd)
    with pytest.raises(DomainError) as e: studio.execute(selected["id"],command(item,actor="registrar",operation_id=cmd.operation_id))
    assert e.value.code=="ROLE_DENIED"


def test_stale_version_rejects_without_change(studio,selected):
    item=setup(studio,selected)
    with pytest.raises(DomainError) as e: studio.execute(selected["id"],command(item,expected_version=2))
    assert e.value.code=="STALE_VERSION"

@pytest.mark.parametrize("point",["after_state","after_effects","after_operation"])
def test_failure_injection_rolls_back_whole_transaction(studio,selected,point):
    item=setup(studio,selected); cmd=command(item)
    with studio.store.transaction() as u: before=u.effect_counts()
    def fault(where):
        if where==point: raise RuntimeError("simulated abrupt transaction failure")
    with pytest.raises(RuntimeError): studio.execute(selected["id"],cmd,fault=fault)
    with studio.store.transaction() as u:
        assert u.find_instance(item["id"],selected["id"])["state"]=="Submitted"
        assert u.effect_counts()==before
    assert studio.execute(selected["id"],cmd)["committed"]


def test_concurrent_commands_only_one_commits(studio,selected):
    item=setup(studio,selected)
    def attempt(cmd):
        try: return studio.execute(selected["id"],cmd)["committed"]
        except DomainError: return False
    with ThreadPoolExecutor(max_workers=2) as pool: results=list(pool.map(attempt,[command(item),command(item)]))
    assert sorted(results)==[False,True]
    assert len(studio.view(selected["id"])["observations"]["outbox"])==1

@pytest.mark.parametrize("point",["after_state","after_effects","after_operation"])
def test_process_termination_recovery_is_atomic(studio,selected,point):
    import subprocess,sys,os,json
    from pathlib import Path
    item=setup(studio,selected);cmd=command(item)
    with studio.store.transaction() as u:before=u.effect_counts()
    code='''import os,sys,json
from pathlib import Path
from eija_studio.bootstrap import build_studio
from eija_studio.domain.models import ExecuteCommand
studio=build_studio(Path(sys.argv[1]))
def terminate(where):
    if where==sys.argv[4]: os._exit(73)
studio.execute(sys.argv[2],ExecuteCommand.model_validate_json(sys.argv[3]),fault=terminate)
'''
    env=os.environ.copy();env["PYTHONPATH"]=str(Path(__file__).resolve().parents[1]/"src")
    result=subprocess.run([sys.executable,"-c",code,str(studio.store.directory),selected["id"],cmd.model_dump_json(),point],env=env,capture_output=True,timeout=15)
    assert result.returncode==73,result.stderr.decode()
    with studio.store.transaction() as u:
        assert u.find_instance(item["id"],selected["id"])["state"]=="Submitted"
        assert u.effect_counts()==before
    assert studio.execute(selected["id"],cmd)["committed"]
