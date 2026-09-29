# Future work: deliberate deferrals

Phase 1 of the [work breakdown](WBS.md) builds the mainline and proves it; anything that only tests a hard edge
case is recorded here instead of built. Each row says why it waits, what should trigger it, and a rough size
(S under a day, M one to three days, L more).

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
