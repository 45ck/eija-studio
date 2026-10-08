# ADR-0045: An OKF v0.2 knowledge base deterministically linked to code

* Status: proposed
* Date: 2026-09-28
* Lane: okf

## Context and problem statement

Humans and agents need a place to start reading EIJA that is smaller than the repository and does not go stale. A hand-written wiki drifts from the code silently: a page keeps describing a guard that was removed. The kernel already refuses to trust unchecked labels (evidence is recomputed, diagrams are generated), so its documentation should meet the same standard. The wiki also has to be consumable by retrieval agents without bespoke tooling.

## Decision drivers

* A page must be *falsifiable against code*: when the code it describes changes, something fails.
* Identical inputs give byte-identical output, so a regeneration diff is meaningful.
* Human insight must survive regeneration; machine facts must not be hand-edited.
* No claim of correctness from a hash: a hash detects change, not truth.
* OSS first (ADR-0016): adopt the format and parsers, write only the EIJA-specific extractors.

## Considered options

* Hand-written markdown wiki with a link checker.
* API documentation generators ([pdoc](https://github.com/mitmproxy/pdoc), [mkdocstrings](https://github.com/mkdocstrings/mkdocstrings), Sphinx autodoc): render code, but carry no trust, provenance or freshness signals and no concept model for ADRs, terms or requirements.
* [Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md) bundle, generated and gated by EIJA-specific tooling. The specification originated in `GoogleCloudPlatform/knowledge-catalog/okf`, which now points to this repository as the canonical home; the two copies of `SPEC.md` are byte-identical (SHA-256 `26aa5da0...1030101`, canonical repository commit `ad30107c`, checked 2026-09-28).
* OKF v0.1 profiles such as Calvin Ops and ProofMap Lite `okf/`: same idea, without `sources`, `generated`, `verified` or `status`, so no machine-readable provenance or lifecycle.

## Decision outcome

Chosen option: "OKF v0.2 bundle at `okf/`, generated from code and gated by `nox -s okf`", because v0.2 makes provenance, trust and lifecycle first-class frontmatter, which is exactly what code linkage needs, and it is plain markdown that any agent can read.

How the linkage works:

* `resource` is a stable `repo://<path>[#<fragment>]` URI. `sources[]` entries carry `hash_method` and `sha256` of the normalised thing they describe (details and normalisation in [ADR-0046](0046-code-link-hash-methods-and-stale-semantics.md)).
* Machine-owned frontmatter and `okf:generated` blocks are rewritten by `python -m quality.okf sync`. Text outside the blocks, unknown frontmatter keys, `verified` and `notes_baseline` are human-owned and preserved; `sync` never advances `notes_baseline` of a page with hand-written Notes, so a code change cannot be waved through by regenerating.
* The generator never mints `verified`, and never writes a timestamp: `generated` carries only `by: process:eija-okf-sync`. Trust tier is therefore *unverified* until a person or process records a verification with an explicit time.
* The gate has five checks: conformance, links, code links (STALE and NOTES_STALE), coverage and drift. `nox -s okf_structure` (tag `fast`) runs only conformance and links; `nox -s okf` (tags `full`, `release`) runs all five, so other lanes' code edits do not turn the fast tier red and the integrating lane runs `sync` once. It is stricter than the specification in one deliberate way: OKF tolerates broken cross-links because knowledge may be not-yet-written, but here a broken link almost always means a rename that a reader will trip over, and every page is generated, so an unresolved link is a defect rather than a placeholder. The root `index.md` and `log.md` are also required, not optional.
* Coverage: every public domain and application symbol (functions, classes, public methods, constants and aliases), module, ADR (including each POC decision in ADR-0000), ubiquitous-language term, bounded context, acceptance criterion, gate and lane has a page.

### Consequences

* Good: a refactor that changes a guard, role, effect or signature of a symbol (or of a same-module private helper it uses) fails `nox -s okf` and names the pages to review; retrieval starts at `okf/index.md`; the wiki doubles as the raw material for diagrams and demos because every concept has a stable URI.
* Good: nothing in the bundle claims correctness it cannot back. A green gate means well-formed, navigable, baselined against today's code and, for curated pages, re-read since the linked source last changed.
* Bad: detection of "the code moved on" is per linked source. Public callees, private methods of a class page, adapter bodies and dependencies do not stale a page (see ADR-0046). Planned techniques and NOT_RUN criteria carry their status in each page's `description`, so the index cannot read as fact.
* Bad: every new public symbol, ADR, lane or nox session needs `python -m quality.okf sync` (a coverage failure tells you), and pages whose linked source changed need a re-read and `review`. AGENTS.md tells lanes to commit the resulting `okf/` changes in their own PR, or the integrating lane to do so once after merging; `okf/` is therefore a shared, generated directory.
* Bad: a whole-class hash would be noisy, so class pages use a signature view and method pages carry the bodies; the split is a heuristic to tune.
* Revisit when: pages routinely go STALE for edits that do not change meaning (tighten the normalisation), or a consumer needs `stale_after` or attested computations (not used today).

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| [PyYAML](https://github.com/yaml/pyyaml) | Adopted for parsing (`safe_load`) and writing (`safe_dump` with a fixed key order, so output is reproducible). The `---` split and the marker-preserving merge are EIJA code. [python-frontmatter](https://github.com/eyeseast/python-frontmatter) was evaluated and dropped: here it only wrapped `yaml.load`. | none needed |
| [markdown-it-py](https://github.com/executablebooks/markdown-it-py) | Adopted for link extraction, so links in code spans and fences are not mistaken for links. | none needed |
| stdlib `ast` | Adopted for symbol resolution and hashing. [griffe](https://github.com/mkdocstrings/griffe) resolves symbols but offers no normalised content hash and adds a dependency for one lookup. | swap the resolver behind `quality/okf/codelink.py` |
| OKF `reference_agent` (open-knowledge-format) | It is an agent package that requires `google-adk` and `google-cloud-bigquery`; it is not a library for validating or linking a code bundle. | reuse its index conventions only, by reading the spec |
| EIJA-specific: `quality/okf/` (extractors, hash methods, gate) | No OSS tool links OKF concepts to Python symbols with normalised hashes. | remains custom; the format is not |
