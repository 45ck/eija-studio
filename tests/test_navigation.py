"""Navigation is an exact, bounded projection; it is not an authority shortcut."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from eija_studio.application.build_subject import SUBJECT_FILE, build_subject, checked_build_subject
from eija_studio.application.presentation import app_presentation
from eija_studio.bootstrap import source_identity
from eija_studio.domain.data import data_for
from eija_studio.domain.models import DomainError, canonical
from eija_studio.domain.navigation import Navigation, navigation_for
from eija_studio.domain.pack import load_pack
from eija_studio.domain.screens import Screens, screens_for
from eija_studio.interfaces.app_build import app_files

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def inputs():
    pack = load_pack(ROOT / "packs/library-loan")
    data = data_for(pack)
    return pack, pack.model, data, screens_for(pack, pack.model, data)


def test_navigation_names_real_panel_scope_and_existing_actions(inputs):
    pack, model, data, screens = inputs
    navigation = navigation_for(pack, model, data, screens)
    assert navigation.schema_version == "eija.navigation.v1" and navigation.record == "Loan"
    assert [(d.id, d.parent, d.panel, d.focus, d.record_required) for d in navigation.destinations[:3]] == [
        ("records", None, "records", "records-title", False), ("new-record", "records", "create", "title", False),
        ("record-detail", "records", "detail", "detail-title", True)]
    checkout = next(d for d in navigation.destinations if d.use_case == "CheckOut")
    assert checkout.model_dump() == {"id": "action:TR-CHECKOUT", "kind": "action", "parent": "record-detail",
        "title": "Check out", "panel": "action-screen", "focus": "action-screen", "record_required": True,
        "use_case": "CheckOut", "transition_ref": "transition:TR-CHECKOUT"}
    assert navigation.capabilities.model_dump() == {"create": "executable", "read": "executable",
                                                    "update": "unsupported", "delete": "unsupported"}
    assert navigation_for(pack, model, data, screens) == navigation


@pytest.mark.parametrize("mutation", [
    lambda d: d["capabilities"].update(delete="executable"),
    lambda d: d["destinations"][1].update(panel="arbitrary-route"),
    lambda d: d["destinations"][2].update(record_required=False),
    lambda d: d["destinations"][3].update(parent="new-record"),
    lambda d: d["destinations"][3].update(id="action:OTHER"),
    lambda d: d["destinations"].append(d["destinations"][0]),
    lambda d: d["destinations"][0].update(use_case="Approve"),
])
def test_typed_navigation_refuses_fake_crud_broken_scope_and_dangling_hierarchy(inputs, mutation):
    document = navigation_for(*inputs).model_dump(mode="json")
    mutation(document)
    with pytest.raises(ValidationError):
        Navigation.model_validate(document)


def test_foreign_contracts_and_unknown_screen_actions_cannot_enter_navigation(inputs):
    pack, model, data, screens = inputs
    foreign = screens.model_copy(update={"id": "other-pack"})
    with pytest.raises(DomainError) as refused:
        navigation_for(pack, model, data, foreign)
    assert refused.value.code == "NAVIGATION_PACK_MISMATCH"
    document = screens.model_dump(mode="json")
    document["screens"][1]["use_case"] = "InventedAction"
    with pytest.raises(DomainError) as refused:
        navigation_for(pack, model, data, Screens.model_validate(document))
    assert refused.value.code == "SCREENS_BLOCKED"


def test_shipped_navigation_and_presentation_read_one_subject_and_screen_title_changes_it(inputs):
    pack, model, _, screens = inputs
    files, manifest = app_files(pack, model, screens, identity_provider=source_identity)
    navigation = Navigation.model_validate_json(files["app/navigation.json"])
    assert app_presentation(files)["navigation"] == navigation.model_dump(mode="json")
    assert "app/navigation.json" in manifest["subject"]["payload_paths"]
    assert checked_build_subject(files) == json.loads(files[SUBJECT_FILE])
    changed = screens.model_dump(mode="json")
    changed["screens"][1]["title"] = "Issue this loan"
    after_files, after_manifest = app_files(pack, model, Screens.model_validate(changed), identity_provider=source_identity)
    assert after_manifest["subject"]["model_hash"] == manifest["subject"]["model_hash"]
    assert after_manifest["subject"]["digest"] != manifest["subject"]["digest"]
    after_navigation = Navigation.model_validate_json(after_files["app/navigation.json"])
    assert after_navigation.digest != navigation.digest
    assert next(d for d in after_navigation.destinations if d.use_case == "CheckOut").title == "Issue this loan"
    substituted = dict(files) | {"app/navigation.json": canonical(after_navigation)}
    with pytest.raises(DomainError) as refused:
        app_presentation(substituted)
    assert refused.value.code == "BUILD_SUBJECT_MISMATCH"


def test_a_distinct_subject_cannot_make_navigation_disagree_with_the_workflow(inputs):
    pack, model, _, screens = inputs
    files, manifest = app_files(pack, model, screens, identity_provider=source_identity)
    navigation = json.loads(files["app/navigation.json"])
    checkout = next(item for item in navigation["destinations"] if item["use_case"] == "CheckOut")
    checkout["use_case"] = "Cancel"
    changed = dict(files) | {"app/navigation.json": canonical(navigation)}
    previous = manifest["subject"]
    # A deliberately different test subject still needs cross-contract fidelity.
    changed[SUBJECT_FILE] = canonical(build_subject(changed, implementation_digest=previous["implementation_digest"],
                                                   template_paths=previous["template_paths"]))
    with pytest.raises(DomainError) as refused:
        app_presentation(changed)
    assert refused.value.code == "NAVIGATION_MODEL_MISMATCH"
