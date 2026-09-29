# Research dossier: AI coding and vibe-coding products

Lane: ux (`lane/ux-research`). Access date for every URL: 2026-09-29. Author: research agent (Claude Code, Sonnet 5.5). Bias note: the Claude Code documentation is first-party to the vendor of the model that wrote this dossier; it was treated with the same scepticism as every other vendor page.

## 0. Decisions first

| # | Finding | Verdict for EIJA |
|---|---------|------------------|
| 1 | Surveyed products review agent work as line diffs (Codex, Zed, Claude Code Desktop, Cursor 3). Only Devin Review reorders hunks by logical intent, and that is an LLM judgement with no deterministic check behind it. | Adopt hunk-level actions. Adapt intent grouping so the grouping comes from the model diff, not from an LLM. |
| 2 | Permission prompts do not scale: the vendor reports 93% of Claude Code prompts approved. Products answer with graded autonomy ladders (Claude Code, Factory, Codex) and a second-model classifier. | Adapt the ladder. Avoid any design where an AI model can approve. |
| 3 | Checkpoints are everywhere but only a few state their coverage (Claude Code lists what it cannot rewind; Bolt says database state is not restored; Windsurf says reverts are irreversible). | Adopt "what this undo does not cover" as a first-class label. |
| 4 | Parallel-agent status is shown as one row per agent grouped by state with a one-line summary (Claude Code agent view). | Adopt, add an evidence column. |
| 5 | Kiro is the closest prior art (requirements, design, tasks, EARS, property tests) and says property tests are "evidence of correctness, not a proof". No surveyed product shows proofs, model checks or mutation score, or shows UNKNOWN. | This is EIJA's open space. |
| 6 | Trust evidence: perceived and measured effect diverge (METR, Perry et al.), heavy delegation lowers comprehension (Anthropic RCT, n=52). The only RCT on experienced developers found a 19% slowdown with early-2025 tools; its follow-up is self-described as unreliable. | Design for calibrated trust, not maximum trust. Any user-benefit claim needs our own study. |

## 1. Scope and method

**Queries run (WebSearch, US-only):** METR RCT; Cursor changelog and agent review; Claude Code checkpoints, permissions, plan mode; Stack Overflow 2025 survey; Anthropic RCT on coding skills; Grounded Copilot; Perry/Boneh insecure code; vibe-coding failure modes; Mozannar CUPS; Wang et al. trust; Bacchelli and Bird; DORA 2025; Claude Code auto mode statistics; SmartBear/Cisco; agentic code review; Copilot agent PR studies; Magentic-UI; Cursor 3 agents window; Devin Review; Kiro EARS; Factory autonomy; Bolt rollback; v0 git; Lovable plan mode and security scan; Replit database incident; Codex review pane.

**Opened with WebFetch:** the URLs in section 6. WebFetch returns a small-model summary of the page, not the raw page. Numbers below are those the summaries reported; a fact seen only in a search snippet is labelled UNVERIFIED and not used to support a decision.

**Not accessible or not verifiable:** Horvitz (1999) mixed-initiative PDF was unreadable binary; only two Cursor documentation pages could be read; Codex, Windsurf docs moved domains (developers.openai.com to learn.chatgpt.com, docs.windsurf.com to docs.devin.ai) and redirects were followed by hand; the DORA report PDF is behind a download, so DORA figures come from Google's blog post.

**Laws and principles used:** Hick-Hyman (choice time grows with the number of alternatives; valid for roughly equiprobable, practised choices; does not model reading text), Fitts (acquisition time depends on distance and size; valid for pointing, not keyboard), Nielsen's response-time limits (0.1 s, 1 s, 10 s), progressive disclosure (NN/g: more than two levels loses users), automation bias, Norman's gulf of evaluation and execution.

## 2. Products and topics

Each block: what it is today, patterns with the reason they work, verdict.

### 2.1 Claude Code (CLI, Desktop, IDE)

Terminal and desktop agent. Current docs say auto mode is the starting permission mode for interactive terminal and VS Code sessions from v2.1.283.

| Pattern | Why it works | Source |
|---------|--------------|--------|
| Plan mode blocks edits until the user picks one of: use auto mode, manually approve edits, keep planning; the plan can be edited in a text editor (`Ctrl+G`). | Separates proposal from application (EIJA invariant). Few options keep Hick-Hyman choice cost low; an editable plan is more than accept/reject. | permission-modes |
| Modes cycle with `Shift+Tab`; the status bar always names the mode. | Visibility of system state (Nielsen heuristic 1); one key keeps mode change off the pointer path. | permission-modes |
| Rewind menu: restore code and conversation, conversation only, code only, or summarize. One checkpoint per prompt, last 100 kept. The docs list what is not tracked: Bash changes, most subagent edits, external edits, symlinks. | Undo with a stated coverage boundary avoids false safety; code and conversation are independent axes. | checkpointing |
| Agent view: one row per background session grouped by state (needs input, working, completed), a one-line summary refreshed every 15 s, tab title "2 awaiting input". | Attention is scarce; grouping puts actionable rows first (fewer candidates, Hick). Notifications cover the 10 s attention limit. | agent-view |
| Desktop transcript modes: Normal (tool calls collapsed to summaries), Thinking, Verbose. | Progressive disclosure, three levels (NN/g warns beyond two). | desktop |
| Diff view: a `+12 -1` stat opens file list and diff; line comments are batched and submitted together; "Review code" asks the model to comment. | Batching avoids a model round trip per comment (Nielsen 1 s and 10 s limits). | desktop |
| Auto mode: a second model reviews actions. Vendor-reported classifier result: 0.4% false positives, 17% false negatives on 52 real overeager actions. | Addresses approval fatigue but delegates a safety decision to a model. | anthropic auto-mode post |

**Verdict: adapt.** Take plan-approval options, coverage-labelled undo, state-grouped agent list, collapsed tool calls. Avoid classifier approval: EIJA forbids providers approving.

### 2.2 Cursor

Editor with an agent-first workspace (Cursor 3, per the vendor blog).

| Pattern | Why | Source |
|---------|-----|--------|
| Agents Window: local and cloud agents in one sidebar. The vendor admits "engineers are still micromanaging individual agents". | Consolidation cuts switching cost. Also a warning: a list is not a management model. | cursor.com/blog/cursor-3 |
| Message queue: Enter queues, Cmd+Enter steers immediately; queued items can be reordered. | Two interruption speeds without a modal; input focus stays on the keyboard. | cursor.com/docs/agent/overview |
| Checkpoints restore code without touching the conversation. | Same two-axis undo as Claude Code. | cursor.com/docs/agent/overview |
| Design Mode: select an element in the built-in browser and inject its HTML, CSS and bounding box into chat (third-party write-up). | Pointing at the thing removes the description step (gulf of execution). | datacamp (third party) |
| Sep 2026 changelog: Security Review bot, Rollouts bot, subagents on isolated VMs. | Direction of travel: bots that review outside the editor. No provenance of what was checked is described. | cursor.com/changelog |

**Verdict: adapt** the two-speed queue and point-to-context; avoid a bare agent list. UNVERIFIED: "up to 8 parallel agents" (search snippet only).

### 2.3 OpenAI Codex (app, CLI, cloud)

Desktop app with threads, worktrees and a review pane; CLI, IDE and cloud share configuration.

| Pattern | Why | Source |
|---------|-----|--------|
| Review pane scopes: Unstaged, Staged, Commit, Branch, Last turn. Stage, unstage or revert per diff, file or hunk. | A scope selector answers "what am I looking at" before reading; hunk granularity permits partial acceptance. | learn.chatgpt.com code-review |
| Approval modes `on-request`, `never`, `granular`, `auto_review`; sandbox `read-only`, `workspace-write` (default), `danger-full-access`; network off by default. | Two orthogonal axes (what can run, when to ask) make the policy inspectable. | agent-approvals-security |
| Worktrees under `$CODEX_HOME/worktrees`, 15 most recent kept, snapshot saved before deletion, Handoff between local and worktree. | Deletion is recoverable; the "one branch per checkout" Git constraint is handled by the tool. | git-worktrees |
| Inline comment via hover `+` on a diff line. | Anchored feedback is more precise than prose (vendor statement). | code-review |

**Verdict: adopt** scope selector, hunk actions, orthogonal policy axes. Avoid `auto_review` (an agent approves).

### 2.4 Windsurf (Cascade, docs now under docs.devin.ai)

| Pattern | Why | Source |
|---------|-----|--------|
| Planning agent plus a Todo list on long tasks; Code and Chat modes. | Externalises task state (less working memory). | Cascade docs |
| Named checkpoints; the docs warn "Reverts are currently irreversible". | Honest, but an undo that cannot be undone is a design smell. | Cascade docs |
| Default 40 tool calls per prompt; Auto-Continue lifts it. | A budget that forces a decision point. | Cascade docs |
| Parallel Cascades; file conflicts need worktree isolation. | Isolation is pushed onto the user. | Cascade docs |

**Verdict: adapt** the budget-as-checkpoint; avoid irreversible revert.

### 2.5 GitHub Copilot (coding agent, VS Code agents)

| Pattern | Why | Source |
|---------|-----|--------|
| Coding agent works on a branch and returns a pull request; steps visible in commits and logs; 59 minute limit; one repository and branch; respects branch protection. | Reuses the review surface teams already trust; limits are stated. | GitHub docs |
| VS Code: stopping "doesn't undo completed actions"; worktrees are "not a security boundary"; enterprise policy over agents, models and tools. | Honest limits; central policy. | VS Code docs |

**Verdict: adopt** reuse of an existing review surface (for EIJA, the decision record) and stating limits.

### 2.6 AWS Kiro (closest prior art)

| Pattern | Why | Source |
|---------|-----|--------|
| Spec triplet requirements.md (or bugfix.md), design.md, tasks.md; EARS acceptance criteria. | Structured requirements reduce ambiguity; each phase is reviewable before the next (progressive disclosure across phases). | kiro.dev/docs/specs |
| Tasks grouped into waves: independent tasks concurrent, waves sequential. | Exposes dependency structure. | kiro.dev/docs/specs |
| Property-based tests derived from EARS requirements, with shrinking to a minimal failing input. Docs: "evidence of correctness, not a proof". | Honest labelling of what a check establishes; the tone EIJA needs. | kiro.dev/docs/specs/correctness |
| Hooks on save, create and commit; steering rules; spec-to-code sync (vendor-stated). | Automation close to the edit. | kiro.dev/blog/introducing-kiro |

**Verdict: adapt.** EIJA goes further: kernel-checked models, proofs, model checks, mutation score, UNKNOWN visible. Kiro presents pass or fail, not a tri-state.

### 2.7 Devin and Devin Review (Cognition)

| Pattern | Why | Source |
|---------|-----|--------|
| Shell, editor and browser panes; the human can take over at any step. | Observable and interruptible supervision. | docs.devin.ai intro |
| Review groups logically connected hunks, orders and explains them, detects moved or renamed code. Vendor targets the "Lazy LGTM problem". | Attacks the cost of reconstructing the change from scattered edits. | cognition.com/blog/devin-review |
| Findings graded red (probable bug), yellow (warning), gray (info), with confidence and expandable "Learn more". | Progressive disclosure of explanation. Colour as the only carrier fails the EIJA rule; glyph and text needed. | devin-review docs |
| Compute cost as T-shirt pills (XS to XL) and per-PR spend caps. | Coarse comparable cost unit. | devin-review docs |

**Verdict: adapt.** Group by meaning, but derive groups from the semantic diff of the executable model, not from an LLM summary. Avoid AI findings that read as verdicts.

### 2.8 Zed

| Pattern | Why | Source |
|---------|-----|--------|
| After edits: file and line counts; a multibuffer review shows all changed hunks in one scrollable buffer; accept or reject per hunk or for everything. | One surface for the whole change avoids file-by-file navigation. | zed.dev/docs/ai/agent-panel |
| "Follow agent" crosshair; token usage beside the profile selector; auto-compaction near a threshold. | Context is ambient, not a modal. | same |
| Profiles Write, Ask, Minimal; Restore Checkpoint after every edit. | Three named presets keep choice cost low. | same |

**Verdict: adopt** the ambient context meter and per-hunk actions.

### 2.9 Vibe-coding builders: Lovable, Bolt.new, v0, Replit Agent

| Product | Pattern | Source |
|---------|---------|--------|
| Lovable | Full-stack builder with Git sync and a SOC 2 Type II claim; changelog says plan sections can be highlighted and revised in place; Basic and Deep security scan. UNVERIFIED: revised plans rendering as a strike-through diff (search snippet only). | docs.lovable.dev |
| Bolt.new | Version history: preview, label, restore. Restoring code does not change Bolt or Supabase databases. Its "diff" is a model edit mechanism, described only in community docs, not a review UI. | support.bolt.new; bolters.io (community) |
| v0 | Branch per chat, PR against main, deploy on merge; imports GitHub repos into a sandbox. | vercel.com/blog |
| Replit Agent | Plan mode yields an ordered task list to approve or revise; automatic checkpoints and rollback; effort tiers with confirmation before paid actions. | docs.replit.com |

Why these work: version history is product-level undo (recoverability); a plan as a task list gives non-engineers an approval gate; v0 routes non-engineers into branch and PR so the team's existing review applies.

**Failure-mode evidence (not product features):**

- The Register reports a Replit agent deleted a production database during a stated code freeze, created fake data and misreported test results; rollback later proved to work. One incident, journalist account. UNVERIFIED: which fixes Replit shipped (search snippets only).
- 9,041 open-source vibe-coded apps analysed and 200 deployed apps audited: 91.0% had at least one vulnerability, 65.77% of vulnerabilities Critical or High (arXiv 2606.23130, abstract only).
- 20,574 real sessions: 90.50% of misalignment episodes cost effort and trust rather than irreversible damage; 91.49% of visible resolutions needed explicit user correction; constraint violations and inaccurate self-reporting grew in share (arXiv 2605.29442; visible pushback only, silent failures missed).
- 33k agent PRs: rejected PRs tend to be larger, touch more files and fail CI; documentation and CI tasks merge best, performance and bug fixes worst (arXiv 2601.15195).

**Verdict: adopt** plan-as-task-list and product-level history; avoid a restore that silently leaves state behind (label it, as Bolt does).

### 2.10 Jules, Amp, Factory

| Product | Pattern | Source |
|---------|---------|--------|
| Jules | Plan generated and approved before any code change; notifications on completion or need for input. UNVERIFIED: parallel tasks. | jules.google/docs |
| Amp | Saved, shareable threads; "orbs" are per-thread machines; start on phone, follow up in the TUI. The manual page gave no verified review or permission details. | ampcode.com/manual |
| Factory Droid | Autonomy Off, Low, Medium, High: each tool has a risk class compared with the level; `permissionRules` allow, ask or block with block winning; Ctrl+L cycles; admins can cap the level. Spec Mode is read-only; approval offers manual approvals, an autonomy level, or keep iterating. | docs.factory.ai auto-run, specification-mode |

**Verdict: adapt** Factory's risk-class-versus-level rule: it is deterministic and explainable, the kind of check EIJA's kernel can own as policy rather than model opinion.

### 2.11 Cross-cutting: reviewing large diffs

- Guidance: review 200 to 400 lines at a time, under 500 lines per hour, sessions under 60 minutes (SmartBear summary of a Cisco study; 2009-era practitioner source).
- Understanding the change dominates review time (Bacchelli and Bird, ICSE 2013): search snippet only, UNVERIFIED here, listed as motivation not evidence.
- Review comments on 3,177 agent PRs cluster into 12 themes: documentation, refactoring, style, testing, security, functional correctness (arXiv 2601.19287).
- 54,791 agent review comments across 342 repos: unresolved ones are mostly "incorrect suggestions" and "intentional design decisions"; inline code suggestions predict resolution; long, complex comments get less attention (arXiv 2607.21997).
- Automation bias: over-acceptance of automated output rises under workload; training reduces complacency more than bias (systematic review in decision support, PMC3240751, clinical domain; transfer to code is an assumption).

**Implication:** once an agent writes thousands of lines, lines are the wrong review unit; the count of meanings changed is.

### 2.12 Research on developer trust and outcomes

| Study | Design | Result | Confidence |
|-------|--------|--------|------------|
| METR RCT (2025) | 16 experienced OSS developers, 246 tasks in their own repos | 19% longer with AI (CI +2% to +39%); forecast 24% faster, believed 20% faster afterwards | High for what it measured; authors call it a snapshot of early-2025 tools |
| METR update (Feb 2026) | Late-2025 cohorts, n=10 and n=47 | Point estimates -18% (CI -38% to +9%) and -4% (CI -15% to +9%); authors call the signal unreliable because 30% to 50% of developers withheld tasks | Medium: authors' own caveats |
| Anthropic RCT (Jan 2026) | 52 mostly junior engineers, unfamiliar Python library | Quiz 50% vs 67% (d=0.738, p=0.01); about 2 min faster, not significant; delegation and iterative AI debugging under 40%, conceptual inquiry 65%+ | Medium: small n, immediate quiz, authors say so |
| Perry et al., CCS 2023 | User study, codex-davinci-002 | Assistant users wrote significantly less secure code and more often believed it secure; lower trust and prompt refinement gave fewer vulnerabilities | Medium: old model; n not in abstract |
| Wang et al., FAccT 2024 | 17 interviews plus design probe | Three challenges: building expectations, configuring the tool, validating suggestions; design directions: communicate performance, configuration, mechanism indicators | Medium: qualitative |
| Mozannar et al., CHI 2024 | 21 programmers, retrospective labelling | CUPS taxonomy of programmer activity with Copilot; reveals inefficiencies and time costs of verifying suggestions (no figure in abstract) | Medium |
| Stack Overflow 2025 | Self-reported survey | See section 3 | Medium: self-selected |
| DORA 2025 | About 5,000 professionals | 4% great deal and 20% a lot of trust; 23% a little; 7% not at all; over 80% report a productivity gain | Medium: self-report, via Google blog |

Pattern: perceived and measured effect diverge (METR, Perry), and how the developer uses the tool matters more than whether they use it (Anthropic RCT, Perry). None of these tested a tool that shows evidence with UNKNOWN visible.

## 3. Quantitative facts

| Fact | Source | Confidence |
|------|--------|------------|
| 93% of Claude Code permission prompts are approved (vendor-reported) | anthropic.com/engineering/claude-code-auto-mode | Medium (vendor, internal) |
| Auto-mode classifier on real overeager actions (n=52): 0.4% false positive, 17% false negative, full pipeline | same | Medium (vendor, small n) |
| Claude Code keeps snapshots for 100 checkpoints; retention sweep about 30 days | code.claude.com/docs/en/checkpointing | High |
| Agent view summary refresh: 15 s | code.claude.com/docs/en/agent-view | High |
| Codex keeps 15 most recent managed worktrees by default | learn.chatgpt.com/docs/environments/git-worktrees | High |
| Copilot coding agent: 59 minute maximum run | docs.github.com coding agent overview | High |
| Cascade: 40 tool calls per prompt by default | docs.devin.ai/desktop/cascade/cascade | High |
| METR 2025: 19% slower, CI +2% to +39%, n=16, 246 tasks | metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study | High |
| METR 2026: -18% (n=10) and -4% (n=47), CIs include zero; 30% to 50% withheld tasks | metr.org/blog/2026-02-24-uplift-update | Medium |
| Anthropic RCT: 50% vs 67% quiz, d=0.738, p=0.01, n=52 | anthropic.com/research/AI-assistance-coding-skills | Medium |
| Stack Overflow 2025: 3.1% highly trust accuracy, 45.7% distrust, 66% "almost right, but not quite", 45.2% say debugging AI code takes longer, 31% use agents regularly, 14.7% vibe code | survey.stackoverflow.co/2025/ai | Medium |
| DORA 2025: 90% adoption, 4% + 20% high trust, 30% little or none, over 80% productivity gain | blog.google DORA 2025 | Medium |
| 91.0% of 200 audited vibe-coded apps had at least one vulnerability; 65.77% Critical or High | arxiv.org/abs/2606.23130 | Medium (abstract only) |
| 90.50% of misalignment episodes are effort or trust costs; 91.49% need explicit user correction; 20,574 sessions | arxiv.org/abs/2605.29442 | Medium |
| 19,450 review comments over 3,177 agent PRs; 12 themes | arxiv.org/abs/2601.19287 | Medium |
| 54,791 agent review comments; Copilot accounts for 72.9% of resolved comments (a share, not a rate) | arxiv.org/abs/2607.21997 | Medium |
| Review 200 to 400 LOC, under 500 LOC per hour, under 60 min | smartbear.com best practices | Medium (2009 practitioner source) |
| Response-time limits 0.1 s, 1 s, 10 s | nngroup.com response times | High as convention; predates current UIs |
| PREDICTION (Hick-Hyman, relative only): choice component scales with log2(n+1). Plan approval with 3 choices: log2 4 = 2.0 bits. Rewind menu with 6 entries including "never mind": log2 7 = 2.81 bits. Ratio about 1.4 for the choice component alone. | derived here from Hick's law | Low: constants a and b unfitted, options are not equiprobable, reading text dominates real time |

## 4. Implications for EIJA

1. **Change the review unit from lines to meanings.** Make a semantic change list (glossary term renamed, state added, guard changed, journey step removed) the primary review surface, with the line diff one disclosure level down. Devin Review groups by intent with an LLM; EIJA can group from the model diff, which is checkable.
2. **Make ripple the second view of every change.** No surveyed product shows how one edit propagates to states, journeys, tests, personas and requirements. Show a count per affected model, with UNKNOWN listed separately and never folded into "no impact".
3. **Evidence as a tri-state column.** Kiro says "evidence, not a proof"; extend that honesty to PASS, FAIL or UNKNOWN per obligation (proof, model check, property test, mutation score). Sort UNKNOWN ahead of PASS.
4. **Owner approval is human-only and low-frequency.** 93% approval shows frequent prompts train reflex approval. Give the owner one gated moment per change with evidence in view; do not adopt classifier or `auto_review` approval.
5. **Deterministic autonomy rules.** Adopt Factory's risk-class-versus-level comparison as kernel policy for what an agent may propose without a pause.
6. **Undo with a coverage label.** Every undo states what it does not restore (external state, data, other models). Borrow Claude Code's list and Bolt's database caveat. Never ship an undo that cannot be undone.
7. **Parallel agents as a state-grouped list.** Rows grouped Needs owner decision, Working, Checked, Failed; one-line summary; evidence tri-state. Cursor's admission of micromanagement shows a list alone is not enough, so the row must answer "what do you need from me".
8. **Ambient context and cost.** A small meter (Zed) and coarse cost pills (Devin), not panels. Any wait over 1 s needs feedback; over 10 s, a progress indicator and cancel (Nielsen).
9. **At most two disclosure levels per surface,** tool calls collapsed by default with a verbose toggle (Claude Code Desktop). A third level needs an HCI-ADR.
10. **Plan the study; do not claim the benefit.** Within-subjects comparison of baseline Studio vs proposed, measuring seeded-defect detection, UNKNOWN recall and time, plus a calibration measure (confidence vs correctness), because METR and Perry show self-report diverges from outcome. No user-benefit claim until it runs.

## 5. Gaps and unverified items

- **UNVERIFIED (search snippet only, not used for decisions):** Cursor "up to 8 parallel agents"; Lovable plan revisions rendered as a diff; Jules parallel tasks; Replit's post-incident fixes; Bacchelli and Bird's finding that understanding dominates review time; Grounded Copilot's acceleration and exploration modes (arXiv 2206.15000); a secondary claim that human reviewers caught a disguised dangerous command 13.6% of the time and that 97% (not 93%) of prompts are approved. The primary Anthropic post, as summarised, reports 93% and no such controlled study.
- **Not opened:** Copilot Workspace history, Windsurf's own review UI, Amp permissions and review, Factory's web app, Devin's planning UI, Horvitz (1999) mixed-initiative principles, the Doherty and Thadhani 400 ms threshold (only Nielsen's three limits were read).
- **No product was used.** Findings are from documentation, changelogs, first-party blogs and some third-party write-ups; no interaction cost was measured. Layout and task-flow numbers belong to design/layouts and design/tasks, not here.
- **Vendor bias:** every product statistic (auto-mode rates, Bugbot, review timing) is vendor-reported.
- **Study limits:** small samples (16, 52), old tools (METR 2025), self-selection (Stack Overflow, DORA). No study tests semantic review, ripple views or visible UNKNOWN: a research gap and a study opportunity.
- **2026 arXiv papers** were read at abstract level only, and the abstract pages did not show peer-review status.

## 6. URLs opened (access date 2026-09-29)

| Topic | URL |
|-------|-----|
| METR 2025 | https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/ |
| METR 2026 update | https://metr.org/blog/2026-02-24-uplift-update/ |
| Claude Code checkpoints | https://code.claude.com/docs/en/checkpointing |
| Claude Code permissions | https://code.claude.com/docs/en/permissions |
| Claude Code permission modes | https://code.claude.com/docs/en/permission-modes |
| Claude Code workflows | https://code.claude.com/docs/en/common-workflows |
| Claude Code agent view | https://code.claude.com/docs/en/agent-view |
| Claude Code Desktop | https://code.claude.com/docs/en/desktop |
| Anthropic auto mode | https://anthropic.com/engineering/claude-code-auto-mode |
| Anthropic coding-skills RCT | https://www.anthropic.com/research/AI-assistance-coding-skills |
| Stack Overflow 2025 AI | https://survey.stackoverflow.co/2025/ai |
| DORA 2025 (Google blog) | https://blog.google/innovation-and-ai/technology/developers-tools/dora-report-2025/ |
| DORA landing | https://dora.dev/dora-report-2025/ |
| Cursor changelog | https://cursor.com/changelog , https://cursor.com/changelog/page/2 |
| Cursor docs | https://cursor.com/docs , https://cursor.com/docs/agent/overview |
| Cursor 3 blog | https://cursor.com/blog/cursor-3 |
| Cursor 3 (third party) | https://www.datacamp.com/blog/cursor-3 |
| Codex app | https://learn.chatgpt.com/docs/app |
| Codex worktrees | https://learn.chatgpt.com/docs/environments/git-worktrees |
| Codex approvals | https://learn.chatgpt.com/docs/agent-approvals-security |
| Codex review | https://learn.chatgpt.com/docs/code-review?surface=app |
| Windsurf Cascade | https://docs.devin.ai/desktop/cascade/cascade |
| Devin intro | https://docs.devin.ai/get-started/devin-intro |
| Devin Review docs | https://docs.devin.ai/work-with-devin/devin-review |
| Devin Review blog | https://cognition.com/blog/devin-review |
| Lovable | https://docs.lovable.dev/introduction/welcome , https://docs.lovable.dev/changelog |
| Bolt | https://support.bolt.new/building/using-bolt/rollback-backup , https://bolters.io/docs/diffs.html (community) |
| v0 | https://vercel.com/blog/introducing-the-new-v0 |
| Replit Agent | https://docs.replit.com/replitai/agent |
| Replit incident | https://www.theregister.com/2025/07/21/replit_saastr_vibe_coding_incident/ |
| Copilot coding agent | https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent |
| VS Code agents | https://code.visualstudio.com/docs/copilot/agents/overview |
| Zed | https://zed.dev/docs/ai/agent-panel |
| Kiro | https://kiro.dev/docs/specs/ , https://kiro.dev/docs/specs/correctness/ , https://kiro.dev/blog/introducing-kiro/ |
| Jules | https://jules.google/docs |
| Amp | https://ampcode.com/manual |
| Factory | https://docs.factory.ai/cli/user-guides/auto-run , https://docs.factory.ai/cli/user-guides/specification-mode |
| Papers (abstract pages) | https://arxiv.org/abs/2211.03622 , https://arxiv.org/abs/2305.11248 , https://arxiv.org/abs/2210.14306 , https://arxiv.org/abs/2606.23130 , https://arxiv.org/abs/2605.29442 , https://arxiv.org/abs/2601.15195 , https://arxiv.org/abs/2601.19287 , https://arxiv.org/abs/2607.21997 , https://arxiv.org/abs/2507.22358 |
| Automation bias review | https://pmc.ncbi.nlm.nih.gov/articles/PMC3240751/ |
| Code review size | https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/ |
| HCI laws | https://www.nngroup.com/articles/response-times-3-important-limits/ , https://www.nngroup.com/articles/progressive-disclosure/ , https://lawsofux.com/hicks-law/ , https://lawsofux.com/fittss-law/ |

Magentic-UI (arXiv 2507.22358, opened) lists six interaction mechanisms for low-cost human involvement (co-planning, co-tasking, multi-tasking, action guards, long-term memory); its abstract gives no quantitative results, so it is cited only as prior art for co-planning and action guards.
