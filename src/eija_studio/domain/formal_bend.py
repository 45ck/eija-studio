"""Admissibility of ``bend_proof`` receipts (ADR-0146; lane bend, ADR-0025 and ADR-0026).

Recomputed here from the raw artifact: every required law is PROVEN by the full ``--verdict`` run, every
seeded-unsafe model makes exactly the laws it was seeded to break fail (the kernel pins that expectation,
it does not read the artifact's own), each unsafe model has a confirmed concrete counterexample, the model
was checked against the runtime by a conformance test above a declared minimum, and the model that was
proved is the model of the CURRENT baseline and candidate.

Accepted under the sealed local producer, not recomputed: that Bend's kernel really answered ``PROVEN``
(no proof certificate leaves the container), and the observed current bytes of the model files.
"""
from __future__ import annotations

from typing import Any

from .formal import (
    LEVEL_SEALED_TOOL, Assessment, Context, Findings, KindSpec, as_records, carried_statements, exact_keys, reported_labels, field,
    has_items, records, strings, text,
)

PROTOCOL = "eija.formal.bend-proof/v1"
KEYS = frozenset({"protocol", "tool", "mode", "model", "binding", "proof", "negative_controls", "conformance",
                  "assumptions", "limitations", "reported", "source"})

ACCEPTED_BEND_VERSIONS = ("2.0.32",)
LAWS = ("teacher_never_approves", "teacher_sequences_never_approve", "approved_only_from_recommended",
        "every_path_to_approved_passes_recommended", "revoked_teacher_cannot_recommend",
        "unassigned_teacher_cannot_recommend", "reject_only_from_declared_source", "forbidden_effects_never_emitted")
# name -> (the laws the seeded fault must break and no others, how the fault is confirmed concretely)
CONTROLS: dict[str, tuple[frozenset[str], tuple[str, str]]] = {
    "teacher_final_approval": (frozenset({"teacher_never_approves", "teacher_sequences_never_approve"}), ("state", "Approved")),
    "approve_skips_recommendation": (frozenset({"approved_only_from_recommended", "every_path_to_approved_passes_recommended"}),
                                     ("state", "Approved")),
    "unassigned_may_recommend": (frozenset({"unassigned_teacher_cannot_recommend"}), ("state", "Recommended")),
    "reject_from_draft": (frozenset({"reject_only_from_declared_source"}), ("state", "Rejected")),
    "payment_effect_emitted": (frozenset({"forbidden_effects_never_emitted"}), ("effect", "PaymentCaptured")),
    "engine_ignores_revocation": (frozenset({"revoked_teacher_cannot_recommend"}), ("state", "Recommended")),
}
MODEL_FILES = ("main.bend", "LAWS.bend", "PROOF.bend", "bend_generate.py")
MIN_CONFORMANCE_CELLS = 225  # 5 fixture actors x (4 baseline + 5 candidate) states x 5 actions

ESTABLISHES = ("For the Bend model generated from the current baseline and candidate workflows, eight authority laws hold for "
               "all actors, all states and all command sequences, and the proofs fail on six seeded-unsafe models.")
DOES_NOT_ESTABLISH = (
    "Anything about the Python runtime, its SQLite adapter or the HTTP layer: the laws are about the generated model.",
    "That the model equals the runtime: conformance is a bounded differential test, not a proof.",
    "That no other fault escapes the proofs: the negative controls are a fixed set of seeded faults.",
    "That the laws are the right laws: same authors as the model, not an independently blinded specification.",
)
PREREQUISITES = "Docker with the pinned eija-bend-checker image (verification/bend/bend_runner.py); NOT_RUN otherwise."


def _tool(a: dict[str, Any], f: Findings) -> None:
    tool = field(a, "tool", dict, "artifact")
    if text(tool, "bend_version", "tool") not in ACCEPTED_BEND_VERSIONS:
        f.unknown(f"Bend {tool['bend_version']} is not a version this kernel accepts {list(ACCEPTED_BEND_VERSIONS)}")
    for key in ("bend_commit", "image_id", "lean_version"):
        text(tool, key, "tool")
    if "@sha256:" not in text(tool, "base_image", "tool"):
        f.unknown("the checker's base image is not pinned by digest")


def _mode(a: dict[str, Any], f: Findings) -> None:
    if text(a, "mode", "artifact") != "complete":
        f.unknown(f"mode {a['mode']!r}: per-law attribution and the controls were not all run (partial evidence)")


def _binding(a: dict[str, Any], ctx: Context, f: Findings) -> None:
    model = field(a, "model", dict, "artifact")
    slots, files = field(model, "semantic_hash", dict, "model"), field(model, "files", dict, "model")
    if slots.get("Candidate") != ctx.candidate_semantic:
        f.stale("the proved Candidate model is not the candidate under review (semantic hash differs)")
    if ctx.baseline_semantic is None:
        f.unknown("the baseline hash was not supplied, so the Baseline slot cannot be bound")
    elif slots.get("Baseline") != ctx.baseline_semantic:
        f.stale("the proved Baseline model is not the baseline of this case (semantic hash differs)")
    binding = field(a, "binding", dict, "artifact")
    current = field(binding, "current_files_sha256", dict, "binding")
    for name in MODEL_FILES:
        if current.get(name) is None:
            f.unknown(f"{name}: the current file could not be observed")
        elif files.get(name) != current[name]:
            f.stale(f"{name} changed after the proof ran")
    regenerated = binding.get("regenerated_main_bend_sha256")
    if regenerated is None:
        f.unknown("the model could not be regenerated from the current workflows, so the proved text is not confirmed")
    elif regenerated != files.get("main.bend"):
        f.stale("regenerating the model from the current workflows gives different text than the one proved")


def _laws(proof: dict[str, Any], f: Findings) -> None:
    listed = records(proof, "laws", "proof")
    results = {text(x, "name", "law"): text(x, "result", "law") for x in listed}
    if len(results) != len(listed):
        f.fail("a law is listed twice")
    for law in LAWS:
        if law not in results:
            f.unknown(f"law {law} is not covered by the receipt")
    for law, result in sorted(results.items()):
        if result != "PROVEN":
            f.fail(f"law {law}: {result}")


def _proof(a: dict[str, Any], f: Findings) -> None:
    proof = field(a, "proof", dict, "artifact")
    if "--verdict" not in text(proof, "command", "proof"):
        f.unknown("the proof was not rechecked by Bend's proof kernel (--verdict)")
    for part in ("model_check", "full_run"):
        result = text(field(proof, part, dict, "proof"), "result", part)
        if result != "PROVEN":
            f.fail(f"{part}: {result}")
    _laws(proof, f)
    if has_items(proof, "laws_without_proof", "proof"):
        f.unknown("a law has no proof")


def _control_problem(c: dict[str, Any], expected: frozenset[str], witness: tuple[str, str]) -> str | None:
    if c.get("model_well_formed") is not True:
        return "the unsafe model was not a well-formed model, so its failure shows nothing"
    if field(c, "full_run", dict, "control").get("result") != "FAILED":
        return "the proofs did not fail on the unsafe model (the proof is insensitive to this fault)"
    failing, passing = set(strings(c, "failing_laws", "control", 0)), set(strings(c, "passing_laws", "control", 0))
    if failing != expected or passing != set(LAWS) - expected:
        return f"the laws that failed {sorted(failing)} are not exactly the ones seeded to fail {sorted(expected)}"
    return _witness_problem(c, *witness)


def _witness_problem(c: dict[str, Any], how: str, want: str) -> str | None:
    if how == "effect":
        probe = field(c, "effect_probe", dict, "control")
        return None if want in strings(probe, "emitted", "effect_probe") else f"the unsafe model was not seen emitting {want}"
    example = field(c, "counterexample", dict, "control")
    reached = (example.get("final_state_in_unsafe_model"), example.get("final_state_expected_by_fault"))
    if example.get("confirmed") is not True or reached != (want, want) or not example.get("steps"):
        return f"no confirmed concrete trace reaching {want} in the unsafe model"
    return None


def _controls(a: dict[str, Any], f: Findings) -> None:
    by_name = {text(c, "name", "control"): c for c in records(a, "negative_controls", "artifact")}
    for name, (expected, witness) in CONTROLS.items():
        if name not in by_name:
            f.unknown(f"negative control {name} is missing: the proof's sensitivity to that fault is not shown")
            continue
        problem = _control_problem(by_name[name], expected, witness)
        if problem:
            f.fail(f"negative control {name}: {problem}")


def _conformance(a: dict[str, Any], f: Findings) -> None:
    conf = field(a, "conformance", dict, "artifact")
    matrix = field(conf, "matrix", dict, "conformance")
    cells, agree = field(matrix, "cells", int, "matrix"), field(matrix, "agree", int, "matrix")
    if cells < MIN_CONFORMANCE_CELLS:
        f.unknown(f"conformance covered {cells} runtime cells, fewer than the declared minimum {MIN_CONFORMANCE_CELLS}")
    if agree != cells or has_items(matrix, "mismatches", "matrix") or has_items(matrix, "unmatched_cells", "matrix"):
        f.fail(f"the Bend model disagrees with the runtime ({agree} of {cells} cells agree)")
    witnesses = records(conf, "witnesses", "conformance")
    if not witnesses:
        f.unknown("no witness traces were compared with the runtime")
    for w in witnesses:
        if not (text(w, "bend_final_state", "witness") == w.get("python_final_state") == w.get("expected_final_state")):
            f.fail(f"witness {w.get('name')!r}: Bend, Python and the expectation disagree")


def check(a: dict[str, Any], ctx: Context) -> Assessment:
    exact_keys(a, KEYS)
    carried_statements(a)
    text(field(a, "source", dict, "artifact"), "origin", "source")
    f = Findings()
    reported_labels(a, f)
    _tool(a, f)
    _mode(a, f)
    _binding(a, ctx, f)
    _proof(a, f)
    _controls(a, f)
    _conformance(a, f)
    return f.result()


def describe(a: dict[str, Any]) -> dict[str, Any]:
    tool = a["tool"]
    return {"tool": {"name": "bend", "version": tool["bend_version"], "image": tool["image_id"]},
            "bounds": {"mode": a["mode"], "models": ["Baseline", "Candidate"], "laws": len(a["proof"]["laws"]),
                       "quantification": "all actors, states and command sequences of the generated model",
                       "conformance_cells": a["conformance"]["matrix"]["cells"]},
            "assumptions": list(a["assumptions"]), "limitations": list(a["limitations"]),
            "negative_controls": [{"name": c["name"], "failing_laws": list(c["failing_laws"])} for c in a["negative_controls"]],
            "counterexamples": []}


def explain(a: dict[str, Any], policy_errors: tuple[str, ...]) -> list[dict[str, Any]]:
    """Negative-control counterexamples whose fault class is one the kernel's own policy reports.

    Display only: a seeded unsafe model with the same fault, not a proof about the candidate."""
    found = []
    for c in as_records(a.get("negative_controls")):
        codes = [x for x in c.get("kernel_policy_findings") or [] if x in policy_errors]
        raw = c.get("counterexample")
        example: dict[str, Any] = raw if type(raw) is dict else {}
        if codes and example.get("confirmed") is True:
            found.append({"source": "bend_proof negative control", "control": c.get("name"), "policy_findings": codes,
                          "laws_that_fail": list(c.get("failing_laws") or []), "trace": example.get("steps"),
                          "final_state": example.get("final_state_in_unsafe_model"),
                          "note": "A seeded unsafe model with the same fault: Bend's proofs fail on it and this concrete run shows why."})
    return found


SPEC = KindSpec(kind="bend_proof", claim="authority_laws_model", method="formal-bend-proof-v1", protocol=PROTOCOL,
                level=LEVEL_SEALED_TOOL, establishes=ESTABLISHES, does_not_establish=DOES_NOT_ESTABLISH,
                prerequisites=PREREQUISITES, check=check, describe=describe, explain=explain)
