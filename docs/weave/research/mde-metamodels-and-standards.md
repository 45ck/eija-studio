# MDE metamodels and standards: what EIJA can import and export instead of inventing

Dossier `mde-metamodels`. Lane: weave. Access date for every URL: 2026-09-29. Bracketed tags like [S12] point to the source list at the end.

## 0. Decisions first

| # | Decision | Confidence |
|---|---|---|
| D1 | Keep the Pydantic contracts plus JSON Schema as EIJA's metamodel. Do not adopt UML, MOF or XMI as an internal or import format. | High |
| D2 | First export target: SysML v2 textual notation for the flat state machine, requirements and traces. It is the only surveyed standard that covers states, transitions, requirements, `satisfy` and `verify` in one small, current, JSON-schema-backed language. Emit-only. Validate with an optional external tool that reports `NOT_RUN` when absent. | Medium: the Python tooling is immature (section 2.2) |
| D3 | Second target: C4-style component map. Emit to Structurizr DSL or LikeC4. Optionally read the JSON export of a human-written "intended architecture" and diff it against the real import graph (reflexion model, section 4). | Medium: export determinism is untested |
| D4 | Mermaid, PlantUML and DOT stay export-only (ADR-0019 and the visual lane). Nothing is imported from them. | High |
| D5 | Every EPL, GPL, LGPL or MPL tool is a separate process, never vendored into the Apache-2.0 tree. Proprietary tools are rejected. | High |
| D6 | Import is restricted to a flat FSM subset and refuses hierarchy, concurrency and history with a stable error code. | High |
| D7 | Interchange JSON that we hash uses RFC 8785 (JCS). Ids derived for exports use UUIDv5. | High: MEASURED gap in section 4 |

## 1. Scope and method

**Question.** Which standards and tools give a reusable metamodel or interchange format for a small typed subset (states, transitions, classes, components, requirements, traces), and what do practitioners abandon?

**What I read in the repo.** `src/eija_studio/domain/models.py` (frozen Pydantic `Workflow`: a flat tuple of states, and transitions carrying role, guards and required and forbidden effects; `canonical()` uses `json.dumps(sort_keys=True)`), the visual lane's `docs/visual.md` and ADR-0023 (one neutral `Graph`/`Sequence`/`ClassModel`, emitters to Mermaid, PlantUML and DOT, provenance comment with `semantic_hash`), the okf lane's ADR-0045 (`resource: repo://path#fragment` and `sources[].sha256`), the quality lane's ADR-0035 (import-linter layers), and ProofMap Lite's README, `docs/gap-audit.md` and `docs/label-conventions.md` (private repo, read through `gh` as owner).

**Queries and sources.** Repository metadata (licence, archived flag, last push, releases, tags) came from the GitHub API and the repositories' own LICENSE and README files. Standards came from the OMG spec landing pages. Empirical studies came from the OpenAlex API (abstracts) and one open-access PDF that I extracted locally. I read 30 or so vendor and project pages.

**Inaccessible or degraded (details in section 6).**
- The session's WebSearch budget was exhausted (200 of 200), so discovery relied on `gh search`, OpenAlex and known vendor pages. Some tools may be missing.
- Petre 2013 is paywalled. Only the abstract was verified.
- OMG PDFs were not opened; only the landing pages listing files and IPR mode.
- The EPL-2.0 FAQ page returned navigation only. I used the licence text itself.

## 2. Per tool

### 2.1 OMG classics: UML, OCL, MOF, XMI

- **What.** UML 2.5.1 (Dec 2017, "RF-Limited" IPR) ships `UML.xmi`, `PrimitiveTypes.xmi`, `StandardProfile.xmi`, `UMLDI.xmi` [S1]. OCL 2.4 (Feb 2014) ships `OCL.cmof` and `EssentialOCL.emof` [S2]. MOF 2.5.1 (Oct 2016) defines EMOF and CMOF and ships `MOF.xmi` plus two OCL constraint files [S3]. XMI 2.5.1 (June 2015) ships `XMI.xsd` and `XMI-Canonical.xsd` [S4].
- **What it gives EIJA.** Vocabulary (stereotypes, multiplicity, composition), and the layering idea: a model conforms to a metamodel. EIJA already has that layering as Pydantic contracts.
- **Why not the format.**
  - A 2007 study reports loss of fidelity when moving UML through XMI because of version differences and proprietary add-ons [S35].
  - The SysML v2 release itself says its XMI is "Eclipse XMI ... not a fully normative OMG XMI representation" [S8].
  - The 2023 survey on formalising UML state machines says the UML specification is written in natural language and that this ambiguity may cause inconsistencies [S34].
  - The classical Statecharts semantics is not compositional [S36].
- **Cost.** No maintained Python UML/XMI stack was found that is worth the coupling. OCL evaluators live in Java (Eclipse OCL, EPL-2.0 [S16b]). EIJA already states invariants as Pydantic validators and, in the SMT lane, as Z3 formulas.
- **Verdict.** Inspiration only. Reject as import or export.

### 2.2 SysML v2, KerML, standard API, Pilot Implementation

- **Status.** KerML 1.0 and SysML 2.0 are formal OMG specs; the API and Services spec is 1.0 [S5][S6][S7]. The Pilot repo README says they were formally adopted 30 June 2025 and editorially updated March 2026 for ISO submission [S8]. Machine-readable files include a JSON schema for the abstract syntax, `KPAR` archives, MOF XMI and, for the API, OpenAPI JSON and OSLC Turtle shapes [S5][S6][S7]. IPR mode is Non-Assert for KerML and the API [S5][S7]. (The OMG pages disagree with each other on publication dates; treat those as unresolved.)
- **Activity.** The release repo has tags 2026-05, 2026-07, 2026-08 (last 2026-09-12) [S8]. The Pilot repo was pushed 2026-09-28 [S9].
- **Licence.** Pilot Implementation and API Services: EPL-2.0 (LICENSE file) [S9][S10]. The Pilot README says "See the files LICENSE and LICENSE-GPL", but the root listing shows only `LICENSE`. That is an unresolved discrepancy [S9]. The official Python client is LGPL-3.0 and last pushed 2021-10-14 [S12].
- **Textual notation covers our subset** (read from example files [S11]):
  - `state def X { first start then off; state off; transition t first off accept Sig then starting; }`.
  - Guards and effects: `accept Sig if cond do send ... then on`.
  - `requirement def R { doc /* ... */ }` with short names like `<'1'>`.
  - `satisfy r by p;`, `verification def V { objective { verify r; } }`.
  - `metadata def` and `@StatusInfo { ... }` annotations, usable for EIJA-specific attributes.
- **Mapping (PREDICTION, not yet tested).** `Workflow` to `state def`; `Transition` to `transition` (action as trigger, guards and effects via `if`/`do`, role and effect names via metadata); contracts to `attribute def` or `part def`; bounded areas to `package`/`part def`; requirement to `requirement def`; test link to `verification def` with `verify`; component link to `satisfy ... by`.
- **Python and JS access.**

| Tool | Licence | Status (2026-09-29) | Note |
|---|---|---|---|
| `sysml2py` (textX-based) | MIT | last PyPI release 0.5.3, 2024-05-30; last commit 2025-03-17 [S14] | Constructs and dumps text. Stale. |
| Open-MBEE `sysmlv2-python-client` | Apache-2.0 | pushed 2026-03-31, 9 stars, "tested against the OpenMBEE Flexo implementation" [S13] | REST client only |
| Open-MBEE `tree-sitter-sysml` | Apache-2.0 | pushed 2026-09-18 [S13] | Grammar for editors; no semantics |
| Open-MBEE `sysml-toolkit` (Rust, Python bindings) | Apache-2.0 | created 2026-09-08, v0.9.1 on 2026-09-20, one visible contributor [S13] | README claims parse, canonical formatter, JSON interchange, deterministic CBOR, validation, lint, Z3 constraint checking. I did not run it. |
| Syside (Sensmetry) | free Editor subscription; Modeler and Automator paid [S15] | commercial | Python API exists; reject |

- **API server.** The Pilot API needs PostgreSQL, JDK 11 and sbt/Play [S10]. Far too heavy for a local kernel.
- **Verdict.** Export target now (text generated by a deterministic emitter, golden-file tested). Optional validator: `sysml-toolkit` `sysmlv2 check` or the Pilot, both as external processes reporting `NOT_RUN` when missing. Adopt SysML v2 naming inside the graph schema. No import in the first phase. The young toolkit is a "watch" item, not a dependency.

### 2.3 Eclipse Modeling: EMF, Sirius, Xtext, Papyrus

- **EMF.** EPL-2.0 [S16]. "From a model specification described in XMI, EMF provides tools and runtime support to produce a set of Java classes" [S16]. Java only. PyEcore is the Python port: BSD-3-Clause, XMI and JSON (de)serialisation, but last release 0.15.2 on 2024-12-12 and last push 2024-12-22 [S17]. The Ecore to EMOF relationship was not verified this session.
- **Sirius** (EPL-2.0, pushed 2026-09-24) builds graphical workbenches from declarative descriptions [S18]. **Xtext** (EPL-2.0, active 2026-09-28, latest tag v2.44.0) builds DSL parsers and IDE support in Java [S19]. **Papyrus**: EPL-2.0, "mature", latest release 7.0.0 (2025-06-11), supports UML 2.5 and SysML 1.6, not SysML v2 [S20].
- **Fit.** All are GUI or JVM stacks. The Pilot's module names (`org.omg.kerml.xtext`, `org.omg.sysml.edit`) indicate Xtext and EMF [S9] (INFERRED), so a JVM is needed only if we run the Pilot as a validator.
- **Verdict.** Inspiration. Ecore export via PyEcore is possible but rejected by default: Pydantic already emits JSON Schema, which is our metamodel.

### 2.4 Capella / Arcadia, Modelio, Archi / ArchiMate

- **Capella** (EPL-2.0, v7.1.0 on 2026-08-03) is an MBSE workbench for the Arcadia method [S21]. `py-capellambse` reads and writes Capella models headlessly in Python (Apache-2.0 plus OFL-1.1 assets; 0.8.1 on 2026-01-20; Python 3.11 to 3.14) [S21]. Systems-engineering layers, not software structure.
- **Modelio.** GPL-3.0 (LICENSE file) [S22]; GitHub tag v6.2.0 on 2026-08-26, while the website still shows 5.4.1 [S22]. Supports UML, BPMN, ArchiMate, SysML [S22]. GPL means a separate process at most.
- **Archi** (MIT, release tag 5.10.0 on 2026-09-03) [S23]. The Open Exchange format is The Open Group's file format for moving ArchiMate 3.1 and 3.2 models between tools; it is explicitly "not intended as a persistent file format" [S23]. The XSD licence terms were not stated on the page I read.
- **Verdict.** Capella: inspiration (layered views). Modelio: reject as dependency, inspiration only. Archi: export target only if a user asks; enterprise architecture is not EIJA's domain.

### 2.5 Architecture-as-code: C4, Structurizr, LikeC4, D2, Ilograph

- **Structurizr.** The 2026 consolidated repo `structurizr/structurizr` is Apache-2.0 (v2026.09.19 on 2026-09-19) with modules for core, dsl, export, json and mcp [S24]. The older `cli`, `lite` and `onpremises` repos are archived (2026-02 and 2026-03) [S24]. Export formats: plantuml, c4plantuml, mermaid, websequencediagrams, static, png/svg, json, theme, and custom exporters. Determinism of output is not documented [S24]. Java runtime.
- **LikeC4.** MIT, v1.59.4 on 2026-09-21 [S25]. CLI: `validate` ("check syntax and layout drift"), `format` with a CI check mode, `export json`, and `gen` for mermaid, dot, d2 and plantuml [S25]. A `packages/mcp` directory exists in the repo, although the CLI docs page I read did not mention an MCP server [S25]. Node runtime.
- **D2.** MPL-2.0, v0.9.0 on 2026-09-07, Go, pre-1.0 [S26]. MPL is file-level copyleft and can be combined with Apache-2.0 code [S45]. No Python API found. Only a diagram renderer for us.
- **Ilograph.** SaaS and desktop app. The public org repos are standard libraries (MIT) and agent skills (Apache-2.0); the docs footer says "Copyright 2025 Ilograph LLC" and no open-source licence for the engine or a JSON schema [S29]. Reject.
- **Fit.** A component map is the best small typed artifact for "components" and "relationships". It maps onto DDD bounded contexts in the architecture doc. Both Structurizr and LikeC4 give JSON export that Python can read.
- **Verdict.** Export target plus optional process, either one; decide by a determinism test (export twice, compare bytes, in a clean directory). Not tested yet.

### 2.6 PlantUML, Mermaid, and their grammars

- **PlantUML.** `LICENSES.md` states the default is GPL-3.0-or-later and lists at-your-option variants: GPL-2.0, LGPL-3.0+, Apache-2.0, BSD-3-Clause, EPL-1.0, MIT. Generated images are not covered by the licence [S27]. (GitHub's API labels the repo LGPL-3.0; the repo's own `LICENSES.md` is authoritative.) Java. No stable public AST; the visual lane uses `plantuml -syntax` as a check.
- **Mermaid.** MIT [S28]. `@mermaid-js/parser` is Langium-based but its grammars cover only newer diagram types (architecture, gitGraph, info, packet, pie, radar, treemap, wardley and a few more). State and class diagrams still ship as `.jison` parsers [S28]. INFERRED: no supported public AST for state diagrams.
- **Verdict.** Export-only, as ADR-0019 already decided. Any reading of emitted text stays an independent test parser, as the visual lane does.

### 2.7 Other formats worth a line

- **SCXML** (W3C Recommendation, 1 Sept 2015) has a normative interpretation algorithm (Appendix D) and a schema [S41]. It is the only surveyed state-machine format with a normative execution algorithm. EIJA guards are named kernel checks, not expressions, so a mapping to `cond` is lossy. Python interpreters found: `pyscxml` (LGPLv3, last release 2012) and `scxml` 0.1.0 (visualisation only) [S41b]. Export target, low priority.
- **ReqIF 1.2** (OMG, July 2016) ships `reqif.xsd` and `reqif.cmof` [S42]. Export target if an external requirements tool appears. OpenFastTrace (the quality lane) is the primary requirements trace tool.
- **Gaphor** (Apache-2.0, Python, v3.3.2 on 2026-05-02) is a UML 2, SysML v1, C4 and RAAML modeller with a Python model API [S30]. Its file format stores layout (`matrix`, `width`, `height`) beside semantics and needs a special merge editor after git conflicts [S30]. Cannot be our source of truth; possible human viewer. Inspiration.
- **draw.io** (Apache-2.0) [S43] is what ProofMap Lite used as editor; see section 3.

## 3. What practitioners abandon, and why

| Finding | Source |
|---|---|
| UML in industry: interviews with 50 professionals in 50 companies identify 5 patterns of use; the abstract questions whether UML is the "lingua franca" claim. I could not read the five patterns (paywalled). | [S31] |
| MDE survey of 450 practitioners plus 22 interviews: MDE is used more widely than believed, rarely for whole systems, mostly through small domain-specific languages, often textual; "modeling languages require significant customization before they can be applied in practice". | [S32] |
| Code generation is not the main driver. Reported productivity gains were 20 to 30 percent (self-reported), and training and organisational cost offset them. | [S32] |
| Top-down mandates struggle; ground-up adoption works. Keep domains tight and narrow. | [S32] |
| One case study: code certification cost rose by a factor of eight because generated code was hard to read (single anecdote, not a rate). | [S32] |
| Architects sometimes inflate models because managers read simple models as not thought out. | [S32] |
| Open-source UML users (485 answers, 458 projects): collaboration is the main motivation; it helps new contributors and people who do not create models. | [S33] |
| Tool interchange loses fidelity and needs vendor extensions. | [S35][S8] |
| ProofMap Lite (owner's repo): inferred model views contradicted project boundaries (GAP-024); generated timestamps caused churn (GAP-003); browser-only drafts were invisible to agents (GAP-010); untracked generated files bypassed a clean check (GAP-033). Its ad-hoc typed graph has 20 node types and 16 edge types in `label-conventions.md`, which is a metamodel invented without a standard behind it. | [S43] |

**Reading for EIJA.** People keep diagrams that are narrow, textual, generated and useful for communication, and they abandon whole-system UML, round-trip code generation and unreadable generated output. That matches ADR-0019 (generated projections, no hand-edited source of truth). Any hand-drawn input we ever accept should be a low-trust `proposal` that the kernel checks; agents propose, the kernel checks, the owner decides.

## 4. Options table

| Name | Licence | Status (2026-09-29) | Verdict | Why | Source |
|---|---|---|---|---|---|
| UML 2.5.1 + XMI 2.5.1 | OMG spec, RF-Limited | formal, 2017/2015 | inspiration | Ambiguous semantics, lossy exchange, no Python stack | [S1][S4][S34][S35] |
| OCL 2.4 | OMG spec, RF-Limited | formal, 2014 | inspiration | Invariant style only; Java evaluators | [S2] |
| MOF 2.5.1 (EMOF/CMOF) | OMG spec | formal, 2016 | inspiration | Layering idea; our M2 is Pydantic | [S3] |
| SysML v2 + KerML (text, JSON schema) | OMG spec, Non-Assert (KerML/API) | formal, adopted 2025-06-30 | export-target | Covers states, transitions, requirements, `satisfy`, `verify` | [S5][S6][S8][S11] |
| SysML v2 Pilot Implementation | EPL-2.0 (README also cites LICENSE-GPL, absent at root) | active, pushed 2026-09-28 | optional-process | JVM validator, never vendored | [S9] |
| SysML v2 API Services | EPL-2.0 | pushed 2026-05-14 | reject | PostgreSQL + JDK 11 + sbt server | [S10] |
| sysml-toolkit | Apache-2.0 | 3 weeks old, v0.9.1, one visible contributor | optional-process | Deterministic-minded claims, unrun by me | [S13] |
| sysml2py | MIT | stale since 2024-05 | reject | Stale; no validation | [S14] |
| SysML v2 official Python client | LGPL-3.0 | last push 2021 | reject | Stale | [S12] |
| Syside (Sensmetry) | commercial, free Editor tier | active | reject | Paid Automator, closed | [S15] |
| EMF / Ecore | EPL-2.0 | active | inspiration | Java; JSON Schema replaces it | [S16] |
| PyEcore | BSD-3-Clause | last release 2024-12-12 | optional-process | Only if an Ecore consumer appears; slow maintenance | [S17] |
| Sirius / Xtext | EPL-2.0 | active | inspiration | JVM, GUI | [S18][S19] |
| Papyrus | EPL-2.0 | mature, 7.0.0 (2025-06) | inspiration | UML/SysML v1 GUI | [S20] |
| Capella + py-capellambse | EPL-2.0 / Apache-2.0 | 7.1.0 (2026-08); 0.8.1 (2026-01) | inspiration | Systems layers, not software | [S21] |
| Modelio | GPL-3.0 | 6.2.0 tag (2026-08-26) | reject | GPL; dependency impossible | [S22] |
| Archi + Open Exchange | MIT; XSD terms unread | 5.10.0 (2026-09) | export-target | Only on demand; enterprise scope | [S23] |
| Structurizr (unified repo) | Apache-2.0 | v2026.09.19 | export-target | Reference C4 DSL; JSON export; JVM | [S24] |
| LikeC4 | MIT | v1.59.4 (2026-09-21) | export-target | `validate`, `format`, JSON export; Node | [S25] |
| D2 | MPL-2.0 | v0.9.0 (2026-09-07) | inspiration | Renderer only | [S26][S45] |
| Ilograph | proprietary (no OSS licence found) | active SaaS | reject | Closed engine | [S29] |
| PlantUML | GPL-3.0-or-later default; LGPL/Apache/BSD/EPL/MIT variants | active | export-target | Already in ADR-0019 | [S27] |
| Mermaid | MIT | active | export-target | State/class have no supported AST | [S28] |
| SCXML | W3C Recommendation | 2015 | export-target | Normative algorithm, but guards are lossy | [S41] |
| ReqIF 1.2 | OMG spec | 2016 | export-target | On demand | [S42] |
| Gaphor | Apache-2.0 | 3.3.2 (2026-05) | inspiration | Layout mixed into semantic file | [S30] |
| textX / Lark / Langium | MIT | active | inspiration | Only if a textual notation is ever needed. EIJA needs no new DSL. | [S46] |

## 5. Mechanisms from maths and computer science (only where it pays)

| School | Mechanism | Benefit | Cost | Verdict | Source |
|---|---|---|---|---|---|
| Type theory and metamodelling | A model graph must map onto a type graph (node kinds and edge kinds with allowed endpoints). Check every link against a table. | One checker for all link types; kills dangling and mistyped links. INFERRED from MOF layering; ProofMap's 20/16 tables are the instance. | Maintain the tables; name each kind after SysML v2 where a term exists | adopt | [S3][S43] |
| Architecture conformance | Reflexion model: compare a human's high-level model with the source model and show where they agree and differ. | Deterministic set differences between intended (C4) and actual (import graph) architecture | The model-to-source mapping is hand-maintained and can drift | adopt | [S37] |
| Canonical forms | JCS (RFC 8785): UTF-16 code-unit key order, ECMAScript number output, UTF-8. | Byte-identical hashes across languages | Python `sort_keys` orders by code point. MEASURED: U+10000 sorts before U+FFFF under JCS, after it in Python. The kernel's `canonical()` differs for such keys; changing it needs its own ADR. | adopt (new artefacts only, using the `rfc8785` package, Apache-2.0 by Trail of Bits) | [S39] |
| Content-addressed naming | UUIDv5 from a stable name in a fixed namespace gives equal ids for equal input. | Deterministic `@id` and `xmi:id` in exports | SHA-1 inside; not a security claim | adopt | [S40] |
| Bidirectional transformations (lenses) | A projection is a `get`. Only imports need a `put`, and then round-trip laws apply. | Export-only paths carry no round-trip burden; imports get a testable law | Property tests per import path | adapt: `parse(emit(m)) == m` on the supported subset | [S38] |
| Statecharts semantics | Restrict to a flat labelled transition system. | Exact meaning; avoids known semantic disputes | Cannot import hierarchy or concurrency | adopt | [S34][S36] |
| Small DSLs | Narrow, textual, generated DSLs succeed more often than broad ones. | Matches EIJA's frozen small vocabulary | Multiple DSLs need integration | adopt as design rule | [S32] |
| Graph rewriting and model-transformation languages | Declarative rewrites over metamodels | None identified beyond generators plus golden files (ADR-0023) | New language, JVM | theory-only | [S44] |

## 6. Implications for EIJA

1. **Metamodel.** `graph/schema/` defines an EIJA interchange profile: a typed graph whose node and edge kinds each cite a SysML v2 term or say "EIJA-specific". Start from ProofMap's 20 node and 16 edge kinds and prune.
2. **SysML v2 emitter.** Add one emitter that follows the visual lane's neutral-model pattern and writes `.sysml`. Stable ordering, LF, no timestamps. The first line carries the same `eija: ... semantic_hash=` provenance comment the visual lane uses. Golden files pin it.
3. **Validation is optional and honest.** Run `sysmlv2 check` or the Pilot in a subprocess, `TMP`/`TEMP` inside `.tmp/`, one process at a time. Missing tool means `NOT_RUN`. A passing syntax check is not a conformance claim to the SysML v2 standard, and a check on a model is not a check on the code.
4. **Ids.** Derive `@id` and `xmi:id` values as UUIDv5 over `repo://` style stable names shared with the okf lane, so an exported element and an OKF page point at the same thing.
5. **Intended architecture.** Let humans write a LikeC4 or Structurizr file. Read its JSON export, map it to the quality lane's import graph, and report agree, differ and missing. Choose the tool by a determinism test first (export twice in clean directories, compare bytes).
6. **Import stays narrow.** Accept only the flat FSM, requirements with `doc`, and `satisfy`/`verify` links. Refuse anything else with a stable error code. Imported content is a `proposal`: the kernel checks it and the owner decides. Agents and providers never approve or apply.
7. **Canonical JSON.** Use JCS for new graph artefacts. Leave `domain/models.py` alone. Note the astral-key gap for a later ADR.
8. **No hand-edited diagram as source of truth.** ProofMap's 46+ gap entries are mostly staleness and drift of hand-edited or heuristic sources [S43]. ADR-0019's generated-only stance removes that class.
9. **Licence hygiene.** Log each tool in `docs/oss/REGISTER.md` with its role (dependency, optional process or export target). GPL, LGPL, MPL and EPL tools are subprocesses only and never vendored. Reject Syside, Ilograph and Modelio as dependencies.
10. **Watch list, not roadmap.** `sysml-toolkit` (three weeks old) and SysML v2 Python bindings in general. Re-check status before any dependency decision.

## 7. Gaps and unverified items

- **Petre 2013.** Only the abstract (via OpenAlex) is verified. The five patterns are not enumerated here. Springer, IEEE and Open University pages were blocked or paywalled.
- **Search coverage.** WebSearch budget exhausted, so tool discovery was limited to `gh search`, OpenAlex and known pages.
- **OMG.** Spec PDFs not opened. Landing pages disagree on dates (the SysML page says "September 2025", the API page says published February 2025 with file id `formal/26-03-04`). UML and MOF licences are "RF-Limited" per the pages; I did not read the terms.
- **SysML v2.** `LICENSE-GPL` cited in the README is not at the repo root. No headless validation CLI of the Pilot was verified. The JSON schema was not opened. The mapping of role, guards and effects to metadata is a PREDICTION. `sysml-toolkit` feature claims are unrun.
- **Ecore and EMOF.** Relationship not verified from the EMF pages I read.
- **Capella, Sirius, Xtext, EMF.** Licences come from the GitHub licence detection, not from opening each LICENSE file. Papyrus source repo not inspected.
- **Modelio.** Website and GitHub disagree on the latest version. Licence of its extension API not checked.
- **Archi.** CLI wiki page failed to load. ArchiMate XSD licence terms not stated on the page.
- **Structurizr and LikeC4.** Export determinism not tested. The Structurizr JSON schema and docs page for JSON returned 404. LikeC4's docs page did not mention MCP while its repo has `packages/mcp`.
- **Whittle et al.** Figures are self-reported by interviewees; the factor-of-eight certification cost is a single case.
- **SCXML, XState.** `python-statemachine` (MIT) SCXML support was not found in its README. XState v5 SCXML status unknown (a `scxml.ts` file exists in core).
- **EPL-2.0 FAQ.** Not retrievable; the reading of module-level scope relies on the licence text in the Pilot repo.
- **ProofMap Lite** is a private repo; I read it through the owner's `gh` access.

## Sources (accessed 2026-09-29)

- [S1] https://www.omg.org/spec/UML/2.5.1
- [S2] https://www.omg.org/spec/OCL/2.4
- [S3] https://www.omg.org/spec/MOF/2.5.1
- [S4] https://www.omg.org/spec/XMI/2.5.1
- [S5] https://www.omg.org/spec/KerML/1.0
- [S6] https://www.omg.org/spec/SysML/2.0
- [S7] https://www.omg.org/spec/SystemsModelingAPI/1.0
- [S8] https://github.com/Systems-Modeling/SysML-v2-Release (README, releases)
- [S9] https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation (LICENSE, README.adoc)
- [S10] https://github.com/Systems-Modeling/SysML-v2-API-Services
- [S11] https://github.com/Systems-Modeling/SysML-v2-Release/tree/master/sysml/src (training "23. State Definitions", "25. Transitions", examples "Simple Tests")
- [S12] https://github.com/orgs/Systems-Modeling/repositories (API Python client, LGPL-3.0, pushed 2021-10-14)
- [S13] https://github.com/Open-MBEE/sysmlv2-python-client , https://github.com/Open-MBEE/tree-sitter-sysml , https://github.com/Open-MBEE/sysml-toolkit
- [S14] https://github.com/Westfall-io/sysml2py , https://pypi.org/project/sysml2py/
- [S15] https://docs.sensmetry.com/ , https://docs.sensmetry.com/resources/licensing/
- [S16] https://github.com/eclipse-emf/org.eclipse.emf ; [S16b] https://github.com/eclipse-ocl/org.eclipse.ocl
- [S17] https://github.com/pyecore/pyecore , https://pypi.org/project/pyecore/
- [S18] https://github.com/eclipse-sirius/sirius-desktop
- [S19] https://github.com/eclipse-xtext/xtext
- [S20] https://projects.eclipse.org/projects/modeling.mdt.papyrus , https://eclipse.dev/papyrus/
- [S21] https://github.com/eclipse-capella/capella , https://github.com/dbinfrago/py-capellambse , https://pypi.org/project/capellambse/
- [S22] https://github.com/ModelioOpenSource/Modelio , http://www.modelio.org/index.htm
- [S23] https://github.com/archimatetool/archi , https://www.opengroup.org/open-group-archimate-model-exchange-file-format
- [S24] https://github.com/structurizr/structurizr , https://docs.structurizr.com/export
- [S25] https://github.com/likec4/likec4 , https://likec4.dev/tooling/cli/
- [S26] https://github.com/d2lang/d2
- [S27] https://github.com/plantuml/plantuml/blob/master/LICENSES.md , https://plantuml.com/faq
- [S28] https://github.com/mermaid-js/mermaid (`packages/parser`, `packages/mermaid/src/diagrams/{state,class}/parser`)
- [S29] https://www.ilograph.com/docs/spec/ , https://github.com/ilograph
- [S30] https://github.com/gaphor/gaphor (README, docs/storage.md, docs/merge_conflicts.md) , https://docs.gaphor.org/en/latest/
- [S31] https://api.openalex.org/works/doi:10.1109/ICSE.2013.6606618 (abstract); https://api.crossref.org/works/10.1109/ICSE.2013.6606618 (metadata)
- [S32] https://eprints.lancs.ac.uk/id/eprint/69765/1/SO_SW_2012_12_0188.R1_Whittle.pdf (Whittle, Hutchinson, Rouncefield, "The State of Practice in Model-Driven Engineering")
- [S33] https://doi.org/10.1109/icse-seip.2017.28 (abstract via OpenAlex)
- [S34] https://doi.org/10.1145/3579821 (abstract via OpenAlex)
- [S35] https://doi.org/10.1145/1297144.1297172 (abstract via OpenAlex)
- [S36] https://doi.org/10.1145/355045.355062 (abstract via OpenAlex)
- [S37] https://doi.org/10.1145/222132.222136 (Murphy, Notkin, Sullivan 1995; abstract via OpenAlex)
- [S38] https://doi.org/10.1145/1232420.1232424 (Foster et al. 2007; abstract via OpenAlex)
- [S39] https://www.rfc-editor.org/rfc/rfc8785 ; https://github.com/trailofbits/rfc8785.py
- [S40] https://www.rfc-editor.org/rfc/rfc9562
- [S41] https://www.w3.org/TR/scxml/ ; [S41b] https://pypi.org/project/pyscxml/ , https://pypi.org/project/scxml/
- [S42] https://www.omg.org/spec/ReqIF/1.2
- [S43] https://github.com/45ck/proofmap-lite (README, docs/gap-audit.md, docs/label-conventions.md; private); https://github.com/jgraph/drawio
- [S44] EIJA worktree files: `src/eija_studio/domain/models.py`, `docs/visual.md` and ADR-0023 (visual lane), ADR-0045 (okf lane), ADR-0035 (quality lane)
- [S45] https://www.mozilla.org/en-US/MPL/2.0/FAQ/
- [S46] https://github.com/textX/textX , https://github.com/lark-parser/lark , https://github.com/eclipse-langium/langium (licence and activity from the GitHub API)
