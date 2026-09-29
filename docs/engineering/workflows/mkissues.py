"""Create labels, milestones and issues for the EIJA Studio plan (45ck/eija-studio). Idempotent by title."""
import json, subprocess, sys

REPO = "45ck/eija-studio"
BRANCH = "integrate/all"
FOOT = "\n\n---\nPlan of record: `docs/engineering/WBS.md` on `integrate/all` (PR #29). Tracker: #30. Deferred edge cases: `docs/engineering/FUTURE-WORK.md`.\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)"

LABELS = {
    "phase-1": ("0e8a16", "Phase 1: domain-agnostic POC core"),
    "phase-2": ("1d76db", "Phase 2: IDE workbench"),
    "phase-3": ("5319e7", "Phase 3: scenes and recording"),
    "later": ("c5def5", "Not in the POC or demo; future work"),
    "owner-only": ("b60205", "Only the owner can do this; agents must never"),
    "kernel": ("fbca04", "Kernel, packs, laws, transactions"),
    "formal": ("d4c5f9", "Formal V&V: Z3, BMC, TLA+, Bend, evidence kinds"),
    "ui": ("f9d0c4", "Studio UI / workbench"),
    "demos": ("bfdadc", "Demo scenarios and recording"),
    "gates": ("ededed", "Quality gates, CI-equivalent, tooling"),
    "weave": ("c2e0c6", "Weave: deterministic code/UI/UML/language links"),
    "hygiene": ("e4e669", "Repo organisation and housekeeping"),
    "deferred": ("cfd3d7", "Deliberately deferred edge case"),
}
MILESTONES = {
    "Phase 1: domain-agnostic POC": "The kernel takes its domain from a pack; two packs run the whole chain; merged to main.",
    "Phase 2: IDE workbench": "IDE-style shell, language/DDD tree, option-D drag-and-drop canvas, landing queue, comparison harness.",
    "Phase 3: scenes and recording": "Four flagship scenes as pack-parameterised scripts, recorded from passing runs; README hero.",
    "Later": "Dogfooding, more languages, deferred proofs and edge cases.",
}
P1, P2, P3, LT = list(MILESTONES)

# (title, milestone, labels, body)
ISSUES = [
 # ---------------- Phase 1 (remaining) ----------------
 ("1.5 Vocabulary fitness gate and removal of pack literals from generic code", P1, ["phase-1", "kernel", "gates"],
  "**State:** started. A WIP checkpoint is on `integrate/core` (`725cc9b`, `quality/gates/vocabulary.py`), merged into `integrate/all`. Not gated or reviewed.\n\n"
  "**Do:** `quality/sessions/vocabulary.py` (fast tier) extracts vocabulary tokens from every pack and scans `src/`, `verification/*.py`, `quality/`, `scripts/`, `contracts/` (exclude `packs/`, GENERATED-headed files and a justified allowlist); also fail on any `Literal[...]` containing a pack token. Record the count before and after removing literals (target zero outside the allowlist).\n\n"
  "**Definition of done:** gate green on the tree; a planted pack token in generic code fails it (negative control); allowlist small and justified (hand-written Bend/TLA excursion proofs are recorded debt); later extended to scan `demos/` and `resources/web` (Phase 2).\n\n**Model:** strong (Opus). **Size:** M."),
 ("1.4b Z3 equivalence gate for the generated SMT laws, with negative control", P1, ["phase-1", "formal"],
  "**State:** `349917d` generates the SMT laws from the pack and drives BMC through `evaluate_run`. Verify the proof obligations actually exist.\n\n"
  "**Do:** confirm/add a Z3 check that hand-written and generated encodings are equivalent on the excursion pack (unsat of the difference) and that the existing differential sampling still passes.\n\n"
  "**Definition of done:** equivalence gate in the formal session; deleting or weakening a law in the pack makes it FAIL; for a NEW pack the kernel reports `bend_proof` and `tlc` as NOT_RUN with the reason, never PASS.\n\n**Model:** strong. **Size:** S-M."),
 ("1.6 Weave-lite: review, tests and integration", P1, ["phase-1", "weave"],
  "**State:** built on `track2` (`d6c6b3b`: index, rules WV-001/002/003/005, SARIF, impact, CLI) and merged into `integrate/all`. Not gated as a whole.\n\n"
  "**Definition of done:** root hash byte-identical across runs and across declaration reordering, on both packs; a planted dangling `repo://` and a planted duplicate binding each give exactly one finding; `eija index | lint [--sarif] | impact` documented; import-linter layering intact.\n\n**Model:** Sonnet. **Size:** S."),
 ("1.7 Evidence kinds: tlc, property, generality, robustness + committed smt/bmc snapshots", P1, ["phase-1", "formal"],
  "Per ADR-0145/0146 add typed artifacts with pure recomputed checks; the mutation kind stays UNKNOWN (deferred). Commit `verification/smt/evidence/smt.json` and `bmc.json` regenerated from the generated laws (with source bindings) so a fresh clone shows PASS, not a silent NOT_RUN.\n\n"
  "**Definition of done:** tampered artifact -> FAIL; missing negative control -> UNKNOWN; forged claimed verdict rejected because the kernel recomputes; fresh clone shows no silent NOT_RUN for smt/bmc.\n\n**Model:** Opus. **Size:** M."),
 ("1.8 MCP and CLI wiring for packs, affordances, lint, impact", P1, ["phase-1", "kernel"],
  "Pass the diagram renderer into the MCP server (mermaid/plantuml/svg currently fail: `mcp_server.py` never receives `diagram_renderer`). New MCP tools `pack`, `affordances`, `lint`, `impact`, `propose_transaction` (records PROPOSED only; the owner accepts via HTTP). CLI `init --pack`, `laws generate|--check` (SMT only). Decisions stay HTTP-only.\n\n"
  "**Definition of done:** tests prove no MCP tool, alias or attribute path lets an agent select, approve or apply; mermaid render works over MCP.\n\n**Model:** Sonnet. **Size:** S."),
 ("1.9 Held-out pack and generality + robustness evaluation with measured numbers", P1, ["phase-1", "formal", "kernel"],
  "A third pack authored from the pack schema docs ONLY and structurally different (e.g. CI/CD deployment approval or medical referral: a cycle, 3+ roles, two final states). `quality/generality/run.py` runs every pack: load, policy, apply every meaning, render all views, weave index, SMT-generated laws prove under Z3; a small malformed corpus plus Hypothesis (`max_examples=50`, derandomized) gives diagnostics only, never PASS.\n\n"
  "**Metamorphic relations:** alpha-renaming gives identical verdicts modulo names; reordering gives equal `semantic_hash`, byte-equal diagrams, equal weave root.\n\n"
  "**Definition of done:** numbers reported as MEASUREMENT with sample sizes (packs run, checks per pack, pass counts); a pack with a violated law yields a FAIL row; a planted vocabulary dependency makes the relations fail.\n\n**Model:** strong. **Size:** M."),
 ("1.10 End-to-end test on two packs and `nox -s clean_clone`", P1, ["phase-1", "gates", "kernel"],
  "`tests/e2e` over public surfaces only, offline, mock provider, harness identity, on BOTH excursion and library-loan: MCP propose -> kernel check -> UML before/after + ripple -> per-kind evidence (PASS/FAIL/UNKNOWN/NOT_RUN shown) -> owner decision via HTTP. `nox -s clean_clone` (full tier) clones into `.tmp`, installs with uv, runs `eija --help` and the e2e test, prints timings. Record one terminal GIF with `python -m demos pr-gif`.\n\n"
  "**Definition of done:** green on both packs; asserts the agent path cannot approve or apply; clean-clone timing recorded.\n\n**Model:** Sonnet. **Size:** M."),
 ("1.11 ADRs and docs closure (ADR-0153, law DSL, WBS rewrite)", P1, ["phase-1", "docs" if False else "hygiene"],
  "ADR-0153 domain-agnostic kernel (closes the dangling link in `GENERALITY-AUDIT.md`); an ADR for the law DSL; ADR-0145/0146 to accepted; `POC-DEFINITION.md` criterion 9 (\"works on a pack the code was not written for\"); `GENERALITY-AUDIT.md` closure with re-measured counts; README status honest; regenerate the ADR index; rewrite `WBS.md` to the plan of record; `FUTURE-WORK.md` complete.\n\n**Model:** Sonnet. **Size:** S."),
 ("1.12 Full gate tier on the merged tree, adversarial review, merge to main", P1, ["phase-1", "gates"],
  "**Important:** nobody has run `nox -t full` on the combined Phase 1 tree, and it is unclear whether `.githooks/pre-push` ran on every push (no `--no-verify` seen).\n\n"
  "**Do:** merge `main`, run `nox -t fast`, `nox -t full`, non-Docker lane sessions, `nox -s clean_clone`. One independent adversarial review (authority: can an agent approve/apply by any path incl. `propose_transaction`, affordance and edit-check endpoints, pack meanings; SMT equivalence; excursion behaviour preservation; held-out pack independence; NOT_RUN vs PASS; vocabulary gate). Acceptance-criteria table in PR #29 (met / partial / unmet with evidence). Merge PR #29 to `main`, close superseded lane PRs (#12, #14, #16, #22, #23, #24, #25), delete stale remote branches.\n\n"
  "**Definition of done:** every gate green (Docker/Bend/live providers NOT_RUN with the reason); no open blocker/major; both packs pass e2e; `main` = domain-agnostic POC.\n\n**Model:** Opus. **Size:** M."),
 ("Refresh the Bend proof evidence snapshot (needs Docker)", P1, ["phase-1", "formal", "later"],
  "The committed Bend snapshot needs a Docker run to refresh after the Phase 0 fixes; it is NOT_RUN with a strict xfail. Run once when Docker is available and commit the snapshot.\n\n**Size:** S."),
 # ---------------- Phase 2 ----------------
 ("2.1 Workbench shell: language/DDD tree, Ctrl+K palette, Problems and evidence panels", P2, ["phase-2", "ui"],
  "Replace the five-tab wizard with an IDE-style shell (vanilla JS/CSS, no bundler, strict CSP): CSS-grid tree | editor tabs | Problems/Evidence | status bar; `tokens.css` generated from `design/tokens/*.json` with a drift check; ARIA `role=tree` (roving focus) built from the pack; Problems panel fed by `eija lint`; evidence panel per kind; every element carries `data-eija-id=\"<pack>.<kind>.<id>\"`. Model editors only; code read-only.\n\n"
  "**Definition of done:** axe: no serious violations; keyboard-only journey; tokens drift check; a planted domain word in `resources/web` fails the vocabulary gate.\n\n**Model:** Sonnet. **Size:** L."),
 ("2.2 Canvas with option-D drag: a drag is one typed transaction the kernel accepts or refuses", P2, ["phase-2", "ui", "kernel"],
  "SVG state/flow canvas (~500 lines) + vendored dagre (49 KB, MIT; CSP smoke test asserts no `Function(`/`eval(`). Pointer Events, 8-unit snap. A drag emits exactly ONE transaction through the edit/check endpoint and affordance map: accepted -> redraw from the SERVER model (150 ms transition); refused -> snap back and announce the law code + refs at the drop target in a live region; `prefers-reduced-motion`; a keyboard path for every gesture (WCAG 2.5.7); role-chip drag onto a transition. New HCI-ADR supersedes ADR-0061 (D-lite).\n\n"
  "**Definition of done (Playwright, one Chrome, both packs):** accepted drag redraws from the server; refused drag snaps back with the law code; DOM == render(model, layout) on 5 fixtures; measured p95 settle time and Fitts/Hick as MEASUREMENT with N stated; a planted illegal transaction is refused.\n\n**Model:** Opus. **Size:** L."),
 ("2.3 Scene-2 view: agent inbox with semantic diff, ripple, per-kind evidence and counterexample", P2, ["phase-2", "ui"],
  "Agent inbox and chapters over `diff_summary`, `impact` and per-kind evidence; the refused/unsafe proposal shows its counterexample. **DoD:** a fixture case renders every chapter on both packs.\n\n**Size:** M."),
 ("2.4 Plain-script landing queue and weave-based conflict predictor", P2, ["phase-2", "demos", "weave"],
  "`quality/tools/landq.py` (no LLM): merge main into a scratch worktree, run the fast gates on the MERGE RESULT, land the green, hold the red with the reason; predictor over weave links (files, symbols, terms) names a conflict BEFORE merging. **DoD:** two scripted branches with a planted overlap: predicted, one lands, one held; a branch that breaks a gate is never landed (negative control).\n\n**Size:** M."),
 ("2.5 Side-by-side vs vibe-coding comparison harness (measured)", P2, ["phase-2", "demos"],
  "Run the same N (default 5) proposed changes offline through a plain text-edit path and the kernel path; a kernel-conformance oracle scores both (does the model still satisfy every pack law?). Output a table of changes, violations caught and ripple size as MEASUREMENT with N stated, never a claim. Works on both packs.\n\n**Size:** M."),
 ("2.6 HCI re-baseline for the new shell (lighter)", P2, ["phase-2", "ui", "gates"],
  "Re-derive the HCI budgets for the workbench (budgets keyed by pack; Fitts/Hick/KLM/Doherty/axe). Record HCI-ADRs 0069+ for decisions taken. The 26->27 chunk ratchet was accepted on the old UI and is re-derived here.\n\n**Size:** M."),
 ("2.7 `pr-gif` verbs: drag, hover, keypress, split-pane, cursor overlay", P2, ["phase-2", "demos"],
  "Extend `demos/prgif` steps; unit-test the step parser and fit logic; browser verbs skip with NOT_RUN if Chrome is unavailable.\n\n**Size:** S."),
 # ---------------- Phase 3 ----------------
 ("3.1 Four flagship scenes as pack-parameterised scripts with dry-run tests", P3, ["phase-3", "demos"],
  "Scenes: (2) agent change reviewed as semantic diff + ripple + per-kind evidence incl. the refused proposal with counterexample; (3) drag-and-drop UML updates the software (one accepted, one refused drop with the law code); (4) parallel agents landing safely (predicted conflict, one lands, one held); (1) side-by-side vs vibe coding with the measured table.\n\n"
  "**Robustness rules:** scripts act only through `data-eija-id` and the affordance API, assert against kernel state, never contain domain words (vocabulary gate scans `demos/`), and their dry-run test runs on BOTH excursion and library-loan in the gates.\n\n**Size:** L."),
 ("3.2 Record from passing runs only; README hero GIF and 60 s cut; merge to main", P3, ["phase-3", "demos"],
  "Record each scene only after its dry run passed on both packs (one Chrome, live cursor and typing, GIF <=5 MB, <=1280 px, <=20 s); library-loan (a domain the kernel was not written around) and excursion. Registry marks `recorded` only via the recorder. README: hero GIF, quickstart verified by `nox -s clean_clone`, honest \"Status and limits\". Full gates, acceptance table, merge.\n\n**Size:** M."),
 # ---------------- Owner-only ----------------
 ("OWNER: restamp the release fixture (green banner)", LT, ["owner-only"],
  "Only the owner runs `scripts/stamp_release.py --acknowledge-self-authored-fixture` (writes `src/eija_studio/resources/trusted_build.json`). Until then the Studio shows `SOURCE_REVIEW_REQUIRED` and POC criterion 1's green banner is unmet. Agents must never do this."),
 ("OWNER: API keys and consent for live provider spend", LT, ["owner-only"],
  "Provide keys via `eija serve --ask-key` (never through an agent) and consent to live calls. Until then live agent scenes stay NOT_RUN. Live status so far: claude and codex smoke PASS; gemini NOT_RUN (auth); opencode/openrouter NOT_RUN."),
 ("OWNER: approve publication (tag, README, recording)", LT, ["owner-only"],
  "Publication is an owner decision: release tag, README, recorded demo."),
 ("OWNER: glance at the agent-hook change and the OKF attestation", LT, ["owner-only", "hygiene"],
  "(1) Phase 0 added `git commit -n`, `core.hooksPath` and `HUSKY=`/`SKIP=` bypass checks to the narrowed `.claude/hooks/pre-tool-use.sh` (security-adjacent). (2) 25 stale OKF pages were re-read by an agent and recorded with `review` = `process:claude-code-integration-phase0`, a self-declared machine actor at tier `machine-confirmed`. Neither blocks work; both deserve a human look."),
 ("OWNER: author and sign the dogfooding standing policy (later)", LT, ["owner-only", "later"],
  "For dogfooding stage S4 (the kernel as merge gate for this repo) the owner authors and signs a standing policy: which change cases may auto-land and with what evidence; everything else escalates. Agents never approve."),
 # ---------------- Hygiene ----------------
 ("Add `.gitattributes` to normalise line endings (LF)", P1, ["hygiene", "gates"],
  "Files written by Windows Python came out CRLF against LF in HEAD, producing whole-file rewrites in diffs and breaking the workflow launcher. Add `* text=auto eol=lf` (binary exceptions) and renormalise. **Size:** S."),
 ("Close superseded lane PRs and delete stale branches after the merge", P1, ["hygiene"],
  "After `integrate/all` merges: close #12, #14, #16, #22, #23, #24, #25 pointing at the merge; delete remote `lane/*`, `wip/*`, `feat/pr-media`, `docs/domain-agnostic`, `poc/tracker`, `integrate/core`, `track2`. Delete the empty `C:\\Dev\\eija-wt\\rev-visual` directory locally."),
 ("Complexity ratchet: bring `verification/` under it (32 functions over budget)", LT, ["deferred", "gates"],
  "Deferred from Phase 0: `verification/` is outside the complexity ratchet; 32 functions exceed the budget. **Trigger:** after the POC merges. **Size:** M."),
 # ---------------- Later ----------------
 ("Generate Bend and TLA+ laws from packs (heavy tools)", LT, ["later", "formal", "deferred"],
  "Deferred: for a NEW pack `bend_proof` and `tlc_model_check` report NOT_RUN with the reason; the hand-written excursion proofs stay, labelled hand-encoded. **Trigger:** need for formal Bend/TLA+ evidence on non-excursion packs. **Size:** L."),
 ("`path_requires` inductive proofs and the mutation evidence kind", LT, ["later", "formal", "deferred"],
  "Sequence laws need hand-written inductive proofs per pack; the mutation kind stays UNKNOWN until a floor is declared. **Size:** L."),
 ("Weave rules WV-010 (requirement without verifier) and WV-020 (term/element/symbol bijection)", LT, ["later", "weave", "deferred"],
  "Deferred from weave-lite (which ships WV-001/002/003/005). **Size:** M."),
 ("Bigger fuzzing and unicode/homoglyph packs; unrelated-element metamorphic relation", LT, ["later", "formal", "deferred"],
  "The first cut uses `max_examples=50` derandomized and alpha-renaming/reordering relations only. **Size:** M."),
 ("Dogfooding stages S1-S5: EIJA develops itself", LT, ["later", "kernel"],
  "S1 EIJA's own domain as a pack (its language: Proposal, ChangeCase, Evidence kind, Receipt, Verdict, Owner decision, Provider, Lane, Landing); S2 an EIJA review packet on every PR; S3 drift lint on our own code; S4 kernel as merge gate under an owner-signed standing policy; S5 agents via MCP.\n\n**Trigger:** after Phase 3. **Size:** XL."),
 ("Multi-language code linking (tree-sitter) beyond Python via `ast`", LT, ["later", "weave"],
  "The POC links Python via stdlib `ast`; other languages bind at file level. **Size:** L."),
 ("In-app image generation and persona/ICP scenarios", LT, ["later", "demos"],
  "Not in the four flagship scenes; unstarted (registry: `image_generation_in_studio`, `e2e_tests_personas_icp` blocked on missing lanes). **Size:** L."),
 ("Design-patterns view, Neo4j export, multi-entity runtime, proof certificates", LT, ["later", "kernel"],
  "Deferred H2 items from the product thesis and lane map. **Size:** XL."),
 ("Definition-of-done / evals lane (ADRs 0113-0136 unwritten)", LT, ["later", "gates"],
  "Design-only today (`docs/dod`). Internal metrics, evals and a product/software/V&V definition of done. **Size:** L."),
]

def sh(args, **kw):
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", **kw)

def main():
    have = {l["name"] for l in json.loads(sh(["gh", "label", "list", "-R", REPO, "--limit", "100", "--json", "name"]).stdout or "[]")}
    for name, (color, desc) in LABELS.items():
        if name not in have:
            r = sh(["gh", "label", "create", name, "-R", REPO, "--color", color, "--description", desc])
            print("label", name, "ok" if r.returncode == 0 else r.stderr.strip()[:100])
    ms = {m["title"]: m["number"] for m in json.loads(sh(["gh", "api", f"repos/{REPO}/milestones?state=all", "--paginate"]).stdout or "[]")}
    for title, desc in MILESTONES.items():
        if title not in ms:
            r = sh(["gh", "api", f"repos/{REPO}/milestones", "-f", f"title={title}", "-f", f"description={desc}"])
            print("milestone", title, "ok" if r.returncode == 0 else r.stderr.strip()[:100])
    existing = {i["title"] for i in json.loads(sh(["gh", "issue", "list", "-R", REPO, "--state", "all", "--limit", "300", "--json", "title"]).stdout or "[]")}
    made = []
    for title, ms_title, labels, body in ISSUES:
        if title in existing:
            print("exists", title[:60]); continue
        labels = [l for l in labels if l in LABELS]
        args = ["gh", "issue", "create", "-R", REPO, "--title", title, "--body", body + FOOT, "--milestone", ms_title]
        for l in labels: args += ["--label", l]
        r = sh(args)
        url = r.stdout.strip().splitlines()[-1] if r.returncode == 0 and r.stdout.strip() else ""
        print("issue", url or ("FAILED " + r.stderr.strip()[:120]), "|", title[:60])
        if url: made.append((title, url))
    json.dump(made, open(sys.argv[1] if len(sys.argv) > 1 else "issues_made.json", "w"), indent=1)

main()
