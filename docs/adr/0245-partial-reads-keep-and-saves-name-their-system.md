# ADR-0245: A partial UML read keeps what it could not read, and a save names its system

* Status: accepted
* Date: 2026-11-13
* Lane: PlayIDE saving and UML interchange (inspection of 2026-11-13)

## Context and problem statement

A Fagan-style inspection of everything that keeps or moves a model (undo and redo, browser autosave, Save and the
systems home, UML import and export) found ten defects. The full log, with severity and location, is
[INSPECTION-SAVE-IMPORT](../engineering/INSPECTION-SAVE-IMPORT.md). Three of them break promises earlier decisions made:

* Issue #165 (ADR-0190) says a partly read file removes nothing. Only arrows a reader *parsed* but could not map
  counted as "not read". An arrow the reader did not parse at all (`A -left[#red]-> B`, `B <-- A`, `A ->> B`), an arrow
  through a `<<choice>>` pseudostate, or a labelled draw.io connector to a rhombus was reported, then forgotten. The
  import offered a plan that removed that transition. A `<<choice>>` pseudostate even became a state, and the plan
  retargeted a transition to it.
* The class model import treats the file as the whole class model. An attribute it could not read (a class-typed
  attribute, say) or an association with a `2..5` end was therefore deleted from the candidate `data.json`, and the
  summary said "Classes reordered" when an association changed.
* ADR-0185 serves one system at a time. A second tab still showing the system it opened on saved its work over the
  other system's `draft.json`, and "Clear saved work" cleared it.

## Decision drivers

* Nothing is dropped silently, and nothing the file still has is removed by an import (ADR-0190, issue #165).
* Saving never loses work that was saved before.
* No new store and no new format: the fixes stay inside the existing report, `draft.json` and browser keys.

## Considered options

* For partial reads: (a) each reader counts every state machine part it drew but could not read; (b) parse more
  PlantUML syntax so fewer arrows are unread. Both are done: (a) is the guarantee, (b) reduces how often it is needed.
* For the class model: (a) keep every current class, attribute and association when any part was not read, as the
  state machine does; (b) keep only the current element whose name the file used for what could not be read. (b) is
  chosen: a class the file leaves out on purpose is still removed, and only what the file has but PlayIDE could not
  read is kept.
* For the stale tab: (a) a version number on `draft.json`; (b) the page names the system it opened on, and the server
  refuses a save or clear for another. (b) is chosen: it needs no new state, and it is exactly the condition.

## Decision outcome

* `Parsed.unread_part` records a transition or region that was drawn but not read, and `Parsed.pseudostate` a
  pseudostate. `Parsed.settle()` runs after every reader: an arrow to or from a pseudostate becomes an unread part, and
  a pseudostate is never a state. The import's partial count adds these, so it removes nothing.
* PlantUML arrows read the style before or after the direction (`-left[#red]->`) and backward arrows (`B <-- A`). A
  line that still looks like an arrow and is not read counts as unread.
* `ImportReport.unread` holds each attribute (class, name) and association (source, target, role) the file has but
  could not be read. The current model's own element with that key is kept in its place and listed under "Kept or
  filled in". `changes` also lists associations added, removed and changed, and a new record class.
* Save and "Clear saved work" send `pack`, the system the page opened on. The server refuses another with
  `SYSTEM_CHANGED` (409), and the page shows the message. Without `pack` (older pages, the CLI) nothing changes.
* In the page: a browser draft written on an earlier model moves to `<draft key>:earlier` before anything can
  overwrite it, and is offered again on later loads until it is reopened. Undo and redo reload the model's own screens
  after the restore ends, so an edit made while they load is kept in the history and in the browser. When storage
  cannot hold even the current snapshot, the older draft under the key moves aside as an earlier draft, so a reload
  does not bring it back as the latest work.

### Consequences

* Good: a partly read file can no longer offer a plan or a `data.json` that drops what it failed to read, and a stale
  tab cannot overwrite another system's saved work.
* Bad: a file with a stray arrow-like line that is not a transition now removes nothing, so a deliberate removal in
  that file must be drawn on the diagram instead. The report says why.
* Revisit when: PlayIDE serves more than one system at a time, or reads pseudostates (then a transition through a
  choice could be read as its branches).

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| none: no new module | The fixes are in the existing readers, mapping and routes (ADR-0190, ADR-0185, ADR-0198) | n/a |
