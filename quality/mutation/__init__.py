"""Mutation analysis of the kernel test suite: an adapter around cosmic-ray (ADR-0033).

The mutation engine is the OSS tool cosmic-ray. This package holds only EIJA-specific glue: which
modules are targeted and with which tests, an isolated scratch workspace so the real checkout is
never mutated, result classification, the ratchet threshold and the survivor report.
"""
