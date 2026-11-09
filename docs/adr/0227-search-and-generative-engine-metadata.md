# ADR-0227: Search and generative-engine metadata for the repository and docs

* Status: accepted
* Date: 2026-11-09
* Lane: docs / discoverability

## Context and problem statement

People and AI assistants find PlayIDE through GitHub, PyPI-style package metadata and the MkDocs site. The package description still called it a "bounded workflow POC", the docs site was titled with the old name and had no social-card or structured metadata, and nothing summarised the project for generative engines. The docs site is not hosted yet (ADR-0017), so there is no canonical public URL.

## Decision drivers

* Truthful claims: every summary keeps the README's boundaries (local preview, offline chat, unfinished live AI creation).
* No paid service, no hosting decision taken on the owner's behalf.
* Reuse the theme's own extension point instead of a plugin.

## Considered options

* mkdocs-material `custom_dir` override adding Open Graph, Twitter and JSON-LD tags (chosen).
* mkdocs-material social plugin: needs Cairo system libraries and generated images; deferred until the site is hosted.
* Hand-written `<head>` per page: drifts.

## Decision outcome

* `pyproject.toml` carries a plain description, keywords, classifiers and `[project.urls]`.
* `llms.txt` (repository root, copied to `docs/llms.txt` so the site serves it at `/llms.txt`) follows the llmstxt.org layout: one summary, key facts with limits, then links.
* `overrides/main.html` adds Open Graph and Twitter tags on every page, and a `SoftwareApplication` JSON-LD block on the home page. Absolute tags (`og:url`, `og:image`, large card) are emitted only once `site_url` is set.
* `docs/robots.txt` allows everything; a `Sitemap:` line is added when the site has a URL.
* `mkdocs.yml` `extra.version` must equal the package version; `scripts/check_community_files.py` checks it, and that the two `llms.txt` copies are identical.

### Consequences

* When the site is hosted, set `site_url` in `mkdocs.yml` and add the `Sitemap:` line to `docs/robots.txt`. Canonical links, absolute sitemap entries and image cards then appear without template changes.
* Repository description and topics on GitHub are set in the repository settings, not in files.
