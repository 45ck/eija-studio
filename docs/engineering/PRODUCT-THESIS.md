# Product thesis: abstractions, domain and language

Status: owner's thesis, 2026-09-29. In the owner's words: *everything is abstraction, especially in software; the domain and its language are the most important thing; this product lets people see that better and see what agents do.* This document turns that into design and engineering consequences. It is a thesis to be tested, not a proven claim.

## The claims

1. **Software is a stack of abstractions.** The hard part is choosing the right ones and naming them (the domain and its language), not typing code.
2. **The abstractions that matter are the domain's**: concepts, rules, invariants and vocabulary. Not AI-tooling abstractions (agent frameworks, prompt formats, tool protocols), which change every few months while the domain model outlives them.
3. **Agents write code faster than people can read it, but they do not hold the team's model of the domain.** The characteristic failure is silent drift: names, boundaries and rules change a little in every generated diff until code, UI, diagrams, tests and documents no longer describe the same thing.
4. **So people need to see the abstractions, and to see what an agent did to them.** Not the diff first; the change to the model first.

## What follows for EIJA

| Consequence | Testable form |
|---|---|
| The primary object is the **domain model and ubiquitous language** (contexts, aggregates, terms, rules, invariants). Change cases and agent activity are views of *changes to that model*. | The language/DDD tree is a navigation root, not a settings page. Every screen names the abstractions it is about. |
| An agent's change is shown **as a change to abstractions** (terms, rules, relations added, renamed, split, merged) before it is shown as a code diff. | The review screen leads with a semantic diff of the model; the code diff is one click deeper. |
| Renaming, merging and splitting a concept is a **first-class, checked operation** with a computed ripple. | A rename produces the list of affected code symbols, UI labels, diagram elements, tests, requirements and evidence, deterministically. |
| **Drift is a lint error.** | Language-versus-code, language-versus-UI and model-versus-diagram mismatches are diagnostics from the compiler over the linked graph (the weave lane). |
| Evidence attaches to **abstractions and their invariants**, and says what it does not cover. | Each invariant shows its checks (test, property, model check, proof) and their status, with UNKNOWN visible. |

## Non-goals

EIJA does not invent AI abstractions, and it does not claim to make abstractions *correct*. It makes them visible, linked, checked against the code, and reviewable, and it keeps the human decision with the human.

## Reading list (leads to verify; do not cite from this file without opening the source)

Brooks, "No Silver Bullet" (essential versus accidental complexity); Naur, "Programming as Theory Building" (1985: a program embodies a theory held by its programmers); Evans, *Domain-Driven Design* (ubiquitous language, bounded contexts); Parnas, "On the Criteria To Be Used in Decomposing Systems into Modules" (1972); Dijkstra, "The Humble Programmer" (1972); Ousterhout, *A Philosophy of Software Design* (deep modules); Abelson and Sussman, *Structure and Interpretation of Computer Programs* (building abstractions).

## Open questions (owned by the eval work)

Does an explicit, linked domain model measurably improve agent success and human review accuracy? The evaluation design must compare agents with and without the language/graph context, and reviewers with and without the semantic diff, using pass^k and pre-registered tasks. Until that is measured this remains a hypothesis we are building the tool to test.
