# EIJA repository agent instructions

Read README.md, docs/TECHNICAL_LEAD_REVIEW.md, docs/SECURITY_AND_TRUST.md and the acceptance matrix before proposing changes. This is a bounded local excursion POC, not a universal compiler.

Work through typed SemanticTransaction / Workflow contracts. Do not create parallel rule/state/journey sources. AI proposals are untrusted; they cannot choose meaning, mint receipts, approve, apply, or change protected policy merely to pass a task.

For a synthetic offline check use `eija demo --out output/demo.json`. For an explicit supported model use `eija compile examples/excursion-candidate.json --out output/compiled --verify`. These are evidence/fixture commands, not human authorisation. For live inference require explicit user permission for egress/spend and both `--allow-network` and request consent. Do not read Codex auth files or pass provider keys in prompts.

Domain and application layers must not import HTTP/vendor/SQLite adapters. Introduce an application-owned port when a genuine external boundary is needed; do not create speculative abstractions or a second interpreter. Every new operator needs executable semantics, missing-resolver rejection, projection rules, identity effects, a negative oracle and an evidence policy.

Run `python scripts/verify_release.py` after changes. A source mismatch is expected for changed implementation and requires review. **Never run the maintainer stamping tool merely to make tests or a gate green.** Do not edit generated receipts, expected outcomes, subject hashes or evidence labels to conceal a failure. Propose fixture/oracle changes separately and explain why the requirement changed.

Keep original evidence and document counterexamples. Do not claim a mocked provider was live, a synthetic test measured a human, a hash proves correctness, or a local capability is institutional identity. Do not autonomously call owner approval/apply endpoints, fabricate review answers, read the private browser launch token or access receipt.key. These instructions reinforce policy but are not a sandbox against an agent with equivalent OS permissions.

Before recommending updated Codex/OpenRouter parameters, check current official documentation and record the tested CLI/model versions. No remote publishing, deployment, paid loops, migration or key handling without explicit authorisation.

## Capability lanes (parallel development)

Work is split into lanes. Each lane has a GitHub issue, a branch `lane/<name>`, an ADR number block (`docs/adr/README.md`) and its own files. Lane rules:

- **OSS first** ([ADR-0016](docs/adr/0016-oss-first-adapters-not-engines.md)). Adopt an existing tool and write only generators and adapters. Add a row to `docs/oss/REGISTER.md` for every tool adopted and every custom module.
- **Gates are nox plugins.** Add `quality/sessions/<lane>.py` with sessions tagged `fast`, `full` or `release`; never edit another lane's session module. Sessions use `python=False` and call `sys.executable`, so they run in the project venv. `nox -t full` must pass before a PR.
- **Verification artefacts** live under `verification/<technique>/`, generated from the executable model. Reports go to `reports/` (gitignored). Committed evidence snapshots name the platform that produced them.
- **Missing prerequisites report `NOT_RUN`**, never `PASS` (Java, Docker/WSL, Chromium, a vendor CLI login).
- **Dependencies** go in the lane's extra in `pyproject.toml`, pinned `==`.
- **Line endings are LF.** On Windows, write files with `newline="\n"`.
- **Stay off the shared hot spots.** Don't reformat unrelated files, don't rename kernel symbols, don't restamp `trusted_build.json`. Kernel changes need a regression test and an ADR.
- **Heavy commands run serially.** The reference PC has 16 GB RAM, and D: is a slow HDD, so keep temp data in the checkout.
