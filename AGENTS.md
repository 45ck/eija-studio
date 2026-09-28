# EIJA repository agent instructions

Read README.md, docs/TECHNICAL_LEAD_REVIEW.md, docs/SECURITY_AND_TRUST.md and the acceptance matrix before proposing changes. This is a bounded local excursion POC, not a universal compiler.

Work through typed SemanticTransaction / Workflow contracts. Do not create parallel rule/state/journey sources. AI proposals are untrusted; they cannot choose meaning, mint receipts, approve, apply, or change protected policy merely to pass a task.

For a synthetic offline check use `eija demo --out output/demo.json`. For an explicit supported model use `eija compile examples/excursion-candidate.json --out output/compiled --verify`. These are evidence/fixture commands, not human authorisation. For live inference require explicit user permission for egress/spend and both `--allow-network` and request consent. Do not read Codex auth files or pass provider keys in prompts.

Domain and application layers must not import HTTP/vendor/SQLite adapters. Introduce an application-owned port when a genuine external boundary is needed; do not create speculative abstractions or a second interpreter. Every new operator needs executable semantics, missing-resolver rejection, projection rules, identity effects, a negative oracle and an evidence policy.

Run `python scripts/verify_release.py` after changes. A source mismatch is expected for changed implementation and requires review. **Never run the maintainer stamping tool merely to make tests or a gate green.** Do not edit generated receipts, expected outcomes, subject hashes or evidence labels to conceal a failure. Propose fixture/oracle changes separately and explain why the requirement changed.

Keep original evidence and document counterexamples. Do not claim a mocked provider was live, a synthetic test measured a human, a hash proves correctness, or a local capability is institutional identity. Do not autonomously call owner approval/apply endpoints, fabricate review answers, read the private browser launch token or access receipt.key. These instructions reinforce policy but are not a sandbox against an agent with equivalent OS permissions.

Before recommending updated Codex/OpenRouter parameters, check current official documentation and record the tested CLI/model versions. No remote publishing, deployment, paid loops, migration or key handling without explicit authorisation.
