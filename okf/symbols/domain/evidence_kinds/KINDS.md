---
type: Constant
title: domain.evidence_kinds.KINDS
description: Constant `KINDS` in `domain/evidence_kinds`.
resource: repo://src/eija_studio/domain/evidence_kinds.py#KINDS
tags:
- symbol
- domain
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/evidence_kinds.py#KINDS
  title: domain/evidence_kinds.py
  hash_method: ast-v2
  sha256: 5ac27b1948ea871ddcedc1817d19c933325d6b57f07c72171946636d80a105e0
notes_baseline: 9892a172094af5271312074b5d1b04e29048e3825f7bb8b65690eaad0879025f
---

# domain.evidence_kinds.KINDS

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`domain/evidence_kinds`](/modules/domain/evidence_kinds.md) |
| Signature | `KINDS: dict[str, KindSpec] = {spec.kind: spec for spec in (BEND_PROOF, SMT_PROOF, BOUNDED_MODEL_CHECK)}` |
| Code | `repo://src/eija_studio/domain/evidence_kinds.py#KINDS` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.formal.KindSpec](/symbols/domain/formal/KindSpec.md) - One evidence kind: what it claims, how it is checked, what it does not establish.
* [domain.formal_bend.SPEC](/symbols/domain/formal_bend/SPEC.md) - Constant `SPEC` in `domain/formal_bend`.
* [domain.formal_bmc.SPEC](/symbols/domain/formal_bmc/SPEC.md) - Constant `SPEC` in `domain/formal_bmc`.
* [domain.formal_smt.SPEC](/symbols/domain/formal_smt/SPEC.md) - Constant `SPEC` in `domain/formal_smt`.

## Referenced by

* [application.formal.attach](/symbols/application/formal/attach.md) - Sealed receipts for every registered kind the source returned, skipping an exact repeat of the latest one.
* [application.formal.packet_view](/symbols/application/formal/packet_view.md) - The formal part of the review packet: per-kind claims, blockers, the full evidence list, explanations.
* [domain.evidence.assess_formal_receipt](/symbols/domain/evidence/assess_formal_receipt.md) - Per-kind admissibility (ADR-0145): envelope checks in the runtime matrix's order, then the kind's own check.
* [domain.evidence.intact_artifact](/symbols/domain/evidence/intact_artifact.md) - The raw artifact of an authentic, hash-consistent, known-protocol receipt of this kind, whatever its subject.
<!-- okf:generated:end links -->
