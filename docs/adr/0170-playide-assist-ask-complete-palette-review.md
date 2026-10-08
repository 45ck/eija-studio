# ADR-0170: PlayIDE asks about the selection, completes exact names, has a command palette and keyboard plan review

* Status: accepted
* Date: 2026-10-08
* Lane: PlayIDE (owner direction, 8 October 2026: "UI, HCI, AHCI")

## Context and problem statement

PlayIDE's chat proposes typed steps (ADR-0156) and rewards checking them (ADR-0157). Three things still made the person do the AI's bookkeeping. The offline proposer reads a bounded grammar with exact model names, but the page did not show the phrases or the names, so people had to guess and be refused. A request could not start from what was selected on the diagram, which HCI-ADR-0064 records as the missing task T13. Reviewing a plan needed the mouse for every step, and there was no single place to reach every command or element. The delegation fence (who proposes, who checks, who approves) was only in a tooltip.

The argument for each change, with sources, is in [docs/hci/design/playide-ahci.md](../hci/design/playide-ahci.md).

## Decision drivers

* The page must not interpret requests or decide steps. No second interpreter: the server's proposer and policy stay the only judges.
* Checking an AI step must be as cheap as accepting it.
* Keyboard and mouse both work for everything; single-key shortcuts act only where focus is (WCAG 2.1.4).
* Low merge risk with parallel PlayIDE work: keep the new behaviour in its own files.

## Considered options

* A separate assist layer (`play-assist.js`, `play-assist.css`) that writes text into the chat box and presses the page's own controls (chosen).
* Vendor a mention library (Tribute, MIT) for name completion. Rejected: last released March 2020, and we need one APG listbox for both the palette and completion anyway.
* Vendor a command-palette library: ninja-keys (MIT, needs Lit and a bundler), cmdk and kbar (MIT, React). Rejected: the page has no framework or bundler; a native `<dialog>` gives focus trapping and Escape for free.
* Check the request's grammar in the page before sending. Rejected: a second interpreter. The page only holds a request with an unfilled ‹blank›, which is form validation, not interpretation.

## Decision outcome

Chosen option: the assist layer.

* **Who does what.** A line under the chat heading: "AI proposes steps · You check, preview and try them · Owner approves and applies in the review workbench".
* **Ask about the selection.** Phrase buttons above the chat box show requests the offline proposer reads. With nothing selected they are templates with blanks (‹state›, ‹role›, ‹action›, ‹new name›). With a state or transition selected they are about it, its exact name filled in ("About Overdue: Add a state after, Rename, Add a transition from here, Start records here, Remove"). Pressing one while the box has text adds it as the next clause with "then". The first blank is selected so typing replaces it; Tab moves to the next.
* **Exact names.** The chat box is a combobox (WAI-ARIA APG). A selected blank offers names of its kind; and keeps that kind while you type over it; otherwise the word being typed is completed from the model's states, the pack's actions and roles, and states the request itself adds. Arrow keys move, Enter or Tab accepts, Escape closes. Ctrl+Enter (⌘Enter) sends. A request with an unfilled blank is held, with "Fill in ‹role› first."
* **Command palette.** Ctrl+K (⌘K), or the **Commands** button, opens a native modal `<dialog>`. It lists the page's commands that are available now (Build & run, Simulate, the run bar's Run, Pause, Step, Stop and Restart, the tabs, Fit, Show the checks, Ask the AI, Review the AI plan, Preview the plan, Back to the model, the review workbench), every state, transition and class, and "Ask the AI about …" for each state and transition. Words filter it. Each command presses the page's own button, so the palette can do nothing a click could not.
* **Keyboard plan review.** While focus is in the current plan: J/K or the arrow keys move between steps, S or Enter shows the step on the diagram, Space (the checkbox's own) accepts or rejects, P turns the preview on or off. Each plan card says so.
* **Hooks into play.js.** play.js dispatches `playide:select` when the selection changes and `playide:ready` when the model has loaded, and its `window.PlayIDE` bridge (shared with the run bar, ADR-0160) gains `pack()` and `base()`. The assist layer reads only `base()` (the model a request is planned against, never a previewed candidate), `pack()` and `selected()`. Nothing else in play.js changed.

### Consequences

* Good: the grammar and the model's names are visible, so fewer requests are refused for a wrong name, and a request starts from the diagram.
* Good: a whole plan can be reviewed without the mouse, and Show me is one key.
* Good: no new dependency, no server change beyond allowing the two assets.
* Bad: the phrase buttons mirror the offline grammar's phrases. If the grammar changes, the buttons must change with it; a live proposer would make them suggestions rather than the only phrases read.
* Bad: no human has used these yet. The design document names the study that would test them.
* Revisit when: a live proposer is allowed (send the selection as context), or the sidebar is relaid out.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| Tribute 5.1.3 (MIT) | Unmaintained since 2020; triggers on a character, not on a selected blank; one listbox serves both uses | Vendor it if completion grows past names |
| ninja-keys 1.2.2 (MIT) | Needs Lit and a bundler; the page has neither | — |
| cmdk, kbar (MIT) | React components; the page has no framework | — |
| Native `<dialog>` and the WAI-ARIA APG combobox pattern (standards) | Adopted | — |
| VS Code, Linear and Cursor command palettes; Cursor's @-context (patterns) | Adopted as interaction patterns, no code | — |
