# Consistency and synchronisation between views

Lane: weave. Aspect: consistency-sync. Date: 2026-09-29. Status: design, input to [ADR-0093](../../adr/0093-weave-consistency-sync.md) (proposed). Transformation contracts and the law catalogue are in [graph/schema/transformations.md](../../../graph/schema/transformations.md). Architecture context: [ARCHITECTURE.md](../ARCHITECTURE.md); evidence base: [research/SYNTHESIS.md](../research/SYNTHESIS.md).

Labels: MEASUREMENT (a script ran, domain stated), PREDICTION (reasoned, not run), DESIGN (a proposal of this lane), UNVERIFIED (not opened or not confirmable; nothing is built on it). Dossier keys: [bx] multi-view-consistency-and-bx, [trace] traceability-and-requirements-graphs, [lang] ubiquitous-language-ontology-and-dsls, [ui] ui-to-model-linking, [mde] mde-metamodels-and-standards, [math] math-and-cs-foundations, [incr] incremental-builds-and-diagnostics, [gdb] graph-databases-and-knowledge-graphs, [assure] assurance-and-proof-linking, [agent] agent-reliability-and-context. Sources I opened myself this session are keyed S1 to S16 in section 13.

## 0. Decisions first

| # | Decision | Confidence | Basis |
|---|---|---|---|
| 1 | **A fact has exactly one authoring home.** Every other occurrence is either generated from it (get-only) or referenced by id and checked. Artefact Y is derived from X iff Y is the output of a fixed, versioned generator that reads only X (and declares its inputs); sources are the artefacts that no such generator produces. Ten kinds of authored source; everything else is derived get-only, recomputed evidence, a mixed page, or a proposal (section 2) | High | Measured drift today: the UI hard-codes 5 actions against a 4-action baseline ([ui], MEASUREMENT); ProofMap Lite gaps GAP-002 (stale dogfood artefacts), GAP-010 (browser-local drafts), GAP-033 (untracked generated files bypass the check); GAP-003 is timestamp churn in generated reports and is only loosely related |
| 2 | **One-way generation plus a digest check is the default; bidirectionality is admitted in exactly four places**: OKF pages (generated blocks plus a human complement, exists), a canvas edit translator (proposal only, deferred), explicit renames, and the human ack. Everything else is get-only, and a hand edit of a generated region is a finding, never a merge | High | Section 4; [bx] decisions 1 and 2; [mde] section 3 (practitioners abandon round-trip generation) |
| 3 | **Sync means regenerate, propose or ack. Nothing writes back into an authored source automatically.** Regenerate is deterministic and safe; propose is a value checked by the kernel; ack is a human act bound to an exact digest | High | AGENTS.md doctrine; kernel `approve` refuses a changed subject (`SUBJECT_CHANGED`) |
| 4 | **Eleven transformation contracts with lens, generation, extraction, complement, merge, rename and ack laws** (transformations.md). Tested by exhaustive enumeration on the kernel's real transaction alphabet, seeded samples, metamorphic permutation, differential tests against git and the kernel, and negative-oracle fixtures that must fail | High for design; the laws are MEASURED on tiny domains only | Section 6 |
| 5 | **Merge = sorted, canonical, line-oriented authored files + a keyed three-way merge + a post-merge compile.** For a fixed base the keyed merge is the join in a flat lattice, so it is symmetric, idempotent and associative where defined (proof in 7.3, 3000 seeded trials pass). It does not preserve every cross-record invariant (measured on two examples, 6.3), so the compile step reports `Findings(M) - (Findings(O) union Findings(T))` as semantic conflicts | High | S1 (Definition 6 as classification; Theorem 1 not applied), MEASUREMENT sections 6.2 and 6.3 |
| 6 | **The ledger and evidence are grow-only sets of content-addressed entries, not sequences.** The link record's `ledger_seq` is an AUTO_INCREMENT-shaped field: git's union merge produced duplicate sequence numbers in 200 of 200 trials and git's text merge conflicted 200 of 200. Request: the link record refers to `entry_id` | High (measured) | Section 6.2 scenario B, S1 Table 2 |
| 7 | **No CRDT library.** A CRDT is warranted only if four conditions all hold (concurrent writers with no review point, interactive latency, invariants that are merge-safe or enforced at commit, acceptance of convergence without human conflict review). Today none holds. The one place the structure is used is the ledger, as a sorted set of hashes merged by union | High | 7.9; S1, S2, S3 |
| 8 | **Renames are explicit records, never inferred or merged as tree moves.** Removal is deprecation first; a node is deleted only when the compiler shows no inbound links | Medium to high | S1 Claim 7 (delete under a foreign key is not I-confluent), S4 (naive tree-move merges give duplicates or cycles), okf ADR-0046 (rename = one deprecated page plus one new page today) |
| 9 | **Consistency is enforced at boundaries, drafts are tolerated.** Working trees may be inconsistent; commit and release tiers enforce. A canvas draft is a proposal value, never evidence | High | [bx] 5.6; ProofMap GAP-010 |
| 10 | **Three findings for other lanes** (section 10): the okf sync rewrites human text it should preserve (MEASURED); a committed manifest root hash conflicts on every merge of two branches that touch sources; the allocation table and this task both assign ADR-0093 | High for the first two | Sections 6.5, 7.7 |

## 1. Scope, method and limits

**Question.** Which artefacts are sources and which are derived; what is each transformation between them; which laws make each testable; where is bidirectionality genuinely needed; how are conflicts handled and merged on the graph; when is a CRDT warranted.

**What I did.** Read every dossier, SYNTHESIS.md, ARCHITECTURE.md, `graph/brief.json`; the kernel (`domain/models.py`, `policy.py`, `impact.py`, `application/service.py`, `compiler.py`); the okf lane (ADR-0045, ADR-0046, `quality/okf/pages.py`, worktree commit `4d5f7eb`) and the visual lane (ADR-0023, `docs/visual.md`, commit `27cbf6a`), read-only; the owner's private ProofMap Lite README, `gap-audit.md` and `label-conventions.md`. Opened primary sources (section 13). Wrote and ran `graph/bench/consistency_checks.py` (tests in `tests/graph/test_consistency_checks.py`).

**Limits, stated once.**
- WebSearch reported its session budget exhausted (200 of 200) when I tried once; discovery was by direct URL. Recall of the merge and bx literature is incomplete. Springer and ACM pages, and the Inria HAL and lip6 copies of the original CRDT paper, were not reachable; section 12 lists what was not read.
- Every law result is an exhaustive enumeration of a tiny domain or a seeded sample. The kernel alphabet today is two semantic transaction kinds plus layout. Nothing generalises beyond the stated domain.
- Git behaviour was measured on git 2.38.1.windows.1, one platform. POSIX is NOT_RUN.
- No claim is made that any of this makes agents or humans more effective. That is UNMEASURED (SYNTHESIS decision 9). Where a benefit is stated below it is a mechanism and a number about the mechanism.
- Hypothesis is not installed in this worktree; the bench uses seeded `random`. The property lane's strategies replace the samplers later (interface I-10).

## 2. Sources and derived artefacts

### 2.1 The selection rule

Definition (DESIGN). Let `X` be a set of authored artefacts. `Y` is *derived from X* iff there is a **fixed, versioned generator** `f` (code in the repository, identified by an id and a version that appear in `prov`) that is deterministic and pure, does not read `Y`, declares every input in `prov`, and satisfies `Y == f(X)` byte for byte for every reachable `X`. The generator restriction matters: without it the definition is vacuous, because the constant function returning `Y` would make everything derivable and the class of sources empty. This is a functional dependency between artefacts, with the dependency witnessed by a named generator. A *source* is an artefact that no registered generator produces. Rules:

- R1 One authoring home per fact. A second copy that a human edits is a redundancy with an update anomaly: edit one, forget the other. The measured instance is the UI's literal action list.
- R2 Other occurrences are generated (get-only) or referenced by id and checked. Checked relations exist only between authored artefacts, and their number is what the compiler pays for.
- R3 A derived artefact is a function of authored sources only. It may read the graph index but not another derived artefact's bytes. Then regeneration is order-independent and one pass deep; a derived-reads-derived cycle is rejected at load time.
- R4 Inferred artefacts (LLM link recovery, GraphRAG) are never sources and never gates.
- R5 Tie-break for the home of a fact: the richest artefact, the one humans already edit, the one with stable ids and a machine-parseable canonical form.

Consequence (DESIGN, reasoned; not a measured benefit). If every view is produced by a correct generator from one source, two derived views cannot disagree with each other unless a generator is wrong (G4 tests that) or a derived file was hand-edited. So the compiler does not need a relation check between two *derived* views; it needs one check per derived view against its source, and relation checks only between *authored* artefacts (UI sidecar to markup, term registry to code, intended architecture to import graph). Two tiers of that per-view check differ in what they detect:

- The **digest tier** compares the digest embedded in the view with the digest recomputed from the current source slice and generator version. It detects *source drift* (the source changed, the view did not). It does **not** detect a hand edit of the view body, because the embedded digest is unchanged by such an edit.
- The **regeneration tier** runs the generator and compares bytes. It detects body tampering and generator bugs that changed the output. Its cost is one generator run per view, `V` runs, not `V` digest comparisons.

An earlier draft compared 209 okf pages against 21,736 pairwise relations. That ratio was withdrawn: nobody proposes pairwise checks between unrelated pages, so it is not evidence of a benefit. The honest comparison is against the authored-pair relations the compiler must check, and that number is not measured here.

### 2.2 Classification

| Class | Artefact | Authoring home | Edited by | Derived from it (get-only) | Drift detected by | Lane |
|---|---|---|---|---|---|---|
| Authored source | Workflow (states, transitions, roles, guards, effects) | `domain/policy.py` baseline plus `examples/*.json` (and the Studio case store at runtime) | Human through typed `SemanticTransaction`; agents propose | Diagrams, journey text, obligations, SysML text, OKF facts blocks, UI action list (to be generated), conformance checks | Embedded `semantic_hash` (G2), regeneration compare | kernel, visual |
| Authored source | Code, tests, contracts | `src/`, `tests/`, `contracts/` | Human, agents by patch | Facts (extractors), import graph, OpenAPI (derived from routes), OKF symbol pages | Digest per hash method | quality, okf |
| Authored source | Requirements | Acceptance matrix CSV (`csv-row-v1`) | Human | OKF requirement pages, coverage report | Row digest | okf |
| Authored source | Term registry, one file per bounded context | `graph/` registry (weave, ADR-0106) | Human | OKF term pages, Contextive, Vale, cspell, SKOS exports | Term digest (`md-bold-term-v1` today) | weave, okf |
| Authored source | Declared links | `graph/links/*.jsonl` | Human; agents by patch | OKF `links` blocks, Cypher/CSV, findings | Link digest and `link_status` | weave |
| Authored source | Decision ledger | `graph/ledger/*.jsonl` | Human owner only | Link status, ack lists | Append-only gate (A4) | weave |
| Authored source | ADRs, personas, journeys (prose) | `docs/adr/`, OKF human notes | Human | Index tables, OKF ADR pages | Digest | okf |
| Authored source | Formal models and laws | TLA+, Bend, SMT files | Human, agents by patch | Witnesses, statement pins | `law-block-v1` digest against the owner-approved pin | tla, bend, smt-bmc |
| Authored source | UI sidecar model and `data-eija-key` markup | `graph/schema` sidecar plus `resources/web` | Human | UIL findings; projections when generated | Set differences over sorted ids (UIL-001 to 008) | weave, hci |
| Authored source | Intended architecture | LikeC4 or Structurizr file | Human | Reflexion result vs the import graph | Exact set difference (WV-026) | weave, quality |
| Derived, get-only | Diagrams (Mermaid, PlantUML, DOT), SysML v2 text | (none) | Nobody: regenerated | | `prov` digest, regeneration compare | visual, weave |
| Derived, get-only | Generated checks, obligations, exports (Cypher/CSV, SCIP, Soufflé, SKOS) | (none) | Nobody | | Same | weave |
| Derived, get-only | Graph index, findings, SARIF | (none) | Nobody | | Rebuild twice, equal root hash | weave |
| Derived, recomputed | Evidence and receipts | Raw observations | Checker | | Recomputed on read, never trusted | kernel |
| Mixed (lens with complement) | OKF page = generated blocks (`facts`, `links`) plus human notes | Blocks: sources; notes: human | Blocks by sync; notes by human | | Laws C1 to C4 | okf |
| Proposal, never truth | Canvas edits, imported diagram files, agent-suggested links, renames and fixes, inferred edges | (none) | Human, agents, tools | | Kernel `apply_transaction`, compiler, human decision | weave, agents |

### 2.3 Two spaces

The Studio has a runtime space (a `Workflow` candidate in a case store, changed by `SemanticTransaction`s through the kernel `apply_transaction`, guarded by `expected_version`) and the repository space (git-tracked files). The graph indexes the repository space and imports runtime outputs only as evidence (receipts, `semantic_hash`). Canvas translation (T2) lives in the runtime space. Merge (T9), ack (T10), rename (T8) live in the repository space. The two meet at one point: a `semantic_hash` and a receipt, both digests, so neither space stores the other's truth.

## 3. What "consistent" means, and when it is enforced

| Notion | Predicate | Checked by | Cost |
|---|---|---|---|
| Generated consistency | `x == tau(slice(s))`; sound cheap form: the embedded `H(m, slice)` equals the recomputed one and the generator version is in `prov` | Fast tier: digest compare (detects source drift only; a hand edit of the body is not seen). Full tier: regenerate and compare bytes (detects body edits and generator drift) | One digest per view; the full compare costs one generator run per view |
| Link consistency | `link_status(link, current_digest, ledger) == COVERED` | Rule WV-005 | One digest per linked slice |
| Relational consistency | A named violation query returns zero rows | Rule runner | Per rule, with early cutoff on read relations |
| Merge consistency | `Findings(M) - (Findings(O) union Findings(T))` is empty | Post-merge compile | One extra compile of the merged tree |

The undeclared-input caveat applies to the cheap form: if a generator reads something not in `prov`, a matching digest can hide a stale view. The full tier and the release tier's double rebuild exist for that reason.

Tiers, and where drafts are tolerated:

| Tier | Trigger | Enforces |
|---|---|---|
| Working tree, editor, agent loop | Any edit | File-local rules and G2 digests only; the tree may be inconsistent (drafts) |
| Fast (pre-commit) | Commit | All digest checks, rules, laws on the reference alphabet, post-merge compile after a merge |
| Full | Local, serial | Regeneration compare, permutation harness, differential tests, property samples |
| Release | Release | Double rebuild equal roots, POSIX goldens (NOT_RUN today), external validators |

A canvas draft is a proposal value that the human submits; it is not written to `localStorage` and treated as evidence (ProofMap Lite GAP-010: browser-local drafts invisible to agents).

Three sync operations, and nothing else:

| Operation | What it does | Deterministic | Authority | Reversible |
|---|---|---|---|---|
| Regenerate | Rewrites derived artefacts from sources | Yes (G1, G5) | Anyone; the gate recomputes | Yes |
| Propose | Emits a patch, an `Accepted(txs, layout, amendments)` or `Rejected(code)`, a resolved merge file | The translator and merge are; the producer (agent) is not | Anyone; nothing applies | Yes (a value) |
| Ack / merge / commit | A human appends a ledger entry, resolves a merge, commits | Given the same inputs | Human owner only | Ledger append-only; git history |

## 4. Where bidirectionality is genuinely needed

Test (DESIGN). A view needs a `put` iff (a) a human authors information in it that is not derivable from the source (a non-empty, valuable complement), and (b) those edits can be stated as typed operations on stable ids. If (a) fails, generate. If (a) holds and (b) fails, treat the view as a source and check the relation. Each `put` costs a translator, a complement, ten laws and a negative-oracle suite; a generator costs G1 to G7.

| View or pair | Human authors info in it? | Typed ops with stable ids? | Decision | Cost | Revisit when |
|---|---|---|---|---|---|
| Mermaid, PlantUML, DOT diagrams | No | n/a | Get-only (exists, ADR-0023) | G1 to G7 | A second workflow kind or unreadable layout |
| SysML v2 text, exports (Cypher, SCIP, SKOS...) | No | n/a | Get-only | G1 to G3, G7 | never for edits |
| OKF page | Yes: notes | Blocks are delimited by markers | Lens with complement (exists) | C1 to C4 | Notes need machine meaning: then promote to a typed sidecar |
| Canvas (draw.io, React Flow) editing the workflow | Layout only is new; the semantics is already authorable through the Studio's typed edit | Yes, if the canvas reports element ids | Deferred. Proposal-only translator T2 with laws L1 to L10 | Translator about 70 lines and law suite about 180 lines in the bench sketch, plus a canvas spike | The owner wants to author transitions by drawing, or the transaction alphabet outgrows a form (today 2 kinds) |
| Imported `.drawio` or SysML file | Yes, if someone drew | Only if cells carry a semantic id (ProofMap uses a labelled `id:` property) | Import as a proposal: parse, diff against the model, emit `Edit`s, translate. Never sync | Parser plus T2 | Same |
| UI sidecar vs markup and API | Yes, both authored | Ids (`data-eija-key`, `operationId`) | Check the relation (UIL rules); generate the action list from the model to remove the redundant copy | Rules | The UI is componentised |
| Code stubs from the model | No after creation | n/a | Model to obligations and checks only (get-only); stubs are create-once scaffolds; then code is a source | G1, G2, E4 | never for regenerate-over-code |
| Code to model | No: extraction is one-way | n/a | Extractors with provenance labels; findings, never write-back | E1 to E5 | never |
| Term registry vs code identifiers | Both authored | Term id, binding URI | Check the bijection; a rename is a proposal via T8 | Rules, codemod | never |
| Rename of an id | One intent, many sources | Yes | REN with explicit record (multi-source put from one intent) | R1 to R4 | never inferred |
| Link baseline | A human decides "reviewed" | Yes: link id and digest | ACK put, subject-bound | A1 to A5 | never automatic |

Why not bidirectional everywhere. Practitioner evidence reported in [mde]: whole-system UML and round-trip code generation are what people abandon, and narrow, textual, generated views survive; one case reported a certification cost increase because generated code was hard to read (single anecdote). Bidirectional code sync is exactly the pattern with the least reported success and the largest determinism surface. The kernel also forbids the shape: agents and providers never apply, so an automatic write-back has no legitimate actor.

## 5. Transformations and laws (summary)

Full cards, signatures and law statements: [transformations.md](../../../graph/schema/transformations.md).

| ID | Transformation | Class | Laws | Status |
|---|---|---|---|---|
| T1 | Model to diagram | GEN | G1, G2, G4 to G7 | exists (visual) |
| T2 | Diagram edit to semantic transaction | PROP | L1 to L10 | bench; product in ADR-0105 |
| T3 | Model to SysML v2 text | GEN | G1 to G3, G5, G7 | DESIGN |
| T4 | Model to obligations, checks, create-once stubs | GEN | G1, G2, G5, G7, E4 | DESIGN |
| T5 | Model to UI projection; UI relation checks | GEN, CHK | G1 to G3; UIL rules | DESIGN |
| T6 | Model and graph to OKF pages | GEN with complement | G1, G2, G7, C1 to C4 | exists (okf); one finding |
| T7 | Code to facts; intended vs actual architecture | EXT, CHK | E1 to E5, G3 | DESIGN |
| T8 | Rename | REN | R1 to R4 | DESIGN |
| T9 | Three-way merge plus post-merge compile | MRG | M1 to M8 | bench |
| T10 | Ack | ACK | A1 to A5 | DESIGN |
| T11 | Graph to exports | GEN | G1, G2, G5, G7 | DESIGN |

**How the laws are tested** (Section 3 of transformations.md gives the tiers):

| Technique | Applies to | What it is | Oracle |
|---|---|---|---|
| Exhaustive enumeration | Lens laws on the kernel alphabet | Every edit x every base, every permutation of a batch | Law holds on all pairs or a counterexample prints |
| Seeded sampling | Merge laws M1 to M5; later lens laws | Fixed-seed random cases; Hypothesis strategies when the property lane lands | Same; the seed and domain are printed |
| Metamorphic permutation | G1, E1, E2, M1, L5 | Shuffle file, state, transition, guard or side order; compare bytes | One distinct output |
| Differential | M7; incremental-equals-clean; G4 | Independent implementation: `git merge-file`, the kernel `apply_transaction`, an independent diagram reader | Agreement whenever both are defined |
| Round trip | E4, R3, C3, G5 | generate then extract; rename then inverse; sync twice; write then regenerate | Byte equality |
| Negative oracle | Every law suite | A deliberately broken implementation must fail at least one law | Detection |
| Idempotence | G5, C3, A2, M3 | Apply twice | Equal to once |

## 6. Measurements from the reference harness

Reproduce: `python graph/bench/consistency_checks.py` (about four minutes, dominated by about 1,600 git processes; `... keyed_merge_laws lens_laws_on_kernel_alphabet` selects checks). Output is canonical ASCII JSON, seeded, no timestamps. Tests: `python -m pytest tests/graph/test_consistency_checks.py`. Kernel imported read-only; git 2.38.1.windows.1; Windows 11; Python 3.12.

### 6.1 Keyed merge laws (MEASUREMENT)

3000 seeded trials, 6 keys, values `a`, `b`, `c` or absent, one shared random base, three replicas each editing a key with probability 0.12. Results: symmetric 3000/3000, identity 3000/3000, idempotent 3000/3000, associative-when-defined 3000/3000, "defined iff at most one distinct value differs from the base per key" 3000/3000. Both regimes exercised: 2758 trials fully defined, 242 with a conflict. A first version of the sampler drew independent replicas and was defined in only 39 of 3000 trials, which made associativity vacuous; the sampler was changed to derive replicas from the base, and the count of defined trials is now reported so vacuity is visible.

### 6.2 git's line merge versus the keyed merge on line files (MEASUREMENT, 200 trials per row, base of 20 lines)

| Scenario | git text merge conflicts | keyed merge conflicts | git clean result equals keyed result | Model (PREDICTION) |
|---|---|---|---|---|
| A. Sorted set, each side adds 1 record (random hash-like keys) | 21 of 200 (105 per mille) | 0 | 179 of 179 | 90 per mille |
| A. Each side adds 2 | 60 of 200 (300) | 0 | 140 of 140 | 307 |
| A. Each side adds 3 | 96 of 200 (480) | 0 | 104 of 104 | 543 |
| A. Each side adds 2, git `--union`, then sort and dedupe | 0 (union takes both) | | equals set union in 200 of 200 | |
| B. Append-only ledger with sequence numbers, each side appends 1 | 200 of 200 | | | conflict certain (same gap) |
| B. Same, git `--union` | 0 | | duplicate `seq` in 200 of 200 | |
| C. Each side edits a different existing record: adjacent lines | 20 of 20 | 0 | | |
| C. Non-adjacent | 0 of 180 | 0 | 180 of 180 | |

Calibration (exhaustive, base of 12 lines, every pair of insertion gaps, all distances reported): git conflicts iff both sides insert into the same gap (13 of 13) and at no gap distance from 1 to 12 (0 of 24, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2 pairs). The model: with a hash-sorted set of `n` random keys the gaps are unequal, so P(same gap) for one insertion each is `2/(n+2)`, not `1/(n+1)`; the first version of this model used `1/(n+1)` and predicted 48 per mille against 105 measured, which is how the unequal-gap correction was found. The simulated model (100,000 samples) is within about two standard errors of the measurement (3 by 3: 543 predicted, 480 measured; standard error about 35). Reading: for a ledger of `n = 200` lines the single-add false conflict rate is about `2/202`, one per cent, and grows with the number of concurrent adds. **Assumption stated:** the model and the measured rows use uniform random hash-like keys. For human-keyed files (two branches appending REQ-101 and REQ-102) inserts cluster in the same gap and the rate is higher; the one per cent figure holds only for hash-sorted keys. It is zero under the keyed merge and under the union driver.

Findings: (i) whenever git merges cleanly the keyed merge agrees (603 of 603 across scenarios A and C), so the keyed merge only resolves cases git calls conflicts (M7); (ii) an append-only file with sequence numbers conflicts every time and union silently corrupts the sequence: `ledger_seq` cannot survive parallel worktrees; (iii) sorting by content hash spreads insertions over gaps and turns a certain conflict into a `2ab/(n+2)`-scale one, and a set-shaped file removes it under union.

### 6.3 Invariants a clean keyed merge does not preserve (MEASUREMENT, kernel `Workflow`)

Records keyed `state:<name>`, `transition:<id>`, `initial_state`; merged with `merge3`; rebuilt through `Workflow(...)`. Two levels are kept apart. *Structural* validity is what the `Workflow` constructor accepts (unique action, no dangling state); it is computed for both sides by revalidating their dumps, not assumed. *Policy* findings are what `check_policy` returns; in these scenarios **both sides already carry policy findings** (they add an unsupported action; 1 or 2 findings per side), so the invariants tested are the structural ones, and the policy set difference `Findings(M) - (Findings(O) union Findings(T))` can be computed only when the merged workflow is structurally valid. For the two invalid merges the run is a **structural-error illustration** of M8, not a set difference of `Finding` objects.

| Scenario | Sides structurally valid (computed) | keyed conflicts | Merged | Emergent structural error | Emergent policy findings | Shape (Bailis Table 2) |
|---|---|---|---|---|---|---|
| Both add an `Escalate` action under different transition ids | yes, yes | 0 | structurally invalid | `Duplicate or ambiguous transition/action` | not computable | Uniqueness with a chosen value; not I-confluent under `merge3` (same shape as Claim 3) |
| One removes state `Rejected` with its transitions; the other adds a transition into `Rejected` | yes, yes | 0 | structurally invalid | `Dangling transition state` | not computable | Foreign key, delete; not I-confluent under `merge3` (same shape as Claim 7) |
| Each adds a different unused state (control) | yes, yes | 0 | valid | none | none (empty set difference) | Insert only; preserved (same shape as Claim 6) |

Each invariant tested (unique action, no dangling state) holds on both sides and fails on the merge, with zero keyed conflicts. Two counterexamples and one control on one tiny alphabet: enough to show the classes are real, not enough to characterise the workflow schema.

### 6.4 Lens laws on the kernel's real alphabet (MEASUREMENT, exhaustive)

Edit alphabet of 10 (add the Recommend edge, retarget Reject to Submitted or Recommended, move a node, garbage edits) x 2 bases (baseline, candidate). The reference translator and the four broken translators are written by the same author, so the negative-oracle result below shows that the suite is not vacuous against these mutants, not that it detects broken translators in general.

| Law | Result |
|---|---|
| L1 GetPut | 3 of 3 no-op pairs |
| L2 PutGet modulo layout and declared amendments | 5 of 5. Partly definitional: `alpha` is the difference between the intended and the actual view, so the content of the law is the bounded-by-declared-actions clause, and `AMENDMENT_POLICY` is set by hand to the measured kernel behaviour |
| L2b PutGetPut-shaped stability (replaying an accepted edit on its own result is a no-op) | 5 of 5. Foster et al. discuss PutGetPut (Mu et al.) as the standard weakening of PutGet; this check is non-vacuous under amendments because the result already contains the kernel's completion of the edit |
| L3 conditional PutPut | 5 of 5 |
| L4 layout independence | 9 of 9 |
| L5 order | 1 distinct batch result over 6 permutations; naive input-order application fails in 3 of 6 |
| L6 non-commutation is typed | 4 of 4 hand-written fixture batches (two conflicting edits of one slot are `Rejected(CONFLICTING_EDITS)`; identical duplicates and disjoint slots are accepted). No negative oracle; the general case is DESIGN |
| L7 totality | 20 of 20 pairs return Accepted or Rejected; nothing raises |
| L8 purity | semantic hashes unchanged. Only this half is tested. The AST test that the module imports no apply or write function is DESIGN: the bench legitimately calls the pure kernel `apply_transaction` for its dry run, and "apply" in L8 means the Studio service or store write, which the bench does not import |
| L9 applicability | 7 of 7 accepted proposals apply |
| L10 identity by id | 6 of 6 (unknown node and label variants of an existing id are `Rejected(UNKNOWN_NODE)`; scoped to edits of elements that must already exist) |
| Negative oracle (author-written mutants) | The reference passes; `bad_getput` is caught by L1 and L2b, `bad_layout` by L4, `bad_putget` by L1 and L2, `bad_unapplicable` by L1, L2b and L9 |
| Coverage | Laws exercised: L1, L2, L2b, L3, L4, L5, L6 (fixtures only), L7, L8 (purity half), L9, L10. L8's AST half is DESIGN. L6 has no negative oracle. So 9 of the 10 numbered laws are exercised in full or in part on the reference alphabet, and one half-law and one absent oracle are open |

The reflective update is real and large enough to matter for a human: drawing the single edge `Submitted --Recommend--> Recommended` makes the kernel rewire two other edges, reported as four amended edges (Approve and Reject each move their source from Submitted to Recommended). Classical PutGet (`get(put(a, c)) = a`) fails there; the law is weakened to "modulo declared amendments", and the amendment is returned to the human. The literature's own weakening is PutGetPut (Foster et al., discussion of copy and merge lenses, crediting Mu et al.), tested here as L2b. Retarget and layout edits have empty amendments.

### 6.5 OKF page sync as a lens with a complement (MEASUREMENT)

Parsing `quality/okf/pages.py` with `ast` (the bench prints the sha256 of the okf worktree's *working copy* as `pages_py_sha256_of_okf_working_copy`; it changes whenever that lane edits the file. This session it printed `6c82c254...`; the value first recorded, `f55816f0...bdcf4b`, was the committed content at okf worktree commit `4d5f7eb`. The result below does not depend on which) and running its `render_body`: generated regions are replaced and the operation is idempotent in all three fixtures; human text is preserved in the plain case and **not** preserved when the notes contain three or more consecutive newlines, in prose or inside a fenced block, because `re.sub(r"\n{3,}", "\n\n", body)` runs over the whole body. Severity low (whitespace), but it violates C1, and a fenced code block with blank lines is altered. Passed to the okf lane (section 10).

## 7. Conflicts, merge and concurrency

### 7.1 Taxonomy

| # | Conflict | Example | Detected by | Resolved by |
|---|---|---|---|---|
| K1 | Textual (line) | Two adds into the same gap of a sorted file | git text merge | `merge3` resolves it when keys differ |
| K2 | Keyed record | Both sides change one record differently; edit versus delete | `merge3` conflict `{key, base, ours, theirs}` | Human picks one or writes a third value |
| K3 | Emergent (semantic) | Clean merge; duplicate action, dangling link, cycle, requirement left without a verifier | Post-merge compile, M8 | Human; agents may propose a patch |
| K4 | Identity | One side renames an id, the other edits or links it | `merge3` (record changed on both) or WV-008, WV-001 after merge | Human; the rename record makes it explicit |
| K5 | Stale acknowledgement | An ack on one branch, a code change on the other | Not a conflict: the ack is bound to a digest, so the merged status is SUSPECT by definition | Human re-reviews |
| K6 | Ledger fork | Two entries for one subject with the same `prev` | A5, reported as CONFLICT | A later entry naming both as `prev` |
| K7 | Pseudo conflict | Both sides made the identical change | `o == t` in `merge3`; M3 | Automatic |
| K8 | Derived-file conflict | A generated file, manifest or index differs on both sides | Rebuild, compare | Take either side, regenerate |

### 7.2 Make the files mergeable before writing any merge code

Authored graph files are line-oriented: one canonical record per line (RFC 8785 subset), sorted by a total key, LF, UTF-8, one record per claim, stable ids. Git's line merge then behaves like a set merge for adds and for edits of different records (6.2: 0 of 180 non-adjacent edit pairs conflicted). Pretty-printed multi-line JSON and array-indexed pointers (RFC 6901) are avoided: an insertion shifts every later index and moves many lines. Sharding by key prefix is available if a file grows, and reduces adjacency.

### 7.3 Keyed three-way merge: definition, theorem, limits

Definition. Records live in maps `K -> Rec` (absent key = absent record). For a fixed base `b`, define on `Rec union {absent, TOP}` the operation `x v_b y`: `x` if `y = b`; `y` if `x = b`; `x` if `x = y`; `TOP` otherwise; `TOP` absorbs. `merge3(b, o, t)` is this operation applied per key; a key with result `TOP` is a conflict; keys are visited in sorted order.

Theorem (DESIGN, elementary, proof here). For a fixed `b`, `v_b` is commutative, associative and idempotent, with identity `b` and top `TOP`.
Proof. For a finite multiset `X` of values let `N(X)` be the set of distinct elements of `X` that differ from `b`. Claim: folding `v_b` over `X` in any grouping and order gives `b` if `N(X)` is empty, the single element if `|N(X)| = 1`, and `TOP` if `|N(X)| >= 2` or `TOP` in `X`. By induction: `x v_b y` has `N({x, y}) = N({x}) union N({y})` and returns per the same three cases (if `y = b` then `N(y)` is empty and the result is `x`; if `x = y` the union has one element). The result depends on `X` only through `N(X)`, so any bracketing and any order give the same value. `b` is the identity, `TOP` absorbs, `x v_b x = x`. QED.

So per key the states form a join-semilattice with bottom `b`, incomparable changed values, and top `TOP`; `merge3` is the pointwise join. That is the state-based convergence condition of the CRDT literature (replicas that received the same updates reach the same state deterministically; Preguica, Baquero, Shapiro overview, S2), relative to the base. M5 follows: the merge is defined iff every key has at most one distinct changed value. Measured consistent with 3000 trials (6.1).

Hypotheses and limits, stated so they cannot be overread.
- H1: all replicas descend from one base `b` and are merged against that same `b`. With criss-cross histories git picks merge bases pairwise, and associativity across different bases is not claimed.
- H2: values are compared as canonical bytes; a whitespace-different but semantically equal record is a conflict. The canonical writer (ADR-0091) removes this.
- H3: `TOP` (a conflict) needs a human decision, which is new information; a resolved file re-enters as an ordinary edit. The lattice describes the automatic part only.
- H4: this says nothing about invariants across keys. That is 7.4.
- Diff3 has no such structure. Khanna, Kunal and Pierce report that diff3's properties are "rather delicate", several natural intuitions are false in general (idempotence, stability, near-success on similar replicas), and that alignment is easy "where keys are available" (S5). Keys remove the alignment problem, which is why a keyed merge on keyed data is the cheaper and more predictable choice.

Records merge atomically, not field by field. A link is one claim; merging `kind` from one side and `to` from the other can produce an ill-typed link that neither author wrote. Field-wise merge is admitted only for artefacts whose fields are independent by schema, and each such artefact must say so.

### 7.4 Which invariants survive a merge (I-confluence)

Bailis et al. define an invariant-and-operation set as I-confluent when merging any two valid states reachable from a common ancestor gives a valid state (Definition 6), and prove (Theorem 1) that in their system model a coordination-free, convergent, available execution exists iff the set is I-confluent (S1, full text read). Their model has replica states that are sets of versions and a commutative, associative, idempotent merge (set union in the initial model). Our merge is not set union, so I use Definition 6 as a *classification tool* over `merge3` and **do not apply Theorem 1**: a smarter merge function (one that cascades a delete, or rejects a duplicate) could preserve invariants that `merge3` does not. The classification below therefore says "not I-confluent under `merge3`", backed by a measured or constructed counterexample, never "coordination is unavoidable". Their Table 2 (claims 1 to 8) supplies the *shapes* of invariant; it is cited as analogy for the shape, not as proof for our merge.

| Invariant | Rule | Under `merge3` | Evidence | Consequence |
|---|---|---|---|---|
| Per-record well-formedness (edge signature, mandatory guards) | WV-002; `Transition` validator | Preserved: `merge3` takes every merged record whole from one side, and each side's records are individually valid. Elementary argument, no citation needed. (Bailis Claims 1 and 2 concern per-item equality and inequality constraints; they are not the reason.) | Elementary; the fixture in 6.3 | No post-merge risk from this invariant |
| Uniqueness of a human-chosen id or value | WV-003; `Workflow` unique action | Not preserved under `merge3` | MEASURED 6.3; same shape as Bailis Claim 3 | Post-merge compile. Prefer content-derived ids where the id has no human meaning |
| Uniqueness of a generated sequence number | `ledger_seq` | Not preserved | MEASURED 6.2 B (200 of 200); same shape as Bailis Claim 5 (AUTO_INCREMENT) | Replace with content-addressed ids |
| Foreign key, insert | WV-001 when a target is added | Preserved | Same shape as Bailis Claim 6 (insert) | none |
| Foreign key, delete | Dangling link | Not preserved under `merge3` | MEASURED 6.3; same shape as Bailis Claim 7 | Deprecate first; delete only when the compiler shows no inbound links. Claim 8 says cascading delete is I-confluent, but that needs the *merge* to cascade; `merge3` must not silently drop an authored link, so the compile reports it instead |
| "At least one verifier per requirement" | WV-010 | Preserved by inserts, not by deleting the last `verifies` link | Bailis's "at least one user" example | Post-merge compile |
| Acyclicity | WV-022, WV-025, WV-042 | Not preserved | Elementary counterexample: base `{a, b}`, ours adds `a -> b`, theirs adds `b -> a`; each acyclic, union cyclic. Kleppmann and Da note naive merges of tree moves give "duplicates or cycles" (S4) | Post-merge compile; rank order for new edges is not imposed |
| Link freshness (`link_status`) | WV-005 | Not an invariant of stored data; it is derived from the merged digests and ledger, so it is correct by construction | A1 (subject-bound ack) | An ack for an old digest cannot clear a newer change; no conflict class needed |
| Any derived fact | closure, findings, views | Recomputed from the merged sources | G5 | Derived facts are merge-safe trivially |

Result: only the authored, cross-record invariants need the post-merge compile, and the table says which. That is a small, listed set, not "everything".

### 7.5 Post-merge compile and emergent findings

After any merge (and after a rebase or cherry-pick) the fast tier runs the compiler on the merged tree `M` and on both parents `O` and `T` and reports `E(M) = Findings(M) - (Findings(O) union Findings(T))` as semantic conflicts (K3). Findings are sets of stable ids (rule id plus subject ids plus canonical arguments, no line numbers; finding model, allocation 0098, on disk inside ADR-0095 lint-compile-rules), so the set difference is exact and order-independent. Findings present on both parents are inherited debt, handled by the baseline ratchet, not by the merge. If a parent is unavailable (a shallow clone), the check reports NOT_RUN. This is a differential check that needs no new rule engine.

### 7.6 The ledger, acks and evidence

Problem (MEASURED 6.2 B): a sequence-numbered append-only file conflicts on every parallel append, and git's union driver "solves" it by writing duplicate sequence numbers. The current link record carries `baseline_decision = {ledger_seq, actor}`.

Design (DESIGN). The ledger is a **set of content-addressed entries**:

```text
entry    = { subject: link id, digest: the digest the reviewer saw, decision: ack | revoke,
             actor: declared id, reason, prev: [entry_id, ...] }
entry_id = sha256( domain tag || len-prefixed canon(entry without entry_id) )      # ADR-0091 encoding; prev[] is sorted before hashing
file     = graph/ledger/<shard>.jsonl, lines sorted by entry_id, no time, no sequence number
link.baseline_decision = { entry_id }        # actor lives inside the entry
```

- Current decision for a subject = the entries not named as `prev` by any other entry (the heads). One head: that decision. Two or more heads: a fork, status CONFLICT (A5), resolved by a new entry whose `prev` lists both. This is a multi-value register whose join is an explicit human act.
- A1: the ack clears the link only if the current digest equals `entry.digest`. So an ack made against old code cannot hide a later code change, on any branch, in any merge order (K5).
- A2 to A5: set semantics, order independence, append-only per commit, visible forks.
- `prev[]` is sorted (bytewise) before hashing, and the writer refuses an unsorted or duplicated `prev`; otherwise two writers who name the same parents in a different order would mint different `entry_id`s for the same decision.
- Merge, option chosen for this draft: git's built-in `union` driver (a `.gitattributes` line, committed, needs no per-clone configuration; the driver definition for custom drivers lives in `.git/config`, S6) followed by canonicalise (sort, dedupe). Union is safe here only because the file is append-only and content-addressed; the gate checks A4 (no line of the parent is missing or changed in the child), which is what catches a hand edit that union would otherwise merge. Under 6.2 A, union then sort-unique equals set union in 200 of 200 trials. The git documentation itself says of `union`: "Do not use this if you do not understand the implications", and that added lines from both sides come in no defined order (S6); the design relies on it only because a following canonicalise step imposes the order and the A4 gate checks the result.
- **UNVERIFIED: hosted merges.** The owner's flow is pull request then merge. Whether a hosting service's merge button honours `merge=union` from `.gitattributes` was not opened and not measured (the WebSearch budget was exhausted, and the bench only uses local `git merge-file`). Until it is measured, a hosted merge of two ledger branches may conflict or drop the union behaviour; the resolve command and the A4 gate remain the safety net, but the convenience is not established for that path.
- **Considered option: one file per entry**, named by `entry_id` and sharded by hash prefix (for example `graph/ledger/ab/abcdef....json`). Two branches adding entries add different files, so git cannot conflict at all; no `.gitattributes` line and no per-file sort or dedupe are needed; append-only is a trivial check (no path of the parent is missing or changed); and a hosted merge behaves like a local one. Costs: many small files (the ledger is human-rate, so hundreds to low thousands), slower whole-ledger reads, and a review diff that shows one file per entry. It is the stronger option on merge safety and simplicity. The single sorted file stays as the draft default only because the link record and the okf lane already assume the path `graph/ledger/*.jsonl`; the choice is a layout change, not a semantic one (the set of `entry_id`s is identical). Recommendation: prefer file-per-entry unless the owner wants one file, and decide before the ledger is first written (open question 2).
- Evidence entries (receipts, witnesses, link certificates) are the same shape: content-addressed, grow-only. A contradiction is CONFLICT in the status join, not a merge failure ([math] 2.8).
- Interface change requested of the link-record owner (the allocation table gives that record to ADR-0093; see section 10): replace `ledger_seq` with `entry_id`.

### 7.7 Derived files that are committed

Some derived artefacts are committed on purpose: diagrams under `docs/diagrams/`, the okf bundle, generated tests, the graph manifest. Policy: on a merge conflict in a derived-committed file take either side and regenerate; the gate compares to a fresh build. The okf lane already expects "one sync commit" when lanes merge (ADR-0045).

Specific hazard (PREDICTION, follows from the definition): a committed `manifest.json` holding the graph root hash conflicts on every merge of two branches that change any indexed source, because the root is a function of all sources and therefore differs on both sides from the base. With several lanes in parallel worktrees that is nearly every merge. Recommendation: keep pins (schema version, extractor pins) in the manifest, and record the root hash in the release receipt and in the double-rebuild gate output instead of in a per-commit file. D-17 and D-24 only require that two clean rebuilds agree, so this needs no change to the determinism doctrine (section 10, F2).

### 7.8 Runtime cases: optimistic concurrency and replay

In the runtime space the kernel already refuses instead of merging: every command carries `expected_version`, the compiled packet blocks with `STALE_BASELINE` when the case's baseline version differs from the active one, and `approve` fails with `SUBJECT_CHANGED` if the reviewed subject hash moved (read in `application/compiler.py`, `service.py`). A case stores its `transactions` list, which is an operation log over a tiny alphabet. So a rebase onto a new baseline can be defined as *replay*: apply the stored transactions to the new baseline through `apply_transaction`, with kernel errors (`MEANING_REQUIRED`, `POLICY_BLOCKED`) as typed conflicts (DESIGN, needs a Studio change and its own ADR; law: replay is deterministic, and replay of commuting transactions equals the merge of results). Not built here; the point is that the operation-based alternative already exists in the data model and needs no CRDT.

### 7.9 When is a CRDT warranted

Criterion (DESIGN, using S1's I-confluence and S2's convergence condition). A CRDT for an artefact is warranted iff all four hold:
1. Two or more writers modify the same artefact concurrently with no review point between them.
2. The latency requirement is below a git round trip (interactive, seconds), so merge-on-integrate is unacceptable.
3. Every invariant over the artefact is I-confluent under the CRDT's merge, or is enforced by a coordinated commit step anyway.
4. The owner accepts convergence without a human reviewing each conflict for that artefact.

| Candidate | 1 | 2 | 3 | 4 | Verdict |
|---|---|---|---|---|---|
| Ledger, evidence set | Yes (many worktrees) | No | Yes (grow-only, content-addressed) | Yes (forks become explicit heads) | Use the structure (sorted set, union), no library |
| Declared links, term registry, requirements | Some | No | Partly (7.4) | No: a silently merged or last-writer-wins ack loses a human decision | Keyed merge plus compile |
| Workflow model in a case | No: single local owner (POC decision), `expected_version` | No | No: uniqueness and policy are not I-confluent (6.3) | No | Optimistic concurrency and replay |
| Canvas, several people drawing live | Not today | Yes | Semantic part no; layout yes | Layout only | Deferred. If it happens: a CRDT document for layout and proposals *below* the translator (Automerge, MIT; Loro, MIT; Yjs, MIT), and the semantic commit stays coordinated by the kernel |
| Prose (OKF notes, ADRs) | No | No | n/a | No | git merge and a human |
| Renames, page moves | n/a | n/a | Naive tree-move merges give duplicates or cycles (S4) | n/a | Explicit rename records |

The semantic invariants of the workflow (unique action, no dangling state) are not I-confluent under `merge3` (6.3), and a CRDT's merge would have to be designed to preserve them; nothing here shows that such a merge exists or does not. Bailis et al.'s Theorem 1 is stated for their set-union model and is not applied. So the design keeps the semantic commit coordinated by the kernel even if a live-collaborative canvas is added. Licences: Automerge and Loro MIT per GitHub SPDX metadata (LICENSE text not opened), Yjs MIT (LICENSE text opened). Any adoption needs its own ADR; none is proposed.

### 7.10 Semantic merge tools

**Dolt is the closest prior art for a keyed three-way merge and was missing from earlier drafts.** Dolt (https://github.com/dolthub/dolt; Apache-2.0 per its LICENSE text and GitHub metadata, opened 2026-09-29; last push 2026-09-28, not archived) is a SQL database with git-style version control. Its merge documentation (https://www.dolthub.com/docs/sql-reference/version-control/merges, opened 2026-09-29) describes a three-way merge over base, ours and theirs, keyed by primary key, with `conflicts` tables that hold `base`, `ours` and `theirs` columns, cell-level resolution by updating `our_` columns, schema conflicts in `dolt_schema_conflicts`, and, separately, "foreign key constraints or unique key constraints" violations tracked in `dolt_constraint_violations`; all three types set the `conflicts` column of the merge result to 1. The last item is the same class as the emergent conflicts of K3 and CS-03: a merge that is clean per key but violates a cross-row constraint. So the claim that no compatible tool has a keyed three-way merge with named conflict classes is **false as a universal**; it survives only in the narrow form that none found does this over git-tracked canonical JSONL files.

Classification: Apache-2.0 makes Dolt usable as a dependency or as a separate optional process. It is not adopted as the trust path because it needs a database store (a Dolt repository with its own commit graph) alongside git, so the authored graph files would stop being the reviewed, diffable artefacts, and every clone, agent worktree and CI run would need Dolt installed and in step with git. It is kept as inspiration for the conflict vocabulary (data, schema, constraint violation) and as a possible export or query target if a relational history of the graph is ever wanted. Not measured: Dolt's merge speed, or how its constraint-violation report compares with the post-merge compile. Other keyed or structured-data merge tools may exist; the WebSearch budget was exhausted, so the survey is limited to git (`merge-file`, `union`), Mergiraf and Dolt and is not exhaustive.


Mergiraf is a syntax-aware git merge driver built on tree-sitter. Its `Cargo.toml` says `license = "GPL-3.0-only"` and its `LICENSE.txt` is the GNU GPL version 3 text (both opened 2026-09-29, https://codeberg.org/mergiraf/mergiraf). GPL-3.0-only cannot be linked into an Apache-2.0 distribution as a dependency; it is compatible as a separate, user-installed process for code files at most. It is not needed for sorted line files (the keyed merge already agrees with git wherever git is clean and resolves the rest) and never sits in the trust path: the gate is always the post-merge compile. GumTree-style tree diff stays for id-less artefacts, as in [math].

Merge driver mechanics (S6): custom drivers are defined in `.git/config`, and `.gitattributes` only selects them by name. So a custom driver is per clone, cannot be committed, and may be absent on a fresh clone or in an agent worktree. Therefore the design gives the merge as a command that reads the three index stages (`git show :1:path`, `:2:path`, `:3:path`) and writes the canonical merged file or a conflict report, and treats a driver as an optional convenience.

## 8. Schools of thought used here

Only rows with an implementable benefit. "Adopt" means used; the mechanism and cost are stated.

| School | Mechanism | Benefit (number or failure it changes) | Cost and limit | Evidence | Verdict |
|---|---|---|---|---|---|
| Bidirectional transformations, lenses | GetPut, PutGet (weakened to a PutGetPut-shaped stability check, L2b), PutPut as executable tests on translators | Catches translators that invent or lose information; makes "picture matches model" falsifiable. 4 of 4 author-written mutants detected (shows the suite is not vacuous, not evidence about real translators) | Laws hold modulo definedness; PutPut legitimately fails for merge-like views | S7 (laws quoted), 6.4 | Adapt as tests; no library (PyPI `lenses` GPLv3+ per [bx]) |
| Delta and reflective lenses | Separate delta discovery from propagation; amend the user's edit and say so | Alignment is given by ids; the amendment is shown (4 edges in the measured case) | Amendments must be declared per transaction kind | [bx] 2.1 (Diskin et al.), 6.4 | Adapt |
| Functional dependencies, normal forms (analogy only) | Y derived iff Y = f(X); one home per fact | Decides direction without tools; explains the redundant UI action list as an update anomaly; derived views need a per-view check against the source, not view-to-view relation checks (reasoned, not measured) | "Same fact" is a judgement; only a heuristic lint (CS-01) | 2.1, [ui] MEASUREMENT | Adopt as design rule |
| Order theory, join-semilattices | `merge3` is the pointwise join of a flat lattice per key | Order-independent, associative where defined; 3000 of 3000 law passes | Same-base hypothesis; a conflict needs a human | 7.3 proof, 6.1 | Adopt |
| I-confluence (Bailis et al.) | Classify each invariant as merge-safe or not | Tells which few rules need the post-merge compile; two measured counterexamples on the kernel's own `Workflow` | Manual classification; their model is set-union merge, ours is a three-way merge (used as a tool) | S1 (Definition 6 only), 6.3, 7.4 | Adopt as classification; Theorem 1 not applied |
| CRDTs (state-based) | Join-semilattice replicas | Explains why the ledger set and keyed merge converge | A library adds metadata and hides conflicts; invariants are not preserved by convergence | S2, S4, 7.9 | Structure adopted, library rejected |
| Diff3 analysis | Alignment by keys instead of by text | Avoids diff3's delicate properties on keyed data; 0 keyed conflicts against 10.5 to 48 per cent false line conflicts at n = 20 | Keys required | S5, 6.2 | Adopt keyed merge |
| Merkle, content addressing | `entry_id = H(entry)`; embedded slice digests | Deduplication, set semantics, subject-bound acks (K5 disappears) | Detects change, not truth | [math] 2.6, 7.6 | Adopt |
| Term and graph rewriting | Explicit rename records, codemods | Renames survive as edits with a map; R1 to R4 | Syntactic renames only | [code], [incr] 2.6 | Adopt |
| Category theory | Two checks: mapping totality (G3), view as homomorphism (G4) | New semantic types cannot silently vanish from a view | Functorial migration and CQL: no implementable benefit; CQL not OSI-licensed | [bx] 2.5, 4 | Two checks adopted, rest theory-only |
| Sheaf-style consistency | Overlap join: views sharing ids must agree | Localises a disagreement to two views and an id | Only needed for authored pairs; derived views agree by construction (2.1) | [bx] 2.7 | Adapt (join) |
| Tolerant consistency (VICToRy line) | Drafts may be inconsistent; enforce at commit | The canvas and the agent loop are not blocked by half-finished states | Needs a visible draft state | [bx] 4 | Adapt (tiers) |

## 9. Interfaces to other lanes and aspects

Every dependency is explicit. "Provides" and "Consumes" are from the weave side.

| # | Interface | Counterpart | Contract | Status |
|---|---|---|---|---|
| I-1 | Hash method registry and `digest(root, ref, method)` | okf lane (`quality/okf/codelink.py`, ADR-0046) | Weave consumes methods and the `repo://` grammar; proposed `workflow-semantic-v1`, `json-key-v1`, `html-key-v1`, `law-block-v1`; a shared CRLF-fold helper; a fixture test both sides run | Needs okf agreement |
| I-2 | Diagram provenance comment | visual lane (ADR-0023) | First line `eija: ... semantic_hash=...`; weave rule WV-027 recomputes and compares; the neutral `Graph`, `Sequence`, `ClassModel` are the `ViewModel` | exists |
| I-3 | `translate` protocol | agents lane (ADR-0041), Studio | `translate(Workflow, Edit) -> Accepted(txs, layout, amendments) or Rejected(code, reason)`, pure; exposed as a proposal-only MCP tool with a per-session JSON Schema of live node ids; no `apply` | DESIGN |
| I-4 | `merge3` and the resolve command | link-record and ledger design (allocation 0093 link record and 0094 ledger; neither on disk; this ADR also carries 0093) | Keyed merge on sorted line files; ledger as a content-addressed set; `baseline_decision = {entry_id}` | Change requested, section 10 |
| I-5 | Finding model and stable ids | Allocation 0098 (ARCHITECTURE section 11); on disk inside ADR-0095 lint-compile-rules | Findings are sets of stable ids so `E(M)` is an exact set difference | Needs the model |
| I-6 | Rule loader and strata | Allocation 0097; on disk inside ADR-0095 lint-compile-rules (the file named 0097 on disk is impact-ranking-math, a different topic) | New rules CS-01 to CS-05 (section 10) are ordinary rules; M8 is a differential run of the compiler | Needs the loader |
| I-7 | Permutation harness | Allocation 0099 (determinism doctrine); not on disk as its own ADR; the file named 0099 on disk is agent-interface | Add merge-side swap (`ours` and `theirs`), base file order and CRLF to the matrix; require one distinct output (M1, M6) | DESIGN |
| I-8 | Incremental engine | Allocation 0100; not on disk | Generator `prov` doubles as the cache key input; the release tier's full rebuild guards the undeclared-input risk | DESIGN |
| I-9 | `eijagraph.views` | Allocation 0105 (views, lenses, SysML emitter, reflexion); on disk as `0105-weave-human-views.md` (first filed as 00101) | Must pass the transformations.md laws; this aspect defines the laws, ADR-0105 the API and SysML emitter | Boundary to agree |
| I-10 | Hypothesis strategies | property lane | Replace the seeded samplers; results stay labelled MEASUREMENT on the tested alphabet | Later |
| I-11 | Kernel put | `src/` (read-only for weave) | `apply_transaction` is the only put; the amendment class per transaction kind is a table in the bench today (`AMENDMENT_POLICY`); the kernel exposing it would remove the duplication (separate ADR) | Question 5 |
| I-12 | Sessions | quality lane | `quality/sessions/graph.py`, tags `fast`, `full`, `release`; the git-dependent M7 check is a `release` step and reports NOT_RUN without git | DESIGN |
| I-13 | Term ids and label authority | lang aspect (ADR-0106), okf | Stable term ids so a rename is R1 to R4 and UIL-004 has a label authority | Needs agreement |

## 10. Findings for other lanes, and candidate rules

Findings (each with evidence and a proposed owner; none acted on here).

| # | Finding | Evidence | Owner |
|---|---|---|---|
| F1 | okf `render_body` collapses three or more consecutive newlines in human text (prose and fenced code), violating law C1 | MEASUREMENT 6.5, `pages.py` sha256 `f55816...bdcf4b` | okf lane: apply the collapse only inside generated blocks, or drop it |
| F2 | The committed manifest root hash is merge-hot | Definition, 7.7 (PREDICTION) | ARCHITECTURE owner: pins in the manifest, root hash in the release receipt and gate output |
| F3 | `baseline_decision.ledger_seq` is not merge-safe. Consumers of the sequence number in sibling aspects (read 2026-09-29): `graph/brief.json` `link_record`, `graph/schema/mcp-tools.md` (`baseline_ledger_seq`), `graph/schema/rules.md` (condition `{"ledger_seq": N}`), the human-views files ("ledger sequence"). Replacement: store `entry_id`; a condition becomes set membership (`ledger_has: entry_id`); if an ordinal is needed for display it is computed as the rank in the lexicographically smallest topological order of the entry DAG (ties by `entry_id`) and never stored | MEASUREMENT 6.2 B (200 of 200 conflicts, 200 of 200 duplicates under union) | Link-record and ledger owner |
| F4 | ADR numbering (see the old-to-new table after this list): this task assigns 0093 to consistency-sync, but the allocation table (ARCHITECTURE section 11) assigns 0093 to the link record and `link_status`, and sibling aspects already cite "ADR-0093" for `link_status` (agent-interface, human-views and impact-ranking design docs, `mcp-tools.md`, `views.md`). 0105 (view lenses) overlaps T2 | Read | Integrator: reconcile before commit (for example this ADR takes a free number in the block and the link-record ADR keeps 0093), then fix the citations in both directions |
| F5 | The kernel case store is not in git, so runtime edits are outside the graph until a receipt exists | 2.3 | Note for the evidence-import design |

ADR numbering, old to new (for the integrator). Every number in 0089 to 0111 is already allocated by ARCHITECTURE section 11 and 0112 is reserved, so this ADR has no free number. Proposed: keep the file `0093-weave-consistency-sync.md` until the integrator decides, and land each decision where the allocation already puts its topic:

| Decision here | Allocation slot | Note |
|---|---|---|
| Sources versus derived, one home per fact, tolerant drafts | 0089 (derived index, truth classes) | Text can move as a section |
| Ledger as content-addressed set, `entry_id`, ack subject binding, file layout | 0094 (human ledger) | Also removes `ledger_seq` from 0093 (link record) |
| `merge3`, post-merge compile, I-confluence classification, CRDT criterion | new number, or 0111 if the integrator accepts a benchmarks-and-consistency scope | No slot fits; this is the residual of this ADR |
| Lens laws L1 to L10, generation laws G1 to G7, complement laws C1 to C4 | 0105 (view lenses) | The laws are specified here, the API there |
| Cross-references written as ADR-0097, 0098, 0099, 0100, 0105 in this lane's files | ARCHITECTURE numbers, not file numbers | On disk today 0095 is lint-compile-rules, 0097 impact-ranking-math, 0099 agent-interface, 0102 formal-verification-of-weave, 0105 human-views |

Candidate rules (prefix CS to avoid colliding with WV ids; the rules aspect owns numbering):

| ID | Name | Kind | Reads | Witness |
|---|---|---|---|---|
| CS-01 | duplicate-fact-copy | graph-global, advisory | extractor literals, model sets | The literal set and the model set it equals (for example the UI's 5 actions) |
| CS-02 | generated-file-hand-edited | file-local | `prov`, regeneration | First differing byte |
| CS-03 | merge-emergent-finding | graph-global, post-merge | findings of M, O, T | The finding and the two parent ids it is absent from |
| CS-04 | ledger-fork | graph-global | ledger entries | The two heads for a subject |
| CS-05 | ledger-not-append-only-or-not-canonical | file-local, git-aware | ledger, parent commit | Missing or changed parent line; out-of-order or duplicate line |

## 11. Open questions

1. Will the link-record owner accept `entry_id` in place of `ledger_seq` (F3)? Until then the ledger cannot be merged safely across worktrees.
2. Ledger layout: one file per entry (no `.gitattributes` line, cannot conflict) or one sorted file merged with `merge=union` (needs a committed `.gitattributes` line, which is repository configuration outside this lane's ownership, and hosted-merge behaviour is UNVERIFIED)? Recommendation in 7.6: one file per entry.
3. Manifest policy (F2): pins only, root hash in the release receipt?
4. Amendment classes (I-11): should the kernel expose which transaction kinds may rewire which actions, or does weave keep a table that a test checks against kernel behaviour?
5. Does the owner want a canvas at all? If yes, a spike is needed for (a) whether draw.io preserves cell ids across saves (UNVERIFIED; the docs I opened say the file is uncompressed XML and say nothing about ids) and (b) how a React Flow canvas emits atomic edit events (not measured, needs a browser).
6. R2 needs a name-erased normaliser to accept a pure rename; is `ast-v1` with the defined name replaced by a placeholder enough, given recursion?
7. Multi-base merges: does the fast tier need to handle git's recursive merge bases, or is the single-base hypothesis acceptable because integration is by one integrator?
8. Field-wise merge for any artefact? Default is atomic records; any exception needs a schema statement of field independence.
9. Position of NOT_RUN for a missing parent in the emergent-findings check (7.5) in the status chain: inherits the open question in SYNTHESIS section 9.
10. POSIX: every byte-identity claim here is Windows only.

## 12. Gaps and UNVERIFIED

- Not read (paywalled or unreachable): Stevens on QVT-R and networks of models; Czarnecki et al.; Hofmann, Pierce, Wagner on symmetric and edit lenses; Egyed; Klare et al. on Vitruvius; Shapiro et al. (Inria HAL returned an access-denied page; lip6 refused the connection). I relied on the Preguica, Baquero, Shapiro overview abstract for the convergence statement (S2) and make no claim from the original papers.
- The EMF Compare conflict documentation URL redirected to a 404; I make no claim about its conflict taxonomy. The taxonomy in 7.1 is this lane's own.
- Mergiraf's supported formats were not opened; its licence (GPL-3.0-only) was confirmed from `Cargo.toml` and the LICENSE text. Automerge and Loro licences are GitHub metadata only (not the LICENSE texts).
- Hosted-merge behaviour of `merge=union` is UNVERIFIED (7.6). Dolt merge speed, and any keyed-merge tool beyond git, Mergiraf and Dolt: not surveyed.
- The Foster et al. copy is the authors' draft ("Vol. TBD"); numbering may differ from the published TOPLAS version. The Khanna et al. copy shows no venue.
- Bailis et al. Theorem 1 is stated for their set-union system model and is **not applied** anywhere in this design. Definition 6 is used as a classification vocabulary, and Table 2 claims are cited as the shape of an invariant, not as proof for `merge3`.
- The ProofMap Lite README and gap audit were read through the owner's `gh` login; the repository is private and unlicensed, so lessons only, no code copied.
- Not measured: agent or human benefit; merge conflict rates on real EIJA history (there is one lane's worth of history); performance of a real canvas; cost of regeneration of the visual and okf outputs.

## 13. Sources (opened 2026-09-29 by me unless marked)

| Key | Source | Used for |
|---|---|---|
| S1 | Bailis, Fekete, Franklin, Ghodsi, Hellerstein, Stoica, "Coordination Avoidance in Database Systems" (PVLDB 8(3); extended version) https://arxiv.org/abs/1402.2237 (PDF text read: Definitions 1 to 6, Theorem 1, Table 2, sections 4 and 5) | I-confluence, uniqueness, foreign key, AUTO_INCREMENT |
| S2 | Preguica, Baquero, Shapiro, "Conflict-free Replicated Data Types (CRDTs)" (arXiv title; an overview) https://arxiv.org/abs/1805.06358 (abstract) | CRDT convergence statement |
| S3 | Yjs LICENSE https://raw.githubusercontent.com/yjs/yjs/main/LICENSE (MIT, text); GitHub REST metadata for automerge/automerge (MIT), loro-dev/loro (MIT), yjs/yjs, jgraph/drawio (Apache-2.0), 2026-09-29 | CRDT library licences |
| S4 | Da and Kleppmann, "Extending JSON CRDTs with Move Operations" https://arxiv.org/abs/2311.14007 (abstract) | Naive moves give duplicates or cycles |
| S5 | Khanna, Kunal, Pierce, "A Formal Investigation of Diff3" https://www.cis.upenn.edu/~bcpierce/papers/diff3-short.pdf (text read: abstract, introduction, section 4) | diff3 properties; keys give clear alignment |
| S6 | git documentation https://git-scm.com/docs/gitattributes and https://git-scm.com/docs/git-merge-file | Driver definitions in `.git/config`; `union`; exit status |
| S7 | Foster, Greenwald, Moore, Pierce, Schmitt, TOPLAS https://www.cis.upenn.edu/~bcpierce/papers/lenses-toplas-final.pdf (text read: laws, PutPut discussion) | Lens laws |
| S8 | OKF v0.2 SPEC https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md | Links untyped, broken links tolerated, `stale_after`, no guidance on rewriting or conflicts |
| S9 | Mergiraf https://codeberg.org/mergiraf/mergiraf (`Cargo.toml` and `LICENSE.txt` opened) | Syntax-aware merge driver, GPL-3.0-only |
| S10 | draw.io file format page https://www.drawio.com/doc/faq/save-file-formats | `.drawio` is uncompressed XML; nothing on cell ids |
| S11 | ProofMap Lite (private, `gh`): README, `docs/gap-audit.md`, `docs/label-conventions.md` | GAP-010, 030, 033; `id:` label convention; model-view contracts |
| S12 | Repo files read: `src/eija_studio/domain/{models,policy,impact}.py`, `application/{service,compiler}.py`; okf worktree `quality/okf/pages.py`, ADR-0045, ADR-0046; visual worktree ADR-0023, `docs/visual.md` | Kernel behaviour, existing generators, existing lens |
| S13 | Dossiers in `docs/weave/research/` (keys at the top), read in full for [bx], and for the sections cited in the others | Prior evidence |
| S15 | Dolt https://github.com/dolthub/dolt (LICENSE text Apache-2.0; GitHub metadata) and https://www.dolthub.com/docs/sql-reference/version-control/merges | Keyed three-way merge prior art; conflict and constraint-violation tables |
| S16 | Licence texts opened 2026-09-29: OpenFastTrace `LICENSE.txt` (GPL-3.0), Doorstop `LICENSE.md` (LGPL-3.0; its `pyproject.toml` says `LGPLv3`), StrictDoc `LICENSE` (Apache-2.0) | Classification in the ADR OSS check |
| S14 | Bench and tests written and run in this worktree: `graph/bench/consistency_checks.py`, `tests/graph/test_consistency_checks.py` | All MEASUREMENT rows in section 6 |
