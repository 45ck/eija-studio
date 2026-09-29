# Agent reliability and context: what the evidence supports

Lane: weave. Dossier: agent-reliability. Access date for every URL: 2026-09-29. Status: research input for ADR block 0089-0112, not a decision.

## Decisions first

| # | Decision | Confidence | Evidence in this file |
|---|---|---|---|
| 1 | Give agents a small typed query interface over the graph (search, neighbours, impact, explain), not a prose dump of it. | High for "small, targeted, linted tool output"; medium for "graph retrieval helps" | SWE-agent ablations (section 2.1), RepoGraph, AGENTS.md study |
| 2 | Treat deterministic kernel diagnostics as the feedback signal in the agent loop. Never rely on the agent's own judgement of its work. | High | Huang 2023, Olausson 2023, DafnyBench, AutoVerus |
| 3 | Assume the agent is non-deterministic even at temperature 0. Record every agent proposal content-addressed. Determinism is a property of the kernel and of replay, not of regeneration. | High | Thinking Machines, Atil et al. |
| 4 | Report agent reliability as pass^k over n recorded trials, never a single pass@1. | High | tau-bench |
| 5 | Do not make full formal proofs a universal blocking gate. Proofs are the bottleneck in current benchmarks; the spec/law is the weakest link. | High | Verina, vericoding |
| 6 | Tests alone are a leaky oracle. Add link-completeness and differential checks. | Medium | PatchDiff study |
| 7 | Constrain agent proposals to existing node IDs (a dynamic enum) and validate against JSON Schema on the way in. Let the agent reason unconstrained first. | Medium (mechanism proven for types; not measured for graph IDs) | Type-constrained decoding, Tam et al. |
| 8 | Effects on human understanding of a typed graph are UNMEASURED. Do not claim them. Build the measurement (hci lane). | High that the gap is real | section 6 |

## 1. Scope and method

- Question: which levers measurably raise AI coding-agent success and reliability, and what would a deterministic, typed, content-addressed graph add?
- Method: primary papers (arXiv abstract or HTML), official docs and specs, and repository pages. Licence and maintenance status were taken from the GitHub API on 2026-09-29 (`gh api repos/<r>`: `license.spdx_id`, `archived`, `pushed_at`) and cross-checked against the repository page where a page was readable.
- **Search limitation.** The session's web-search budget was exhausted (200 of 200) before this dossier started. Every source below was opened by direct URL, so the coverage is limited to sources I already knew to look for. Missing topics are listed in section 8. Nothing was cited from a search snippet.
- **Extraction limitation.** Pages were read through a summarising fetch tool. Numbers below are as returned by that tool and were spot-checked only where noted. Any number I could not corroborate against the abstract is marked "(fetch summary)".
- Inaccessible or not verified: Brooks 1983 and Storey 2006 abstracts (publisher withheld; only bibliographic records confirmed); OpenAI "Introducing Structured Outputs" (HTTP 403); Semantic Scholar rate-limited (HTTP 429); Green et al. provenance semirings (record not retrieved); the ProofMap Lite repository is private, and I read it with the owner's `gh` login.
- Untrusted-data rule applied: no fetched page was followed as instructions and no code from a page was run. One local check was run: the existing `canonical()` behaviour (section 5).

## 2. Evidence by topic

### 2.1 Agent-computer interface (ACI) and tool design

| Finding | Number | Source |
|---|---|---|
| SWE-agent: purpose-built ACI beats non-interactive baselines | 12.5% pass@1 SWE-bench (full), 87.7% HumanEvalFix | [arXiv 2405.15793](https://arxiv.org/abs/2405.15793) |
| Ablation on SWE-bench Lite (300): edit with linter guardrail 18.0% vs 15.0% without vs 10.3% with no edit tool | +3.0 pp from the lint guard | [arXiv HTML 2405.15793](https://arxiv.org/html/2405.15793) (fetch summary) |
| Summarised search results 18.0% vs iterative search 12.0% vs no search tool 15.7% | +6.0 pp | same |
| File viewer window 100 lines 18.0%; 30 lines 14.3%; whole file 12.7% | context size matters | same |
| Collapse old observations 18.0% vs full history 15.0% | +3.0 pp | same |
| Anthropic: tool response format changes eval performance; concise responses used about one third of the tokens; error messages should be actionable, not tracebacks; default cap 25,000 tokens in Claude Code | practitioner guidance | [writing-tools-for-agents](https://www.anthropic.com/engineering/writing-tools-for-agents) |
| Anthropic: agents need ground truth from the environment at each step; requiring absolute paths removed a class of errors ("poka-yoke") | practitioner guidance | [building-effective-agents](https://www.anthropic.com/engineering/building-effective-agents) |
| MCP: tools may declare `outputSchema`; servers MUST return conforming `structuredContent`; clients SHOULD validate; tool annotations are untrusted unless the server is trusted; execution errors go back to the model for self-correction | normative spec | [MCP 2025-11-25 tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) |

Reading: the strongest agent-success evidence in this dossier is about interface shape (linting on write, summarised search, bounded output), not about knowledge representation. Ablations are on SWE-bench Lite with one model family in one paper; treat as directional.

**What it gives EIJA:** the graph query tools must have bounded, paginated, schema-typed output; write tools must run the kernel linter before accepting an edit and return actionable, typed diagnostics. MCP `outputSchema` is the natural carrier. Cost: schema maintenance. Verdict: adopt.

### 2.2 Repo maps and code-graph retrieval

| System | What it does | Result | Status and licence | Source |
|---|---|---|---|---|
| Aider repo map | tree-sitter tags; file graph; personalised PageRank (`nx.pagerank`, edge weights scaled by `sqrt(num_refs)`, boosts for files in chat); output fitted to a token budget (default 1k, `--map-tokens`); disk cache keyed by mtime | no controlled success-rate figure found in the pages I read | Apache-2.0, last push 2026-05-22 | [repomap docs](https://aider.chat/docs/repomap.html), [repomap.py](https://raw.githubusercontent.com/Aider-AI/aider/main/aider/repomap.py) |
| RepoGraph | tree-sitter line-level graph, k-hop ego-graph retrieval, plug-in for other agents | SWE-bench Lite: +2.34 pp Agentless, +2.66 pp RAG, +2.33 pp AutoCodeRover, +2.00 pp SWE-agent. Python only, GPT-4-series only, Lite only (paper's stated limits) | Apache-2.0, last push 2025-04-01; ICLR 2025 | [arXiv 2410.14684](https://arxiv.org/abs/2410.14684), [HTML](https://arxiv.org/html/2410.14684) |
| CodexGraph | static analysis into Neo4j; an LLM writes natural-language queries, a second LLM translates to Cypher | CrossCodeEval Lite Python EM 27.90 vs 21.20 for BM25 and AutoCodeRover (fetch summary); 22.16k tokens vs 1.47k for BM25 on CrossCodeEval. Python only. The SWE-bench and EvoCodeBench numbers in the fetch summary looked duplicated, so I do not use them | paper says "work in progress"; code in Apache-2.0 ms-agent (UNVERIFIED that the CodexGraph agent still lives there) | [arXiv 2408.03910](https://arxiv.org/abs/2408.03910), [HTML v3](https://arxiv.org/html/2408.03910v3) |
| AutoCodeRover | AST/class/method-aware search plus spectrum-based fault localisation from tests | 19% SWE-bench Lite at about $0.43 per issue | ISSTA 2024; repository licence not checked (UNVERIFIED) | [arXiv 2404.05427](https://arxiv.org/abs/2404.05427) |
| Agentless | fixed three phases: localise, repair, validate; no agent loop | 32.00% SWE-bench Lite at $0.70 per task (paper); README later reports 40.7% Lite and 50.8% Verified with Claude 3.5 Sonnet | MIT, last push 2024-12-22 (stale) | [arXiv 2407.01489](https://arxiv.org/abs/2407.01489), [repo](https://github.com/OpenAutoCoder/Agentless) |

Counter-evidence: an ETH study found repository-level context files (AGENTS.md style) "does not generally improve task success rates, while increasing inference cost by over 20% on average"; repository overviews were unhelpful ([arXiv 2602.11988](https://arxiv.org/abs/2602.11988)). Chroma tested 18 LLMs and found performance degrades as input length grows even on simple tasks; distractors compound it ([context rot](https://www.trychroma.com/research/context-rot)). "Lost in the Middle" shows lower accuracy for information in the middle of long contexts ([arXiv 2307.03172](https://arxiv.org/abs/2307.03172)).

Reading, with the honest bound:
- Structural retrieval gives consistent but modest gains (about 2 to 3 pp absolute on SWE-bench Lite for RepoGraph) and can cost far more tokens (CodexGraph). It is not a large lever on its own.
- Static, always-on prose context can be net negative. On-demand, targeted retrieval is the safer design. This matches Anthropic's "just-in-time" guidance: keep lightweight identifiers, load on demand ([context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). Content-addressed node IDs are exactly such identifiers (an inference, not a measured result).
- Aider's mechanism (rank by graph centrality, personalise to the current task, fill a fixed token budget) is the reusable idea. Its weights are heuristics; I found no ablation validating them.

**What it gives EIJA:** a `graph.context(task_nodes, token_budget)` operation: personalised PageRank or k-hop closure over the typed graph, output sorted and truncated deterministically to a budget, with a `complete`/`frontier` flag exactly like `impact.closure` already returns. Cost: must pin float tolerance and tie-breaking (section 5). Verdict: adapt (algorithm from Aider, not its code).

### 2.3 Verifier-in-the-loop, tests and self-correction

| Finding | Source |
|---|---|
| Without external feedback, LLMs "struggle to self-correct their responses... at times, their performance even degrades" (ICLR 2024) | [arXiv 2310.01798](https://arxiv.org/abs/2310.01798) |
| Self-repair gains are "often modest" once repair cost is counted; the bottleneck is the quality of feedback; stronger-model or human feedback gives larger gains (ICLR 2024) | [arXiv 2306.09896](https://arxiv.org/abs/2306.09896) |
| Adding test cases to the prompt raised success on MBPP/HumanEval (GPT-4, Llama 3); small benchmarks | [arXiv 2402.13521](https://arxiv.org/abs/2402.13521) |
| SWE-bench patches that pass the tests are not always right: 7.8% pass the tests but fail the developer suite; 29.6% behave differently from the ground truth; reported resolution rates inflated by 6.2 pp | [arXiv 2503.15223](https://arxiv.org/abs/2503.15223) |
| Sampling: Codex solved 28.8% of HumanEval with one sample and 70.2% with 100 samples | [arXiv 2107.03374](https://arxiv.org/abs/2107.03374) |
| Original SWE-bench: best model solved 1.96% (2023 baseline, for scale) | [arXiv 2310.06770](https://arxiv.org/abs/2310.06770) |

Reading: verification helps when it is external, precise and cheap. Tests are necessary but leaky as the sole oracle, which is the case for link checks and differential checks that do not depend on the test suite being complete.

**What it gives EIJA:** the kernel's `assess_receipt` style output (typed, recomputed from raw observations) is the "high-quality feedback" the self-repair literature says is the bottleneck. Add graph diagnostics of the form "requirement R-12 has no verifying test", "node X changed, dependents Y, Z not re-verified" as machine-readable feedback. Verdict: adopt.

### 2.4 Structured output and constrained decoding

| Item | Licence | Status (GitHub API, 2026-09-29) | What it is | Source |
|---|---|---|---|---|
| Outlines | Apache-2.0 | active, pushed 2026-09-21 | JSON Schema, regex, CFG constrained generation for many backends | [repo](https://github.com/dottxt-ai/outlines) |
| XGrammar | Apache-2.0 | active, pushed 2026-09-28 | CFG engine; paper claims up to 100x speedup over prior solutions; MLSys 2025 | [repo](https://github.com/mlc-ai/xgrammar), [arXiv 2411.15100](https://arxiv.org/abs/2411.15100) |
| llguidance | MIT | active, pushed 2026-09-25 | Rust engine; README claims about 50 microseconds per token mask (vendor claim) | [repo](https://github.com/guidance-ai/llguidance) |
| OpenAI Structured Outputs | vendor API | n/a | `strict: true` guarantees schema adherence; supports a subset of JSON Schema; first request per schema has extra latency; refusals need not match the schema | [docs](https://developers.openai.com/api/docs/guides/structured-outputs) |
| JSONSchemaBench | paper CC BY 4.0 | n/a | 10K real-world schemas; compares Guidance, Outlines, llama.cpp, XGrammar, OpenAI, Gemini on efficiency, coverage, quality; concludes practical effectiveness is poorly understood | [arXiv 2501.10868](https://arxiv.org/abs/2501.10868) |

Cautions:
- Constraining format can hurt reasoning. "Let Me Speak Freely?" reports a significant decline in reasoning under format restrictions, worse with stricter formats ([arXiv 2408.02442](https://arxiv.org/abs/2408.02442)). I did not fetch any rebuttal; whether the effect holds for modern schema-aware decoders is UNVERIFIED. Safe design: free reasoning first, structured emission last.
- Structure is not meaning. A schema-valid proposal can still reference a non-existent requirement. This is where type-constrained decoding is relevant: constraining decoding with a type system's rules more than halved compilation errors and improved functional correctness on HumanEval and MBPP ([arXiv 2504.09246](https://arxiv.org/abs/2504.09246)); monitor-guided decoding used static analysis for type-consistent dereferences and let a 1.1B model beat a larger one on compile rate ([arXiv 2306.10763](https://arxiv.org/abs/2306.10763)). Both are on code generation, not on graph edits; transferring to "node ID must exist in the graph" is a design hypothesis.

**What it gives EIJA:** EIJA calls vendor CLIs and hosted APIs, so it cannot embed a decoder. It can (a) publish JSON Schemas (with an `enum` of live node IDs generated from the graph) as the contract, (b) validate on receipt with the kernel, and (c) reject with a typed error the agent can act on. Outlines, XGrammar and llguidance are therefore inspiration and possible export targets, not dependencies. Cost: dynamic enums grow with the graph; large enums pressure schema-compile time (OpenAI documents first-request latency). Verdict: adapt.

### 2.5 Spec-driven development

| Tool | Licence and status | What it is | Evidence of effect |
|---|---|---|---|
| spec-kit | MIT, pushed 2026-09-28 (GitHub API); README lists constitution, specify, plan, tasks, implement, converge commands | spec, plan, tasks workflow for agents | none found; process guidance | [repo](https://github.com/github/spec-kit) |
| Kiro | proprietary AWS product (Kiro Crew is open source, not evaluated) | requirements.md, design.md, tasks.md; dependency-graph "waves"; property-based tests in the IDE | vendor claims only; none independently verified | [specs docs](https://kiro.dev/docs/specs/), [kiro.dev](https://kiro.dev/) |

Reading: I found no peer-reviewed or independently measured evidence that spec-driven workflows raise agent success rates. They are process scaffolding. The EIJA-relevant idea is that their artefacts (requirements, design, tasks) are the nodes the graph would link; the value is the machine-checked links, not the file layout. Verdict: inspiration, and spec-kit as an export target.

### 2.6 Neurosymbolic verification (Dafny, Verus, Lean; Bend)

| Benchmark | Result | Source |
|---|---|---|
| DafnyBench (about 750 programs, 53k lines) | best 68% (2024); error-message feedback helped; success falls as annotation volume grows | [arXiv 2406.08467](https://arxiv.org/abs/2406.08467) |
| AutoVerus (Verus) | proofs for more than 90% of 150 tasks; more than half in under 30 s or 3 LLM calls; multi-agent with verifier feedback | [arXiv 2409.13082](https://arxiv.org/abs/2409.13082) |
| Clover (Dafny) | consistency across code, docstring and formal spec; up to 87% acceptance of correct samples, zero false accepts on CloverBench (intro-level) | [arXiv 2310.17807](https://arxiv.org/abs/2310.17807) |
| Verina (189 Lean tasks) | o3: code 72.6%, spec soundness/completeness 52.3%, proof 4.9% | [arXiv 2505.23135](https://arxiv.org/abs/2505.23135) |
| Vericoding (12,504 specs) | off-the-shelf LLMs: Dafny 82%, Verus 44%, Lean 27%; Dafny rose from 68% to 96% in a year; natural-language descriptions did not help | [arXiv 2509.22908](https://arxiv.org/abs/2509.22908) |

Reading:
- Verified generation works well where the automation is strong (Dafny SMT-backed) and poorly where proofs are manual (Lean).
- Specifications are the weak link: spec generation at 52.3% means a wrong law can be proven perfectly. Clover's three-way consistency check (code, doc, spec) is the applicable pattern: the graph should link and check all three.
- A proof about a model is not a proof about the code. Conformance is a separate claim (rule 5).

Bend ([bendlang/bend](https://github.com/bendlang/bend), Apache-2.0, pushed 2026-09-28; local checkout read): the README's `LAWS.bend` plus `PROOF.bend` design has the compiler demand a proof whenever code changes, so an agent must retry until laws hold. Its speed and checker-benchmark claims are self-reported targets ("Status" labels); the README itself says "We don't have as many benchmarks as we'd like yet, especially for the checker". I found no independent evaluation of agent success with LAWS.bend. Verdict: keep in the formal lane as an optional process; do not build on its performance claims.

**What it gives EIJA:** the graph should represent a law/spec node with a link to its proof artefact and a link to the code it is claimed to conform to, and show conformance as its own edge with its own status (`NOT_RUN`, `MODEL_ONLY`, `CONFORMANCE_TESTED`). Verdict: adopt the link discipline; make proofs a non-blocking assurance level except for the narrow laws where an SMT-backed tool is stable.

### 2.7 Determinism levers and reliability metrics

| Finding | Source |
|---|---|
| Qwen3-235B at temperature 0, 1000 identical requests gave 80 unique completions; first divergence at token 103. Cause: lack of batch invariance (server load changes batch size). Batch-invariant kernels fix it at a cost (26 s default vs 42 to 55 s in their test; MEASUREMENT by the vendor, on vLLM) | [Thinking Machines](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/) |
| Five LLMs, eight tasks, ten runs: accuracy varied up to 15% across runs, best-to-worst gaps up to 70 points; no model consistent on all tasks | [arXiv 2408.04667](https://arxiv.org/abs/2408.04667) |
| Anthropic's consistency guidance: use Structured Outputs for guaranteed schema conformance; prefill is not supported on Claude 4.6 and later | [Anthropic docs](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/increase-consistency) |
| tau-bench: pass^k = E over tasks of C(c,k)/C(n,k), the probability all k trials succeed (c successes in n trials). GPT-4o function-calling agent above 60% average success on retail; pass^8 below 25%. Failure classes included domain rule-following (removing the policy document dropped airline success by 22.4%) | [arXiv 2406.12045](https://arxiv.org/abs/2406.12045), [HTML](https://arxiv.org/html/2406.12045) (fetch summary for the formula and ablation) |
| tau-bench repository is MIT and superseded by newer tau2/tau3 repositories; use those for current tasks | [tau-bench](https://github.com/sierra-research/tau-bench), [tau2-bench](https://github.com/sierra-research/tau2-bench) |
| VCR.py records HTTP interactions as cassettes and replays them offline (MIT, pushed 2026-09-15) | [vcrpy](https://github.com/kevin1024/vcrpy) |

Reading: temperature and seed are not a determinism guarantee for hosted models. Reproducibility must come from recording (content-addressed transcript of prompt, tool results and output) and replaying at the adapter boundary. EIJA's providers are CLI agents, so an HTTP cassette library does not sit at the right boundary; a transcript record keyed by hash does. Verdict: adapt (VCR's idea, EIJA's format).

Metrics rule for the metrics lane: report n, c, pass@1 and pass^k for k up to n, per task class; state that a small n gives a wide interval (arithmetic, not a citation); label results MEASUREMENT with the model id, CLI version and date, and label anything extrapolated PREDICTION.

### 2.8 Human comprehension and review

| Source | What is verified | What is not |
|---|---|---|
| Bird and Bacchelli, "Expectations, outcomes, and challenges of modern code review", ICSE 2013 ([MSR page](https://www.microsoft.com/en-us/research/publication/expectations-outcomes-and-challenges-of-modern-code-review/)) | Observation, interviews and surveys at Microsoft. Finding defects is the main motivation but reviews also transfer knowledge and awareness; "code and change understanding is the key aspect of code reviewing"; tools support understanding poorly | Generalisation beyond that setting |
| Brooks, "Towards a Theory of the Comprehension of Computer Programs", Int. J. Man-Machine Studies, 1983 (record via [Semantic Scholar API](https://api.semanticscholar.org/graph/v1/paper/DOI:10.1016/S0020-7373(83)80031-5?fields=title,year,venue,authors,abstract)) | Bibliographic record only | Content: abstract withheld, paper not opened. I do not build on its claims |
| Storey, "Theories, tools and research methods in program comprehension: past, present and future", Software Quality Journal, 2006 (record via [Semantic Scholar API](https://api.semanticscholar.org/graph/v1/paper/DOI:10.1007/s11219-006-9216-4?fields=title,year,venue,authors,abstract)) | Bibliographic record only | Content: not opened. Not built on |
| METR RCT: 16 experienced open-source developers, 246 tasks, early-2025 AI tools; developers took 19% longer while expecting a speedup ([arXiv 2507.09089](https://arxiv.org/abs/2507.09089)) | The figure and the sample size | Small n, one setting, tools of that date; do not extrapolate to current agents |

Reading: the only verified human-side result relevant here is that understanding the change is the central difficulty of review. Everything about how a graph would improve that understanding is a hypothesis (section 6). The comprehension literature (Brooks, Storey) is the right place to ground the hypothesis, but I could not read it this session.

## 3. Options table

Verdict vocabulary: dependency, optional process (separate process, output consumed as data), export target, inspiration, reject.

| Name | Licence (source) | Status 2026-09-29 | Verdict | Why | Source |
|---|---|---|---|---|---|
| MCP spec and SDKs | Apache-2.0 for new contributions, MIT legacy, CC-BY-4.0 docs (LICENSE text read) | active; repo schema dated 2026-07-28 while I read the 2025-11-25 tools page | dependency (agents lane) | outputSchema/structuredContent fit typed graph queries; pin the spec version | [spec](https://modelcontextprotocol.io/specification/2025-11-25), [LICENSE](https://raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/main/LICENSE) |
| SWE-agent | MIT | active; maintainers say mini-swe-agent has superseded it | inspiration | ACI ablations; harness for optional benchmarking | [repo](https://github.com/SWE-agent/SWE-agent) |
| mini-swe-agent | MIT | active, pushed 2026-09-21 | optional process | candidate baseline runner (not evaluated) | [repo](https://github.com/SWE-agent/mini-swe-agent) |
| Aider | Apache-2.0 | active but last push 2026-05-22 | inspiration | repo-map algorithm; do not vendor | [repo](https://github.com/Aider-AI/aider) |
| RepoGraph | Apache-2.0 | last push 2025-04-01 | inspiration | k-hop ego-graph retrieval | [repo](https://github.com/ozyyshr/RepoGraph) |
| CodexGraph (ms-agent) | Apache-2.0 | active repo; component UNVERIFIED | inspiration | shows graph-DB retrieval works but costs tokens | [arXiv](https://arxiv.org/abs/2408.03910) |
| Agentless | MIT | stale (2024-12-22) | inspiration | fixed pipeline localise/repair/validate matches "kernel decides" | [repo](https://github.com/OpenAutoCoder/Agentless) |
| Neo4j Community | GPLv3, with commercial supersession clause (LICENSE.txt read) | active | optional process, export target only | copyleft: never link into an Apache-2.0 package; graph fits in memory (my estimate, see section 8) | [LICENSE](https://raw.githubusercontent.com/neo4j/neo4j/dev/LICENSE.txt) |
| Kuzu | MIT | archived 2025-10-10 | reject | no maintenance | [repo](https://github.com/kuzudb/kuzu) |
| tree-sitter | MIT | active | dependency (optional extra) | multi-language symbol extraction; Python `ast` suffices for Python | [repo](https://github.com/tree-sitter/tree-sitter) |
| SCIP | Apache-2.0 | active (scip-code/scip) | export target | code-intelligence index interchange | [repo](https://github.com/sourcegraph/scip) |
| Outlines | Apache-2.0 | active | inspiration, export target | JSON Schema contract; EIJA cannot embed a decoder | [repo](https://github.com/dottxt-ai/outlines) |
| XGrammar | Apache-2.0 | active | inspiration | grammar engine research | [repo](https://github.com/mlc-ai/xgrammar) |
| llguidance | MIT | active | inspiration | same | [repo](https://github.com/guidance-ai/llguidance) |
| spec-kit | MIT | active | export target | emit spec-kit-shaped files from graph nodes | [repo](https://github.com/github/spec-kit) |
| Kiro | proprietary | active | inspiration | closed product; claims are vendor's | [kiro.dev](https://kiro.dev/) |
| tau-bench / tau2-bench | MIT | tau-bench superseded | inspiration | adopt the pass^k metric definition; harness optional | [arXiv](https://arxiv.org/abs/2406.12045) |
| OpenFastTrace | GPL-3.0 (GitHub API license record; LICENSE text opened via API, v3) | active, release 4.10.0 | optional process only | JVM tool; run as a separate process and read its report; never import | [repo](https://github.com/itsallcode/openfasttrace) |
| Dafny | MIT plus separate third-party notices (GitHub reports NOASSERTION) | active | optional process | formal lane | [repo](https://github.com/dafny-lang/dafny) |
| Verus | MIT (LICENSE text read) | active, under active development per README | optional process | formal lane | [repo](https://github.com/verus-lang/verus) |
| Lean 4 | Apache-2.0 | active | optional process | formal lane | [repo](https://github.com/leanprover/lean4) |
| Bend | Apache-2.0 (LICENSE header read) | active | optional process | laws-and-proofs; claims self-reported | [repo](https://github.com/bendlang/bend) |
| Soufflé | UPL-1.0 (licence text not opened) | active, pushed 2026-07-13 | optional process | Datalog rules with provenance; C++ toolchain cost | [repo](https://github.com/souffle-lang/souffle) |
| Salsa | Apache-2.0 or MIT | active | inspiration | incremental query model (Rust) | [repo](https://github.com/salsa-rs/salsa) |
| VCR.py | MIT | active | inspiration | record/replay idea; wrong boundary for CLI agents | [repo](https://github.com/kevin1024/vcrpy) |
| OKF v0.2 | Apache-2.0 repo record (GitHub API) | active | dependency on the format (okf lane) | markdown plus YAML; links untyped; consumers must not reject broken links | [SPEC](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) |
| RFC 8785 (JCS) | IETF RFC, Informational, independent stream | fixed | adopt or adapt | canonical JSON for hashing | [RFC](https://datatracker.ietf.org/doc/html/rfc8785) |

## 4. Mechanisms table (maths and CS ideas that earn a place)

| School | Mechanism | Benefit (evidence class) | Cost | Verdict | Source |
|---|---|---|---|---|---|
| Order theory / fixed points | Impact closure as a least fixed point, cycle-safe, with a budget that returns `complete` and `frontier` | Deterministic blast radius the agent and human can both read; already in `domain/impact.py` (MEASURED: exists in repo) | Only as complete as the encoded edges (`envelope` field already says so) | adopt | `src/eija_studio/domain/impact.py` |
| Graph theory | Personalised PageRank plus a token budget for context selection | Fits context to a budget; used in Aider (mechanism exists; success-rate effect not shown in sources read) | Float iteration must be pinned (tolerance, iteration cap, rounding to fixed decimals, sorted node order, explicit tie-break) or outputs differ across platforms | adapt | [repomap.py](https://raw.githubusercontent.com/Aider-AI/aider/main/aider/repomap.py) |
| Graph theory | k-hop ego-graph retrieval | RepoGraph +2.0 to +2.66 pp on SWE-bench Lite (Python, GPT-4 series) | Hop count is a tuning parameter; more tokens | adopt (as one retrieval mode) | [arXiv 2410.14684](https://arxiv.org/abs/2410.14684) |
| Content-addressed Merkle structures | Node identity is a hash of canonical content; a link stores the target's hash; staleness is a hash mismatch, not a timestamp | Removes stale-evidence bugs; ProofMap's gap register records four such failures (GAP-002, 003, 028, 025: stale reports, timestamp churn, stale changed-path context, reused reports) (MEASUREMENT of the owner's own history) | Hash churn on every edit unless identities separate stable IDs from content hashes; use both | adopt | ProofMap `docs/gap-audit.md` (private repo, read via `gh`) |
| Canonical serialisation | RFC 8785 JCS for anything hashed or signed across platforms | Byte-stable across languages | Existing `canonical()` is not JCS: MEASURED on Python 3.12, `1.0` serialises as `1.0` (JCS: `1`), and key order is by code point, so U+FF5E sorts before U+1F600 while JCS (UTF-16 code units) puts U+1F600 first. Safe today because the kernel only compares its own hashes; unsafe for interop | adapt: for graph IDs use ASCII-only keys and integer-only numbers, or implement JCS; do not change the kernel without an ADR | [RFC 8785](https://datatracker.ietf.org/doc/html/rfc8785) |
| Incremental computation | Memoise each check keyed by the hash of its inputs (build-system style, "early cutoff") | Re-verify only changed subgraph; faster agent loop (mechanism; speed-up not measured here) | Missed dependency means a stale PASS, so the check must declare its inputs and the cache key must include tool versions | adapt | [Build Systems a la Carte](https://www.microsoft.com/en-us/research/publication/build-systems-la-carte/), [Salsa](https://github.com/salsa-rs/salsa) |
| Type theory | Typed node and edge kinds; constrain proposals to existing IDs | Type-constrained decoding halved compile errors (code, not graphs) | Schema growth; provider must support schema-constrained output or validate after the fact | adapt | [arXiv 2504.09246](https://arxiv.org/abs/2504.09246) |
| Datalog | Link rules written as Horn clauses ("every requirement has at least one verifying test") | Declarative, explainable rules; Soufflé has provenance tracking | Extra toolchain; a plain Python rule table would cover the first 10 rules | theory-only for now (revisit at more than about 30 rules) | [Soufflé](https://github.com/souffle-lang/souffle) |
| Provenance semirings | Annotate query results with how they derive from base facts | Could power "why is this red" explanations | Not verified this session (paper record not retrieved) | theory-only, UNVERIFIED | none |
| Probabilistic assurance | pass^k over n recorded trials | Exposes agent inconsistency that pass@1 hides: pass^8 below 25% for a >60% pass@1 agent (tau-bench) | Cost of n runs; small n means wide intervals | adopt (measurement) | [arXiv 2406.12045](https://arxiv.org/abs/2406.12045) |
| Information theory / knapsack | Budgeted selection of context under a token limit | Context rot and lost-in-the-middle make a smaller, better-ordered context worth more than a larger one (directional) | Needs a value function; Aider's is heuristic | adapt (as the PageRank budget above) | [context rot](https://www.trychroma.com/research/context-rot), [arXiv 2307.03172](https://arxiv.org/abs/2307.03172) |
| Category theory, bidirectional transformations, term and graph rewriting | none found linking these to agent success rates in the sources read | none shown | conceptual overhead | theory-only (defer to the other lane dossiers) | n/a |

## 5. What a deterministic, typed, content-addressed graph would and would not change

Supported by evidence (with the bound):
1. **Interface shape.** Typed, bounded, linted tool output helped agents by 3 to 6 pp per feature in SWE-agent's ablations. The graph is a good backing store for such tools. Bound: SWE-bench Lite, one paper.
2. **Retrieval.** Structural retrieval adds about 2 to 3 pp for RepoGraph. Bound: Python, GPT-4-series, Lite only.
3. **Feedback quality.** External precise feedback beats self-critique (Huang; Olausson; DafnyBench). A graph checker is an external, deterministic feedback source.
4. **Reliability reporting.** pass^k reveals fragility that pass@1 hides.
5. **Reproducibility.** Recording is necessary because regeneration is not reproducible.

Plausible but unmeasured (speculation, flagged):
- Fewer wrong-target edits when proposals must name existing node IDs (analogy to type-constrained decoding).
- Smaller prompts and less context rot when the agent holds IDs and pulls detail on demand (analogy to Anthropic guidance; contradicted by CodexGraph's token cost if queries are poorly bounded).
- Faster human review because the graph shows "what changed and what it touches" (Bird and Bacchelli says understanding is the bottleneck; no study shows a graph view fixes it).
- Better outcomes from link-completeness checks that catch what tests miss (PatchDiff shows tests miss things; no study of link checks).

Measured, negative, or cautionary:
- Static overview context did not improve success and raised cost over 20% (AGENTS.md study). Do not ship a big always-loaded graph summary.
- Constraining output format may reduce reasoning (one paper, unrebutted here).
- METR RCT: experienced developers were 19% slower with early-2025 tools. This says that measurement, not assumption, must decide whether the workflow helps.

## 6. Implications for EIJA (concrete)

1. **Agent-facing graph API as MCP tools with `outputSchema`** (agents lane owns the server; weave defines the query set): `node`, `neighbors`, `impact`, `context(budget)`, `explain(link)`. Every result is bounded, sorted, includes `complete` and `frontier`, and carries content hashes.
2. **Write path runs the kernel linter before acceptance** and returns typed diagnostics (rule id, node ids, hash of the offending content, suggested next action). This mirrors the linter-on-edit ablation.
3. **Dynamic ID enums.** Generate a JSON Schema per session from the live graph so proposals can only reference existing node IDs; validate on receipt regardless of whether the provider enforces the schema. Ask for reasoning first, then the structured block.
4. **Record-and-replay transcript** per agent run: prompt hash, tool calls and results, output, model id, CLI version. Key by hash. Replays must be byte-identical; live regeneration is never assumed to be.
5. **Reliability harness**: n trials per task, report pass^k, label MEASUREMENT with model and date. Kernel checks themselves must be byte-deterministic across Windows and POSIX (rule 4).
6. **Canonicalisation decision**: use ASCII-only identifiers and integer-only numbers in graph documents, or adopt RFC 8785 exactly; record the choice in an ADR and add a cross-platform golden-hash test. Do not modify `src/` without its own ADR.
7. **Incremental checks with early cutoff**: cache key = hash of declared inputs plus tool versions; a missing declaration is a NOT_RUN, not a PASS.
8. **Three-way consistency as the core lint** (Clover pattern): code, spec/law and prose/diagram nodes must agree by link; conformance of code to a proof or model is a separate edge with its own status.
9. **Proof policy**: proofs are advisory unless the tool is SMT-backed and pinned; the law/spec text gets human review because spec quality is the weak point (Verina).
10. **Human-facing evidence**: before claiming the graph helps people, add a small hci-lane study (task time and error in "find what this change affects", with and without the graph view). Until then, label the human benefit PREDICTION.

## 7. ProofMap Lite lessons (owner's repo, private, read via `gh`)

- Pipeline: draw.io map, semantic graph, change bundle, Codex prompt, OpenFastTrace spec, proof report. OpenFastTrace is GPL-3.0, so keeping it an external process is the right call.
- The 46+ item gap register shows the failure modes of a file-based traceability loop: stale generated artefacts, timestamp churn, drift closed by prose only (GAP-029, fixed by requiring warning ids in the change bundle), install contract wording drifting across surfaces (GAP-012). These are the deterministic-link problems this lane exists to remove. They are a measurement of one repository's history, not a benchmark.

## 8. Gaps and unverified items

- No web search available; coverage limited to sources known in advance. Not covered: independent evaluations of spec-driven development; SWE-bench Verified/Pro methodology; Anthropic and OpenAI model-specific determinism documentation; rebuttals to the format-restriction paper; Lean-based agent frameworks.
- Brooks 1983 and Storey 2006 content, and the provenance-semiring paper: not read. No claim depends on them.
- CodexGraph SWE-bench numbers (summariser output inconsistent) and whether its code still lives in ms-agent.
- AutoCodeRover licence; Soufflé UPL-1.0 text; Dafny's third-party notices.
- Whether Neo4j is needed: my estimate that the EIJA graph fits in memory (thousands to low hundreds of thousands of nodes) is an assumption to be checked by `graph/bench/`, not a citation.
- The 2026-07-28 MCP schema: I read the 2025-11-25 tools page only; check differences before pinning.
- Effect sizes above are from different benchmarks, models and dates and must not be added together.
- No result here shows that a typed graph raises agent success rates or human comprehension. That is the hypothesis this lane should test.
