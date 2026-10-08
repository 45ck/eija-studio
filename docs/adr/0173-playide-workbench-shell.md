# ADR-0173: PlayIDE's workbench shell, after Visual Studio, VS Code, Cursor and draw.io

* Status: accepted
* Date: 2026-10-08
* Lane: PlayIDE (owner direction, 8 October 2026)

## Context and problem statement

After watching the recorded tours, the owner said there was "too much going on in sidebar" and that it "feels weird", and asked to "make playIDE really good, copy or take inspiration from existing sources, cursor, codex app, etc and visual studio etc drawio". The right sidebar stacked six things: the checks list, the run bar's debugger, the chat, the inspector, the simulation report and the running app. Whichever appeared pushed the chat out of view, and the inspector moved up and down as the others came and went. The header held the brand, the checks ring, the run bar, a toast, a score, Simulate, Build & run and a link in one row.

## Decision drivers

* People who use PlayIDE already use an IDE. Familiar places for familiar things cost nothing to learn.
* Each region has one job and stays where it is. Nothing new should push the chat or the inspector around.
* What is visible by default is what is used all the time: the diagram, the outline, the inspector and the chat. Run output appears when something runs.
* The run bar, ripple badges, checks ring and Laws tab already exist and keep working. Every element id stays, so the page's scripts and the recorded demos still find them.
* Presentation only. The shell decides nothing (ADR-0156, ADR-0157).

## Considered options

* A workbench shell in the shape engineers already know (chosen): title bar with a command center, a toolbar, the outline over the inspector on the left, editor tabs for the diagrams in the centre with the panel below, the chat on the right, a status bar.
* Keep one sidebar and add collapsible sections. Rejected: it still stacks unrelated things, and collapsing is more work than not showing.
* Floating windows (Visual Studio's dockable tool windows). Rejected for now: a docking manager is a large dependency for six panes, and floating panes hide the diagram.
* Adopt a layout library (Golden Layout, Dockview, FlexLayout). Rejected: Dockview and FlexLayout need a framework or a bundler; Golden Layout 2 would own every pane's DOM. A CSS grid with three splitters does the job in about 200 lines.

## Decision outcome

Chosen option. Sources, all patterns only (no code copied):

| Region | What it holds | Taken from |
|---|---|---|
| Title bar | PlayIDE, the model, a command center that opens the Ctrl+K palette (ADR-0170), layout toggles | VS Code's command center and layout controls; Cursor's title bar |
| Toolbar | The run bar (Run, Pause, Step, Stop, Restart, speed), Simulate, Build & run, and the checks ring, whose list opens as a popover under it | Visual Studio's standard and debug toolbars (ADR-0160) |
| Left | The model outline above the inspector | Visual Studio's Solution Explorer above the Properties window; draw.io's format panel is the same idea on the other side |
| Centre | Editor tabs: the five UML diagrams, then Laws and Permissions after a divider. Ripple badges stay on the tabs (ADR-0158). The UML palette is a column beside the state machine | VS Code editor tabs; draw.io's shape library beside the canvas |
| Below the diagrams | One panel with tabs: Run (the debugger, ADR-0160), Simulation (ADR-0152) and Running app (ADR-0151). It opens on whichever has just started and can be resized or hidden | VS Code's panel, which reveals new output; Visual Studio's output and diagnostic windows |
| Right | The chat alone, full height, in plan mode with its authority strip (ADR-0156, ADR-0170) | Cursor's agent panel; the Codex app's conversation beside the work |
| Status bar | The model, "Previewing a plan" while a plan is shown, the selection, the last toast, the Simulate score and Ctrl K | VS Code and Visual Studio status bars |

* Ctrl+B hides the left side, as in VS Code; Ctrl+Alt+P the panel and Ctrl+Alt+C the chat. VS Code's Ctrl+J and Cursor's Ctrl+L are kept by the browser (Downloads and the address bar in Chrome), so a web page cannot use them. The three splitters are keyboard resizable. Sizes and hidden regions are kept in the browser (`localStorage`), and the page works the same when storage is blocked.
* The review view (ADR-0172) has no chat column and no chat toggle.
* The code is `play-shell.js` and `play-shell.css`. `play.html` moves the regions; the shell script only watches `hidden` on the panel's sections and on the plan banner, sets layout attributes on `body`, and mirrors the model name and the selection into the status bar. A section another script shows comes to the front of the panel.
* Diagram tabs that do not fit behave as in VS Code: the strip scrolls (the mouse wheel scrolls it sideways), the edge that hides tabs fades, the chosen tab is scrolled into view, and a **More tabs** button (») lists every tab, marking those out of view. Buttons beside the strip (Fit, zoom, and any a view adds) never cover it. Checked at 1280, 1440, 1600 and 1920 pixels wide, with the chat open and closed.
* The side columns give way before the diagram does: the centre keeps at least 520 pixels, and the chat narrows first.

### Consequences

* Good: the chat and the inspector no longer move. Run output has one place. The title bar holds the name, the command center and three toggles; the toolbar holds what runs the model.
* Good: everything is where an engineer from Visual Studio, VS Code, Cursor or draw.io would look first.
* Bad: the window needs about 1100 pixels of width for all three columns. Below that, the side columns narrow; hiding one is a keypress.
* Bad: `play.html` changed shape, so open branches that edit its sidebar will conflict once. The ids did not change.
* Bad: the panel shows one of Run, Simulation and Running app at a time, where the sidebar could show two. The tabs show which have something.
* Revisit when: a usability study (owed under ADR-0170) shows people missing the panel or the checks popover.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| Golden Layout 2 (MIT) | Owns each pane's DOM and lifecycle; the page's scripts address fixed ids | Adopt if PlayIDE needs floating or user-arranged panes |
| Dockview (MIT), FlexLayout (MIT) | React or a bundler; PlayIDE is plain scripts with no build step | — |
| Split.js (MIT) | Would cover the splitters, but CSS grid plus pointer capture is shorter than the adapter | Swap in if more splitters appear |
| VS Code workbench layout, Visual Studio tool windows, Cursor agent panel, Codex app, draw.io (patterns) | Layouts and shortcuts only; no code or icons copied | — |
