# Policy mutation review: 2026-10-02

The integration run reported 129 policy mutants: 74 killed, 32 surviving and 23 classified as
equivalent, with a score of 0.6981. This failed the existing 1.0 ratchet. New authority tests address
observable gaps without changing policy, production packs, operators or the pass threshold.
The fresh `nox -s mutation_quick` run on 2 October 2026 killed **107** of the 129 generated
mutants, with **zero survivors, timeouts or incompetent mutants** and 22 audited postponed-annotation
exclusions. The executable-body score is **1.0**, meeting the unchanged ratchet. This result is
limited to `domain/policy.py`; it is not a full-kernel mutation score. The raw summary and survivor
report are generated under `reports/mutation/` by that command.

## What the tests add

| Contract | Missing fault classes exercised |
|---|---|
| Compatibility with the Bend adapter | Exact `FORBIDDEN` export; missing attributes remain missing |
| Declared transition creation | Unknown-action code, derived and explicit IDs, keyword calling convention |
| Complete catalogue checking | A first unknown action cannot hide guard and effect errors on later transitions |
| Structured refusals | Exact `codes` and sorted `refs` identify the violated laws and requested transitions |
| Invalid declarations | A parsed unused action missing mandatory guards produces `EDIT_INVALID`, not an unstructured validation exception |
| Meaning boundary | Reading declared commands grants no support; unsupported empty/nonempty and missing meanings never produce candidates |
| Unsupported previews | A coherent forbidden-authority preview remains policy-blocked; supported, empty, absent and structurally impossible meanings produce no alternate preview |
| Pack-specific demos | A library-loan demo uses that pack's renewal meaning; no supported meaning means no invented candidate |

Expected outcomes use named pack declarations, protected authority facts and the public error
contract. The invalid-guard input goes through `parse_pack` and `AddTransition`; no mocked
interpreter or unvalidated model construction is needed. Only test input is malformed.

## Review of every quick-run exclusion

Reviewed policy source SHA-256:
`4c7f975930e9cb86e78076bfd3fb98f77224bdb89ca346895a225740fdcc20bc`.
Positions below refer to that source. All 23 reported exclusions were inspected.

| Function | Line:column | Assessment |
|---|---|---|
| `_pack` | 15:21 | Postponed argument annotation |
| `baseline` | 27:24 | Postponed argument annotation |
| `effects_table` | 32:29 | Postponed argument annotation |
| `forbidden_effects` | 37:33 | Postponed argument annotation |
| `meaning_options` | 41:31 | Postponed argument annotation |
| `transition` | 46:76, 47:34 | Two postponed argument annotations |
| `transition` | 46:91 | **Not equivalent:** `*` to `/` changes accepted calls; exclusion removed |
| `law_violations` | 73:47 | Postponed argument annotation |
| `check_policy` | 77:45 | Postponed argument annotation |
| `policy_refs` | 83:44 | Postponed argument annotation |
| `ensure_policy` | 88:46 | Postponed argument annotation |
| `apply_structural_all` | 106:90 | Postponed argument annotation |
| `apply_transactions` | 114:88 | Postponed argument annotation |
| `meaning_transactions` | 124:53 | Postponed argument annotation |
| `apply_meaning` | 131:63 | Postponed argument annotation |
| `what_if` | 139:57, 139:84 | Postponed argument and return annotations |
| `apply_transaction` | 151:55, 151:89 | Two postponed argument annotations |
| `first_supported_meaning` | 159:39 | Postponed argument annotation |
| `demo_candidate` | 167:30 | Postponed argument annotation |
| `meaning_questions` | 191:50 | Postponed argument annotation |

For each of the 22 annotation edits, compiling the original and edited module without executing
it produced equal function code objects, including nested code constants and calling convention.
The module uses `from __future__ import annotations`; these edits alter postponed annotation
metadata but leave every executable function body unchanged. Inspection of current `src`,
`quality` and `verification` found no consumer resolving this policy module's function annotations.
The agent policy reads persistence Protocol annotations, and OKF reads source AST signatures;
neither drives execution of these policy functions from their type hints.

This supports exclusion from the current **executable-body fault model**, not general equivalence
of annotations. Static typing, generated documentation and `typing.get_type_hints` can observe
the difference. Report wording now states that boundary instead of claiming annotations are
never evaluated. Do not present the resulting score as evidence about type contracts or all code.

The separator edit does change executable calling convention. Keyword arguments allowed by
the original function become invalid, and a formerly forbidden sixth positional argument becomes
accepted. Tests cover the actual public `transition` call and the classifier. The invalid generic
exemption is removed. `engine.parse_dump` classifies only after execution: killed mutants are
never reclassified as equivalent. Cached results already contain classification, so the cache
fingerprint now includes `equivalents.py`; changing the rules invalidates `--resume` results.

## Removed release-target exemptions

These exemptions are outside the quick policy target, but their rationales were demonstrably
invalid. They have been removed rather than left to inflate a later release-target score.

| Removed exemption | Why its rationale was insufficient | Regression evidence |
|---|---|---|
| `Proposal` alternatives limit 4 to 5 in `domain/models.py` | Its rationale assumed four enum interpretations. `Alternative.interpretation` is now a meaning-ID string, so five distinct valid IDs are constructible. | Five individually valid, distinct IDs are accepted as alternatives individually; four fit a Proposal; all five fail specifically with the `alternatives` length error. The classifier now returns no exemption for 4 to 5. |
| Runtime binding keys `case`, `subject`, `command` renamed in `application/runtime.py` | A fresh store records and compares the same changed key, but a persisted pre-change operation has a different binding hash. A retry can become `OPERATION_CONFLICT`. | An actual synthetic operation is persisted and replayed after reopening SQLite, with no new effects. A literal established-format oracle pins its binding. Renaming each key while retaining the same values changes the hash; a disposable row with that altered format causes `OPERATION_CONFLICT`, not replay. The classifier exempts none of the three keys. |

The regressions live in `tests/test_mutation_tooling.py` and use the real Proposal validator and
runtime with disposable SQLite data; no production model or runtime source is changed. They
establish why the exemptions are false. Release mutation targets currently select separate
contract/runtime oracle files, so their next mutation measurement may still expose these faults
as survivors until those selected oracles gain equivalent behavioral coverage. No full-target
mutation score is claimed from this narrow check.

No new equivalence exemption, lower ratchet, adjusted receipt or expected policy outcome was
introduced to make a gate pass.
