# ADR-0203: A system landscape of the workflows that share classes

* Status: accepted for workflows in one folder
* Date: 2026-10-09
* Lane: PlayIDE (owner direction, 9 October 2026: refine how software and computers are designed in PlayIDE, so system design is credible for a startup or an enterprise architect)

## Context and problem statement

PlayIDE edits one workflow at a time: one state machine moving one record class, with its class diagram, use cases, screens and laws. Real systems have several workflows. A library lends books and also fines members. The two share classes, actors and notifications. Nothing in PlayIDE showed how the workflows of one system relate, and nothing noticed when two of them modelled the same class differently.

The Components tab did not fill this gap. It shows the app one model builds, read from the generated files (ADR-0155), so its structure is the same for every model. ADR-0155 recorded this as its main limitation.

An architect who opens a design tool first wants to know which parts the system has, who uses them, what each part offers, what it depends on, and who owns each shared class. Two teams modelling `Member` with different field lengths cause real defects. In an enterprise, that question is master data. In a startup, it is the bug that appears in the second service.

## Decision drivers

* One source per fact (ADR-0093). The landscape must not be a second model of the system written beside the packs.
* Every view is an editor or a projection of the model the kernel checks. Each workflow in the landscape is a pack that the kernel's pack check accepted.
* Say what is not executed. Workflows do not call each other at run time, and the kernel has no cross-workflow messages yet (#93). A dependency in the landscape is a design dependency, and the page says so.
* Proper UML component notation, for engineers who know UML.
* Stay out of the kernel. A workflow-composition operator would be a kernel change, which waits on #80.

## What existing tools do

| Tool | How several services or workflows are shown | What PlayIDE takes from it |
|---|---|---|
| Structurizr / C4 (Apache-2.0 DSL) | A hand-written container diagram, with a second model of the system beside the code | The level: parts of one system, their users and dependencies. Not the hand-written model |
| Context Mapper (Apache-2.0) | A DDD context map in its own DSL, with relationships (shared kernel, customer/supplier) | Shared classes and ownership are the first question |
| Backstage catalog (Apache-2.0) | YAML descriptors per component, with `dependsOn` written by hand | Each part declares what it provides. In PlayIDE that is its actions, not a descriptor |
| Visual Paradigm, Enterprise Architect (proprietary) | Drawn component diagrams, not checked against anything | UML notation: a lollipop for a provided interface, «use» for a dependency |

All of these describe the system in a second document that someone keeps in step by hand. None reads a set of executable workflows. A library would add a second metamodel and solve nothing. The custom code is a projection of the packs.

## Considered options

* **Derive the landscape from the packs in one folder: workflows that share a class are one system (chosen).**
* **A `system.json` listing member workflows and their links.** This is closer to C4. It is a second source for something the class diagrams already say (fines names `Loan`), so it can drift. Reconsider it when a system needs a link that no class expresses.
* **Cross-workflow messages in the kernel** ("when a loan is returned late, a fine starts"). This is the real composition. It is a kernel operator (#93), and it waits on the owner's source review (#80).

## Decision outcome

Chosen option: `application/landscape.py`, `landscape(focus, systems, unreadable)`. The route is `POST /api/play/landscape`. The page shows it as the **System** lens of the Components tab (`play-landscape.js`).

* **Which workflows.** These are the packs beside the open one (`packs/` for shipped packs, the systems home for your own) that the kernel's pack check accepts, reachable from the open workflow through classes their class diagrams name. Packs that share nothing are listed as *Not in this system*. Packs the pack check refused are listed as *Not read*, so nothing is dropped silently. The open workflow is the model shown, including a previewed plan and a chat-grown class diagram (ADR-0202).
* **Ownership.** The workflow whose record a class is owns that class. Another workflow that names the class has a «use» dependency on the owner, labelled with the class. A class that two workflows name and neither moves is drawn as a «class» on its own, marked *shared, no owner*.
* **What each workflow provides.** Its actions are drawn as a provided interface (lollipop). Each action lists the roles its transitions give it to. Roles with one name are one actor, which has a «use» dependency on each workflow where it holds an action. The workflow's notification effects are what it publishes (the outbox of the built app).
* **Findings.** Each finding names its classes, attributes and workflows. There are two severities: `warning` (*Disagrees*) and `consider` (*To consider*).
  * `CLASS_COPIES_DIFFER` (warning): an attribute declared two ways (type, length, choices, required) in two copies of one class.
  * `ATTRIBUTE_NOT_ON_OWNER` (warning): a workflow adds an attribute to a class another workflow owns.
  * `RECORD_MOVED_TWICE` (warning): two state machines move the same record class.
  * `CLASS_HAS_NO_OWNER` (consider): a shared class that no workflow moves.
  * `RECIPIENT_IS_NOT_AN_ACTOR` (consider): a notification to a recipient that is no role in the system.
* A new shipped pack, `library-fines` (Fine: Issued, Disputed, Paid, Waived), names `Loan` and `Member`. Opening `library-loan` and choosing **System** shows two workflows, three actors, fines using loan through `Loan`, and `Member` shared with no owner. `Member.card` is 20 characters in one copy and 32 in the other. The pack has its own laws and scenarios, and every pack-wide gate runs on it.

### Consequences

* Good: a second workflow joins the system by naming a class, with no new file and nothing to keep in step. Once the class diagrams agree, the findings go away.
* Good: the findings are the questions an architect asks first. Each one names exactly what to change.
* Good: the lens is a projection. It writes nothing and decides nothing, and it is computed on the server.
* Bad: classes link by name only. Two unrelated classes with the same name in one folder would be drawn as one system. Separate them by folder.
* Bad: a link is a design dependency. The built apps do not call each other, and the kernel does not run a cross-workflow step. The page says so (`limits`).
* Bad: a deployment view (which process, which database file, which port) is not drawn yet. It can be read from the same generated files as ADR-0155.
* Revisit when: the kernel gains cross-workflow messages (#93), when a link has to be expressed that no class expresses (then `system.json`), or when systems span folders.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| Structurizr DSL / C4-PlantUML | Hand-written second model of the system; nothing reads executable workflows | Export the landscape as Structurizr DSL for teams that use it |
| Context Mapper | Its own DSL and metamodel for bounded contexts; a second source | Export the shared classes as a context map |
| Backstage catalog | Hand-written YAML descriptors and `dependsOn` | Publish each workflow as a catalog component from the same result |
| maxGraph `actor`, `ellipse`, `rectangle` shapes (existing, Apache-2.0) | Adopted to draw it | — |
