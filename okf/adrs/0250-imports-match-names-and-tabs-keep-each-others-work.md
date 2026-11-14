---
type: Architecture Decision Record
title: 'ADR-0250: An import matches renamed and respaced names, and two tabs keep each other''s work'
description: A second, deeper inspection of saving and UML interchange followed ADR-0245.
resource: repo://docs/adr/0250-imports-match-names-and-tabs-keep-each-others-work.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0250-imports-match-names-and-tabs-keep-each-others-work.md
  title: 0250-imports-match-names-and-tabs-keep-each-others-work.md
  hash_method: lf-sha256-v1
  sha256: 3c492b8a38d309283df1451aa27a5b2bf3921c8db352746d15509dd8da69bdc0
notes_baseline: 80bfaa426767f40db1a08341ca744d976d99a04fe7a86f2b8fe067da0a0877b0
---

# ADR-0250: An import matches renamed and respaced names, and two tabs keep each other's work

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-14 |
| Lane | PlayIDE saving and UML interchange (second inspection, 2026-11-14) |
| Source | `repo://docs/adr/0250-imports-match-names-and-tabs-keep-each-others-work.md` |

## Decision outcome (verbatim)

> * `interop/names.py`: `same_names` maps a read name to the model state it equals but for spacing, reported under
>   "Kept or filled in"; `renames` plans `rename_state` first, and the rest of the difference is planned on the renamed model.
> * `interop/kept.py` `keep_text`: descriptions and enumeration literals that differ only in spacing are the current
>   ones; where the format has no notes on attributes (`Parsed.attribute_notes` is false for Mermaid), the current
>   descriptions are kept.
> * PlantUML writes `"`, a leading `'` and `/'` as `<U+XXXX>`, and writes a state named like a keyword by its alias.
> * `draft.json` gets a `revision`. Save and Clear send `base`; a different saved revision is refused with
>   `DRAFT_CHANGED` (409). The check and the write hold the systems lock, so a save cannot land in a system opened in
>   between. A caller that sends no `base` (the CLI, older pages) is not checked.
> * Each browser draft names its tab. A tab keeps another tab's draft under its own earlier key before writing or
>   clearing the key, says once that the system is open in another tab, and drops its own earlier copy when it writes again.
> * `load_pack(..., claim=False)` reads a pack without filing the snapshot under that folder; the template list and the
>   workflows beside the open system use it.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0240: Composite states](/adrs/0240-composite-states.md) - Issue #93, item 3.
* [ADR-0245: A partial UML read keeps what it could not read, and a save names its system](/adrs/0245-partial-reads-keep-and-saves-name-their-system.md) - A Fagan-style inspection of everything that keeps or moves a model (undo and redo, browser autosave, Save and the systems home, UML import and export) found te…
<!-- okf:generated:end links -->
