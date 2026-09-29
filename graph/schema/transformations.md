# Transformation contracts

Lane: weave. Aspect: consistency-sync. Date: 2026-09-29. Status: DESIGN (contracts), with reference measurements from `graph/bench/consistency_checks.py`. Decision record: [ADR-0093](../../docs/adr/0093-weave-consistency-sync.md). Reasoning, evidence and rejected alternatives: [consistency-and-sync.md](../../docs/weave/design/consistency-and-sync.md). Nothing here is implemented as product code yet; the bench file is a reference sketch that pins the laws, and the product modules (`eijagraph.views`, `eijagraph.merge`, `eijagraph.links`, extractors) must pass the same laws.

Labels: MEASUREMENT (a script ran, domain stated), PREDICTION (reasoned, not run), DESIGN (a proposal of this lane), UNVERIFIED (not opened; nothing is built on it).

## 0. How to read a contract

Every transformation below is one of six classes. The class decides which laws apply and who may run it.

| Class | Meaning | Who may run it | Writes to |
|---|---|---|---|
| GEN | Pure get: `tau(source slice) -> bytes`. No hand edits to the output. | Anyone; the gate recomputes | A derived file (or stdout) |
| EXT | Extraction: files to typed facts with provenance labels. Untrusted producer. | Anyone; the checker recomputes | The disposable index only |
| PROP | Proposal-put: a view edit becomes typed transactions, or a typed rejection. Never applies. | Human, agent, provider (proposal only) | Nothing. Output is a value |
| MRG | Three-way merge of authored, line-oriented files, then a post-merge compile | Human (git), integrator | The merge result, reviewed before commit |
| REN | Rename: one explicit `{old_id, new_id}` record plus the edits it implies in every source | Codemod, applied by a human | Authored sources, in one reviewable diff |
| ACK | Decision: append a subject-bound entry to the human ledger | Human owner only | The ledger (append-only set) |

Notation. `s` is a git tree of authored files. `slice(s, x)` is the part of `s` that a transformation reads for output `x`. `H(m, b)` is the digest of bytes `b` under hash method `m` (methods are versioned and shared with the okf lane: `ast-v1`, `ast-sig-v1`, `ast-api-v1`, `lf-sha256-v1`, `csv-row-v1`, `md-bold-term-v1`, `md-table-row-v1`; proposed `workflow-semantic-v1`, `json-key-v1`, `html-key-v1`, `law-block-v1`). `canon` is the RFC 8785 subset writer (strings, safe integers, booleans, null; no floats; ADR-0091). `prov(x)` is the provenance record embedded in a generated artefact: transformation id, transformation version, hash method, `H(m, slice)`; never a time. `==` on artefacts is byte equality.

Every transformation obeys the determinism doctrine (D-01 to D-24 in the weave architecture): sorted iteration by a total key, explicit UTF-8 and LF, no wall clock, time zone, uuid4, hostname, absolute path or locale in output, identity by id and never by label, no dependence on `PYTHONHASHSEED`, temp files in `.tmp/`. A missing prerequisite reports NOT_RUN, which absorbs PASS.

## 1. Law catalogue

Each law says what is checked, under which hypotheses, and how. Laws hold "modulo definedness" in the sense of Foster et al.: they are claimed only where both sides are defined, and definedness itself is tested (a typed rejection is a defined outcome).

### 1.1 Generation laws (GEN)

| ID | Law | How tested |
|---|---|---|
| G1 | Determinism and permutation invariance: `tau(p(s)) == tau(s)` for every `p` in the declared non-semantic permutations of `tau` (order of states, transitions, guards, effects, files; whitespace; CRLF versus LF). Equivalent to: two sources with equal semantic hash give equal output bytes | Metamorphic shuffle test over all views and formats, seeded; the visual lane already runs it |
| G2 | Provenance: the output embeds `prov(x)`; if `H(m, slice(s, x))` differs from the embedded digest the artefact is STALE. The check is sound only if the generator version is inside `prov` (an undeclared input yields stale-but-passing) | Fast tier compares digests; full tier regenerates and compares bytes; a seeded edit to each declared input must flip the verdict |
| G3 | Totality: a declared mapping `M: semantic type -> view kind or not_shown(reason)` is defined on every type of the schema; a type with no entry is a finding (WV-028) | Add a schema type in a fixture and require the finding; ProofMap Lite reached the same check independently (its model-view contracts, GAP-030) |
| G4 | Faithfulness (view as homomorphism): an independent reader `rho` (shares no code with the generator) recovers the shown part: `rho(tau(s)) == shown(s)`; a path in the model maps to a path in the view | Independent parser of the emitted text; the visual lane recovers state-diagram edges this way |
| G5 | Fixed point: regenerating a correct file gives the same bytes; `--check` never writes | Write, regenerate, compare; check mode on a read-only tree |
| G6 | Safety: every label is escaped; an untrusted model file cannot inject syntax into the output | Fuzzed labels through the real renderers (visual lane `diagrams_syntax`), NOT_RUN without them |
| G7 | Canonical bytes: UTF-8, LF, one final newline, sorted, no floats | Byte-level grep gate and golden files; Windows and POSIX goldens (POSIX is NOT_RUN today) |

### 1.2 Lens laws for proposal-puts (PROP)

A view `V` over source `S` has `get: S -> V`. A view edit is translated by `translate: (S, Edit) -> Accepted(txs, layout, amendments) | Rejected(code, reason)`. The only `put` is the kernel `apply_transaction`. Layout is the complement `LayoutChange` and never enters the semantic hash. Foster et al. define GetPut as `put(get(c), c) = c`, PutGet as `get(put(a, c)) = a`, and PutPut as `put(a', put(a, c)) = put(a', c)`, all "if both operations are defined" (opened 2026-09-29; they also state PutPut is not required for their tree combinators). EIJA weakens PutGet with a declared amendment (Diskin, Koenig, Lawford call this a reflective update) and adds five laws about the translator itself. The literature's own standard weakening is PutGetPut (Mu et al., discussed by Foster et al. in their treatment of copy and merge lenses); it is tested as L2b, because L2 alone is partly definitional (the amendment is computed as the difference between the intended and the actual view, so the law's content is the clause that the amendment stays within the declared amendment class).

| ID | Law | Statement | Test (domain) |
|---|---|---|---|
| L1 | GetPut | An edit that asks for what the view already shows yields `Accepted(txs = [], layout = [])` and the same semantic hash | Exhaustive over the alphabet x bases |
| L2 | PutGet modulo layout and declared amendments | Let `intended = apply_view_edit(get(s), e)` and `after = get(put(s, txs))`. Let `alpha_plus = (after - get(s)) - (intended - get(s))` and `alpha_minus = (get(s) - after) - (get(s) - intended)` (edges; likewise states). Then `after == (intended - alpha_minus) + alpha_plus`, and `alpha` is returned with `Accepted`, and every edge in `alpha` has an action in the declared amendment class of the transaction kind; `alpha` is empty when `txs` is empty | Exhaustive; classical PutGet holds exactly where `alpha` is empty |
| L2b | PutGetPut-shaped stability | Replaying an accepted edit on its own result gives `Accepted(txs = [], layout = [])`: `put(get(put(a, c)), put(a, c)) = put(a, c)` in the notation above, checked by replay. Non-vacuous under amendments, because the result already contains the kernel's completion of the edit | Exhaustive over accepted (edit, base) pairs |
| L3 | Conditional PutPut | For two edits of the same slot, translate-and-apply of the second on the result of the first equals translate-and-apply of the second alone (last edit wins). Claimed only for slots where it is tested; map-like and merge-like views may legitimately fail it (Foster et al.) | Exhaustive over same-slot pairs |
| L4 | Layout independence | A layout edit yields `txs = []`, changes no semantic hash, and touches only the complement | Exhaustive over nodes |
| L5 | Order | The batch translator sorts edits by dependency (enabling before dependent, semantic before layout, canonical tiebreak). Its result is identical for every permutation of the input batch. Naive input-order application is measured, so the need for ordering is a number, not an opinion | All permutations of a 3-edit batch |
| L6 | Non-commutation is typed | Where two edits do not commute and no dependency order exists, the batch is `Rejected(code)`; it is never silently reordered into a different meaning. Implemented for the case of two different edits of one slot (`CONFLICTING_EDITS`) | 4 hand-written fixture batches (MEASURED, no negative oracle); DESIGN for the general case |
| L7 | Totality | Every input, including garbage, returns `Accepted` or `Rejected(code)` with a stable code; the translator never raises | Includes an empty tuple, unknown kinds, unknown nodes, wrong arity |
| L8 | Purity and no authority | `translate` does not mutate its inputs, does not call `apply`, and returns proposals only. "Apply" here means the Studio service or case-store write (the one that changes runtime state). The pure kernel `apply_transaction` is allowed inside `translate` for its dry run, because it returns a new value and writes nothing | Frozen models; semantic hash before and after (MEASURED). **DESIGN, not implemented:** an AST test that the product module imports no Studio service or store-write function |
| L9 | Applicability | Every `Accepted` proposal applies through the kernel put without refusal (partiality is turned into a typed rejection by a dry run) | Every accepted pair is applied |
| L10 | Identity by id | An edit of an element that must already exist names it by stable id, never by label or position; an unknown id (or a label variant of an existing id) is `Rejected(UNKNOWN_NODE)`. Edits that create elements are governed by L1 and L9 | Fixture: 3 unknown ids x 2 bases (MEASURED) |

Every law suite ships a negative-oracle fixture: deliberately broken translators (emits a transaction for a no-op, retargets the wrong slot, leaks layout into the semantic model, skips the dry run) must each be detected by at least one law. The reference suite passes on the reference translator and fails on all four (MEASUREMENT, table in the design doc). The four mutants are written by the author of the reference translator, so this shows the suite is not vacuous against these mutants; it is not evidence that it catches translator bugs in general. Coverage today: L1 to L5, L7, L9 and L10 are exercised in full on the reference alphabet, L6 on fixtures without a negative oracle, L8 only in its purity half (the AST half is DESIGN); so 9 of the 10 numbered laws are exercised in full or in part, and none is claimed beyond that.

### 1.3 Extraction laws (EXT)

| ID | Law | How tested |
|---|---|---|
| E1 | Determinism: output facts are sorted by a total key and independent of file order, hash seed, locale, time zone, CWD and CRLF | Permutation harness (D-19) |
| E2 | Locality: the facts of file `f` depend only on the bytes of `f` and the pins. Adding or editing an unrelated file leaves them unchanged. This is what makes early cutoff sound | Metamorphic test: add a file, compare per-file facts |
| E3 | Label honesty: every fact carries one provenance label (`exact`, `syntactic`, `candidate(n)`, `tool-resolved`, `unresolved`, `partial`) and a soundness class (`must`, `may`, `heuristic`); a `partial` extraction cannot PASS a gate; a missing tool is NOT_RUN | Fixtures: broken syntax, missing tool |
| E4 | Conformance with a generator: `extract(generate(model))` recovers the generated slice (the round trip that is cheap and honest: generate then extract, never the reverse) | Generated stubs and checks only |
| E5 | Untrusted: no extractor output can satisfy a gate by itself; the checker recomputes from raw inputs | Seeded lie test: an extractor that reports a fact the file does not contain must be caught by the checker |

### 1.4 Complement laws for mixed artefacts (a page with generated blocks and human text)

An OKF page is a lens whose view is the generated blocks (`facts`, `links`) and whose complement is the human text. Sync is `put(get(model), page)`.

| ID | Law | Statement |
|---|---|---|
| C1 | Human text preserved | Bytes outside generated blocks are unchanged by sync (GetPut with complement) |
| C2 | Generated regions equal regeneration | Bytes inside generated blocks equal what the generator produces from the current source (PutGet) |
| C3 | Idempotent | Sync of a synced page is the identity |
| C4 | Unknown frontmatter keys and `verified` preserved; the generator never mints `verified` and never writes a time | Fixture |

MEASUREMENT (2026-09-29): C2, C3 and the `verified` rule hold for the okf lane's `render_body` on three fixtures, and C1 fails when the human text has three or more consecutive newlines (prose or inside a fenced block): `re.sub(r"\n{3,}", "\n\n", body)` runs over the whole body, not only over generated blocks. The reference bench reports this on every run so the okf lane can see it clear.

### 1.5 Merge laws (MRG)

`merge3(base, ours, theirs)` is defined on maps `key -> canonical record text` (an absent key is an absent record). Per key `k`, with `b, o, t` the three values: if `o == t` the result is `o`; else if `o == b` it is `t`; else if `t == b` it is `o`; else the key is a conflict `{key, base, ours, theirs}`. Keys are visited in sorted order, records are compared by canonical bytes.

| ID | Law | Statement |
|---|---|---|
| M1 | Symmetry | `merge3(b, o, t)` and `merge3(b, t, o)` give the same merged map and the same conflicts with sides swapped |
| M2 | Identity | `merge3(b, o, b) == o` |
| M3 | Idempotence | `merge3(b, x, x) == x` (identical edits on both sides are a pseudo conflict and resolve) |
| M4 | Associativity when defined | For three replicas of one base, `merge3(b, merge3(b, o, t), u)` and `merge3(b, o, merge3(b, t, u))` are both defined or both undefined, and equal when defined |
| M5 | Definedness | The merge is defined iff, for every key, at most one distinct value differs from the base value |
| M6 | Determinism | Output depends only on the three inputs' canonical bytes: sorted, no actor, time, path or platform; conflict lists are sorted by key |
| M7 | Agreement with the line merge | Whenever `git merge-file` reports no conflict on sorted, unique-keyed line files, its result equals the keyed result. So the keyed merge only ever resolves cases git reports as conflicts |
| M8 | Emergent findings | For the merged tree `M`, `Findings(M) - (Findings(O) union Findings(T))` is the set of findings introduced by the merge itself; a non-empty set is a semantic conflict even when `merge3` reported none |

M8 status: the bench exercises it only as a structural-error illustration on the kernel `Workflow` (both sides pass the constructor, the merge does not; policy findings cannot be compared when the merge does not construct). A set difference of real `Finding` objects needs the finding model and is DESIGN. M7 is a differential test against `git merge-file` and needs git.

M1 to M5 are elementary consequences of one fact: for a fixed base, the per-key operation is the join in the flat lattice `base < v < TOP` (each changed value `v` incomparable to the others, `TOP` = conflict). Proof and limits are in the design doc, section 7.3. Hypotheses: one shared base for all replicas; canonical record bytes; no re-basing between merges. With criss-cross histories (different merge bases) associativity is not claimed.

### 1.6 Rename laws (REN)

| ID | Law |
|---|---|
| R1 | Completeness: after a rename `old -> new`, no declared link, registry entry, OKF page or sidecar references `old` except the rename record; a removed id with no rename record is a finding (WV-008) |
| R2 | A rename is not an edit: it is accepted as a rename only if the target's digest under a name-erased normaliser is equal before and after (DESIGN; a possible implementation is `ast-v1` with the defined name replaced by a placeholder). Otherwise it is an edit and inbound links become SUSPECT |
| R3 | Inverse: applying `old -> new` then `new -> old` restores every touched file byte for byte |
| R4 | Commutes with unrelated edits: a rename and an edit to a disjoint file can be applied in either order with the same result |

### 1.7 Decision laws (ACK)

| ID | Law |
|---|---|
| A1 | Subject-bound: an ack carries the digest the reviewer saw; it clears a link only if the current digest equals it. An ack for an older digest never clears a newer change (mirrors the kernel's `SUBJECT_CHANGED` on approve) |
| A2 | Set semantics: entries are content-addressed (`entry_id = H(domain tag, canon(entry without id))`); adding the same entry twice is one entry |
| A3 | Order independence: the link status is a function of the set of entries, not of file order or arrival |
| A4 | Append-only: for every commit, the entry set of the parent is a subset of the entry set of the child |
| A5 | Forks are visible: two entries for one subject that name the same `prev` (or both none) are two heads, reported as CONFLICT until a later entry names both as `prev` |

## 2. Transformation cards

Status column: `exists` (implemented in a lane), `bench` (reference sketch in `graph/bench/consistency_checks.py`), `DESIGN`. Owners are lanes, not people.

### T1. Model to diagram (GEN)

| Field | Contract |
|---|---|
| Signature | `Workflow -> Graph / Sequence / ClassModel -> Mermaid / PlantUML / DOT text` |
| Inputs and pins | `Workflow` (semantic hash), `model_impact` for the ripple; emitter version |
| Output | Text with a first-line provenance comment `eija: ... semantic_hash=...`; committed copies under `docs/diagrams/` |
| Laws | G1, G2, G4, G5, G6, G7 |
| Failure modes | Unsupported view/format pair returns a stable error code (exit 2); an untrusted model file is escaped |
| Tests | Goldens; reorder invariance; independent state-edge reader; drift gate `diagrams_drift`; real renderers in the release tier, NOT_RUN if absent |
| Status, owner | exists, visual lane (ADR-0023). Weave adds G3 (mapping totality) and the weave-side drift finding WV-027 |

### T2. Diagram edit to semantic transaction (PROP)

| Field | Contract |
|---|---|
| Signature | `translate(Workflow, Edit) -> Accepted(txs, layout, amendments) or Rejected(code, reason)`; `translate_batch(Workflow, [Edit])` orders by dependency |
| Edit source | A canvas that reports atomic edits carrying element ids, or an imported diagram file whose cells carry the semantic id as a labelled property (ProofMap Lite reads `id: component.example` from the cell label, which avoids depending on the editor's own cell ids; whether draw.io preserves cell ids across saves is UNVERIFIED) |
| Output | Proposals only. `SemanticTransaction`s go to the Studio, where the kernel `apply_transaction` is the only put and a human decides; `LayoutChange` is the complement |
| Laws | L1 to L10 (L2b added; L8 AST half and L6 general case are DESIGN) |
| Failure modes | Kernel codes pass through (`MEANING_REQUIRED`, `POLICY_BLOCKED`, `UNSUPPORTED_EDIT`, `UNKNOWN_NODE`, `SUBJECT_CHANGED`); `UNSUPPORTED_REJECTION_SOURCE`, `CONFLICTING_EDITS` and `MALFORMED_EDIT` in the bench; no silent repair |
| Tests | Exhaustive over the current alphabet (2 semantic transaction kinds plus layout) and both bases, all permutations of a 3-edit batch, four negative-oracle translators. Hypothesis strategies from the property lane when the alphabet grows |
| Status, owner | bench (reference translator); product code is `eijagraph.views` (ADR-0105). Canvas itself is deferred (design doc section 4 gives the trigger) |
| Honest limit | Results are MEASUREMENT on a tiny alphabet, not a proof. The reflective update is real: drawing one edge (Recommend) makes the kernel rewire Approve and Reject, reported as four amended edges |

### T3. Model to SysML v2 text (GEN)

| Field | Contract |
|---|---|
| Signature | `Workflow (+ graph types) -> .sysml text` |
| Inputs and pins | Semantic hash, emitter version; ids as UUIDv5 over `repo://` URIs in a fixed namespace |
| Laws | G1, G2, G3, G5, G7 |
| Validation | Optional, in a subprocess (sysml-toolkit or the Pilot); a passing syntax check is not a conformance claim to the standard, and a missing tool is NOT_RUN |
| Import | Narrow and a proposal: flat FSM, requirements with `doc`, `satisfy` and `verify` links, everything else refused with a stable code; imported content is checked by the kernel and decided by the owner |
| Status, owner | DESIGN, weave (ADR-0105) |

### T4. Model to code obligations, checks and stubs (GEN, and one create-once scaffold)

| Field | Contract |
|---|---|
| Direction | Model to obligations and checks only. Code is never generated back over a hand-written file. Reason: bidirectional code sync is the round trip practitioners abandon (design doc section 4) |
| Obligations | Table of `(state, actor, action)` rows and expected guards and effects derived from the `Workflow`; discharged by the existing runtime verifier, which recomputes evidence from raw observations |
| Generated checks | Table-driven test files under a `generated/` path with a banner and `prov`; owned by the generator; a hand edit is a finding (CS-02) |
| Stubs | Create-once scaffolds: written only if the target does not exist; after creation the code is a source and the graph tracks it with a `satisfies` link and digest |
| Laws | G1, G2, G5, G7, and E4 (extract-after-generate recovers the generated slice) |
| Status, owner | DESIGN; obligations partly exist in the impact chain (`obligation:<action>`) |

### T5. Model to UI projection and UI checks (GEN for projections, CHK for links)

| Field | Contract |
|---|---|
| Projection | The action list, and the rule table, generated from the `Workflow` (removes the measured hard-coded list of 5 actions against a 4-action baseline). Needs a `src/` change in the Studio, so it is a separate ADR and PR |
| Relation | The UI sidecar is authored; `data-eija-key` in the markup is authored; they are related by ids, so the relation is checked (UIL-001 to UIL-008), not generated |
| Laws | G1 to G3 for projections; the UIL rules are CHK, with enabled-set equality complete only over the enumerated `(state, actor)` pairs |
| Status, owner | DESIGN, weave (ADR-0107) with the hci lane's browser |

### T6. Graph and model to OKF pages (GEN with complement)

| Field | Contract |
|---|---|
| Signature | `(source, sidecar links, term registry) -> page` where the page is generated blocks plus human text |
| Laws | G1, G2, G7 for the blocks; C1 to C4 for the whole page; typed links come from the sidecar, prose links stay untyped (OKF states the kind is conveyed by prose) and a broken link is an error (stricter than OKF, which tolerates them) |
| Freshness | By digest (`sources[].sha256` with `hash_method`); OKF `stale_after` reads the wall clock and is not used for verdicts |
| Status, owner | exists, okf lane (ADR-0045, ADR-0046); weave adds the `links` block source and the complement law check. Finding for the okf lane: C1 violation above |

### T7. Code to facts, and intended architecture versus actual (EXT, CHK)

| Field | Contract |
|---|---|
| Signature | `files -> sorted typed facts with provenance` (Python `ast` first; tree-sitter and SCIP when a surface needs them) |
| Laws | E1 to E5 |
| Reflexion | `intended (LikeC4 or Structurizr JSON) vs actual (import graph)`: agree, differ, missing sets by exact set difference (WV-026); the mapping is authored and checked for totality (G3) |
| Direction | One way. Facts are never written back to code. A fix is a proposal (byte-range edits with `applicability` and a `precondition_sha256`) |
| Status, owner | DESIGN, weave (ADR-0095) |

### T8. Rename (REN)

| Field | Contract |
|---|---|
| Signature | `rename(old_id, new_id) -> edits over all sources + {old_id, new_id, digest_before, digest_after}` |
| Mechanism | LibCST for Python, byte-range edits for Markdown, YAML, JSON and OKF pages; the rename record is committed |
| Laws | R1 to R4 |
| Why explicit | Similarity-based rename detection is a guess (git detects renames heuristically); identity by id needs a record, and an OKF page for a moved symbol is otherwise one deprecated page and one new page |
| Status, owner | DESIGN, weave (ADR-0110) |

### T9. Three-way merge and post-merge compile (MRG)

| Field | Contract |
|---|---|
| Signature | `merge3(base, ours, theirs) -> (merged, conflicts)`; then `compile(merged)`; the semantic conflicts are `Findings(M) - (Findings(O) union Findings(T))` |
| Applies to | Authored line-oriented files: `graph/links/*.jsonl`, term registry, acceptance matrix, sidecars. Each file is sorted by key, one canonical record per line. Records merge atomically (never field by field), because a link is one claim and a field-wise merge could combine `kind` from one side and `to` from the other into an ill-typed link |
| Entry points | A command that reads the index stages (`git show :1:path :2:path :3:path`) and writes the merged canonical file or a conflict report, needing no repository configuration; an optional git merge driver (definitions live in `.git/config`, so they are per clone and never a trust dependency); the gate is always the post-merge compile |
| Laws | M1 to M8 |
| Status, owner | bench (reference `merge3`); product code `eijagraph.merge`, ADR-0093 with the ledger (ADR-0094) |

### T10. Ack (ACK)

| Field | Contract |
|---|---|
| Signature | `ack(subject, reviewed_digest, decision, reason, prev) -> entry` appended to `graph/ledger/*.jsonl` |
| Entry | `{subject, digest, decision, actor, reason, prev[]}` plus `entry_id` = domain-separated hash of the canonical entry. No sequence number and no time in the file (a receipt holds times) |
| File shape | Preferred: one file per entry, named by `entry_id` (sharded by hash prefix), which cannot conflict and needs no driver. Alternative: one file of lines sorted by `entry_id`, merged with git's built-in `union` driver plus canonicalise (sort and dedupe); safe only because the file is append-only and content-addressed, a gate checks A4, and hosted-merge behaviour of `merge=union` is UNVERIFIED. `prev[]` is sorted before hashing |
| Laws | A1 to A5 |
| Authority | Human owner only. Agents and providers never write here (absence of tool, file-diff gate on the path) |
| Status, owner | DESIGN; requires a change to the link record (`baseline_decision` refers to `entry_id`, not `ledger_seq`), see design doc section 7.6 |

### T11. Graph to exports (GEN)

| Field | Contract |
|---|---|
| Targets | Cypher/CSV (Neo4j, optional and one-way), SCIP, Soufflé facts, SKOS, Contextive, Vale, cspell, rdjson, SARIF |
| Laws | G1, G2, G5, G7; sorted rows; ids as UUIDv5 where the target needs UUIDs |
| Direction | Get-only. No import from an export ever reaches a source; an edit in Neo4j browser is not evidence |
| Status, owner | DESIGN, weave (ADR-0109) |

## 3. Where each law runs

| Tier | Runs | Cost note |
|---|---|---|
| Edit-time (agent loop) | File-local rules, G2 digest comparison, M1 to M6 unit tests | PREDICTION: well under a second per file; unmeasured |
| Fast (pre-commit, `nox -s graph -- fast`) | G1 to G3, G5, G7 on all views, E1 to E3, L1 to L10 on the reference alphabet (the DESIGN halves excepted), R1, A1 to A4, post-merge compile after a merge | Bench checks without git: measured in seconds |
| Full | Permutation harness, differential incremental-equals-clean, G4 with independent readers, seeded property tests (M1 to M5 at larger samples, lens laws with Hypothesis), rendered UI tier (NOT_RUN without Chrome) | Serial on the shared PC |
| Release | Double rebuild equal roots, POSIX golden compare (NOT_RUN until run on Linux or WSL), external validators (PlantUML syntax, SysML validator), M7 differential against `git merge-file` | One browser or container at a time |

## 4. Sources for this file

Opened by me on 2026-09-29: Foster, Greenwald, Moore, Pierce, Schmitt, "Combinators for Bi-Directional Tree Transformations" (TOPLAS; the authors' copy at https://www.cis.upenn.edu/~bcpierce/papers/lenses-toplas-final.pdf), laws quoted from its section on lens laws; Bailis et al., "Coordination Avoidance in Database Systems" (https://arxiv.org/abs/1402.2237, full text read; Definition 6 is used as a classification vocabulary only, Theorem 1 is stated for a set-union model and is not applied); Khanna, Kunal, Pierce, "A Formal Investigation of Diff3" (https://www.cis.upenn.edu/~bcpierce/papers/diff3-short.pdf; venue not shown in the copy I read); git documentation https://git-scm.com/docs/gitattributes and https://git-scm.com/docs/git-merge-file; OKF v0.2 SPEC https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md; ProofMap Lite `docs/label-conventions.md` and `docs/gap-audit.md` (private repo, read with the owner's `gh` login). Everything else is cited to the dossiers in `docs/weave/research/` in the design doc.
