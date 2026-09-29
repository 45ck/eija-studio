"""Independent reference semantics and certificate checkers for the weave (stdlib only).

Purpose: give the weave a second, tiny, separately written definition of every function whose
wrong answer would let a gate pass by mistake. Nothing in this package imports ``eijagraph`` or
``eija_studio``: a bug in the production code cannot hide in its own oracle. Tests and benchmarks
may import the kernel (``eija_studio.domain``) as a third opinion; this package never does.

Scope and honesty (see docs/weave/design/formal-verification-of-weave.md):

* These modules are references and checkers, not proofs. Where a theorem is stated in a docstring
  the proof is on paper in the design document, and the tests check it exhaustively on a stated
  small domain. A green test is a MEASUREMENT on that domain, never a statement about all inputs.
* Every function is deterministic: sorted iteration, no clock, no randomness, no environment.
"""
