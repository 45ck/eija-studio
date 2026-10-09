# ADR-0198: Undo, redo and autosave of the edited document in PlayIDE

* Status: accepted
* Date: 2026-10-08
* Lane: PlayIDE (owner direction, 8 October 2026: beat existing UML tools on robustness)

## Context and problem statement

PlayIDE is meant to be more robust than the UML tools engineers already use, and every one of those has undo. PlayIDE had none. A wrong click on an inspector tool, an AI plan that replaced the one being checked, or a screen field removed by mistake could only be put back by hand. Nothing survived a reload either: a crashed tab or an accidental refresh threw away the plan, its ticks and every screen edit.

## Decision drivers

* Every kind of edit undoes the same way: drawing from the palette, the inspector's tools, the Delete key, an AI plan, ticking or unticking a step, taking a follow-on, and each screen edit.
* Nothing restored is trusted. The model is still decided by the server: an undone or recovered plan is checked again, like any edit (ADR-0156).
* No second source of truth. Undo must not invent another representation of the model.
* A crash or reload loses no edit that was made.
* Text boxes keep the browser's own text undo.
* The read-only review view (ADR-0172) neither offers undo nor restores a draft.

## What existing tools do

| Tool | How it undoes and keeps work | What PlayIDE takes from it |
|---|---|---|
| maxGraph `UndoManager` (Apache-2.0, already vendored) | Records changes to the graph's cells and undoes them. | Nothing directly: PlayIDE's diagrams are views redrawn from the plan, so undoing cells would undo the picture, not the edit. |
| [Immer](https://github.com/immerjs/immer) patches (MIT) | Produces a patch and its inverse for each change to an immutable state tree. | The idea of whole-document versions. Not the library: the document is small JSON, so a snapshot is simpler than patches and needs no dependency. |
| [Yjs](https://github.com/yjs/yjs) `UndoManager` (MIT) | Undo scoped to one user over a shared CRDT document. | Reference for later collaborative editing; a CRDT is far more than one person's undo needs. |
| [Javascript Undo Manager](https://github.com/ArthurClemens/Javascript-Undo-Manager) (MIT) | A stack of command pairs (do and undo). | Rejected: each PlayIDE edit is an asynchronous server check, so an inverse command would still have to ask the server; restoring the document and asking once is simpler. |
| VS Code hot exit, draw.io drafts | Unsaved work is kept on every change and brought back on the next start, with a way to discard it. | The behaviour: keep on every edit, recover on load, say so, offer Discard. |

## Considered options

* **Snapshots of the edited document** (chosen).
* **maxGraph's `UndoManager`** on each diagram: it would undo cell changes on one diagram, not plan steps or screens, and the next redraw from the server would put them back.
* **Inverse commands** for each kind of edit: as many inverses as there are edit kinds, each still needing a server round trip.

## Decision outcome

Chosen option: snapshots, because what a person edits in PlayIDE is already one small document and the server already checks any version of it.

* **The document.** The plan (its typed steps, AI or drawn, which are accepted, and the AI's metadata) and the screens edited in the designer. The model in force is never edited in PlayIDE, so it is not part of it. View state (the preview, the server's verdict, the ripple, the card in the chat) stays out.
* **History.** Every edit takes a snapshot after it is made, with a label in the page's own words ("add state Archived", "let Librarian take MarkOverdue", "reject step 1", "relabel dueDate"). Up to 100 are kept. **Undo** and **Redo** move between them: the toolbar arrows (their tooltips name the edit), Ctrl+Z, and Ctrl+Shift+Z or Ctrl+Y. The status bar says what was undone. Keys typed in an input, text area, select or editable element are left to the browser.
* **Restoring.** The plan is put back as it was, its card in the chat re-enabled, and the server asked to check and preview it again, so a step that no longer applies says so. A drawn plan that is undone away disappears from the chat; an AI plan that is undone away stays as a record marked "Undone." and comes back on redo.
* **Autosave.** Each snapshot is written to `localStorage` (`playide.draft.v1:<pack>:<case>`) as it is made, with up to 30 history entries either side of the current one; if storage is full, the current document alone is kept. The status bar says "Saved in this browser", or that storage is unavailable. When the document is empty the draft is removed.
* **Recovery.** On load, a kept draft comes back with its history and a note in the chat ("Recovered your unsaved work from …: 2 plan steps and screen edits"), with **Discard it** (itself undoable). If the model in force has changed since, the note says that every step is checked against it again.
* **With Save (ADR-0185).** Opening a saved draft and importing a UML file are undoable edits too ("open the saved work", "import a UML file"). Work this browser kept is never older than a save, because every edit is kept as it is made and a save does not clear it, so when it comes back on load the saved draft is not opened over it; the Save mark then compares the recovered work with the saved draft.
* **For saving to a file.** `window.PlayIDE` gains `document()`, `restore(doc, label)` (opens a document as an undoable edit), `undo()`, `redo()` and `history()`. Every edit fires `playide:edit` and `hooks.edit`. Saving and opening a system is another feature's job; it builds on these rather than keeping its own copy.

### Consequences

* Good: one mechanism covers every edit kind, and new edit kinds join by calling `commit(label)`.
* Good: nothing restored is trusted; the server checks every version.
* Good: a reload or crash loses nothing; recovery is visible and can be discarded.
* Bad: the draft lives in one browser profile. Another browser or machine does not see it, and clearing site data removes it. Saving to a file is the durable path.
* Bad: two tabs on the same model write the same draft; the last edit wins.
* Revisit when: collaborative editing is wanted (then Yjs).

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| maxGraph `UndoManager` | Undoes diagram cells, which are views redrawn from the plan | None needed |
| Immer, Javascript Undo Manager | A dependency for a few dozen lines over a small JSON document; inverse commands would still need the server | Adopt Immer patches if the document grows large |
| Yjs | A CRDT for one person's undo | Adopt with collaborative editing |
