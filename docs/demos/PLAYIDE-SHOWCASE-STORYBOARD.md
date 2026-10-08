# PlayIDE showcase: storyboard and recording script

The showcase is a short product video for engineers who already know UML. It should make one point: software engineering is more fun, and more accurate, when you work on the system's design and watch it run, instead of typing code and reading pull-request diffs.

It is recorded from the real running product, like every EIJA demo ([ADR-0047](../adr/0047-hardcoded-scripted-demos-not-demo-machine.md)). The script is [`demos/scenarios/playide_showcase.py`](../../demos/scenarios/playide_showcase.py). Each step clicks the real `/play` page of an ephemeral `eija serve` and asserts text the page renders. A beat whose feature has not merged is skipped and listed in the take's manifest. It is never mocked.

## The story in one line

Design it in UML, press play, watch it run, fix it by dragging, let the AI do the follow-on busywork and check it, review the change as a model, then ship it.

## Beats

| # | Beat | What the viewer sees | What is real | Status |
|---|---|---|---|---|
| 0 | Title | "Software engineering, played." | A title card | Recorded |
| 1 | The model is the program | The library-loan state machine, then the class, use case and screen views drawn from the same model | ADR-0151, 0153, 0154. The design check passes | Recorded |
| 2 | Press play | A breakpoint on a state (F9), then Run (F5): seeded users act, the kernel decides every step, and the run pauses on the breakpoint and then on the kernel's refusals, marked on the diagram. Build & run then starts the real app beside the model | ADR-0160 (run bar), ADR-0150 | Recorded |
| 3 | Fix it by dragging, not typing | A state dragged from the palette. The policy checks it at once as a typed step | ADR-0157 | Recorded |
| 4 | Watch it ripple | The drag badges every diagram tab it touches and warns that nothing leads into the new state. The class diagram gains the enum literal. The AI's follow-on (a way in) is re-checked by the server and ripples into a new use case and screen | ADR-0158; offline proposer, labelled | Recorded |
| 5 | Let the AI do the busywork | A plain-language request becomes typed UML steps. The policy refuses one, the viewer looks at each step, unticks the refused one and keeps the rest | ADR-0156. The offline phrase reader is labelled on screen | Recorded |
| 6 | Review it as a model, not a PR | The change as a UML diff you can run and approve in PlayIDE | Thread "Review changes in PlayIDE, not PRs". The owner suggested a short moment where a non-technical stakeholder reads the same UML diff (not a plain-language translation) | Skipped until it merges |
| 7 | Prove it, then play again | Build the changed system, run conformance and simulate again. The checks ring fills to 4 of 4 | ADR-0157 | Recorded |
| 8 | Ship it | Verify, approve and apply | Waits on the owner's source review and restamp (issue #80) | Skipped |
| 9 | End card | "Less typing. No diff archaeology." | A title card | Recorded |

Chapter chips number only the beats that are shown, so a skipped beat leaves no gap.

Candidate beat, not yet scripted: on an approvals or claims workflow, the AI's change quietly lets a clerk approve their own claim, and the diagram diff and permission check catch it. It needs a pack with that workflow. Wording to keep: "review the change, not the code" and "the app cannot disobey the model". Wording to avoid: "generate apps from UML", "compliant" and "replaces PRs".

Two other threads change how beats look rather than adding beats. "Executable UML on the EIJA engine" may add a run of a sequence or class behaviour to beat 1. "PlayIDE UX, HCI and agentic HCI" may change the layout every beat is filmed on. The script's selectors are updated when either merges.

## How it is filmed

- **Camera.** `Scene.zoom(target)` eases the page in on the thing being described, like a screen-recording editor's auto-zoom, and `zoom_out()` returns. It is a CSS transform on the real app, which stays live. Drags always zoom out first.
- **Chapters.** `Scene.chapter(n, title)` shows a chip in the bottom left that names the beat.
- **Captions** say what is real and what is not. The offline AI is called an offline phrase reader on screen.
- **Finishing.** `python -m demos finish playide_showcase` frames the take on a 1080p stage with rounded corners and a shadow. It is encoded as H.264 MP4. Nothing is cut, sped up or reordered.

## Record it

```bash
pip install -e ".[demos]"
python -m demos run playide_showcase --dry-run   # same clicks and assertions, no video
python -m demos run playide_showcase             # demos/output/playide_showcase.webm and its manifest
python -m demos finish playide_showcase          # demos/output/playide_showcase.mp4
```

When a pending feature merges, replace its `scene.skip(PENDING[...])` line with the real act and record again. The take becomes `recorded` (no skipped beats) only when beat 8 runs, which needs issue #80.
