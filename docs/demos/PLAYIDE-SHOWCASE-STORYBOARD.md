# PlayIDE showcase: storyboard and recording script

The showcase is a short product video for engineers who already know UML. It should make one point: software engineering is more fun, and more accurate, when you work on the system's design and watch it run, instead of typing code and reading pull-request diffs.

It is recorded from the real running product, like every EIJA demo ([ADR-0047](../adr/0047-hardcoded-scripted-demos-not-demo-machine.md)). The script is [`demos/scenarios/playide_showcase.py`](../../demos/scenarios/playide_showcase.py). Each step clicks the real `/play` page of an ephemeral `eija serve` and asserts text the page renders. A beat whose feature has not merged is skipped and listed in the take's manifest. It is never mocked.

## The story in one line

Design it in UML, press play, watch it run, fix it in place, let the AI do the follow-on busywork and check it, review the change as a model, then ship it.

## Beats

The spine (Calvin, 2026-10-09): how easy it is to understand a UML change, your own and the AI's, and what to consider before accepting it. Beat 4 shows your own edit in the Changes view and its ripple as the things to consider; beat 5 shows the AI's change in the same view; beat 6 is what to consider before you accept it. The highlights cut is built on those three beats.

| # | Beat | What the viewer sees | What is real | Status |
|---|---|---|---|---|
| 0 | Title | "Software engineering, played." | A title card | Recorded |
| 1 | The model is the program | The library-loan state machine, then the class, use case, sequence and screen views drawn from the same model | ADR-0151, 0153, 0154. The design check passes | Recorded |
| 2 | Press play | A breakpoint on a state (F9), then Run (F5): seeded users act, the kernel decides every step, and the run pauses on the breakpoint and then on the kernel's refusals, marked on the diagram. Build & run then starts the real app beside the model | ADR-0160 (run bar), ADR-0150 | Recorded |
| 3 | Fix it in place, not in code | State picked in the palette, a click on the diagram, the name typed in the inline editor there. The policy checks it at once as a typed step, and Undo and Redo step it back and forth | ADR-0157, ADR-0174 | Recorded |
| 4 | Watch it ripple | The new state badges every diagram tab it touches and warns that nothing leads into the new state. The class diagram gains the enum literal. The AI's follow-on (a way in) is re-checked by the server and ripples into a new use case and screen | ADR-0158; offline proposer, labelled | Recorded |
| 5 | Let the AI do the busywork | A plain-language request (let librarians renew overdue loans) becomes two typed UML steps. The policy allows them, and the viewer looks at each on the diagram | ADR-0156. The offline phrase reader is labelled on screen | Recorded |
| 6 | Review the change, not the code | The Review tab draws both models on one diagram (new path green, deleted path dashed red). Before each answer the reviewer predicts what the kernel will do. A wrong prediction catches that the AI quietly deleted late returns, the Tests tab shows the late-return scenario failing and paints the broken step on the diagram, and the Sequences tab draws the same scenario as a UML interaction that now ends in the kernel's refusal. The step is rejected, and the review runs again and passes | ADR-0175, ADR-0177, ADR-0195 | Recorded |
| 7 | Prove it, then play again | Build the changed system, run conformance and simulate again. The Laws tab proves every law over every reachable run and names what it never reached. All 7 scenario tests pass again. The checks ring fills to 5 of 5 | ADR-0157, ADR-0158, ADR-0166 | Recorded |
| 8 | Ship it | Verify, approve and apply | Waits on the owner's source review and restamp (issue #80) | Skipped |
| 8a | Share it as UML | The same page opened as `/play?view=review`: read-only diagrams, Permissions and runs, with no editing tools and no chat, for a stakeholder who reads UML | ADR-0172, ADR-0171 | Recorded |
| 8b | Bring your own UML tools | The Import / Export menu (XMI, PlantUML, Mermaid, draw.io). The pack's PlantUML export with one transition added, as if edited elsewhere, is imported: the kernel reads it as one typed edit, the laws hold, and it becomes a plan like any other. A support desk drawn in another tool is then offered as a new system, and the report lists what the kernel could not carry, each with its reason | ADR-0190 | Recorded |
| 8c | Start your own system | Systems, New system: a name, a record class and a three-line sketch of a support desk. The kernel checks the sketch as it is typed, and the page reopens on the new system with every diagram drawn from it | ADR-0185 | Recorded |
| 9 | End card | "Less typing. No diff archaeology." | A title card | Recorded |

Chapter chips number only the beats that are shown, so a skipped beat leaves no gap.

Candidate beat, not yet scripted: on an approvals or claims workflow, the AI's change quietly lets a clerk approve their own claim, and the diagram diff and permission check catch it. It needs a pack with that workflow. Wording to keep: "review the change, not the code" and "the app cannot disobey the model". Wording to avoid: "generate apps from UML", "compliant" and "replaces PRs".

Every beat is filmed on the workbench shell (ADR-0173): outline and inspector on the left, diagram tabs in the middle, chat on the right, and Run, Simulation and the app in a bottom panel. The UML change view (ADR-0176) restyles the review diagram when it merges.

## How it is filmed

- **Camera.** `Scene.zoom(target)` eases the page in on the thing being described, like a screen-recording editor's auto-zoom, and `zoom_out()` returns. It is a CSS transform on the real app, which stays live. Drags and clicks at a point always zoom out first.
- **Chapters.** `Scene.chapter(n, title, card=True)` opens each beat with a short motion-graphic card (number and title over the blurred, still-live app), then leaves a chip in the bottom left that names the beat.
- **Captions** say what is real and what is not. The offline AI is called an offline phrase reader on screen.
- **Finishing.** `python -m demos finish playide_showcase` frames the take on a 1080p stage with rounded corners and a shadow. It is encoded as H.264 MP4. Nothing is cut, sped up or reordered.

## The highlights cut

[`demos/scenarios/playide_highlights.py`](../../demos/scenarios/playide_highlights.py) tells the same story in about two minutes for the README: the model, a breakpoint, an edit in place and its ripple, the AI's change, the catch (a wrong prediction and the late-return sequence diagram ending in a refusal), and the proof. It is its own unedited take of the real product, not a cut of the full one, so it is checked the same way. It runs with `scene.pace = 0.75`, which tightens caption holds and camera motion but never skips an act or an assertion.

## Record it

```bash
pip install -e ".[demos]"
python -m demos run playide_showcase --dry-run   # same clicks and assertions, no video
python -m demos run playide_showcase             # demos/output/playide_showcase.webm and its manifest
python -m demos finish playide_showcase          # demos/output/playide_showcase.mp4
python -m demos run playide_highlights && python -m demos finish playide_highlights
```

When a pending feature merges, replace its `scene.skip(PENDING[...])` line with the real act and record again. The take becomes `recorded` (no skipped beats) only when beat 8 runs, which needs issue #80.
