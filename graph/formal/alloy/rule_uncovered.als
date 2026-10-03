// Pilot: the rule "requirement without a verifier" written in Alloy by hand, to compare the Alloy route with the
// clingo route on the same rule (graph/formal/eijaref/asp.py, program "uncovered" in graph/bench/formal_checks.py).
// IR form:  verified(R) :- verifies(T, R).   violation(R) :- requirement(R), not verified(R).
//
// Three questions, all bounded by their declared scope:
//   fires        can the rule fire at all (is it dead)?                          expect an instance
//   silent       is it silent whenever a verifier exists (the rule's meaning)?  expect no counterexample
//   joint        is there a non-trivial graph on which the rule is silent?       expect an instance
// The Alloy model is hand-written here; a generated route (IR to Alloy) is not built, see OBLIGATIONS.md.

sig Node { verifies: set Node }      // t -> r means: t verifies r
sig Requirement in Node {}

pred verified[r: Node]  { some verifies.r }
pred violation[r: Node] { r in Requirement and not verified[r] }

run   fires  { some r: Node | violation[r] } for 3 expect 1
check silent { all r: Requirement | verified[r] implies not violation[r] } for 5 expect 0
run   joint  { some Requirement and some verifies and no r: Node | violation[r] } for 4 expect 1
