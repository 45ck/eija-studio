---
type: Architecture Decision Record
title: 'ADR-0025: Machine-check protected authority laws with Bend 2 in a pinned container'
description: The v0.2 runtime matrix observes one step of the runtime for 125 synthetic cells with a same-author oracle.
resource: repo://docs/adr/0025-bend-machine-checked-laws.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0025-bend-machine-checked-laws.md
  title: 0025-bend-machine-checked-laws.md
  hash_method: lf-sha256-v1
  sha256: 23a076126f117b189fd6ab4ca1d5604bd8c7ce8e196c52ec8c6e9b080e485039
notes_baseline: d7c799233f008802269e93016b81125de60ca91fd8152ac4cff3928b4481885d
---

# ADR-0025: Machine-check protected authority laws with Bend 2 in a pinned container

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed (accepted when the `lane/bend` pull request merges) |
| Date | 2026-09-28 |
| Lane | bend (formal: Bend laws and proofs) |
| Source | `repo://docs/adr/0025-bend-machine-checked-laws.md` |

## Decision outcome (verbatim)

> Chosen option: "Bend 2 run in a pinned Docker image", because its `LAWS.bend` / `PROOF.bend` convention matches the
> "human states the law, AI writes the proof, the kernel checks it" doctrine of the project, it proves properties for
> **all** action sequences by induction (which bounded checking cannot), and `--verdict` gives a small independently
> proved trust base.
>
> * Bend does not run on native Windows, so the checker is a Docker image (`verification/bend/Dockerfile`): base image by
>   digest, Bend by version, git commit and archive sha256, Lean (used only to compile the BendTT kernel) by version and
>   archive sha256. The official installer always installs the latest release and is therefore not run verbatim.
> * The gate runs the container with no network, a read-only root filesystem, no capabilities and read-only inputs.
> * PASS means exactly `bend PROOF.bend --verdict` printed `ALL PROOFS CHECK` with exit code 0. Docker, the daemon, the
>   image (built only on request: `--build` or `EIJA_BEND_BUILD=1`, since it downloads about 300 MB) missing means
>   `NOT_RUN`: exit code 3, a skipped nox session, a report with `status: NOT_RUN` and the reason. A proof run that
>   starts and then times out or is killed is a `FAIL`, never a skip. Plain `bend` output (no `--verdict`) is never
>   counted as a proof.
> * The evidence is `reports/formal/bend.json` with `kind: bend_proof`. A `bend_proof` states laws about the **model**; it
>   never stands in for runtime conformance, a human study or a proof of the Python code
>   ([ADR-0026](repo://docs/adr/0026-bend-model-generation-controls-conformance.md) defines the companions).
> * Sessions: `bend_drift` (fast, full; no Docker), `formal_bend_quick` (full; Docker), `formal_bend` (release; Docker).

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://verification/bend/bend_runner.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0018: Formal V&V portfolio: each technique is a distinct evidence kind](/adrs/0018-formal-vv-portfolio.md) - v0.2 verifies one-step behaviour with a same-author 5×5×5 runtime matrix.
* [ADR-0026: The Bend model is generated from the Workflow; negative controls and conformance accompany every proof](/adrs/0026-bend-model-generation-controls-conformance.md) - A proof is only as meaningful as the model it is about and the specification it proves.
* [ADR-0027: TLA+ specification of the workflow and commit protocol, checked with TLC](/adrs/0027-tla-plus-specification-and-model-checking.md) - The v0.2 runtime matrix checks one step from each state.
* [ADR-0029: Z3 proof that the protected policy admits only authority-preserving candidates](/adrs/0029-z3-policy-soundness-proof.md) - `domain.policy.check_policy` is the gate between an AI-proposed candidate workflow and the local owner.

## Referenced by

* [ADR-0145: Per-kind admissibility: the kernel recomputes formal evidence from raw artifacts](/adrs/0145-per-kind-evidence-admissibility.md) - `domain.evidence.assess_receipt` recomputes admissibility for one claim only: the runtime matrix (`runtime_matrix` / `integration_test`).
* [Formal: Bend laws and proofs](/lanes/0025-formal-bend-laws-and-proofs.md) - Capability lane with ADR numbers 0025–0026 reserved.
<!-- okf:generated:end links -->
