# Knowledge base (OKF v0.2 wiki linked to code)

`okf/` is an internal wiki in [Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md): a directory of markdown files with YAML frontmatter, readable with `cat` and consumable by any agent. Start at [okf/index.md](../okf/index.md). Decisions: [ADR-0045](adr/0045-okf-knowledge-base-linked-to-code.md) and [ADR-0046](adr/0046-code-link-hash-methods-and-stale-semantics.md).

The specification moved from `GoogleCloudPlatform/knowledge-catalog/okf` to `GoogleCloudPlatform/open-knowledge-format`; both copies of `SPEC.md` were byte-identical when checked (SHA-256 `26aa5da029278939f914e578107242d9607d4f2dc5fe153272b82f9ed1030101`). The bundle declares `okf_version: "0.2"` in its root `index.md`.

## What is in the bundle

| Directory | Concept `type` | Generated from |
|---|---|---|
| `language/` | Ubiquitous Language Term | `**Term:**` paragraphs of the ubiquitous-language section in `docs/architecture/ARCHITECTURE.md` |
| `contexts/` | Bounded Context | the context-map table in the same file |
| `modules/<layer>/` | Module | `src/eija_studio/{domain,application,adapters,interfaces}/*.py` and `bootstrap.py` |
| `symbols/<layer>/<module>/` | Function, Class, Method, Constant, Type Alias | public symbols of the domain and application layers (and public methods of their non-Protocol classes) |
| `adrs/`, `adrs/poc/` | Architecture Decision Record | each `docs/adr/NNNN-*.md`, and each ADR-001..014 row of the POC decision log |
| `requirements/` | Acceptance Criterion | rows of `docs/verification/ACCEPTANCE_MATRIX.csv` |
| `verification/` | Verification Technique | the ADR-0018 portfolio table, plus the one technique the kernel implements today |
| `gates/` | Quality Gate | `@nox.session` functions in `quality/sessions/*.py` |
| `lanes/` | Capability Lane | the reserved-numbers table in `docs/adr/README.md` |

## How a page is linked to code

```yaml
type: Function
title: domain.policy.check_policy
resource: repo://src/eija_studio/domain/policy.py#check_policy
status: stable
generated: {by: process:eija-okf-sync}      # no timestamp: output is reproducible
sources:
  - resource: repo://src/eija_studio/domain/policy.py#check_policy
    hash_method: ast-v1                     # how the source is normalised before hashing
    sha256: 8761653b...                     # baseline; the gate recomputes it from the code
```

* `repo://<path>[#<fragment>]` names a file or one thing in it (a python symbol such as `Studio.approve`, a CSV row id, a term or a table row).
* `sources[].sha256` and `hash_method` are extensions of the `sources` entry; OKF permits extra keys. Methods are listed in [ADR-0046](adr/0046-code-link-hash-methods-and-stale-semantics.md). Python is hashed as a canonical AST, so comments, formatting and CRLF never stale a page while a changed literal, guard, signature or docstring does.
* `verified` is never written by the generator. Trust tier (SPEC section 5.3) is *unverified* until `python -m quality.okf review <page> --by human:<id> --at <ISO 8601>` records a verification; `review` refuses a page whose sources changed since baseline.

## Who owns what on a page

| Part | Owner | Regenerated |
|---|---|---|
| `type`, `title`, `description`, `resource`, `tags`, `status`, `generated`, `sources` | machine | yes |
| text between `<!-- okf:generated:begin NAME -->` and `<!-- okf:generated:end NAME -->` (`facts`, `links`) | machine | yes |
| everything else in the body, notably `## Notes` | human | never touched |
| `description_override`, any other unknown frontmatter key | human | preserved; `description_override` replaces `description` (use it where the source has no docstring) |
| `verified` | human or process | preserved while every source hash is unchanged, dropped when one changes |
| `index.md` files | machine | yes |
| `log.md` | human | created once, never rewritten |

`links` blocks contain generated cross-references (`Depends on`, `Realised in code`, `Referenced by`, ...). Depends-on edges come from static name references in the symbol's AST that resolve to another public symbol; this is not a call graph.

## Commands

```bash
python -m quality.okf sync                    # regenerate machine-owned content and indexes (idempotent)
python -m quality.okf check                   # the gate; exit 1 on any finding
python -m quality.okf check --only codelinks  # one of: conformance, links, codelinks, coverage, drift
python -m quality.okf review symbols/domain/policy/check_policy.md --by human:alice --at 2026-09-28T09:00:00Z
nox -s okf                                    # the gate; tags: fast, full
nox -s okf_tools                              # tests of the tooling (quality/okf/tests); tag: full
pip install -e ".[okf]"                       # python-frontmatter, PyYAML, markdown-it-py (pinned)
```

## The gate

| Check | Fails when | Stricter than the spec? |
|---|---|---|
| conformance | a concept has no parseable frontmatter or an empty `type`; `index.md` has frontmatter other than the root `okf_version: "0.2"`, no section or no `* [Title](url)` entries; `log.md` has a non-ISO or out-of-order date; an optional family is malformed (`status`, `generated.by`, `verified`, timestamps without offset, duplicate `sources[].id`, dangling footnotes) | root `index.md` and `log.md` are required |
| links | a markdown link does not resolve to a page (or an existing repository path when it leaves the bundle), or a `repo://` mention does not resolve | yes: the spec tolerates broken links because knowledge may be not-yet-written; every page here is generated, so a broken link is a defect. Links inside code spans and fences are not links. Anchors (`#heading`) are not checked |
| codelinks | a `resource` does not resolve, or a source lacks a hash, or **STALE**: the source changed since the page was baselined. The report lists the pages to review | yes |
| coverage | a public domain/application symbol, module, ADR, POC decision, term, context, acceptance row, gate, lane or verification technique has no page, or its page's `resource` differs | yes |
| drift | regenerating the bundle would change any file (a hand-edited generated block, a missing index entry, a stale hash) | yes |

A pass establishes that the wiki is well-formed, navigable and was baselined against the current code. It does not establish that any page's prose is correct, that the code is correct, or that a person reviewed a page (see the trust-tier counts in the report).

## Workflow

1. Change code, an ADR, the acceptance matrix or a nox session.
2. `nox -s okf` fails with STALE (existing pages), MISSING_PAGE (new symbol, ADR or gate) or DRIFT.
3. Read each listed page against the diff and update the `## Notes` prose.
4. `python -m quality.okf sync`. Pages whose source changed lose any `verified` entry. Pages for vanished sources become `status: deprecated` and stay for history; delete them by hand when the history is unwanted.
5. Optionally record a review with `python -m quality.okf review`.
6. Commit code and `okf/` together.

Adding a new concept kind means adding an extractor in `quality/okf/extract.py` (and, if it needs a new normalisation, a new versioned hash method in `codelink.py` with a test that shows what does and does not change the hash).

## Limits

* The generated `Signature` rows use `ast.unparse`, which can differ across Python minor versions for unusual syntax; hashes do not use it.
* Symbol pages cover the domain and application layers only. Adapters and interfaces have module pages.
* Type-alias versus constant is a naming heuristic (ALL_CAPS is a constant).
* Static name references miss dynamic dispatch, and a name shared by several symbols is not resolved.
