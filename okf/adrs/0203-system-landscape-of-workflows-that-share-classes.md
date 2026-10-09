---
type: Architecture Decision Record
title: 'ADR-0203: A system landscape of the workflows that share classes'
description: 'PlayIDE edits one workflow at a time: one state machine moving one record class, with its class diagram, use cases, screens and laws.'
resource: repo://docs/adr/0203-system-landscape-of-workflows-that-share-classes.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0203-system-landscape-of-workflows-that-share-classes.md
  title: 0203-system-landscape-of-workflows-that-share-classes.md
  hash_method: lf-sha256-v1
  sha256: 7d63932322ee0ebcb8163d9e0836be097328c72eb417e57abc95b21554090bf1
notes_baseline: 60f5d496537da6243715887b16a4b2addf1ae7bd053f16d65cc0c29fa67d4a52
---

# ADR-0203: A system landscape of the workflows that share classes

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted for workflows in one folder |
| Date | 2026-10-09 |
| Lane | PlayIDE (owner direction, 9 October 2026: refine how software and computers are designed in PlayIDE, so system design is credible for a startup or an enterprise architect) |
| Source | `repo://docs/adr/0203-system-landscape-of-workflows-that-share-classes.md` |

## Decision outcome (verbatim)

> Chosen option: `application/landscape.py`, `landscape(focus, systems, unreadable)`. The route is `POST /api/play/landscape`. The page shows it as the **System** lens of the Components tab (`play-landscape.js`).
>
> * **Which workflows.** These are the packs beside the open one (`packs/` for shipped packs, the systems home for your own) that the kernel's pack check accepts, reachable from the open workflow through classes their class diagrams name. Packs that share nothing are listed as *Not in this system*. Packs the pack check refused are listed as *Not read*, so nothing is dropped silently. The open workflow is the model shown, including a previewed plan and a chat-grown class diagram (ADR-0202).
> * **Ownership.** The workflow whose record a class is owns that class. Another workflow that names the class has a «use» dependency on the owner, labelled with the class. A class that two workflows name and neither moves is drawn as a «class» on its own, marked *shared, no owner*.
> * **What each workflow provides.** Its actions are drawn as a provided interface (lollipop). Each action lists the roles its transitions give it to. Roles with one name are one actor, which has a «use» dependency on each workflow where it holds an action. The workflow's notification effects are what it publishes (the outbox of the built app).
> * **Findings.** Each finding names its classes, attributes and workflows. There are two severities: `warning` (*Disagrees*) and `consider` (*To consider*).
>   * `CLASS_COPIES_DIFFER` (warning): an attribute declared two ways (type, length, choices, required) in two copies of one class.
>   * `ATTRIBUTE_NOT_ON_OWNER` (warning): a workflow adds an attribute to a class another workflow owns.
>   * `RECORD_MOVED_TWICE` (warning): two state machines move the same record class.
>   * `CLASS_HAS_NO_OWNER` (consider): a shared class that no workflow moves.
>   * `RECIPIENT_IS_NOT_AN_ACTOR` (consider): a notification to a recipient that is no role in the system.
> * A new shipped pack, `library-fines` (Fine: Issued, Disputed, Paid, Waived), names `Loan` and `Member`. Opening `library-loan` and choosing **System** shows two workflows, three actors, fines using loan through `Loan`, and `Member` shared with no owner. `Member.card` is 20 characters in one copy and 32 in the other. The pack has its own laws and scenarios, and every pack-wide gate runs on it.

## Sections

* Context and problem statement
* Decision drivers
* What existing tools do
* Considered options
* Decision outcome
* OSS check (required for any custom module)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0093: Consistency and synchronisation between views: one source per fact, one-way generation, keyed merge](/adrs/0093-weave-consistency-sync.md) - EIJA keeps many views of one system: code, workflow model, diagrams, OKF pages, term registry, UI sidecar, requirements, links, ledger, exports.
* [ADR-0155: Component diagrams read from the generated code](/adrs/0155-component-diagrams-read-from-the-generated-code.md) - The owner's roadmap asks for component diagrams after use cases and screens.
* [ADR-0202: Grow the class diagram in chat](/adrs/0202-grow-the-class-diagram-in-chat.md) - ADR-0201 let a system started from a sketch grow its state machine round after round in chat.

## Referenced by

* [ADR-0204: The ripple reaches the other workflows of the system](/adrs/0204-the-ripple-reaches-the-other-workflows-of-the-system.md) - The ripple (ADR-0158) shows what a change does to every diagram of one workflow.
* [ADR-0206: A deployment view read from the built app's files](/adrs/0206-a-deployment-view-read-from-the-built-apps-files.md) - PlayIDE had no deployment view.
<!-- okf:generated:end links -->
