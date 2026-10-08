"""Screens (ADR-0154): each use case's screen, bound to the record class, checked before any app is built from it."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from eija_studio.application.appgen import generate
from eija_studio.domain.data import data_for
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import load_pack
from eija_studio.domain.screens import (CREATE, Screens, check_screens, default_screens, load_screens, parse_screens,
                                        screens_for, use_cases)

ROOT = Path(__file__).resolve().parents[1]
LOAN = load_pack(ROOT / "packs" / "library-loan")
EXCURSION = load_pack(ROOT / "packs" / "excursion")


def codes(screens: Screens, pack=LOAN) -> list[str]:
    return sorted(p["code"] for p in check_screens(screens, pack.model, data_for(pack)))


def edited(screens: Screens, which: str, **change) -> Screens:
    document = screens.model_dump(mode="json")
    for screen in document["screens"]:
        if screen["use_case"] == which:
            screen.update(change)
    return Screens.model_validate(document)


def test_use_cases_are_creating_a_record_then_each_action():
    assert use_cases(LOAN.model) == [CREATE, *dict.fromkeys(t.action for t in sorted(LOAN.model.transitions, key=lambda t: t.id))]


def test_a_pack_without_screens_gets_one_screen_per_use_case():
    screens = screens_for(EXCURSION, EXCURSION.model, data_for(EXCURSION))
    assert screens == default_screens(EXCURSION, EXCURSION.model, data_for(EXCURSION))
    assert [s.use_case for s in screens.screens] == use_cases(EXCURSION.model)
    record = data_for(EXCURSION).entity("Excursion")
    assert [f.attribute for f in screens.screen(CREATE).fields] == [a.name for a in record.attributes]
    assert codes(screens, EXCURSION) == []
    review = load_pack(ROOT / "packs" / "eija-review-slice")
    assert all(not s.fields for s in screens_for(review, review.model, None).screens)  # no data model, no fields


def test_authored_screens_load_beside_the_pack_and_pass():
    screens = screens_for(LOAN, LOAN.model, data_for(LOAN))
    assert screens == load_screens(ROOT / "packs" / "library-loan", "library-loan")
    assert screens.screen(CREATE).title == "Request a loan" and codes(screens) == []


def test_design_problems_have_stable_codes():
    screens = screens_for(LOAN, LOAN.model, data_for(LOAN))
    create = screens.screen(CREATE)
    assert codes(edited(screens, CREATE, fields=[f.model_dump() for f in create.fields[1:]])) == ["SCREEN_MISSING_REQUIRED"]
    assert codes(edited(screens, "Return", fields=[{"attribute": "colour"}])) == ["SCREEN_UNKNOWN_ATTRIBUTE"]
    assert codes(edited(screens, "Return", use_case="Renew")) == ["SCREEN_MISSING_USE_CASE", "SCREEN_UNKNOWN_USE_CASE"]
    assert codes(edited(screens, "Return", use_case="Cancel")) == ["SCREEN_DUPLICATE_USE_CASE", "SCREEN_MISSING_USE_CASE"]
    assert codes(edited(screens, CREATE, use_case="Return")) == ["SCREEN_DUPLICATE_USE_CASE", "SCREEN_MISSING_CREATE"]


def test_malformed_or_foreign_screens_are_refused():
    document = json.loads((ROOT / "packs" / "library-loan" / "screens.json").read_text(encoding="utf-8"))
    for change, code in ((lambda d: d | {"screens": []}, "SCREENS_INVALID"),
                         (lambda d: d | {"id": "excursion"}, "SCREENS_PACK_MISMATCH")):
        with pytest.raises(DomainError) as error:
            parse_screens(change(dict(document)), "library-loan")
        assert error.value.code == code
    twice = document["screens"][0] | {"fields": [{"attribute": "dueDate"}, {"attribute": "dueDate"}]}
    with pytest.raises(DomainError):
        parse_screens(document | {"screens": [twice]}, "library-loan")


def test_no_app_is_built_from_screens_with_design_problems():
    screens = screens_for(LOAN, LOAN.model, data_for(LOAN))
    broken = edited(screens, CREATE, fields=[])
    with pytest.raises(DomainError) as error:
        generate(LOAN, LOAN.model, data_for(LOAN), broken)
    assert error.value.code == "SCREENS_BLOCKED" and "SCREEN_MISSING_REQUIRED" in error.value.details["codes"]
    with pytest.raises(DomainError) as error:
        generate(LOAN, LOAN.model, data_for(LOAN), default_screens(EXCURSION, EXCURSION.model, data_for(EXCURSION)))
    assert error.value.code == "SCREENS_PACK_MISMATCH"


def test_screens_are_built_into_the_app_and_its_oracle():
    screens = screens_for(LOAN, LOAN.model, data_for(LOAN))
    files, manifest = generate(LOAN, LOAN.model, data_for(LOAN), screens)
    assert Screens.model_validate_json(files["app/screens.json"]) == screens
    assert json.loads(files["tests/oracle.json"])["screens_digest"] == screens.digest
    assert manifest["screens"] == {"digest": screens.digest, "count": len(screens.screens)}
    relabelled = edited(screens, CREATE, title="Borrow")
    _, other = generate(LOAN, LOAN.model, data_for(LOAN), relabelled)
    assert other["oracle"]["hash"] != manifest["oracle"]["hash"]  # other screens are another build


def test_every_action_gets_a_screen_and_a_missing_one_is_a_problem():
    screens = screens_for(LOAN, LOAN.model, data_for(LOAN))
    without = Screens(id=LOAN.id, screens=tuple(s for s in screens.screens if s.use_case != "Return"))
    assert codes(without) == ["SCREEN_MISSING_USE_CASE"]
    renamed = LOAN.model.model_copy(update={"transitions": tuple(
        t.model_copy(update={"action": "Renew"}) if t.action == "Return" else t for t in LOAN.model.transitions)})
    completed = screens_for(LOAN, renamed, data_for(LOAN))  # authored screens, plus a default one for the new action
    assert completed.screen("Renew").title == "Renew" and completed.screen(CREATE).title == "Request a loan"
    assert [p["code"] for p in check_screens(completed, renamed, data_for(LOAN))] == ["SCREEN_UNKNOWN_USE_CASE"]  # Return is gone


def test_an_action_named_create_is_its_own_use_case():
    named = EXCURSION.model.model_copy(update={"transitions": tuple(
        t.model_copy(update={"action": "create"}) if i == 0 else t for i, t in enumerate(EXCURSION.model.transitions))})
    screens = default_screens(EXCURSION, named, data_for(EXCURSION))
    assert screens.screen(CREATE) != screens.screen("create") and codes(screens, EXCURSION.model_copy(update={"model": named})) == []
