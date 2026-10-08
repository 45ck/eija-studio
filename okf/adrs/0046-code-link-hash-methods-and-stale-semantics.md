---
type: Architecture Decision Record
title: 'ADR-0046: Code-link hash methods and STALE semantics'
description: ADR-0045 links wiki pages to code with content hashes.
resource: repo://docs/adr/0046-code-link-hash-methods-and-stale-semantics.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0046-code-link-hash-methods-and-stale-semantics.md
  title: 0046-code-link-hash-methods-and-stale-semantics.md
  hash_method: lf-sha256-v1
  sha256: 4098c2873d594aa5e80a52efc4dc816b04e0896276c94370c86812c9f435f2cb
notes_baseline: 3b67866bdfcb9920ee04d87f358797b5933c3979fa0757426c4fa4ad6047cd70
verified:
- by: process:eija-okf-lane-fix
  at: '2026-09-28T23:24:05Z'
  notes_sha256: bdf401d9ecaaa59a7cb306f7babc53f26e4ada5773303ace614ddbcab44d046a
  sources_sha256: 3b67866bdfcb9920ee04d87f358797b5933c3979fa0757426c4fa4ad6047cd70
---

# ADR-0046: Code-link hash methods and STALE semantics

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed |
| Date | 2026-09-28 |
| Lane | okf |
| Source | `repo://docs/adr/0046-code-link-hash-methods-and-stale-semantics.md` |

## Decision outcome (verbatim)

> Chosen option: canonical AST JSON with named methods, recorded per source in `hash_method`:
>
> | Method | Names | Normalisation |
> |---|---|---|
> | `ast-v1` | (legacy; still verifiable) | the symbol's own canonical AST, docstring included; private helpers are NOT hashed |
> | `ast-v2` | function, method, module-level constant, nox session | `ast-v1` plus the same-module private helpers the symbol reaches, transitively: module-level `_name` functions, classes and assignments, and `self._method` / `cls._method` of its own class. Static, by name |
> | `ast-sig-v1` | class | signature view: bases, decorators, fields with annotations and defaults, public method signatures; bodies excluded (method pages carry the bodies) |
> | `ast-api-v1` | module | public symbols' signature view plus module docstring, sorted by name; private names excluded |
> | `lf-sha256-v1` | whole file | UTF-8 with CRLF folded to LF |
> | `csv-row-v1` | acceptance row | canonical JSON of the row, addressed by first column |
> | `md-bold-term-v1` | ubiquitous-language term | term and whitespace-normalised definition |
> | `md-table-row-v1` | table row | cell texts, addressed by the slug of any cell |
>
> Semantics:
>
> * A page is **STALE** when a recorded hash no longer matches the current source. The gate fails and lists the pages to review.
> * `sync` re-baselines the machine-owned parts (hashes, generated blocks) but does **not** advance `notes_baseline`, the source state a page's hand-written `## Notes` were last aligned to. A page with curated Notes whose sources moved on therefore stays red as **NOTES_STALE** after `sync`, and only `python -m quality.okf review <page> --by <actor> --at <ISO-8601>` clears it. `review` refuses a page whose sources changed since baseline, validates `--by` and `--at` before writing, stays inside the bundle, and never reads a clock. Pages without hand-written Notes follow their sources. A curated page with no baseline is seeded once by `sync`; deleting the key to silence the gate is a visible diff, not a technical barrier.
> * `verified` entries are append-only history, each bound to `notes_sha256` (the text outside generated blocks) and `sources_sha256` at review time. An entry counts toward the trust tier only while both still match, so rewriting the prose or moving the code drops the page to unverified without deleting history. The actor is a **self-declared label**: nothing authenticates `human:<id>`, and the tool cannot tell a person from an agent typing `human:`. Agents must record `process:<id>`. Restricting `human:` to an owner allow-list is an open owner decision.
> * Hashing is **per source**. A page's hash covers its own symbol (`ast-v2`: plus private helpers it reaches); a class page covers signatures only; module pages of adapters and interfaces cover public signatures only. Public callees, other modules, adapter bodies and dependency edges do not propagate staleness.
> * A page whose source disappeared is marked `status: deprecated` by `sync` and kept (OKF section 5.4), exempt from resolution and staleness checks. Deleting it is a human decision.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://quality/okf/crosscheck.py`
<!-- okf:generated:end facts -->

## Notes

The normalisation lives in `repo://quality/okf/codelink.py` (`canon`, `digest`); its tests, `repo://quality/okf/tests/test_okf_codelink.py`, show what does and does not change a hash. `ast-v2` adds same-module private helpers to a symbol's hash; `repo://quality/okf/crosscheck.py` recomputes the committed hashes under another interpreter. `sync` never clears NOTES_STALE and the `human:` actor is self-declared: both are stated in the decision above, not just here.

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0045: An OKF v0.2 knowledge base deterministically linked to code](/adrs/0045-okf-knowledge-base-linked-to-code.md) - Humans and agents need a place to start reading EIJA that is smaller than the repository and does not go stale.

## Referenced by

* [ADR-0045: An OKF v0.2 knowledge base deterministically linked to code](/adrs/0045-okf-knowledge-base-linked-to-code.md) - Humans and agents need a place to start reading EIJA that is smaller than the repository and does not go stale.
* [Knowledge base: OKF v0.2 wiki deterministically linked to code](/lanes/0045-knowledge-base-okf-v0-2-wiki.md) - Capability lane with ADR numbers 0045–0046 reserved.
<!-- okf:generated:end links -->
