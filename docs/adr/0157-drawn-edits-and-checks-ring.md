# ADR-0157: Drawn edits join the plan, and a checks ring rewards checking

* Status: accepted
* Date: 2026-10-08
* Lane: PlayIDE (owner direction, 8 October 2026)

## Context and problem statement

The owner wants PlayIDE to be visual and mouse-driven ("drag and drop, design then test in place") and to feel rewarding, "tied to real checks". The positioning research found a risk in rewarding the wrong thing: when an AI writes the change, scoring output (steps made, lines generated) rewards rubber-stamping. The reward should go to checking and understanding the AI's proposals.

Owner edits (`/edit`, `/undo`, `/layout`) are owner-only routes that an agent must not call. A palette that wrote through them would also save each gesture straight into a change case, with no preview.

## Decision drivers

* One edit vocabulary. Drawn changes must be the same typed transactions the policy already checks, not a second canvas model.
* Design, then test in place: a drawn change shows on every diagram, and Build & run and Simulate run on it, before anything is saved.
* Rewards come only from real results on the model being shown, and only for checking, never for producing changes.

## Considered options

* Drawn edits become steps of the plan (ADR-0156), authored by "you", previewed through the same server check (chosen).
* Write each gesture through the owner edit route. Rejected: owner-only, saves immediately, no preview.
* maxGraph's connection handler (drag from state to state) for transitions. Deferred: dropping the Transition tool on the state it leaves, then choosing the target, action and role, needs fewer gestures to be complete and is keyboard reachable.
* Points for steps accepted or apps built. Rejected: rewards output, not checking.

## Decision outcome

Chosen option.

* **Palette.** The state machine tab has a UML palette: State, Transition and Initial. Each can be dragged onto the diagram (dropped on a state, it starts there) or pressed. The inspector shows a short form, and the result joins the plan as a typed step (`add_state`, `add_transition`, `set_initial`). A selected state offers "Add a transition from here", "Start records here", "Rename…" and "Remove". A selected transition offers "Let <role> take it", "Move an end…" and "Remove". Delete removes the selection. Every drawn step is labelled "You"; AI steps are labelled "AI".
* **Same check.** `preview_plan` now returns each step's text, so the server words every step, drawn or proposed. A legal drawn change is previewed at once. A plan's card in the chat is the one list of steps; a newer AI plan retires the old card.
* **Checks ring.** The header shows a four-part ring. Each part is a real check on the model being shown (the base model, or the previewed plan with the screens on screen):
  * every AI step looked at on the diagram ("Show me");
  * the screens pass the design check;
  * Build & run passed conformance for exactly this view;
  * Simulate ran on exactly this view.
  Any change to the plan or the screens empties the build and simulation parts until they are run again.
* **Points.** Points are earned only for checking:
  * +1 for looking at an AI step on the diagram;
  * +3 for unticking an AI step when that alone turns a refused plan into one the policy allows (a step the policy caught);
  * +3 for a conformance pass on a previewed AI change;
  * +2 for simulating one.
  Each award is given once per step or per plan state. Making steps, accepting them or drawing earns nothing. Points live in the page for the session; they are not evidence and are never stored.

### Consequences

* Good: drawing and the AI share one path to the policy, and nothing reaches the store from either.
* Good: the reward tracks what the research says matters: looking at what the AI did and testing it.
* Bad: drawn changes are not saved; saving a plan as a change case still needs an owner decision (issue #89).
* Bad: points are per page session and could be gamed by reloading; they are encouragement, not a measure.
* Revisit when: plans can be saved (issue #89), or a direct drag between states is wanted.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| draw.io sidebar palette (Apache-2.0) | A pattern: drag a shape from a palette onto the canvas. Adopted as the interaction; the draw.io editor itself is not embedded | — |
| maxGraph `ConnectionHandler` | Deferred (see options) | Use for direct drag between states |
| HTML5 drag and drop (browser standard) | Adopted | — |
| Gamification engines (e.g. Oasis, Gamification-Engine) | Server-side point stores; here points must not be stored or treated as evidence | — |
