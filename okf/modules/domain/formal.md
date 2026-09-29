---
type: Module
title: domain.formal
description: Primitives for per-kind admissibility of formal evidence (ADR-0145, ADR-0146).
resource: repo://src/eija_studio/domain/formal.py
tags:
- module
- domain
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal.py
  title: domain/formal.py
  hash_method: ast-api-v1
  sha256: 5c5efe49259a15c57e9a4e25a13c2c299b529e7364f176ff3204509285c731b8
notes_baseline: bc560c71c4f0ac4ef0291c5e1cfcde1d292fb9885ae52ae1b3172ded18c3e765
---

# domain.formal

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | domain |
| Code | `repo://src/eija_studio/domain/formal.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Primitives for per-kind admissibility of formal evidence (ADR-0145, ADR-0146).

The kernel is the small trusted checker. An artifact (and the extractor that produced it, and any agent
that asked for it) is untrusted: a supplied green label is never read as a verdict. Each evidence kind
declares a typed artifact shape and a pure ``check`` that RECOMPUTES the verdict from the raw typed
content: law results, negative controls, declared minimum bounds, coverage and the binding to the
current subject. This module holds the vocabulary those checks share; the kinds live in
``formal_bend``, ``formal_smt`` and ``formal_bmc``, and ``evidence_kinds`` registers them.

Nothing here imports a vendor library, touches the file system or reads a clock.
~~~

## Public symbols

* [`Assessment`](/symbols/domain/formal/Assessment.md) (class) - no docstring
* [`Context`](/symbols/domain/formal/Context.md) (class) - What the kernel itself knows about the CURRENT subject, beyond the technical dimensions.
* [`FORMAL_PRODUCER`](/symbols/domain/formal/FORMAL_PRODUCER.md) (constant) - no docstring
* [`Findings`](/symbols/domain/formal/Findings.md) (class) - Collects reasons by severity.
* [`FormalArtifact`](/symbols/domain/formal/FormalArtifact.md) (class) - One raw formal artifact from a tool report.
* [`KindSpec`](/symbols/domain/formal/KindSpec.md) (class) - One evidence kind: what it claims, how it is checked, what it does not establish.
* [`LEVEL_RECOMPUTED`](/symbols/domain/formal/LEVEL_RECOMPUTED.md) (constant) - no docstring
* [`LEVEL_SEALED_TOOL`](/symbols/domain/formal/LEVEL_SEALED_TOOL.md) (constant) - no docstring
* [`Malformed`](/symbols/domain/formal/Malformed.md) (class) - The artifact does not have the declared typed shape (a structural defect, judged FAIL).
* [`as_records`](/symbols/domain/formal/as_records.md) (function) - Defensive view for display-only helpers: a list of dicts, or nothing.
* [`carried_statements`](/symbols/domain/formal/carried_statements.md) (function) - The artifact must carry its own assumptions and limitations (a proof without them is not shown as one).
* [`digest`](/symbols/domain/formal/digest.md) (function) - no docstring
* [`exact_keys`](/symbols/domain/formal/exact_keys.md) (function) - no docstring
* [`field`](/symbols/domain/formal/field.md) (function) - ``container[key]`` if it is exactly of ``typ`` (``bool`` is not an ``int``); else the artifact is malformed.
* [`has_items`](/symbols/domain/formal/has_items.md) (function) - True if the list at ``key`` is not empty (its items may be of any type).
* [`not_run_reason`](/symbols/domain/formal/not_run_reason.md) (function) - A NOT_RUN artifact is exactly {protocol, not_run: {reason, prerequisite}}: honest absence, never PASS.
* [`records`](/symbols/domain/formal/records.md) (function) - no docstring
* [`reported_labels`](/symbols/domain/formal/reported_labels.md) (function) - The tool's own verdict and check labels may LOWER the status, never raise it.
* [`source_binding`](/symbols/domain/formal/source_binding.md) (function) - Producer sources named by the tool's report versus the bytes the adapter observes now.
* [`strings`](/symbols/domain/formal/strings.md) (function) - no docstring
* [`text`](/symbols/domain/formal/text.md) (function) - no docstring
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.compiler](/modules/application/compiler.md) - Compiler: model → projections + impacts + obligations + computed review packet.
* [application.formal](/modules/application/formal.md) - Formal evidence in the application layer: seal what an adapter collected, and build the packet view.
* [application.ports](/modules/application/ports.md) - Application-owned ports.
* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [domain.evidence](/modules/domain/evidence.md) - Compatibility is computed.
* [domain.evidence_kinds](/modules/domain/evidence_kinds.md) - The registry of evidence kinds the kernel can assess (ADR-0145).
* [domain.formal_bend](/modules/domain/formal_bend.md) - Admissibility of ``bend_proof`` receipts (ADR-0146; lane bend, ADR-0025 and ADR-0026).
* [domain.formal_bmc](/modules/domain/formal_bmc.md) - Admissibility of ``bounded_model_check`` receipts (ADR-0146; lane smt-bmc, ADR-0030).
* [domain.formal_smt](/modules/domain/formal_smt.md) - Admissibility of ``smt_proof`` receipts (ADR-0146; lane smt-bmc, ADR-0029).
* [domain.formal.Assessment](/symbols/domain/formal/Assessment.md) - `class Assessment` in `domain/formal`.
* [domain.formal.Context](/symbols/domain/formal/Context.md) - What the kernel itself knows about the CURRENT subject, beyond the technical dimensions.
* [domain.formal.FORMAL_PRODUCER](/symbols/domain/formal/FORMAL_PRODUCER.md) - Constant `FORMAL_PRODUCER` in `domain/formal`.
* [domain.formal.Findings.fail](/symbols/domain/formal/Findings.fail.md) - `def fail(self, why: str) -> None` in `domain/formal`.
* [domain.formal.Findings](/symbols/domain/formal/Findings.md) - Collects reasons by severity.
* [domain.formal.Findings.result](/symbols/domain/formal/Findings.result.md) - `def result(self) -> Assessment` in `domain/formal`.
* [domain.formal.Findings.stale](/symbols/domain/formal/Findings.stale.md) - `def stale(self, why: str) -> None` in `domain/formal`.
* [domain.formal.Findings.unknown](/symbols/domain/formal/Findings.unknown.md) - `def unknown(self, why: str) -> None` in `domain/formal`.
* [domain.formal.FormalArtifact](/symbols/domain/formal/FormalArtifact.md) - One raw formal artifact from a tool report.
* [domain.formal.KindSpec](/symbols/domain/formal/KindSpec.md) - One evidence kind: what it claims, how it is checked, what it does not establish.
* [domain.formal.LEVEL_RECOMPUTED](/symbols/domain/formal/LEVEL_RECOMPUTED.md) - Constant `LEVEL_RECOMPUTED` in `domain/formal`.
* [domain.formal.LEVEL_SEALED_TOOL](/symbols/domain/formal/LEVEL_SEALED_TOOL.md) - Constant `LEVEL_SEALED_TOOL` in `domain/formal`.
* [domain.formal.Malformed](/symbols/domain/formal/Malformed.md) - The artifact does not have the declared typed shape (a structural defect, judged FAIL).
* [domain.formal.as_records](/symbols/domain/formal/as_records.md) - Defensive view for display-only helpers: a list of dicts, or nothing.
* [domain.formal.carried_statements](/symbols/domain/formal/carried_statements.md) - The artifact must carry its own assumptions and limitations (a proof without them is not shown as one).
* [domain.formal.digest](/symbols/domain/formal/digest.md) - `def digest(container: Any, key: str, where: str) -> str` in `domain/formal`.
* [domain.formal.exact_keys](/symbols/domain/formal/exact_keys.md) - `def exact_keys(artifact: dict[str, Any], keys: frozenset[str]) -> None` in `domain/formal`.
* [domain.formal.field](/symbols/domain/formal/field.md) - ``container[key]`` if it is exactly of ``typ`` (``bool`` is not an ``int``); else the artifact is malformed.
* [domain.formal.has_items](/symbols/domain/formal/has_items.md) - True if the list at ``key`` is not empty (its items may be of any type).
* [domain.formal.not_run_reason](/symbols/domain/formal/not_run_reason.md) - A NOT_RUN artifact is exactly {protocol, not_run: {reason, prerequisite}}: honest absence, never PASS.
* [domain.formal.records](/symbols/domain/formal/records.md) - `def records(container: Any, key: str, where: str) -> list[dict[str, Any]]` in `domain/formal`.
* [domain.formal.reported_labels](/symbols/domain/formal/reported_labels.md) - The tool's own verdict and check labels may LOWER the status, never raise it.
* [domain.formal.source_binding](/symbols/domain/formal/source_binding.md) - Producer sources named by the tool's report versus the bytes the adapter observes now.
* [domain.formal.strings](/symbols/domain/formal/strings.md) - `def strings(container: Any, key: str, where: str, minimum: int=1) -> list[str]` in `domain/formal`.
* [domain.formal.text](/symbols/domain/formal/text.md) - `def text(container: Any, key: str, where: str) -> str` in `domain/formal`.
<!-- okf:generated:end links -->
