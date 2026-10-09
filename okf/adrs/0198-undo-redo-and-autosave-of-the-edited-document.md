---
type: Architecture Decision Record
title: 'ADR-0198: Undo, redo and autosave of the edited document in PlayIDE'
description: PlayIDE is meant to be more robust than the UML tools engineers already use, and every one of those has undo.
resource: repo://docs/adr/0198-undo-redo-and-autosave-of-the-edited-document.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0198-undo-redo-and-autosave-of-the-edited-document.md
  title: 0198-undo-redo-and-autosave-of-the-edited-document.md
  hash_method: lf-sha256-v1
  sha256: 5221439c5eaa7a7417821e557471bb56d52232545826aa089930ac0eb3369724
notes_baseline: 0bb87a2c802ae90eda7bf85c6f749a78ed8c79213750952dd04cd587ea399d67
---

# ADR-0198: Undo, redo and autosave of the edited document in PlayIDE

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-08 |
| Lane | PlayIDE (owner direction, 8 October 2026: beat existing UML tools on robustness) |
| Source | `repo://docs/adr/0198-undo-redo-and-autosave-of-the-edited-document.md` |

## Decision outcome (verbatim)

> Chosen option: snapshots, because what a person edits in PlayIDE is already one small document and the server already checks any version of it.
>
> * **The document.** The plan (its typed steps, AI or drawn, which are accepted, and the AI's metadata) and the screens edited in the designer. The model in force is never edited in PlayIDE, so it is not part of it. View state (the preview, the server's verdict, the ripple, the card in the chat) stays out.
> * **History.** Every edit takes a snapshot after it is made, with a label in the page's own words ("add state Archived", "let Librarian take MarkOverdue", "reject step 1", "relabel dueDate"). Up to 100 are kept. **Undo** and **Redo** move between them: the toolbar arrows (their tooltips name the edit), Ctrl+Z, and Ctrl+Shift+Z or Ctrl+Y. The status bar says what was undone. Keys typed in an input, text area, select or editable element are left to the browser.
> * **Restoring.** The plan is put back as it was, its card in the chat re-enabled, and the server asked to check and preview it again, so a step that no longer applies says so. A drawn plan that is undone away disappears from the chat; an AI plan that is undone away stays as a record marked "Undone." and comes back on redo.
> * **Autosave.** Each snapshot is written to `localStorage` (`playide.draft.v1:<pack>:<case>`) as it is made, with up to 30 history entries either side of the current one; if storage is full, the current document alone is kept. The status bar says "Saved in this browser", or that storage is unavailable. When the document is empty the draft is removed.
> * **Recovery.** On load, a kept draft comes back with its history and a note in the chat ("Recovered your unsaved work from …: 2 plan steps and screen edits"), with **Discard it** (itself undoable). If the model in force has changed since, the note says that every step is checked against it again.
> * **With Save (ADR-0185).** Opening a saved draft and importing a UML file are undoable edits too ("open the saved work", "import a UML file"). Work this browser kept is never older than a save, because every edit is kept as it is made and a save does not clear it, so when it comes back on load the saved draft is not opened over it; the Save mark then compares the recovered work with the saved draft.
> * **For saving to a file.** `window.PlayIDE` gains `document()`, `restore(doc, label)` (opens a document as an undoable edit), `undo()`, `redo()` and `history()`. Every edit fires `playide:edit` and `hooks.edit`. Saving and opening a system is another feature's job; it builds on these rather than keeping its own copy.

## Sections

* Context and problem statement
* Decision drivers
* What existing tools do
* Considered options
* Decision outcome
* OSS check (required for any custom module)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0156: Chat plan mode proposes typed steps the person accepts or rejects](/adrs/0156-chat-plan-mode-proposes-typed-steps.md) - The owner's roadmap asks for an AI chat sidebar "like T3 Code, with plan mode prominent", in which the AI proposes changes to the UML and the person accepts or…
* [ADR-0172: A read-only review view of PlayIDE for people who review the model](/adrs/0172-review-view-for-reading-the-model.md) - The owner set the audience as people who know UML, and noted that UML "is meant for non technical people to review it sometimes".
* [ADR-0185: Start, open and save your own system in PlayIDE](/adrs/0185-start-open-and-save-your-own-system.md) - PlayIDE could only show the pack the server was started with (`eija serve --pack …`), and every pack was one that ships with EIJA.

## Referenced by

* [ADR-0201: Build a new system in chat, round after round](/adrs/0201-build-a-new-system-in-chat-round-after-round.md) - The showcase changes a pack that already exists (Library loan).
<!-- okf:generated:end links -->
