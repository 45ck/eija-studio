"""A bounded declared trace adapter, separate from policy and verification execution.

Requirement hashes use the same canonical row shape as Weave's csv-row-v1.
No prose is parsed into rules, no source links are inferred, and no evidence is minted.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from eija_studio.application.law_proof import compare_laws
from eija_studio.domain.laws import Law
from eija_studio.domain.models import DomainError, Workflow, fingerprint
from eija_studio.domain.pack import Pack

REQUIREMENT_PATH = "docs/verification/ACCEPTANCE_MATRIX.csv"


def compare_requirements(rows: list[dict[str, str]], drafts: Mapping[str, str]) -> list[dict[str, Any]]:
    """Compare prose only for existing IDs. Unknown IDs never introduce a new executable rule."""
    known = {row["id"] for row in rows}
    if set(drafts) - known:
        raise DomainError("REQUIREMENT_UNKNOWN", "Choose an existing acceptance requirement ID")
    changes = []
    for row in rows:
        before = row["observable_acceptance_criterion"]
        after = drafts.get(row["id"], before)
        if not isinstance(after, str) or not 1 <= len(after.strip()) <= 2000:
            raise DomainError("REQUIREMENT_DRAFT_INVALID", "Requirement prose must contain 1-2000 characters")
        after_row = row | {"observable_acceptance_criterion": after}
        changes.append({"id": row["id"], "before": before, "after": after,
                        "before_hash": fingerprint(row), "after_hash": fingerprint(after_row),
                        "hash_method": "csv-row-v1", "changed": before != after,
                        "status": "DRAFT_PROSE_ONLY" if before != after else "UNCHANGED",
                        "policy_changed": False})
    return changes


def _is_self_pack(pack: Pack, declarations: dict[str, Any]) -> bool:
    required_bindings = set(declarations.get("required_bindings", []))
    return bool(required_bindings) and {b for term in pack.language.terms for b in term.binds} >= required_bindings


def _changed_model_refs(baseline: Workflow, model: Workflow) -> set[str]:
    old_transitions = {"transition:" + t.id: fingerprint(t) for t in baseline.transitions}
    new_transitions = {"transition:" + t.id: fingerprint(t) for t in model.transitions}
    changed = {ref for ref in old_transitions.keys() | new_transitions.keys()
               if old_transitions.get(ref) != new_transitions.get(ref)}
    return changed | {"state:" + state for state in set(baseline.states) ^ set(model.states)}


def _source_links(declared: dict[str, Any], nodes: dict[str, Any], ref: str,
                  requirement_hash: str) -> list[dict[str, Any]]:
    links = []
    for kind in ("satisfies", "verifies"):
        for source in declared.get(kind, []):
            node = nodes.get(source)
            links.append({"kind": kind, "from": source, "to": ref, "class": "declared",
                          "resolved": node is not None, "source_hash": node.get("digest") if node else None,
                          "requirement_hash": requirement_hash, "evidence_status": "NOT_RUN",
                          "scope": "Declared relationship; resolution does not establish behaviour or a test result."})
    return links


def _law_links(pack: Pack, laws: dict[str, Law], declared: dict[str, Any], ref: str,
               requirement_hash: str) -> list[dict[str, Any]]:
    links = []
    for law_id in declared.get("laws", []):
        law = laws.get(law_id)
        links.append({"kind": "formalises", "from": f"repo://packs/{pack.id}/pack.json#law/{law_id}",
                      "ref": "law:" + law_id, "to": ref, "class": "declared",
                      "resolved": law is not None, "source_hash": fingerprint(law) if law else None,
                      "requirement_hash": requirement_hash, "evidence_status": "NOT_RUN",
                      "scope": "Reference-model law; fidelity to requirement prose is not automatically proved."})
    return links


def _unresolved_links(links: list[dict[str, Any]], model_links: list[dict[str, Any]]) -> list[str]:
    gaps = [link["from"] for link in links if not link["resolved"]]
    gaps += [item["ref"] for item in model_links if not item["resolved"]]
    if not links:
        gaps.append("No self-dogfood law, service or test link declared for this requirement.")
    return gaps


def _is_affected(change: dict[str, Any], declared: dict[str, Any], changed_laws: set[str],
                 changed_model_refs: set[str]) -> bool:
    return (change["changed"] or any(law in changed_laws for law in declared.get("laws", []))
            or any(ref in changed_model_refs for ref in declared.get("model", [])))


def _requirement_item(row: dict[str, str], change: dict[str, Any], ref: str,
                      declared: dict[str, Any], links: list[dict[str, Any]], model_refs: set[str],
                      affected: bool) -> dict[str, Any]:
    model_links = [{"ref": item, "resolved": item in model_refs} for item in declared.get("model", [])]
    return {**change, "area": row["area"], "reference": ref,
            "required_evidence": row["required_evidence"],
            "historical_status": row["v0_2_status"], "historical_scope": row["v0_2_scope_note"],
            "observed_status": "NOT_RUN", "links": links, "model_links": model_links,
            "unresolved": _unresolved_links(links, model_links), "affected": affected,
            "affected_checks": declared.get("verifies", []) if affected else [],
            "review_required": "Declared links need review against changed prose/law subjects." if affected else None}


def _requirement_items(pack: Pack, model: Workflow, baseline: Workflow, rows: list[dict[str, str]],
                       changes: list[dict[str, Any]], declarations: dict[str, Any], nodes: dict[str, Any],
                       is_self: bool, changed_laws: set[str], laws: dict[str, Law]) -> list[dict[str, Any]]:
    model_refs = {"state:" + s for s in model.states} | {"transition:" + t.id for t in model.transitions}
    changed_model_refs = _changed_model_refs(baseline, model)
    requirements = []
    for row, change in zip(rows, changes, strict=True):
        ref = "repo://" + REQUIREMENT_PATH + "#" + row["id"]
        declared = declarations.get("links", {}).get(row["id"], {}) if is_self else {}
        links = _source_links(declared, nodes, ref, change["before_hash"])
        links += _law_links(pack, laws, declared, ref, change["before_hash"])
        affected = _is_affected(change, declared, changed_laws, changed_model_refs)
        requirements.append(_requirement_item(row, change, ref, declared, links, model_refs, affected))
    return requirements


def _law_change_status(before: dict[str, Any] | None, after: dict[str, Any] | None,
                       changed_fields: list[str]) -> str:
    if before is None:
        return "added"
    if after is None:
        return "removed"
    return "changed" if changed_fields else "unchanged"


def _law_change(law_id: str, before: dict[str, Any] | None, after: dict[str, Any] | None) -> dict[str, Any]:
    before_fields, after_fields = before or {}, after or {}
    changed_fields = sorted(k for k in (set(before_fields) | set(after_fields))
                            if before_fields.get(k) != after_fields.get(k))
    return {"id": law_id, "before": before, "after": after, "fields": changed_fields,
            "description_changed": "description" in changed_fields,
            "draft_policy_fields": [field for field in changed_fields if field != "description"],
            "status": _law_change_status(before, after, changed_fields),
            "before_hash": fingerprint(before) if before else None, "after_hash": fingerprint(after) if after else None,
            "activation": "DRAFT_ONLY" if before != after else "UNCHANGED"}


def _law_changes(old_laws: dict[str, Law], laws: dict[str, Law]) -> list[dict[str, Any]]:
    law_changes = []
    for law_id in sorted(set(old_laws) | set(laws)):
        before = old_laws[law_id].model_dump(mode="json", exclude_none=True) if law_id in old_laws else None
        after = laws[law_id].model_dump(mode="json", exclude_none=True) if law_id in laws else None
        law_changes.append(_law_change(law_id, before, after))
    return law_changes


def _terms(pack: Pack) -> list[dict[str, Any]]:
    return [{"id": term.id, "label": term.label, "definition": term.definition,
             "hash": fingerprint(term.model_dump(mode="json") | {"binds": sorted(term.binds), "refs": sorted(term.refs)}),
             "model_refs": list(term.refs), "source_refs": list(term.binds), "status": "DECLARED"}
            for term in pack.language.terms]


def _coverage(requirements: list[dict[str, Any]], is_self: bool) -> dict[str, Any]:
    return {"status": "DECLARED_PARTIAL" if is_self else "UNBOUND",
            "requirements": len(requirements), "linked": sum(bool(r["links"]) for r in requirements),
            "resolved_links": sum(link["resolved"] for r in requirements for link in r["links"]),
            "scope": "Explicit pack-declared acceptance relations only; no completeness or current test-pass claim."}


def requirement_review(pack: Pack, model: Workflow, snapshot: dict[str, Any], *,
                       connection: dict[str, Any] | None = None, drafts: Mapping[str, str] | None = None,
                       candidate_pack: Pack | None = None, baseline: Workflow | None = None) -> dict[str, Any]:
    """Pinned requirement rows and declared model/law/source/test links with visible gaps."""
    candidate_pack = candidate_pack or pack
    baseline = baseline or pack.model
    changes = compare_requirements(snapshot["rows"], drafts or {})
    connection = connection or {}
    nodes = {node["id"]: node for node in connection.get("nodes", [])}
    declarations = snapshot.get("traceability", {})
    is_self = _is_self_pack(pack, declarations)
    laws = {law.id: law for law in candidate_pack.laws}
    old_laws = {law.id: law for law in pack.laws}
    law_diff = compare_laws(pack, candidate_pack)
    changed_laws = {law for values in law_diff.values() for law in values}
    requirements = _requirement_items(pack, model, baseline, snapshot["rows"], changes,
                                     declarations, nodes, is_self, changed_laws, laws)
    return {"schema": "eija.requirement-review.v1", "provenance": snapshot["provenance"],
            "subject": {"pack_id": pack.id, "pack_digest": pack.digest, "model_hash": model.semantic_hash,
                        "baseline_model_hash": baseline.semantic_hash,
                        "candidate_pack_digest": candidate_pack.digest,
                        "source_hash": connection.get("source_hash"),
                        "traceability_declarations_hash": fingerprint(declarations),
                        "requirement_rows_hash": fingerprint(snapshot["rows"])},
            "coverage": _coverage(requirements, is_self),
            "requirements": requirements, "laws": {"summary": law_diff, "items": _law_changes(old_laws, laws)},
            "terms": _terms(pack),
            "limits": ["The acceptance snapshot is historical requirement text; status columns are not current run results.",
                       "Requirement prose drafts never change policy or become active.",
                       "Law changes are draft-only; review fidelity and run the existing law checker separately.",
                       "Source resolution is structural; implementation behaviour needs retained service checks."]}
