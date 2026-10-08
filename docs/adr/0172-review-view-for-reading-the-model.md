# ADR-0172: A read-only review view of PlayIDE for people who review the model

* Status: accepted
* Date: 2026-10-08
* Lane: PlayIDE (owner direction, 8 October 2026)

## Context and problem statement

The owner set the audience as people who know UML, and noted that UML "is meant for non technical people to review it sometimes". A stakeholder who reviews a system design wants the real diagrams, the permissions and a way to watch the model run. They do not want drawing tools, an AI chat or controls that look like they change something. PlayIDE showed everything to everyone.

## Decision drivers

* The same UML, not a translation of it. The owner ruled out plain-language captions that replace the diagrams and a UML-teaching mode.
* Approval and apply stay owner-only in the review workbench. A view must not suggest otherwise.
* No second page and no second source: one page, with tools out of view.

## Considered options

* A query parameter, `?view=review`, that hides the editing tools on the same page (chosen).
* A separate read-only page. Rejected: it would duplicate the diagrams and drift from them.
* A server-side role for reviewers. Not needed for this: PlayIDE never saves an edit (plans are previewed, not applied), and approval is already owner-only on the server. A per-person identity is a separate decision (HCI-ADR-0064 D5, D6, D9).

## Decision outcome

Chosen option.

* `/play?view=review` shows a "Review view · read only" badge with an **Edit** link back, and hides the drawing palette, the chat, every edit tool in the inspector (`edit-tools`), the screen designer's attribute palette and reset button. The screen card is `inert`: readable, not editable. Delete on the canvas does nothing.
* Everything that reads or runs the model stays: all diagrams, **Permissions** (ADR-0171), Simulate, the run bar and its breakpoints, Build & run with the running app, and the checks ring.
* The command palette offers "Open the review view (read-only)" and, in it, "Leave the review view (edit)". AI and plan commands are not listed there.
* The page's session token still gates the page. The view is about what a reviewer sees, not about who may do what. The server's authority does not change.

### Consequences

* Good: a stakeholder can read the real UML, ask who can do what and watch seeded users go through, with nothing on screen that edits.
* Bad: it is a view, not a permission. Anyone with the page can leave it with Edit. That is acceptable only because nothing in PlayIDE persists a change.
* Revisit when: PlayIDE can save a plan as a change case (issue #89), or the Studio gets per-person identities.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| HTML `inert` attribute and CSS (standards) | Adopted | — |
| Feature-flag or permission libraries (e.g. CASL) | A client-side permission model would be a second authority beside the server's; this is presentation only | — |
