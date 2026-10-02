# EIJA repository agent instructions

Read README.md, docs/TECHNICAL_LEAD_REVIEW.md, docs/SECURITY_AND_TRUST.md and the acceptance matrix before proposing changes. Build a complete, polished local code/model IDE for UML-literate engineers using AI, with explicit supported semantics. The current acceptance target is EIJA's own checkout; connect it read-only before extending to external repositories. Read docs/engineering/SELF-DOGFOOD-ACCEPTANCE.md for the engineering and full IDE UX acceptance bar, and keep repository intake, extracted structure, behavior bindings and verified properties distinct. The dated v0.2 reviews remain historical evidence, not current integration results.

Work through typed SemanticTransaction / Workflow contracts. Do not create parallel rule/state/journey sources. AI proposals are untrusted; they cannot choose meaning, mint receipts, approve, apply, or change protected policy merely to pass a task.

For a synthetic offline check use `eija demo --out output/demo.json`. For an explicit supported model use `eija compile examples/excursion-candidate.json --out output/compiled --verify`. These are evidence/fixture commands, not human authorisation. For live inference require explicit user permission for egress/spend and both `--allow-network` and request consent. Do not read Codex auth files or pass provider keys in prompts.

Domain and application layers must not import HTTP/vendor/SQLite adapters. Introduce an application-owned port when a genuine external boundary is needed; do not create speculative abstractions or a second interpreter. Every new operator needs executable semantics, missing-resolver rejection, projection rules, identity effects, a negative oracle and an evidence policy.

Run `python scripts/verify_release.py` after changes. A source mismatch is expected for changed implementation and requires review. **Never run the maintainer stamping tool merely to make tests or a gate green.** Do not edit generated receipts, expected outcomes, subject hashes or evidence labels to conceal a failure. Propose fixture/oracle changes separately and explain why the requirement changed.

Keep original evidence and document counterexamples. Do not claim a mocked provider was live, a synthetic test measured a human, a hash proves correctness, or a local capability is institutional identity. Do not autonomously call owner approval/apply endpoints, fabricate review answers, read the private browser launch token or access receipt.key. These instructions reinforce policy but are not a sandbox against an agent with equivalent OS permissions.

Before recommending updated Codex/OpenRouter parameters, check current official documentation and record the tested CLI/model versions. No remote publishing, deployment, paid loops, migration or key handling without explicit authorisation.

For agent onboarding and what an agent may or may not do over MCP, see `docs/agents/contract.md` and `docs/agents/quickstart.md` (`eija mcp`).
## Knowledge base (start retrieval here)

Start retrieval at [okf/index.md](okf/index.md): an [OKF v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md) wiki of the ubiquitous language, bounded contexts, modules, public symbols, ADRs, acceptance criteria, verification techniques, gates and lanes. Every page has a `repo://` `resource` and hashes of the code it describes, so open the page, then the linked source. Do not hand-edit frontmatter or `okf:generated` blocks; write prose under `## Notes`. After adding a public domain/application symbol, ADR, nox session or lane, or changing a linked source, run `python -m quality.okf sync` and commit the resulting `okf/` changes in the same PR (or leave one sync commit to the integrating lane). `nox -s okf` (full/release tiers) reports STALE pages (source changed since the page was baselined) and NOTES_STALE pages (hand-written Notes not re-read since): read them, fix the Notes, then `python -m quality.okf review`. Never record `verified` without reading the page, and agents use `--by process:<id>`, never `human:<id>`. The fast tier runs only `nox -s okf_structure`. See [docs/knowledge-base.md](docs/knowledge-base.md).

## Capability lanes (parallel development)

Work is split into lanes. Each lane has a GitHub issue, a branch `lane/<name>`, an ADR number block (`docs/adr/README.md`) and its own files. Lane rules:

- **OSS first** ([ADR-0016](docs/adr/0016-oss-first-adapters-not-engines.md)). Adopt an existing tool and write only generators and adapters. Add a row to `docs/oss/REGISTER.md` for every tool adopted and every custom module.
- **Gates are nox plugins.** Add `quality/sessions/<lane>.py` with sessions tagged `fast`, `full` or `release`; never edit another lane's session module. Sessions use `python=False` and call `sys.executable`, so they run in the project venv. `nox -t full` must pass before a PR.
- **Verification artefacts** live under `verification/<technique>/`, generated from the executable model. Reports go to `reports/` (gitignored). Committed evidence snapshots name the platform that produced them.
- **Missing prerequisites report `NOT_RUN`**, never `PASS` (Java, Docker/WSL, Chromium, a vendor CLI login).
- **Dependencies** go in the lane's extra in `pyproject.toml`, pinned `==`.
- **Line endings are LF.** On Windows, write files with `newline="\n"`.
- **Keep the wiki in step.** If your change adds a public domain/application symbol, an ADR, a nox session or a lane, or moves a linked source, run `python -m quality.okf sync`, review the pages it lists, and commit `okf/` in the same PR (`nox -s okf`, tags full and release).
- **Stay off the shared hot spots.** Don't reformat unrelated files, don't rename kernel symbols, don't restamp `trusted_build.json`. Kernel changes need a regression test and an ADR.
- **Heavy commands run serially.** The reference PC has 16 GB RAM, and D: is a slow HDD, so keep temp data in the checkout.
- **Quality gates** ([docs/quality/gates.md](docs/quality/gates.md), ADR-0035/0036): run `nox -t fast` before committing and `nox -t full` before a PR. Never bypass hooks (`--no-verify`). Thresholds only tighten: fix the code or shrink the named debt; do not add ignores, raise budgets or lower `fail_under` to get green. `pip install -e ".[dev,lint]"` provides the tools.
