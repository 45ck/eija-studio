---
name: eija-studio
description: Inspect and verify bounded EIJA Change Cases with the local semantic compiler, retaining evidence and human authority boundaries.
---

# EIJA Studio local workflow

Use when a task asks to interpret, compile, inspect, verify or explain an EIJA Change Case. Read the repository AGENTS.md and the declared validation envelope first. This is a repository skill file, not an installed ChatGPT plugin, MCP server or proof backend.

1. State the requested business meaning and unsupported alternatives. Do not silently select or downgrade intent.
2. Inspect `contracts/workflow.schema.json`, the protected excursion policy, and relevant tests. Keep current baseline and candidate separate.
3. Run the offline demo or compile a supported explicit model. Capture paths, semantic/implementation/environment subjects and raw receipts.
4. Explain affected authority, state entry, assignment, effects and remaining UNKNOWN claims. A browser check is not human evidence.
5. Run regression/negative tests (`python -m pytest`). Check release identity separately with `python scripts/verify_release.py` or `eija doctor`: if the implementation differs from its fixture, stop at source review rather than changing the manifest yourself.
6. Produce a review packet for the owner. Do not approve, apply, infer consent, reveal keys or manufacture correct answers as a human acknowledgement.

Commands are in README.md. Live provider use requires the owner's explicit consent and local credential configuration. Output must distinguish tested behaviour, same-author inference, mocked contracts, unrun live paths and proposed follow-up work.
