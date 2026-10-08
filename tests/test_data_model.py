"""Data models (ADR-0153): the class diagram's entities and attributes, and the one check record values go through."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from eija_studio.domain.data import DataModel, check_values, data_for, load_data, parse_data
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import load_pack

ROOT = Path(__file__).resolve().parents[1]


def loan():
    return load_data(ROOT / "packs" / "library-loan", "library-loan")


def refused(entity, values):
    with pytest.raises(DomainError) as error:
        check_values(entity, values)
    return error.value.code


def test_authored_data_models_load_beside_their_packs():
    assert data_for(load_pack(ROOT / "packs" / "excursion")).record == "Excursion"
    assert data_for(load_pack(ROOT / "packs" / "library-loan")).record == "Loan"
    assert data_for(load_pack(ROOT / "packs" / "eija-review-slice")) is None  # optional: no data.json, no data model


def test_record_values_are_checked_by_type():
    entity = loan().entity("Loan")
    valid = {"itemTitle": "Dune", "memberCard": "M-1", "dueDate": "2026-11-01", "format": "Book"}
    assert check_values(entity, valid | {"renewals": 2, "itemTitle": "Dune"}) == valid | {"renewals": 2}
    assert check_values(entity, valid | {"renewals": None}) == valid  # an empty optional value is simply absent
    assert refused(entity, {k: v for k, v in valid.items() if k != "dueDate"}) == "FIELD_REQUIRED"
    assert refused(entity, valid | {"itemTitle": ""}) == "FIELD_REQUIRED"
    assert refused(entity, valid | {"renewals": "two"}) == "FIELD_TYPE"
    assert refused(entity, valid | {"renewals": True}) == "FIELD_TYPE"  # a boolean is not a number
    assert refused(entity, valid | {"dueDate": "2026-02-30"}) == "FIELD_TYPE"
    assert refused(entity, valid | {"format": "Vinyl"}) == "FIELD_CHOICE"
    assert refused(entity, valid | {"memberCard": "x" * 21}) == "FIELD_TOO_LONG"
    assert refused(entity, valid | {"colour": "red"}) == "UNKNOWN_FIELD"


def test_incoherent_data_models_are_refused():
    document = json.loads((ROOT / "packs" / "library-loan" / "data.json").read_text(encoding="utf-8"))
    for change, code in ((lambda d: d | {"record": "Nothing"}, "DATA_INVALID"),
                         (lambda d: d | {"associations": [{"source": "Loan", "target": "Ghost"}]}, "DATA_INVALID"),
                         (lambda d: d | {"entities": d["entities"] + d["entities"][:1]}, "DATA_INVALID"),
                         (lambda d: d | {"id": "excursion"}, "DATA_PACK_MISMATCH")):
        with pytest.raises(DomainError) as error:
            parse_data(change(dict(document)), "library-loan")
        assert error.value.code == code
    bad_choice = {"name": "x", "type": "choice"}
    with pytest.raises(ValueError):
        DataModel.model_validate({"id": "a", "record": "A", "entities": [{"name": "A", "attributes": [bad_choice]}]})


def test_the_digest_changes_with_the_data_model():
    data = loan()
    renamed = DataModel.model_validate(data.model_dump() | {"record": "Item"})
    assert data.digest != renamed.digest and data.digest == loan().digest
