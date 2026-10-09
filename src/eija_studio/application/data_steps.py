"""Data-model steps in a chat plan (ADR-0202): add an attribute to a class, remove one, or make one required or optional.

A system started in PlayIDE has a class diagram (`data.json`, ADR-0153) whose record class is the built app's form.
Building such a system in chat (ADR-0201) also means growing that form, so a plan step may change the data model as
well as the state machine. These steps are not kernel transactions: the data model is not governed by the policy or
the laws, and has its own contract (`domain.data.DataModel`), which checks every result here. A step changes a draft
held in memory (`domain.pack.hold`); nothing is written, and a shipped pack's data model stays its owner's.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Annotated, Any, Literal, Union

from pydantic import Field, ValidationError

from eija_studio.domain.data import ATTRIBUTE_NAME, DATA_FILE, NAME, Attribute, DataModel, Entity, data_for, parse_data
from eija_studio.domain.models import Contract, DomainError
from eija_studio.domain.pack import Pack, hold
from eija_studio.domain.transactions import Transaction, parse_transaction

from .new_system import declare


class AddAttribute(Contract):
    kind: Literal["add_attribute"]
    entity: str = Field(pattern=NAME)
    attribute: Attribute


class RemoveAttribute(Contract):
    kind: Literal["remove_attribute"]
    entity: str = Field(pattern=NAME)
    name: str = Field(pattern=ATTRIBUTE_NAME)


class SetRequired(Contract):
    kind: Literal["set_required"]
    entity: str = Field(pattern=NAME)
    name: str = Field(pattern=ATTRIBUTE_NAME)
    required: bool


DataStep = Annotated[Union[AddAttribute, RemoveAttribute, SetRequired], Field(discriminator="kind")]  # noqa: UP007
DATA_STEP_KINDS = ("add_attribute", "remove_attribute", "set_required")
DataEdit = AddAttribute | RemoveAttribute | SetRequired
Step = Transaction | DataEdit
FIXED = "This system's data model is its owner's: chat changes the class diagram only on a system you started"


class _StepDocument(Contract):
    step: DataStep


def parse_step(data: Any) -> Step:
    """A plan step: a data-model step, or else a kernel transaction (`parse_transaction`). Malformed is `EDIT_INVALID`."""
    if not isinstance(data, dict) or data.get("kind") not in DATA_STEP_KINDS:
        return parse_transaction(data)
    try:
        return _StepDocument.model_validate({"step": data}).step
    except ValidationError:
        raise DomainError("EDIT_INVALID", "Data-model step fields are invalid", details={"codes": ["EDIT_INVALID"], "refs": []}) from None


DATA_EDITS = (AddAttribute, RemoveAttribute, SetRequired)


def is_data(step: Step) -> bool:
    return isinstance(step, DATA_EDITS)


def split(steps: Sequence[Step]) -> tuple[list[Transaction], list[DataEdit]]:
    """The kernel transactions and the data-model steps, each in plan order."""
    transactions: list[Transaction] = []
    edits: list[DataEdit] = []
    for step in steps:
        if isinstance(step, DATA_EDITS):
            edits.append(step)
        else:
            transactions.append(step)
    return transactions, edits


def _refused(code: str, message: str, ref: str) -> DomainError:
    return DomainError(code, message, details={"codes": [code], "refs": [ref]})


def _entity(document: dict[str, Any], name: str) -> dict[str, Any]:
    found: dict[str, Any] | None = next((e for e in document["entities"] if e["name"] == name), None)
    if found is None:
        raise _refused("EDIT_INVALID", f"The class diagram has no class {name}", "class:" + name)
    return found


def _attribute(entity: dict[str, Any], name: str) -> dict[str, Any]:
    found: dict[str, Any] | None = next((a for a in entity["attributes"] if a["name"] == name), None)
    if found is None:
        raise _refused("EDIT_INVALID", f"{entity['name']} has no attribute {name}", f"attribute:{entity['name']}.{name}")
    return found


def _apply(document: dict[str, Any], step: DataEdit) -> None:
    entity = _entity(document, step.entity)
    if isinstance(step, AddAttribute):
        if any(a["name"].casefold() == step.attribute.name.casefold() for a in entity["attributes"]):
            raise _refused("EDIT_INVALID", f"{step.entity} already has an attribute {step.attribute.name}",
                           f"attribute:{step.entity}.{step.attribute.name}")
        entity["attributes"].append(step.attribute.model_dump(mode="json"))
    elif isinstance(step, RemoveAttribute):
        entity["attributes"].remove(_attribute(entity, step.name))
    elif isinstance(step, SetRequired):
        _attribute(entity, step.name)["required"] = step.required


def apply_data(data: DataModel | None, steps: Sequence[DataEdit]) -> DataModel | None:
    """`data` with the data-model steps applied in turn, checked by the data model's own contract; `data` when none."""
    if not steps:
        return data
    if data is None:
        raise _refused("EDIT_INVALID", "This system has no class diagram (data.json) to change", "class:")
    document = data.model_dump(mode="json")
    for step in steps:
        _apply(document, step)
    try:
        return parse_data(document, data.id)
    except DomainError as error:
        raise DomainError("EDIT_INVALID", error.message, details={"codes": ["EDIT_INVALID"], "refs": []}) from None


def draft_pack(pack: Pack, steps: Sequence[Step], grows: bool) -> Pack:
    """`pack` as these plan steps would have it, held in memory: on a system the person started (`grows`), the actions
    and roles they name are declared (ADR-0201) and the data model holds their data-model steps (ADR-0202). A shipped
    pack is itself, and a data-model step on it is refused."""
    transactions, data_steps = split(steps)
    if data_steps and not grows:
        raise DomainError("PLAN_DATA_FIXED", FIXED, details={"codes": ["PLAN_DATA_FIXED"], "refs": []})
    if not grows:
        return pack
    working = declare(pack, transactions)
    return hold(working, DATA_FILE, apply_data(data_for(pack), data_steps)) if data_steps else working


def _type(a: dict[str, Any]) -> str:
    return f"one of {', '.join(a['choices'])}" if a["type"] == "choice" else a["type"]


def describe_data(step: DataEdit) -> str:
    """One line a person can check against the class diagram."""
    if isinstance(step, AddAttribute):
        a = step.attribute.model_dump(mode="json")
        return f"Add attribute {a['name']}: {_type(a)} to {step.entity}" + (", required" if a["required"] else "")
    if isinstance(step, RemoveAttribute):
        return f"Remove attribute {step.name} from {step.entity}"
    return f"Make {step.entity}.{step.name} {'required' if step.required else 'optional'}"


def data_changes(before: DataModel | None, after: DataModel | None) -> list[str]:
    """What changed on the class diagram, in words: attributes gained and lost, and required ones made optional or back."""
    if before is None or after is None or before.digest == after.digest:
        return []
    known = {e.name for e in before.entities}
    return [text for entity in after.entities
            for text in _entity_changes(entity, before.entity(entity.name) if entity.name in known else None)]


def _entity_changes(entity: Entity, was: Entity | None) -> list[str]:
    old = {a.name: a for a in was.attributes} if was is not None else {}
    new = {a.name: a for a in entity.attributes}
    gained = [f"{entity.name} gains {n}" for n in new if n not in old]
    lost = [f"{entity.name} loses {n}" for n in old if n not in new]
    return gained + lost + _required_changes(entity.name, old, new)


def _required_changes(name: str, old: dict[str, Attribute], new: dict[str, Attribute]) -> list[str]:
    both = [n for n in new if n in old and new[n].required != old[n].required]
    return [f"{name}.{n} is now {'required' if new[n].required else 'optional'}" for n in both]
