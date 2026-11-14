# ADR-0250: An import matches renamed and respaced names, and two tabs keep each other's work

* Status: accepted
* Date: 2026-11-14
* Lane: PlayIDE saving and UML interchange (second inspection, 2026-11-14)

## Context and problem statement

A second, deeper inspection of saving and UML interchange followed ADR-0245. It round-tripped every shipped pack
through all four formats, including the kernel features they use (composite states, time events, linked objects,
signals, value guards, built associations). Unchanged files came back CLEAN. Files edited the way a person edits
them did not, and neither did names and text that a format writes differently. Two tabs on one system also lost work.
The log, with severity and location, is the second part of [INSPECTION-SAVE-IMPORT](../engineering/INSPECTION-SAVE-IMPORT.md).

* A file is a picture, not a log of edits. A state renamed in it was planned as add, retarget and remove. When the
  state was in a composite (ADR-0240), the plan dropped it from the composite, and when it was a composite's initial
  state, the kernel refused the removal and left an empty state behind.
* Every reader collapses whitespace, so a name or description with a tab, two spaces or a trailing space came back as
  a change. PlantUML wrote `"` as `'`, read a state named `state` as a declaration, and read a line starting with `'`
  as a comment. Mermaid lists attribute descriptions as not carried, and then its import deleted them.
* Two tabs on one system shared one browser draft key, and each tab's Save replaced the other's `draft.json` unseen.
* Listing the templates read every shipped pack, and a snapshot is filed under the folder it was last read from. A
  system whose `pack.json` matched a shipped one (a copy with its own class model) then read the shipped `data.json`.

## Decision drivers

* An import plans the edit the person made, not a longer one that loses what the kernel attached to a state.
* A round trip changes nothing, whatever the names and text are.
* Neither tab can lose the other tab's work, and nothing waits on the other tab.

## Considered options

* For renames: (a) ask the person which states were renamed; (b) plan `rename_state` when a removed state and an
  added state carry exactly the same arrows, and no other pair does. (b) is chosen: it needs no question, the kernel's
  own `rename_state` already keeps composites, and an ambiguous case falls back to add and remove as before.
* For spacing: (a) refuse such names in the kernel; (b) treat a read name that equals one model state but for
  spacing as that state, and keep current text that differs only in spacing. (b) is chosen: it changes no contract.
* For two tabs saving: (a) the last save wins, as before; (b) Save sends the revision of the saved draft the page last
  saw, and the server refuses another with `DRAFT_CHANGED`. Pressed again, the page sends the revision it was refused
  on, so the person can still replace it on purpose.
* For two tabs autosaving: (a) one key per tab; (b) one key, but each draft names its tab, and a tab moves another
  tab's draft to `<draft key>:earlier:tab-<id>` before it writes. (b) is chosen: recovery on load stays as it is, and
  the other tab's work is offered with Reopen, like any earlier draft (ADR-0245).

## Decision outcome

* `interop/names.py`: `same_names` maps a read name to the model state it equals but for spacing, reported under
  "Kept or filled in"; `renames` plans `rename_state` first, and the rest of the difference is planned on the renamed model.
* `interop/kept.py` `keep_text`: descriptions and enumeration literals that differ only in spacing are the current
  ones; where the format has no notes on attributes (`Parsed.attribute_notes` is false for Mermaid), the current
  descriptions are kept.
* PlantUML writes `"`, a leading `'` and `/'` as `<U+XXXX>`, and writes a state named like a keyword by its alias.
* `draft.json` gets a `revision`. Save and Clear send `base`; a different saved revision is refused with
  `DRAFT_CHANGED` (409). The check and the write hold the systems lock, so a save cannot land in a system opened in
  between. A caller that sends no `base` (the CLI, older pages) is not checked.
* Each browser draft names its tab. A tab keeps another tab's draft under its own earlier key before writing or
  clearing the key, says once that the system is open in another tab, and drops its own earlier copy when it writes again.
* `load_pack(..., claim=False)` reads a pack without filing the snapshot under that folder; the template list and the
  workflows beside the open system use it.

### Consequences

* Good: renaming a state in Visual Paradigm, PlantUML or draw.io becomes one rename step; awkward names round-trip.
* Good: two tabs cannot silently replace each other's saved or kept work.
* Neutral: a rename whose arrows match several states is still planned as add and remove.
* Neutral: scenario steps accept only identifier-like state names, while a state may be named freely. This is noted
  for the kernel, not changed here.
