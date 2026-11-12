# Hostile input and scale: how PlayIDE's edges were tested

PlayIDE's claim over other UML tools is robustness. This note records how its edges were attacked on 12 November 2026,
what broke, and what now keeps each fix in place. The decision is [ADR-0236](../adr/0236-hostile-input-and-plan-cost.md).

## What was run

| Edge | How | Volume | Found |
|---|---|---|---|
| UML import (XMI, PlantUML, Mermaid, draw.io) | Seeded mutation of every pack's export in every format (insert markup, escapes, numbers; delete; duplicate), against `import_model` and `start_from_file` | 20,000 files | draw.io position that is not a number |
| UML import, targeted | Escapes beyond Unicode or surrogates, 5,000-digit counts, `²` as a bound, a DTD, 50,000-deep nesting, a 1.9 MB line, 100,000 `[` or `#`, NUL bytes, 3,000-state chains, 40-state complete graphs, 1,000 classes | 30 files | 5 more crash classes (escapes, long counts, `²`) |
| Plan mode | Random proposer plans of 1 to 6 typed steps over every pack, mostly well-formed, through `_steps` and `preview_plan` | 90,000 plans | nothing |
| HTTP API | Random bodies (junk values, real and broken models, plans) to all 48 POST routes, with the systems routes on | 9,500 requests | nothing (no 500) |
| `eija` command | 8 bad files (non-UTF-8, truncated, `[]`, `null`, wrong shape, 100,000-deep, missing, a folder) and 7 bad packs, across 9 commands | 120 runs | `check-export` tracebacks; one vague message for every case |
| Autosave | 11 shapes of a corrupt browser draft, in Chromium | 11 reloads | 5 stop the page opening |
| Large model | `scripts/large_pack.py` (32 states, 64 transitions, 40 classes): every export, import, render and a 64-step plan, timed and profiled | 1 pack | 64-step plan check 1.2 s, from a replay of every earlier step |

## Times at the model's limits

Measured on the max-size pack in a cloud container, one run each:

| Operation | Before | After |
|---|---|---|
| Plan check, 64 steps | 1,197 ms | 71 ms |
| UML import, any format (runs the law proof) | about 700 ms | unchanged |
| Law proof | 659 ms | unchanged |
| Start a system from a UML file | 15 to 62 ms | unchanged |
| Export, any format | 4 to 25 ms | unchanged |
| Render a diagram | 1 to 3 ms | unchanged |
| Build & run (HTTP, small pack) | 2.5 to 3 s | unchanged (appgen lane) |

The law proof is a black-box search: it asks the kernel every action by every class of actor in every state reached.
It stays that way on purpose (ADR-0236).

## What keeps it fixed

* `tests/test_hostile_input.py` (fast tier, about 2 s): every crash input above, a seeded mutation fuzz straight at
  each reader (150 files per format), the plan check against a replay reference on 400 seeded plans, a count of
  structural applications for a 64-step plan, the command line's error codes, and a `draft.json` in five wrong shapes.
* `tests/test_play_history.py::test_a_kept_draft_the_page_cannot_read_is_set_aside_and_the_page_still_opens`
  (browser, opt-in with `EIJA_BROWSER_TESTS=1`): five corrupt browser drafts, each set aside, and a good one still
  recovered.

## Running the fuzzers again

The fuzz loops in the tests are seeded and small. For a longer run, raise the loop counts in a local copy, or change
the seed strings (`hostile-<format>`, `plan-differential`); a failure prints the input that caused it.
