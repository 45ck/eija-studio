# Review of the inspection pull requests merged on 13 and 14 November 2026 (#250 to #261)

**Date:** 14 November 2026. **Kind:** principal engineering review, one pull request at a time, after the
2026-11-13 Fagan day. **Scope:** #250, #251, #252, #253, #254, #255, #256, #257, #258, #259, #260 and #261 as merged
on main at 41369a25. **Questions asked of each:** does it do what it says; is the fix at the cause or at a symptom;
does its regression test fail without the fix; did a later merge undo or contradict it. Cross-cutting integration
of the whole day is a separate review.

**Regression tests:** `tests/test_todays_pr_review.py`. Each failed on main before its fix (8 failed, 5 passed; after:
13 passed).

## Verdict per pull request

| PR | What it claims | Verdict |
|---|---|---|
| #250 | Defects in AI chat and plan mode | Holds. Fixes are at the cause; tests fail without them. |
| #251 | 11 defects in running and checking a design in place | Holds. |
| #252 | Built app requires a whole operation id (D1) | Holds, and #260's `_operation` keeps it: no default, no truncation. |
| #253 | AI chat inspection, round two | Holds. |
| #254 | Name the file a set-aside draft went to (D2) | Holds. Not fixed here: `set_aside_draft` checks for a free name and then moves the file, so two page loads at the same moment could both pick one name. PlayIDE serves one person, so this is noted only. |
| #255 | Ten defects in saving, undo and UML import | Holds. |
| #256 | Eight diagram editing defects | Holds; the browser suite passes on this branch (124 tests, none skipped once the `hci` extra is installed). |
| #257 | M1 to M5 from the re-inspection of #217 to #252 | Holds; #258 K5 is the same fix as M1 and the two agree. |
| #258 | Eight kernel defects (ADR-0246) | The kernel fixes hold, but K3 was not carried to the SCXML export: **N1**. |
| #259 | Tests, gates and docs | Holds. Its log moved to `docs/quality/inspections/`, while two test modules name a path there that never existed: **N3**. |
| #260 | Ten app generator defects (ADR-0249) | Holds. A whole float version (M3) and the whole operation id (#252) both survive it. |
| #261 | `UNDECLARED_ROLE` in the legacy oracle and both SMT encodings | Holds. `_by_slot` is right because a generated candidate has one transition per action. |

## Defects found and fixed

### N1 (major): the SCXML export ordered any text against a date

#258 (K3) changed `ValueGuard.holds` so that an ordering against a date fails for text that is not a date. The SCXML
export (ADR-0165) still compared such text as a string, and `verification/scxml/differential.py` found it once a
model had such a guard: no shipped pack has one, so the gate stayed green.

library-loan with `CheckOut [due > "2026-01-15"]`, `python -m verification.scxml.differential` on that model:

```text
before  FAIL  due="other": kernel REFUSED VALUE_GUARD_DENIED, chart committed to OnLoan
after   PASS  0 disagreements (due = none, 2026-01-14, 2026-01-15, 2026-01-16, other)
```

Fix: the sender attaches `date_<name>`, and an ordering against a date requires it, as the kernel does.

### N2 (major): the SCXML export compared values of different kinds

The kernel never lets a guard hold across kinds: `[x != "a"]` is false for the number 6 and `[x == 1]` is false for
true. The chart used Python's comparison, which takes `True == 1`, `6 != "a"`, and raises a `TypeError` on
`"6" > 5`. The data model stops such values in a built app, but the export is offered as an independent statement
of the kernel's meaning, and the differential only proved it on values of the guard's own kind.

library-loan with two guards over one attribute on `CheckOut`:

```text
before  [x == 1 and x != false]   x=1:  kernel REFUSED VALUE_GUARD_DENIED, chart committed to OnLoan
        [x > 5 and x != "a"]       x=6:  kernel REFUSED VALUE_GUARD_DENIED, chart committed to OnLoan
        [x > 5]                    x="6": the chart's cond raised TypeError
after   PASS, 0 disagreements; the chart refuses each, as the kernel does
```

Fix: the sender attaches `kind_<name>` (boolean, number, text or none), and each guard's term first requires the
guard's own kind.

### N3 (minor): two inspection test modules named log files that do not exist

`tests/test_appgen_inspection.py` and `tests/test_merged_pr_inspection.py` pointed at
`docs/quality/inspections/2026-11-13-*.md`. The logs are `docs/quality/inspection-2026-11-13-*.md`. Fixed, and a test
now checks that every inspection test module names a log that exists.

## Not fixed, recorded

* The inspection logs of the same day sit in three places (`docs/quality/`, `docs/quality/inspections/`,
  `docs/engineering/`). Moving them would break links in ADRs, the changelog and the knowledge base; the cross-cutting
  integration review owns that choice.
* #254: the set-aside race described above.
