---
type: Architecture Decision Record
title: 'ADR-0146: Formal receipt formats, binding to the subject, and NOT_RUN semantics'
description: ADR-0145 decides that the kernel recomputes formal evidence per kind.
resource: repo://docs/adr/0146-formal-receipt-formats-binding-and-not-run.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0146-formal-receipt-formats-binding-and-not-run.md
  title: 0146-formal-receipt-formats-binding-and-not-run.md
  hash_method: lf-sha256-v1
  sha256: 4692b511acd289f3570f6b2feb4121f376bd199ee600b8bd6814f171b222e078
notes_baseline: 1a29024a4627ec90f907664f174875e45d8551e578d4f2197ecddbd5263520c9
---

# ADR-0146: Formal receipt formats, binding to the subject, and NOT_RUN semantics

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed (accepted when the `lane/evidence-kinds` pull request merges) |
| Date | 2026-09-29 |
| Lane | evidence-kinds (POC criteria 4 and 5) |
| Source | `repo://docs/adr/0146-formal-receipt-formats-binding-and-not-run.md` |

## Decision outcome (verbatim)

> Chosen option: "a normalised, typed artifact per kind, copied from the report by an adapter that computes no verdict".
>
> **Receipt** (same shape as the runtime receipt, plus `measurements`):
> `{id, claim, kind, subject, producer: "eija-formal-intake", method, created_at, artifact_hash, artifact, measurements}`, sealed
> with the local HMAC. `subject` carries the technical dimensions of the current subject; `artifact_hash = fingerprint(artifact)`;
> `created_at` and `measurements` (platform, Python, report file hash, origin path) are outside the hash.
>
> **Artifact** (`protocol` names the version; the top-level key set is exact, so an unexpected field is a structural FAIL):
>
> | Kind (claim) | Protocol | Raw content copied from the report | Binding fields |
> |---|---|---|---|
> | `bend_proof` (`authority_laws_model`) | `eija.formal.bend-proof/v1` | tool and image identity, mode, per-law results, model-check and full `--verdict` results, six negative controls (failing laws, confirmed counterexample or effect probe, kernel policy findings), conformance matrix and witnesses | `model.semantic_hash{Baseline,Candidate}`, `model.files`, `binding.current_files_sha256`, `binding.regenerated_main_bend_sha256` |
> | `smt_proof` (`policy_soundness`) | `eija.formal.smt-proof/v1` | solver identity, grammar bounds, per-invariant status (a refuted one keeps its witness), non-vacuity, admitted-set enumeration with the semantic hash of each admitted workflow, differential-test counts and disagreement lists, named leave-one-out controls with witness transitions | `subject_function`, `binding.{reported,current}_sources_sha256_lf` |
> | `bounded_model_check` (`runtime_safety_bounded`) | `eija.formal.bounded-model-check/v1` | tier, bounds (depth, alphabet, toggles), invariants checked, per model: states, transitions, depth reached, exhausted, truncated, unreached outcome classes, invariant checks; counterexamples; the seeded-fault self-test | `subject_function`, per-model `semantic_hash`, `binding.{reported,current}_sources_sha256_lf` |
>
> Every artifact also carries `assumptions`, `limitations` (both must be non-empty), `reported` (the tool's own verdict and check
> labels, used only to lower a status) and `source.origin` (the report path). Wall-clock, timings and platform are not artifact
> fields.
>
> **Binding.** Recomputed by the kernel from the Workflow objects it holds: the current candidate and baseline semantic hashes

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0145: Per-kind admissibility: the kernel recomputes formal evidence from raw artifacts](/adrs/0145-per-kind-evidence-admissibility.md) - `domain.evidence.assess_receipt` recomputes admissibility for one claim only: the runtime matrix (`runtime_matrix` / `integration_test`).
<!-- okf:generated:end links -->
