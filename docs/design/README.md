# IDE design reference

The [3 October code/model review checkpoint](2026-10-03-CODE-REVIEW-VALIDATION.md) records the implemented review workspace, its bounded observations and remaining acceptance work. The [immutable Code review guide](../engineering/IMMUTABLE-CODE-REVIEW.md) applies to the pinned integration checkout, not the code currently on main. The [earlier UX build rationale](https://github.com/45ck/eija-studio/blob/1f1b07f648890d8e03f81d4269fa479d80a0f46a/docs/design/NEXT-UX-PASS.md) remains a proposal/history record; the checkpoint states what was actually observed.

The [whole-application UX contract](WHOLE-APP-UX.md) defines linked screens and HCI acceptance. The [personas and user stories](WHOLE-APP-STORIES.md) turn those screens into tasks with observable outcomes. These documents guide implementation; their planned journeys are not claims of completed validation.

The [current implementation and HCI ledger](IMPLEMENTATION-STATUS.md) maps all four personas, fifteen stories and ten screens to scoped observations and remaining work, including the exact public-clone preview. It preserves the density failure, latency gap and unmeasured human benefit.

## Interactive whole-app reference

The [interactive design reference](interactive/README.md) makes the proposed **ten-surface** workspace inspectable, including selected changes, source/evidence returns, edit preview, history and recovery. It follows the [project mission](../engineering/MISSION.md), [whole-app UX contract](WHOLE-APP-UX.md), [personas and stories](WHOLE-APP-STORIES.md) and [HCI evaluation protocol](../hci/README.md). The four personas—domain engineer/modeller, AI-assisted engineer, reviewer/technical lead and agent-factory operator—remain design hypotheses, not interviewed or validated segments.

All cases, models, source excerpts, witnesses, runtime outcomes and factory states are **prepared illustrations**. The reference has no backend, model persistence, live agent, source transformation or executable factory. State-selection controls expose the proposed interactions; they do not execute product commands or produce evidence. Read the [state/interaction handoff](interactive/HANDOFF.md) and [publication asset manifest](interactive/asset-manifest.json) and [original frozen QA5 manifest](assets/interactive-20261003/frozen-design5-manifest.json) for exact scope, retained identities and remaining evaluation work. An interaction check on this fixture does not accept a product story, HCI budget, accessibility conformance or human-comprehension claim.

The [3 October interactive design review](2026-10-03-INTERACTIVE-DESIGN-REVIEW.md) records ten passing browser groups on the exact frozen reference, actual design captures, retained defects and remaining axe/legibility limits. It is separate from the working product's validation. The publication package trims trailing spaces from two derived log copies and updates provenance documentation; runtime HTML/JS/CSS/assets remain byte-identical to QA5, whose original identity and receipts are preserved.

The diagrams reuse the existing EIJA comparison, canvas and review components plus pinned Dagre/graphlib **byte for byte**, with their copied licenses and provenance. All nine captured component/license files also match [immutable implementation ca95f46](https://github.com/45ck/eija-studio/tree/ca95f468206fec706f7a274788faf872877ac4a1), so their clean upstream bytes are available. The frozen manifest preserves its original capture HEAD and dirty-source provenance; this later match does not rewrite that history. The separately authored `design.js` manages prepared fixtures and local presentation state only; no new diff, graph-layout, policy, solver or orchestration engine is introduced. GitHub shows the HTML source; the reference README describes local serving from the portable `docs/design/interactive/` folder. Actual product observations remain in the implementation ledger and dated checkpoints above.

## Generated visual concepts

![EIJA Studio IDE concept](eija-ide-concept-v1.png)

This generated concept sets a visual quality target for the working IDE. It is not a screenshot, test result, executable model, or claim of shipped functionality. Diagram arrows, counts, example hashes, and status labels are illustrative; the running application must derive these from its actual model and evidence.

The target is a productive desktop workspace: compact project chrome, searchable explorer, readable semantic canvas, contextual inspector, source navigation, and persistent evidence/history/intent panels. Independent scrolling, keyboard navigation, resizing, empty/error states, and trustworthy feedback matter as much as the still image. Every visible product control must work or explain its unavailable state.

Generated on 2026-10-02 with the built-in imagegen tool. The prompt is recorded in [eija-ide-concept-v1.prompt.md](eija-ide-concept-v1.prompt.md). This is a design asset; showcase videos and proof of feasibility must use the real application.

## Connected concept screens

| Screen | Design purpose | Prompt |
|---|---|---|
| [Visual change review](eija-visual-change-concept-v1.png) | Compare baseline and candidate concepts before inspecting source; keep additions, removals and coverage gaps legible | [Generation prompt](eija-visual-change-concept-v1.prompt.md) |
| [Evidence and runtime investigation](eija-evidence-runtime-concept-v1.png) | Explain a refused change, navigate a counterexample and inspect evidence scope | [Generation prompt](eija-evidence-runtime-concept-v1.prompt.md) |
| [Parallel agent coordination](eija-agent-coordination-concept-v1.png) | Inspect potential overlap and a combined change; this capability remains planned | [Generation prompt](eija-agent-coordination-concept-v1.prompt.md) |

All four images are generated visual references, not executable specifications. Example source, counts, arrows, agent activity and check results are illustrative. In particular, the evidence illustration does not define an authority policy or suggest changing permissions to pass a check. Implementation derives behavior and authority from the existing kernel and uses real observations for status. The design contract, rather than incidental generated details, defines the acceptance criteria.
