# ADR-0203: Describe your app, and what's missing

* Status: accepted
* Date: 2026-10-09
* Lane: PlayIDE. Owner, 9 October 2026: "it should start off like lovable or replit a box to type in than it makes all uml and u edit it etc or descirbe what needs to be changed or drag it like drawio and edit it etc. usually its a mix of both. and you work across all models and views to get it all ready, if something is missing it lets you know etc".

## Context and problem statement

Until now a new system started from three sketch lines, a template or a UML file (ADR-0185, ADR-0190), and then grew in chat (ADR-0201, ADR-0202). That is a modeller's start. People building an app with an AI expect something different: one box where they say what the app is for, and every part of it made at once. After that they change it by asking or by dragging, usually both.

PlayIDE also never said what a system still lacked. Each tab had its own checks, so you had to visit every tab to find out whether the system was ready.

## Decision drivers

* The AI stays offline and labelled as such (owner, 8 October 2026). The describer is a fixed reader, and the page says so.
* A description is untrusted. The kernel's pack check, the data model's contract and the kernel's own runs decide everything, exactly as they do for a sketch.
* Laws are protected policy. An AI must not choose them, so they are never generated.
* Test cases must say what the kernel does, not what a reader guessed.
* "What's missing" restates checks the IDE already runs. It adds no second set of rules.
* Domain words stay out of generic code (the vocabulary gate). The app shapes are data.

## What existing tools do

| Tool | How an app starts | What PlayIDE takes from it |
|---|---|---|
| Lovable, Replit Agent, bolt.new, v0 (proprietary) | One prompt box; the whole app is generated, then changed in chat | One box first, every view made from it, then chat or direct edits |
| Stately "Generate with AI" (proprietary) | A statechart from a prompt | The state machine is part of what is made, in the diagram's own notation |
| VS Code Problems panel, Xcode issue navigator | One list of every problem across files, each opening where it is fixed | What's missing: one list across every view, each row opening that view |

No library was adopted. The generator is a port with an offline adapter, and the list reads PlayIDE's existing checks.

## Considered options

* **An offline describer behind an application port; documents built as a sketch's are; tests recorded by the kernel; laws left to the person; one "What's missing" list across every view** (chosen).
* **Ask a live model.** This is the closest to Lovable, but the owner chose an offline proposer, and it would spend money on every keystroke of the preview.
* **Generate laws too.** The system would be complete on paper, but an AI would be setting protected policy.
* **A readiness score instead of a list.** A number is a compact summary, but it does not say what to do next.

## Decision outcome

Chosen option.

* **Describe it.** The New system dialog opens on "Describe your app" (also the "＋ New" button, and `/play?new=describe`).
  * The description goes to a `SystemDescriber` (`application/ports.py`). The offline adapter, `adapters/system_describer.py`, picks the app shape whose keywords the description uses most. The shapes are data in `describe-shapes.json`, beside the shipped packs: orders, tickets, bookings, approvals, loans, hiring, deliveries, publishing and bugs, or a plain one.
  * Role nouns from the description rename the shape's roles. "With …" and "has …" lists become fields: a name with "(a, b, c)" is a choice, price-like words are numbers, date-like words are dates, and anything else is text.
  * The adapter says what it read and assumed, and that it is a fixed shape, not a live model.
* **Every model and view.** `application/describe_system.describe_documents` builds the documents:
  * `pack.json` and `data.json` exactly as a sketch's (`sketch_documents`), with the fields added to the record class;
  * `scenarios.json`, with one test per end state (the shortest way there) and one refusal (the first step taken by a role that may not take it), each step written as what the kernel did (`record_steps`).

  Every document passes the same checks as any new system (`checked_documents`). Use cases, screens, sequences, components and permissions are derived from these documents, as for any system. Before anything is created, the form says what each view will have. Nothing is written until Create and open.
* **No laws are generated.** What's missing says there are none, gives an example from the model ("Collected is final") and says laws are the person's to set.
* **What's missing.** `POST /api/play/ready` returns a row per view: state machine, class diagram, use cases and permissions, screens, tests and sequences, and laws. Each row is either ready or lists what is missing or wrong, with where to fix it. It reads the work in progress: the plan's accepted steps when the policy allows them, previewed or not. The checks behind the rows are:
  * a state nothing reaches;
  * a record with only a title;
  * a role that takes no action;
  * the screens' design check;
  * no tests, a failing test, or an action no test takes;
  * no laws, or a law the kernel finds broken or cannot decide.

  The panel sits at the top of the left sidebar, and each row opens its view.

### Consequences

* Good: a new app starts from one sentence, with every view populated and checked, and the person sees at once what is left to do.
* Good: nothing new is trusted. The describer's answer is checked like a sketch, the tests are the kernel's own behaviour, and laws stay the person's.
* Bad: the offline describer recognises only the shapes in its data file. Anything else becomes the plain shape, with fields read from the description. A live describer would be another adapter behind the same port, after the owner says yes.
* Bad: the recorded tests pin down today's behaviour. A later change that alters it makes them fail. That is their purpose, but a person has to re-record them on purpose.
* Neutral: shipped packs and the sketch, template and UML starts are unchanged.

## Verification

* `tests/test_play_describe.py` checks four things:
  * a coffee-shop description through the HTTP routes: the summary of every view, creation, three tests passing in the kernel, Build & run conformance, three sequences, and What's missing showing laws as missing, with a new unreachable state appearing in it;
  * a describer whose fields the data model refuses is rejected;
  * an empty description is refused;
  * four descriptions map to the expected shapes.
* A manual Chromium run checked `/play?new=describe`: the summary under the box, creation, the What's missing panel, the class and sequence diagrams, and a chat round that the panel follows.
* The greenfield demo starts from a description (`demos/scenarios/playide_greenfield.py`).

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| spaCy / NLTK (MIT / Apache-2.0) | A parser would read more phrasings but adds a model download and still guesses. The offline reader is a stand-in for a live model behind the port | Use a live describer adapter (owner's call) rather than a heavier offline parser |
| Lovable / Replit Agent (proprietary) | Hosted services, not libraries | Patterns only |
