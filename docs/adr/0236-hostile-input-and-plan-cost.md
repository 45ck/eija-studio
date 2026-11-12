# ADR-0236: Hostile input at PlayIDE's edges, and the cost of a plan at the model's limits

* Status: accepted
* Date: 2026-11-12
* Lane: robustness (UML interchange, command line, autosave, plan mode)

## Context and problem statement

Robustness is PlayIDE's stated edge over other UML tools. A fuzzing pass over its edges, recorded in
[HOSTILE-INPUT](../engineering/HOSTILE-INPUT.md), found four kinds of failure:

* **UML import.** A numeric escape beyond Unicode (`#99999999999;` in Mermaid, `<U+FFFFFF>` in PlantUML), a number of
  more than 4,300 digits (which Python will not convert), an XMI bound written with a character such as `²` (which
  `str.isdigit` accepts and `int` refuses), or a draw.io position that is not a number made a reader raise a bare
  `ValueError`. In the IDE that was a 500 with no reason; on the command line, a vague message.
* **Command line.** `eija check-export` printed a traceback for a file holding a JSON list, `null` or deeply nested
  arrays. Every other bad input (a missing file, a folder, non-UTF-8 bytes, invalid JSON, a schema mismatch) printed
  the same sentence, `INPUT_OR_ENVIRONMENT_ERROR`, so a person could not tell which was wrong.
* **Autosave.** A draft kept in browser storage in another shape (written by an older page, cut short, or edited by
  hand) stopped PlayIDE from opening at all, on every reload, until storage was cleared by hand. A `draft.json` saved
  on disk in another shape could fail the same way when reopened.
* **Speed.** The chat plan check re-applied every accepted step before each new one: a 64-step plan (the most a draft
  holds) made about 2,000 applications, about 1.2 s at the model's limits, on every accept or reject.

The plan path (90,000 random proposer plans) and the HTTP API (9,500 random requests to 48 routes) raised nothing.

## Decision drivers

* Untrusted input is refused with a stable code and a sentence a person can act on. It never crashes a request or a
  command, and is never echoed back.
* Nothing the person made is deleted: an unreadable draft is set aside, not dropped.
* The kernel's verdicts do not change. A speed-up must give the same verdicts as before, and a test must prove it.
* Fixes go where the bad input is read. A net catches the next case anyone has not found yet.

## Considered options

* Fix each reader, and put a net in `parse_file` that turns any other reader `ValueError` into `IMPORT_INVALID`
  (chosen). The fuzz test calls the readers directly, under the net, so a new crash still shows up there.
* Only the net. Rejected: a file with one bad escape would then be refused whole, when the escape can be kept as written.
* Coverage-guided fuzzing with Atheris (Apache-2.0) in CI. Deferred: it needs a libFuzzer build of CPython for good
  coverage, and seeded mutation loops found every case here in seconds. Revisit if a reader grows a real grammar.

## Decision outcome

**UML readers.** An escape that names no character is kept as written. A count of more than 18 digits is read as
10^18, which every limit refuses as it would the number itself. An XMI bound must be ASCII digits. A draw.io
position that is unreadable or infinite counts as 0: it only orders what was drawn. `interop.model` holds the
helpers (`whole`, `is_count`, `character`).

**Command line.** `failure_report` names what is wrong: `FILE_NOT_FOUND` and `NOT_A_FILE` (with the path the person
gave), `PERMISSION_DENIED`, `NOT_UTF8` (with the byte offset), `INVALID_JSON` (with line and column),
`SCHEMA_INVALID` (with each field and problem, never the value) and `INPUT_TOO_DEEP`. `check-export` refuses a file
that is not a JSON object.

**Autosave.** The page reopens a browser draft only when its shape is the one it writes. Any other draft is moved to
`<key>:unreadable` and the page opens on the model in force, with a note. If a draft passes the shape check and still
fails to reopen, the page sets it aside and opens anyway. On disk, `GET /api/play/draft` checks `draft.json` against
`SavedWork`; one in another shape is moved to `draft.unreadable.json` and the page says so.

**Plan check.** `_statuses` keeps the model after the steps that applied so far (`plan._Applied`), so each step is
applied once. A 64-step plan at the limits now takes about 70 ms. The verdicts match a replay of every earlier step
on 400 seeded random plans in the fast tests (8,000 in the fuzzing pass), and a test counts the applications.

### Consequences

* Good: every input found by fuzzing is read or refused with a reason, and a seeded test keeps it so.
* Good: a bad draft no longer locks a person out of their own IDE, and their work is kept.
* Good: the plan check is about 17 times faster at the limits.
* Bad: the law proof is still about 0.7 s at the limits (it asks the kernel every action by every class of actor in
  every state). A UML import runs it, so a max-size import takes about 0.7 s. It is a black-box search on purpose:
  skipping actions with no transition from a state would trust a pre-filter instead of the kernel.
* Revisit when: the model's limits grow past 32 states and 64 transitions, or a reader gains a grammar worth
  coverage-guided fuzzing.
