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
| Language-edit transactions (`rename_term`, `bind_term`) applied to a case | They are part of the typed vocabulary but a case holds a workflow, not a language overlay; applying them is refused with `TERM_EDIT_UNSUPPORTED` | The workbench tree (WBS 2.1) edits terms | M |
