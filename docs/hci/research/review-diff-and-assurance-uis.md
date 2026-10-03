# Review, diff and assurance UIs: what to copy, what to avoid

Dossier: review-assurance-ui. Author lane: lane/ux-research. Access date for every URL: 2026-09-29.
Status: research input for HCI-ADRs (block 0057-0088). Nothing here is a measurement of EIJA users. Statements marked PREDICTION or HYPOTHESIS are untested.

## Decisions first

| # | Finding | Verdict for EIJA |
|---|---------|------------------|
| 1 | Two mainstream products count "no result" as success: GitHub reports a skipped required check as success, and Codecov defaults `if_not_found` to success. | Avoid. UNKNOWN and NOT RUN must never roll up into PASS. |
| 2 | Tools that report bounded checks put the bound in the result (Quint `--max-steps` default 10, Alloy default scope 3, Quint simulator prints sample count and seed). | Adopt. Every verdict carries its bound and its declared domain. |
| 3 | The best-verified "covers X, not Y" patterns are per-obligation counts with an explicit "justified/assumed" column (GNATprove) and a dependency listing (Lean `#print axioms`). | Adapt into a four-slot coverage row (section 9). |
| 4 | Trace viewers that default to "changed variables only" plus a user-defined expression column (TLA+ Toolbox) reduce what a reader scans per state. | Adopt for counterexamples. |
| 5 | Semantic diff tools hide edits and say they cannot guarantee the hidden edits are irrelevant (SemanticDiff FAQ). | Adapt: hide only what the kernel can show is null, and always show a count of hidden edits. |
| 6 | Copilot review can be configured to submit approving reviews (public preview, off by default). | Avoid for EIJA: providers never approve. |

## 1. Scope and method

- Tools used: WebSearch (US-only) to locate pages, then WebFetch to open them. WebFetch returns a model-written summary of each page, not raw text; two PDFs (Google and Microsoft code-review papers) were downloaded and read as text.
- About 45 queries and page opens. Full list of opened URLs is in section 13. Search-snippet-only items are labelled "snippet" in the source column and were not built upon unless marked medium.
- Blocked or empty: Springer (Baum et al.) and SAGE returned 403/redirect; Applitools test-results page 404; Chromatic UI-review page 404; GSN standard download page gave no text; the vscode-tlaplus wiki pages returned only navigation. These are listed as unverified in section 12.
- Laws: this dossier links patterns to principles (recognition over recall, response-time limits, redundant coding, automation complacency, cognitive load). Fitts and Hick-Hyman parameters are owned by the layout-laws dossier and are not re-verified here.
- No screenshots or proprietary assets were copied. Quotes are at most a few words.

## 2. Code-review surfaces

What they are today: PR review in GitHub (with Copilot review), Gerrit, Reviewable, Graphite stacks, CodeRabbit.

| Pattern | Why it works (principle) | Source |
|---|---|---|
| Per-file "Viewed" checkbox that collapses the file, plus a header progress bar of files viewed | Externalises memory of what has been read (recognition over recall); makes remaining work visible | GitHub Docs, reviewing proposed changes |
| Reviewable keeps "reviewed" marks per file revision and shows the net delta since your last review | Re-review cost proportional to the change, not the whole diff | Reviewable docs |
| Gerrit attention set: a chevron marks whose turn it is; everyone else can ignore the change | Removes monitoring load; a single explicit "next actor" | Gerrit attention-set docs |
| Gerrit submit requirements: six statuses (SATISFIED, UNSATISFIED, NOT_APPLICABLE, OVERRIDDEN, ERROR, FORCED), each with an inspectable expression | Distinguishes "does not apply" and "bypassed" from "passed"; the rule is visible on hover | Gerrit submit-requirements docs, user-review-ui docs |
| Gerrit inline comments with Done / Ack resolution and diff between patch sets | Comment lifecycle is explicit, not implied by a code change | Gerrit user-review-ui docs |
| CodeRabbit walkthrough: grouped change table (one source file plus 27 localisation files become two rows), optional sequence diagram, review-effort score 1 to 5, severity and category badges | Chunking and a pre-read summary reduce comprehension cost; but the summary is AI-authored | CodeRabbit walkthrough docs, code-review overview |
| Copilot review: default review type is Comment; comments tagged High/Medium/Low; docs state it is not guaranteed to spot all problems and to supplement with human review | Honest authority boundary in the default; severity aids triage | GitHub Docs, Copilot code review (two pages) |
| Graphite stack view; reviewers work bottom-up; orange marker flags changes further up the stack; teams flag PRs over 250 lines or 25 files | Smaller units limit working-memory load; ordering follows dependency, not the alphabet | Graphite best-practices docs |

Evidence about review load (peer-reviewed or primary):

- Understanding the change is the main challenge; only 14% (78) of sampled Microsoft review comments concerned defects (Bacchelli and Bird, ICSE 2013).
- Google (9 million reviewed changes): median 24 lines changed; over 80% of changes need at most one iteration of resolving comments; under 25% have more than one reviewer; median review latency under 4 hours. Analysis warnings carry "Please fix" and "Not useful" buttons; analyzers with high "Not useful" rates are fixed or disabled, which the authors call critical for developer trust (Sadowski et al., ICSE-SEIP 2018).
- Alphabetical file order: 10.2% of 1,355 surveyed developers think it optimal; 63.9% worry it makes them miss bugs; 66% want customisable order and dependency-aware grouping (survey, accepted at ICSE 2026; self-report, not detection data).
- Decomposing a composite change (controlled experiment, 28 participants): fewer false positives, more context-seeking; no gain in defects found or in rationale comprehension.

Verdicts:

- Adopt: Viewed-with-progress; persistence of reviewed marks across revisions (invalidate when the meaning hash changes); attention set (the three actors are AI, kernel, owner); Gerrit's non-collapsing status set; inspectable rule behind each status; Google-style "Not useful" feedback on AI suggestions.
- Adapt: CodeRabbit's grouped summary, but generate the grouping from the semantic transaction, not from a model; label any AI-authored summary as such.
- Avoid: alphabetical default order; AI review that can satisfy required-approval rules; AI-estimated "effort" or "severity" shown without a label naming the estimator.

## 3. Visual-diff services

What they are today: Chromatic (Storybook), Percy (BrowserStack), Applitools Eyes.

| Pattern | Why it works | Source |
|---|---|---|
| Baseline is the merge base, and an accepted snapshot needs no re-acceptance until it changes | Review effort tied to change, not repetition | Chromatic docs (review) |
| Review is Pending until a checklist of three tasks (changeset approved, threads resolved, reviewers approved) completes, then Passed | Pending is a first-class state; done requires explicit acts | Chromatic docs (review) |
| Percy states: Unreviewed, Approved, Changes requested; one Changes-requested snapshot changes the build status; per a search snippet, requested changes carry forward only while the diff matches the original | Worst-status-wins roll-up; carry-forward tied to the diff still matching (snippet) | BrowserStack Percy basics, Visual Reviews 2.0 |
| Side-by-side and overlay modes, a diff-highlight toggle (Chromatic: neon green; Percy: purple underline on the width/browser that changed), single-key shortcuts (D diff, A approve, arrows to move) | Recognition over recall; low interaction cost per item | Chromatic docs, Percy Visual Reviews 2.0 |
| Applitools match levels per checkpoint or region: Strict, Layout, Ignore Colors, Dynamic, Exact, None; regions can be ignore or floating | The review question is declared in advance ("what counts as a difference"); a tolerance is a visible setting | Applitools match-levels docs |

Caveat: an Applitools match level is a way to decide a change does not matter. The setting must stay visible next to the verdict, or a tolerance becomes a hidden rounding-up.

Verdicts: Adopt worst-status-wins roll-up, approvals bound to the exact diff and per-item keyboard approve (approve stays an owner-only action; never a provider action). Adapt match levels into a visible "what counts as changed" policy on each semantic diff. Avoid treating "unchanged" as evidence when the check did not run.

## 4. Quality gates and coverage

What they are today: SonarQube quality gate; Codecov statuses and PR comment.

| Pattern | Why it works | Source |
|---|---|---|
| Gate has two states, Passed or Failed; on PRs only new-code conditions apply | Clear boundary; reviewer attention is on what the change touched | SonarQube quality-gate docs |
| Sonar way defaults: new-code coverage at least 80.0%, duplication at most 3.0%, no new issues, security hotspots reviewed; coverage and duplication conditions are ignored under 20 new lines | Threshold is inspectable; but small changes escape the check by design | SonarQube quality-gate docs |
| Codecov separates project and patch status; patch measures only lines changed in the PR | Same "new code" focus | Codecov commit-status docs |
| Codecov `if_not_found` defaults to success; `informational: true` passes regardless of coverage | Convenience default, but it turns missing evidence into a green tick | Codecov commit-status docs |

Verdicts: Adopt new-code focus. Avoid two-state gates and any default that maps missing data to success. Adapt the 20-line exemption idea only as an explicit NOT APPLICABLE state, never as silent success.

## 5. Traces and counterexamples

What they are today: TLA+ Toolbox and VS Code extension, Quint (simulator and Apalache), Alloy Analyzer, Hypothesis.

| Pattern | Why it works | Source |
|---|---|---|
| TLA+ Toolbox error trace: one expandable row per state; values that changed are colour-highlighted; filters for "all variables", "only changed", "changed within a frame"; alt-click hides a variable; double-click jumps to the spec action | Reduces per-state scan to the delta; link to source supports causal reading | Toolbox docs (executing TLC), Learn TLA+ |
| Trace Explorer: user-typed expressions (primed and unprimed variables) evaluated at every state and shown as extra values | Lets the reader ask "why" without leaving the trace (direct manipulation of the question) | Toolbox docs |
| VS Code TLA+ extension changelog: mark value changes between states (0.2.0), hide unmodified variables (1.1.0), filter by variable name (1.2.0), copy values (1.3.0), switch between multiple traces (1.4.0) | Same delta pattern in an editor; iterative feature growth shows the demand | vscode-tlaplus CHANGELOG |
| Quint simulator prints "[violation]", the example execution, a seed, and sample count; "OK" means no violation found in explored runs and "there might still be an issue"; docs say a model checker's counterexample is minimal, the simulator's is not | Verdict wording is calibrated; reproducibility is one copyable token | Quint simulator docs, model-checkers docs |
| Apalache (in Quint) is bounded: `--max-steps` defaults to 10; "verified" is always for a bound | Bound is a parameter the user sees | Quint model-checkers docs |
| Alloy: every model is bounded by scope (default 3 per top-level signature); `check` finds counterexamples; no counterexample means the assertion holds within scope; visualiser offers graph, text, tree and table views, projections that turn relations into labels, an evaluator, and (Alloy 6) side-by-side current and next state | Multiple representations of one instance; the bound is part of the command | Alloy docs: commands, visualizer |
| Hypothesis shrinks a failure to a minimal example, prints notes, saves it to a database for replay; explain mode annotates which parts can vary ("or any other generated value"); reproduce blobs are not stable across versions | Minimal case lowers reading cost; explicit statement that lack of explanation is not evidence | Hypothesis docs (settings, replaying failures), hypothesis.works article on shrinking |
| Practitioner note: a full state graph becomes a "hairball" on real specs; HTML export of a trace helps sharing | Full graphs exceed working memory; sharing needs a link, not an app | Davis, emptysqua.re (blog, 2021) |

Verdicts:

- Adopt: changed-only default, expression column, jump-to-action link, minimal-counterexample labelling ("minimal" vs "not minimised"), seed or replay token, bound inside the verdict text.
- Adapt: Alloy's view switch (graph, table, text) for the EIJA journey and state models, always generated from the model.
- Avoid: whole-state-space graphs as a default view; "no violation" without the bound.

## 6. Proof states, verification status, mutation

What they are today: Lean 4 infoview, Rocq (Coq), Dafny IDE, Frama-C GUI, SPARK GNATprove, Stryker mutation reports.

| Pattern | Why it works | Source |
|---|---|---|
| Lean infoview shows the goal at the cursor with hypotheses above a turnstile; squiggles are red (error), orange (warning), blue (info); an orange scroll-bar progress marker shows unprocessed regions; gutter shows a double check for a finished theorem | The unfinished region is visible where you scroll; done is a distinct mark | Lean 4 VS Code manual |
| Lean `#print axioms` lists every axiom a theorem depends on; `sorryAx` marks an unfinished proof; three standard axioms are expected | A claim ships with its assumptions; "proved modulo X" is queryable | Lean reference (Axioms) |
| Rocq `Print Assumptions` lists axioms and parameters a theorem relies on; `Admitted` turns a proof into an axiom | Same idea; snippet only, primary page not confirmed | search snippet (Rocq refman, ANSSI doc); see section 12 |
| Dafny gutter: thin green bar for verified ("visible but least distracting"), wider red rectangle for errors, yellow bars around the error context, circle-check for partially proved assertions, animated zig-zag while verifying with previous results still shown, dimmed icons when stale, grey with red triangles for parse errors; shapes chosen for colour-blind users | Quiet success, loud failure; stale and in-progress are distinct states; redundant shape coding | Dafny blog (2023-04) |
| Dafny reference: `{:verify false}`, `assume`, `{:timeLimit}`, `{:resource_limit}` exist; running out of resources is an "unknown" outcome distinct from a failed proof | Skips and limits are language-level, so they can be listed | Dafny Reference Manual |
| Frama-C GUI: green marker when a plug-in proved a property, yellow when a proof was attempted and failed; statuses include valid, invalid, unknown, no proof attempted | Attempted-and-failed differs from not-attempted | Frama-C GUI page |
| GNATprove summary: columns Total, Flow, Provers, Justified, Unproved; Unproved means neither proved nor justified; messages graded low/medium/high; distinguishes "reached time and step limit" from "gave up" | Justification is a separate column, so assumed is never counted as proved | SPARK User's Guide |
| Stryker mutant states: Pending, Killed, Survived, No coverage, Timeout, Runtime error, Compile error, Ignored. Score = detected / valid; a second score = detected / covered | Two denominators are published; No coverage is its own state | Stryker docs |

Verdicts: Adopt Dafny's quiet-success, stale and in-progress states; GNATprove's separate Justified column; Stryker's two-denominator score with No coverage visible; Lean's dependency listing. Avoid one merged "coverage %" number.

## 7. Semantic diff

What they are today: SemanticDiff (VS Code and GitHub app), difftastic (CLI), GumTree (research).

| Pattern | Why it works | Source |
|---|---|---|
| Parse both versions to ASTs, match nodes, hide whitespace, optional commas and redundant parentheses; recognises that reordered keyword arguments are equal in Python | Removes non-semantic noise, lowering the number of items to inspect | SemanticDiff docs and home |
| Moved code drawn with a border on old and new location (colour per move); refactoring labels; minimap; middle bar linking versions | Identity of a moved block is preserved visually (proximity, common region) | SemanticDiff docs |
| Documented limit: cannot guarantee hidden changes are irrelevant in all contexts; unsupported languages fall back to line diff | Honest limit; the user is told it hides things | SemanticDiff docs |
| difftastic: structural diff via tree-sitter, shortest-path search over a graph of syntax-node matches, shows real line numbers before and after | Diff is a search for the cheapest explanation of the change | difftastic docs |
| Comparison write-up (vendor): difftastic lacks moved-code detection and mishandles Python indentation changes; SemanticDiff supports fewer languages and has no inline view | Shows where syntax-only diffs fail; vendor source, treat as medium | SemanticDiff blog |
| GumTree: edit script at AST granularity including move actions; two phases (top-down isomorphic subtrees, bottom-up node matching) | Peer-reviewed basis for move detection | Falleri et al., ASE 2014 (snippet only) |

Verdict: Adapt. EIJA's model has typed operations (a semantic transaction), so the diff can be exact: list operations, not inferred hunks. Where a text or code diff is shown, use the "N hidden" affordance and a border-per-move convention. Avoid inferring meaning with a model.

## 8. Impact and dependency overlays

What they are today: Nx graph, Backstage catalog, Sourcegraph code navigation.

| Pattern | Why it works | Source |
|---|---|---|
| Nx affected = git diff, then files-to-projects mapping, then dependency traversal; a lock-file change marks every project affected as a "failsafe"; docs admit that touching a widely used project can affect almost everything | Conservative over-approximation; safe direction of error | Nx affected docs |
| Nx graph: focus on a node, search, group by folder, proximity controls, click an edge to see the files that create it, export JSON | Progressive disclosure of a large graph; edge provenance | Nx explore-graph docs |
| Backstage typed relations (ownedBy, dependsOn, partOf, providesApi, consumesApi), each with an automatic inverse | Typed edges let the UI answer "who is affected" and "who owns it" | Backstage well-known-relations docs |
| Sourcegraph uses precise (index-based) navigation when available and falls back to search-based | Two confidence tiers; the docs do not say how the UI labels the tier (unverified) | Sourcegraph docs |

Verdicts: Adopt Nx's edge provenance and focus controls, with "affected" defined by the executable model. Adapt confidence tiers: each impact edge is labelled kernel-derived, heuristic, or unknown. Avoid fading unaffected nodes, which implies proven safe; show "not analysed" distinctly from "analysed, unaffected".

## 9. Cross-cutting: trust, status taxonomy, colour, "covers X but not Y"

Trust signals with evidence:

- Automation complacency and bias arise under multitask load, affect expert and naive users, and are not removed by simple practice or instructions (Parasuraman and Manzey 2010, abstract via PubMed E-utilities). Design implication (inference, not a finding): prose warnings alone are unlikely to fix over-reliance, so the interface should make unknowns structurally visible.
- Appropriate reliance requires calibrated trust; trust guides reliance when full understanding is impractical (Lee and See 2004, abstract).
- Google found the "Not useful" feedback loop critical to trust in automated analysis (Sadowski et al. 2018).
- Response time: 0.1 s feels instant, 1 s keeps flow, 10 s is the limit for attention; slower work needs a progress indicator and a way to cancel (Nielsen, NN/g). Validity: these are perceptual thresholds from interactive work, not proof-check durations.

Status taxonomies seen (count of distinct states shown to users):

| Tool | States | Note |
|---|---|---|
| Gerrit submit requirement | 6 | separates NOT_APPLICABLE, OVERRIDDEN, FORCED from SATISFIED |
| GitHub check conclusion | 8 plus stale (startup_failure is suites only) | success, failure, neutral, cancelled, skipped, timed_out, action_required, startup_failure (suites); skipped required check counts as success |
| Stryker mutant | 8 | No coverage and Timeout are distinct from Survived |
| Percy snapshot | 3 | Unreviewed / Approved / Changes requested |
| SonarQube gate | 2 | Passed / Failed |
| Frama-C | 4 or more | valid, invalid, unknown, no proof attempted |

Colour use: green for good and red for bad is universal in these tools but is never sufficient. WCAG 1.4.1 requires that colour not be the only visual means of conveying information; Dafny chose distinct shapes, and Lean uses icons plus underline colour. No product page opened here states a colour-vision test for its palette (unverified).

What is the best-known way to show "this proof covers X but not Y" to a busy engineer? No single verified best-known pattern exists in the sources opened. The strongest components are:

1. Count table with a Justified/assumed column and an Unproved column (GNATprove).
2. Dependency listing of assumptions per claim (Lean `#print axioms`).
3. The bound printed with the verdict (Quint max-steps, Alloy scope, simulator samples and seed).
4. Two denominators, with the uncovered part named (Stryker).
5. Inline marks at the object itself, quiet for done, loud for not (Dafny).
6. Undeveloped-goal diamond in assurance cases (GSN; secondary sources only).

Proposed EIJA composite (design proposal, untested): one row per claim with four slots: `claim | covered domain (with count, e.g. 125 of 125 declared cells) | assumed | NOT covered`. The last slot is never empty; if nothing is known, it says UNKNOWN. HYPOTHESIS H1: showing the fourth slot reduces owner approvals that overlook unknowns compared with the current baseline; requires a user study (protocol owned by the study-design dossier).

## 10. Quantitative facts

| Fact | Source | Confidence |
|---|---|---|
| Google review: median 24 lines changed; over 10% of changes touch one line; about 90% modify fewer than 10 files | Sadowski et al. 2018 (PDF read) | high |
| Google: over 80% of changes need at most one comment-resolution iteration; fewer than 25% have more than one reviewer; median latency under 4 hours | same | high |
| Google: comments per change peak at 12.5 for changes of about 1,250 lines | same | high |
| Microsoft sample: defect comments 78 (14%); understanding the change is the key challenge | Bacchelli and Bird 2013 (PDF read) | high |
| File-order survey: 1,355 developers, 182 projects; 10.2% find alphabetical optimal; 63.9% fear missed bugs; 66% want custom order or dependency grouping | arXiv 2609.04207 (accepted ICSE 2026) | medium (self-report) |
| Change-decomposition experiment: 28 participants; fewer false positives; no more defects found | arXiv 1805.10978 | medium (small sample) |
| GitHub: a skipped required check reports success and does not block merge | GitHub Docs, about status checks | high |
| GitHub: check conclusions listed; `stale` assigned after 14+ days incomplete | GitHub REST checks guide | high |
| Codecov: `if_not_found` default success | Codecov commit-status docs | high |
| SonarQube Sonar way: coverage at least 80.0%, duplication at most 3.0% on new code; ignored under 20 new lines | SonarQube docs | high |
| Gerrit submit requirements: 6 statuses | Gerrit docs | high |
| Stryker: 8 mutant states; score = detected / valid; alternative = detected / covered | Stryker docs | high |
| Quint/Apalache: `--max-steps` default 10 | Quint docs | high |
| Alloy default scope: up to 3 per top-level signature | Alloy docs | high |
| Hypothesis defaults: `max_examples` 100, `deadline` 200 ms | Hypothesis API reference | high |
| CodeRabbit review effort scale 1 to 5; severity Critical/Major/Minor/Trivial/Info | CodeRabbit docs | high (as documented) |
| Copilot review comment severity High/Medium/Low; default review type Comment; approvals off by default | GitHub Docs | high |
| Graphite guideline: flag PRs over 250 lines or 25 files | Graphite docs (recommendation, not evidence) | medium |
| Percy Visual Reviews 2.0 targets builds of 10,000+ snapshots | Percy blog (vendor) | medium |
| Response-time limits 0.1 s, 1 s, 10 s | NN/g | high |
| Nx marks all projects affected on a lock-file change | Nx docs | high |

## 11. Implications for EIJA

1. Closed status vocabulary, no roll-up to green. Reuse EIJA's own terms (PASS, PARTIAL, NOT_RUN, UNKNOWN, CONFLICT, BLOCKED, plus STALE). Each has a glyph, a word and a colour. The aggregate shows counts by state ("12 pass, 3 unknown, 1 fail"), never a percentage alone. Any UNKNOWN caps the aggregate at "pass with unknowns". Evidence: GitHub skipped, Codecov default, Stryker, GNATprove.
2. The bound is part of the verdict. Render "PASS on 125 of 125 declared cells" and "no violation within N steps, seed S". This matches ARCHITECTURE.md ("complete declared Cartesian coverage") and Quint and Alloy practice.
3. Coverage row with four slots (claim, covered, assumed, not covered) shown at the object, with a detail view listing assumptions like `#print axioms`. Test it in the study before it becomes a standard.
4. Counterexample view: states as rows, changed variables only by default, expression column, jump from a state to the model action that fired, "minimal" or "not minimised" label, replay token. Show as a table or sequence generated from the model, not a state-space graph.
5. Review by meaning: list semantic operations first, grouped by concept, ordered by dependency, not alphabet. Per-item "Viewed" persists across revisions and clears when the operation's hash changes. A permanent "N formatting-only or null edits hidden" counter reveals them on click.
6. Attention set for three actors. Show whose turn it is: kernel running, owner deciding, AI proposing. The AI is never in a slot that can approve; AI comments carry an "AI-estimated" label on severity and effort. Copilot-style approving reviews are out.
7. Impact overlay with tiers: kernel-derived edge, heuristic edge, unknown. Affected sets are over-approximations by default (Nx failsafe), and "not analysed" is never drawn like "unaffected".
8. Quiet success, loud unknown. Follow Dafny: PASS is the least conspicuous mark; UNKNOWN and CONFLICT must be visible without scrolling. Keep the previous verdict visible but marked STALE while re-checking; give progress after 1 s and a cancel control after 10 s (NN/g limits, perceptual only).
9. Visible tolerance. Any "what counts as changed" policy (Applitools-style match levels) sits beside the verdict it affects.
10. Feedback loop on AI proposals: a "Not useful" action logged per suggestion source, as at Google. Track it as a study measure.

## 12. Gaps and unverified items

- UNVERIFIED (primary source not opened): Rocq `Print Assumptions` and `Admitted` behaviour (snippet only); Lean "declaration uses sorry" warning text (snippet); GSN undeveloped-goal diamond (secondary sources only); Chromatic Accepted and Denied state names (snippet; pages opened name only Pending, Passed); Applitools Unresolved and Failed result states (page 404); Baum et al. working-memory result (paywalled; snippet); Jackson's small-scope hypothesis (snippet).
- UNVERIFIED product behaviour: how Sourcegraph labels precise versus search-based results; Backstage catalog-graph UI; Nx graph affected-node styling; Percy's AI review agent; TLA+ VS Code Trace Explorer UI beyond the changelog; Dafny counterexample display; Reviewable and Graphite visual details (docs summaries only).
- WebFetch summaries are model-written; numeric claims marked high were cross-checked only where the page or PDF text supports them.
- No colour-vision or contrast data found for any product palette. To be produced in the tokens work, with computed contrast.
- No published user-study evidence found that a "covers/does not cover" display improves review decisions. HYPOTHESIS H1 in section 9 needs a study; we do not claim benefit.
- Not covered: Isabelle, Verus, Kani, CBMC, PIT, Semgrep, SARIF viewers, Sonar's UI beyond gates, GitLab and Bitbucket review, and AI-native review products other than CodeRabbit and Copilot.

## 13. URLs opened (access date 2026-09-29)

Review: docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/reviewing-proposed-changes-in-a-pull-request; docs.github.com/en/copilot/using-github-copilot/code-review/using-copilot-code-review; docs.github.com/en/copilot/concepts/agents/code-review; docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks; docs.github.com/en/rest/guides/using-the-rest-api-to-interact-with-checks; gerrit-review.googlesource.com/Documentation/user-review-ui.html, config-submit-requirements.html, user-attention-set.html; docs.reviewable.io; graphite.com/docs/best-practices-for-reviewing-stacks; docs.coderabbit.ai/guides/code-review-overview and /pr-reviews/walkthroughs.

Visual diff: chromatic.com/docs/review and docs.chromatic.com/docs/review; browserstack.com/docs/percy/overview/visual-testing-basics; browserstack.com/blog/introducing-visual-reviews-2-0; applitools.com/docs/eyes/concepts/best-practices/match-levels.

Gates: docs.sonarsource.com/sonarqube-server/quality-standards-administration/managing-quality-gates/introduction-to-quality-gates; docs.codecov.com/docs/commit-status and /pull-request-comments.

Traces and models: learntla.com/topics/toolbox.html; tla.msr-inria.inria.fr/tlatoolbox/doc/model/executing-tlc.html; github.com/tlaplus/vscode-tlaplus and raw CHANGELOG.md; docs.tlapl.us/using:vscode:visualizing_states (DOT only); emptysqua.re/blog/interactive-tla-plus; quint.sh/docs/model-checkers and /docs/simulator; alloy.readthedocs.io/en/latest/tooling/visualizer.html and /language/commands.html; alloytools.org/faq/what_kind_of_analysis_does_the_alloy_analyzer_do.html; hypothesis.readthedocs.io (reference/api, tutorial/replaying-failures); hypothesis.works/articles/how-hypothesis-works.

Proof and verification status: lean-lang.org/doc/reference/latest/Axioms/ and /Tactic-Proofs/; github.com/leanprover/vscode-lean4 manual; dafny.org/blog/2023/04/19/making-verification-compelling-visual-verification-feedback-for-dafny/; dafny.org/latest/DafnyRef/DafnyRef; rocq-prover.org/refman/language/core/assumptions.html; frama-c.com/html/gui.html; docs.adacore.com/spark2014-docs/html/ug/en/source/how_to_view_gnatprove_output.html; stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/.

Semantic diff and impact: difftastic.wilfred.me.uk and /diffing.html; semanticdiff.com, /docs/what-is-semanticdiff/, /blog/semanticdiff-vs-difftastic/; nx.dev/docs/features/explore-graph and /ci-features/affected; backstage.io/docs/features/software-catalog/ and /well-known-relations; sourcegraph.com/docs/code-search/code-navigation/precise_code_navigation.

Papers and standards: sback.it/publications/icse2018seip.pdf (Sadowski et al.); microsoft.com/en-us/research/wp-content/uploads/2016/02/ICSE202013-codereview.pdf (Bacchelli and Bird); arxiv.org/abs/2609.04207; arxiv.org/abs/2605.17548 (vision paper, not evidence); arxiv.org/abs/1805.10978; PubMed abstracts 15151155 (Lee and See) and 21077562 (Parasuraman and Manzey) via NCBI E-utilities; w3.org/WAI/WCAG22/Understanding/use-of-color.html; nngroup.com/articles/response-times-3-important-limits/; modeling-languages.com/goal-structuring-notation-introduction/.
