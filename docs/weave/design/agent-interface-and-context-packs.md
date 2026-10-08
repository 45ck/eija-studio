# Agent interface, context packs and determinism enforcement

Lane: weave. Aspect: agent-interface. Date: 2026-09-29. Status: DESIGN feeding [ADR-0099](../../adr/0099-weave-agent-interface.md). Nothing here is built except `graph/bench/agent_interface_checks.py` and two test files. Normative tool contract: [graph/schema/mcp-tools.md](../../../graph/schema/mcp-tools.md) (machine-checked). Architecture and vocabulary: [ARCHITECTURE.md](../ARCHITECTURE.md), [research/SYNTHESIS.md](../research/SYNTHESIS.md). Sibling aspects this one builds on, read from the shared worktree on 2026-09-29: the metamodel and identity aspect ([graph/schema/metamodel.json](../../../graph/schema/metamodel.json), [identity-vectors.json](../../../graph/schema/identity-vectors.json)), the impact-ranking aspect ([impact-ranking-and-confidence.md](impact-ranking-and-confidence.md)) and the consistency-sync aspect ([consistency-and-sync.md](consistency-and-sync.md)). Where they define something (node and link types, digest format, ranking, selection, impact, test selection, change risk) this document consumes it and does not redefine it.

Labels: MEASUREMENT (a script ran, domain stated), PREDICTION (arithmetic or reasoning on stated assumptions, nothing observed), DESIGN (a proposal of this lane), UNVERIFIED (not opened or not confirmable; nothing is built on it). Every URL in section 16 was opened on 2026-09-29. Web search was exhausted (200 of 200) before this aspect started, so "no tool does X" means "not found by direct fetches".

## 0. Decisions first

| # | Decision | Confidence | Basis |
|---|---|---|---|
| 1 | Agents get **20 typed, bounded, read-mostly tools** (10 in the default `core` tier, 10 in `extended`), served by the agents lane's MCP server. No free-form Cypher or SQL, no pushed graph summary. | High that a typed surface is safer and testable; medium that it helps | SWE-agent ablations, AGENTS.md study, section 2 |
| 2 | Every result is a **hash-carrying envelope**: `graph_root`, `request_hash`, `response_hash`, bounds (`complete`, `frontier`), typed errors with machine-actionable next calls. Same (root, tool, arguments) gives byte-identical bytes. | High | D-01 to D-12, MCP spec, section 4 |
| 3 | A **context pack** is a pure function of (snapshot, task, budget, parameters): all mandatory obligations first (never dropped; `BUDGET_TOO_SMALL` instead), then a ranked tier chosen by the impact-ranking aspect's integer personalised PageRank and budgeted selection. Items carry content hashes so staleness is a hash comparison. Pull, not push. This aspect adds the pack layer, not the mathematics. | Medium (mechanism measured for determinism; benefit UNMEASURED) | Section 5, bench |
| 4 | **Edit ladder**: typed semantic transaction (kernel) > codemod EditSet (deterministic, precondition-hashed) > anchored text edit > free-form. Free-form edits stay allowed but are observed, diffed and checked. Tools return proposals; none applies an edit or a decision. | High for the ordering; UNMEASURED for the size of the effect | Section 7 |
| 5 | **Dry runs are pure**: `txn_dry_run` composes the kernel's pure `apply_transaction` and `model_impact` with an `eijagraph` overlay; `edit_preview` applies an EditSet to an in-memory overlay. Both report predicted ripple labelled PREDICTION and never write. | High | Bench (kernel purity checked), section 6 |
| 6 | **Agent-produced links go through a small trusted checker** that recomputes endpoints, signatures, method and digest, and guards against moved goalposts (obligation reduction). A proposal is inert: it changes no graph fact, clears no link, satisfies no gate. | High | Certifying algorithms; assess_receipt precedent; section 8 |
| 7 | **Owner-only actions are absent**, not denied: ack, ledger, statement approval, policy, suppression, baseline growth, receipts, apply, consent. A test asserts absence. | High | ADR-0041 |
| 8 | **Replay log** = server-side hash-chained record of the deterministic side of a run (tool calls, responses, observed worktree changes, proposals), plus client transcripts imported as self-reported blobs. Replay verifies the deterministic side and never claims the model would answer the same. | High | Thinking Machines, bench, section 9 |
| 9 | **Evaluation**: pass^k over n recorded trials, unit of analysis is the task, paired arms, hidden oracles independent of the graph, blocked randomisation, pre-registered. At a feasible 78 tasks x 5 trials only a difference of about 10 percentage points is detectable (PREDICTION), so a null result will mean "no effect at least that large", not "no effect". | High that this design is honest; effect sizes UNMEASURED | Section 10 |
| 10 | **No claim that the graph makes agents better or humans understand more is made here.** The literature bounds the expected size of interface effects at a few percentage points and includes a negative result for always-on context. | High | Section 2 |

## 1. Scope

**In scope:** what an external coding agent (Claude Code, Codex, OpenCode, Gemini CLI) calls; how the kernel checks what it produces; how a run is recorded and audited; how reliability is measured. The graph itself (facts, links, rules, ledger) is other aspects' work and is consumed through interfaces (section 12).

**Two kinds of agent.** (a) An external agent that drives EIJA through MCP tools (ADR-0041); most of this document. (b) A provider that Studio itself invokes for an untrusted single-shot proposal (`ProposalProvider.propose`); it needs only the recording fields in section 9.

**Position in the stack:** L6 projection (get-only) plus a proposal inbox. The tools read L2 to L5; `proposal_submit` writes one inert record; nothing writes L0 sources or the decision plane.

**Non-goals:** a sandbox against an agent with the owner's OS permissions (AGENTS.md says the interface is not one); prompt-injection defence beyond limiting what tools can do; making the model deterministic; a general agent framework.

## 2. What the evidence supports, and what it does not

| Finding | Number and bound | Design consequence | Source |
|---|---|---|---|
| Edit with a linter guardrail vs without vs no edit tool | 18.0 vs 15.0 vs 10.3 percent resolved; SWE-bench Lite (300), GPT-4 Turbo, SWE-agent ablation | Feedback on write is a lever: `edit_preview` and `diagnostics_get(since)` return typed findings for the edit just made | SWE-agent Table 3 (arXiv 2405.15793 HTML) |
| Search results summarised vs iterative vs none | 18.0 vs 12.0 vs 15.7 | Bounded, summarised answers beat open-ended exploration; a badly bounded tool can be worse than none | same |
| File viewer window 100 lines vs 30 vs whole file | 18.0 vs 14.3 vs 12.7 | Slices are capped (32768 bytes in `graph_node`; 4096-byte default slice in packs, DESIGN) | same |
| Only the last 5 observations kept vs full history | 18.0 vs 15.0 | Server returns deltas (`since`) so an agent need not re-read | same |
| Tool responses: concise vs detailed | 72 vs 206 tokens in the article's example (about one third); Claude Code caps tool responses at 25,000 tokens by default; errors should be actionable, not tracebacks | `detail` set to concise or full, hard caps, typed errors with `next` calls | Anthropic, "Writing effective tools for agents" |
| Repository code graph retrieval added to four systems | +2.00 to +2.66 resolve rate on SWE-bench Lite; Python only; GPT-4 series only; Lite only (authors' limits) | Expect a modest effect from structural retrieval; do not promise more | RepoGraph (arXiv 2410.14684 HTML) |
| Repository-level context files (AGENTS.md style) | Did not improve success overall; inference cost up by more than 20 percent on average; repository overviews gave no benefit | **Pull, not push**: no graph summary is added to a standing prompt; packs are requested per task | Gloaguen et al. (arXiv 2602.11988) |
| Position of relevant information in long context | Accuracy is often highest at the beginning or end and degrades in the middle | Pack order: obligations and seeds first, ranked tier by descending relevance (DESIGN, unmeasured) | Liu et al. (arXiv 2307.03172) |
| Self-correction without external feedback | Struggles, at times degrades | The feedback signal is the deterministic checker, never the agent's own review | Huang et al. (arXiv 2310.01798) |
| Self-repair when repair cost is counted | Gains often modest; feedback quality is the bottleneck; stronger feedback helps more | Findings carry witnesses and structured `args`, not prose | Olausson et al. (arXiv 2306.09896) |
| Patches that pass the benchmark tests | 7.8 percent count as correct while failing the developer suite; 29.6 percent of plausible patches behave differently from ground truth; reported resolution inflated by 6.2 points | Tests alone are a leaky oracle: the evaluation reports a false-accept rate against hidden checks | Wang et al. (arXiv 2503.15223) |
| Edit format | On 89 Python refactoring tasks GPT-4 Turbo scored 20 percent with the baseline format and 61 percent with unified diffs; lazy comments 12 of 89 tasks down to 4 | Edit representation matters; EditSet is an explicit, familiar, checkable format. The result is one vendor-era model and one benchmark | Aider, "Unified diffs" |
| Structured output constraints | "Significant decline" in reasoning under format restrictions; stricter formats worse | Let the agent reason freely, emit the structured proposal last; validate on receipt | Tam et al. (arXiv 2408.02442) |
| Temperature 0 non-determinism | 1000 completions of one prompt gave 80 unique outputs; first divergence at token 103; cause is batch-size-dependent kernels; deterministic kernels 42 to 55 s vs 26 s in their test | Determinism is a property of the kernel and of recording and replay, not of regeneration | Thinking Machines |
| Reliability metric | pass^k = E over tasks of C(c,k)/C(n,k); best gpt-4o agent above 60 percent average success had pass^8 below 25 percent | Report pass^k, not only pass@1 | tau-bench (arXiv 2406.12045 HTML) |
| MCP tool rules | outputSchema optional, conformance MUST, serialised JSON in TextContent SHOULD; annotations untrusted; errors as `isError`; servers MUST validate, rate limit, sanitize; 2026-07-28 revision: no protocol session, deterministic tool order SHOULD | Envelope, absence of owner tools, stateless cursors and snapshot handles | MCP 2025-11-25 and 2026-07-28 tools pages |

**Not supported by anything opened:** that a typed graph raises agent success; that packs beat plain retrieval; that humans understand a change faster with a semantic diff; that codemods beat anchored text edits for agents; that dry runs change agent behaviour. Each is a hypothesis with a falsifier in section 10. Effect sizes in this table come from different benchmarks, models and dates and must not be added.

## 3. The tool surface

Contract: [mcp-tools.md](../../../graph/schema/mcp-tools.md). Design principles, each tied to a rule there.

| Principle | Rule | Why |
|---|---|---|
| Few, typed tools; no query language | C-12, C-14, section 9 of the contract | Text-to-query errors and unbounded cost; typed tools can be schema-validated, hashed and golden-tested |
| Tiered exposure fixed at server start | C-12 | MCP 2026-07-28: tool list must not vary per connection. Tool count becomes an evaluation factor (core 10 vs extended 20) |
| Every answer says what it left out | C-08 | `complete` and `frontier` are the kernel's `impact.closure` idiom, generalised |
| Names not UUIDs | NodeId is a `repo://` path plus fragment | Anthropic guidance on meaningful identifiers; the id is also the okf lane's link target |
| Deltas over re-reads | `diagnostics_get(since)`, `snapshot_diff`, `pack_verify` | SWE-agent history ablation |
| Untrusted text is marked | C-11 | Indirect injection through repository text cannot be filtered out; it can be labelled and its blast radius limited by absence of dangerous tools |
| No trusted inputs | C-13 | Digests and statuses are recomputed |

Mapping from ARCHITECTURE section 9 and the impact-ranking aspect's agent tool names: `node` = `graph_node`; `neighbors` = `graph_neighbors`; `impact` = `graph_impact` (returns that aspect's `eija.weave.impact.v1` report); `context` and `context(budget)` = `context_pack`; `explain` = `graph_why` and `diagnostics_explain`; `select_tests` = `select_tests`; `risk` = `change_risk`; `violations` = `diagnostics_get`; `link_status` = `link_status`; `ui_links` = `graph_neighbors` over `exercised_by`, `names`, `styled_by`; `language.lookup` = `language_lookup`; `language.check` = `diagnostics_get(rule_family: language)`. New relative to both: `graph_status`, `graph_search`, `pack_verify`, `snapshot_diff`, `evidence_get`, `edit_preview`, `txn_dry_run`, `codemod_plan`, `proposal_submit`. Core tier (10): `graph_status`, `graph_node`, `graph_search`, `graph_neighbors`, `graph_impact`, `diagnostics_get`, `context_pack`, `edit_preview`, `txn_dry_run`, `proposal_submit`; `select_tests` is a candidate for promotion to core, decided by the tier ablation.

**A session, end to end (DESIGN).**

1. `graph_status` returns the snapshot, verdict and NOT_RUN list. An agent that ignores NOT_RUN is still told, on every later envelope, in `snapshot.not_run`.
2. `context_pack(intent, seeds, budget)` returns obligations first (seed slices, the requirement statements they satisfy, their verifiers, their terms, open findings, SUSPECT links), then a ranked tier.
3. The agent edits with its own tools (free-form) or asks `codemod_plan` for a rename and previews the EditSet with `edit_preview`.
4. After editing, `diagnostics_get(since=<root before>)` returns only new, updated and absent findings. `pack_verify` on the items it holds says which pieces of context are now stale.
5. For a change to the executable model, `txn_dry_run` reports the kernel's verdict and closure plus the graph ripple; only the owner can `select`, `edit` and `apply` in Studio.
6. Links the agent believes should exist go through `proposal_submit`; the checker answers `ACCEPTABLE_FOR_REVIEW` or `REJECTED(code)`; the owner decides.
7. The run log records steps 1 to 6; `session_close` seals the head hash with the kernel's receipt signer (an integrity seal, not institutional identity).

## 4. Determinism enforcement for the interface

The model is not deterministic and this design does not pretend otherwise. Everything on the server side is a pure function of (snapshot, request), and the property is enforced at ten points.

| # | Mechanism | Guards against | Oracle | Status |
|---|---|---|---|---|
| E1 | RFC 8785 subset serialisation of the envelope; `content` text equals that serialisation; `response_hash` inside the envelope | Byte drift between platforms and between text and structured content | Schema, golden JSON-RPC bytes, RFC vectors | JCS key order measured (below); golden tests NOT_RUN (no server) |
| E2 | Ranking in bit-exact integers (the impact-ranking aspect's `ppr_int`); pack layer sorts by total keys | Float bits that depend on summation order | Shuffle test over node and edge order | The impact-ranking aspect measured 40 of 40 differing float hashes on 300 nodes (their document). Here (MEASUREMENT, 40 shuffles, 300 nodes) the pack is byte-identical (1 distinct) and a float ranking would still have selected the same items (1 distinct item sequence), so the integer rule is justified by byte identity and boundary risk (PREDICTION), not by an observed change in selection |
| E3 | Total orders and sorted set arguments (C-04, C-05) | Set and dict iteration, `PYTHONHASHSEED`, filesystem order | Permutation harness D-19 over each tool with a golden request | NOT_RUN (no implementation) |
| E4 | Resource limits by count, not time: response caps in cost units, per-run call quota, SQLite VM instruction budget for the reserved SQL tool | Wall-clock dependence (D-04) vs MCP "rate limit" MUST | Same query, same data: same handler count | MEASUREMENT: 1 distinct `set_progress_handler` call count over 5 runs and over 10 shuffled insertion orders, 300-node graph, SQLite 3.49.1, Windows; other SQLite versions NOT_RUN |
| E5 | Keyset cursors bound to `graph_root` and `request_hash` | Stale or replayed pages | STALE_SNAPSHOT test after an edit | DESIGN |
| E6 | `tool_list_sha256` over names, descriptions, schemas and annotations | Supply-chain drift in prompt-visible text; silent tool additions | Golden `tools/list` | DESIGN (ADR-0041 already treats the name list as a governance decision) |
| E7 | Server validates its own result against `outputSchema` before sending (C-16) | Non-conforming output (MCP MUST) | Contract examples validate (11 tests pass) | Contract side MEASURED; server side NOT_RUN |
| E8 | Snapshot pinning: every envelope carries the resolved root; `WORKTREE` and `HEAD` are resolved once per call and recorded | "Which graph did the agent see?" | Replay audit | DESIGN |
| E9 | Domain-separated hashing of a self-delimiting JSON value, `dhash(tag, value)` of the identity aspect (`"sha256:"` + SHA-256 over ASCII tag, NUL, RFC 8785 bytes) | Field-concatenation collisions; cross-domain reuse | Golden vectors; `["a","bc"]` vs `["ab","c"]` | MEASUREMENT: this bench's writer reproduces all 10 golden JCS vectors and all 10 node hashes in `graph/schema/identity-vectors.json` and rejects the 3 must-reject cases; naive byte concatenation collides, the JSON form does not, and one record under two tags does not |
| E10 | Replay audit (section 9) | Tool non-determinism found after the fact | Recorded responses recomputed | MEASUREMENT on a toy tool: 40 of 40 recorded closure calls reproduce; NOT_RUN on the real server |

Two measured details worth stating: RFC 8785 orders object keys by UTF-16 code units, so U+1F600 sorts before U+FF5E, while Python's default string order (code point) does the opposite (MEASUREMENT in the bench; RFC statement read at the RFC page). The kernel's `canonical()` therefore must not be used for these hashes (SYNTHESIS R5).

**What an MCP SDK may do to bytes is UNVERIFIED.** The agents lane's server uses `mcp==2.2.0` (ADR-0041). Whether it re-serialises `structuredContent` or reorders keys was not checked. The contract therefore has the handler build the `CallToolResult` explicitly (both `content[0].text` and `structuredContent` from one canonical string) and requires a golden JSON-RPC byte test on the wire.

## 5. Context packs

### 5.1 Definition

A **context pack** is `P(S, T, B, params)`, a pure function of

- `S`: a snapshot (`graph_root`),
- `T = (intent, seeds, seed_terms)`: `intent` in `understand | modify | rename | diagnose | review`; `seeds` are node ids; `seed_terms` are resolved only by exact registered forms (no guessing; unknown or ambiguous terms are reported in `obligations.unresolved`),
- `B`: a budget in **bytes** (contract C-07: the UTF-8 length of an item's canonical JSON rendering at the chosen level; where the item is an OKF page the okf lane's page bytes are the cost, which is the impact-ranking aspect's `render_bytes`; reconciling the two is open question 11),
- `params`: the ranking parameters as that aspect reports them (`alpha`, `iterations`, `err_bound_units`, digests of the arc set and the flow table) plus the pack policy version.

`pack_id = dhash("eija.weave.pack.v1", {request (normalised), graph_root, params})`. The same inputs reproduce the same pack bytes, so a pack can be cited, re-derived and audited.

Budget is in bytes rather than tokens because tokenizers are model-specific and change (the impact-ranking aspect makes the same choice); the bytes-to-tokens ratio will be measured per model in the evaluation. Nothing here assumes a ratio.

### 5.2 Slots: what is mandatory

| Slot | Filled by | Level | Intents | Tier |
|---|---|---|---|---|
| `seed` | the seed nodes | slice (summary for `review`) | all | mandatory |
| `statement` | requirements and invariants reached by `satisfies`, `realises`, `serves` from a seed | summary | modify, rename, review, diagnose | mandatory |
| `verifier` | tests, properties, formal laws reached by `verifies`, `covers`, `proves` to a seed or its statements | handle | modify, rename, review, diagnose | mandatory |
| `term` | terms reached by `names` (bounded contexts included) | summary | all | mandatory |
| `finding` | open findings located on a seed | inline (Finding) | modify, diagnose, review | mandatory |
| `suspect` | SUSPECT links touching a seed | handle | modify, rename, review | mandatory |
| `governing` | ADRs reached by `motivates`, `documents` | handle | modify, review | optional |
| `ripple` | `graph_impact` closure at tiers 0 and 1 (count and first ids; the rest as `frontier`) | handle | modify, rename | mandatory summary, optional members |
| `ranked` | two-hop neighbourhood minus the above, by relevance | handle, summary or slice by budget | all | optional |

The mandatory set `M` is exact, not ranked: it is what the kernel's rules say the change touches. If `cost(M) > B` the tool returns `BUDGET_TOO_SMALL` with `args.needed = cost(M)`; it never silently drops an obligation. A slot that cannot be filled (unknown term, unresolved link) appears in `obligations.unresolved`.

### 5.3 Ranking and selection belong to the impact-ranking aspect

Not redefined here. That aspect (design sections 5 and 6, decisions IR-4 and IR-5) defines: relevance as personalised PageRank in bit-exact fixed-point integers (mass `2^40`, default teleport `alpha = 1/5`, impact-direction weight 2 and reverse weight 1, exact-integer splitting with remainders to sorted targets, `K` from `alpha` by an integer inequality, a proven `L1` error bound printed as `err_bound_units`, scores in parts per million); and budgeted selection (pinned items first, `BUDGET_TOO_SMALL` with the needed amount, then candidates by score per cost compared by cross-multiplication with ties by id, skipping those that do not fit, keeping the better of that set and the best single fitting candidate, with an at-least-half-of-optimum guarantee under stated hypotheses). Their reference implementation is `graph/bench/impact_math_reference.py` (`ppr_int`, `select_context`, `pass_hat_k`), which this aspect's bench imports as its ranking and selection oracle. Their reported offline co-change study (design section 5.6 there; numbers not re-run by me): on two Python repositories the default ranking had recall@10 of 0.454 (doorstop) and 0.461 (strictdoc) against 0.446 and 0.214 for a path-prefix baseline that uses no graph, which that document describes as beating the path-prefix baseline on one repository and tying it on the other; so the graph's advantage over a trivial baseline is uneven. That is why the evaluation has a graph-free pack arm (A0c).

What this aspect adds on top, and only this:

1. **Mandatory slots** (section 5.2) are the "pinned" input of `select_context`: exact, from the rules, not ranked.
2. **Levels**: a candidate may be included as a handle, a summary or a slice. Upgrading a level is treated as buying the increment at its extra cost by the same density rule; this step is a heuristic and the selection guarantee is stated for the single-level case only.
3. **Omission accounting**: `select_context` lists omitted candidates that were eligible; candidates it filters out before selection (cost above the room, zero score) are counted by the pack layer so `omitted` is complete (interface remark for the ranking aspect: report these too, or state that callers must).
4. **Envelope, hashes and freshness** (`pack_id`, item content hashes, `pack_verify`).

### 5.4 Pack layer, measured (MEASUREMENT, synthetic)

300 nodes, 747 typed edges (five link kinds, seed 7), 40 shuffles of node and edge order, 3 seeds, budget 2400 bytes, default weights (2, 1), ranking and selection from the reference: 1 distinct pack (dhash of the canonical pack), 22 items (mandatory first), 2391 of 2400 bytes spent, 44 eligible candidates omitted (so `complete: false`, reported). `BUDGET_TOO_SMALL` reports the needed cost. Replacing the integer ranking by a float power iteration with the same iteration count still gave 1 distinct item sequence over the 40 shuffles. Changing one included node's content hash makes `pack_verify` flag exactly that item (1 of 22). The synthetic graph shows the mechanism, not the quality of packs on a real repository.

### 5.5 Order and form of a pack (DESIGN, unmeasured)

Header (counts, `complete`, omissions), then seeds, then mandatory slots in table order, then ranked items by descending relevance. This follows the lost-in-the-middle observation (relevant information at the beginning or end is used best) and keeps the obligations where they are read first. Whether this order matters for a modern agent is an ablation in section 10 (`pack order`), not an assumption.

### 5.6 Pull, not push

The AGENTS.md study found repository-level context files did not improve success and raised cost by over 20 percent; the same study saw no benefit from repository overviews. So no pack is injected into a standing prompt. An agent asks for a pack when it starts a task, and the evaluation includes a push arm to test this decision rather than assume it.

### 5.7 Offline evaluation before any agent is run (DESIGN)

`pack_recall@B`: extend the impact-ranking aspect's co-change harness (`graph/bench/ranking_cochange_eval.py`, leave-one-out seeds from historical commits) from a ranking to a pack: build the pack at `B` in {2048, 4096, 8192, 16384} bytes and report the share of the commit's other changed files and symbols that are in the pack, against (a) the path-prefix baseline, (b) lexical grep with the same budget, (c) random. This costs no model calls and can reject a bad layer early. It measures localisation, not agent success. The EIJA history is short (7 commits at their measurement), so the first meaningful run uses the external repositories that harness already pins, and states n.

### 5.8 Limits

Relevance is a heuristic. Sufficiency of a pack for a task is unmeasured. A pack is not evidence: it carries provenance labels, but a `heuristic` item is a lead, never a gate input. A pack built on a partial extraction says so per item (`label: partial`).

## 6. Diagnostics, dry runs and predicted ripple

### 6.1 Diagnostics retrieval

`diagnostics_get` returns Findings (contract `Finding`: rule id, level, `message_id` plus structured `args`, locations, witness steps, fingerprint, optional fix handle). It is the feedback loop: after an edit the agent asks for `since=<root before>` and receives `new`, `updated` and `absent` states (SARIF `baselineState` vocabulary: `new`, `updated`, `unchanged`, `absent`, as read in SARIF 2.1.0 section 3.27.24). Errors are never dropped to fit a cap. `by_level` counts the whole scope so the agent knows what was cut. Whether structured `args` raise fix rates over prose is a PREDICTION; the per-rule metric is "fix applied and finding gone" (INCREMENTAL dossier, metrics lane).

### 6.2 Dry run of a typed semantic transaction

The kernel already has the pure pieces: `apply_transaction(model, tx) -> Workflow` (raises `DomainError` with a code) and `model_impact(before, after)` (closure with `complete`, `frontier`, `envelope`). `Studio.edit` is owner-only and persists; the pure functions are neither. `eijagraph` must not import the kernel (R9), so the agents lane's adapter (which may) calls the kernel and passes the candidate workflow to `eijagraph` as an overlay file.

MEASUREMENT (kernel, `graph/bench/agent_interface_checks.py`, baseline from `policy.baseline()`):

| Transaction on the baseline | Kernel result |
|---|---|
| `enable_recommendation` | ACCEPTED. Semantic hash `5d3ef3a1...` to `b26c9af5...`; actions Submit, Approve, Reject, Revise become plus Recommend; changed actions Approve, Recommend, Reject; `model_impact` closure of 20 nodes, `complete: true` |
| `set_rejection_source` (Submitted) before enabling | REJECTED, `MEANING_REQUIRED` |
| `set_rejection_source` (Submitted) after enabling | ACCEPTED; changed action Reject |
| Purity | the input model's semantic hash is unchanged after each call |

The order dependence in the second row is why a dry run is useful to an agent: it learns the required order from a typed code, not from a stack trace.

**Predicted ripple.** Let `Delta` be the workflow elements added, removed or changed between base and candidate (keyed by element id, as the semantic hash treats them), `R` their node ids (`workflow_element` subtypes `state`, `transition`, `role`, `guard`, `effect` in the metamodel), and `G` the overlay graph. The tool reports the impact-ranking aspect's tiered closure of `R` over `G`: counts per tier and the affected ids with their tier (tier 0 sound `must` arcs, tier 1 adds `may`, tier 2 adds heuristic), sorted, with the kernel wording that it covers encoded edges only. It also reports `findings_delta` (findings new on the overlay, for example a new transition with no `verifies` link, WV-010) and `links_becoming_suspect` (edge ids of links whose anchored endpoint digest changes; for workflow elements the digest method is the metamodel's proposed `workflow-element-v1` or `workflow-semantic-v1`). The label is PREDICTION: the sets are computed, and the claim that a real implementation will touch them is not observed.

**Ripple accuracy, measured after the fact (DESIGN).** After an agent implements the change, let `A` = ids that existed in both the base snapshot and the final snapshot and whose content hash changed, and `R_hat` = the predicted affected set (all tiers up to the requested `max_tier`). `ripple_recall = |A intersect R_hat| / |A|` and `ripple_precision = |A intersect R_hat| / |R_hat|`, reported per tier. Recall below 1 lists unpredicted changes, i.e. missing edges: a backlog for the extractors. Precision well below 1 is expected because closure over-approximates (`may` edges). This makes the graph's own quality a number that comes out of every run.

### 6.3 Preview of an edit

`edit_preview` applies an EditSet to an in-memory overlay (never the disk), rebuilds the affected part incrementally (the incremental engine's early cutoff, ADR-0100) and returns preconditions, `findings_delta` and `links_becoming_suspect`. A file whose changed region parses only with recovery is listed as partial and the findings that depend on it are NOT_RUN (D-14). Cost is one incremental build per call, unmeasured (PREDICTION: seconds on a repository this size; the cache is off by default until `graph/bench` shows a gain, ARCHITECTURE section 8).

## 7. Edits: transactions, codemods and free-form

### 7.1 The ladder

| Rung | Mechanism | Determinism and precondition | Failure mode | Applied by |
|---|---|---|---|---|
| L3 typed semantic transaction | Kernel `SemanticTransaction` (2 kinds today) | Pure function; typed rejection codes | Only what the kernel models | Owner in Studio; agents get `txn_dry_run` only |
| L2 codemod EditSet | LibCST for Python renames, byte-range edits for Markdown, YAML, OKF, ADR tables; `codemod_plan` | Same inputs give the same EditSet (a test: the LibCST codemod tutorial page I read makes no determinism or idempotence claim); each file has `precondition_sha256` | Unresolvable sites are reported, never guessed | The agent, with its own file tools, or an owner-run CLI (no MCP apply in v1) |
| L1 anchored text edit | The agent's own editor tool (`old_str` must match exactly, per the text-editor tool docs) with `edit_preview` as a pre-flight | Fails closed on mismatch; no semantic check by itself | Overreach or a syntactically valid but wrong edit | The agent |
| L0 free-form | Any shell or editor write | None | Anything | The agent; observed as `worktree_observed` and checked afterwards |

Policy (DESIGN): use the highest rung that expresses the change; the run log records the rung mix per run (the share of changed files touched by each rung is a metric in section 10, not a rule). Free-form editing is never blocked, because the interface cannot see or stop an agent's own tools and pretending otherwise would be false comfort; it is checked by the same rules on the resulting tree.

### 7.2 What a codemod buys, measured on this repository

A textual rename of a domain word touches more than code. MEASUREMENT (`rename_probe`, 23 files under `src/eija_studio`, source tree hash prefix `35a152fec0f4ce75`, CRLF folded, Python `tokenize`):

| Word | Word-boundary text matches | As code NAME tokens | In strings, docstrings, comments | Code tokens directly after `.` |
|---|---|---|---|---|
| `approve` | 6 | 3 | 3 (50 percent) | 1 |
| `impact` | 8 | 6 | 2 (25 percent) | 2 |
| `receipt` | 21 | 16 | 5 (24 percent) | 0 |
| `verify` | 14 | 9 | 5 (36 percent) | 4 |
| `closure` | 2 | 2 | 0 | 0 |
| `fingerprint` | 22 | 22 | 0 | 0 |

Reading, with limits. For a concept rename the non-code hits are not necessarily wrong (prose should follow the term) but they are different kinds of site: a docstring is a `documents` edge to update, a string literal may be a wire or storage value that must not change, a comment is free text. A codemod separates the kinds and reports string references as `unresolved` for a decision. Even among code tokens the probe is only syntactic: 4 of the 9 `verify` name tokens follow a dot (attribute access on some object), so a token match is a candidate, not a resolved reference; resolution needs scope and type information (LibCST metadata, or SCIP). One repository, six words chosen by me, no claim about rates elsewhere.

### 7.3 EditSet

Schema in the contract (`EditSet`, `FileChange`, `TextEdit`). Design points:

- Offsets are UTF-8 byte offsets into the LF-folded content (D-06), not identities. Each edit carries `old_sha256` of the bytes it replaces; each file carries `precondition_sha256` (and optionally `postcondition_sha256`). Any mismatch fails closed (`PRECONDITION_MISMATCH`), and a file already at its postcondition reports `ALREADY_APPLIED` (idempotence). A file with mixed line endings is refused.
- Edits within a file must not overlap (reported as `OVERLAP`); two EditSets over disjoint files commute, and this is a property test (apply in both orders, compare bytes).
- Mapping to SARIF 2.1.0: an EditSet is a `fix` object whose `artifactChanges` are the `FileChange`s and whose `replacements` carry `deletedRegion` and `insertedContent`; `precondition_sha256` and `applicability` live in `properties`. SARIF defines the fix as a proposed solution; in the sections I read (3.55 to 3.57) I saw no precondition field, which is why ours go in `properties`.
- `applicability` uses the rustc vocabulary the incremental dossier recommends (`machine_applicable`, `has_placeholders`, `maybe_incorrect`, `unspecified`); I did not reopen the rustc guide.
- Generated files are regenerated, not edited: `regenerate_view` returns a `commands` entry (pinned generator and arguments), because generated views are get-only lenses.
- A rename emits `{old_id, new_id}` records (`renamed_to`, D-23); a removal without a record is WV-008.

### 7.4 Why no MCP apply in v1

Applying an EditSet through the server would put file writes on a surface whose current guarantee is "nothing here changes the workspace except a case". A flag-gated `editset_apply` is reserved (contract section 8). The deterministic benefit is available without it: the agent applies the edits itself and the checker re-runs.

## 8. Verifying agent-produced links: untrusted producer, small trusted checker

Pattern: a certifying algorithm produces an output with a witness and a checker accepts or rejects from the input, output and witness, so the user need not trust the producer; the authors stress that the checker must be simple and that the user must be able to see why the witness proves the output (McConnell, Mehlhorn, Naeher, Schweitzer; the LEDA maximum-matching module is 280 lines and its checker 26 lines, read in the PDF). Applied here: the agent (or an extractor) proposes a link; the checker recomputes what it can from L0 sources; the owner decides.

### 8.1 What the checker verifies for `proposal_submit(kind: link)`

| Step | Check | Recomputed from | Reject code |
|---|---|---|---|
| C1 | The proposal validates against the schema; `(type(from), kind, type(to))` is an allowed edge signature | `graph/schema` (hash-pinned; an agent cannot widen it) | `SIGNATURE_VIOLATION` |
| C2 | Both endpoints exist in the snapshot | node table via okf `parse_uri` | `ENDPOINT_MISSING` |
| C3 | The hash method equals the policy method for this link kind; the target digest is computed by the checker | okf `digest(root, ref, method)` on the target slice | `METHOD_POLICY_MISMATCH`, `UNRESOLVABLE_TARGET` |
| C4 | Origin is `inferred`; if the kind would count toward a gate, it does not until a declared line and a ledger baseline exist | link record and `link_status` (ADR-0093) | `INFERRED_CANNOT_SATISFY_GATE` |
| C5 | Obligations do not shrink (section 8.3) | keyed diff of the obligation set on the overlay | `OBLIGATION_REDUCED` |
| C6 | Same-author flag: requirement, verifier and satisfier all introduced by the current `agent_run` with no owner-approved statement digest | worktree changes plus statement pins (ADR-0103) | `SAME_AUTHOR_EVIDENCE` (advisory unless policy makes it blocking) |
| C7 | The subject is not under a protected path | protected-path policy | `PROTECTED_SUBJECT` |
| C8 | A missing resolver or parser | extractor status | `NOT_RUN` |

**What acceptance means.** `ACCEPTABLE_FOR_REVIEW` says: well-typed, anchored to existing endpoints, digest recomputed, not gaming the obligation set. It does not say the requirement is satisfied by the symbol: that is a semantic judgement, which is why a human ledger entry is the only clearing act. The proposal record is inert (contract `proposal_submit`).

### 8.2 Trusted computing base

The checker is `eijagraph.proposals.check` plus `link_status`, the okf digest functions, the schema files, Python and `hashlib`. Target: a checker small enough to read in one sitting (PREDICTION: on the order of 200 lines; not measured, and a line-count gate is proposed so the claim can fail). Everything the agent supplies is treated as data: a digest, a status or a verdict in a request is rejected by the schema (contract C-13, `additionalProperties: false`, test `test_every_input_forbids_extra_properties_and_has_no_trusted_status_field`).

### 8.3 The moved-goalpost guard

Let `O(S)` be the obligation set of a snapshot: `(requirement id, statement digest)`, `(invariant id, statement digest)`, owner-pinned statement digests, enabled rule ids with their severities, suppression fingerprints, acceptance-matrix rows. For a change `S -> S'` require `O(S) \ O(S')` to be covered by ledger decisions, else `OBLIGATION_REDUCED`. Reason: coverage `kappa(S) = |{r in R(S) : r has a COVERED verifier}| / |R(S)|` rises when `R` shrinks, so deleting or weakening requirements, lowering severities, disabling rules or adding suppressions can make a gate green without evidence. The guard is a rule over the graph, so it also fires on free-form edits, not only on MCP proposals. It is aimed at the observed failure classes: weakened postconditions and escape hatches in vericoding (about 9 percent of specs too weak in the sampled outputs, per the assurance dossier, S23; not reopened) and AGENTS.md's ban on changing protected policy merely to pass a task. New rule ideas requested from the rules aspect (ADR-0097): **WV-048 obligation-reduced** and **WV-049 same-author-evidence**; the existing WV-038, WV-045 and WV-046 cover pinned statements, suppressions and baseline growth.

### 8.4 Dependencies stated as interfaces

`link_status(link, current_digest, ledger)` and the ledger (ADR-0093, 0094); `assess_link` and statement pinning (ADR-0102, 0103); the okf `digest` and `parse_uri`; the edge-signature schema (ADR-0092). Open point for the ledger aspect: whether a new declared link needs an owner baseline for every kind or only for kinds that satisfy gates. The agent surface works either way; the owner's ack load per pull request is a metric.

## 9. Replay logs

### 9.1 What is recorded, and by whom

Format: contract section 7. One directory per run: `header.json`, `events.jsonl` (hash chain), `blobs/<sha256>` (content-addressed bodies), optional `timing.jsonl` (never hashed; wall-clock and token usage integers live here so artefacts stay time-free, D-04).

| Recorded | Source | Trust |
|---|---|---|
| Tool calls, envelopes, `graph_root` per call | MCP server | Server-authored; recomputable |
| Worktree changes at each call (path, before and after SHA-256, after-content blob) | Server, from file contents | Observed at tool-call granularity only |
| Proposals and checker verdicts | Server | Recomputable |
| Model and client messages | Client transcript imported as blobs | **Self-reported, unverified** |
| Model id, client name and version | Client | Self-reported |
| Provider kind `live`, `mocked` or `recorded`; egress | Providers lane (`provider_run`) | Mocked is never called live; mocked runs are excluded from reliability statistics |

What the server cannot see: the agent's shell commands, its native editor calls, its private reasoning, and edits between two tool calls except as file diffs at the next call. The log says so in `session_close` (a `coverage` note), and no result is described as "the whole run".

### 9.2 Chain and seal

`event_hash = dhash("eija.weave.agent-run-event.v1", {"prev": prev, "event": event})` (identity aspect's convention: `"sha256:"` + SHA-256 over the ASCII tag, NUL and the RFC 8785 subset bytes); the first `prev` is `sha256:` followed by 64 zeros; `run_id` is the last event hash. MEASUREMENT (200-event synthetic chain with astral and BMP keys): editing one field in any of the 200 events is detected at that event (200 of 200); swapping any adjacent pair is detected (199 of 199); dropping the last event is detected; re-ordering dictionary keys does not change the head. A chain detects accidental and naive tampering. It does not stop a party who can rewrite the whole file from recomputing every hash, so `session_close` records the head sealed by the kernel's existing receipt signer (HMAC, an integrity seal that is not institutional identity, per the kernel documentation). AGENTS.md's limit applies: an agent with the owner's OS permissions is not prevented from touching files.

### 9.3 Replay modes

| Mode | Procedure | Establishes | Does not establish |
|---|---|---|---|
| Verify-replay (audit) | Rebuild each recorded `graph_root` from `base_commit`, `overlay_sha256` and the observed changes; re-issue each recorded call; compare `response_hash`; re-run the checker on each proposal; recompute `findings_digest` | The deterministic side of the run reproduces; any divergence is a tool bug, a pin drift or tampering | That the model would say the same thing again |
| Counterfactual replay | Same recorded calls against new rules or pins; report which responses change | The effect of a rule change on an old run (regression review) | Anything about the model's behaviour under the new rules |

Outcomes: PASS (every response reproduces), FAIL (a response, root or proposal verdict differs, with the first divergence located), NOT_RUN (a pinned tool, grammar or Python minor version is unavailable, or the log is marked partial). A log with `--graph-run-log off`, a size-quota overflow or a truncated chain is `PARTIAL` and can never PASS (D-14, D-15).

MEASUREMENT (toy tool = kernel `impact.closure` on a 120-node graph, 40 recorded calls): 40 of 40 responses reproduce on the same snapshot; removing one edge changes `graph_root` and therefore every response's hash (40 of 40, because responses carry the root), while the affected set actually changes in 8 of 40. This shows why the root is in every response: drift is detected even when the specific answer happened not to change.

### 9.4 Why record and replay rather than regenerate

Thinking Machines measured 80 unique completions in 1000 requests at temperature 0 for one prompt on one model, and traced it to batch-size-dependent kernels; their deterministic-kernel fix costs time. EIJA drives vendor CLIs and hosted APIs and cannot change kernels. So reproducibility comes from recording at the boundary EIJA controls. VCR.py's cassette idea (record then replay HTTP) is the inspiration; the boundary differs because the agents are CLIs, so the recorded interface is the MCP tool boundary and the worktree.

### 9.5 The human view of a run (DESIGN, unmeasured)

`eija graph run-report <run_id>` renders, deterministically from the log: the task and pins, the pack (ids and hashes) the agent requested, tool calls in order with bounds, files changed with before and after hashes, findings delta (new, absent), links that became SUSPECT, proposals with checker verdicts, and the honest limits (what the server could not see). It is the answer to "what happened", and it is a projection of the log, not a narrative written by a model. That it helps a reviewer is a PREDICTION for the hci lane to test (interface: the log and `snapshot_diff`).

### 9.6 Privacy and export

Logs contain prompts, code and possibly secrets typed into prompts. They stay under `.eija/` (gitignored) by default; export to `evidence/agent-runs/` (an `agent_run` node) is an owner act with redaction of blobs marked private. The agents lane's redaction rules (question text without expected answers, no seals) apply to tool results before they are recorded.

## 10. Evaluation design for agent reliability

### 10.1 Questions and falsifiers

| Id | Hypothesis | Falsified if |
|---|---|---|
| H1 | With the graph interface, tasks are solved more reliably: higher mean per-task success and higher pass^k | The paired difference's 95 percent interval includes 0 or is negative at the planned power, or the false-accept rate rises |
| H2 | Cost per solved task (tool calls, tokens) is not higher | Median cost per solved task rises by more than the pre-registered margin |
| H3 | Fewer incomplete changes reach the final tree undetected: lower false-accept rate against hidden checks | False-accept rate not lower |
| H4 | Each lever contributes: read tools, packs, feedback (`diagnostics_get`, dry runs), codemods, proposals | Removing the lever leaves the primary metric unchanged within noise (exploratory) |
| H5 | Predicted ripple is informative: ripple recall above a stated floor | Recall at or below the floor set from the pilot |
| H6 | Pull beats push for packs | Push arm equal or better |

Circularity guard: a task whose success predicate is a graph rule (for example "no WV-010 findings") measures conformance to the compiler, which the graph arm satisfies by construction. Those are reported separately as compiler-conformance tasks and never as evidence of benefit. Benefit tasks use oracles that do not read the graph (section 10.3).

### 10.2 Arms (same model, same CLI version, same tool budget, same prompt template per task)

| Arm | Repository state | Tools |
|---|---|---|
| A0a | Repository as before the weave lane (no `graph/`, no OKF wiki, no `docs/weave`) | Native tools, tests, existing MCP surface (ADR-0041 tools) |
| A0b | Weave artefacts present as files | Same as A0a; no graph tools |
| A0c | As A0b | A0b plus a **graph-free pack**: lexical retrieval (ripgrep-based) filling the same budget, same envelope. Controls for the pack idea versus the graph |
| A1 | As A0b | Core tier read tools only (`graph_status`, `graph_node`, `graph_search`, `graph_neighbors`, `graph_impact`, `diagnostics_get`) |
| A2 | As A0b | A1 plus `context_pack`, pull (agent decides) |
| A2p | As A0b | A1 plus `context_pack` result pushed into the first prompt |
| A3 | As A0b | Full core tier (adds `edit_preview`, `txn_dry_run`, `proposal_submit`) |
| A4 | As A0b | Extended tier (all 20) |

Primary contrast: A3 versus A0b (does the interface help when the artefacts are already readable) and A3 versus A0a (does the whole weave lane help). A0c isolates the graph from packs in general. A1 to A4 form the ablation ladder; tool count (core 10 versus extended 20) is a factor because more tools can hurt tool selection (a hypothesis; no number opened).

### 10.3 Tasks and oracles

| Source | Construction | Oracle | Independence from the graph |
|---|---|---|---|
| Historical | Commits with a fix and tests in the EIJA history (SWE-bench-style: task statement, base commit, tests from the fix; SWE-bench instances pair an issue with a pull request containing tests) | Hidden tests from the fix commit plus a differential behavioural check in the style of PatchDiff | Independent |
| Seeded | Domain-model changes with known ground truth authored by the owner or a second person (add a transition; rename a domain term across code, UI, docs, tests; split a concept), each with hidden acceptance tests and a hand-written checklist | Kernel receipts and browser or API tests; the checklist | Independent (authored before the graph rules) |
| Held-out repository | One or two other Python repositories with tests, chosen before any run | Their own tests plus hidden mutants | Independent; Python only (graph extractors are Python-first) |

Threats named up front: contamination (models may have seen public repositories; the EIJA repository is recent, which reduces but does not remove this); the graph rules being written by the same team that writes the tasks; task selection favouring graph-friendly work. Mitigation: freeze the task manifest (ids, base commits, oracle hashes) and commit its SHA-256 before any run.

### 10.4 Metrics

| Metric | Definition | Label |
|---|---|---|
| Per-task success `q_hat_t` | `c_t / n` from the hidden oracle, not from the agent's report | MEASUREMENT |
| `pass^k` | `mean_t C(c_t, k) / C(n, k)`, defined in tau-bench; the plug-in `(c_t/n)^k` is biased upward (section 10.5) | MEASUREMENT with n stated |
| `pass@k` | `mean_t (1 - C(n - c_t, k) / C(n, k))` (Chen et al., unbiased estimator; reported for comparison only) | MEASUREMENT |
| False-accept rate | Share of runs that pass the visible tests and the agent's own check but fail a hidden check | MEASUREMENT |
| Cost | Tool calls, input and output tokens from CLI usage output (self-reported), cost units of responses, elapsed time from `timing.jsonl` | MEASUREMENT, self-reported |
| Rung mix | Share of changed files by edit rung (section 7.1) | MEASUREMENT |
| Ripple recall and precision | Section 6.2 | MEASUREMENT |
| Pack recall@B | Section 5.7, offline | MEASUREMENT |
| Owner-only attempts | Calls to absent operations (protocol errors) | MEASUREMENT; expected 0 |
| Replay audit result | PASS, FAIL or NOT_RUN per run | MEASUREMENT |
| Reviewer accuracy and time with and without semantic diff | Owned by the hci lane; interface: run log and `snapshot_diff` | UNMEASURED |
| Any confidence percentage, "trust" or "risk" score | Not computed | Not shipped |

### 10.5 Statistics

**Estimators (exact).** For task `t` with `c_t` successes in `n` trials, `pass^k_t = C(c_t,k)/C(n,k)` is the fraction of the k-subsets of trials that are all successes. If trials are exchangeable Bernoulli(`q_t`) given the task, its expectation is `q_t^k` (each k-subset is all-success with probability `q_t^k`), so the estimator is unbiased for `q_t^k`; similarly `1 - C(n-c,k)/C(n,k)` is unbiased for `1 - (1-q)^k`. The plug-in `(c/n)^k` is biased upward for `0 < q < 1`, `k >= 2` (Jensen, `x^k` convex). MEASUREMENT (exact enumeration, `n = 6`, 11 rational `q`, all `k`): both estimators unbiased, the plug-in above truth in every case; at `q = 1/2`, `n = 8`, `k = 4` the plug-in overshoots by 203/4096 (0.050). Chen et al. make the same point for pass@k (their Appendix A).

**Why pass^k.** MEASUREMENT (hand-built, exact): two agents each with 3/4 success over 10 tasks x 8 trials. Agent A succeeds 6 of 8 on every task: pass^1 = 3/4, pass^2 = 15/28 = 0.54, pass^4 = 3/14 = 0.21, pass^8 = 0. Agent B is perfect on 7 tasks, 4 of 8 on one and 0 of 8 on two: pass^1 = 3/4, pass^2 = 101/140 = 0.72, pass^4 = 491/700 = 0.70, pass^8 = 7/10. The same average hides opposite reliability profiles, which is what tau-bench's metric is for.

**Unit and interval.** The unit is the task (trials within a task are correlated). The estimate is `mean_t` of the per-task estimator; the paired difference is `Delta_hat = mean_t (X_A,t - X_B,t)`. Intervals: percentile bootstrap over tasks, resampling tasks with a SplitMix64 stream from a seed committed in the manifest (so the analysis is reproducible), plus an analytic standard error over tasks. Miller (arXiv 2411.00640) treats evaluation questions as draws from a super-population and gives formulas for analysis, model comparison and experiment planning; I read the abstract only, so which of his estimators are adopted is decided after reading the paper (UNVERIFIED detail). Report `n`, `c_t` per task, model id, CLI version, date. The primary endpoint is `Delta` in mean per-task success (pass^1), because power planning is exact for it; pass^n and pass^4 are pre-registered key secondaries, with bootstrap intervals.

**Variance, reported not assumed.** For every arm report the variance components: the between-task variance of `q_t` (as the sample variance of `c_t / n` minus its expected sampling part `mean v_a / n`), the mean within-task Bernoulli variance `v_a = mean_t q_hat_t (1 - q_hat_t) * n/(n-1)` (the `n/(n-1)` factor makes it unbiased for `q (1 - q)`), and the intraclass share `rho = Var_t(q) / (Var_t(q) + v_a)`. High `rho` means task difficulty dominates and more tasks help; low `rho` means the agent is inconsistent on a task, which is what pass^k exposes. The gap `pass^1 - pass^n` per arm is reported as an inconsistency index (0 for a deterministic agent). These numbers also feed the next study's power calculation, replacing the assumptions in 10.6.

**Multiplicity.** One primary contrast (A3 versus A0b). Other contrasts are labelled exploratory.

### 10.6 Sample size (PREDICTION: arithmetic on assumptions)

By the law of total variance, with tasks sampled from a population and trials independent given the task,

```text
Var(Delta_hat) = ( sigma_D^2 + (v0 + v1) / n ) / T
sigma_D^2 = Var_t(q1_t - q0_t),   v_a = E_t[ q_a,t (1 - q_a,t) ]
T >= (z_{0.975} + z_{0.8})^2 * ( sigma_D^2 + (v0 + v1)/n ) / delta^2,     z_{0.975} + z_{0.8} = 2.8016
```

Assumptions (stated because nothing here is observed): base success 0.5, between-task variance of `q` equal to 0.06 so `v_a = 0.25 - 0.06 = 0.19` and `v0 + v1 = 0.38`, target `delta = 0.10`, two-sided 0.05, power 0.8, normal approximation. Tasks needed `T`:

| `sigma_D` | n = 1 | n = 3 | n = 5 | n = 10 |
|---|---|---|---|---|
| 0.05 | 301 | 102 | 62 | 32 |
| 0.15 | 316 | 118 | 78 | 48 |
| 0.30 | 369 | 171 | 131 | 101 |

Reading: when task-level heterogeneity of the effect is small, extra trials per task buy a lot (`sigma_D = 0.05`: 301 tasks at n = 1 versus 62 at n = 5); when it is large (0.30) they buy little, and only more tasks help. Minimum detectable difference for `sigma_D = 0.15`, n = 5: 0.197 at T = 20, 0.161 at 30, 0.124 at 50, **0.100 at 78**, 0.072 at 150, 0.051 at 300, 0.030 at 866. So with a feasible 78 tasks x 5 trials the study can only detect about 10 points; the 2 to 3 point effects seen for interface levers in the literature (section 2) would need hundreds of tasks. Consequences: (1) run a pilot first (about 10 tasks x 3 trials x 2 arms, excluded from the confirmatory analysis) to estimate `sigma_D`, `v_a` and cost per run; (2) fix `T` from the pilot and pre-register the minimum detectable difference; (3) state in advance that a null result means "no effect of at least MDE detectable", not "no effect".

Budget: 78 tasks x 5 trials x 2 arms = 780 agent runs for the primary contrast; the full eight-arm ladder is 3,120 runs. Cost per run is unmeasured (the spend-observability lane will supply it after the pilot).

### 10.7 Procedure

1. Freeze the manifest: task ids, base commits, oracle files by SHA-256, arms, seeds, analysis script hash. Commit the manifest hash before any run (pre-registration).
2. For each (task, trial): run every arm back to back in an order drawn from the seeded stream, so provider-side drift hits arms equally (blocked randomisation). Each run gets a clean worktree from the base commit.
3. Record model id, CLI version, date, tool tier, quota, provider kind. Refuse mocked runs (`provider.kind = mocked`).
4. Score with the hidden oracles after the run, outside the agent's reach; store the score in the run log's `session_close`.
5. Run the replay audit on every run (E10). A FAIL is a bug to fix before analysis; NOT_RUN is reported.
6. Analyse with the frozen script; report in `eija.weave.agent-eval.v1` (results, n, c per task, intervals, MDE, exclusions with reasons). Timing sections are separate from deterministic sections (metrics-lane convention).

Harness reuse (ADR-0016): Inspect AI (MIT, UK AI Security Institute; last push 2026-09-28) provides `pass_k` ("probability that all k epoch attempts succeed using a draw-without-replacement estimator"), `pass_at` and `at_least` reducers, so the reducer is not rebuilt; the bench's exact enumeration is used as the oracle that checks the estimator. Whether Inspect can drive external agent CLIs (Claude Code, Codex) inside a worktree was not verified (UNVERIFIED); if not, the runner is a small custom script that spawns the CLI, and Inspect (or the bench formulas) only scores. tau2-bench and SWE-bench (MIT) are sources of methods and, for Python tasks, harness ideas; not dependencies.

### 10.8 Threats to validity

| Threat | Effect | Mitigation |
|---|---|---|
| Oracle authored by the graph's authors | Inflates the graph arm | Independent oracles authored before the rules; compiler-conformance tasks reported separately |
| Hidden-oracle leakage through the repository | The agent reads the tests | Oracles live outside the worktree until scoring |
| Provider or model drift during the study | Confounds arms | Blocked randomisation, dates recorded, replay of tool side |
| Contamination | Inflates all arms | Recent repository, held-out repository, note in report |
| Agent CLI updates | Confounds | Pin versions per study; record `client.version` |
| Trials not independent (caches, provider state) | Understates variance | Fresh worktrees; record session ids; note |
| Learning across trials | Overstates | No memory features enabled; recorded |
| More tools means more tool-selection errors | Understates the graph | Tier ablation |
| Self-reported token usage | Noise in cost | Reported as self-reported |
| Small `n` of tasks | Wide intervals | MDE stated in advance; pilot |
| Multiple comparisons | False positives | One primary contrast |
| METR result: experienced developers were 19 percent slower with early-2025 tools while expecting a speedup (16 developers, 246 tasks; arXiv 2507.09089, not reopened this session) | Reminder that assumed benefit can be wrong | Decide by measurement |

### 10.9 What would change the design

A pack recall no better than lexical retrieval at the same budget (drop or simplify the ranking). A push arm equal to pull (allow standing packs). `sigma_D` above 0.30 in the pilot (increase tasks, not trials). A tier ablation showing extended below core (shrink the tool set). False-accept rate unchanged (the graph's checks are not catching what hidden oracles catch: fix the rules, not the story).

## 11. Honest limits of this aspect

- The tool layer is a contract; no server exists. All server-side determinism claims are DESIGN except where a MEASUREMENT is stated.
- Synthetic-graph measurements show mechanisms (determinism, bounds), not the quality of packs on a real repository.
- The interface narrows what an agent may do through MCP; it is not a sandbox (AGENTS.md).
- A hash proves change, not correctness; a checker's acceptance proves mechanical well-formedness, not that a link is true.
- Nothing shows yet that agents or humans do better with any of this.

## 12. Interfaces to other lanes and aspects

| Counterpart | Weave provides | Weave needs | Open point |
|---|---|---|---|
| agents lane (ADR-0041) | `TOOL_SPECS` in `eijagraph` (name, `inputSchema`, `outputSchema`, annotations, handler), with a test asserting equality with the contract blocks; recorder hook; startup flags | Registration of the weave tools next to the seven existing ones; the AST test extended to the graph tools and to `interfaces/` never importing the ledger writer; the adapter that composes kernel pure functions with overlays for `txn_dry_run`; explicit construction of `CallToolResult` (section 4); `--graph-tools`, `--graph-quota`, `--graph-run-log` flags | Which MCP protocol version and SDK behaviour is negotiated (UNVERIFIED); where proposals are shown to the owner (Change Case attachment or a CLI listing) |
| providers lane | Recording fields (`provider.kind`, egress, `prompt_sha256`, usage integers) | `provider_run` including `live` and a mocked flag; a stable place to store the prompt hash | Whether provider prompts should include a pack (then `prompt_sha256` covers it) |
| okf lane | Consumption of `repo://`, `parse_uri`, `digest`, hash methods; packs and results may carry `resource_link`s to OKF pages instead of embedding text | Stable digest function and CRLF fold shared with weave | `workflow-semantic-v1` method (SYNTHESIS open question 4) |
| visual lane | `txn_dry_run` uses the same shape as the lens `translate(ViewModel, Edit) -> Accepted or Rejected` (ADR-0105) | Nothing for v1 | Whether diagram edits get an agent tool later |
| impact-ranking aspect | Consumes `ppr_int`, `select_context`, tiered impact (`eija.weave.impact.v1`), `select_tests`, change-risk vector, `pass_hat_k`; provides the pack layer (mandatory slots, levels, envelope, `pack_verify`) and the agent tool wrappers `graph_impact`, `context_pack`, `select_tests`, `change_risk` | Per-node `render_bytes` and per-test `cost` attributes from the schema aspect; `select_context` reporting all non-chosen eligible candidates; the `params` digest set on every result | Byte budget versus `render_bytes` (open question 11) |
| metamodel and identity aspect | Consumes node types, link kinds, id scheme and `sha256:` digest format from `metamodel.json`, `dhash` and the golden vectors; the contract's enums and node-id pattern are tested equal to it | Stable `metamodel_version`; edge ids (`eija.weave.edge-id.v1`) as link references | The earlier `brief.json` lists 37 node types and 27 link types; `metamodel.json` lists 42 and 29 (workflow elements became concrete types); the contract follows `metamodel.json` |
| consistency-sync aspect | Its rule that sync means regenerate, propose or ack matches the tool set (`codemod_plan` regenerates, `proposal_submit` proposes, ack is owner-only); its request that link records refer to `entry_id` rather than `ledger_seq` is followed by the contract (`baseline_entry`) | A canvas edit translator (deferred there) would be a further proposal producer | If the link aspect keeps `ledger_seq`, change one field |
| quality lane | `quality/sessions/graph.py` `fast` tier runs contract and bench tests; `full` tier runs permutation harness over tools once a server exists | Session plumbing; import-linter contract that `eijagraph` does not import `eija_studio` | None |
| metrics lane | Section for agent reliability: pass^k, false-accept rate, ripple recall, replay audit results, all MEASUREMENT with n | Convention for deterministic versus timing sections | Section name |
| hci lane | Run report and `snapshot_diff` as inputs to reviewer studies | The reviewer study design | Owned by hci |
| property lane | Edit-sequence strategies for the differential incremental test, commutation test of EditSets | Hypothesis strategies | None |
| mutation lane | Attach `fault_detection` to `verifies` edges (ARCHITECTURE section 9) so a proposal's verifier can be labelled anchored-only or calibrated | Mutation scores with tool pin | Vacuity guard for `verifies` proposals |
| tla, bend, smt-bmc | `evidence_get` reads `assess_link` results; witnesses are theirs | Witness schema (ADR-0102) | None |
| kernel | Reference oracles in tests only; a request that `SemanticTransaction`'s schema stay the single source (contract test compares) | Nothing new | Kernel change requests stay in ADR-0112 |
| other weave aspects | Consumes: node ids and fragment registry (ADR-0090), canonical hashing (ADR-0091), edge signatures (ADR-0092), link record and `link_status` (ADR-0093), ledger (ADR-0094), extractor labels (ADR-0095), storage, overlay and snapshot API (ADR-0096), rules and Finding (ADR-0097, 0098), incremental cache (ADR-0100), certificates (ADR-0102, 0103), lenses (ADR-0105), language (ADR-0106), UI (ADR-0107). Provides: WV-048, WV-049 requests; the `eijagraph.overlay.preview(snapshot, {path: bytes or None}) -> PreviewResult` interface needed by the storage aspect | See left | ADR number clash (open questions 1 and 13) |

## 13. Build order, reuse and cost

| Step | Deliverable | Exit criterion (measurable) | Phase |
|---|---|---|---|
| 1 | `eijagraph.mcp.specs` (`TOOL_SPECS`, checked equal to the contract blocks); envelope builder with `response_hash` | Contract tests plus golden envelope bytes equal on Windows; POSIX NOT_RUN reported | P3 |
| 2 | Read tools over the SQLite index (`graph_status` to `graph_impact`, `diagnostics_get`) | Permutation harness: 1 distinct response per golden request; `graph_impact` equals kernel `impact.closure` on the oracle set | P3 |
| 3 | `eijagraph.pack` over the ranking aspect's `eijagraph.rank` (integer ranking and selection) | Shuffle test 1 distinct pack; `pack_recall@B` reported against lexical and random | P3 |
| 4 | `eijagraph.runlog` and replay audit | 100 percent of recorded tool calls reproduce on the toy server; tamper tests as in the bench | P3 |
| 5 | Overlay, `edit_preview`, `txn_dry_run` | Purity test; ripple recall computed on the seeded tasks | P3 |
| 6 | `eijagraph.proposals.check` | Every rejection code has a negative fixture; checker line count reported | P3 |
| 7 | `eijagraph.codemod` (LibCST `rename_symbol`, range-edit `rename_term`) and EditSet property tests | Idempotence, commutation of disjoint EditSets, fail-closed on stale precondition | P3 |
| 8 | Pilot, then the pre-registered evaluation | Numbers with n, model id, date | P4 |

Reuse and licence roles (licence texts opened via the GitHub licence API or pages on 2026-09-29, except where marked). Full OSS-check table in the ADR.

| Tool | Licence | Role for an Apache-2.0 package |
|---|---|---|
| MCP Python SDK | MIT (LICENSE text) | Dependency of the agents lane; not ours |
| jsonschema | MIT (synthesis, PyPI) | Dependency (`graph` extra) |
| LibCST | MIT with PSF-derived files listed in its LICENSE (text read; GitHub reports NOASSERTION) | Dependency in phase 3 (`codemod_plan`) |
| Inspect AI | MIT (LICENSE text) | Optional process for the study; not in the `graph` extra |
| tau2-bench, SWE-bench | MIT (SPDX; tau2-bench text read) | Inspiration (metric definition, task construction) |
| Aider, RepoGraph | Apache-2.0 (Aider text read; RepoGraph SPDX) | Inspiration (repo-map ranking, k-hop retrieval); no code copied; the ranking used is the impact-ranking aspect's integer implementation |
| VCR.py | MIT (SPDX) | Inspiration (record and replay) |
| OpenTelemetry GenAI semantic conventions | Apache-2.0 (SPDX); stability status UNVERIFIED | Optional export target for run logs; not adopted for the format |
| ast-grep | MIT (SPDX) | Optional process for non-Python codemods (phase 2 or later) |
| SQLite (stdlib), `hashlib`, `json` | public domain, PSF | Dependency |

ADR number: the harness assigned this aspect **0099**; ARCHITECTURE section 11 and `brief.json` give 0099 to the determinism doctrine and 0108 to the agent query set. Both files are in the block; the integrator must reconcile before merge (open question 1).

## 14. Measurement ledger

Command: `python graph/bench/agent_interface_checks.py` (about 18 s; stdlib plus read-only kernel import and the sibling reference; output byte-identical across `PYTHONHASHSEED`, `LC_ALL` and `TZ` in two runs on Windows 11, Python 3.12.10, SQLite 3.49.1). POSIX: NOT_RUN. Oracles: `tests/graph/test_agent_interface_checks.py` (13 tests) and `tests/graph/test_agent_interface_contract.py` (11 tests). The bench imports `graph/bench/impact_math_reference.py` (the impact-ranking aspect's reference) and reports NOT_RUN for checks that need it if it is absent.

| Fact | Value | Label |
|---|---|---|
| pass^k and pass@k estimators unbiased; plug-in biased | exact, n = 6, 11 q values; plug-in bias 203/4096 at q = 1/2, n = 8, k = 4 | MEASUREMENT |
| Two agents, equal pass@1 | pass^8 = 0 versus 7/10 | MEASUREMENT (hand-built) |
| Tasks needed, minimum detectable difference | tables in section 10.6 | PREDICTION |
| Golden vectors of the identity aspect | this bench's writer reproduces 10 of 10 JCS byte strings and 10 of 10 node hashes; 3 of 3 must-reject cases rejected | MEASUREMENT |
| Pack identity under shuffles | 1 distinct pack in 40 shuffles; a float ranking would have selected the same items (1 distinct sequence) | MEASUREMENT, synthetic 300 nodes |
| Ranking and selection quality, float non-determinism, co-change recall | not measured here; reported by the impact-ranking aspect | see that document |
| Hash chain tamper detection | 200 of 200 edits, 199 of 199 swaps, truncation detected, key order irrelevant; naive concatenation collides, `dhash` does not | MEASUREMENT, synthetic |
| Toy tool replay | 40 of 40 reproduce; 40 of 40 flagged by root after one edge removed; 8 of 40 actually changed | MEASUREMENT, synthetic |
| SQLite instruction-count limit | 1 distinct count over 5 runs and 10 shuffled insertion orders; aborts at half budget | MEASUREMENT, one platform |
| Text rename overreach | table in section 7.2 | MEASUREMENT, one repository, six words |
| Kernel dry run | table in section 6.2 | MEASUREMENT (kernel functions) |
| Effect of any of this on agents or humans | not measured | UNMEASURED |

## 15. Open questions

1. **ADR number**: 0099 (assigned) versus 0108 (ARCHITECTURE section 11, `brief.json`). Which record carries the agent interface, and does the determinism doctrine keep 0099?
2. **Proposal inbox**: where does the owner see `proposal_submit` records: a Change Case attachment (kernel, needs its own ADR), `.eija/proposals/` with a CLI, or the run report only?
3. **Ledger scope**: must every new declared link get an owner baseline, or only kinds that satisfy gates (ADR-0094)? This sets the owner's review load.
4. **Tier default**: is `core` (10 tools) the right default, and should the owner be able to choose per client? Decided by the tier ablation, not by taste.
5. **Worktree writes**: whether `editset_apply` ever ships (ADR-0041 precedent: adding a tool is a governance decision).
6. **MCP SDK bytes**: does `mcp==2.2.0` preserve a handler-built `CallToolResult`, and which protocol revision does it negotiate? Needs a wire-level golden test in the agents lane.
7. **Harness**: can Inspect AI drive external agent CLIs in a worktree, or is a custom runner needed? Verify before the pilot.
8. **Human benefit**: the hci lane's reviewer study design (interface: run report, `snapshot_diff`).
9. **POSIX**: all byte-identity claims are Windows-only; one run on Linux or WSL and committed goldens are needed (SYNTHESIS open question 8).
10. **Rules**: acceptance of WV-048 and WV-049 by the rules aspect.
11. **Cost model**: the pack budget is bytes of rendered items; the impact-ranking aspect uses OKF page bytes (`render_bytes`). One definition per node type and level is needed from the schema aspect.
12. **Link references**: the contract references links by edge id (metamodel) and ledger baselines by an opaque `baseline_entry`; the consistency-sync aspect asks for `entry_id` instead of `ledger_seq`, the link aspect has not answered.
13. **Which numbering wins**: every aspect currently writes its own ADR numbers (this one 0099, ranking 0097, consistency 0093, metamodel 0089); the integrator maps them onto the ARCHITECTURE section 11 table or amends it.

## 16. Sources (opened 2026-09-29)

| Source | What was read |
|---|---|
| https://modelcontextprotocol.io/specification/2025-11-25/server/tools | Tools page: outputSchema, structuredContent, annotations, errors, security considerations |
| https://modelcontextprotocol.io/specification/2026-07-28/server/tools | Same page for the latest revision: stateless requests, deterministic tool order, stateful-tools handles |
| https://modelcontextprotocol.io/specification/latest | Latest revision identified as 2026-07-28 |
| https://arxiv.org/html/2405.15793 | SWE-agent ablation Table 3 numbers |
| https://www.anthropic.com/engineering/writing-tools-for-agents | Tool-writing guidance, 25,000-token default cap, 72 versus 206 token example |
| https://aider.chat/docs/unified-diffs.html | 20 to 61 percent unified-diff result on 89 tasks |
| https://aider.chat/docs/repomap.html | Repo map ranking and 1,000-token default |
| https://arxiv.org/html/2410.14684 | RepoGraph improvements and stated limitations |
| https://arxiv.org/abs/2602.11988 | AGENTS.md study: no success gain, cost up over 20 percent |
| https://arxiv.org/abs/2307.03172 | Lost in the middle abstract |
| https://arxiv.org/abs/2310.01798 | Self-correction abstract |
| https://arxiv.org/abs/2306.09896 | Self-repair abstract |
| https://arxiv.org/abs/2503.15223 | PatchDiff abstract with 7.8, 29.6 and 6.2 figures |
| https://arxiv.org/abs/2310.06770 | SWE-bench task design (issue plus pull request with tests) |
| https://arxiv.org/abs/2408.02442 | Format restrictions abstract |
| https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/ | 80 unique completions in 1000; cause; kernel timing |
| https://arxiv.org/html/2406.12045 and https://arxiv.org/abs/2406.12045 | tau-bench pass^k definition and pass^8 statement |
| https://arxiv.org/pdf/2107.03374 (PDF read locally) | pass@k unbiased estimator and the bias of `1 - (1 - p_hat)^k` (Appendix A) |
| https://raw.githubusercontent.com/openai/human-eval/master/human_eval/evaluation.py | Reference `estimate_pass_at_k` implementation |
| https://arxiv.org/abs/2411.00640 | Miller: error bars for evals (clustered SE, paired differences, power) |
| https://inspect.aisi.org.uk/reference/inspect_ai.scorer.html and https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_ai/main/README.md | Inspect reducers `pass_k`, `pass_at`, `at_least`; project description |
| https://people.mpi-inf.mpg.de/~mehlhorn/ftp/CertifyingAlgorithms.pdf (PDF read locally) | Certifying algorithms definition; LEDA 280 versus 26 lines |
| https://www.rfc-editor.org/rfc/rfc8785 | UTF-16 code-unit key order; number rules; informational status |
| https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/sarif-v2.1.0-errata01-os-complete.html | `fix`, `artifactChange`, `replacement`, `baselineState` |
| https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool | `str_replace`: `old_str` must match exactly |
| https://libcst.readthedocs.io/en/latest/codemods_tutorial.html | Codemods and `CodemodTest`; no determinism claim on the page |
| https://docs.python.org/3/library/sqlite3.html | `set_progress_handler`, `set_authorizer`, read-only URI |
| https://en.wikipedia.org/wiki/Maximum_coverage_problem | Budgeted variant attribution (secondary source; primary not opened) |
| https://github.com/open-telemetry/semantic-conventions-genai | Repository exists, Apache-2.0; stability not stated on the page |
| GitHub API `repos/{r}` and `repos/{r}/license` for UKGovernmentBEIS/inspect_ai, sierra-research/tau2-bench, modelcontextprotocol/python-sdk, Instagram/LibCST, Aider-AI/aider, ozyyshr/RepoGraph, SWE-bench/SWE-bench, ast-grep/ast-grep, kevin1024/vcrpy | Licence, archived flag, last push (all active except RepoGraph, last push 2025-04-01; Aider last push 2026-05-22) |
| Repository files read: `src/eija_studio/domain/{impact,models,policy}.py`, `application/service.py`, `AGENTS.md`, `docs/weave/research/*`, `docs/weave/ARCHITECTURE.md`, `graph/brief.json`; sibling aspects' files in this worktree (`graph/schema/metamodel.json`, `README.md`, `identity-vectors.json`, `graph/bench/identity_checks.py`, `graph/bench/impact_math_reference.py`, `docs/weave/design/impact-ranking-and-confidence.md`, `docs/weave/design/consistency-and-sync.md`); sibling worktrees `agents` (`interfaces/mcp_server.py`, ADR-0041, `docs/agents/contract.md`) and `providers` (`adapters/providers/*`), read-only | Existing surface, owner-only list, kernel pure functions, provider recording |
