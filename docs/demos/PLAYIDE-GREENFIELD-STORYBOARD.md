# PlayIDE greenfield: storyboard and recording script

The showcase changes a system that already exists. This cut answers the other question (Calvin, 2026-10-09): what about a new app, built fast with an AI and changed again and again? It starts from three lines and builds a coffee-order system, form included, in six chat asks, reading each round as it goes.

It is recorded from the real running product, like every EIJA demo ([ADR-0047](../adr/0047-hardcoded-scripted-demos-not-demo-machine.md)). The script is [`demos/scenarios/playide_greenfield.py`](../../demos/scenarios/playide_greenfield.py); what it relies on is [ADR-0201](../adr/0201-build-a-new-system-in-chat-round-after-round.md) and [ADR-0202](../adr/0202-grow-the-class-diagram-in-chat.md). Each step clicks the real `/play` page of an ephemeral `eija serve` and asserts text the page renders. The chat's proposer is the offline phrase reader (`offline-plan-fixture-v1`), and the video says so.

## The story in one line

Sketch it in three lines, ask for one thing at a time, read each round in UML with what to consider, change your mind, and run the app after every round.

## Beats

| # | Beat | What the viewer sees | What is real |
|---|---|---|---|
| 0 | Title | "Greenfield, in UML" | A title card |
| 1 | Start from three lines | Systems, New system: Coffee orders, record class Order, three sketch lines. The kernel checks the sketch as it is typed, and the page reopens on the new system | ADR-0185 |
| 2 | Round 1: a feature | "add Cancel from Placed to Cancelled for Customer" becomes two steps: Add state Cancelled, then Add Cancel (new action Cancel). Previewed on the diagram | ADR-0201: a new state as its own step, a new action declared as a sketch declares one |
| 3 | Round 2: the record's fields | "add field size as choice Small, Medium, Large required then add field notes". The verdict says Order gains size and notes; the class diagram marks the new rows with + | ADR-0202: data-model steps on a draft data model, checked by its own contract |
| 4 | Round 3: a new requirement | Customers pay before brewing. The plan card says 3 rounds and heads each with what was asked. The Changes view's Round 3 shows only this round: Paid and Pay added, Start moved with its old route as a ghost, and To consider for this round | ADR-0201 (`since`), ADR-0176 |
| 5 | Rounds 4 and 5 | A rename that every transition follows; then a manager may cancel too, a new role with a test user, and the verdict names what is new. The Permissions tab shows who can do what | ADR-0201, ADR-0171 |
| 6 | Round 6: change your mind | "remove state Cancelled" removes the Cancel transition first, as its own step. Round 6 alone shows the ghosts; All 6 rounds shows the whole system against the sketch | ADR-0201, ADR-0176 |
| 7 | Run it, every round | Build & run, with size and notes on the app's form: every conformance case matches the kernel and the app runs beside the model. Simulate. Save keeps every round with its ask | ADR-0150, ADR-0152, ADR-0185 |
| 8 | End card | "Vibe-code it. Then read it." Offline proposer; nothing applied | A title card |

## Not shown, and why

* **Making the rounds the model in force.** A plan, however many rounds, is a draft. How a chat plan becomes a change case is issue #89, and verify, approve and apply wait on issue #80.
* **New classes and associations.** Chat adds, removes and requires attributes of a class; it cannot add a class or an association yet (ADR-0202).

## Record it

```
python -m demos run playide_greenfield --dry-run   # the same clicks and assertions, no video
python -m demos run playide_greenfield             # demos/output/playide_greenfield.webm and its manifest
python -m demos finish playide_greenfield          # 1080p MP4 on the stage, demos/output/playide_greenfield.mp4
python -m demos registry --write
```

In a cloud container, first link Playwright's Chromium where the recorder looks for Chrome: `/opt/pw-browsers/chromium-1194/chrome-linux/chrome` to `/opt/google/chrome/chrome`.
