# ADR-0145: Per-kind admissibility: the kernel recomputes formal evidence from raw artifacts

* Status: proposed (accepted when the `lane/evidence-kinds` pull request merges)
* Date: 2026-09-29
* Lane: evidence-kinds (POC criteria 4 and 5)

## Context and problem statement

`domain.evidence.assess_receipt` recomputes admissibility for one claim only: the runtime matrix (`runtime_matrix` /
`integration_test`). Every other claim returns `UNKNOWN` by design, because the verifier had no authority to establish it
([ADR-009](0000-poc-decision-log.md)). The formal lanes now produce results the owner should see next to the matrix: Bend
laws ([ADR-0025](0025-bend-machine-checked-laws.md)), a Z3 proof of policy soundness and a bounded model check of the
runtime (ADR-0029, ADR-0030), and later TLC, property tests and a mutation score
([ADR-0018](0018-formal-vv-portfolio.md)). Today none of them can appear in the review packet or the Studio, so the POC
cannot show "formal evidence, UNKNOWN visible" (criterion 4) or the counterexample that stops the unsafe change (criterion
5). How does the kernel accept a formal result without accepting a green label?

## Decision drivers

* The kernel is the small trusted checker; artifacts, extractors, tool reports and agents are untrusted. A supplied green
  status is never evidence ([ADR-009](0000-poc-decision-log.md)).
* A proof about a MODEL is not a proof about the code; a bounded search is bounded. Each kind must carry its assumptions and
  bounds and say what it does not establish.
* A proof that cannot fail proves nothing: negative controls are part of admissibility, not decoration.
* Evidence must bind to the CURRENT subject; a changed model must make a receipt STALE, not quietly still green.
* FAIL must stop approval; UNKNOWN and NOT_RUN must never block and must never be rounded up
  ([ADR-010](0000-poc-decision-log.md)).
* Adding TLC, property tests or a mutation score must not need a kernel rewrite.
* Determinism across Windows and POSIX; import-linter layers stay intact.

## Considered options

* **Trust the sealed local producer only.** Accept a receipt whose HMAC seal verifies and whose artifact says `PASS`.
  Simple, but the seal proves only that the local intake wrapped some bytes: a bug in an extractor, a tampered report, a
  weakened law file or a tool run that an agent influenced would produce a green the kernel never examined. It also makes
  the kernel's answer identical to the label it was given. Rejected.
* **Recompute from raw typed artifacts, per kind (chosen).** Each kind is a typed shape plus a pure `check` that derives the
  verdict from the raw content: law results, negative controls, declared minimum bounds, coverage and the binding to the
  current subject. The tool's own labels may lower a status, never raise it.
* **Re-check a proof certificate.** The strongest option: Z3 can export a proof object and Bend's `--verdict` rechecks with a
  Lean-proven kernel, so a small independent checker could accept `unsat` without trusting the solver. Neither certificate
  currently leaves its tool, and an independent checker for the SMT encoding does not exist here. Not available today; kept as
  the upgrade path (below).
* **Re-run the tools inside the kernel.** Would recompute everything, but needs Docker, Java, z3 and minutes of CPU inside
  `domain/`, breaks the layering contracts and determinism, and turns the small checker into a large one. Rejected.

## Decision outcome

Chosen option: "recompute from raw typed artifacts, per kind", with these rules.

1. **A kind is a registered `KindSpec`** (`domain/evidence_kinds.py`): claim, method, protocol version, evidence level, what it
   establishes, what it does NOT establish, prerequisites, a pure `check(artifact, context) -> Assessment`, a `describe` for the
   packet and an `explain` for policy blocks. A kind that is not registered is `UNKNOWN` by construction. The runtime matrix path
   is unchanged (`assess_receipt` keeps its behaviour for `runtime_matrix` / `integration_test`).
2. **The envelope is checked in the runtime matrix's order** (claim and kind, subject dimensions, artifact hash, producer, method,
   protocol) so a stale or tampered receipt is judged the same way for every kind. A hash mismatch or a malformed artifact is
   `FAIL`; an unknown producer or protocol version is `UNKNOWN`; a receipt for another subject is `STALE`.
3. **Statuses** are the existing algebra `PASS / FAIL / STALE / UNKNOWN / CONFLICT` plus a distinct **`NOT_RUN`** for a missing
   prerequisite (Docker, Java, z3, a saved run). Combination: authenticated PASS and FAIL never average (`CONFLICT`); FAIL beats
   everything but CONFLICT; PASS beats STALE, NOT_RUN and UNKNOWN; then STALE, NOT_RUN, UNKNOWN. No receipt at all is `UNKNOWN`
   ("no receipt attached"), so absence is visible.
4. **Within a kind, findings have a severity:** STALE (about another subject), then FAIL (a counterexample, a contradiction, a
   control that did not fail, a structural defect), then UNKNOWN (evidence missing, incomplete, below a declared minimum bound, an
   unaccepted tool version). Only PASS when there is no finding. Each finding is a text reason shown in the packet.
5. **The tool's own labels can only lower.** A `FAIL`, `PARTIAL`, `INCONCLUSIVE` or failed tool check reported by the tool caps the
   status; a `PASS` label is ignored (the kernel recomputes).
6. **Negative controls are pinned by the kernel**, not read from the artifact: the kernel knows which seeded faults each proof
   must reject and which laws each must break. A missing control is `UNKNOWN`; a control the proof did not reject, or that broke
   other laws, or has no confirmed concrete counterexample, is `FAIL` (the proof is insensitive: its green is worthless).
7. **Bounds are declared minimums** (BMC depth, Bend conformance cells, SMT differential candidates, Bend `complete` mode); a bound
   smaller than the minimum is `UNKNOWN`, and the packet shows the bound that was run.
8. **Binding to the current subject has two layers, and the packet says which.** *Recomputed by the kernel:* the semantic hashes
   of the current baseline and candidate compared with the model the tool was about (Bend: both slots; SMT: the candidate is in
   the set of workflows the policy was shown to admit; BMC: the candidate is among the models explored). *Attested by the sealed
   local adapter:* the current bytes of the tool's model and source files (and, for Bend, the model regenerated from the current
   workflows), compared with what the report names. A difference is `STALE`; an unobservable current source is `UNKNOWN`.
9. **Evidence levels** are labels for the reader, not inputs to a status: `recomputed` (the kernel re-derived the outcome from
   raw observations of its own semantics: the runtime matrix) and `sealed_tool_verdict` (a solver or prover verdict without a
   checkable certificate, accepted under the sealed local producer). Bend, SMT and BMC are all `sealed_tool_verdict` today.
10. **FAIL and CONFLICT of any formal kind block technical eligibility** (`FORMAL_EVIDENCE_FAIL:<kind>`); UNKNOWN, NOT_RUN and
    STALE never block. The formal kinds are ADDITIONAL to the runtime matrix, which stays required.

### Consequences

* Good: a formal result appears in the packet only through a recomputation a reviewer can read; a forged green, a tampered
  byte, a stale model, missing negative controls and shallow bounds each have a named test.
* Good: a new kind (`tlc_model_check`, property test, mutation score) is one module and one registry line; the envelope,
  aggregation, packet, UI and CLI are unchanged.
* Good: a proof upgraded to a checkable certificate changes only its `level` and its `check`, not the architecture.
* Bad: the kernel pins names (required laws, invariants, controls, mutants, tool versions, minimum bounds), so a lane that
  renames or adds a required item must change the kernel and this ADR in the same review. That is deliberate friction: it
  prevents a lane from weakening its own evidence unnoticed, and extra items in a report (more invariants) are accepted only if
  they are proved too.
* Bad: `sealed_tool_verdict` evidence still trusts the tool (Z3, Bend's kernel) and the sealed local adapter. The HMAC key owner
  can forge anything ([SECURITY_AND_TRUST.md](../SECURITY_AND_TRUST.md)); this ADR narrows what a non-key-holder can do, it does
  not remove that limit.
* Bad: the laws themselves (`LAWS.bend`), the SMT invariants and the BMC oracle are same-author specifications; recomputation
  checks that the proofs are about them, not that they are the right requirements.
* Revisit when: a proof certificate (Z3 proof objects, a second solver, Lean export) can be re-checked by an independent small
  checker: promote that kind to a checked level. Also when a fourth kind lands (a registry that must be edited in several files
  is a signal to extract a kind plugin contract).

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| pydantic (already a dependency) for the artifact shapes | strict models validate shape but not the verdict logic; keeping the typed accessors next to the checks makes every failure a readable reason string and avoids a second schema language | move shapes to strict pydantic models if a kind's shape grows beyond a screen |
| jsonschema | same as above, plus a new dependency in the kernel | as above |
| Z3 proof objects / Lean / a second solver as certificate checkers | not exported or not available for this encoding today | the upgrade path in the Consequences |
