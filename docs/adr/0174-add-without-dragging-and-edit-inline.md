# ADR-0174: Add UML elements without dragging, and edit them where they are

* Status: accepted
* Date: 2026-10-08
* Lane: PlayIDE (owner direction, 8 October 2026)
* Related: ADR-0157 (drawn edits and the checks ring), ADR-0172 (review view), ADR-0173 (workbench shell)

## Context and problem statement

After watching the showcase cut, the owner said "dragging sucks kind of" and asked whether to "use a modal when dragging or not even just edit inline?". Since ADR-0157 the only pointer way to add a state, a transition or the initial state was to drag a palette item onto the diagram; pressing an item opened a form in the inspector on the far left, away from where you were looking. A drag is a long, precise gesture: you hold the button across the screen, and a slip drops nowhere. Then the name went into a form in another region.

## Decision drivers

* People who use PlayIDE already use draw.io, Visio or an IDE designer. Those tools let you pick a shape and click to place it, double-click empty space to add, and double-click a shape to edit its text in place.
* Edit where you look. The editor for an element appears next to it, not in another panel.
* Nothing blocks. No modal: the diagram, the plan and the chat stay usable, and Escape always gets you out.
* Every gesture still makes one typed step that joins the plan and is checked by the server (ADR-0156, ADR-0157). The new gestures decide nothing.
* Keyboard users need no pointing, and the review view changes nothing (ADR-0172).

## Considered options

* Pick, then click, with a small editor where you click (chosen).
* A modal dialog after each drop. Rejected: it covers the diagram you are designing, adds a dismissal to every edit, and the owner was unsure about it.
* Keep drag only and enlarge the drop targets. Rejected: the drag itself was the complaint.
* maxGraph's built-in in-place label editor. Rejected for adding: a new state needs a name before it exists, and a transition needs an action and a role from the pack's fixed lists, which a text editor cannot offer. Renaming could use it, but one editor for every gesture is simpler to learn and to test.

## Decision outcome

| Gesture | What happens |
|---|---|
| Click State in the palette, then click the diagram | A name editor opens at that point. Clicking on a state places the new state after it. |
| Click Transition, then the state it leaves, then the state it goes to | An editor under the target asks only for the action and who may take it. Clicking the same state twice makes a self-transition. |
| Click Initial, then a state | The step is added at once. |
| Double-click empty space | A new state's name editor opens there. |
| Double-click a state | Rename it in place. |
| Double-click a transition | Change who may take it. |
| Drag from the palette (kept) | Drops into the same editor, at the drop point. |
| Enter or Space on a palette item | The full form opens in the inspector, as before, so the keyboard needs no pointing. |

* An armed palette item shows as pressed, the cursor becomes a crosshair and the hint under the diagram says what to click next. A tool places one element and is put down; Escape or clicking the item again puts it down sooner.
* In the editor, Enter adds the step to the plan and Escape drops it. Clicking elsewhere drops an editor that is still empty; one with something typed stays until Enter or Escape.
* The review view ignores every one of these gestures.
* The code is in `play.js` (`arm`, `inlineEdit`, `onCanvasClick`, `onCanvasDoubleClick`, `wireCanvas`) and `play.css`. It reuses `formFor` and `addStep`, so the steps are the same typed transactions as before. The demo recorder gains `Scene.click_at` for clicking a point on the diagram.

### Consequences

* Good: adding a state is two clicks and a name, with the name typed where the state goes. Renaming is a double-click.
* Good: no modal, and drag still works for people who like it.
* Bad: the state machine is laid out automatically, so a new state appears where the layout puts it, not exactly where you clicked. The editor opens where you clicked.
* Bad: gestures that are not visible have to be learnt; the hint under the diagram names them, and the palette items' tooltips say what to click.
* Revisit when: a usability study (owed under ADR-0170) shows people missing the double-click gestures, or the class and use case diagrams become editable.

## Amendment, 9 October 2026: shapes land where you put them

The owner tried it and wrote that a dragged state did not "put it in the right place". It did not. The state machine was laid out again by Dagre after every step, and fitted to the window again, so a new state went wherever the layout put it. The plan banner that appears with the first step also pushed the canvas down by about 46 pixels. Dragging a state to move it worked until the next redraw, then it snapped back. The class, use case and component diagrams did the same, and pressing on a class's attribute row did not take hold of the class.

* A state you place by clicking or dropping is centred exactly where you clicked or let go, at any zoom. Before you commit, a dashed outline shows where it will land. A transition shows a dashed line from the state it leaves to the pointer, and the state under the pointer is outlined.
* The first gesture on the state machine pins every shape where it is drawn, so nothing you did not touch moves when the plan redraws. A state you drag stays where you let go, and the transitions that touch it route straight again. Any state the AI adds goes below the pinned ones. The view keeps its zoom and scroll across those redraws, and holds still when the plan banner or the panel moves the canvas.
* On the class, use case and component diagrams, a shape you drag stays where you let go for the visit, through preview redraws. Pressing on an attribute row or another fixed part of a shape takes hold of the shape.
* **Tidy** (beside Fit, and in Ctrl+K) forgets every position and lays the diagrams out again. It shows only when something has been placed or moved.
* Positions are presentation only. They never reach the model, the plan or the server. The state machine's positions are kept in this browser per model (`localStorage`), and the page works the same when storage is blocked.
* On the Screens tab, a line shows where a dragged field or attribute will go before you let go.
* Fitting never shrinks the diagram below a readable size (labels of about 10 pixels and up). When the canvas is short, as with the Simulation panel open, the diagram keeps that size and starts at its top left; only the **Fit** button may go smaller (#139).
* On a system you started yourself, the transition editor takes a typed action and role, with the declared ones offered as suggestions, and says when the step will declare a new one (ADR-0201). Template and sample models keep the fixed lists.

## Amendment, 9 October 2026: the diagram stays on camera

The demo dry run (round 11) found three places where the state machine left the canvas on camera.

* On first load at 1280 by 800, the foot of the state machine was clipped by 3 pixels. Fitting now measures the diagram again after scaling, because labels do not scale exactly with the view, and takes off what still overflows. While nobody has placed a shape or moved the view, a canvas that settles to a new height where it stands is fitted again.
* When the plan banner pushed the canvas down, holding the drawing still slid its top (the initial dot) under the banner. Holding still now never moves the top above the canvas margin, and a diagram that was all on screen before the canvas moved is fitted again when it no longer fits.
* With Run or Simulation open, the diagram keeps its readable size from #139 and starts at its top, so a state near the foot, such as Returned, was off screen. Run and Replay now pan, without zooming, to keep the current step and its transition in view. A refused step keeps the state it was refused in.

The code is in `play.js` (`fit`, `holdStill`, `follow`) and `play-run.js`. `tests/test_play_canvas_on_camera.py` checks all three in a real browser.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| maxGraph 0.x `CellEditorHandler` (Apache-2.0, already used) | Edits one cell's label as text; adding needs fields from fixed lists before a cell exists | Use it for renaming if more labels become editable |
| draw.io, Visio, Visual Studio designers (patterns) | Interaction patterns only; no code or icons copied | — |
