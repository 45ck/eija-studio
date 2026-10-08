---
type: Architecture Decision Record
title: 'ADR-0173: PlayIDE''s workbench shell, after Visual Studio, VS Code, Cursor and draw.io'
description: After watching the recorded tours, the owner said there was "too much going on in sidebar" and that it "feels weird", and asked to "make playIDE really good, copy or take inspiration from existing sources, cursor, codex…
resource: repo://docs/adr/0173-playide-workbench-shell.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0173-playide-workbench-shell.md
  title: 0173-playide-workbench-shell.md
  hash_method: lf-sha256-v1
  sha256: d4d35264e7d7d6ab6142de8c011d766df2ba15b82e25c2d84b44d6d2e8836e18
notes_baseline: 0818d608d137ddb74200350454fcfb3046bb7f33cf828c60624e5a5691d48526
---

# ADR-0173: PlayIDE's workbench shell, after Visual Studio, VS Code, Cursor and draw.io

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-08 |
| Lane | PlayIDE (owner direction, 8 October 2026) |
| Source | `repo://docs/adr/0173-playide-workbench-shell.md` |

## Decision outcome (verbatim)

> Chosen option. Sources, all patterns only (no code copied):
>
> | Region | What it holds | Taken from |
> |---|---|---|
> | Title bar | PlayIDE, the model, a command center that opens the Ctrl+K palette (ADR-0170), layout toggles | VS Code's command center and layout controls; Cursor's title bar |
> | Toolbar | The run bar (Run, Pause, Step, Stop, Restart, speed), Simulate, Build & run, and the checks ring, whose list opens as a popover under it | Visual Studio's standard and debug toolbars (ADR-0160) |
> | Left | The model outline above the inspector | Visual Studio's Solution Explorer above the Properties window; draw.io's format panel is the same idea on the other side |
> | Centre | Editor tabs: the five UML diagrams, then Laws and Permissions after a divider. Ripple badges stay on the tabs (ADR-0158). The UML palette is a column beside the state machine | VS Code editor tabs; draw.io's shape library beside the canvas |
> | Below the diagrams | One panel with tabs: Run (the debugger, ADR-0160), Simulation (ADR-0152) and Running app (ADR-0151). It opens on whichever has just started and can be resized or hidden | VS Code's panel, which reveals new output; Visual Studio's output and diagnostic windows |
> | Right | The chat alone, full height, in plan mode with its authority strip (ADR-0156, ADR-0170) | Cursor's agent panel; the Codex app's conversation beside the work |
> | Status bar | The model, "Previewing a plan" while a plan is shown, the selection, the last toast, the Simulate score and Ctrl K | VS Code and Visual Studio status bars |
>
> * Ctrl+B hides the left side, as in VS Code; Ctrl+Alt+P the panel and Ctrl+Alt+C the chat. VS Code's Ctrl+J and Cursor's Ctrl+L are kept by the browser (Downloads and the address bar in Chrome), so a web page cannot use them. The three splitters are keyboard resizable. Sizes and hidden regions are kept in the browser (`localStorage`), and the page works the same when storage is blocked.
> * The review view (ADR-0172) has no chat column and no chat toggle.
> * The code is `play-shell.js` and `play-shell.css`. `play.html` moves the regions; the shell script only watches `hidden` on the panel's sections and on the plan banner, sets layout attributes on `body`, and mirrors the model name and the selection into the status bar. A section another script shows comes to the front of the panel.
> * The side columns give way before the diagram does: the centre keeps at least 520 pixels, and the chat narrows first.

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

* [ADR-0151: PlayIDE canvas with Build & run of the live app](/adrs/0151-playide-canvas-and-build-and-run.md) - The owner wants EIJA to feel like "UML you can trust to build apps": a visual, mouse-driven IDE (named PlayIDE) where a UML-literate engineer designs a system…
* [ADR-0152: Simulate seeded users through the kernel and paint where they went](/adrs/0152-simulate-seeded-users-through-the-kernel.md) - The owner asked for PlayIDE to feel like a simulation game for software engineers: build a system, watch it run and find problems fast.
* [ADR-0156: Chat plan mode proposes typed steps the person accepts or rejects](/adrs/0156-chat-plan-mode-proposes-typed-steps.md) - The owner's roadmap asks for an AI chat sidebar "like T3 Code, with plan mode prominent", in which the AI proposes changes to the UML and the person accepts or…
* [ADR-0157: Drawn edits join the plan, and a checks ring rewards checking](/adrs/0157-drawn-edits-and-checks-ring.md) - The owner wants PlayIDE to be visual and mouse-driven ("drag and drop, design then test in place") and to feel rewarding, "tied to real checks".
* [ADR-0158: A change ripples across every diagram, and the AI's follow-on edits are re-checked](/adrs/0158-ripple-across-diagrams-with-checked-follow-ons.md) - PlayIDE draws five diagrams of one system: the state machine, the class diagram, the use cases, the screens and the components of the built app.
* [ADR-0160: A run bar with breakpoints, over one seeded run the kernel decides](/adrs/0160-run-bar-with-breakpoints-over-a-seeded-run.md) - The owner asked for "a similar thing to Visual Studio where it has play and stop etc": run the system, pause it, step through it and stop it, from inside PlayI…
* [ADR-0170: PlayIDE asks about the selection, completes exact names, has a command palette and keyboard plan review](/adrs/0170-playide-assist-ask-complete-palette-review.md) - PlayIDE's chat proposes typed steps (ADR-0156) and rewards checking them (ADR-0157).
* [ADR-0172: A read-only review view of PlayIDE for people who review the model](/adrs/0172-review-view-for-reading-the-model.md) - The owner set the audience as people who know UML, and noted that UML "is meant for non technical people to review it sometimes".
<!-- okf:generated:end links -->
