# Future work and retained technical leads

**Reconciled 11 October 2026.** The [current roadmap](../ROADMAP.md) and [delivery contract](PLAYIDE-DELIVERY.md) supersede the old phase/branch sequencing below. The older rows are retained technical leads, not a claim that each item is still missing in today's implementation. Recheck linked code, tests and issue state before taking one on; preserve original evidence when an item is resolved.

## Current priorities

| Work | When and why | Required outcome |
|---|---|---|
| Finish integrated tracing, C4, shared identities and persistent recovery | M1: new local code does not yet have complete combined browser/release evidence | Current SD01–SD12 and UX01–UX08 observations; exact build/pack/data/screens/template/implementation subject; no inherited green results |
| Clean installation and distribution | M1: another engineer must reproduce the product outside this checkout | Fresh Windows and Linux records where actually run; correct packs/resources; installation and launch from a path with spaces |
| Typed action inputs, conditions and updates | M2: RefundDesk amounts currently do not determine eligibility | Typed semantics in the existing kernel, forms/diffs and transactional failure tests |
| Revision adoption and migrations | M2: retained records and cases cannot depend on disposable workspaces | Compatibility preview, explicit transformations, validation, backup and recovery; no silent schema reinterpretation |
| Relationships and asynchronous delivery | M3: drawn related classes/workflows do not establish runtime coordination | Referential/multiplicity invariants, aggregate boundaries, idempotency, retries and recovery against real test adapters |
| Source/model transformations and parallel changes | M4: read-only source facts are not source-generation assurance | Bounded transformation/refusal contract and checks on actual combined changes |
| Shared operations | M5: local owner fixtures are not production authority | Authentication, authorisation, secrets, deployment, monitoring, backup/restore and incident evidence |
| Consented live pilot and human benefit | Separate validation after supported journeys work | Actual provider run and the [V&V study](../research/2026-10-02-vv-protocol.md); fixtures, videos and test counts are not substitutes |

Reuse existing requirement and issue identities through the roadmap. Language-edit transactions remain outside the workflow vocabulary in `domain/transactions.py`; treating vocabulary, law, schema or screen drafts as active still needs the corresponding revision contract. The current store refuses incompatible workspace/case identities rather than silently migrating them. Formal backend generalisation and third-party extension work remain evidence-driven additions, not prerequisites for claiming every supported local feature.

## Historical leads to revalidate

These estimates and implementation counts describe the earlier audit. They are neither fresh measurements nor permission to omit current regression checks.

| Item | Why it waits | Trigger | Size |
|---|---|---|---|
| Refresh `verification/bend/evidence/bend.json` with the fixed Bend runner (per-law `--verdict`, archive pin, Dockerfile-hash image tag) | The snapshot is a real Docker run and this PC does not start Docker (Docker-backed sessions are NOT_RUN here). The strict xfail `test_the_snapshot_was_produced_by_the_current_gate_and_dockerfile` marks the gap and starts failing loudly (XPASS) once the snapshot is refreshed | A host with Docker: `nox -s formal_bend -- --build --snapshot`, then remove the xfail marker | S (one run, a few minutes, plus one commit) |
| Put `verification/` under the complexity ratchet (xenon roots and `DEFAULT_ROOTS`) | 32 functions in `verification/{smt,tla,bend,...}` are over the budget of 10 (the worst: `tla/run.py::main` 26, `smt/prove.py::build_report` 26). Recording them as debt would launder new debt; refactoring formal-lane code is a behaviour-risk change that needs its own tests | The formal lanes are next edited, or before Phase 1 exit | M (32 refactors, each with the lane's own regression tests) |

### Earlier phase deferrals

The [work breakdown](WBS.md) supplies historical context. Its phase references and rough sizes below need reconciliation with M0–M5 before scheduling work (S under a day, M one to three days, L more in that original estimate).

| Item | Why deferred | Trigger | Size |
|---|---|---|---|
| Generate Bend laws (`LAWS.bend`) from a pack | The hand-written excursion proofs stay (labelled hand-encoded); a new pack reports `bend` as NOT_RUN with the reason (`packs/library-loan/pack.json`, `verifiers`) | A second pack needs Bend evidence for a demo or a review | L |
| Generate TLA+ laws (`Laws_<pack>.tla`) from a pack | Same: `Excursion.tla` stays hand-written; a new pack reports `tlc` as NOT_RUN | TLC evidence is required for a non-excursion pack | M |
| Inductive proofs for `path_requires` | The law is checked on the table (graph reachability) and on runs (`evaluate_run`); no proof certificate | A pack whose safety case rests on a sequence law | L |
| `mutation` evidence kind | Stays UNKNOWN until a floor is declared; never PASS on score alone | A declared mutation floor per pack | M |
| Weave rules WV-010 and WV-020 | Law/term without verifier and term/element bijection are research-grade checks | Weave-lite (WBS 1.6) is in daily use on two packs | M |
| Unicode/homoglyph pack identifiers and large pack fuzzing | The loader fuzz runs 50 derandomised single edits; ids are ASCII-pattern constrained | Packs authored by third parties | M |
| Metamorphic relation "unrelated extra element leaves verdicts unchanged" | The alpha-renaming and reordering relations cover the POC | Held-out pack evaluation (WBS 1.9) needs it | S |
| Old Change Case migration | Old cases are refused cleanly with `CASE_SCHEMA_OLD`; POC workspaces are disposable | A workspace that must survive a kernel upgrade | M |
| Hypothesis schema/model drift tests for `contracts/pack.schema.json` | The pack schema is checked for regeneration drift and both packs validate against it; the generated-instance fuzzing used for the smaller contracts is too slow for the nested pack | A pack authoring tool that emits packs from the schema | S |
| Ship `packs/` inside the wheel | Packs live at the repository root; an installed wheel needs `EIJA_PACK` pointing at a pack directory | The first published wheel | S |
| Resolve `repo://` term bindings at load time | The loader checks the URI form only; resolution and digests belong to weave-lite (WBS 1.6) | WBS 1.6 | S |
| Language-edit transactions (`rename_term`, `bind_term`) | Not in the typed vocabulary yet (`domain/transactions.py`): a case holds a workflow, not a language overlay, and binding needs the weave index; an unknown kind is refused by the contract (422) | The workbench tree (WBS 2.1) edits terms, after WBS 1.6 | M |
| Remove the deprecated closed `models.SemanticTransaction` | Only `verification/bend/bend_generate.py` still builds one, and the committed Bend proof binds that file's bytes; changing them turns the Bend evidence non-PASS and Docker is not available to regenerate it | WBS 1.4 regenerates the Bend model and proof | S |
| Affordances for structural edits (add/remove state or transition, guards, effects) | The map enumerates the drag (transition end x state) and role changes (transition x role), the two canvas gestures of the demo; the other kinds are still checked when applied (`edit/check`, `edit`) | The canvas offers add/remove gestures (WBS 2.x) | S |
| Bind the per-pack generated-law SMT report into the review packet | `python -m verification.smt.laws` proves every pack (reports/formal/smt-laws-<pack>.json), but the packet still reads only the hand-encoded excursion report; a pack whose `smt_proof` verifier is `generated` is NOT_RUN in the packet with that reason | WBS 1.7 (committed smt/bmc evidence with source bindings) | S |
| Model an undeclared action's fields in the SMT grammar | The grammar keeps one flag for "some undeclared action" (as the hand grammar did): admission is exact (UNSUPPORTED_ACTION), but the other codes such an action would add are not modelled, so the differential compares those candidates (10 of 1237 for library-loan) on admission only | Error-code precision matters for a pack-authoring UI | S |
| BMC search over a non-excursion pack's runtime | The state property is generic (`evaluate_run`), but `verification/bmc/report.py` explores the excursion workflows and fixture actors only; library-loan's `bounded_model_check` is NOT_RUN in the packet with the reason | A second pack needs runtime BMC evidence | M |
| Retire the hand-written SMT encoding | The equivalence gate passes (23/23 codes, 27/27 planted pack defects detected); the hand encoding is kept as the reference until the owner decides; note that 5 of the 27 planted defects are caught only by code equivalence, not by the hand-written authority invariants, which are weaker than the pack's laws | Owner decision after the milestone review | S |
| Pack-declared controls for the kernel's hand-proof admissibility (`domain/formal_smt.py` NAMED_CONTROLS, `domain/formal_bend.py` CONTROLS) | They name the excursion's clauses and witnesses, so the vocabulary gate allowlists both files as debt; moving them into the pack now would be redone by 1.7 and must not weaken the check | WBS 1.7 (`laws[].controls`) | S |
| Pack-driven smoke scripts (`scripts/browser_smoke.py`, `browser_component_smoke.py`, `http_smoke.py`, `wheel_smoke.py`, `capture_visual_screenshots.py`) | They drive the default pack's demo journey step by step; allowlisted by the vocabulary gate as debt | WBS 1.10 e2e runs both packs | M |
| Context-aware vocabulary matching | The gate is a case-sensitive whole-word search; three pack tokens that are also English or UML words (`Return`, `Member`, `unsupported`) are not searched, and one English heading carries a `vocab-ok:` line marker | A pack whose tokens collide with more common words | S |
