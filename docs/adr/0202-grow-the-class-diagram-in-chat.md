# ADR-0202: Grow the class diagram in chat

* Status: accepted for systems started in PlayIDE
* Date: 2026-10-09
* Lane: PlayIDE (follows ADR-0201; the owner's standing ask, 9 October 2026, to get the greenfield loop done)

## Context and problem statement

ADR-0201 let a system started from a sketch grow its state machine round after round in chat. Its data model did not grow. A sketch gives the record class one attribute, `title` (ADR-0185), so after any number of rounds the built app's form still had one field. Chat could not add a field, so to vibe code a real app you had to leave PlayIDE and edit `data.json` by hand. ADR-0201 recorded this as its largest open gap.

The kernel transaction vocabulary (`domain.transactions`) changes the workflow only. The data model (`data.json`, ADR-0153) is a separate optional document with its own contract (`domain.data.DataModel`) and its own digest. The policy and the laws never read it.

## Decision drivers

* Do not widen the kernel. The data model is not governed by the policy, so changing it is not a kernel operator, and a new kernel transaction would need a kernel source review (#80).
* The data model's own contract decides whether a result is a data model, as it does for a hand-written `data.json`.
* Saving is not applying (ADR-0185, ADR-0201). Nothing writes `data.json`, and the pack's digest does not change.
* A shipped pack's data model belongs to its owner, just as its vocabulary does (ADR-0201).
* Every view that reads the data model (class diagram, screens, Build & run, conformance, ripple, export) reads the same draft.

## What existing tools do

| Tool | How the data model changes in chat | What PlayIDE takes from it |
|---|---|---|
| Lovable, bolt.new (proprietary) | "Add a size field" edits the schema and the form together | One ask changes the record class, and the form follows it |
| Prisma / Supabase migrations (Apache-2.0) | A schema change is a typed, reviewable step | Each change is a typed step a person can untick |
| Visual Paradigm, StarUML (proprietary) | Attributes are edited on the class diagram | The step reads as the class diagram writes it: `size: {Small, Medium, Large}` |

None of these could be adopted as a library. The change is to PlayIDE's own plan, so no dependency is added.

## Considered options

* **Data-model steps in the same plan, applied to a draft data model held in memory, on systems you started** (chosen).
* **A new kernel transaction for attributes.** One vocabulary, but it would add a kernel operator over a document the kernel does not govern, and it waits on #80's source review.
* **Write `data.json` from chat.** This is the fastest loop, but it changes the system without review, and saving is not applying.

## Decision outcome

Chosen option.

* **Three steps.** `add_attribute` (class, attribute as `domain.data.Attribute`), `remove_attribute` and `set_required` live in `application/data_steps.py`. `parse_step` reads a plan step as one of these, or else as a kernel transaction. They sit in the same plan list as the state-machine steps, so ticking, rounds, undo, Save and reopen all work across both.
* **A draft holds its data model.** `domain.pack.hold(pack, "data.json", data)` returns a copy of the pack that holds the draft data model in memory. The pack document and digest are the same, and `domain.data.data_for` returns the held model. `derive` keeps what a draft holds. `application.data_steps.draft_pack` makes a plan's draft: ADR-0201's declared vocabulary plus the applied data steps. Every PlayIDE route that runs a plan uses it.
* **Checked by the data model's contract.** Each step applies after the accepted data steps before it. A missing class or attribute, or a duplicate attribute, is `EDIT_INVALID`. The result is re-checked by `parse_data`. The state-machine steps still go through the policy as one change.
* **Only on your own system.** On a shipped pack, a data step is `PLAN_DATA_FIXED`: the preview marks it as not applying, and every other route refuses it.
* **The offline proposer can say it.** It understands three phrases: `add field size as choice Small, Medium, Large required`, `remove field notes` and `make notes required`. The type is text unless one is named.
* **What you see.** A step reads `Add attribute size: one of Small, Medium, Large to Order, required`. The verdict and the preview banner add `Order gains size`. While a plan is previewed, the class diagram marks added rows with +, changed rows with ~, and removed rows as struck-through ghosts. "Show me" opens the class it changes. The ripple's class items list the attribute changes, per round with `since` as well.

### Consequences

* Good: a system can be built from a sketch, form included, without leaving chat. The generated app passes conformance on the draft data model (`tests/test_play_data_steps.py`).
* Good: the kernel is unchanged, and a data step can never loosen a law or reach a change case.
* Bad: the draft data model, like the grown vocabulary, is not the model in force until #89 and #80 are decided.
* Bad: chat cannot add a class or an association yet. A choice field's choices are fixed once added (remove the field and add it again to change them).
* Neutral: a shipped pack's class diagram is unchanged.
* Revisit when: #89 decides how a chat plan becomes a change case, or classes and associations are needed.

## Verification

* `tests/test_play_data_steps.py` covers:
  * three rounds that add fields, require one, remove one and mix in a state-machine step;
  * the preview's draft data model and its changes;
  * Build & run passing conformance;
  * the screens, the UML export and the ripple (whole plan and one round) reading the draft;
  * the system's `data.json` left as the sketch wrote it;
  * a saved draft keeping the steps;
  * a shipped pack refusing every data step;
  * malformed and unappliable steps refused;
  * a held data model leaving the pack's digest alone.
* The greenfield demo (`demos/scenarios/playide_greenfield.py`) adds the fields round and asserts the class diagram's `+ size` row.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| Prisma schema engine (Apache-2.0) | A database schema migrator. PlayIDE's data model is a UML class model checked by its own contract, and nothing is migrated | Use it if the built app ever gets a real database schema |
| jsonpatch (BSD) | A JSON Patch over `data.json` would be untyped and could not be described as UML | Typed steps keep each change readable |
