# ADR-0204: The ripple reaches the other workflows of the system

* Status: accepted
* Date: 2026-10-09
* Lane: PlayIDE software architecture views (issue #146; follows ADR-0158 and ADR-0203)

## Context and problem statement

The ripple (ADR-0158) shows what a change does to every diagram of one workflow. The System lens (ADR-0203) shows the workflows that share classes with it. The ripple did not cover the other workflows. On a system you started, a chat round can change a class diagram (ADR-0202). It can drop `Loan.dueDate` from the loans workflow while the fines workflow still uses it, and nothing said so.

## Decision drivers

* The ripple stays the one list of what a change does (ADR-0158). A second "impact on the system" panel would be a parallel source.
* The other workflows are reported, never edited. Their documents belong to them, and the follow-on proposer only edits the open workflow.
* No new rules. The checks are the ones in the System lens.

## Considered options

* **Run `landscape()` on the system before and after the change, and list the difference as a "System" diagram of the ripple (chosen).**
* **Re-check each other workflow's own diagrams against the candidate.** This is more thorough. But the workflows are only linked by classes until cross-workflow messages exist (#93), and the class findings are exactly that link.

## Decision outcome

Chosen option. The ripple gains `diagrams.system`, computed by `ripple._system_items` from two landscapes. The route passes the landscapes only when the open workflow has sibling packs.

* A disagreement with another workflow that the change introduces (`CLASS_COPIES_DIFFER`, `ATTRIBUTE_NOT_ON_OWNER`, `RECORD_MOVED_TWICE`) is a **warning**. It is listed in the ripple's problems and counted on the checks ring, as other warnings are. The warning does not make the diagrams disagree, because each app still builds.
* A «use» link from another workflow that the change breaks is a warning (`SYSTEM_LINK_BROKEN`).
* A finding the change resolves, and a "to consider" it raises, are changes.
* The plan's ripple list names them "System". The Components tab's badge counts them. Choosing one opens the Components tab on the System lens with the shape selected; an owned class is shown as its workflow. Checking it earns the checks-ring point that other ripple items earn. The Changes view's "Also changes" line links to it.

### Consequences

* Good: a change to a shared class is seen where every other ripple item is seen, before anything is saved.
* Good: the other workflow's documents are untouched, and the follow-on proposer is unchanged.
* Bad: only class-level effects are seen. A state-machine step changes no class, so it never ripples into the system. Messages between workflows (#93) would change that.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| None new | Reuses `application/landscape.py` (ADR-0203) and the ripple (ADR-0158) | — |
