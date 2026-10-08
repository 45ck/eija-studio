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
| 2 | Press play | Build & run generates the app and checks its cases against the kernel. The app runs beside the model. Simulate sends seeded users through it, and refusals show where they got stuck | ADR-0150, 0152 | Recorded. It will use the run bar (play, pause, step, stop) when that merges |
| 3 | Fix it by dragging, not typing | A state dragged from the palette and a transition added with three choices. The policy checks each as a typed step | ADR-0157 | Recorded |
| 4 | See the ripple | The drawn change badges the class, use case, screen and component views it affects. The AI proposes the follow-on edits and the kernel re-checks them | Thread "Help me work out a plan for a project" | Skipped until it merges |
| 5 | Let the AI do the busywork | A plain-language request becomes typed UML steps. The policy refuses one, the viewer looks at each step, unticks the refused one and keeps the rest | ADR-0156. The offline phrase reader is labelled on screen | Recorded |
| 6 | Review it as a model, not a PR | The change as a UML diff you can run and approve in PlayIDE | Thread "Review changes in PlayIDE, not PRs" | Skipped until it merges |
| 7 | Prove it, then play again | Build the changed system, run conformance and simulate again. The checks ring fills to 4 of 4 | ADR-0157 | Recorded |
| 8 | Ship it | Verify, approve and apply | Waits on the owner's source review and restamp (issue #80) | Skipped |
| 9 | End card | "Less typing. No diff archaeology." | A title card | Recorded |

Chapter chips number only the beats that are shown, so a skipped beat leaves no gap.

Two other threads change how beats look rather than adding beats. "Executable UML on the EIJA engine" may add a run of a sequence or class behaviour to beat 1. "PlayIDE UX, HCI and agentic HCI" may change the layout every beat is filmed on. The script's selectors are updated when either merges.

## How it is filmed

- **Camera.** `Scene.zoom(target)` eases the page in on the thing being described, like a screen-recording editor's auto-zoom, and `zoom_out()` returns. It is a CSS transform on the real app, which stays live. Drags always zoom out first.
- **Chapters.** `Scene.chapter(n, title)` shows a chip at the top centre that names the beat.
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
