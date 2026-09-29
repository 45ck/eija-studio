// Bounded mechanical check of the two certificate theorems in graph/formal/eijaref (closure.py, order.py).
//
// What this is: a model of the CHECKERS' acceptance conditions, not of the Python code. Each predicate
// below is named after the condition it mirrors (a, b1, b2, b3, c in closure.py; s1..s3 in order.py).
// What a green run means: no counterexample exists with at most 7 nodes (bounded). It does not prove the
// theorems for larger graphs; the paper proofs in the design document do that, and this run is a check
// on the STATEMENTS (each condition is necessary: dropping any one produces a counterexample).
// Drift between this file and closure.py/order.py is guarded by graph/formal/run_alloy.py (see OBLIGATIONS.md).

sig N { e: set N,            // the edge relation
        parent: lone N,      // certificate: derivation parent
        rank: lone Int,      // certificate: derivation rank (only meaningful on C minus R)
        label: lone N }      // certificate for SCC labelling

one sig Cert { R: set N, C: set N }

// ---- closure certificate ---------------------------------------------------------------------
pred a  { Cert.R in Cert.C }
pred b1 { all n: Cert.C - Cert.R | some n.parent and n in n.parent.e }
pred b2 { all n: Cert.C - Cert.R | n.parent in Cert.C }
pred b3 { all n: Cert.C - Cert.R | some n.parent.rank and some n.rank and n.parent.rank < n.rank }
pred c  { all u: Cert.C | u.e in Cert.C }
fun lfp: set N { Cert.R.*e }

assert soundness       { (a and b1 and b2 and b3 and c) implies Cert.C = lfp }
assert unreachable     { all t: N | (a and c and t not in Cert.C) implies t not in lfp }
// Mutants: each drops one condition and MUST have a counterexample.
assert mutant_no_a     { (b1 and b2 and b3 and c) implies Cert.C = lfp }
assert mutant_no_b1    { (a and b2 and b3 and c) implies Cert.C = lfp }
assert mutant_no_b2    { (a and b1 and b3 and c) implies Cert.C = lfp }
assert mutant_no_b3    { (a and b1 and b2 and c) implies Cert.C = lfp }
assert mutant_no_c     { (a and b1 and b2 and b3) implies Cert.C = lfp }

check soundness    for 7 but 4 Int expect 0
check unreachable  for 7 but 4 Int expect 0
check mutant_no_a  for 7 but 4 Int expect 1
check mutant_no_b1 for 7 but 4 Int expect 1
check mutant_no_b2 for 7 but 4 Int expect 1
check mutant_no_b3 for 7 but 4 Int expect 1
check mutant_no_c  for 7 but 4 Int expect 1
run   accepted_nonvacuous { a and b1 and b2 and b3 and c and some Cert.C - Cert.R and some e } for 7 but 4 Int expect 1

// ---- SCC labelling certificate ---------------------------------------------------------------
pred same[x, y: N] { x.label = y.label and some x.label }
pred s0 { all n: N | some n.label and n.label in N and n.label.label = n.label }        // total, representative in own class
pred s2 { all x, y: N | same[x, y] implies y in x.*(e & label.~label) }                  // strongly connected inside the class
fun q: N -> N { { a, b: N | some x, y: N | x.label = a and y.label = b and x->y in e and a != b } }
pred s3 { no a: N | a in a.^q }                                                          // quotient is acyclic
fun scc: N -> N { { x, y: N | y in x.*e and x in y.*e } }

assert scc_soundness   { (s0 and s2 and s3) implies (all x, y: N | same[x, y] iff x->y in scc) }
assert scc_no_s3       { (s0 and s2)        implies (all x, y: N | same[x, y] iff x->y in scc) }
assert scc_no_s2       { (s0 and s3)        implies (all x, y: N | same[x, y] iff x->y in scc) }
check scc_soundness for 6 expect 0
check scc_no_s3     for 6 expect 1
check scc_no_s2     for 6 expect 1
