---
type: Architecture Decision Record
title: 'ADR-0046: Code-link hash methods and STALE semantics'
description: ADR-0045 links wiki pages to code with content hashes.
resource: repo://docs/adr/0046-code-link-hash-methods-and-stale-semantics.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0046-code-link-hash-methods-and-stale-semantics.md
  title: 0046-code-link-hash-methods-and-stale-semantics.md
  hash_method: lf-sha256-v1
  sha256: 2522b69d5a5e8fe711fbcd09e495915f57ba52bd0cbe09fceff063252422b422
---

# ADR-0046: Code-link hash methods and STALE semantics

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-28 |
| Lane | okf |
| Source | `repo://docs/adr/0046-code-link-hash-methods-and-stale-semantics.md` |

## Decision outcome (verbatim)

> Chosen option: canonical AST JSON with named methods, recorded per source in `hash_method`:
>
> | Method | Names | Normalisation |
> |---|---|---|
> | `ast-v1` | function, method, module-level constant | full canonical AST, docstring included |
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
> * `sync` re-baselines hashes and **drops `verified`** on any page whose source hash changed, because a verification only holds for the content it confirmed. The trust tier falls back to unverified until someone reviews the page and records `python -m quality.okf review <page> --by human:<id> --at <ISO-8601>`. `review` refuses a page whose sources changed since baseline. It never reads a clock; the time is an argument.
> * A page whose source disappeared is marked `status: deprecated` by `sync` and kept (OKF section 5.4), exempt from resolution and staleness checks. Deleting it is a human decision.
> * Method identifiers are versioned. Changing a normalisation is a new method name plus a full re-baseline, never a silent edit.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)
<!-- okf:generated:end facts -->

## Notes

The normalisation lives in `repo://quality/okf/codelink.py` (`canon`, `digest`); its tests, `repo://quality/okf/tests/test_okf_codelink.py`, show what does and does not change a hash.

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0045: An OKF v0.2 knowledge base deterministically linked to code](/adrs/0045-okf-knowledge-base-linked-to-code.md) - Humans and agents need a place to start reading EIJA that is smaller than the repository and does not go stale.

## Referenced by

* [ADR-0045: An OKF v0.2 knowledge base deterministically linked to code](/adrs/0045-okf-knowledge-base-linked-to-code.md) - Humans and agents need a place to start reading EIJA that is smaller than the repository and does not go stale.
* [Knowledge base: OKF v0.2 wiki deterministically linked to code](/lanes/0045-knowledge-base-okf-v0-2-wiki.md) - Capability lane with ADR numbers 0045–0046 reserved.
<!-- okf:generated:end links -->
