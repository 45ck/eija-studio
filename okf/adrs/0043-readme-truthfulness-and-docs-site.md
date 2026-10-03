---
type: Architecture Decision Record
title: 'ADR-0043: The README is verifiable: generated diagrams, dated status, MkDocs Material docs site'
description: EIJA's promise is that what you see matches the code.
resource: repo://docs/adr/0043-readme-truthfulness-and-docs-site.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0043-readme-truthfulness-and-docs-site.md
  title: 0043-readme-truthfulness-and-docs-site.md
  hash_method: lf-sha256-v1
  sha256: 0578f6eb74d471d8b33d5155722144b3bd199e23ef8dce979f64bd547620891d
notes_baseline: 7ea602e3844643b10b96e21abc348800f35dd27b53503a2d4753b56e1c6c230c
---

# ADR-0043: The README is verifiable: generated diagrams, dated status, MkDocs Material docs site

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed |
| Date | 2026-09-29 |
| Lane | oss |
| Source | `repo://docs/adr/0043-readme-truthfulness-and-docs-site.md` |

## Decision outcome (verbatim)

> Chosen: MkDocs + Material, a small stdlib link checker, and a generated README region.
>
> 1. **README diagram is generated.** `scripts/gen_readme_diagram.py` imports `domain.policy`, builds `baseline()` and the `enable_recommendation` candidate, diffs the typed models, and writes Mermaid between two markers in `README.md`. Session `readme_diagram` (fast) fails when the committed text differs from a fresh render. The visual lane later replaces it with the generated diff image; a TODO comment marks the swap and no image is embedded until it exists.
> 2. **Status vocabulary.** `on main`, `open PR`, `branch pushed`, `planned`. A statement is `on main` only if a reader can reproduce it from a checkout of `main`. Status tables carry a date. Anything that needs a missing prerequisite reports `NOT_RUN`.
> 3. **Docs site.** `mkdocs.yml` builds `docs/` with the Material theme. Session `docs` (release) runs `mkdocs build --strict` and reports `NOT_RUN` when MkDocs is not installed. There is no deployment step.
> 4. **Links.** Session `docs_links` (fast) checks that relative links and heading anchors in README, community files and `docs/` resolve. Targets that another lane will create are listed in the checker's `PENDING` table, reported as pending, and never as ok. `docs_links` is the link validator: `mkdocs.yml` sets `validation.links.not_found` and `omitted_files` to `info`, because pages under `docs/` legitimately link to repository files outside the site (`../AGENTS.md`, `../evidence/`), so `mkdocs build --strict` alone cannot catch a broken link and the built site would carry those links dead if it were ever deployed. Whether every ADR is listed in the index is not checked here: the `adr_index` gate owns that (the index is generated).
> 5. **Community files** (CONTRIBUTING, CODE_OF_CONDUCT from the official Contributor Covenant 2.1 text, SECURITY, CITATION.cff, issue and PR templates) are checked by session `community_files` for presence, for version agreement between `CITATION.cff` and `pyproject.toml`, for issue forms that parse (PyYAML, pinned in the `docs` extra), and for a roadmap that covers every ADR block reserved in `docs/adr/README.md` (derived, not hard-coded). A run where PyYAML is missing prints `NOT_RUN` for the form check, exits 2 and the nox session is skipped, never green.
> 6. **Status claims.** The roadmap, the README and the lane hubs name pull requests as `open PR #n` or `merged PR #n`. `scripts/check_pr_status.py` (session `pr_status`, release tier) compares them with `gh pr list` and reports `NOT_RUN` without `gh` and network. The offline gates cannot notice a stale PR state; the date on each status table and this release-tier check are the mitigation, and the README's gate line is a dated snapshot that nothing verifies.
> 7. **Ownership.** `README.md` is edited only by the oss lane. Other lanes put their detail in `docs/` and the oss lane links to it.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://README.md`
* `repo://pyproject.toml`
* `repo://scripts/check_doc_links.py`
* `repo://scripts/check_pr_status.py`
* `repo://scripts/gen_readme_diagram.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0017: Local quality gates with nox sessions and noslop enforcement](/adrs/0017-local-quality-gates.md) - Hosted CI is not currently available for this repository.
* [ADR-0018: Formal V&V portfolio: each technique is a distinct evidence kind](/adrs/0018-formal-vv-portfolio.md) - v0.2 verifies one-step behaviour with a same-author 5×5×5 runtime matrix.
* [ADR-0019: Diagrams are generated projections of the executable model](/adrs/0019-diagrams-generated-from-executable-model.md) - Reviewers need to see what a change, usually an agent's change, does: state machines, sequences, classes, journeys and ripple effects.
* [ADR-0023: Generated UML and visual diff, with Mermaid as the primary renderer](/adrs/0023-generated-uml-and-visual-diff.md) - ADR-0019 decided that diagrams are generated projections of the executable model.

## Referenced by

* [OSS community, documentation and release](/lanes/0043-oss-community-documentation-and-release.md) - Capability lane with ADR numbers 0043–0044 reserved.
<!-- okf:generated:end links -->
