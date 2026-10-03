"""Immutable display projections of the deciding formal record, never new evidence or verdicts.

Raw JSON is retained as canonical text so inspecting a specimen cannot mutate a sealed artifact.
The adapters below read known artifact locations only; action labels never become navigation refs.
"""
from __future__ import annotations

from typing import Any, Callable, Literal

from pydantic import ValidationError

from eija_studio.domain.evidence import FormalVerdict, intact_artifact
from eija_studio.domain.formal import Context
from eija_studio.domain.models import Contract, Workflow, canonical, fingerprint
from eija_studio.domain.pack import Pack


class InspectionContext(Contract):
    """The case revision and review scope captured by the compiler, not inferred by a browser."""

    case_id: str
    case_version: int
    scope: str


class InspectionReview(Contract):
    """Full review identity; subject_json retains every subject field, including presentation."""

    case_id: str | None
    case_version: int | None
    scope: str | None
    subject_json: str
    subject_hash: str
    candidate_semantic_hash: str
    pack_id: str | None
    pack_digest: str | None


class InspectionReceipt(Contract):
    """Identity of the exact deciding intact receipt; its seal is deliberately not projected."""

    id: str | None
    subject_json: str
    artifact_hash: str | None
    producer: str | None
    method: str | None
    subject_matches_review: bool


class InspectionModel(Contract):
    """A supplied specimen, a validated projection of it, or an explicit absence of model data."""

    availability: Literal["valid_workflow", "raw_invalid", "not_provided"] = "not_provided"
    slot: str | None = None
    supplied_semantic_hash: str | None = None
    computed_semantic_hash: str | None = None
    raw_json: str | None = None
    workflow: Workflow | None = None
    validation_errors: tuple[str, ...] = ()


class InspectionStep(Contract):
    """An ordered literal recorded step. No action-name or execution inference is performed."""

    index: int
    raw_json: str
    text: str | None


class InspectionNavigation(Contract):
    """Current artifacts have no complete witness-reference contract, so no link is emitted."""

    current_model: None = None
    source: None = None
    reasons: tuple[str, ...] = ("EXPLICIT_REFERENCE_BINDING_NOT_PROVIDED",)


class InspectionRecord(Contract):
    """One exact JSON-pointer location within the deciding artifact, labelled by its known origin."""

    artifact_path: str
    origin: Literal["counterexample", "negative_control", "diagnostic"]
    label: str
    invariant: str | None
    raw_json: str
    steps: tuple[InspectionStep, ...] = ()
    model: InspectionModel = InspectionModel()
    navigation: InspectionNavigation = InspectionNavigation()


class WitnessInspection(Contract):
    """Supplemental record inspection; availability never changes the existing evidence status."""

    schema_version: Literal["eija.formal-inspection.v1"] = "eija.formal-inspection.v1"
    display_only: Literal[True] = True
    scope: Literal["formal-record-inspection"] = "formal-record-inspection"
    kind: str
    status: str
    reasons: tuple[str, ...]
    availability: Literal["available", "unavailable"]
    availability_reasons: tuple[str, ...]
    review: InspectionReview
    receipt: InspectionReceipt | None = None
    artifact_json: str | None = None
    records: tuple[InspectionRecord, ...] = ()
    record_count: int = 0
    projection_reasons: tuple[str, ...] = ()


def _text(value: Any) -> str | None:
    return value if type(value) is str else None


def _object(value: Any) -> dict[str, Any]:
    return value if type(value) is dict else {}


def _items(value: Any) -> list[Any]:
    return value if type(value) is list else []


def _rows(value: Any, path: str, notes: list[str]) -> list[Any]:
    if type(value) is not list:
        notes.append(f"UNPROJECTED_RECORDS: {path} is not a list; retained in artifact_json")
    return _items(value)


def _pointer(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _model(raw: Any = None, *, slot: str | None = None, supplied: Any = None) -> InspectionModel:
    supplied_hash = _text(supplied)
    if raw is None:
        return InspectionModel(slot=slot, supplied_semantic_hash=supplied_hash)
    try:
        workflow = Workflow.model_validate(raw)
    except ValidationError as error:
        errors = tuple(f"{'.'.join(str(p) for p in item['loc']) or '$'}: {item['msg']}"
                       for item in error.errors(include_input=False, include_context=False, include_url=False))
        return InspectionModel(availability="raw_invalid", raw_json=canonical(raw), validation_errors=errors,
                               slot=slot, supplied_semantic_hash=supplied_hash)
    return InspectionModel(availability="valid_workflow", raw_json=canonical(raw), workflow=workflow,
                           computed_semantic_hash=workflow.semantic_hash, slot=slot, supplied_semantic_hash=supplied_hash)


def _record(path: str, origin: Literal["counterexample", "negative_control", "diagnostic"], raw: Any,
            label: Any = None, invariant: Any = None, trace: Any = None,
            model: InspectionModel | None = None) -> InspectionRecord:
    steps = tuple(InspectionStep(index=i, raw_json=canonical(step), text=_text(step))
                  for i, step in enumerate(_items(trace)))
    return InspectionRecord(artifact_path=path, origin=origin, label=_text(label) or path,
                            invariant=_text(invariant), raw_json=canonical(raw), steps=steps,
                            model=model if model is not None else InspectionModel())


def _bmc(artifact: dict[str, Any], notes: list[str]) -> list[InspectionRecord]:
    found = []
    models = _object(artifact.get("models"))
    if type(artifact.get("counterexamples")) is not dict:
        notes.append("UNPROJECTED_RECORDS: /counterexamples is not an object; retained in artifact_json")
    for slot, values in sorted(_object(artifact.get("counterexamples")).items()):
        path = f"/counterexamples/{_pointer(slot)}"
        for index, raw in enumerate(_rows(values, path, notes)):
            row = _object(raw)
            if not _text(row.get("invariant")) or type(row.get("trace")) is not list:
                notes.append(f"MALFORMED_RECORDED_WITNESS: {path}/{index}; retained as a raw diagnostic")
                found.append(_record(f"{path}/{index}", "diagnostic", raw))
            else:
                found.append(_record(f"{path}/{index}", "counterexample", raw,
                                     row.get("invariant"), row.get("invariant"), row.get("trace"),
                                     _model(slot=slot, supplied=_object(models.get(slot)).get("semantic_hash"))))
    found.extend(_record(f"/mutation_self_test/{i}", "negative_control", raw, _object(raw).get("mutant"))
                 for i, raw in enumerate(_rows(artifact.get("mutation_self_test"), "/mutation_self_test", notes)))
    return found


def _smt_invariant(path: str, raw: Any, notes: list[str]) -> InspectionRecord | None:
    row = _object(raw)
    identifier, status = _text(row.get("id")), row.get("status")
    if not identifier or status not in ("proved", "refuted", "unknown"):
        notes.append(f"MALFORMED_INVARIANT_RECORD: {path}; retained as a raw diagnostic")
        return _record(path, "diagnostic", raw, identifier, identifier)
    if status == "proved":
        return None
    if status == "unknown":
        return _record(path, "diagnostic", raw, identifier, identifier)
    specimen = _object(row.get("counterexample")).get("candidate")
    if specimen is None:
        notes.append(f"RECORDED_SPECIMEN_UNAVAILABLE: {path}; refutation retained as a raw diagnostic")
        return _record(path, "diagnostic", raw, identifier, identifier)
    return _record(path, "counterexample", raw, identifier, identifier, model=_model(specimen))


def _smt(artifact: dict[str, Any], notes: list[str]) -> list[InspectionRecord]:
    found = []
    for index, raw in enumerate(_rows(artifact.get("invariants"), "/invariants", notes)):
        record = _smt_invariant(f"/invariants/{index}", raw, notes)
        if record is not None:
            found.append(record)
    controls = _object(artifact.get("negative_controls"))
    found.extend(_record(f"/negative_controls/named/{i}", "negative_control", raw,
                         _object(raw).get("remove"), _object(raw).get("expect_violation_of"))
                 for i, raw in enumerate(_rows(controls.get("named"), "/negative_controls/named", notes)))
    return found


def _bend(artifact: dict[str, Any], notes: list[str]) -> list[InspectionRecord]:
    found = [_record(f"/proof/laws/{i}", "diagnostic", raw, _object(raw).get("name"), _object(raw).get("name"))
             for i, raw in enumerate(_rows(_object(artifact.get("proof")).get("laws"), "/proof/laws", notes))
             if _object(raw).get("result") != "PROVEN"]
    for i, raw in enumerate(_rows(artifact.get("negative_controls"), "/negative_controls", notes)):
        row = _object(raw)
        # The positive proof's Baseline/Candidate hashes do not identify these seeded unsafe models.
        trace = _object(row.get("counterexample")).get("steps")
        found.append(_record(f"/negative_controls/{i}", "negative_control", raw, row.get("name"), trace=trace))
    return found


def _review_binding(subject: dict[str, Any], context: Context, pack: Pack | None,
                    captured: InspectionContext | None) -> InspectionReview:
    return InspectionReview(case_id=captured.case_id if captured else None,
                            case_version=captured.case_version if captured else None,
                            scope=captured.scope if captured else None,
                            subject_json=canonical(subject), subject_hash=fingerprint(subject),
                            candidate_semantic_hash=context.candidate_semantic,
                            pack_id=pack.id if pack else None, pack_digest=pack.digest if pack else None)


def _project_records(kind: str, artifact: dict[str, Any]) -> tuple[tuple[InspectionRecord, ...], tuple[str, ...]]:
    adapter = {"bounded_model_check": _bmc, "smt_proof": _smt, "bend_proof": _bend}.get(kind)
    notes: list[str] = []
    try:
        records = () if adapter is None else tuple(adapter(artifact, notes))
        if not records:
            notes.append("NO_STRUCTURED_RECORDS; inspect the retained artifact and verdict reasons")
        return records, tuple(notes)
    except (KeyError, TypeError, AttributeError, IndexError, ValueError, RecursionError):
        # Integrity does not guarantee the nested schema. Retain raw bytes and the existing verdict.
        return (), ("STRUCTURED_RECORD_PROJECTION_UNAVAILABLE; inspect the retained artifact and verdict reasons",)


def inspect_verdict(verdict: FormalVerdict, subject: dict[str, Any], context: Context,
                    authenticator: Callable[[dict[str, Any]], bool], pack: Pack | None,
                    review_context: InspectionContext | None = None) -> WitnessInspection:
    """Project only the deciding receipt, retaining uncertainty and all recorded raw data without writes."""
    review = _review_binding(subject, context, pack, review_context)
    unavailable = []
    if review_context is None or pack is None:
        unavailable.append("REVIEW_CONTEXT_UNAVAILABLE")
    receipt = verdict.receipt
    artifact = None if receipt is None else intact_artifact(receipt, verdict.kind, authenticator)
    if artifact is None:
        unavailable.append("NO_DECIDING_RECEIPT" if receipt is None else "INTACT_ARTIFACT_UNAVAILABLE")
    if unavailable or artifact is None or receipt is None:
        return WitnessInspection(availability="unavailable", availability_reasons=tuple(unavailable),
                                 kind=verdict.kind, status=verdict.status, reasons=verdict.reasons, review=review)
    binding = InspectionReceipt(id=_text(receipt.get("id")), subject_json=canonical(receipt.get("subject")),
                                artifact_hash=_text(receipt.get("artifact_hash")),
                                producer=_text(receipt.get("producer")), method=_text(receipt.get("method")),
                                subject_matches_review=receipt.get("subject") == subject)
    records, reasons = _project_records(verdict.kind, artifact)
    return WitnessInspection(availability="available", availability_reasons=(), receipt=binding,
                             artifact_json=canonical(artifact), records=records, record_count=len(records),
                             projection_reasons=reasons, kind=verdict.kind, status=verdict.status,
                             reasons=verdict.reasons, review=review)
