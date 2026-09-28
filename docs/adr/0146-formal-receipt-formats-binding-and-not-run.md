# ADR-0146: Formal receipt formats, binding to the subject, and NOT_RUN semantics

* Status: proposed (accepted when the `lane/evidence-kinds` pull request merges)
* Date: 2026-09-29
* Lane: evidence-kinds (POC criteria 4 and 5)

## Context and problem statement

[ADR-0145](0145-per-kind-evidence-admissibility.md) decides that the kernel recomputes formal evidence per kind. That needs a
concrete receipt and artifact format: what a tool's report becomes before the kernel sees it, how a receipt binds to the current
subject, what is recomputed and what is only attested, and what happens when a prerequisite (Docker, Java, z3, a saved run) is
missing. Determinism matters: canonical artifacts must be byte-identical on Windows and POSIX, with no wall-clock in any hash.

## Decision drivers

* Raw, typed, retained content: the kernel must be able to recompute from what is stored, not from a summary label.
* Adapters read tools; they do not judge. A verdict computed in an adapter is a verdict nobody rechecks.
* Absence must be visible: a missing prerequisite is a state in the packet, not a gap.
* Same bytes on every OS: no timestamps, platform strings or timings inside a hashed artifact; LF-normalised source hashes.
* Layers: domain has the pure checks and the artifact data type, application owns the port and the intake, adapters read
  reports and import only from the domain, bootstrap wires.

## Considered options

* **Store the tool's whole report in the receipt.** Faithful, but the SMT report is about 300 KB (mostly leave-one-out rows),
  changes with every timing, and would make every `verify` grow the case row; two runs of the same proof would hash differently.
* **Store a verdict summary.** Small, but the kernel would judge a label.
* **Store a normalised subset of the raw fields, copied not interpreted (chosen).** Small, deterministic, and everything the
  kernel needs to recompute is present; the report file's hash and the platform go beside the artifact, unhashed.

## Decision outcome

Chosen option: "a normalised, typed artifact per kind, copied from the report by an adapter that computes no verdict".

**Receipt** (same shape as the runtime receipt, plus `measurements`):
`{id, claim, kind, subject, producer: "eija-formal-intake", method, created_at, artifact_hash, artifact, measurements}`, sealed
with the local HMAC. `subject` carries the technical dimensions of the current subject; `artifact_hash = fingerprint(artifact)`;
`created_at` and `measurements` (platform, Python, report file hash, origin path) are outside the hash.

**Artifact** (`protocol` names the version; the top-level key set is exact, so an unexpected field is a structural FAIL):

| Kind (claim) | Protocol | Raw content copied from the report | Binding fields |
|---|---|---|---|
| `bend_proof` (`authority_laws_model`) | `eija.formal.bend-proof/v1` | tool and image identity, mode, per-law results, model-check and full `--verdict` results, six negative controls (failing laws, confirmed counterexample or effect probe, kernel policy findings), conformance matrix and witnesses | `model.semantic_hash{Baseline,Candidate}`, `model.files`, `binding.current_files_sha256`, `binding.regenerated_main_bend_sha256` |
| `smt_proof` (`policy_soundness`) | `eija.formal.smt-proof/v1` | solver identity, grammar bounds, per-invariant status (a refuted one keeps its witness), non-vacuity, admitted-set enumeration with the semantic hash of each admitted workflow, differential-test counts and disagreement lists, named leave-one-out controls with witness transitions | `subject_function`, `binding.{reported,current}_sources_sha256_lf` |
| `bounded_model_check` (`runtime_safety_bounded`) | `eija.formal.bounded-model-check/v1` | tier, bounds (depth, alphabet, toggles), invariants checked, per model: states, transitions, depth reached, exhausted, truncated, unreached outcome classes, invariant checks; counterexamples; the seeded-fault self-test | `subject_function`, per-model `semantic_hash`, `binding.{reported,current}_sources_sha256_lf` |

Every artifact also carries `assumptions`, `limitations` (both must be non-empty), `reported` (the tool's own verdict and check
labels, used only to lower a status) and `source.origin` (the report path). Wall-clock, timings and platform are not artifact
fields.

**Binding.** Recomputed by the kernel from the Workflow objects it holds: the current candidate and baseline semantic hashes
against the models the tool was about. Attested by the sealed local adapter and then compared inside the artifact: the current
bytes (LF-normalised SHA-256) of the model and source files against those the report names, and for Bend the `main.bend`
regenerated from the current baseline and candidate by the lane's own generator against the text that was proved. Any difference
is `STALE`. The adapter cannot regenerate outside a source checkout (the generator lives under `verification/`), so there the
binding is `UNKNOWN`, not assumed.

**NOT_RUN.** When a prerequisite is missing or a report cannot be read, the adapter returns an artifact that is exactly
`{protocol, not_run: {reason, prerequisite}}` and the intake seals it like any receipt, so the packet shows the kind as
`NOT_RUN` with the reason. It never contributes PASS, never blocks, never hides a FAIL (FAIL beats it), and is beaten by a real PASS
for the same subject. A `not_run` block mixed with content, an empty reason or an extra key is a structural `FAIL`. A report of an
unexpected shape or schema becomes `NOT_RUN` ("does not have the expected report shape"), never a crash and never a pass. Every
readable report is its own receipt (a fresh run and the committed snapshot, or a shallow and a deep search), so a broken or stale
report never hides a good one and a fresh failing report conflicts with an older pass.

**Intake.** `Studio.verify` asks the optional `FormalEvidenceSource` port for artifacts after the runtime matrix, seals them with
the local signer and appends them to the case; an exact repeat of the latest receipt of a kind (same artifact hash, same technical
dimensions) is not appended again. Without a source, the kinds are `UNKNOWN` ("no receipt attached"). `build_studio(formal=True)`
wires the adapter; the CLI and the Studio do, unless `--no-formal`.

**Explanations.** When the kernel's policy blocks a candidate, the packet attaches the negative-control counterexamples of intact
(authentic, hash-consistent, known-protocol) receipts whose fault class equals a policy error code: a Bend control's
`kernel_policy_findings`, an SMT leave-one-out clause `<code>/...`. They are labelled as seeded unsafe models that explain the
block, never as a proof about the candidate, and carry the status of the positive proof beside them (STALE when it is about
another model).

**Blocked meanings.** A proposed interpretation the policy refuses (`final_approval`) never becomes a candidate, so it has no
receipts. The packet of a case without a selected meaning therefore carries `blocked_meanings`: the what-if model that
interpretation would produce (recommendation enabled, the fault applied: Approve held by the Teacher; it is exactly the model the
Bend lane seeds as its unsafe control), the kernel's policy errors for it, and the same negative-control explanations. The what-if
model is evaluated and explained, never stored, never verified and never approvable.

**Determinism.** An artifact is a pure function of the report and the current source bytes: canonical JSON (sorted keys, no
NaN), LF-normalised hashes, no clock. Tests assert identical artifact hashes across repeated collection, across a CRLF checkout
and across changes in report timings.

### Consequences

* Good: the packet can show every formal claim with status, level, assumptions, bounds, what it does not establish and, for a
  block, the counterexample; a missing tool is a visible `NOT_RUN`.
* Good: adapters stay thin readers (they copy fields and compute nothing); the kernel holds all judgement; another lane's report format change
  breaks an extractor test or becomes `NOT_RUN`, never a silent PASS.
* Bad: the artifact is a projection: fields the kernel does not read (per-clause timings, the full leave-one-out table) are not
  retained in the case; the report file's hash (in `measurements`) identifies the source.
* Bad: file-level binding is attested, not recomputed, and the laws file is bound by hash but not judged.
* Bad: the receipt's `subject` dimensions are stamped at intake, so for an older report (a committed snapshot) they say "collected
  for this subject", not "proved for this subject". The proof-time binding is the artifact's own: the model hashes, the
  admitted set, the file and source hashes the report names. A source the report does not name (for Bend, the runtime that the
  conformance test compared with) is not bound: the Bend lane should record those hashes in its report, and the runtime matrix,
  which is recomputed for the current subject on every verify, stays required.
* Bad: a process that can write `reports/formal/*.json` or the committed snapshots can supply a report that is internally
  consistent and the local intake will seal it. Recomputation rejects inconsistent forgeries only; provenance of a report is not
  authenticated (git review covers the committed snapshots).
* Revisit when: the smt-bmc or bend lane changes its report schema (bump the protocol), the formal lanes commit evidence
  snapshots (add them to the report search paths), or a kind needs a checkable certificate (add its bytes to the artifact).

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| in-toto / SLSA attestations | attest who built what; do not recompute a formal verdict from raw content, and need signing infrastructure the local POC does not have | wrap the sealed receipt in an attestation when an independent trust root exists |
| Bend, Z3, the BMC explorer | they are the tools; this ADR only reads their reports | unchanged |
