---
type: Module
title: domain.linked
description: 'Linked objects (issue #93 item 4, ADR-0241): the states a record''s linked objects are in, as the checkers try them.'
resource: repo://src/eija_studio/domain/linked.py
tags:
- module
- domain
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/linked.py
  title: domain/linked.py
  hash_method: ast-api-v1
  sha256: ae994ef1f65ff566d9e3705522eafdb5fcf7e4c8478c82baee69a0ee96bfe7f7
notes_baseline: f45f6ef228d4f8e0a98e4db61d5fa730824fa61ba063d9051ec40a13921bf629
---

# domain.linked

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | domain |
| Code | `repo://src/eija_studio/domain/linked.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Linked objects (issue #93 item 4, ADR-0241): the states a record's linked objects are in, as the checkers try them.

A record links to objects of other classes through reference fields (ADR-0235). A workflow may give such an object a
small lifecycle (`Workflow.objects`), and a transition may move it (`Transition.then`). Other records can link to the
same object, so any state of its lifecycle can be the one a step meets. The checkers therefore try a step with its
objects in every state (`combinations`), and the ordinary cases of the built app's oracle use the states a run of this
record alone reaches (`along`).
~~~

## Public symbols

* [`admitting`](/symbols/domain/linked/admitting.md) (function) - The first combination of states (as `combinations` orders them) from which `transition` can move every object it names;…
* [`along`](/symbols/domain/linked/along.md) (function) - For each state a record can reach, the states its linked objects are in when only this record moves them, from every ob…
* [`combinations`](/symbols/domain/linked/combinations.md) (function) - Every combination of states of the objects `transition` moves, one dict per combination; `[{}]` when it moves none.

## Internal imports

* [`domain/models`](/modules/domain/models.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).

## Referenced by

* [application.appgen](/modules/application/appgen.md) - App generation: a reviewed workflow model becomes a runnable app and its conformance oracle (ADR-0150).
* [application.law_proof](/modules/application/law_proof.md) - Prove a pack's laws over every run the kernel allows (ADR-0166).
* [application.scenario_run](/modules/application/scenario_run.md) - Run a pack's scenarios (its test cases) through the kernel, and record new ones (ADR-0177).
* [application.scxml](/modules/application/scxml.md) - The workflow state machine as a W3C SCXML statechart (ADR-0165).
* [domain.linked.admitting](/symbols/domain/linked/admitting.md) - The first combination of states (as `combinations` orders them) from which `transition` can move every object it names; `{}` when it moves none, None when no c…
* [domain.linked.along](/symbols/domain/linked/along.md) - For each state a record can reach, the states its linked objects are in when only this record moves them, from every object in its initial state: the first suc…
* [domain.linked.combinations](/symbols/domain/linked/combinations.md) - Every combination of states of the objects `transition` moves, one dict per combination; `[{}]` when it moves none.
<!-- okf:generated:end links -->
