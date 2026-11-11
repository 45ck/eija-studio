---
type: Architecture Decision Record
title: 'ADR-0227: Search and generative-engine metadata for the repository and docs'
description: People and AI assistants find PlayIDE through GitHub, PyPI-style package metadata and the MkDocs site.
resource: repo://docs/adr/0227-search-and-generative-engine-metadata.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0227-search-and-generative-engine-metadata.md
  title: 0227-search-and-generative-engine-metadata.md
  hash_method: lf-sha256-v1
  sha256: 509b55a6e7695dd83338b7a9cc7ca94dfcf71ab7f6c13691f5966165718d3267
notes_baseline: 5330ac46fbddd94b0e78f61b7580a1382674f130b1c30c849914c237b51ec356
---

# ADR-0227: Search and generative-engine metadata for the repository and docs

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-09 |
| Lane | docs / discoverability |
| Source | `repo://docs/adr/0227-search-and-generative-engine-metadata.md` |

## Decision outcome (verbatim)

> * `pyproject.toml` carries a plain description, keywords, classifiers and `[project.urls]`.
> * `llms.txt` (repository root, copied to `docs/llms.txt` so the site serves it at `/llms.txt`) follows the llmstxt.org layout: one summary, key facts with limits, then links.
> * `overrides/main.html` adds Open Graph and Twitter tags on every page, and a `SoftwareApplication` JSON-LD block on the home page. Absolute tags (`og:url`, `og:image`, large card) are emitted only once `site_url` is set.
> * `docs/robots.txt` allows everything; a `Sitemap:` line is added when the site has a URL.
> * `mkdocs.yml` `extra.version` must equal the package version; `scripts/check_community_files.py` checks it, and that the two `llms.txt` copies are identical.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://pyproject.toml`
* `repo://scripts/check_community_files.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0017: Local quality gates with nox sessions and noslop enforcement](/adrs/0017-local-quality-gates.md) - Hosted CI was not available for this repository when this was written (September 2026).
<!-- okf:generated:end links -->
