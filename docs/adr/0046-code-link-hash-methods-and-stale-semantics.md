# ADR-0046: Code-link hash methods and STALE semantics

* Status: proposed
* Date: 2026-09-28
* Lane: okf

## Context and problem statement

[ADR-0045](0045-okf-knowledge-base-linked-to-code.md) links wiki pages to code with content hashes. A raw file hash would stale every page on every whitespace edit, and a coarse one would stale nothing that matters. The hash method decides what "the code the page describes changed" means, so it is a design decision with consequences for reviewers.

## Decision drivers

* Formatting, comments and line endings (CRLF checkouts) must not stale a page.
* A change to logic, a literal, a guard, a signature or a docstring must stale it: docstrings carry invariants.
* Editing one function must not stale its siblings.
* Hashes must be stable across Python 3.11 to 3.13 for the same program text. This is evidence, not a proof: on 2026-09-29 all 182 committed source hashes were recomputed under CPython 3.11.15, 3.12.10 and 3.13.12 with no mismatch (`quality/okf/crosscheck.py`, exercised by `nox -s okf_tools`; a missing interpreter reports NOT_RUN).
* A refactor inside a private helper (a CAS check in `Studio._case`) must stale the public symbols that depend on it, not pass silently.

## Considered options

* Whole-file SHA-256 for everything: simple, far too noisy.
* `ast.dump` of the symbol: not stable across Python versions (fields are added or omitted), so committed hashes would break on an interpreter upgrade.
* A canonical JSON form of the AST built with `ast.iter_fields`, dropping positions, empty lists and `None` fields, hashed with SHA-256 (chosen).

## Decision outcome

Chosen option: canonical AST JSON with named methods, recorded per source in `hash_method`:

| Method | Names | Normalisation |
|---|---|---|
| `ast-v1` | (legacy; still verifiable) | the symbol's own canonical AST, docstring included; private helpers are NOT hashed |
| `ast-v2` | function, method, module-level constant, nox session | `ast-v1` plus the same-module private helpers the symbol reaches, transitively: module-level `_name` functions, classes and assignments, and `self._method` / `cls._method` of its own class. Static, by name |
| `ast-sig-v1` | class | signature view: bases, decorators, fields with annotations and defaults, public method signatures; bodies excluded (method pages carry the bodies) |
| `ast-api-v1` | module | public symbols' signature view plus module docstring, sorted by name; private names excluded |
| `lf-sha256-v1` | whole file | UTF-8 with CRLF folded to LF |
| `csv-row-v1` | acceptance row | canonical JSON of the row, addressed by first column |
| `md-bold-term-v1` | ubiquitous-language term | term and whitespace-normalised definition |
| `md-table-row-v1` | table row | cell texts, addressed by the slug of any cell |

Semantics:

* A page is **STALE** when a recorded hash no longer matches the current source. The gate fails and lists the pages to review.
* `sync` re-baselines the machine-owned parts (hashes, generated blocks) but does **not** advance `notes_baseline`, the source state a page's hand-written `## Notes` were last aligned to. A page with curated Notes whose sources moved on therefore stays red as **NOTES_STALE** after `sync`, and only `python -m quality.okf review <page> --by <actor> --at <ISO-8601>` clears it. `review` refuses a page whose sources changed since baseline, validates `--by` and `--at` before writing, stays inside the bundle, and never reads a clock. Pages without hand-written Notes follow their sources. A curated page with no baseline is seeded once by `sync`; deleting the key to silence the gate is a visible diff, not a technical barrier.
* `verified` entries are append-only history, each bound to `notes_sha256` (the text outside generated blocks) and `sources_sha256` at review time. An entry counts toward the trust tier only while both still match, so rewriting the prose or moving the code drops the page to unverified without deleting history. The actor is a **self-declared label**: nothing authenticates `human:<id>`, and the tool cannot tell a person from an agent typing `human:`. Agents must record `process:<id>`. Restricting `human:` to an owner allow-list is an open owner decision.
* Hashing is **per source**. A page's hash covers its own symbol (`ast-v2`: plus private helpers it reaches); a class page covers signatures only; module pages of adapters and interfaces cover public signatures only. Public callees, other modules, adapter bodies and dependency edges do not propagate staleness.
* A page whose source disappeared is marked `status: deprecated` by `sync` and kept (OKF section 5.4), exempt from resolution and staleness checks. Deleting it is a human decision.
* Method identifiers are versioned. Changing a normalisation is a new method name plus a full re-baseline, never a silent edit.

### Consequences

* Good: reformatting never stales a page; a one-character logic change does; a signature or docstring change stales the symbol and its module page; the unrelated sibling stays fresh.
* Good: hashes survive an interpreter upgrade unless the AST of the same text genuinely changes shape.
* Bad: a hash cannot say *what* changed or whether the page is still right; the reviewer must read the diff. The gate output names the source URI and both hash prefixes.
* Bad: the guarantee is narrower than "a page cannot describe moved code". A body change in a public callee, a class's private methods (class pages), or an adapter's function body does not stale the page that mentions it. `nox -s okf` green means: hashed sources unchanged since baseline, curated Notes re-read since then, generated content in sync.
* Bad: `review` records a claim by a self-declared actor; the audit trail is the git diff of the page, not authentication.
* Bad: renames appear as one deprecated page and one new page, not as a move.
* Revisit when: a Python release changes the AST of unchanged text (add `ast-v3`), reviewers want a semantic diff in the STALE report, or the owner wants an authenticated reviewer identity.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| stdlib `ast` | Adopted; only the canonical serialisation is EIJA code. | none needed |
| [griffe](https://github.com/mkdocstrings/griffe) | Extracts API signatures well but does not hash bodies or produce a version-stable canonical form. | could supply `ast-api-v1` inputs later |
| [libcst](https://github.com/Instagram/LibCST) | Preserves formatting, which is the opposite of what a normalised hash needs. | none |
