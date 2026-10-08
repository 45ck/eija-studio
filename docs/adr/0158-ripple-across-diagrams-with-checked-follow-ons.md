# ADR-0158: A change ripples across every diagram, and the AI's follow-on edits are re-checked

* Status: accepted
* Date: 2026-10-08
* Lane: PlayIDE (owner direction, 8 October 2026)

## Context and problem statement

PlayIDE draws five diagrams of one system: the state machine, the class diagram, the use cases, the screens and the components of the built app. After the PlayIDE tour, the owner asked to see "play and seeing how that affects other UML models": "by changing one you need to change others (AI can help here?) and deterministically check". On the decision card the owner chose "Impact + AI fixes": each drawn change shows which diagrams it affects and what broke, the AI proposes the follow-on edits, the kernel re-checks them, and then the owner builds.

Before this, a change to the state machine already reached the other diagrams, because they are read from it (ADR-0153 to ADR-0155), but nothing said so. A real inconsistency could go unnoticed until Build & run refused. For example, removing an action whose screen the pack designed leaves that screen pointing at a use case that no longer exists, and the app cannot be built (`SCREEN_UNKNOWN_USE_CASE`). A new state that nothing leads into was accepted silently.

## Decision drivers

* One source of truth. The ripple is computed from the same model, data model, screens and generated files the app is built from. There is no second model of how diagrams relate.
* Deterministic and explainable. Each effect names its diagram, its kind and the element it is about.
* The AI only proposes. Follow-on edits are untrusted, re-checked like any plan step, and taken one at a time by the person.
* Nothing is saved, approved or applied from here (ADR-0156).

## Considered options

* Compute the ripple on the server from the two models, the screens and the two builds; follow-ons come from the plan proposer and are re-checked (chosen).
* Auto-sync: apply follow-on edits automatically. Rejected by the owner on the decision card: the owner reviews each change.
* Impact only, with no follow-ons. Rejected by the owner: "AI can help here".
* A general model-to-model consistency engine (Eclipse OCL, Epsilon EVL, the MDE "megamodel" approach). Not adopted: they need an EMF/Ecore metamodel of all five diagrams, which would be a second source of truth beside the kernel's typed contracts. The checks here are the existing ones (policy, screen design check, conformance), applied across diagrams.

## Decision outcome

Chosen option.

* **Ripple** (`application/ripple.py`, `POST /api/play/ripple`). Given the request's accepted plan steps and the designer's screens, the server compares the saved system (the active model with the pack's screens) with the plan's version. Every effect is `added`, `removed`, `changed`, `warning` (the app still builds) or `problem` (out of step):
  * **State machine:** added and removed states and actions, changed actions, a new initial state; `STATE_UNREACHABLE` for a state that no transition now leads into, and `STATE_NO_EXIT` for a state that had a way out and now has none.
  * **Class diagram:** the record class has a `state` association to a derived `«enumeration» <Record>State`, whose literals are the state machine's states. A state added or removed is a literal added or removed.
  * **Use cases:** use cases (actions) added or gone, actor associations (role takes action) added or gone, and actors added or gone.
  * **Screens:** default screens the build would add, screens dropped, and every design problem the change introduces (`check_screens`).
  * **Components:** each drawn component whose generated files differ between the two builds, and `SCREENS_BLOCKED` when the plan's version cannot be built.
  * **Conformance:** the number of oracle cases before and after.
  A plan *agrees* when it has no `problem`; warnings are shown but do not block.
* **Follow-ons.** When the ripple has warnings or problems, the server asks the plan proposer (the `PlanProposer` port gains `follow_on`) for follow-on steps: a state-machine transaction, or a screen step that adds or removes one screen. `check_follow_ons` re-checks each one on its own: a transaction with the plan through the policy (`apply_transactions`), a screen step by the design check. A screen step that does not reduce the design problems is refused (`FOLLOW_ON_FIXES_NOTHING`). The offline proposer (`offline-plan-fixture-v1`) uses fixed rules:
  * a default screen for a use case without one, and no screen for a use case that is gone;
  * for an unreachable state, a transition into it from the nearest reachable state before it, using a declared action the model does not use yet;
  * for a state with no way out, a transition to an end state its neighbours lead to.
  These are guesses. The page labels them AI, offline fixture, not a live model.
* **Page.** Each diagram tab carries a badge with its count of effects: amber for warnings, red for problems. While the plan is previewed, added and changed elements are marked on each diagram; on the model without the plan, removed ones are marked in red. The plan's card in the chat lists the ripple by diagram. Clicking an effect opens that diagram at that element. The card also lists the AI follow-ons with an Add button for each one the server accepts:
  * a transaction joins the plan as an AI step;
  * a screen step replaces the designer's screens.
  Either way the plan, the screens and the ripple are checked again.
* **Checks ring.** A fifth part, "Diagrams agree", is green when there is no change or the current ripple has no problem. Following ADR-0157, points come only from checking: +1 the first time you open the ripple on each other diagram, for each version of the plan. Taking a follow-on earns nothing.

### Consequences

* Good: a change to one diagram visibly reaches the others. The case that used to fail only at build time (a stranded screen) is caught as you draw, with a one-click, re-checked fix.
* Good: the class diagram now shows the record's states as a UML enumeration, so the state machine and the class diagram are visibly one model.
* Good: every follow-on goes through the existing checks; the proposer cannot widen what is allowed.
* Bad: the offline proposer's follow-ons are rule-based guesses (for example, which action leads into a new state); a live model would need the owner's permission for network use and spend.
* Bad: the ripple builds the app twice in memory on each change (about 0.1 s for the library pack); a large pack may need caching.
* Revisit when: a live proposer is allowed, plans can be saved (issue #89), or the data model becomes editable in PlayIDE (then a data change ripples into screens too).

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| Eclipse OCL, Epsilon EVL (EPL-2.0) | Need an Ecore metamodel of all diagrams: a second source of truth beside the kernel's contracts; JVM-only | Adopt if diagrams ever move to an EMF metamodel |
| Sirius / Capella cross-diagram synchronisation (EPL-2.0) | Desktop Eclipse RCP; the pattern (one semantic model, many synchronised views) is the one PlayIDE already follows | Pattern only |
| Existing `check_screens`, `apply_transactions`, `laws.reachable`, `app_files`, `app_components` | Adopted: every check is one of these | — |
