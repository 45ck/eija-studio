# ADR-0099: Agent interface: typed read tools, deterministic context packs, pure dry runs, a small link checker and hash-chained replay

* Status: proposed
* Date: 2026-09-29
* Lane: weave (aspect: agent-interface). Number note: this record was assigned 0099; `docs/weave/ARCHITECTURE.md` section 11 and `graph/brief.json` allocate 0099 to the determinism doctrine and 0108 to the agent query set. The integrator must reconcile before merge (design document, open questions 1 and 13: every aspect currently writes its own numbers). References to "ADR-0093" and similar below use the ARCHITECTURE section 11 numbering.

Design, evidence and arithmetic: [docs/weave/design/agent-interface-and-context-packs.md](../weave/design/agent-interface-and-context-packs.md). This record consumes, and does not redefine, the metamodel and identity aspect (`graph/schema/metamodel.json`, `identity-vectors.json`) and the impact-ranking aspect (`docs/weave/design/impact-ranking-and-confidence.md`). Normative contract, machine-checked: [graph/schema/mcp-tools.md](../../graph/schema/mcp-tools.md). Reproducible checks: `graph/bench/agent_interface_checks.py`, `tests/graph/test_agent_interface_checks.py`, `tests/graph/test_agent_interface_contract.py`.

## Context and problem statement

The weave graph will hold typed, hash-anchored links over code, UI, diagrams, language, requirements, tests, proofs and evidence, with a checker that reports findings. External coding agents (Claude Code, Codex, OpenCode, Gemini CLI) connect to EIJA through the MCP server of ADR-0041, whose rule is "AI proposes, the kernel checks, the local owner decides", and which exposes seven case tools and no owner operation. How do agents use the graph so that their work is more reliable and a person can see exactly what happened, without letting an agent choose meaning, clear a suspect link, move a goalpost or apply anything, and without making the interface itself a source of non-determinism? And how is the claim "this helps" tested rather than assumed?

## Decision drivers

* Determinism doctrine D-01 to D-24: same inputs, byte-identical outputs; no wall clock, locale or hash-seed dependence; a missing prerequisite is NOT_RUN and absorbs PASS.
* Untrusted producers, a small trusted checker, a human decision (ARCHITECTURE section 6). Agents and providers never approve or apply. Owner operations must be absent from the surface, not merely denied (ADR-0041).
* Evidence on agent interfaces: bounded, linted, summarised tool output helped in ablations (3 to 6 points on SWE-bench Lite, one model, one paper); repository-level static context did not help and cost over 20 percent more; structural retrieval gave 2 to 2.7 points; models are non-deterministic even at temperature 0 (80 unique completions in 1000); tests alone are a leaky oracle (design document, section 2).
* Agents call vendor CLIs; EIJA cannot embed a decoder, change kernels or see the agent's own tools.
* MCP facts: `outputSchema` conformance is a server MUST; serialized JSON in a TextContent block is a SHOULD; annotations are untrusted; the 2026-07-28 revision has no protocol session and requires a per-connection-stable tool list (pages opened 2026-09-29).
* OSS first (ADR-0016): adapters, not engines.
* No benefit to agents or humans is claimed until measured; the measurement must be designed so a null result is interpretable.

## Considered options

Interface shape:

* A. **Typed, bounded query tools with a hash-carrying envelope** (chosen).
* B. Expose a query language (Cypher through a graph-database MCP server, or read-only SQL) to the agent. Rejected: a stateful GPL/SSPL/BSL server or an unbounded query surface in the trust path; text-to-query errors are the agent's problem; cost bounds by wall clock break D-04. A read-only SQL tool remains reserved behind an owner flag with an instruction-count limit (measured stable, section 4 of the design).
* C. Graph as files only (OKF pages plus grep and the agent's own file tools). Kept as evaluation arm A0b; it has no impact closure, no witnesses and no checker feedback.
* D. Push a graph summary into a standing prompt or AGENTS.md. Rejected on the AGENTS.md study (no gain, cost up over 20 percent); tested as arm A2p rather than assumed.

Context selection:

* E. **Deterministic budgeted pack: exact mandatory obligations, then the impact-ranking aspect's integer personalised PageRank and budgeted selection** (chosen). Aider's repo map and RepoGraph are the inspiration; no code is reused. This aspect adds the pack layer only.
* F. Embedding or vector retrieval. Rejected for the deterministic path: results depend on model and index versions (reasoning, not measured); may be an evaluation baseline.
* G. Pack ranked by float PageRank (networkx or the obvious loop). Rejected: bit patterns depend on summation order (the impact-ranking aspect measured 40 of 40 differing hashes); in this aspect's 40-shuffle pack sample the selected items did not change, so this is an insurance decision, stated as such.

Edits:

* H. **Ladder: typed semantic transaction, codemod EditSet, anchored text edit, free-form observed** (chosen), with tools returning proposals only.
* I. Free-form edits only, checked afterwards. Kept as the floor; not blocked because the interface cannot see the agent's own tools.
* J. Codemod-only. Rejected: cannot express most changes; the probe shows text rename overreach but no codemod covers all work.
* K. MCP tool that applies EditSets to the worktree. Deferred behind an owner flag (governance decision, ADR-0041 precedent).

Link verification:

* L. **Certifying-style checker over inert proposals** (chosen): recompute endpoints, signature, method, digest and obligation monotonicity; the owner decides.
* M. Trust the agent's link with a digest it supplies (the Doorstop-style stored fingerprint, written by the producer). Rejected: the producer would vouch for itself.
* N. LLM-judge of link plausibility. Rejected as evidence (inferred proposals cannot satisfy a gate); may rank a review queue.

Reproducibility:

* O. **Server-side hash-chained log of the deterministic side, client transcripts imported as self-reported blobs, verify-replay and counterfactual replay** (chosen).
* P. Rely on client transcripts alone. Rejected: not recomputable, not tamper-evident.
* Q. HTTP cassettes (VCR.py style). Rejected: wrong boundary for CLI agents.
* R. Regenerate the model output and hope. Rejected on the non-determinism measurement.

Evaluation:

* S. **Pre-registered paired study: task as unit, pass^k over n trials, eight arms including a graph-free pack control, hidden independent oracles, pilot first** (chosen). Inspect AI's `pass_k` reducer for scoring where usable.
* T. Report pass@1 on a benchmark. Rejected: hides inconsistency (measured example: same 3/4, pass^8 of 0 versus 7/10).
* U. Build a bespoke harness. Rejected unless Inspect cannot drive the agent CLIs (unverified).

## Decision outcome

Chosen options: A, E, H, L, O and S, because together they keep every agent-visible fact a recomputable function of (snapshot, request), keep decisions with the owner, and make the benefit claim falsifiable.

### Decision details

1. **Tool surface.** 20 tools: `core` (10) `graph_status`, `graph_node`, `graph_search`, `graph_neighbors`, `graph_impact`, `diagnostics_get`, `context_pack`, `edit_preview`, `txn_dry_run`, `proposal_submit`; `extended` (10) `graph_why`, `select_tests`, `change_risk`, `link_status`, `diagnostics_explain`, `language_lookup`, `evidence_get`, `pack_verify`, `snapshot_diff`, `codemod_plan`. Fixed at server start by the owner; listed in name order. `graph_impact`, `context_pack`, `select_tests` and `change_risk` carry the impact-ranking aspect's results. Schemas, envelope, error codes, cursor and budget rules are in the contract (C-01 to C-18); its node and link enums, id pattern and digest format are tested equal to `metamodel.json`.
2. **Envelope and determinism.** RFC 8785 subset serialisation, integers only, `graph_root`, `request_hash`, `response_hash` (the identity aspect's `dhash`: `sha256:` over ASCII tag, NUL and the canonical JSON; the bench writer reproduces all 10 golden vectors), total orders, sorted set arguments, keyset cursors bound to the root, budgets in cost units (UTF-8 bytes of canonical JSON), call quota instead of a rate limiter, self-validation against `outputSchema` before sending, golden `tools/list` hash.
3. **Context pack.** `pack_id` is a hash of the normalised request, root and ranking parameters. Mandatory slots (seed, statement, verifier, term, finding, suspect, ripple summary) are exact and are the "pinned" input of the ranking aspect's `select_context`; `BUDGET_TOO_SMALL` reports the needed cost and never drops an obligation. The optional tier uses that aspect's bit-exact personalised PageRank and budgeted selection (its at-least-half-of-optimum argument and measurements are there, not repeated here); this record adds levels (handle, summary, slice, a heuristic upgrade rule), omission accounting, the envelope and `pack_verify`. Packs are pulled per task, never standing context. Item hashes make freshness a hash comparison. The same aspect's offline co-change study reports the default ranking beating a graph-free path-prefix baseline on one of two repositories and tying it on the other, hence the graph-free pack arm in the evaluation.
4. **Dry runs.** `txn_dry_run` composes the kernel's pure `apply_transaction` and `model_impact` (in the agents lane's adapter, since `eijagraph` must not import the kernel) with an `eijagraph` overlay; the verdict, delta and closure are the kernel's, the graph ripple is `eijagraph`'s and is labelled PREDICTION. `edit_preview` applies an EditSet to an in-memory overlay. Neither writes.
5. **Edits.** EditSet with per-file `precondition_sha256`, per-edit `old_sha256`, optional postcondition (idempotence), non-overlap, disjoint EditSets commute, mixed line endings refused, SARIF `fix` mapping, renames as `{old_id, new_id}` records, generated files regenerated not edited. No MCP apply in v1.
6. **Checker for agent-produced links.** Steps C1 to C8 in the design (signature, endpoints, method and recomputed digest, inferred class, obligation monotonicity, same-author flag, protected subject, NOT_RUN). Accepting means mechanically well-formed and non-gaming, never that the link is true. New rule ideas for the rules aspect: WV-048 obligation-reduced, WV-049 same-author-evidence.
7. **Absent operations.** The eleven ADR-0041 owner operations plus ledger append, ack, statement approval, policy and schema edits, rule disabling, suppression and baseline growth, receipt minting, status override, consent, keys, free-form query and external process execution. A test lists them and asserts none is a tool.
8. **Replay.** `eija.agent-run.v1`: header, hash-chained events, content-addressed blobs, unhashed timing sidecar. Server-authored events are recomputable; model messages are self-reported. Verify-replay and counterfactual replay return PASS, FAIL or NOT_RUN and never PASS on a partial log. The head is sealed with the kernel receipt signer (integrity seal, not institutional identity).
9. **Evaluation.** Unit of analysis is the task; estimator `C(c,k)/C(n,k)` (unbiased under exchangeable trials, verified by exact enumeration); paired differences with bootstrap intervals from a committed seed; primary contrast A3 versus A0b; graph-free pack control A0c; minimum detectable difference stated in advance (about 10 points at 78 tasks x 5 trials for an assumed `sigma_D` of 0.15: PREDICTION); pilot first.

### Consequences

* Good: an agent's view of the graph is reproducible from a root hash; every answer states what it omitted; owner authority is enforced by absence and by a test; the link checker is small enough to read; dry runs teach the required order of semantic operations from typed codes (MEASUREMENT: `set_rejection_source` before `enable_recommendation` gives `MEANING_REQUIRED`); the evaluation cannot be won by circular tasks and states what a null means; ripple recall turns graph incompleteness into a per-run number.
* Bad: 20 tools is a large surface and tool count may hurt selection (ablated, not assumed); contract and schema upkeep (mitigated by tests that validate the document itself); the ranking and its weights are heuristics (its measured advantage over a path-prefix baseline is uneven, see above); overlay builds cost time per preview (unmeasured); logs may contain sensitive prompts; the server sees only its own traffic and file diffs, so a replay proves the tool side only; the study is expensive (780 runs for the primary contrast at 78 tasks x 5 trials x 2 arms; cost per run unmeasured).
* Not established: that any of this raises agent success or human understanding; that `bytes` track `tokens` for any model; that the MCP SDK preserves handler-built bytes (UNVERIFIED); POSIX byte-identity (NOT_RUN); the effect of the ranking weights.
* Revisit when: the pilot shows `sigma_D` above 0.30 (change the design of the study, not the tools); `pack_recall@B` is not better than lexical retrieval at the same budget (drop or simplify ranking); the tier ablation shows `extended` below `core` (shrink the set); the false-accept rate does not fall (fix the rules); a required agent client cannot take `structuredContent` (fall back to text only with the same bytes); the MCP SDK reorders or re-serialises results (build the result explicitly); the kernel adds transaction kinds (regenerate the schema, the test compares it); an owner wants worktree writes over MCP (new ADR).

## OSS check (required for any custom module)

Licence roles for an Apache-2.0 package. "Text" means the licence file head was opened this session (2026-09-29); "SPDX" means GitHub metadata only.

| OSS checked | Licence (basis) | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|---|
| MCP Python SDK (`modelcontextprotocol/python-sdk`) | MIT (text) | Adopted through the agents lane (`mcp==2.2.0`); weave adds only tool specs and handlers. What the SDK does to result bytes is unverified, so the handler builds the result explicitly | Replace the one adapter file; the contract is protocol-version independent |
| jsonschema | MIT (synthesis, PyPI) | Adopted (`graph` extra) to validate envelopes, EditSets and examples | None needed |
| RFC 8785 (`rfc8785` 0.1.4, Apache-2.0 per synthesis) or the identity aspect's subset writer | Apache-2.0 | The identity aspect owns the subset writer and `dhash`; this aspect only uses them. Its bench carries an independent short writer that reproduces the identity golden vectors (10 of 10 JCS strings and node hashes), so the two implementations cross-check each other | Swap in the library once vectors pass |
| LibCST | MIT with PSF-derived files (text; GitHub reports NOASSERTION) | Adopt in phase 3 for `rename_symbol`; the codemod tutorial page I read makes no determinism or idempotence claim, so ours are tested; EditSet, preconditions and unresolved-site reporting are custom | ast-grep (MIT, optional process) for JS, TS, CSS; range edits for Markdown |
| ast-grep | MIT (SPDX) | Optional process for non-Python fixes | None |
| Inspect AI | MIT (text) | Its `pass_k`, `pass_at` and `at_least` reducers score the study; whether it drives external agent CLIs is unverified. Optional process outside the `graph` extra | Bench formulas score; custom runner spawns the CLI |
| tau2-bench, tau-bench, SWE-bench harness | MIT (text for tau2-bench; SPDX for the others) | Inspiration for the metric definition and task construction; not dependencies | None |
| Aider repo map | Apache-2.0 (text) | Inspiration for personalised ranking under a budget. Per the agent dossier's reading of `repomap.py` (not reopened) it ranks with networkx float PageRank and caches by mtime, both banned by D-10 and D-04; the integer version and hash keys are the impact-ranking aspect's and ours | The ranking module is that aspect's `eijagraph.rank`; this record depends on it |
| RepoGraph | Apache-2.0 (SPDX) | Inspiration for k-hop retrieval; Python only, GPT-4 series only | None |
| VCR.py | MIT (SPDX) | Record and replay idea; wrong boundary for CLI agents | Own hash-chained log |
| OpenTelemetry GenAI semantic conventions | Apache-2.0 (SPDX); stability UNVERIFIED | Possible export mapping for run logs; not adopted as the format because the log needs hash chaining and content-addressed blobs | Export adapter later |
| Neo4j or another graph-database MCP server | GPL-3.0 server (synthesis, text opened there) and others rejected in ADR on storage | Would put a stateful server outside git in the trust path and expose free-form queries | Export target only |
| SQLite (stdlib) | public domain | Dependency; deterministic resource limits by `set_progress_handler` instruction count | None |

Custom modules (each with a `docs/oss/REGISTER.md` row to append at integration; not appended by this aspect to avoid write conflicts on the shared file): `eijagraph.mcp` (tool specs, envelope, handlers), `eijagraph.pack` (mandatory slots, levels, omission accounting, `pack_verify`; ranking and selection come from `eijagraph.rank`), `eijagraph.editset` (EditSet, applier for previews), `eijagraph.codemod` (rename planners), `eijagraph.proposals` (checker), `eijagraph.runlog` (chain, replay audit), `graph/eval` (manifest and analysis, phase P4). Justification common to all: none of the OSS above provides a typed envelope over the EIJA graph, a budgeted pack with exact obligations, a precondition-hashed EditSet, a link checker keyed to the ledger, or a hash-chained tool-boundary log; each is small, has an oracle, and can be replaced module by module.

## Interfaces and open questions

Interfaces to the agents, providers, okf, visual, quality, metrics, hci, property, mutation, tla, bend, smt-bmc and kernel lanes, and to the other weave aspects (ADR-0090 to ADR-0107), are tabulated in design section 12. Open questions are design section 15: the ADR number, where the owner sees proposals, the ledger scope for new links, the default tier, worktree writes, SDK byte behaviour, whether Inspect can drive agent CLIs, the human-benefit study, POSIX byte-identity and acceptance of WV-048 and WV-049.
