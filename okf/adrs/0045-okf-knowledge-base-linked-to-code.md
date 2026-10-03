---
type: Architecture Decision Record
title: 'ADR-0045: An OKF v0.2 knowledge base deterministically linked to code'
description: Humans and agents need a place to start reading EIJA that is smaller than the repository and does not go stale.
resource: repo://docs/adr/0045-okf-knowledge-base-linked-to-code.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0045-okf-knowledge-base-linked-to-code.md
  title: 0045-okf-knowledge-base-linked-to-code.md
  hash_method: lf-sha256-v1
  sha256: ebe5c97d436a6d4e94c4c7a8bd9a0d186fffe321c0f231756f5f71f3fcb301f4
notes_baseline: 4f2d4c715a5d36ed00d29a1b3852f11933357957e34101a6767f606f743e8617
verified:
- by: process:eija-okf-lane-fix
  at: '2026-09-28T23:24:05Z'
  notes_sha256: daa96077fbe4018a5859a097276a24e330f4c037fdac4262009cb703aac7c1ce
  sources_sha256: 4f2d4c715a5d36ed00d29a1b3852f11933357957e34101a6767f606f743e8617
---

# ADR-0045: An OKF v0.2 knowledge base deterministically linked to code

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed |
| Date | 2026-09-28 |
| Lane | okf |
| Source | `repo://docs/adr/0045-okf-knowledge-base-linked-to-code.md` |

## Decision outcome (verbatim)

> Chosen option: "OKF v0.2 bundle at `okf/`, generated from code and gated by `nox -s okf`", because v0.2 makes provenance, trust and lifecycle first-class frontmatter, which is exactly what code linkage needs, and it is plain markdown that any agent can read.
>
> How the linkage works:
>
> * `resource` is a stable `repo://<path>[#<fragment>]` URI. `sources[]` entries carry `hash_method` and `sha256` of the normalised thing they describe (details and normalisation in [ADR-0046](repo://docs/adr/0046-code-link-hash-methods-and-stale-semantics.md)).
> * Machine-owned frontmatter and `okf:generated` blocks are rewritten by `python -m quality.okf sync`. Text outside the blocks, unknown frontmatter keys, `verified` and `notes_baseline` are human-owned and preserved; `sync` never advances `notes_baseline` of a page with hand-written Notes, so a code change cannot be waved through by regenerating.
> * The generator never mints `verified`, and never writes a timestamp: `generated` carries only `by: process:eija-okf-sync`. Trust tier is therefore *unverified* until a person or process records a verification with an explicit time.
> * The gate has five checks: conformance, links, code links (STALE and NOTES_STALE), coverage and drift. `nox -s okf_structure` (tag `fast`) runs only conformance and links; `nox -s okf` (tags `full`, `release`) runs all five, so other lanes' code edits do not turn the fast tier red and the integrating lane runs `sync` once. It is stricter than the specification in one deliberate way: OKF tolerates broken cross-links because knowledge may be not-yet-written, but here a broken link almost always means a rename that a reader will trip over, and every page is generated, so an unresolved link is a defect rather than a placeholder. The root `index.md` and `log.md` are also required, not optional.
> * Coverage: every public domain and application symbol (functions, classes, public methods, constants and aliases), module, ADR (including each POC decision in ADR-0000), ubiquitous-language term, bounded context, acceptance criterion, gate and lane has a page.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://quality/okf/codelink.py`
<!-- okf:generated:end facts -->

## Notes

Hash methods and STALE semantics are decided separately in [ADR-0046](/adrs/0046-code-link-hash-methods-and-stale-semantics.md). Operating guide: `repo://docs/knowledge-base.md`.

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0000: v0.2 proof-of-concept decision log (ADR-001 … ADR-014)](/adrs/0000-poc-decision-log.md) - These fourteen decisions shipped with EIJA Studio 0.2.0 and are kept verbatim as one log.
* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0046: Code-link hash methods and STALE semantics](/adrs/0046-code-link-hash-methods-and-stale-semantics.md) - ADR-0045 links wiki pages to code with content hashes.

## Referenced by

* [ADR-0046: Code-link hash methods and STALE semantics](/adrs/0046-code-link-hash-methods-and-stale-semantics.md) - ADR-0045 links wiki pages to code with content hashes.
* [ADR-0097: Impact, ranking and evidence-status mathematics: fixed points, integer relevance, greedy selection, count vectors, and no confidence percentage](/adrs/0097-weave-impact-ranking-math.md) - The weave graph must answer six questions about a change: what does it affect, what should an agent or a person read, which tests give the cheapest useful re-c…
* [Knowledge base: OKF v0.2 wiki deterministically linked to code](/lanes/0045-knowledge-base-okf-v0-2-wiki.md) - Capability lane with ADR numbers 0045–0046 reserved.
<!-- okf:generated:end links -->
