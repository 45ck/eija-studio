# PlayIDE greenfield: storyboard and recording script

The showcase changes a system that already exists. This cut answers the other question, put by Calvin on 2026-10-09: what about a new app, built fast with an AI and changed again and again? He described it this way: "it should start off like loveable or replit a box to type in than it makes all uml and u edit it … or drag it like drawio … usually its a mix of both … if something is missing it lets you know".

So the cut starts from one description of a coffee shop and gets every model and view. It then builds the app in five rounds that mix chat asks with a state drawn by hand, and it reads What's missing after each round.

It is recorded from the real running product, like every EIJA demo ([ADR-0047](../adr/0047-hardcoded-scripted-demos-not-demo-machine.md)). The script is [`demos/scenarios/playide_greenfield.py`](../../demos/scenarios/playide_greenfield.py). What it relies on is set out in [ADR-0201](../adr/0201-build-a-new-system-in-chat-round-after-round.md), [ADR-0202](../adr/0202-grow-the-class-diagram-in-chat.md) and [ADR-0216](../adr/0216-describe-your-app-and-whats-missing.md).

Each step clicks the real `/play` page of an ephemeral `eija serve` and asserts text the page renders. The describer (`offline-describe-fixture-v1`) and the chat's proposer (`offline-plan-fixture-v1`) are offline readers, and the video says so.

## The story in one line

Describe it in one box, get every view, then ask and drag. Read each round in UML along with what is still missing, and run the app.

## Beats

| # | Beat | What the viewer sees | What is real |
|---|---|---|---|
| 0 | Title | "Greenfield, in UML" | A title card |
| 1 | Describe it | "＋ New" opens the Describe box. A coffee shop is described in two sentences. Before anything is created, the form lists every view: state machine, class diagram, use cases, screens, 3 tests recorded by the kernel, and no laws. It also lists what the offline reader assumed. | ADR-0216 |
| 2 | Every model and view | The state machine with Barista and Customer. The class diagram with size and notes. The recorded tests as sequence diagrams. What's missing: no laws yet, because laws are yours to set. | ADR-0216, ADR-0153, ADR-0195 |
| 3 | Round 1: a new requirement | In chat, customers pay before brewing. The plan adds Paid and Pay, and Start moves. What's missing follows the plan: no test takes Pay, and the recorded way to Collected now fails because paying comes first. | ADR-0201 |
| 4 | Round 2: draw it, then ask | A state is dragged onto the diagram and named Refunded. What's missing says Refunded cannot be reached. A chat ask adds Refund into it, and the plan shows You and AI steps together. | ADR-0174, ADR-0201, ADR-0216 |
| 5 | Round 3: the form | "add field pickupTime as text then make size required". The class diagram marks pickupTime with +. | ADR-0202 |
| 6 | Round 4: rename, and a new role | Ready becomes AwaitingPickup, and a manager may cancel. The verdict names what is new. The Changes view shows this round alone. | ADR-0201, ADR-0176 |
| 7 | Round 5: change your mind | "remove state Cancelled" removes its transition first. What's missing reports that the recorded cancelling test fails too. The Changes view shows every round together. | ADR-0201, ADR-0216 |
| 8 | Run it | Build & run passes every conformance case. Simulate runs, and Save keeps every round. | ADR-0150, ADR-0152, ADR-0185 |
| 9 | End card | "Vibe-code it. Then read it." The describer and proposer are offline, and nothing is applied. | A title card |

## Not shown, and why

* **Making the rounds the model in force.** A plan, however many rounds it has, is a draft. How a chat plan becomes a change case is issue #89, and verify, approve and apply wait on issue #80.
* **Writing a law.** The cut shows that none is generated. Writing one is the Laws tab's job (ADR-0177).
* **A live describer.** The owner chose an offline proposer. A live one would be another adapter behind the same port.

## Record it

```
python -m demos run playide_greenfield --dry-run   # the same clicks and assertions, no video
python -m demos run playide_greenfield             # demos/output/playide_greenfield.webm and its manifest
python -m demos finish playide_greenfield          # 1080p MP4 on the stage, demos/output/playide_greenfield.mp4
python -m demos registry --write
```

In a cloud container, first link Playwright's Chromium to the path where the recorder looks for Chrome: `/opt/pw-browsers/chromium-1194/chrome-linux/chrome` to `/opt/google/chrome/chrome`.
