# ADR-0046: Code-link hash methods and STALE semantics

* Status: accepted
* Date: 2026-09-28
* Lane: okf

## Context and problem statement

[ADR-0045](0045-okf-knowledge-base-linked-to-code.md) links wiki pages to code with content hashes. A raw file hash would stale every page on every whitespace edit, and a coarse one would stale nothing that matters. The hash method decides what "the code the page describes changed" means, so it is a design decision with consequences for reviewers.

## Decision drivers

* Formatting, comments and line endings (CRLF checkouts) must not stale a page.
* A change to logic, a literal, a guard, a signature or a docstring must stale it: docstrings carry invariants.
* Editing one function must not stale its siblings.
* Hashes must be stable across Python 3.11 to 3.13 for the same program text.

## Considered options

* Whole-file SHA-256 for everything: simple, far too noisy.
* `ast.dump` of the symbol: not stable across Python versions (fields are added or omitted), so committed hashes would break on an interpreter upgrade.
* A canonical JSON form of the AST built with `ast.iter_fields`, dropping positions, empty lists and `None` fields, hashed with SHA-256 (chosen).

## Decision outcome

Chosen option: canonical AST JSON with named methods, recorded per source in `hash_method`:

| Method | Names | Normalisation |
|---|---|---|
| `ast-v1` | function, method, module-level constant | full canonical AST, docstring included |
| `ast-sig-v1` | class | signature view: bases, decorators, fields with annotations and defaults, public method signatures; bodies excluded (method pages carry the bodies) |
| `ast-api-v1` | module | public symbols' signature view plus module docstring, sorted by name; private names excluded |
| `lf-sha256-v1` | whole file | UTF-8 with CRLF folded to LF |
| `csv-row-v1` | acceptance row | canonical JSON of the row, addressed by first column |
| `md-bold-term-v1` | ubiquitous-language term | term and whitespace-normalised definition |
| `md-table-row-v1` | table row | cell texts, addressed by the slug of any cell |

Semantics:

* A page is **STALE** when a recorded hash no longer matches the current source. The gate fails and lists the pages to review.
* `sync` re-baselines hashes and **drops `verified`** on any page whose source hash changed, because a verification only holds for the content it confirmed. The trust tier falls back to unverified until someone reviews the page and records `python -m quality.okf review <page> --by human:<id> --at <ISO-8601>`. `review` refuses a page whose sources changed since baseline. It never reads a clock; the time is an argument.
* A page whose source disappeared is marked `status: deprecated` by `sync` and kept (OKF section 5.4), exempt from resolution and staleness checks. Deleting it is a human decision.
* Method identifiers are versioned. Changing a normalisation is a new method name plus a full re-baseline, never a silent edit.

### Consequences

* Good: reformatting never stales a page; a one-character logic change does; a signature or docstring change stales the symbol and its module page; the unrelated sibling stays fresh.
* Good: hashes survive an interpreter upgrade unless the AST of the same text genuinely changes shape.
* Bad: a hash cannot say *what* changed or whether the page is still right; the reviewer must read the diff. The gate output names the source URI and both hash prefixes.
* Bad: renames appear as one deprecated page and one new page, not as a move.
* Revisit when: a Python release changes the AST of unchanged text (add `ast-v2`), or reviewers want a semantic diff in the STALE report.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| stdlib `ast` | Adopted; only the canonical serialisation is EIJA code. | none needed |
| [griffe](https://github.com/mkdocstrings/griffe) | Extracts API signatures well but does not hash bodies or produce a version-stable canonical form. | could supply `ast-api-v1` inputs later |
| [libcst](https://github.com/Instagram/LibCST) | Preserves formatting, which is the opposite of what a normalised hash needs. | none |
