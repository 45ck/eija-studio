# ADR-0215: See and run the app as each role

* Status: accepted
* Date: 2026-10-09
* Lane: PlayIDE (owner direction, 9 October 2026: refine how humans and software are designed; thread "Humans, roles and screens")

## Context and problem statement

PlayIDE already models the human side of a system: roles and fixture actors in the pack, a use case diagram ([ADR-0154](0154-use-cases-and-screens-designed-against-the-model.md)), one screen per use case, and a Permissions matrix the kernel fills ([ADR-0171](0171-permissions-matrix-and-reachability-questions.md)). But the pieces did not meet. An actor on the use case diagram could not be selected. A role in the outline only opened the Permissions tab. The screen designer listed every screen with no way to ask "what does a Clerk see?". The built app showed every role's actions to every actor, each disabled with a refusal, and its screen had a dismiss button labelled "Cancel", which in library-loan is also the name of an action. Engineers check a role-based design by looking at it as each role, and nothing let them.

## Decision drivers

* What a role may do is the kernel's answer, never a reading of the page.
* One source per fact: a role's screens are the screens of the use cases it may take. There is no per-role screen file.
* Design, then try it in place, as the person who will use it.
* Honest limits: where the model says nothing (who may start a record), the page says "any active actor".

## Considered options

* A role layer over the existing permissions answer, with "Run as" opening the built app acting as one fixture actor (chosen).
* Per-role screen files (`screens.<role>.json`). Rejected: a second source for which screens a role sees. The model's transitions already say it.
* A role filter that reads `transition.role` in the page. Rejected: it would miss guards (assigned only, revoked) that the kernel applies per actor.

## Decision outcome

Chosen option: `resources/web/play-roles.js` and `play-roles.css`.

* **An actor is selectable.** Choosing an actor on the use case diagram, a role in the outline, or a role's column heading on the Permissions tab selects `role:<id>`. The inspector shows the role's description (`pack_summary` now carries `role_notes`), the use cases the kernel lets its fixture actors take (from which states, and *assigned only* where a guard narrows it), the fixture actors who play it, and buttons to see their screens, to see who can do what, and to run the app as each actor. The run bar's breakpoint tool no longer appears for an actor.
* **See the app as.** The Screens tab has a role bar above the designer. Choosing a role strikes through the screens it never sees, notes on the open screen whether the role sees it (and if not, which role does), and lists the role's screens in order, the ones it never sees, and **Run as** buttons. Starting a record counts for every role, because the kernel lets any active actor start one.
* **Run as.** `PlayIDE.runAs(actor)` reuses the last build when it is of the model and screens on show and passed conformance, and builds otherwise. The running app opens at `#actor=<id>`.
* **The built app puts the acting role first.** The generated page honours `#actor=<id>` (and later changes to it), shows the acting role beside the picker and flags an inactive actor, lists the acting role's actions first with the kernel's refusal where a guard applies, folds the other roles' actions under *For other roles*, and highlights the role's rows in the rules table. The screen's dismiss button says Close. The server still decides every option and every action.

### Consequences

* Good: a reviewer can check a role-based design the way it will be used: pick a role, see its screens, run the app as it.
* Good: the role view follows a previewed plan, because it is the same kernel answer as the Permissions matrix.
* Bad: what a role may do is shown with the pack's fixture actors, as in ADR-0171; it is not a statement about every real actor.
* Bad: the model cannot yet say who may start a record, so every role sees the create screen ([#142](https://github.com/45ck/eija-studio/issues/142), a kernel change).
* Revisit when: #142 lands (the create screen joins the role filter), or screens gain per-role layout.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| Casbin, Open Policy Agent | A second permissions source beside the model | — |
| GrapesJS device and preview modes | Free HTML bound to nothing in the model; refused by the strict CSP (ADR-0154) | — |
| Existing `/api/play/access` and maxGraph actor cells | Adopted: the kernel's per-actor answers and the diagram's own cells | — |
| URL fragment and `hashchange` (web platform) | Adopted for opening the built app as an actor | — |
