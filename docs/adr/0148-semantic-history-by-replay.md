# ADR-0148: Semantic undo and redo by replaying existing typed commands

* Status: accepted for the local owner workbench
* Date: 2026-10-02
* Lane: integration

## Context

The canvas edits a selected Change Case through typed transactions. An accidental edit needs
reversal without removing the owner's original meaning selection, bypassing policy, rewriting
verification receipts or silently recovering an old approval. The case already stores its captured
baseline and effective transaction sequence; SQLite stores the full case JSON and an append-only
audit. It has no complete historical case snapshots or timestamps for legacy edits.

## Decision

Use the existing `apply_transactions` and `apply_transaction` interpreter and policy checker.
`application/history.py` is a replay and presentation adapter, not a new command or inversion
engine. Validate that the selected supported meaning is exactly the transaction prefix. Replay
that prefix atomically, then each owner edit independently, and require exact Workflow equality
with the current candidate. Semantic-hash equality alone would miss ordering changes.

`ChangeCase.transactions` remains the effective sequence. `redo_transactions` is a persisted
stack with its next command at the end and a default empty tuple for existing cases. Undo moves
one owner command to that stack and rebuilds the preceding model. Redo runs the next command
through the same interpreter. A fresh accepted edit discards the redo branch while recording its
commands in the audit. No initial meaning transaction may enter the undo stack, including when
the meaning's atomic batch contains several commands. A supported empty batch still has a
protected meaning selection.

Both commands require the owner's existing `edit` capability, exact expected case version and
an open case. State, version, audit and decision invalidation commit in the same unit of work.
Refused commands leave all of them unchanged. Replaying inconsistent persisted history fails
closed as `HISTORY_INCONSISTENT`; it does not repair source, model or receipts.

Successful edits, undo and redo append events containing actor, time, before/after case version,
transaction and semantic hashes. Receipts, the captured baseline and active baseline are not
changed. Any decision is invalidated; every accepted command returns the case to `PREVIEW`.
An old receipt may become applicable again when the compiler finds the exact verified subject,
but no verification run is fabricated and no decision is restored. Applied or discarded cases
remain closed. Reversing an applied baseline requires a new Change Case and normal review.

GET `/api/cases/{case_id}/history` supplies reconstructed semantic models, active edits, pending
redo commands and actual command audit summaries. It labels them as reconstructions, not case
or evidence snapshots, and invents no legacy timestamps. POST `undo` and `redo` use the same
session, origin, content-type and strict version checks as existing owner edit routes. No new
MCP mutation tool is introduced.

Layout is explicitly outside this semantic history. Undo preserves saved node positions, even
when some positions refer to a state absent in the reconstructed model; the existing projection
only displays positions for current states. Generic browser/text-editor undo must not be
intercepted as semantic undo. The UI must label these controls and fetch canonical state after
each command. Read-only navigation does not restore a historical case or proof state.

## Consequences and validation

No event-sourcing library, inverse-transaction vocabulary, state-machine engine or database
migration is needed. The existing Pydantic contract and SQLite JSON persistence own the stack;
the existing interpreter owns every semantic result. Replay work scales linearly with command
count, while a full history response includes a model per revision. Pagination or validated
checkpoints can be added when measured history size warrants them, without replacing authority.

`tests/test_semantic_history.py` covers atomic prefix protection, two-way round trips, branch
abandonment audit, exact restoration after transition removal and state rename, a second pack,
empty meanings, legacy case defaults, restart persistence, authority/CAS/closed-case refusals,
policy-refused commands, damaged history, transaction rollback, immutable receipts and baseline,
decision invalidation, read-only navigation, excluded layout and HTTP boundaries. The committed
Change Case schema is regenerated from the model. Trusted release identity is not restamped.
