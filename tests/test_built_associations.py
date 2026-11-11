"""Built associations (issue #145, ADR-0235).

An association from the record class to at most one object of another class can be marked `built`. The built app then
holds a reference field named by the association's role, stores objects of the other class, and refuses a record whose
reference names no stored object. Nothing else changes: an association that is not built is left out of every dump, so
every shipped data model, digest and oracle keeps its bytes.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from eija_studio.application.interop import FORMATS, export_model, import_model
from eija_studio.application.appgen import data_cases, generate, stock
from eija_studio.application.class_build import class_build
from eija_studio.domain.data import MAX_RECORD_FIELDS, DataModel, check_record, record_fields, references
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import load_pack
from eija_studio.interfaces.app_build import conformance
from eija_studio.interfaces.cli import main

ROOT = Path(__file__).resolve().parents[1]
LOAN_DIR = ROOT / "packs" / "library-loan"
LOAN = load_pack(LOAN_DIR)
DOC = json.loads((LOAN_DIR / "data.json").read_text(encoding="utf-8"))
BORROWER = 2  # Loan 0..* to 1 Member, role "borrower"


def _built(*indexes: int, **change) -> DataModel:
    doc = json.loads(json.dumps(DOC))
    for n in indexes:
        doc["associations"][n] |= {"built": True} | change
    return DataModel.model_validate(doc)


def test_nothing_built_keeps_every_byte():
    plain = DataModel.model_validate(DOC)
    assert "built" not in json.dumps(plain.model_dump(mode="json"))
    assert references(plain) == [] and record_fields(plain) == plain.entity("Loan").attributes
    files, _ = generate(LOAN, LOAN.model, plain)
    assert "objects" not in json.loads(files["tests/oracle.json"])
    assert _built(BORROWER).digest != plain.digest


def test_a_built_association_is_a_reference_field():
    data = _built(BORROWER)
    [ref] = references(data)
    assert (ref.name, ref.target, ref.required) == ("borrower", "Member", True)
    assert record_fields(data)[-1].name == "borrower"
    assert references(_built(BORROWER, target_multiplicity="0..1"))[0].required is False


@pytest.mark.parametrize("change", [{"target_multiplicity": "0..*"}, {"role": ""}, {"role": "memberCard"}, {"role": "Bad"}])
def test_only_a_to_one_association_with_a_free_role_can_be_built(change):
    with pytest.raises(ValueError):
        _built(BORROWER, **change)


def test_an_association_between_two_other_classes_cannot_be_built():
    with pytest.raises(ValueError):
        _built(0)  # Item to Copy: the record class is neither end


def test_attributes_and_references_together_fit_one_screen():
    doc = json.loads(json.dumps(DOC))
    loan = next(e for e in doc["entities"] if e["name"] == "Loan")
    loan["attributes"] += [{"name": f"extra{n}", "type": "text"} for n in range(MAX_RECORD_FIELDS - len(loan["attributes"]))]
    DataModel.model_validate(doc)  # 40 attributes and nothing built
    doc["associations"][BORROWER]["built"] = True
    with pytest.raises(ValueError, match="at most 40 fields"):
        DataModel.model_validate(doc)


@pytest.mark.parametrize("fmt", FORMATS)
def test_uml_files_say_built_is_not_carried_and_an_unchanged_link_stays_built(fmt):
    data = _built(BORROWER)
    text, exported = export_model(fmt, LOAN, None, data)
    assert any("reference fields" in item for item in exported["not_carried"])
    back = import_model(fmt, text, LOAN, None, data)
    assert back["class_model"]["candidate"] == data.model_dump(mode="json")
    assert "Loan -> Member" in json.dumps(back["defaulted"])


def test_check_record_refuses_a_reference_to_nothing():
    data = _built(BORROWER)
    valid = data_cases(LOAN, data, LOAN.model)[0]["fields"]
    stored = {("Member", valid["borrower"])}
    assert check_record(data, valid, lambda c, i: (c, i) in stored)["borrower"] == valid["borrower"]
    for broken, code in [({"borrower": "nobody"}, "REFERENCE_UNKNOWN"), ({"borrower": 7}, "FIELD_TYPE"),
                         ({"borrower": ""}, "FIELD_REQUIRED")]:
        with pytest.raises(DomainError) as e:
            check_record(data, valid | broken, lambda c, i: (c, i) in stored)
        assert e.value.code == code


def test_the_oracle_stores_objects_and_tries_each_wrong_reference():
    data = _built(BORROWER)
    files, _ = generate(LOAN, LOAN.model, data)
    oracle = json.loads(files["tests/oracle.json"])
    assert oracle["objects"] == stock(data) and [o["class"] for o in stock(data)] == ["Member"]
    answers = {c["name"]: c["expect"] for c in oracle["data_cases"]}
    assert answers["valid"]["outcome"] == "CREATED"
    assert answers["borrower unknown"] == {"outcome": "REFUSED", "code": "REFERENCE_UNKNOWN"}
    assert answers["borrower missing"] == {"outcome": "REFUSED", "code": "FIELD_REQUIRED"}


def test_the_class_build_report_says_what_is_built():
    report = class_build(_built(BORROWER))
    assert report["built"] == ["Loan", "Member"] and report["drawn_only"] == ["Copy", "Item"]
    assert report["associations"][BORROWER]["built"] and "is built" in report["associations"][BORROWER]["message"]
    assert not report["associations"][1]["built"]


def _built_pack(tmp_path: Path) -> Path:
    pack_dir = tmp_path / "library-loan"
    shutil.copytree(LOAN_DIR, pack_dir)
    (pack_dir / "screens.json").unlink()  # the shipped screens predate the reference field; use the default ones
    doc = json.loads(json.dumps(DOC))
    doc["associations"][BORROWER]["built"] = True
    (pack_dir / "data.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8", newline="\n")
    return pack_dir


def test_a_built_app_checks_references_and_conformance_catches_an_app_that_does_not(tmp_path):
    pack_dir, out = _built_pack(tmp_path), tmp_path / "app"
    assert main(["build", "--pack", str(pack_dir), "--out", str(out)]) == 0
    manifest = json.loads((out / "BUILD.json").read_text(encoding="utf-8"))
    assert manifest["conformance"]["status"] == "PASS", manifest["conformance"]
    service = out / "app" / "service.py"
    text = service.read_text(encoding="utf-8")
    marker = 'return self.db.execute("SELECT 1 FROM objects WHERE class=? AND id=?", (cls, object_id)).fetchone() is not None'
    assert marker in text
    service.write_text(text.replace(marker, "return True"), encoding="utf-8")
    assert conformance(out)["status"] == "FAIL"  # negative control: an app that believes every id
