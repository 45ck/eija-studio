"""The registry of evidence kinds the kernel can assess (ADR-0145).

A kind that is not registered here is UNKNOWN by construction: the kernel has no authority to establish a
claim it has no admissibility rule for. Adding a kind (a TLC model check, a property test, a mutation score)
means adding a module with a typed artifact shape and a pure ``check``, and one line here; nothing else in
the kernel changes.
"""
from __future__ import annotations

from .formal import KindSpec
from .formal_bend import SPEC as BEND_PROOF
from .formal_bmc import SPEC as BOUNDED_MODEL_CHECK
from .formal_smt import SPEC as SMT_PROOF

KINDS: dict[str, KindSpec] = {spec.kind: spec for spec in (BEND_PROOF, SMT_PROOF, BOUNDED_MODEL_CHECK)}
