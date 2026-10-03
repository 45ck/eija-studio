---
type: Architecture Decision Record
title: 'ADR-0095: The weave compiler and lint rules: violation queries over a typed graph, SARIF diagnostics, expiring suppressions'
description: EIJA wants deterministic, machine-checkable links between code, tests, requirements, the ubiquitous language, UI, diagrams, formal models, evidence and ADRs, and a compiler and linters over the whole set, so that agents…
resource: repo://docs/adr/0095-weave-lint-compile-rules.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0095-weave-lint-compile-rules.md
  title: 0095-weave-lint-compile-rules.md
  hash_method: lf-sha256-v1
  sha256: e770b0d1d795d27e061ce42abb3b193f5c050ef97394473e1378e0cdcb07e543
notes_baseline: feb7c4960a6a55906d4f74295d713fffce3d7b9968d5208b26e70a2be97d5e49
---

# ADR-0095: The weave compiler and lint rules: violation queries over a typed graph, SARIF diagnostics, expiring suppressions

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed |
| Date | 2026-09-29 |
| Lane | weave (aspect lint-compile-rules) |
| Source | `repo://docs/adr/0095-weave-lint-compile-rules.md` |

## Decision outcome (verbatim)

> Chosen option: **B**, because [B1] a benchmark of the same four rules written four ways returned identical results in every engine at every size run, SQL rules are 1 to 6 lines (Python 3 to 13), SQLite's authorizer proves which relations a rule reads, a finding can be reproduced with the stdlib `sqlite3` shell, and pySHACL took 140.6 s for one SPARQL closure rule at 2,000 nodes where SQL took 7 ms. Evidence keys ([B1], [incr], [code] and so on) are those of the design document and of `docs/weave/research/SYNTHESIS.md`. Details, tables and evidence are in [docs/weave/design/compiler-and-lint-rules.md](repo://docs/weave/design/compiler-and-lint-rules.md); record schemas are in [graph/schema/rules.md](repo://graph/schema/rules.md); the machine-readable catalogue is [graph/rules/catalogue.json](repo://graph/rules/catalogue.json).
>
> Sub-decisions:
>
> 1. **Pipeline.** Seven stages: extract, canonicalise and type-check, derive, check, diagnose, propose fixes, project. 14 compile-class rules (name resolution, typing, extraction, canonical form) mark a run `malformed` and block projections; 83 lint-class rules never do (a SUSPECT link must not block the OKF sync that repairs it).
> 2. **Rule language.** SQL violation queries (64 rules), Python (31), tool-backed (2). Datalog, SHACL and Cypher are export targets and optional cross-checks. Rules declare the relations they read with polarity; the loader enforces the declaration (SQLite authorizer for SQL, a deny-by-default accessor for Python) and computes the stratum `max(0, positive reads, negative reads + 1)`. No negation inside a recursive stratum.
> 3. **Verdicts.** PASS, FAIL, NOT_RUN, folded by the chain minimum `FAIL < NOT_RUN < PASS`. Closed-world guard, stated by polarity: findings that are monotone in an incomplete relation (a base relation read positively and directly) are real when seen, so FAIL stands and silence is NOT_RUN; findings that are anti-monotone in it (a negatively read relation: absence, anti-join, `count < min`) or that go through a derived relation can be artefacts of the missing facts, so the rule is NOT_RUN whatever it found. A rule that could not be evaluated at all is NOT_RUN; an empty run is NOT_RUN. Exit codes 0, 1, 2, 3.
> 4. **Catalogue.** 97 rules in 12 categories, all `proposed`, ids stable and never reused; three brief ideas merged into others (WV-021, 030, 035) and one generalised (WV-022 is now the acyclicity template); 15 rules generated from metamodel constraints (two obligations that differ only in the type of the other end, WV-031 UI control and WV-063 symbol, are told apart by the template parameter `peer`, and the validator rejects two template rules with identical parameters); a declared-polarity audit corrected 14 rules that worded a negation but declared only positive reads (strata now 41, 38, 17 and 1 rules at 0 to 3), and the validator now checks that a negation in a statement is matched by a negative read or a reviewed attribute-only entry; six ids (WV-010, 011, 031, 037, 053, 054) are referenced by `graph/schema/metamodel.json` obligations and exist; WV-048 (obligation reduced) and WV-049 (same-author evidence) are the two rules the agent-interface aspect asked for, under those ids.
> 5. **Diagnostics.** SARIF 2.1.0 profile `eija-sarif/v1`: no GUIDs, times, machine, account, command line, absolute paths or baseline state; sorted; `columnKind` explicit; NOT_RUN as a notification plus a `kind: open` result; `message.id` and `arguments` alongside `text`. Identity `eija.finding.v1` is SHA-256 over domain-separated, length-prefixed rule id, sorted subject ids and identity arguments, stored in `partialFingerprints`.
> 6. **Severity and suppression.** Levels error, warning, note, notrun; a `proposed` or `experimental` rule has effective level `note`. Suppressions carry resolving evidence and expire by ledger sequence, release, subject digest or an explicit `--as-of` input, never by the clock; an unevaluable expiry does not suppress. No inline pragmas. Baselines only shrink. Severity, tier, maturity, exemptions and the suppression and baseline files are protected policy pinned by owner-approved digest.
> 7. **False positives.** Soundness class per rule; `may` and `heuristic` rules start at note or warning; every false positive becomes a negative fixture plus a rule or policy change; precision is reported as counts, never as a confidence gate.
> 8. **Incremental evaluation.** Opt-in; per-rule key over relation-slice hashes; early cutoff; `incremental == clean` is the oracle; off by default because the predicted saving is below a second at the current size.
> 9. **Fixes** are proposals (byte-range edits, applicability, precondition hash), fail closed, disjoint, idempotent, at most 10 passes; clearing a SUSPECT link is a human ledger act, not a fix.
> 10. **Testing and governance.** Fire/repair/benign fixture matrix from a catalogue-defined operator vocabulary (389 minimum cases), golden SARIF, polarity property test, permutation harness, rule-source mutation by the mutation lane's engine; adding a rule needs a catalogue entry, fixtures and an ADR-lite line in `graph/rules/decisions.jsonl` (WV-093 checks presence; a promotion gate in the validator checks content: a rule may leave `proposed` only with `alternatives_checked` true and its own alternatives text, and today 94 of 97 entries are declared stubs); a full ADR only for a new relation, node or link type, extractor, dependency, kernel change or stage contract.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://docs/weave/ARCHITECTURE.md`
* `repo://docs/weave/research/SYNTHESIS.md`
* `repo://graph/rules/check_catalogue.py`
* `repo://graph/rules/reference.py`
* `repo://graph/schema/metamodel.json`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.

## Referenced by

* [ADR-0093: Consistency and synchronisation between views: one source per fact, one-way generation, keyed merge](/adrs/0093-weave-consistency-sync.md) - EIJA keeps many views of one system: code, workflow model, diagrams, OKF pages, term registry, UI sidecar, requirements, links, ledger, exports.
* [ADR-0097: Impact, ranking and evidence-status mathematics: fixed points, integer relevance, greedy selection, count vectors, and no confidence percentage](/adrs/0097-weave-impact-ranking-math.md) - The weave graph must answer six questions about a change: what does it affect, what should an agent or a person read, which tests give the cheapest useful re-c…
* [Weave: deterministic linked graph, compiler and linter (`weave`)](/lanes/0089-weave-deterministic-linked-graph.md) - Capability lane with ADR numbers 0089–0112 reserved.
<!-- okf:generated:end links -->
