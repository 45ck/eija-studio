# ADR-0025: Machine-check protected authority laws with Bend 2 in a pinned container

* Status: proposed (accepted when the `lane/bend` pull request merges)
* Date: 2026-09-28
* Lane: bend (formal: Bend laws and proofs)

## Context and problem statement

The v0.2 runtime matrix observes one step of the runtime for 125 synthetic cells with a same-author oracle. The
protected policy is stronger than any single step: a teacher must never reach Approved by any sequence of actions,
approval must be preceded by recommendation, and forbidden effects must never be emitted. [ADR-0018](0018-formal-vv-portfolio.md)
reserves an evidence kind `bend_proof` for laws that hold for all action sequences of the model generated from code.
Which tool checks them, where does it run on a Windows-first reference PC, and what does a green result mean?

## Decision drivers

* The laws must be stated by a human in a form a reviewer can read, separately from the proofs an AI may write (a
  human-owned specification, machine-owned proof).
* A proof checker with a small trusted kernel; a wrong proof must not be accepted.
* OSS first ([ADR-0016](0016-oss-first-adapters-not-engines.md)); no custom prover.
* A missing prerequisite reports `NOT_RUN`, never `PASS`.
* Reproducible verdicts: the tool version and its dependencies must be pinned.

## Considered options

* **Bend 2** ([bendlang/bend](https://github.com/bendlang/bend), Apache-2.0): `LAWS.bend` states laws, `PROOF.bend` proves
  them, `bend PROOF.bend --verdict` rechecks with a small Lean-proven kernel (BendTT). Linux, macOS and WSL only.
* Lean 4 / Coq / Agda / Isabelle directly: mature, larger proof ecosystems, heavier toolchains, no laws/proof file
  convention aimed at AI-written proofs, and a translation layer we would have to invent.
* Dafny: verifies programs, not standalone laws about a generated model.
* Z3 and TLA+/TLC: covered by their own lanes ([ADR-0029..0030](README.md), [ADR-0027..0028](README.md)) for different
  claims (policy soundness, bounded temporal properties); complementary, not substitutes for an unbounded proof over all sequences.

## Decision outcome

Chosen option: "Bend 2 run in a pinned Docker image", because its `LAWS.bend` / `PROOF.bend` convention matches the
"human states the law, AI writes the proof, the kernel checks it" doctrine of the project, it proves properties for
**all** action sequences by induction (which bounded checking cannot), and `--verdict` gives a small independently
proved trust base.

* Bend does not run on native Windows, so the checker is a Docker image (`verification/bend/Dockerfile`): base image by
  digest, Bend by version, git commit and archive sha256, Lean (used only to compile the BendTT kernel) by version and
  archive sha256. The official installer always installs the latest release and is therefore not run verbatim.
* The gate runs the container with no network, a read-only root filesystem, no capabilities and read-only inputs.
* PASS means exactly `bend PROOF.bend --verdict` printed `ALL PROOFS CHECK` with exit code 0. Docker, the daemon, the
  image (first build needs network) or a timeout missing means `NOT_RUN`: exit code 3, a skipped nox session, a report with
  `status: NOT_RUN` and the reason.
* The evidence is `reports/formal/bend.json` with `kind: bend_proof`. A `bend_proof` states laws about the **model**; it
  never stands in for runtime conformance, a human study or a proof of the Python code
  ([ADR-0026](0026-bend-model-generation-controls-conformance.md) defines the companions).
* Sessions: `bend_drift` (fast, full; no Docker), `formal_bend_quick` (full; Docker), `formal_bend` (release; Docker).

### Consequences

* Good: machine-checked laws over all sequences with a small trust base; the laws read as specifications; the same
  proofs are reusable against unsafe variants.
* Bad: a Docker dependency (skipped, not failed, when absent); Bend 2 is young (2.0.x) and its language may change,
  so the version is pinned and upgrading is an explicit, reviewed change; the first image build needs network and
  downloads roughly 300 MB of pinned archives.
* Revisit when: Bend supports native Windows, a Bend release changes `--verdict` semantics, or another lane's
  Lean/Coq tooling makes a shared proof toolchain cheaper.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| Bend 2 (`bend`, BendTT kernel), Lean 4, Docker | Adopted as is; not forked | Replace the checker image with a native `bend` install on Linux/macOS/WSL by editing only `Checker` in `bend_runner.py` |
| `verification/bend/bend_runner.py` | No existing tool runs a pinned Bend, classifies its verdict honestly and emits an EIJA evidence record | Thin adapter (subprocess + JSON); delete if Bend ships an evidence-report mode |
