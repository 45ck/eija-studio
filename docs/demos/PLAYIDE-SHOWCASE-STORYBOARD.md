# PlayIDE showcase: storyboard and recording script

The showcase is a short product video for engineers who already know UML. It should make one point: software engineering is more fun, and more accurate, when you work on the system's design and watch it run, instead of typing code and reading pull-request diffs.

It is recorded from the real running product, like every EIJA demo ([ADR-0047](../adr/0047-hardcoded-scripted-demos-not-demo-machine.md)). The script is [`demos/scenarios/playide_showcase.py`](../../demos/scenarios/playide_showcase.py). Each step clicks the real `/play` page of an ephemeral `eija serve` and asserts text the page renders. A beat whose feature has not merged is skipped and listed in the take's manifest. It is never mocked.

## The story in one line

Design the whole system in UML: the people, the AI agents and the software. Press play, read every change before you accept it, yours and the AI's, and let the kernel prove it.

## Beats (v4, the flagship)

The spine stays (Calvin, 2026-10-09 02:50): how easy it is to understand a UML change, your own and the AI's, and what to consider before accepting it. v4 widens what is designed (Calvin, 2026-10-09 06:03 and 06:08): how humans, computers, agents and software are all designed in one model, while staying fun and gamified and tied to real checks. Each beat comes from a thread that shipped it, and each lists the exact clicks the script makes.

| # | Beat | What the viewer sees | Source | Status |
|---|---|---|---|---|
| 0 | Title | "Design the whole system. Then play it." | Title card | Scripted |
| 1 | The model is the program | The library-loan state machine, then the class, use case, sequence and screen views drawn from the same model | ADR-0151, 0153, 0154 | Recorded in v3 |
| 2 | Press play | A breakpoint on Overdue, then Run: seeded users act, the kernel decides every step, and each decided step moves along its transition as a dot, green through and red stopped with a cross | ADR-0160; traffic from #162 (ADR-0208) | Traffic from #162 |
| 3 | Your change, at a glance | Drop a state where you want it, name it inline. The Changes view tags it You, and To consider lists the warning, the laws, the other diagrams and the tests it adds | ADR-0157, #128 | Recorded in v3 |
| 4 | The AI's change, at a glance | A plain request becomes typed UML steps. The same view tags each AI, keeps the removed arrow as a ghost, and To consider says it breaks the late-return sequence | ADR-0156, #128 | Recorded in v3 |
| 5 | What to consider before you accept | A wrong prediction catches the deleted late return. Tests paints the broken step, Sequences ends in the kernel's refusal. Untick the step, and the review passes | ADR-0175, 0177, 0195 | Recorded in v3 |
| 6 | Prove it, then play again | What's missing says no test takes the AI's new Renew, so record one in Tests (CheckOut, MarkOverdue, Renew, each step tried in the kernel). Then build and run, Simulate replayed as traffic on the state machine, every law proved, all 8 tests pass, and the ring turns green once: "Every check passes" | ADR-0157, 0158, 0166; ring moments from #162 | Ring moments from #162 |
| 7 | People: who sees what | Screens, See the app as Clerk: "A Clerk sees 2 of 7 screens", the rest struck through. The generated screens are checked for accessibility (WCAG 2.2 AA): 8 of 9 pass, and the AI's new Renew screen needs field labels. The Librarian actor lists what the kernel lets it do ("assigned only" where a guard narrows it) and Run as opens the built app acting as that person | #160 (ADR-0215), #180 | Scripted |
| 8 | Software: the whole system | Components, System lens: "4 workflows · 12 actors · 2 disagree". The shared Member class is marked where two class diagrams disagree. Then Deployment: a UML deployment diagram read from the built app (browser, Python process with its live address and the conformance cases it passes, SQLite file, routes); select the process and download its API contract (OpenAPI 3.1), written from the model | #155 (ADR-0203), #168, #188, #192 (ADR-0207) | Scripted |
| 9 | Share it as UML | `/play?view=review`: read-only diagrams, Permissions and runs for a stakeholder who reads UML | ADR-0172 | Recorded in v3 |
| 10 | Bring your own UML tools | PlantUML edited elsewhere comes back as one typed edit with the laws holding; a support desk from another tool becomes a new system with a report of what was not carried | ADR-0190 | Recorded in v3 |
| 11 | AI agents, timers and systems, in real sectors | Systems, New system: the templates (building permit, card payment, parcel delivery, SaaS subscription, specialist referral, refund desk). Open Refund desk: «agent», «timer» and «system» actors beside the people. Ask for a hand-off to a supervisor and slip in `allow SupportAgent to ApproveRefund`: three person-in-the-loop laws refuse the plan. Untick that step and the ring says "Caught it"; the hand-off alone is allowed. Sequences draws the test where the agent's ApproveRefund() call is answered "refused: ROLE_DENIED". Simulate: what people, agents, timers and systems tried, and what the kernel refused | #159, #161 (ADR-0210), #172 | Scripted |
| 12 | No record gets stuck | Systems, New system, Building permit. Ask `add state OnHold after InReview then add HoldApplication from InReview to OnHold for PlanReviewer`: the plan is refused (APPLICATION_STUCK), because an application on hold could never be certified, refused, withdrawn or lapsed. Laws lists "Every application can still be finished", proved over every run | #191 (ADR-0221) | Scripted |
| 13 | Start your own | New system, Describe your app: "A coffee shop app. Customers order drinks, baristas make them, then customers collect them…". Before anything is made, every view it will have, checked by the kernel, with 3 tests recorded. Create: the coffee shop runs, and "What's missing" lists what to do next (no laws yet: those are yours to write) | #176 (ADR-0216) | Scripted |
| 14 | Ship it | Verify, approve and apply | Issue #80 | Placeholder card |
| 15 | End card | "Design the people, the agents and the software. Then play it." | Title card | Scripted |

Chapter chips number only the beats that are shown, so a skipped beat leaves no gap. The AI is the offline phrase reader (`offline-plan-fixture-v1`) throughout, and every chat card says so on screen. Beats 11, 12 and 13 open another system from the Systems dialog, so the page reloads on it; the systems are throwaway (`EIJA_SYSTEMS` is a temporary folder).

Wording to keep: "review the change, not the code" and "the app cannot disobey the model". Wording to avoid: "generate apps from UML", "compliant" and "replaces PRs".

Every beat is filmed on the workbench shell (ADR-0173): outline and inspector on the left, diagram tabs in the middle, chat on the right, and Run, Simulation and the app in a bottom panel.

## The highlights cut (v4)

About two and a half minutes, its own unedited take: the title, your change at a glance, the AI's change and the catch, the proof as traffic ending in "Every check passes", people (see the app as a Clerk), and an agent stopped by a law on Refund desk and caught. It runs at `scene.pace = 0.75`.

## How it is filmed

- **Camera.** `Scene.zoom(target)` eases the page in on the thing being described, like a screen-recording editor's auto-zoom, and `zoom_out()` returns. It is a CSS transform on the real app, which stays live. Drags and clicks at a point always zoom out first.
- **Chapters.** `Scene.chapter(n, title, card=True)` opens each beat with a short motion-graphic card (number and title over the blurred, still-live app), then leaves a chip in the bottom left that names the beat.
- **Captions** say what is real and what is not. The offline AI is called an offline phrase reader on screen.
- **Finishing.** `python -m demos finish playide_showcase` frames the take on a 1080p stage with rounded corners and a shadow. It is encoded as H.264 MP4. Nothing is cut, sped up or reordered.

The README embeds the highlights cut as [`assets/playide-showcase/playide-highlights.mp4`](assets/playide-showcase/playide-highlights.mp4), a 1280-wide H.264 re-encode (`ffmpeg -vf scale=1280:-2 -crf 30 -an -movflags +faststart`) of the finished take, with a poster frame from the "Your change, at a glance" chapter. The full cut sits below it the same way, as [`assets/playide-showcase/playide-showcase.mp4`](assets/playide-showcase/playide-showcase.mp4) with a poster from "Software: the whole system". Re-encode the video and poster after each new take of either cut.

## Record it

```bash
pip install -e ".[demos]"
python -m demos run playide_showcase --dry-run   # same clicks and assertions, no video
python -m demos run playide_showcase             # demos/output/playide_showcase.webm and its manifest
python -m demos finish playide_showcase          # demos/output/playide_showcase.mp4
python -m demos run playide_highlights && python -m demos finish playide_highlights
```

When a pending feature merges, replace its `scene.skip(PENDING[...])` line with the real act and record again. The take becomes `recorded` (no skipped beats) only when the ship beat (14) runs, which needs issue #80.
