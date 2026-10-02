# EIJA: evidence and bounded V&V protocol

Research cutoff: 2 October 2026. Prepared from primary public research and a read-only review of the integration checkout. This is a proposed protocol, not collected EIJA user-study results. The owner's first target is EIJA itself; external projects are not selected or connected by this document. Current engineering acceptance is tracked in [SELF-DOGFOOD-ACCEPTANCE.md](../engineering/SELF-DOGFOOD-ACCEPTANCE.md).

## The claim worth testing

EIJA should let a UML-literate engineer understand and control the meaning of an agent's changes, with less review effort and fewer missed consequential defects. It should connect ordinary repositories and make supported structural facts deterministic, while keeping uncertain domain interpretations visibly provisional.

"Higher quality V&V" is currently an architectural ambition. It becomes a result only after comparing actual outcomes against an appropriate baseline. "Any codebase" is an extensibility ambition: repository intake with explicit coverage, followed by supported extraction and behavior bindings. It does not mean universal inference or proof of every language and business rule.

## Strong empirical evidence available by the cutoff

| Source and date | Method and finding | Boundary and EIJA implication |
|---|---|---|
| [Martin-Lopez et al., More Code, Less Understanding?](https://doi.org/10.1109/TSE.2026.3679627), online 31 March 2026, IEEE TSE July issue; [author manuscript](https://personal.us.es/amarlop/wp-content/uploads/2026/03/More-Code-Less-Understanding-On-the-Impact-of-AI-Assistants-on-Developers-Productivity-and-Code-Ownership.pdf) | Crossover experiment with 69 participants: 47 students, 8 researchers, 14 professional developers. Each performed two coding tasks, with and without AI. AI yielded more than twice the median task completeness but 12.5% lower performance answering technical questions about their implementation. Overall time effects were inconclusive. | Immediate code-ownership questions are not long-term competence; small professional subgroup and varied tasks. Measure ability to explain and change code separately from completion. |
| [Shen and Tamkin, How AI Impacts Skill Formation](https://www.anthropic.com/research/AI-assistance-coding-skills), 29 January 2026 | Randomized study of 52 mostly junior Python developers unfamiliar with Trio. AI users averaged 50% on an immediate comprehension quiz versus 67% without AI; d=.738, p=.01. The roughly two-minute time gain was not significant. | New-library learning with a sidebar assistant, not a test of current agentic IDEs. Interaction-pattern associations are exploratory, not randomized evidence that explanations cause learning. EIJA needs objective comprehension checks, not only reassuring explanations. |
| [Qiao et al., Faster but Not Wiser](https://arxiv.org/abs/2511.02922v3), revised 27 September 2026 | Within-subjects study of 15 CS graduate students adding features in an unfamiliar codebase. Copilot improved performance without an overall comprehension improvement (p=.59). Higher-comprehension participants made more write-then-view transitions. | Small student sample. Category correlations did not survive multiple-comparison correction; workflow association is not causation. Supports treating correct output and correct mental model as distinct measures. |
| [He et al., AI Writes Faster Than Humans Can Review](https://arxiv.org/abs/2607.01904v1), 2 July 2026 | One-company longitudinal panel: 802 developers, 196,212 PRs, January 2024–April 2026. Throughput reached 2.09 times baseline; reviewer load roughly doubled; automated review overtook human review; merge and revert rates were stable. | Observational adoption and intensity, single AI-forward company, PR activity is not delivered value. Cannot establish exact causality or comprehensive quality. Review capacity is a credible problem even where generation gains are large. |
| [Borg et al., Echoes of AI](https://link.springer.com/article/10.1007/s10664-026-10889-1), 9 June 2026 | Preregistered two-phase experiment, 151 participants, 95% professional. New participants evolved Java application variants with no AI in phase 2. No significant subsequent time or code-quality difference between AI-assisted and manual antecedents. Phase-1 AI use associated with a 30.7% median time reduction. | Data collected in late 2024 before current agents. Bounded application and maintenance tasks. Important counterevidence: do not claim AI-written code inherently has worse maintainability. |
| [Cui et al., three field experiments](https://www.microsoft.com/en-us/research/publication/the-effects-of-generative-ai-on-high-skilled-work-evidence-from-three-field-experiments-with-software-developers/), June 2025 | Randomized access to coding completion assistance across three companies and 4,867 developers. Pooled estimate: 26.08% more completed tasks, standard error 10.3%. Less experienced developers had greater adoption and gains. | Access to completion tooling and task throughput, not EIJA, comprehension, or present-day agents. A fair EIJA baseline should retain strong AI assistance. |
| [METR productivity update](https://metr.org/blog/2026-02-24-uplift-update/), 24 February 2026 | Follow-up included 57 developers, 143 repositories and over 800 tasks. Raw estimates suggested improvement from the early-2025 result, but researchers explicitly judge the signal unreliable due participation/task selection and concurrent-agent time measurement. | Do not present the 2025 19% slowdown as current universal fact, or the later estimates as established speedups. Predeclare eligible tasks, preserve dropouts, and measure active human time separately from wall time. |

The evidence establishes a serious problem worth tackling, plus heterogeneous AI benefits. None of these studies establishes that UML, EIJA, or deterministic graphs fix it.

## Distinguish the four assurance questions

1. **Software verification:** Does EIJA faithfully implement its contracts? Tests, property tests, negative controls, schema checks and E2E journeys answer this within their exercised scope.
2. **Formal model verification:** Do encoded properties hold under specified assumptions and bounds? Report which law, model/source hash, checker, bound, assumptions and result. An SMT result and a bounded trace check are different evidence.
3. **Model fidelity:** Does the model correspond to the actual application and the owner's intended rules? AST extraction proves structural facts only within adapter semantics; conformance tests and independently annotated source links test correspondence. Human confirmation is required for domain meaning that code cannot uniquely establish.
4. **Product validation:** Do engineers make better decisions or learn enough to maintain the result, at a useful cost? Only observed human work and real task outcomes answer this. Thousands of internal tests cannot substitute for this question.

All evidence should bind to an exact repository revision or content manifest, model revision, adapter/checker versions and relevant dependency/configuration hashes. Source change makes dependent evidence stale. Reordering harmless input should not. A green result with the wrong subject is a failure.

## One bounded end-to-end acceptance milestone

Finish one continuous loop on **EIJA's own checkout** before connecting an external repository or broadening the assurance portfolio:

**Connect snapshot → inspect actual structure/domain hypotheses → capture one agent's change → see a semantic explanation with source links and UML → inspect ripple and evidence → accept or reject the proposed model change through the existing owner flow → export and replay a review packet.**

Keep the first milestone finite: one safe change, one consequential unsafe change, one stale-source case and one unsupported-language/construct case. A pair of overlapping worktree changes belongs to the later comparison milestone, unless the integration run explicitly implements and tests that capability. Broader fuzzing/proof expansion should follow a discovered defect or supported feature, not postpone the usable loop indefinitely.

Acceptance observations:

| Observation | Required result |
|---|---|
| Fresh setup from documented instructions | A person can launch the workbench and connect the chosen local snapshot; record command, platform, elapsed time and errors. |
| Repository intake | Preserve the source tree; report included, excluded, binary/generated/unparseable/unsupported files and reasons. A file hash is not a semantic link. |
| Repeatability | Identical snapshot and configuration produce the same canonical structural graph, diagnostics, impact results and evidence subjects, excluding explicitly nonsemantic timestamps. |
| Structural honesty | Every claimed symbol/edge has a source location and extraction method. Unresolved dynamic dispatch, imports, reflection and unavailable dependencies are shown as unknown, not guessed as facts. |
| Domain honesty | Inferred business concepts and language bindings are labelled proposals until confirmed or source-supported. Conflicting meanings can coexist pending resolution. |
| Safe change | Valid change is reviewable, succeeds through the intended flow, regenerates views, and preserves unrelated work. |
| Unsafe change | A planted rule violation produces the correct affected concept, reason and witness/source path. It is caught even when the ordinary positive test still passes. |
| Staleness | Change a relevant source/configuration/law; old evidence stops being current. Unrelated edits do not invalidate everything indiscriminately. |
| Later cross-worktree comparison | After the first self-dogfood loop passes, two agents alter the same rule through different files; check whether semantic overlap is visible without a textual conflict. Any landing claim uses checks on the combined result. This is not a first-flow completion claim. |
| Usable UI | Real ordinary browser-to-server journey, source navigation, keyboard alternative to diagram gestures, and actionable refusal. Bridged component tests alone are not relabelled browser E2E. |
| Portability | A fresh workspace can replay the packet against its declared snapshot and reproduce the deterministic results. |

Block this milestone on data loss, false evidence attribution, an undetected declared critical fixture, broken safe path, or inability to complete the chosen real-repo journey. Noncritical unsupported features get an explicit limitation and backlog entry. Do not hold this milestone hostage to proving all software.

## Repository selection and the meaning of generality

The first and currently selected target is **EIJA itself**. Dogfood source links, supported structural indexing, model edits and evidence on its actual checkout. It is a familiar development case and cannot count as held-out evidence.

Only after that acceptance passes, select the next small portfolio before outcome access: a small owner-chosen application, a full-stack application with a different supported language/framework, and a previously unseen public repository. Record each scope, license, build/test prerequisites, allowed data and independent oracle before connection. No external project is selected by this protocol. Use local snapshots and synthetic data; repository validation does not require provider actions.

The held-out repository must be selected after the relevant adapter/core contract freezes by an evaluator other than the implementer. Include a partially supported case to test honest coverage. External adoption, cross-repository generality and held-out results remain NOT_RUN until separately executed.

Do not fit a custom pack to every chosen repo and then call that universal extraction. Count adapter changes, manual bindings, setup minutes, unsupported constructs, incorrect links, missed links and tasks that cannot be represented. If the held-out task forces core/adapter edits, record a development failure and choose a new held-out case for the next evaluation.

Separate coverage levels: repository intake; file/dependency structure; supported symbol/call/control structure; confirmed domain-rule links; checked behaviours. A repository may pass intake with no domain-level assurance. The UI should make that distinction immediately visible.

## Independent oracle and defect corpus

Have an evaluator author expected behaviour from requirements and executable observations, without reusing EIJA's implementation or generated graph as the truth. Store the oracle manifest before running either condition. Keep hidden evaluation cases outside the agent-visible context. The evaluator can be a separate agent for an initial engineering test, but this is only partial independence: shared models/assumptions can still agree on a mistake. A maintainer or other human should adjudicate the final domain meanings and reviewer-study answer key.

For each fixture record: base and changed revision/content hash; requirement; expected behaviour; exact defect and affected invariant; independent source references; executable hidden check; allowed interpretations; severity; discovery date; authored-by provenance; contamination status. Make a paired safe variant so a tool that rejects everything cannot win.

Include:

- a label rename that silently changes permission or persisted semantics;
- a removed precondition/guard that existing happy-path tests miss;
- a state reached without its required predecessor;
- a second code path violating a displayed invariant;
- stale tests/proof/model after an implementation change;
- a misleading proposed semantic summary contradicted by source;
- an omitted dependency, dynamic call or indirect effect;
- a harmless refactor that should not become a critical warning;
- two individually valid branches whose combined change violates a rule;
- a legitimate unknown where no sound result is available.

Score critical misses, correct detections, false alarms and abstentions separately. Report precision/recall only over a declared annotated set, with unmodelled behaviours visible in the denominator. A model checker cannot detect an unencoded business intention by itself.

## Fair automated task comparison

Use the same current coding model/version, initial repository, task statement, visible tests, tools, machine, time cap, number of attempts and parallelism for both conditions. The baseline is ordinary agent coding plus ordinary tests/review; EIJA adds its graph/context and review surface. Account for EIJA indexing, annotation, model repair and evidence generation, including failed attempts. Do not give EIJA the hidden answer key or unique domain requirements.

Two tracks answer different questions:

- **Fixed-patch review:** present identical changes to both conditions. This isolates whether the EIJA explanation and graph improve reviewing a given change.
- **Build and evolve:** run the same five successive feature/refactor changes from a frozen baseline in each condition. This tests generation plus review plus accumulated drift. Freeze task order for an initial demonstration; randomize/counterbalance it in the later experiment where order is not intrinsically required.

First deliver a deterministic fixture replay with full receipts. Then run a small live pilot with a budget declared before execution; record all replicates rather than cherry-picking the best run. Expand only if the pilot is usable. Report task correctness, preservation of existing behaviours, hidden defects, setup cost, active human time, elapsed time, tokens/currency, interventions and rework. Report sequence success and the raw numerator/denominator of repeated successful runs; do not inflate assurance by adding unlike test counts together.

## Human validation that can actually establish comprehension value

Recruit 6–8 UML-literate engineers for a feasibility pilot. This is a product study, not a statistically decisive superiority claim. Include different levels of professional and AI-tool experience; record both. Give everyone the same short training and separate practice tasks.

Use counterbalanced within-person review tasks with matched but different changes so nobody sees the same answer twice. Everyone retains a strong coding assistant. Compare ordinary source diff + tests + agent explanation with the same material plus EIJA. A later ablation can add a plain source-grounded diagram without EIJA to distinguish visualization from the extra checking/context.

Predeclare the primary endpoint as **correct review decisions within the fixed review time**, with critical misses separately protected. A decision is only correct when its stated reason and impacted behaviour agree with the independent oracle. Measure:

- identification of changed concepts, rules and consequences;
- detection of seeded hidden defects and false rejection of safe changes;
- time to a correct decision and active navigation effort;
- confidence calibration, not just confidence;
- explanation of a new consequence not stated in the tool's summary;
- delayed recall and a small follow-up maintenance task after 24–72 hours, if feasible;
- setup/annotation overhead, subjective workload and reported usefulness.

Instrument only agreed task activity. Separate subjective ease from objective understanding. Blind answer grading to condition when possible, use a fixed rubric, have two graders adjudicate disagreements, and retain censored/abandoned tasks in the report. The person writing a persuasive EIJA explanation should not be the sole grader.

Use the pilot to estimate variability, task difficulty, ceiling/floor effects, overhead and a realistic sample size. For a later confirmatory study, preregister sample size, meaningful effect threshold, acceptable critical-miss margin, exclusions, missingness handling and analysis before viewing outcomes. Analyze repeated observations with participant/task clustering. Report confidence intervals and uncertainty; no significance hunting across many metrics.

## Practical stop/continue decisions

Ship an engineering preview once the bounded real-repo E2E loop and its required controls pass, with explicit adapter and assurance limits. That demonstrates functioning software.

Continue investing in the product hypothesis if the human pilot shows engineers can correctly explain changes, catch consequential defects and use the flow without excessive setup or interruption. If EIJA merely produces attractive diagrams, raises confidence without accuracy, misses dynamic paths while implying completeness, or consumes the time it purports to save, fix that observed problem before adding another proof backend.

Reserve claims such as "better V&V", "reduced comprehension burden" and "works across codebases" for the exact measured task/repository/population envelope. Publish failures alongside successful examples. A finite useful release and honest limits are compatible with an ambitious product.

## Local document observations relevant to delivery

The product thesis calls this a hypothesis to test and specifies hybrid code/model work, prompt-first extraction, UML as a working surface, semantic diffs, source ripple and worktree-aware review. Its 2 October clarification makes EIJA self-dogfood the first target and distinguishes the initial read-only connection from later source transformation. `docs/engineering/STATUS.md` records the combined Phase-1 tree as not yet fully gated and the workbench as not implemented at the saved checkpoint; it also records 77% tool waiting in a prior two-hour run. These are saved observations, not fresh execution results.

`docs/verification/VERIFICATION.md` carefully distinguishes local tests, mocked providers, real TCP, bridged browser rendering, independent assurance and absent human data. Preserve that precision. `docs/adr/0028-runtime-conformance-by-graph-comparison-and-trace-validation.md` provides a useful fidelity pattern: compare the real runtime to a bounded model, include a deliberately wrong model, and state what the abstraction omits. Reuse that pattern where it applies rather than inventing a universal proof claim.
