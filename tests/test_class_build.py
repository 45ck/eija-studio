"""What the built app does with the class diagram (#145, ADR-0205): only the record class is built, so the other classes
and every association are reported as drawn, not built, and a record attribute standing in for an association is a
"to consider". Each check has a negative case."""
from __future__ import annotations

from eija_studio.application.class_build import class_build
from eija_studio.application.ripple import _build_items
from eija_studio.domain.data import DataModel, data_for
from eija_studio.domain.pack import PACKS_ROOT, load_pack


def loan() -> DataModel:
    data = data_for(load_pack(PACKS_ROOT / "library-loan"))
    assert data is not None
    return data


def edited(data: DataModel, **attributes: str) -> DataModel:
    """The loan class diagram with the record's attributes renamed, as an edit of `data.json` would leave it."""
    document = data.model_dump(mode="json")
    record = next(e for e in document["entities"] if e["name"] == data.record)
    for attribute in record["attributes"]:
        attribute["name"] = attributes.get(attribute["name"], attribute["name"])
    return DataModel.model_validate(document)


def test_only_the_record_class_is_built_and_every_association_is_drawn_only():
    report = class_build(loan())
    assert report["built"] == ["Loan"] and report["drawn_only"] == ["Copy", "Item", "Member"]
    assert [(a["source"], a["target"]) for a in report["associations"]] == [("Item", "Copy"), ("Loan", "Copy"), ("Loan", "Member")]
    assert all("drawn, not built" in a["message"] for a in report["associations"]) and "#65" in report["limits"][0]


def test_a_record_attribute_named_after_an_associated_class_stands_in_for_the_association():
    [finding] = class_build(loan())["findings"]
    assert finding["code"] == "ATTRIBUTE_STANDS_IN_FOR_ASSOCIATION" and finding["severity"] == "consider"
    assert finding["subject"] == ["class:Loan", "attribute:Loan.memberCard", "assoc:2"]
    assert "not that such a Member exists" in finding["message"]


def test_a_role_name_counts_and_an_unrelated_attribute_does_not():
    assert [f["subject"][1] for f in class_build(edited(loan(), memberCard="borrowerId"))["findings"]] == ["attribute:Loan.borrowerId"]
    # itemTitle names Item, but Loan is not associated with Item (only through Copy), so it stands in for nothing.
    assert class_build(edited(loan(), memberCard="cardNumber"))["findings"] == []


def test_a_change_that_makes_an_attribute_stand_in_is_a_to_consider_in_the_ripple():
    before, after = edited(loan(), memberCard="cardNumber"), loan()
    [item] = _build_items(before, after)
    assert item["change"] == "changed" and item["text"].startswith("To consider: Loan.memberCard")
    assert item["ref"] == "class:Loan" and item["code"] == "ATTRIBUTE_STANDS_IN_FOR_ASSOCIATION"
    assert _build_items(after, after) == [] and _build_items(None, after) == []
