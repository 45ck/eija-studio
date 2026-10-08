---
type: Architecture Decision Record
title: 'ADR-0158: PlayIDE asks about the selection, completes exact names, has a command palette and keyboard plan review'
description: PlayIDE's chat proposes typed steps (ADR-0156) and rewards checking them (ADR-0157).
resource: repo://docs/adr/0158-playide-assist-ask-complete-palette-review.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0158-playide-assist-ask-complete-palette-review.md
  title: 0158-playide-assist-ask-complete-palette-review.md
  hash_method: lf-sha256-v1
  sha256: 6e945573e1a1134675ae9dd967d357c170eb7327c8b2290ad0e8f2f7398aa940
notes_baseline: ddfa949125ac65cff602dbe64e15b315f0a7c8342ad871adac91ae25d570f019
---

# ADR-0158: PlayIDE asks about the selection, completes exact names, has a command palette and keyboard plan review

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-08 |
| Lane | PlayIDE (owner direction, 8 October 2026: "UI, HCI, AHCI") |
| Source | `repo://docs/adr/0158-playide-assist-ask-complete-palette-review.md` |

## Decision outcome (verbatim)

> Chosen option: the assist layer.
>
> * **Who does what.** A line under the chat heading: "AI proposes steps · You check, preview and try them · Owner approves and applies in the review workbench".
> * **Ask about the selection.** Phrase buttons above the chat box show requests the offline proposer reads. With nothing selected they are templates with blanks (‹state›, ‹role›, ‹action›, ‹new name›). With a state or transition selected they are about it, its exact name filled in ("About Overdue: Add a state after, Rename, Add a transition from here, Start records here, Remove"). Pressing one while the box has text adds it as the next clause with "then". The first blank is selected so typing replaces it; Tab moves to the next.
> * **Exact names.** The chat box is a combobox (WAI-ARIA APG). A selected blank offers names of its kind; otherwise the word being typed is completed from the model's states, the pack's actions and roles, and states the request itself adds. Arrow keys move, Enter or Tab accepts, Escape closes. Ctrl+Enter (⌘Enter) sends. A request with an unfilled blank is held, with "Fill in ‹role› first."
> * **Command palette.** Ctrl+K (⌘K), or the **Commands** button, opens a native modal `<dialog>`. It lists the page's commands that are available now (Build & run, Simulate, the tabs, Fit, Show the checks, Ask the AI, Review the AI plan, Preview the plan, Back to the model, the review workbench), every state, transition and class, and "Ask the AI about …" for each state and transition. Words filter it. Each command presses the page's own button, so the palette can do nothing a click could not.
> * **Keyboard plan review.** While focus is in the current plan: J/K or the arrow keys move between steps, S or Enter shows the step on the diagram, Space (the checkbox's own) accepts or rejects, P turns the preview on or off. Each plan card says so.
> * **Hooks into play.js.** play.js dispatches `playide:select` when the selection changes and `playide:ready` when the model has loaded, and exposes a frozen read-only `window.PlayIDE` with `model()`, `pack()` and `selected()`. Nothing else in play.js changed.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [HCI-ADR-0064: AI and agent interaction: proposal cards, delegation fence, isolated owner controls](/adrs/0064-hci-ai-interaction.md) - HCI-ADR-0064: AI and agent interaction: proposal cards, delegation fence, isolated owner controls
* [ADR-0156: Chat plan mode proposes typed steps the person accepts or rejects](/adrs/0156-chat-plan-mode-proposes-typed-steps.md) - The owner's roadmap asks for an AI chat sidebar "like T3 Code, with plan mode prominent", in which the AI proposes changes to the UML and the person accepts or…
* [ADR-0157: Drawn edits join the plan, and a checks ring rewards checking](/adrs/0157-drawn-edits-and-checks-ring.md) - The owner wants PlayIDE to be visual and mouse-driven ("drag and drop, design then test in place") and to feel rewarding, "tied to real checks".
<!-- okf:generated:end links -->
