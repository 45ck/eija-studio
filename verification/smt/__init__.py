"""SMT (Z3) soundness proof of the protected excursion policy.

Establishes, over the symbolic Transition grammar and under the stated assumptions, that
`eija_studio.domain.policy.check_policy` admits only authority-preserving candidates. It does not
prove the runtime, the SQLite adapter or the Python interpreter correct.
"""
