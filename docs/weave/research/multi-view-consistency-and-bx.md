# Multi-view consistency and bidirectional transformations (bx)

Research dossier `view-consistency-bx`, lane `weave`, 2026-09-29. All URLs were opened on 2026-09-29 unless marked UNVERIFIED. Evidence labels: MEASUREMENT (run in this worktree), PREDICTION (reasoned, not run).

## Decisions first

| # | Decision | Confidence |
|---|---|---|
| 1 | Model every view (diagram, journey, class page, OKF page) as an **asymmetric lens over one typed source**: the `Workflow` and its `SemanticTransaction`s. Do not build a multi-master synchroniser. | High: the kernel already has this shape (`get` = `policy.projections`, `put` = `policy.apply_transaction`). |
| 2 | A drag-and-drop canvas is a **view that reports atomic edits**. Each edit is translated by a per-view *edit translator* into `SemanticTransaction`s, `LayoutChange`s, or a typed rejection. Nothing else may reach the kernel. This is the Vitruvius contract, minus the EMF stack. | High |
| 3 | Adopt the **lens laws as executable tests** (GetPut, PutGet, conditional PutPut), not a lens library. No compatible-licence Python library exists (table 3); the law checker is about 100 lines and EIJA-specific. | High |
| 4 | Do **not** adopt eMoflon (GPL-3.0), Vitruv (EPL-1.0, Java/EMF), Sirius (EPL-2.0), Hets (GPL-2.0-or-later), CQL (non-commercial terms) or tldraw (no production use). Use them as inspiration. Revisit TGG tooling only when a trigger in section 5 fires. | Medium-high |
| 5 | Category theory (functorial migration), institutions and sheaves stay **theory-only**, each with one small concrete residue we do adopt (section 4). | High |
| 6 | Canonical JSON for anything the graph lane hashes: RFC 8785 via `rfc8785` (Apache-2.0). The kernel's `canonical()` is **not** RFC 8785 (MEASUREMENT below). | High |

## 1. Scope and method

**Question.** How do we keep many views of one system consistent, and what survives contact with a UML canvas whose edits must map to typed semantic transactions and back?

**What I did.**
- Read the repo: `domain/impact.py`, `domain/models.py` (`canonical`, `SemanticTransaction`, `LayoutChange`), `domain/policy.py`, `docs/architecture/ARCHITECTURE.md`, and the visual (ADR-0023, `docs/visual.md`), okf (`quality/okf/codelink.py`, `okf/index.md`) and agents (ADR-0041) worktrees, read-only.
- Read the owner's private `45ck/proofmap-lite` README and `docs/gap-audit.md` through the authenticated `gh` CLI.
- Opened primary sources: Foster et al. lens paper (full text, draft copy from cis.upenn.edu, via `pdftotext`), arXiv abstracts (Diskin et al., Fritsche et al., Spivak, Spivak and Wisnesky, Robinson, Hansen and Ghrist), RFC 8785, RFC 6902, OMG QVT 1.3 landing page, project pages and LICENSE files, and GitHub metadata (licence, `pushed_at`, archived) through the GitHub API.
- Ran one small experiment (section 3.8).

**What was inaccessible or limited.**
- WebSearch hit its session budget (200 of 200) before this task started. Discovery therefore used known URLs, the arXiv and Crossref APIs, and GitHub search. Recall of the literature is probably incomplete.
- Springer, ACM and Elsevier abstracts were paywalled or redirected to a cookie wall. Stevens (QVT-R, 2008; bx in the large, 2019), Czarnecki et al. (2009), Hofmann, Pierce and Wagner (symmetric and edit lenses), Atkinson et al. (orthographic modelling), Egyed (2011) and Klare et al. (Vitruvius, JSS 2021) were confirmed to exist by DOI through Crossref but **their content was not read**. Claims that would need them are UNVERIFIED (section 6).
- WebFetch summarises pages with a small model. Licences were cross-checked against LICENSE file text where the table says "text opened".

## 2. Per tool and school

### 2.1 Lenses (Foster et al.; symmetric, edit and delta lenses)

- **What.** A lens is a pair `get: C -> A` and `put: A x C -> C`. Definitions as printed in the paper ([Foster, Greenwald, Moore, Pierce, Schmitt, TOPLAS 2007](https://www.cis.upenn.edu/~bcpierce/papers/lenses-toplas-final.pdf), draft copy): **GetPut** `put(get c, c) = c`; **PutGet** `get(put(a, c)) = a`; optional **PutPut** `put(a', put(a, c)) = put(a', c)`. A well-behaved lens satisfies the first two; adding PutPut makes it *very well behaved*. Both laws hold "if both operations are defined".
- **Limits stated by the authors.** They do not require PutPut for their tree combinators because `map`, `flatten`, `merge` and conditionals fail it "for reasons that seem pragmatically unavoidable". Their examples show `put` with hidden side effects breaks GetPut, and dropping view information breaks PutGet.
- **Formal link.** [Delta lenses as coalgebras for a comonad (arXiv 2108.00390)](https://arxiv.org/abs/2108.00390) abstract: classical state-based lenses "also known as very well-behaved lenses" are algebras for a monad and coalgebras for a comonad; delta lenses generalise them.
- **Delta lenses.** [Diskin, Xiong, Czarnecki, JOT 2011](https://www.jot.fm/contents/issue_2011_01/article6.html) abstract: state-based bx hides alignment inside update propagation; they "separate concerns" into *delta discovery* (alignment) and *delta propagation*, with model spaces as categories whose arrows are deltas.
- **Multiary and reflective.** [Diskin, Koenig, Lawford (arXiv 1911.11302)](https://arxiv.org/abs/1911.11302) proposes multiary delta lenses with *reflective* updates, "when consistency restoration requires some amendment of the update that violated consistency". The author notes the journal (FAC) version has "multiple essential typos in section 7.1"; use the arXiv version.
- **Symmetric and edit lenses** ([Hofmann, Pierce, Wagner 2011](https://doi.org/10.1145/1926385.1926428), [2012](https://doi.org/10.1145/2103656.2103715)): bibliographic record verified; content not read.
- **Status and licence of implementations.** Boomerang: LGPL-2.1, last commit 2023-03-15, OCaml, string lenses ([repo](https://github.com/boomerang-lang/boomerang), [Harmony page](https://www.engineering.upenn.edu/~harmony/)). PyPI `lenses` 1.2.0 is GPLv3+ ([PyPI](https://pypi.org/pypi/lenses/json)), so it cannot be a dependency of an Apache-2.0 package we distribute.
- **Gives EIJA.** A vocabulary and three testable laws for "edit the picture, get the model, redraw the picture".
- **Cost.** Laws hold only modulo definedness. Any lossy view needs a *complement* (data the view hides) or amendments.
- **Verdict.** Adapt the laws as property tests. No library dependency.

### 2.2 Vitruvius / Vitruv (KIT), and orthographic modelling

- **What.** [Vitruv](https://github.com/vitruv-tools/Vitruv) is "a framework for view-based (software) development"; a V-SUM (Virtual Single Underlying Model, class `VirtualModel`) keeps several metamodels consistent by running `ChangePropagationSpecifications`. Consistency rules are written in the Reactions language ([Vitruv-DSLs](https://github.com/vitruv-tools/Vitruv-DSLs)) or coded against interfaces in [Vitruv-Change](https://github.com/vitruv-tools/Vitruv-Change). The [wiki](https://github.com/vitruv-tools/.github/wiki) says: "All views have to report atomic modifications of the elements that they are displaying. Based on this information, internal model instances of the involved metamodels are synchronized."
- **Status.** Active: push 2026-09-28; release v4.0.0 on 2026-06-17 (Xtend translated to Java, per release notes). Stack: Maven, EMF, Xtext, Java ([org page](https://github.com/vitruv-tools/)). There is also a web modelling UI repo, Vitruv-UI-Methodologist.
- **Licence.** EPL-1.0 (LICENSE text opened). Weak copyleft; fine as a separate tool, awkward to link into an Apache-2.0 Python package.
- **Orthographic software modelling** (Atkinson, Stoll, Bostan, [DOI](https://doi.org/10.1007/978-3-642-14819-4_15)): title and venue verified, content not read. Vitruv and OSM are both "view-based over a (virtual) single model"; that is the only claim I make.
- **Gives EIJA.** The exact contract for a canvas: views report atomic edits; consistency preservation is change-driven; there is no monolithic super-model.
- **Cost.** JVM and EMF ecosystem, metamodels in Ecore, rules in a DSL. About 16 GB shared RAM, Windows, Python kernel: poor fit.
- **Verdict.** Inspiration. Copy the contract, not the code.

### 2.3 Triple graph grammars, eMoflon, QVT-R

- **TGG.** Consistency is specified by rules that describe how to create consistent pairs of models; further rules that propagate changes in either direction are derived from them (per the Fritsche abstract below; origin: [Schürr 1995, DOI](https://doi.org/10.1007/3-540-59071-4_45), bibliographic only). [Fritsche et al. (arXiv 2005.14510)](https://arxiv.org/abs/2005.14510): restricting sync to derived rules "may lead to unnecessary deletion and recreation of model elements", which is "unnecessary information loss"; short-cut repair rules reuse elements, with termination and correctness proved and completeness "discussed", implemented in eMoflon. [Fritsche et al. (arXiv 2011.03357)](https://arxiv.org/abs/2011.03357) handles concurrent edits via a causal dependency relation. [VICToRy (arXiv 2012.01655)](https://arxiv.org/abs/2012.01655) is an interactive debugger for tolerant TGG consistency management.
- **eMoflon::IBeX.** "Eclipse-based incremental interpreter for bidirectional graph transformations based on TGGs" ([README](https://github.com/eMoflon/emoflon-ibex)). Active (push 2026-09-09). **GPL-3.0** (LICENSE text opened). Needs JDK 21+, Eclipse 2026-03, Graphviz; optional ILP solvers. **eMoflon::Neo** ([repo](https://github.com/eMoflon/emoflon-neo)) is a Neo4j-backed variant, EPL-2.0, push 2026-07-23. Neo4j itself is GPL-3.0 per GitHub metadata (licence text not opened).
- **QVT-R.** [QVT 1.3](https://www.omg.org/spec/QVT/1.3/About-QVT) (June 2016, formal) defines Relations, Operational Mappings and Core. Semantic problems reported in [Stevens (2008)](https://doi.org/10.1007/s10270-008-0109-9) were not read (UNVERIFIED); no maintained Python implementation was found.
- **Gives EIJA.** Ideas: repair-in-place instead of delete-and-recreate to limit information loss; explicit trace links keyed by stable ids (our design, inspired by TGG pairs of models, not taken from a verified TGG definition).
- **Cost.** Rules to author per view pair; GPL, Java and Eclipse toolchain.
- **Verdict.** Inspiration. Optional process only if a trigger in section 5 fires.

### 2.4 Sirius, GLSP and canvas libraries

- **Sirius** ([site](https://eclipse.dev/sirius/), [Sirius Web](https://www.eclipse.dev/sirius/sirius-web.html)): declarative viewpoint specification; Sirius Web separates a *Domain* (data) from a *View* (how it is "graphically visualized and edited") and propagates diagram edits to the semantic model. Stack: Spring, React, PostgreSQL, GraphQL. EPL-2.0 (Desktop LICENSE opened), active (push 2026-09-24 and 2026-09-28).
- **Eclipse GLSP** ([repo](https://github.com/eclipse-glsp/glsp)): "Graphical language server platform for building web-based diagram editors", modelled on the Language Server Protocol; dual EPL-2.0 or GPL-2.0 with Classpath Exception (LICENSE text opened); push 2026-09-27. Closest existing analogue of "canvas sends operations to a server that owns the model".
- **Canvas widgets.** draw.io ([jgraph/drawio](https://github.com/jgraph/drawio)): Apache-2.0, active. React Flow ([xyflow](https://github.com/xyflow/xyflow)): MIT, active. tldraw ([LICENSE.md](https://github.com/tldraw/tldraw/blob/main/LICENSE.md), text opened): permits Development Environments, and the Conditions say "Not to use the Software in Production Environments" without a licence key.
- **Verdict.** Sirius and GLSP: inspiration (the pattern "server owns semantic model; client sends typed operations"). draw.io: export target and optional editing surface. React Flow: dependency candidate for a native canvas. tldraw: reject.

### 2.5 Categorical data integration (Spivak, CQL)

- **Theory.** [Spivak, Functorial Data Migration (arXiv 1009.1166)](https://arxiv.org/abs/1009.1166): a schema is a small category, an instance a set-valued functor; a schema morphism induces three migration functors that "parameterize projections, unions, and joins". [Spivak and Wisnesky (arXiv 1212.5303)](https://arxiv.org/abs/1212.5303) gives FQL, closed under composition and equivalent to relational algebra extended with key generation (per the arXiv summary; theorem statement not read).
- **CQL.** [CategoricalData/CQL](https://github.com/CategoricalData/CQL): Java IDE, "reference implementation of David Spivak's functorial data migration". Active (last commit 2026-07-26). Conexus AI commercialises it ([site](https://categoricaldata.net/)). **Licence**, README verbatim: "BSD 3 license for non-commercial use and exploratory/evaluative commercial use; contact us for other licenses"; there is no LICENSE file in the repo root, and GitHub reports no SPDX licence. That is not an open-source licence in the OSI sense; treat it as non-commercial.
- **Gives EIJA.** The idea that a view definition is *data*: a declared mapping from semantic types to view elements that can be checked for totality.
- **Cost.** Java, a separate query language, no Python implementation, non-commercial terms.
- **Verdict.** Theory-only plus one adopted check (mapping totality). CQL is inspiration; never a dependency.

### 2.6 Institutions and Hets

- **Theory.** Goguen and Burstall, [Institutions](https://doi.org/10.1145/147508.147524) (JACM 1992; bibliographic only): abstract model theory where each logic is an institution and translations between logics are morphisms.
- **Hets** ([spechub/Hets](https://github.com/spechub/Hets)): Haskell, "parsing, static analysis, and proof management tool" for heterogeneous specifications with "logic translations as first-class citizens"; the README lists logics including MOF and QVT (the repo tree has `QVTR.hs`, `UML.hs`, `CSMOF`). "GPLv2 or higher" (README; LICENSE.txt opened). Last commit **2025-10-07**, 12 months before today; open issues 639. Maintenance is slow, not archived.
- **Gives EIJA.** A precise statement of our honesty rule: a proof in one logic (TLA+, SMT, Bend) is a statement about that model; moving it to code or UML is a separate translation with its own claim.
- **Cost.** Haskell toolchain, GPL, steep learning curve, no pay-off for a Python kernel.
- **Verdict.** Theory-only. Optional-process at most for one-off experiments.

### 2.7 Sheaf-style consistency

- **Sources.** [Robinson, Sheaves are the canonical datastructure for sensor integration (arXiv 1603.01446)](https://arxiv.org/abs/1603.01446); [Hansen and Ghrist, Toward a Spectral Theory of Cellular Sheaves (arXiv 1808.01513)](https://arxiv.org/abs/1808.01513): Hodge Laplacian on a sheaf of vector spaces over cell complexes, tied to sheaf cohomology.
- **Reading for EIJA.** Views are "local sections" over overlapping parts of the system; consistency means sections agree on overlaps; obstruction to gluing is a global inconsistency. I did not verify any theorem statement and make no theorem claim.
- **Cost.** The theory targets vector-space or cell-complex data. Our data are discrete typed records.
- **Verdict.** Theory-only. The implementable residue is a pairwise overlap join (section 4).

### 2.8 ProofMap Lite: lessons from the owner's prior attempt

Source: private repo `45ck/proofmap-lite` (README, `docs/gap-audit.md`, read through `gh`, 2026-09-29).

| Lesson | Evidence in repo | Consequence for EIJA |
|---|---|---|
| A canvas edit that lives in browser storage is not evidence | GAP-010 (draw.io XML in `localStorage`) | Canvas state must be exported to a repo file or, better, committed as typed transactions |
| Views inferred from code contradicted project boundaries | GAP-024 (interaction and ERD candidates implied autosave and DB tables) | Generate views only from typed data; hand-inferred diagrams are candidates, never truth |
| Generated timestamps caused churn; stale reports were mistaken for current ones | GAP-003, GAP-025, GAP-028 | Content-addressed artefacts, no wall-clock, hash of inputs inside every generated file |
| Warnings closed by prose | GAP-029 | A drift finding is closed only by a machine-checked artefact |
| Heuristic drift rules gave false positives and negatives | GAP-011, GAP-019, GAP-027 | Prefer exact projection hashes over heuristic "related file changed" rules |
| Model and coverage artefacts multiplied (43+ change bundles, many `.drawio` candidates) | README verification list | Fewer artefact kinds, all derived from one source; the graph is an index, not a second truth |

## 3. Options table

Licence column: "text opened" means I read the LICENSE file; otherwise GitHub SPDX metadata or a page statement. Verdicts on licences are engineering reading, not legal advice.

| Name | Licence | Status (2026-09-29) | Verdict | Why | Source |
|---|---|---|---|---|---|
| Foster et al. lens laws | paper (ACM copyright; draft copy hosted by authors) | Published 2007, foundational | inspiration | Source of GetPut, PutGet, PutPut | [PDF](https://www.cis.upenn.edu/~bcpierce/papers/lenses-toplas-final.pdf) |
| Boomerang | LGPL-2.1 | Last commit 2023-03-15, OCaml | reject | Stale, string-oriented, wrong language | [repo](https://github.com/boomerang-lang/boomerang) |
| PyPI `lenses` | GPLv3+ | 1.2.0 | reject | GPL cannot be a dependency of Apache-2.0 distribution | [PyPI](https://pypi.org/pypi/lenses/json) |
| Vitruv (+ DSLs, Change) | EPL-1.0 (text opened) | Active; v4.0.0 2026-06-17 | inspiration | Views report atomic edits; JVM/EMF stack too heavy | [repo](https://github.com/vitruv-tools/Vitruv) |
| eMoflon::IBeX | GPL-3.0 (text opened) | Active; push 2026-09-09 | inspiration (optional-process only if triggered) | TGG engine; GPL, Eclipse, JDK 21 | [repo](https://github.com/eMoflon/emoflon-ibex) |
| eMoflon::Neo | EPL-2.0 (text opened) | Push 2026-07-23; needs Neo4j (GPL-3.0 per GitHub) | inspiration | Shows TGG on a graph DB; heavy | [repo](https://github.com/eMoflon/emoflon-neo) |
| OMG QVT 1.3 | OMG spec | Formal, June 2016 | inspiration | Relations language; semantics not verified | [spec](https://www.omg.org/spec/QVT/1.3/About-QVT) |
| Sirius Desktop / Web | EPL-2.0 (text opened) | Active; pushes 2026-09-24 / 09-28 | inspiration | Domain/View split, declarative mapping | [Sirius Web](https://www.eclipse.dev/sirius/sirius-web.html) |
| Eclipse GLSP | EPL-2.0 or GPL-2.0 + Classpath Exception (text opened) | Active; push 2026-09-27 | inspiration | LSP-style protocol for diagram editors | [repo](https://github.com/eclipse-glsp/glsp) |
| draw.io | Apache-2.0 (text opened) | Active; push 2026-09-25 | export target | Editable surface; file is not truth | [repo](https://github.com/jgraph/drawio) |
| React Flow (xyflow) | MIT (text opened) | Active; push 2026-09-24 | dependency (candidate, frontend only) | Native node canvas; not yet evaluated in depth | [repo](https://github.com/xyflow/xyflow) |
| tldraw | Custom; no production use without key (text opened) | Active | reject | Licence blocks production | [LICENSE](https://github.com/tldraw/tldraw/blob/main/LICENSE.md) |
| CQL (Conexus AI) | BSD-3 for non-commercial and exploratory/evaluative use only, per README; no LICENSE file | Active; last commit 2026-07-26 | inspiration | Functorial migration reference; terms are non-commercial | [README](https://github.com/CategoricalData/CQL) |
| Hets | GPL-2.0-or-later (README; LICENSE.txt opened) | Last commit 2025-10-07 | inspiration | Heterogeneous logics; Haskell, GPL, slow maintenance | [repo](https://github.com/spechub/Hets) |
| `rfc8785` (Trail of Bits) | Apache-2.0 | 0.1.4 (2024-09-27); repo push 2026-09-28 | dependency | Pure-Python RFC 8785 for graph-lane hashes | [PyPI](https://pypi.org/project/rfc8785/), [repo](https://github.com/trailofbits/rfc8785.py) |
| RFC 6902 JSON Patch | IETF | Published April 2013 | export target | Diff format for exports; six ops, atomic on failure; it is structural, not domain-typed | [RFC](https://www.rfc-editor.org/rfc/rfc6902) |
| RFC 8785 JCS | IETF | Informational, 2020 | dependency (via `rfc8785`) | Byte-stable JSON; I-JSON, no duplicate keys, IEEE 754 numbers | [RFC](https://www.rfc-editor.org/rfc/rfc8785) |

## 4. Mechanisms table

| School | Mechanism | Benefit | Cost | Verdict | Source |
|---|---|---|---|---|---|
| Lenses | GetPut and PutGet as property tests for every view/edit-translator pair | Catches edit translators that drop or invent information; turns "the picture matches the model" into a falsifiable claim | Needs a defined complement; laws hold modulo definedness | **adapt** | Foster et al. |
| Lenses | Conditional PutPut ("last drag wins") tested where it should hold | Lets the UI coalesce a drag sequence into one transaction | Fails legitimately for map-like, merge-like and versioned views (authors' own examples) | **adapt** (optional law, per view) | Foster et al. §3 |
| Delta lenses | Separate delta discovery from delta propagation | A canvas emits explicit edit events with stable ids, so alignment is given; only propagation needs logic | None for canvas; text-file views still need diffing | **adopt** | [Diskin 2011](https://www.jot.fm/contents/issue_2011_01/article6.html) |
| Delta lenses | Reflective updates: consistency restoration may amend the user's edit | Honest handling of "you added a transition; I also had to add its guard" | Amendments must be shown to the human as a diff | **adapt** | [Diskin et al.](https://arxiv.org/abs/1911.11302) |
| View-based (Vitruv) | Views report atomic modifications; propagation is change-driven | Simple contract for the canvas; no full-model diff on each save | Rules per view pair | **adopt** (as contract) | [Vitruv wiki](https://github.com/vitruv-tools/.github/wiki) |
| TGG | Trace links with stable ids (our design); repair-in-place rather than delete and recreate | Less information loss, faster propagation (as reported by authors, in eMoflon) | Rule authoring; GPL tooling | **adapt** (idea only: trace links, in-place update) | [Fritsche et al.](https://arxiv.org/abs/2005.14510) |
| Tolerant consistency | Drafts may be inconsistent; the commit boundary is where consistency is enforced | Canvas feels free; kernel guards still bind | Need a visible "draft" state | **adapt** | [VICToRy](https://arxiv.org/abs/2012.01655) |
| Functorial migration | View definition as a declared mapping, checked for totality over semantic types (every type is drawn or explicitly "not shown") | New semantic types cannot silently vanish from views | A test, not a categorical engine | **adapt** (check only); the rest **theory-only** | [Spivak](https://arxiv.org/abs/1009.1166) |
| Institutions | Every artefact kind has its own satisfaction relation; cross-kind claims need an explicit translation | Encodes "a proof about a model is not a proof about the code" in the data model | None as a rule; a full institution framework is heavy | **theory-only** (rule adopted as labelling policy) | [Goguen and Burstall](https://doi.org/10.1145/147508.147524), [Hets](https://github.com/spechub/Hets) |
| Sheaves | Overlap agreement: views that share ids must agree on shared facts; disagreement is a located finding | Pinpoints which two views disagree, on which id | Only the join is cheap; cohomology and Laplacians add nothing for discrete records | **adapt** (join) / **theory-only** (cohomology) | [Robinson](https://arxiv.org/abs/1603.01446), [Hansen and Ghrist](https://arxiv.org/abs/1808.01513) |
| Merkle / content addressing | Every generated view embeds the hash of the source it was projected from (already in ADR-0023) and the okf lane's `repo://` + hash method | Drift is a hash comparison, not a judgement | Hash proves change, not correctness | **adopt** (exists) | ADR-0023, `quality/okf/codelink.py` |
| Canonical serialisation | RFC 8785 for graph-lane artefacts | Byte-identical across platforms | Numbers limited to IEEE 754; no Unicode normalisation | **adopt** | [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785) |
| Concurrency | Causal-dependency conflict handling for concurrent multi-model edits | Needed only with several simultaneous writers | Complex; EIJA has a single local owner and `expected_version` | **theory-only** | [Fritsche et al.](https://arxiv.org/abs/2011.03357) |

### 3.8 MEASUREMENT: EIJA's own transactions behave like a lens with partiality

Script `.tmp/exp_lens.py` (not committed), run 2026-09-29 with `PYTHONHASHSEED=0` on the `weave` worktree. It enumerates the whole `SemanticTransaction` alphabet (`enable`, `set(Submitted)`, `set(Recommended)`) against two base models. Domain is tiny; this is exhaustive over 3 transactions x 2 bases, not evidence about other domains.

| Finding | Result |
|---|---|
| Idempotence of `enable` | Holds (same semantic hash after two applications) |
| PutPut-like law `put(put(m,t1),t2) = put(m,t2)` on the enabled model | Holds for all 9 ordered pairs |
| Same law on the baseline | Fails only through **definedness**: `set(...)` on the baseline raises `MEANING_REQUIRED` ("Enable the recommendation meaning first") |
| Commutativity of `enable` and `set(...)` | Not commutative: `set` first is refused. Order of canvas edits matters, so the translator must emit them in dependency order |
| `canonical()` vs RFC 8785 | Keys `U+FF5E` and `U+1F600`: kernel emits `U+FF5E` first (code point order); RFC 8785 sorts by UTF-16 code units and puts `U+1F600` first. `canonical({"x": 1.0})` gives `1.0`; RFC 8785 gives `1` |
| Windows console | Printing a non-ASCII key under the default cp1252 console raised `UnicodeEncodeError`; `PYTHONIOENCODING=utf-8` fixed it. Any CLI that emits canonical text must set the encoding itself |

## 5. Implications for EIJA

1. **One lens shape, stated in an ADR.** `Workflow` is the source; a view is `get(Workflow) -> ViewModel` (pure, deterministic, already how the visual lane works); a canvas edit is translated by `translate(ViewModel, Edit) -> Accepted(transactions, layout, amendments) | Rejected(code, reason)`. The kernel's `apply_transaction` remains the only `put`. Agents and providers may submit edits but never approve or apply.
2. **Interface with other lanes.** Visual lane: reuse its format-neutral `Graph`/`ClassModel` as the `ViewModel`; the canvas is a second consumer of the same projections. Agents lane: expose `translate` as a proposal-only MCP tool (their ADR-0041 already forbids select, edit, approve, apply). Okf lane: a page about a view links to the source with a `repo://` URI and a hash method; I propose (not implement) a `workflow-semantic-v1` method that hashes `Workflow.semantic_hash`. Property lane: use their Hypothesis strategies for the laws.
3. **Law suite in `tests/graph/`.** For each view: GetPut (no-op edit yields no transactions and the same semantic hash), PutGet (re-projecting after the translated transaction reproduces the intended view modulo layout and declared amendments), conditional PutPut, and "layout edits never change the semantic hash". Where the alphabet is small, enumerate exhaustively as in 3.8, and run Hypothesis elsewhere. Label results as MEASUREMENT on the tested alphabet, never as a proof.
4. **Identity by id, never by label.** Every canvas element carries the semantic id (for transitions, `Transition.id`). Alignment is then given (Diskin), and renames cannot look like delete plus add. draw.io files are an import/export surface only, and an unexported browser state is not evidence (ProofMap GAP-010).
5. **Complement and failure modes as tests, not prose.**

   | Failure mode | Where it shows in the canvas | Required behaviour |
   |---|---|---|
   | Information loss | Layout, colour, notes not in the semantic model | Store in a layout complement (`LayoutChange`), keyed by id; never in the semantic hash |
   | Non-invertibility (many pictures, one model) | Two diagrams for the same `Workflow` | Deterministic normal form; identical semantic hash means identical projection |
   | Partiality | `set` before `enable` (measured) | Typed rejection with the kernel error code, no silent repair |
   | Order dependence | Drag sequences | Translator orders transactions by dependency; test non-commutation |
   | Amendment | Kernel must add a guard the user did not draw | Return the amendment explicitly; the human sees "you drew X, the kernel also needs Y" |
   | Conflict | Stale view | Reject via existing `expected_version`; single local owner, so no concurrent merge |

6. **Tolerate drafts, enforce at commit.** A canvas may hold an incomplete drawing. Consistency is checked at the transaction boundary by `ensure_policy` plus a view-consistency gate: recompute every projection from the source and compare embedded hashes (extends the visual lane's drift gate).
7. **Mapping totality check.** A declared table from semantic types to view element kinds, with an explicit `not_shown` marker, fails the gate when a new type appears without an entry. This is the only piece of functorial data migration we adopt.
8. **Canonical JSON.** The graph lane hashes with `rfc8785` and names the algorithm in the hash string (for example `sha256:jcs`). It never compares its hashes with kernel `fingerprint()` output. Changing the kernel `canonical()` needs its own ADR and a migration of stamped hashes, which this lane must not do. Emit UTF-8 explicitly on Windows.
9. **Triggers to revisit heavier tools.** Evaluate eMoflon (as a separate process exchanging files, since GPL-3.0) or Vitruv only if (a) three or more independently hand-edited artefact kinds must stay consistent with each other, not just with the source, or (b) a customer needs concurrent multi-user editing. Neither holds today.
10. **Build list, each with an OSS check.** Custom: (a) law checker and edit-translator protocol (about 100 lines; alternatives PyPI `lenses` GPLv3+, Boomerang LGPL-2.1 stale OCaml); (b) mapping totality check; (c) view-consistency gate. Everything else uses existing tools. Add one row per lane item to `docs/oss/REGISTER.md`. The `graph` extra needs `rfc8785==0.1.4` pinned.

## 6. Gaps and unverified items

- UNVERIFIED (content not read; existence and venue confirmed by Crossref DOI records): Stevens on QVT-R semantic issues (2008) and networks of models (2019); Czarnecki et al. cross-discipline perspective (2009); Hofmann, Pierce, Wagner symmetric and edit lenses; Atkinson et al. orthographic modelling; Klare et al. Vitruvius JSS 2021; Egyed 2011 inconsistency detection; Schürr 1995 TGG. I state no claim about their results.
- UNVERIFIED: the theorem statements in Spivak and Wisnesky (closure of FQL), and everything specific in the sheaf papers beyond their abstracts. No theorem is relied upon.
- UNVERIFIED: the list of known QVT-R failure modes; the QVT 1.3 PDF was not opened, only the landing page.
- The Foster et al. text is the authors' draft copy ("Vol. TBD"); the published TOPLAS version may differ in numbering or wording.
- Neo4j licence is GitHub SPDX metadata only. The CQL release tag `march_31_2026` shows `published_at` 2026-01-07 in the GitHub API; recorded as observed.
- Licence compatibility statements are engineering readings, not legal advice; an owner decision is needed before shipping any GPL or EPL component, even as a separate process.
- Not measured: how an actual React Flow or draw.io canvas would emit atomic edit events, nor its performance. Needs a spike; not run because it needs a browser.
- WebSearch was unavailable, so lesser-known bx tools (for example BiGUL, and Ecore-based diff and merge tools) were not surveyed. The bx community's [examples repository](https://bx-community.wikidot.com/) is a likely source of benchmark cases for `graph/bench`.
- The measurement in 3.8 covers 3 transactions and 2 base models on the current kernel; it does not generalise to richer workflows or to view-to-source edits for diagrams beyond the state view.
