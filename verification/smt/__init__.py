"""SMT (Z3) soundness proofs of a domain pack's policy: the hand-written encoding of the default pack, and the
encoding generated from any pack's laws (``laws_gen``, gated by ``laws_gate``).

Establishes, over the symbolic Transition grammar and under the stated assumptions, that
`eija_studio.domain.policy.check_policy` admits only authority-preserving candidates. It does not
prove the runtime, the SQLite adapter or the Python interpreter correct.
"""
