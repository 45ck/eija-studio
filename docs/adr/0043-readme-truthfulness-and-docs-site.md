# ADR-0043: The README is verifiable: generated diagrams, dated status, MkDocs Material docs site

* Status: proposed
* Date: 2026-09-29
* Lane: oss

## Context and problem statement

EIJA's promise is that what you see matches the code. A README that hand-draws its example, or that describes features from other lanes as if they had landed, breaks that promise on the first page. At the same time the project needs a front door (why use it, how an agent starts, why it can be trusted), community files, and a documentation site, while hosted CI is unavailable ([ADR-0017](0017-local-quality-gates.md)), so nothing may depend on a deployed pipeline.

## Decision drivers

* Every claim on the front page is either true on `main` or explicitly marked in progress or planned, with the evidence kind named ([ADR-0018](0018-formal-vv-portfolio.md)).
* The README's visual example must come from the executable model, as [ADR-0019](0019-diagrams-generated-from-executable-model.md) requires of all diagrams.
* OSS first ([ADR-0016](0016-oss-first-adapters-not-engines.md)): adopt a documentation generator, write only glue.
* Gates must run locally and offline-tolerant, and report `NOT_RUN` (never `PASS`) when a prerequisite is missing.
* Parallel lanes must not have to edit the README to land: the README is owned by one lane.

## Considered options

* MkDocs with Material theme, Mermaid via `pymdownx.superfences` (chosen)
* Docusaurus / VitePress / Sphinx (rejected: Node toolchain or reStructuredText for a Markdown-first Python project; Sphinx remains an option if API reference generation is wanted)
* GitHub Pages deployment workflow (rejected for now: hosted CI is unavailable; `mkdocs build --strict` runs locally as a `release` session)
* Link checking with [lychee](https://github.com/lycheeverse/lychee) or markdown-link-check (rejected for the default gate: a Rust binary or a Node toolchain for a relative-link check; the check is about 100 lines of Python; both stay documented as optional external-link checkers)
* Hand-drawn README diagram (rejected: it can disagree with the code)

## Decision outcome

Chosen: MkDocs + Material, a small stdlib link checker, and a generated README region.

1. **README diagram is generated.** `scripts/gen_readme_diagram.py` imports `domain.policy`, builds `baseline()` and the `enable_recommendation` candidate, diffs the typed models, and writes Mermaid between two markers in `README.md`. Session `readme_diagram` (fast) fails when the committed text differs from a fresh render. The visual lane later replaces it with the generated diff image; a TODO comment marks the swap and no image is embedded until it exists.
2. **Status vocabulary.** `on main`, `open PR`, `branch pushed`, `planned`. A statement is `on main` only if a reader can reproduce it from a checkout of `main`. Status tables carry a date. Anything that needs a missing prerequisite reports `NOT_RUN`.
3. **Docs site.** `mkdocs.yml` builds `docs/` with the Material theme. Session `docs` (release) runs `mkdocs build --strict` and reports `NOT_RUN` when MkDocs is not installed. There is no deployment step.
4. **Links.** Session `docs_links` (fast) checks that relative links and heading anchors in README, community files and `docs/` resolve. Targets that another lane will create are listed in the checker's `PENDING` table, reported as pending, and never as ok.
5. **Community files** (CONTRIBUTING, CODE_OF_CONDUCT from the official Contributor Covenant 2.1 text, SECURITY, CITATION.cff, issue and PR templates) are checked by session `community_files` for presence and for version agreement between `CITATION.cff` and `pyproject.toml`.
6. **Ownership.** `README.md` is edited only by the oss lane. Other lanes put their detail in `docs/` and the oss lane links to it.

### Consequences

* Good: the front page cannot silently drift from the policy model; status claims are dated and auditable; no vendor hosting or CI dependency.
* Bad: the README needs regenerating when `domain.policy` changes (the gate says so); a status table needs manual refresh (its date shows how stale it is); a `PENDING` table is a small piece of maintenance while lanes are in flight.
* Revisit when: hosted CI returns (add deployment and an external-link check), or the `PENDING` table has been empty for a release.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| lychee, markdown-link-check | Binary or Node toolchain for an offline relative-link and anchor check; MkDocs `--strict` covers only files under `docs/` | Swap `scripts/check_doc_links.py` for lychee once external-link checking is wanted |
| Mermaid CLI / PlantUML | They render diagrams; they do not know EIJA's `Workflow`. The generator only projects the model into Mermaid text | Superseded by the visual lane's generators (ADR-0023) |
