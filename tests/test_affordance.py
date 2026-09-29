"""WBS 1.3: the open change vocabulary, the affordance map and the drag, with their authority boundary.

PROOF (property): on both packs, from the baseline and from every supported meaning's candidate, and after random
walks of legal edits, every affordance marked legal applies and passes policy, and every illegal one is refused with
exactly the listed codes. The oracle is independent of ``domain.affordance``: structural application followed by
``check_policy``. Negative controls: a lying affordance map (a flipped verdict, a wrong code) is caught by that oracle;
a stored case in the old vocabulary is refused, the same case without it loads.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from hypothesis import given, settings, strategies as st

from eija_studio.domain.affordance import affordances
from eija_studio.domain.models import AGENT, OWNER, DomainError, Workflow
from eija_studio.domain.pack import Pack, load_pack
from eija_studio.domain.policy import apply_meaning, apply_structural_all, apply_transactions, check_policy, demo_candidate, what_if
from eija_studio.domain.transactions import AddState, RetargetTransition, SetRole, parse_transaction
from eija_studio.interfaces.http import create_app
from eija_studio.interfaces.mcp_server import AGENT_TOOLS, OWNER_ONLY_OPERATIONS
from kernel_support import harness_studio

ROOT = Path(__file__).resolve().parents[1]
EXCURSION, LIBRARY = load_pack(ROOT / "packs" / "excursion"), load_pack(ROOT / "packs" / "library-loan")
PACKS = {"excursion": EXCURSION, "library-loan": LIBRARY}
DRAG = json.loads((ROOT / "tests" / "fixtures" / "drag" / "excursion-reject-source-to-initial.json").read_text(encoding="utf-8"))
HEADERS = {"Authorization": "Bearer unit-test-token", "Origin": "http://127.0.0.1:8765"}


def starts(pack: Pack) -> list[Workflow]:
    return [pack.model] + [apply_meaning(pack.model, m.id, pack) for m in pack.meanings if m.supported]


# ---- the independent oracle -------------------------------------------------------------------------------

def expected_verdict(model: Workflow, pack: Pack, transaction: dict) -> tuple[bool, list[str]]:
    """What the kernel must say about one edit: structure first (EDIT_INVALID), then the policy's codes."""
    try:
        result = apply_structural_all(model, (parse_transaction(transaction),), pack)
    except DomainError as error:
        return False, [error.code]
    codes = check_policy(result, pack)
    return not codes, codes


def oracle_problems(model: Workflow, pack: Pack, items: list[dict]) -> list[str]:
    problems = []
    for item in items:
        legal, codes = expected_verdict(model, pack, item["transaction"])
        if (item["legal"], item["codes"]) != (legal, codes):
            problems.append(f"{item['element']} {item['kind']} {item['target']}: map says {item['legal']} {item['codes']}, oracle {legal} {codes}")
    return problems


def check_every_affordance(model: Workflow, pack: Pack) -> list[dict]:
    items = affordances(model, pack)
    assert oracle_problems(model, pack, items) == []
    for item in items:
        tx = parse_transaction(item["transaction"])
        if item["legal"]:
            assert check_policy(apply_transactions(model, (tx,), pack), pack) == []
        else:
            with pytest.raises(DomainError) as caught:
                apply_transactions(model, (tx,), pack)
            assert (caught.value.details or {}).get("codes") == item["codes"], item
    return items


@pytest.mark.parametrize("name", sorted(PACKS))
def test_every_affordance_of_every_start_model_is_truthful(name):
    pack = PACKS[name]
    counts = [(len(items), sum(i["legal"] for i in items)) for items in (check_every_affordance(m, pack) for m in starts(pack))]
    # Measured sizes (transitions x (2 ends x other states) + transitions x other roles), so a silently empty map fails.
    assert counts == {"excursion": [(32, 0), (50, 1)], "library-loan": [(50, 26), (60, 32)]}[name]


@settings(max_examples=50, derandomize=True, deadline=None)
@given(name=st.sampled_from(sorted(PACKS)), start=st.integers(0, 1), walk=st.lists(st.integers(0, 10_000), max_size=3))
def test_random_walks_of_legal_edits_keep_the_map_truthful(name, start, walk):
    pack = PACKS[name]
    model = starts(pack)[start % len(starts(pack))]
    for pick in walk:
        legal = [i for i in check_every_affordance(model, pack) if i["legal"]]
        if not legal:
            break
        model = apply_transactions(model, (parse_transaction(legal[pick % len(legal)]["transaction"]),), pack)
        assert check_policy(model, pack) == []
    check_every_affordance(model, pack)


def test_negative_control_a_lying_affordance_map_is_caught():
    model = demo_candidate()
    items = affordances(model, EXCURSION)
    illegal = next(i for i in items if not i["legal"])
    flipped = [i | {"legal": True, "codes": []} if i is illegal else i for i in items]
    wrong_code = [i | {"codes": ["PROTECTED_AUTHORITY:Submit"]} if i is illegal else i for i in items]
    assert len(oracle_problems(model, EXCURSION, flipped)) == 1
    assert len(oracle_problems(model, EXCURSION, wrong_code)) == 1
    assert oracle_problems(model, EXCURSION, items) == []


# ---- the drag fixture ---------------------------------------------------------------------------------------

def test_the_drag_fixture_names_the_initial_state():
    assert DRAG["transaction"]["state"] == EXCURSION.model.initial_state


def test_the_drag_is_refused_by_the_law_with_refs_in_the_kernel():
    candidate = apply_meaning(EXCURSION.model, DRAG["meaning"], EXCURSION)
    with pytest.raises(DomainError) as caught:
        apply_transactions(candidate, (parse_transaction(DRAG["transaction"]),), EXCURSION)
    assert caught.value.code == DRAG["expected"]["code"]
    assert caught.value.details == {"codes": DRAG["expected"]["codes"], "refs": DRAG["expected"]["refs"]}
    marked = next(i for i in affordances(candidate, EXCURSION) if i["transaction"] == DRAG["transaction"])
    assert (marked["legal"], marked["codes"], marked["refs"]) == (False, DRAG["expected"]["codes"], DRAG["expected"]["refs"])


def test_the_drag_is_refused_over_http_and_the_case_is_unchanged(studio, selected):
    api = TestClient(create_app(studio, "unit-test-token"), base_url="http://127.0.0.1:8765")
    before = studio.view(selected["id"])["case"]
    check = api.post(f"/api/cases/{selected['id']}/edit/check", headers=HEADERS, json={"transaction": DRAG["transaction"]})
    assert check.status_code == 200 and check.json() == {"legal": False, "codes": DRAG["expected"]["codes"], "refs": DRAG["expected"]["refs"]}
    edit = api.post(f"/api/cases/{selected['id']}/edit", headers=HEADERS,
                    json={"expected_version": selected["version"], "transaction": DRAG["transaction"]})
    assert edit.status_code == 409
    assert edit.json()["code"] == "POLICY_BLOCKED"
    assert edit.json()["details"] == {"codes": DRAG["expected"]["codes"], "refs": DRAG["expected"]["refs"]}
    assert studio.view(selected["id"])["case"] == before
    listed = api.get(f"/api/cases/{selected['id']}/affordances", headers=HEADERS).json()
    assert listed["pack"] == "excursion" and len(listed["affordances"]) == 50


def test_a_legal_drag_is_accepted_and_recorded(studio, selected):
    tx = RetargetTransition(kind="retarget_transition", transition="TR-REJECT", end="source", state="Submitted")
    edited = studio.edit(selected["id"], selected["version"], tx, OWNER)
    assert edited["transactions"][-1] == tx.model_dump(mode="json") and edited["version"] == selected["version"] + 1
    assert next(t for t in edited["candidate"]["transitions"] if t["id"] == "TR-REJECT")["from_state"] == "Submitted"


# ---- the authority boundary ---------------------------------------------------------------------------------

@pytest.mark.parametrize("tx", [
    RetargetTransition(kind="retarget_transition", transition="TR-REJECT", end="source", state="Submitted"),
    SetRole(kind="set_role", transition="TR-APPROVE", role="Registrar"),
    AddState(kind="add_state", state="Escalated"),
])
def test_an_agent_cannot_edit_with_any_new_kind(studio, selected, tx):
    with pytest.raises(DomainError) as caught:
        studio.edit(selected["id"], selected["version"], tx, AGENT)
    assert caught.value.code == "AUTHORITY_REQUIRED"


def test_the_new_read_paths_write_nothing(studio, selected):
    def state():
        with studio.store.transaction() as u:
            return u.load_case(selected["id"]), u.observations(selected["id"])
    before = state()
    studio.affordances(selected["id"])
    studio.edit_check(selected["id"], parse_transaction(DRAG["transaction"]))
    studio.edit_check(selected["id"], RetargetTransition(kind="retarget_transition", transition="TR-REJECT", end="source", state="Submitted"))
    assert state() == before


def test_the_agent_surface_gains_no_mutating_edit_path():
    assert "edit" in OWNER_ONLY_OPERATIONS
    assert not {"edit", "edit_check", "affordances", "select", "approve", "apply"} & set(AGENT_TOOLS)


def test_the_new_endpoints_need_the_owner_session(studio, selected):
    api = TestClient(create_app(studio, "unit-test-token"), base_url="http://127.0.0.1:8765")
    assert api.get(f"/api/cases/{selected['id']}/affordances").status_code == 401
    no_token = {"Origin": HEADERS["Origin"]}
    assert api.post(f"/api/cases/{selected['id']}/edit/check", headers=no_token, json={"transaction": DRAG["transaction"]}).status_code == 401


# ---- selection applies the pack's meanings; old cases are refused ------------------------------------------

def test_selection_applies_the_pack_meanings_transactions(selected):
    meaning = EXCURSION.meaning("recommend_only")
    assert selected["transactions"] == [tx.model_dump(mode="json") for tx in meaning.transactions]
    assert Workflow.model_validate(selected["candidate"]) == demo_candidate()


def test_the_second_pack_selects_its_own_meaning_and_refuses_its_unsafe_one(tmp_path):
    studio = harness_studio(tmp_path / "ws", pack=LIBRARY)
    case = studio.create(LIBRARY.fixtures.demo_request)
    case = studio.propose(case["id"], case["version"])
    assert [a["interpretation"] for a in case["proposal"]["alternatives"]] == ["allow_renewal", "member_self_checkout"]
    with pytest.raises(DomainError) as caught:
        studio.select(case["id"], case["version"], "member_self_checkout", OWNER)
    assert caught.value.code == "MEANING_UNSUPPORTED"
    chosen = studio.select(case["id"], case["version"], "allow_renewal", OWNER)
    assert "TR-RENEW" in {t["id"] for t in chosen["candidate"]["transitions"]}
    drag = RetargetTransition(kind="retarget_transition", transition="TR-RETURN", end="source", state="Requested")
    check = studio.edit_check(chosen["id"], drag)
    assert not check["legal"] and "LOAN_RETURN_WITHOUT_CHECKOUT" in check["codes"] and "law:returned-requires-loan" in check["refs"]


@pytest.mark.parametrize("name", sorted(PACKS))
def test_every_meaning_is_what_the_pack_says(name):
    pack = PACKS[name]
    for meaning in pack.meanings:
        if meaning.supported:
            assert check_policy(apply_meaning(pack.model, meaning.id, pack), pack) == [], meaning.id
        elif meaning.transactions:  # an unsupported meaning that would change the model is refused by a law
            assert check_policy(what_if(pack.model, meaning.id, pack), pack) != [], meaning.id


def _old_copy(studio, selected, transactions):
    body = selected | {"id": "0" * 31 + "1", "version": 0, "transactions": transactions}
    with studio.store.transaction() as u:
        u.insert_case(body)
    return body["id"]


def test_a_case_in_the_old_vocabulary_is_refused_cleanly(studio, selected):
    case_id = _old_copy(studio, selected, [{"kind": "enable_recommendation", "rejection_source": "Recommended"}])
    for call in (lambda: studio.view(case_id), lambda: studio.affordances(case_id),
                 lambda: studio.select(case_id, 0, "recommend_only", OWNER)):
        with pytest.raises(DomainError) as caught:
            call()
        assert caught.value.code == "CASE_SCHEMA_OLD"


def test_negative_control_the_same_case_in_the_new_vocabulary_loads(studio, selected):
    case_id = _old_copy(studio, selected, selected["transactions"])
    assert studio.view(case_id)["case"]["id"] == case_id
