# What PlayIDE's AI can do, and what it can't (17 November 2026)

This is a scripted recording of the real PlayIDE page (`/play`). Every click is a real browser action against a real `eija serve`, and every step asserts text the page actually rendered. `python -m demos run playide_ai_can_and_cannot --dry-run` repeats the same clicks and assertions without video. The take is **PASS**, with no act skipped. It runs 4 minutes 8 seconds, recorded from `main` at `c80fb05`.

[Watch the README copy](assets/playide-ai-20261117/playide-ai-can-and-cannot.mp4) (1280 wide).

## The AI in this video

There is no live model. The chat's proposer is the offline phrase reader (`offline-plan-fixture-v1`) and the new-system describer is the offline shape reader (`offline-describe-fixture-v1`). The first title card and the first chat caption say so. A live provider exists behind an explicit opt-in ([ADR-0230](../adr/0230-opt-in-live-plan-mode-and-agent-plan-check.md)), but demos never use it.

## What the run shows

| Chapter | What is real |
|---|---|
| Who does what | The strip beside the chat: the AI proposes steps, you check and try them, the owner approves and applies in the review workbench. |
| Can: turn plain words into UML steps | On the library loan, "add Renew from Overdue to OnLoan for Librarian then remove transition ReturnLate" becomes two typed steps the policy allows, drawn on the state machine and tagged AI. |
| Can't: slip a breaking change past you | To consider says the result breaks the late-return sequence. In Review the person predicts "yes, a librarian can still return an overdue loan", and the kernel says no. The late-return sequence diagram ends in the kernel's refusal. Rejecting that step leaves no high-risk change. |
| Can't: guess what you meant | A vague ask ("make returns faster and add some fraud checks") is refused with how to ask instead. An unknown name (`remove state Lost`) is refused. A value limit ("only if the fine is under 50") is refused with `PLAN_LIMIT_UNSUPPORTED`, because dropping it would change the model in a way nobody asked for. |
| Can't: write your laws | "Add a law that a loan is never deleted" is not a plan step. The Laws tab shows each law the person wrote holding on every run the kernel allows. |
| Prove the app still matches | Build & run: every conformance case matches the kernel. Simulate replays users as traffic, and the kernel refuses some. |
| Can: draft a whole system from one sentence | A coffee shop described in one box: the describer's check before anything is made, tests recorded by the kernel, the state machine and the class diagram with the named fields. What's missing says there are no laws, because none are generated. |
| Can't: let an AI agent break a law | On the refund desk template, asking to let the support agent (an AI agent actor) approve refunds is refused: only a person approves a refund. Unticking that step is caught, and the hand-off alone is allowed. |
| Can't: approve or apply | "Source review required" in the header. Nothing proposed is in force; approving and applying stay with the owner. |

## Not shown

Nothing is approved or applied; that waits on the owner's source review and restamp (issue #80). The live provider is not shown. The offline readers only know their phrases and shapes, so the refusals here show the offline reader's limits as well as the kernel's; a live model would read more phrasings, and the kernel, the laws and the owner gate would still decide.

## Reproduce the recording

```bash
pip install -e ".[demos]"
python -m demos run playide_ai_can_and_cannot --dry-run   # same clicks and assertions, no video
python -m demos run playide_ai_can_and_cannot             # demos/output/playide_ai_can_and_cannot.webm and its manifest
python -m demos finish playide_ai_can_and_cannot          # demos/output/playide_ai_can_and_cannot.mp4 (1080p stage)
ffmpeg -i demos/output/playide_ai_can_and_cannot.mp4 -vf scale=1280:-2 -crf 30 -an -movflags +faststart \
  docs/demos/assets/playide-ai-20261117/playide-ai-can-and-cannot.mp4
```

The poster is the frame at 0:56 (the reviewer is asked to predict before the kernel answers).
